"""Real embedding provider: OpenAI embeddings API. No mock fallback: errors are raised."""
import os
import time
from typing import Protocol

from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError

PRICE_PER_MTOK = {"text-embedding-3-small": 0.02, "text-embedding-3-large": 0.13}  # USD, list price
DIMENSIONS = {"text-embedding-3-small": 1536, "text-embedding-3-large": 3072}


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, question: str) -> list[float]: ...


class OpenAIEmbedder:
    """Documents and queries are embedded the same way (the model has no query/doc prefix)."""

    def __init__(self, model_name: str = "text-embedding-3-small", batch_size: int = 96) -> None:
        key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not key:
            raise RuntimeError("OPENAI_API_KEY is missing in starter/.env")
        if model_name not in DIMENSIONS:
            raise ValueError(f"Unknown dimensions for {model_name}")
        self.model_name, self.dimensions, self.batch_size = model_name, DIMENSIONS[model_name], batch_size
        self.client = OpenAI(api_key=key, timeout=60)
        self.tokens_used = 0
        self.api_calls = 0

    def _create(self, texts: list[str]) -> list[list[float]]:
        for attempt in range(4):
            try:
                resp = self.client.embeddings.create(model=self.model_name, input=texts)
                break
            except (RateLimitError, APITimeoutError, APIConnectionError):
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        self.api_calls += 1
        self.tokens_used += resp.usage.total_tokens
        vectors = [d.embedding for d in sorted(resp.data, key=lambda d: d.index)]
        if len(vectors) != len(texts) or any(len(v) != self.dimensions for v in vectors):
            raise RuntimeError("Embedding response has wrong count or dimensions")
        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            out.extend(self._create(texts[i:i + self.batch_size]))
        return out

    def embed_query(self, question: str) -> list[float]:
        return self._create([question])[0]

    def cost_usd(self) -> float:
        return self.tokens_used / 1_000_000 * PRICE_PER_MTOK[self.model_name]
