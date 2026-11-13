"""Day 06 pipeline. Run from the repo root or starter/:

    python -m src.run prepare           # read + normalize PDF -> data/pages.jsonl, data/manifest.json
    python -m src.run ingest            # chunk A/B/C, embed, upsert into pgvector (re-run safe)
    python -m src.run validate          # check benchmark counts, evidence and filter values
    python -m src.run evaluate --split dev|test
    python -m src.run audit-prep        # samples for manual coherence/grounding/metadata audit
"""
import argparse
import json
import os
import statistics
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from .chunking import by_paragraph, fixed_size
from .embeddings import OpenAIEmbedder
from .evaluation import evaluate_query, gold_entries, squash, summarize
from .ingestion import load_pdf
from .models import DocumentPage
from .store import FILTER_FIELDS, PgVectorStore, content_hash

STARTER = Path(__file__).resolve().parents[1]
REPO = STARTER.parent
CONFIG = json.loads((STARTER / "config.json").read_text(encoding="utf-8"))
PAGES_FILE = REPO / "data" / "pages.jsonl"
MANIFEST = REPO / "data" / "manifest.json"
BENCHMARK = REPO / "benchmark" / "questions.json"
RESULTS = REPO / "results"
ATTRIBUTION = "Download for free at https://openstax.org/details/books/calculus-volume-1."


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def setup() -> tuple[OpenAIEmbedder, PgVectorStore]:
    load_dotenv(STARTER / ".env", override=True)
    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL missing in starter/.env")
    embedder = OpenAIEmbedder(CONFIG["embedding"]["model"])
    store = PgVectorStore(url, embedder.dimensions)
    store.create_schema()
    return embedder, store


def load_pages() -> list[DocumentPage]:
    rows = [json.loads(l) for l in PAGES_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [DocumentPage(r["document_id"], r["source"], r["page"], r["text"], r["metadata"]) for r in rows]


def make_chunks(name: str, pages: list[DocumentPage]):
    cfg = CONFIG["strategies"][name]
    if cfg["chunking"] == "fixed_size":
        return [c for p in pages for c in fixed_size(p, cfg["size"], cfg["overlap"])]
    return [c for p in pages for c in by_paragraph(p, cfg["max_size"], cfg["min_size"])]


def cmd_prepare(_args) -> None:
    """Read + normalize the PDF, write data/pages.jsonl and data/manifest.json (no API calls)."""
    doc = CONFIG["document"]
    pdf = REPO / doc["pdf_path"]
    if not pdf.exists():
        raise SystemExit(f"PDF not found: {pdf}. See data/manifest.json for the download URL.")
    t0 = time.perf_counter()
    pages, sections, log = load_pdf(pdf, doc["document_id"], doc["source"], doc["sections"],
                                    doc["min_chars_per_page"])
    read_seconds = time.perf_counter() - t0
    if len(pages) < 30:
        raise SystemExit(f"Only {len(pages)} content pages; need >= 30")
    PAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PAGES_FILE.open("w", encoding="utf-8") as f:
        for p in pages:
            f.write(json.dumps({**asdict(p), "chars": len(p.text), "attribution": ATTRIBUTION},
                               ensure_ascii=False) + "\n")
    write_json(MANIFEST, {
        "source_id": doc["document_id"], "title": "Calculus Volume 1 (OpenStax)",
        "authors": "Gilbert Strang, Edwin \"Jed\" Herman et al.", "publisher": "OpenStax, Rice University",
        "source_path_or_url": doc["url"], "local_path": doc["pdf_path"],
        "license_or_permission": "CC BY-NC-SA 4.0 (PDF page 4). Non-commercial lab use with attribution; "
                                 "extracted text in data/pages.jsonl keeps the required attribution line.",
        "attribution": ATTRIBUTION, "version": "2018 print, PDF modified 2018-08-15 (PDF metadata)",
        "accessed_at": doc["accessed_at"], "physical_pages_in_pdf": 873,
        "page_numbering": "page = physical PDF page (1-based); printed_page = number printed in the running header",
        "counting_rule": "All pages of sections 2.3, 2.4, 3.1, 3.2 taken from the PDF outline. A page counts "
                         "if it has >= 200 normalized chars. Cover, TOC, glossary, chapter-review pages are "
                         "not included. Exercise pages are counted separately (page_type=exercises).",
        "sections": sections,
        "pages_counted": len(pages),
        "pages_text": sum(p.metadata["page_type"] == "text" for p in pages),
        "pages_exercises": sum(p.metadata["page_type"] == "exercises" for p in pages),
        "pages": [{"page": p.page, "printed_page": p.metadata["printed_page"], "section": p.metadata["section"],
                   "page_type": p.metadata["page_type"], "chars": len(p.text)} for p in pages],
        "total_chars": sum(len(p.text) for p in pages),
        "read_seconds": round(read_seconds, 2),
        "ingest_log": log,
        "known_issues": [
            "pypdf flattens math layout: fractions, exponents and limits lose structure (x2 means x^2).",
            "Some words are glued together (e.g. 'ofa', 'atb', 'inFigure'); kept as-is, not auto-fixed.",
            "Figures and graphs are images: only their captions are kept. No OCR was needed (no scanned pages).",
            "pypdf prints 'Unknown destination' for one outline item; section ranges were still read.",
            "Page 222 starts with the last lines of the Chapter 3 introduction (kept, section 3.1)."],
    })
    print(f"{len(pages)} pages written; log entries: {len(log)}")


def cmd_ingest(_args) -> None:
    pages = load_pages()
    embedder, store = setup()
    run = {"started_at": now(), "model": embedder.model_name, "dimensions": embedder.dimensions,
           "db": store.versions(), "pages": len(pages), "strategies": {}}
    for name in CONFIG["strategies"]:
        t = time.perf_counter()
        tokens_before, calls_before = embedder.tokens_used, embedder.api_calls
        rows_before = store.count(name)
        chunks = make_chunks(name, pages)
        hashes = [content_hash(c.text) for c in chunks]
        cached = store.vectors_by_hash(sorted(set(hashes)), embedder.model_name)
        todo = sorted({h for h in hashes if h not in cached})
        text_by_hash = {content_hash(c.text): c.text for c in chunks}
        new = dict(zip(todo, embedder.embed_documents([text_by_hash[h] for h in todo]))) if todo else {}
        vectors = [cached.get(h) or new[h] for h in hashes]
        res = store.upsert(name, chunks, vectors, embedder.model_name, CONFIG["document"]["document_id"])
        lengths = [len(c.text) for c in chunks]
        tokens = embedder.tokens_used - tokens_before
        run["strategies"][name] = {
            "config": CONFIG["strategies"][name], "chunks": len(chunks), "rows_before": rows_before,
            "rows_after": store.count(name), **res, "embedded_now": len(todo), "reused_vectors": len(chunks) - len(todo),
            "api_calls": embedder.api_calls - calls_before, "tokens": tokens,
            "cost_usd": round(tokens / 1e6 * 0.02, 6), "seconds": round(time.perf_counter() - t, 2),
            "len_min": min(lengths), "len_median": statistics.median(lengths),
            "len_mean": round(statistics.mean(lengths), 1), "len_max": max(lengths), "total_chars": sum(lengths)}
        print(name, json.dumps(run["strategies"][name], ensure_ascii=False))
    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / "ingest_runs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(run, ensure_ascii=False) + "\n")


def load_questions() -> list[dict]:
    return json.loads(BENCHMARK.read_text(encoding="utf-8"))["questions"]


def cmd_validate(_args) -> bool:
    pages = {p.page: p for p in load_pages()}
    qs = load_questions()
    problems = []
    for q in qs:
        for g in gold_entries(q):
            page = pages.get(g["page"])
            if page is None or squash(g["quote"]) not in squash(page.text):
                problems.append(f"{q['id']}: evidence not found on page {g['page']}")
        for k, v in (q.get("filter") or {}).items():
            if k not in FILTER_FIELDS or not any(p.metadata.get(k) == v for p in pages.values()):
                problems.append(f"{q['id']}: filter {k}={v!r} not a valid metadata value")
    dev = [q for q in qs if q["split"] == "dev"]
    test = [q for q in qs if q["split"] == "test"]
    filt = [q for q in qs if q.get("filter")]
    counts = {"total": len(qs), "dev": len(dev), "test": len(test), "with_filter": len(filt),
              "test_with_filter": sum(q["split"] == "test" for q in filt)}
    if len(qs) < 20 or len(dev) < 15 or len(test) < 5 or len(filt) < 3 or counts["test_with_filter"] < 1:
        problems.append(f"counts do not meet BENCHMARK.md minimums: {counts}")
    write_json(RESULTS / "benchmark_validation.json", {"checked_at": now(), "counts": counts, "problems": problems})
    print(json.dumps(counts), "problems:", problems or "none")
    return not problems


def cmd_evaluate(args) -> None:
    if not cmd_validate(args):
        raise SystemExit("Benchmark invalid; fix before evaluating.")
    embedder, store = setup()
    qs = [q for q in load_questions() if args.split == "all" or q["split"] == args.split]
    qvec = {q["id"]: embedder.embed_query(q["question"]) for q in qs}
    summary = {"run_at": now(), "split": args.split, "model": embedder.model_name, "strategies": {}}
    for name, cfg in CONFIG["strategies"].items():
        traces, t = [], time.perf_counter()
        for q in qs:
            applied = q.get("filter") if cfg["use_filter"] and q.get("filter") else None
            hits = store.search(name, qvec[q["id"]], CONFIG["top_k"], applied)
            traces.append(evaluate_query(q, hits, applied))
        seconds = time.perf_counter() - t
        out = RESULTS / "traces" / f"{name}_{args.split}.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("".join(json.dumps(tr, ensure_ascii=False) + "\n" for tr in traces), encoding="utf-8")
        s = summarize(traces)
        s["search_seconds"] = round(seconds, 3)
        s["missed"] = [tr["id"] for tr in traces if not tr["hit3"]]
        summary["strategies"][name] = s
        print(name, json.dumps(s[args.split if args.split != "all" else "all"]), "missed@3:", s["missed"])
    summary["query_embedding_tokens"] = embedder.tokens_used
    summary["query_embedding_cost_usd"] = round(embedder.cost_usd(), 6)
    write_json(RESULTS / f"metrics_{args.split}.json", summary)


def cmd_audit_prep(_args) -> None:
    """Fixed samples for manual labels. Coherence positions are chosen by rule, before reading scores:
    10 'text' pages at equal steps through the sorted page list; position = middle character of the page."""
    pages = [p for p in load_pages() if p.metadata["page_type"] == "text"]
    pick = [pages[i * len(pages) // 10] for i in range(10)]
    by_strategy = {n: make_chunks(n, pages) for n in ("A", "B")}
    lines = ["# Coherence samples (C uses the same chunks as B)\n"]
    for i, p in enumerate(pick, 1):
        pos = len(p.text) // 2
        lines.append(f"\n## P{i:02d} page {p.page} (section {p.metadata['section']}), char {pos}\n")
        for n, chunks in by_strategy.items():
            c = next(c for c in chunks if c.page == p.page
                     and c.metadata["char_start"] <= pos < c.metadata["char_end"])
            lines.append(f"\n### {n} `{c.chunk_id}` ({len(c.text)} chars)\n\n```text\n{c.text}\n```\n")
    (RESULTS / "audit").mkdir(parents=True, exist_ok=True)
    (RESULTS / "audit" / "coherence_samples.md").write_text("".join(lines), encoding="utf-8")

    # Metadata check on test top-3: chunk text must be on that PDF page; section/chapter/page_type
    # must match the page's values derived from the PDF outline.
    page_map = {p.page: p for p in load_pages()}
    rows = ["strategy,question_id,rank,chunk_id,page,section,text_on_page,section_ok,chapter_ok,page_type_ok,filter,filter_ok"]
    for n in CONFIG["strategies"]:
        f = RESULTS / "traces" / f"{n}_test.jsonl"
        if not f.exists():
            continue
        for tr in map(json.loads, f.read_text(encoding="utf-8").splitlines()):
            for h in tr["hits"]:
                src = page_map[h["page"]]
                flt = tr["filter_in_question"] or {}
                rows.append(",".join(map(str, [
                    n, tr["id"], h["rank"], h["chunk_id"], h["page"], h["section"],
                    squash(h["text"]) in squash(src.text), h["section"] == src.metadata["section"],
                    h["chapter"] == src.metadata["chapter"], h["page_type"] == src.metadata["page_type"],
                    json.dumps(flt).replace(",", ";") if flt else "", all(h[k] == v for k, v in flt.items()) if flt else "N/A"])))
    (RESULTS / "audit" / "metadata_check.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("wrote results/audit/coherence_samples.md and metadata_check.csv")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare").set_defaults(fn=cmd_prepare)
    sub.add_parser("ingest").set_defaults(fn=cmd_ingest)
    sub.add_parser("validate").set_defaults(fn=cmd_validate)
    ev = sub.add_parser("evaluate")
    ev.add_argument("--split", choices=["dev", "test", "all"], required=True)
    ev.set_defaults(fn=cmd_evaluate)
    sub.add_parser("audit-prep").set_defaults(fn=cmd_audit_prep)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
