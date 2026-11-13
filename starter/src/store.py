"""PostgreSQL + pgvector store. Driver: pg8000 (pure Python), because Windows Smart App
Control blocks the psycopg-binary DLL on the author's machine. SQL is fully parameterized."""
import hashlib
import json
from typing import Any
from urllib.parse import urlparse

import pg8000.native

from .models import Chunk

TABLE = "day6_chunks"
FILTER_FIELDS = {"chapter": "int", "section": "text", "page_type": "text"}  # allowed filters


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _vec(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.8f}" for x in v) + "]"


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int) -> None:
        u = urlparse(database_url)
        if u.scheme not in ("postgresql", "postgres"):
            raise ValueError("DATABASE_URL must start with postgresql://")
        self.dimensions = dimensions
        self.conn = pg8000.native.Connection(user=u.username, password=u.password, host=u.hostname,
                                             port=u.port or 5432, database=u.path.lstrip("/"))

    def versions(self) -> dict[str, str]:
        row = self.conn.run("SELECT current_setting('server_version'), "
                            "(SELECT extversion FROM pg_extension WHERE extname='vector')")[0]
        if row[1] is None:
            raise RuntimeError("pgvector extension is missing")
        return {"postgres": row[0], "pgvector": row[1]}

    def create_schema(self) -> None:
        self.conn.run(f"""CREATE TABLE IF NOT EXISTS {TABLE} (
            strategy TEXT NOT NULL, chunk_id TEXT NOT NULL,
            document_id TEXT NOT NULL, source TEXT NOT NULL, page INT NOT NULL,
            printed_page INT, chapter INT NOT NULL, section TEXT NOT NULL,
            section_title TEXT, page_type TEXT NOT NULL,
            char_start INT, char_end INT, text TEXT NOT NULL,
            content_hash TEXT NOT NULL, embedding_model TEXT NOT NULL,
            embedding vector({self.dimensions}) NOT NULL,
            PRIMARY KEY (strategy, chunk_id))""")
        dim = self.conn.run("SELECT atttypmod FROM pg_attribute WHERE attrelid = :t::regclass "
                            "AND attname = 'embedding'", t=TABLE)[0][0]
        if dim != self.dimensions:
            raise RuntimeError(f"Table has vector({dim}) but model gives {self.dimensions}")

    def count(self, strategy: str) -> int:
        return self.conn.run(f"SELECT count(*) FROM {TABLE} WHERE strategy = :s", s=strategy)[0][0]

    def vectors_by_hash(self, hashes: list[str], model: str) -> dict[str, list[float]]:
        """Reuse stored vectors for identical text (any strategy) so re-ingest costs nothing."""
        if not hashes:
            return {}
        rows = self.conn.run(f"SELECT DISTINCT ON (content_hash) content_hash, embedding::text FROM {TABLE} "
                             "WHERE embedding_model = :m AND content_hash = ANY(:h)", m=model, h=hashes)
        return {h: json.loads(v) for h, v in rows}

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]], model: str,
               document_id: str) -> dict[str, int]:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors differ in length")
        if any(len(v) != self.dimensions for v in vectors):
            raise ValueError("vector dimension mismatch")
        ids = [c.chunk_id for c in chunks]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate chunk_id inside one ingest")
        self.conn.run("BEGIN")
        try:
            for c, v in zip(chunks, vectors):
                m = c.metadata
                self.conn.run(
                    f"""INSERT INTO {TABLE} VALUES (:strategy, :chunk_id, :doc, :source, :page, :pp, :ch,
                        :sec, :st, :pt, :cs, :ce, :text, :hash, :model, CAST(:emb AS vector))
                        ON CONFLICT (strategy, chunk_id) DO UPDATE SET text = EXCLUDED.text,
                        content_hash = EXCLUDED.content_hash, embedding = EXCLUDED.embedding,
                        embedding_model = EXCLUDED.embedding_model, page = EXCLUDED.page,
                        printed_page = EXCLUDED.printed_page, chapter = EXCLUDED.chapter,
                        section = EXCLUDED.section, section_title = EXCLUDED.section_title,
                        page_type = EXCLUDED.page_type, char_start = EXCLUDED.char_start,
                        char_end = EXCLUDED.char_end, source = EXCLUDED.source""",
                    strategy=strategy, chunk_id=c.chunk_id, doc=c.document_id, source=c.source, page=c.page,
                    pp=m.get("printed_page"), ch=m["chapter"], sec=m["section"], st=m.get("section_title"),
                    pt=m["page_type"], cs=m.get("char_start"), ce=m.get("char_end"), text=c.text,
                    hash=content_hash(c.text), model=model, emb=_vec(v))
            # Remove chunks of this document that no longer exist (changed source / chunking).
            deleted = self.conn.run(f"DELETE FROM {TABLE} WHERE strategy = :s AND document_id = :d "
                                    "AND NOT (chunk_id = ANY(:ids)) RETURNING chunk_id",
                                    s=strategy, d=document_id, ids=ids)
            self.conn.run("COMMIT")
        except Exception:
            self.conn.run("ROLLBACK")
            raise
        return {"written": len(chunks), "deleted_obsolete": len(deleted)}

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Exact (sequential scan) cosine search; filters are applied in SQL before ranking."""
        where, params = ["strategy = :strategy"], {"strategy": strategy, "q": _vec(query_vector), "k": top_k}
        for i, (field, value) in enumerate((filters or {}).items()):
            if field not in FILTER_FIELDS:
                raise ValueError(f"filter field not allowed: {field}")
            where.append(f"{field} = :f{i}")
            params[f"f{i}"] = value
        rows = self.conn.run(
            f"""SELECT chunk_id, document_id, source, page, printed_page, chapter, section, section_title,
                page_type, char_start, char_end, text, 1 - (embedding <=> CAST(:q AS vector)) AS score
                FROM {TABLE} WHERE {' AND '.join(where)}
                ORDER BY embedding <=> CAST(:q AS vector) LIMIT :k""", **params)
        cols = ["chunk_id", "document_id", "source", "page", "printed_page", "chapter", "section",
                "section_title", "page_type", "char_start", "char_end", "text", "score"]
        return [dict(zip(cols, r)) for r in rows]
