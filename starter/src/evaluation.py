"""Evidence-based retrieval scoring and per-query traces.

A retrieved chunk is a hit when it comes from a gold (source, page) AND contains the
whole evidence quote (whitespace/case-insensitive). Any documented alternative gold
evidence is accepted. Coherence and grounding are labelled by hand, not here."""
import re
from typing import Any


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def gold_entries(q: dict[str, Any]) -> list[dict[str, Any]]:
    main = {"source_id": q["gold_source_id"], "page": q["gold_page"], "quote": q["evidence_quote"]}
    return [main] + list(q.get("alternatives", []))


def is_hit(q: dict[str, Any], hit: dict[str, Any]) -> bool:
    text = squash(hit["text"])
    return any(hit["document_id"] == g.get("source_id", q["gold_source_id"]) and hit["page"] == g["page"]
               and squash(g["quote"]) in text for g in gold_entries(q))


def filter_ok(filters: dict[str, Any] | None, hit: dict[str, Any]) -> bool:
    return all(hit.get(k) == v for k, v in (filters or {}).items())


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]],
                   applied_filter: dict[str, Any] | None = None) -> dict[str, Any]:
    flags = [is_hit(question, h) for h in hits]
    gold_pages = {g["page"] for g in gold_entries(question)}
    return {
        "id": question["id"], "split": question["split"], "type": question.get("type"),
        "question": question["question"], "filter_in_question": question.get("filter"),
        "filter_applied": applied_filter,
        "hit1": bool(flags[:1] and flags[0]), "hit3": any(flags[:3]),
        "first_hit_rank": flags.index(True) + 1 if True in flags else None,
        "gold_page_in_top3": any(h["page"] in gold_pages for h in hits[:3]),
        "filter_compliant": (all(filter_ok(question["filter"], h) for h in hits[:3])
                             if question.get("filter") else None),
        "hits": [{**h, "rank": i + 1, "is_evidence_hit": f} for i, (h, f) in enumerate(zip(hits, flags))],
    }


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for split in ("dev", "test", "all"):
        rows = [t for t in traces if split == "all" or t["split"] == split]
        frows = [t for t in rows if t["filter_compliant"] is not None]
        out[split] = {
            "n": len(rows),
            "hit1": sum(t["hit1"] for t in rows),
            "hit3": sum(t["hit3"] for t in rows),
            "filter_questions": len(frows),
            "filter_compliant": sum(t["filter_compliant"] for t in frows),
        }
    return out
