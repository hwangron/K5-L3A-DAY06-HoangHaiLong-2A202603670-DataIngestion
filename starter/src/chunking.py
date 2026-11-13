"""Fixed-size (A) and structure-aware (B/C) chunking, one page at a time."""
import re

from .models import Chunk, DocumentPage

# Lines that open a new logical block in this textbook.
_STRONG = re.compile(
    r"^(Example \d+\.\d+$|Theorem \d+\.\d+:|Definition$|Problem-Solving Strategy|Learning Objectives$"
    r"|Proof$|\d+\.\d+ \| |\d+\.\d+ EXERCISES$|In summary:)")
_WEAK = re.compile(r"^(Figure \d+\.\d+|Table \d+\.\d+$|In the following exercises|For the following exercises)")


def _is_heading(line: str, prev: str | None) -> bool:
    """Heuristic for sub-section titles such as 'The Squeeze Theorem' or 'Continuity at a Point'."""
    if len(line) > 60 or not line[0].isupper() or line[-1] in ".,:;?)" or "=" in line or "lim" in line:
        return False
    if prev is not None and _STRONG.match(prev):  # title line of an Example/Theorem: keep together
        return False
    words = [w for w in line.split() if len(w) > 3]
    return bool(words) and sum(w[0].isupper() for w in words) / len(words) >= 0.6


def _chunk(page: DocumentPage, kind: str, idx: int, start: int, end: int) -> Chunk:
    return Chunk(
        chunk_id=f"{page.document_id}-p{page.page:03d}-{kind}-{idx:02d}",
        document_id=page.document_id, source=page.source, page=page.page,
        text=page.text[start:end].strip(),
        metadata={**page.metadata, "char_start": start, "char_end": end})


def fixed_size(page: DocumentPage, size: int, overlap: int) -> list[Chunk]:
    """Character windows of `size` with `overlap`; ignores sentence/structure on purpose."""
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    chunks, start, idx = [], 0, 0
    while start < len(page.text):
        end = min(start + size, len(page.text))
        chunks.append(_chunk(page, "fixed", idx, start, end))
        if end == len(page.text):
            break
        start, idx = end - overlap, idx + 1
    return chunks


def _blocks(text: str) -> list[tuple[int, int, bool]]:
    """Split the page into (start, end, starts_with_strong_boundary) blocks of whole lines."""
    blocks, offset, prev = [], 0, None
    cur_start, cur_strong = 0, True
    for line in text.split("\n"):
        line_start = offset
        offset += len(line) + 1
        strong = bool(_STRONG.match(line)) or _is_heading(line, prev)
        weak = bool(_WEAK.match(line))
        if (strong or weak) and line_start > cur_start:
            blocks.append((cur_start, line_start, cur_strong))
            cur_start, cur_strong = line_start, strong
        prev = line
    blocks.append((cur_start, len(text), cur_strong))
    return blocks


def by_paragraph(page: DocumentPage, max_size: int, min_size: int = 250) -> list[Chunk]:
    """Group structural blocks up to `max_size`; start a new chunk at strong boundaries
    (headings, Example, Theorem, Definition) once the current chunk has `min_size` chars.
    Oversized blocks are split on line boundaries."""
    spans: list[tuple[int, int]] = []
    cur: list[int] | None = None
    text = page.text
    for b_start, b_end, strong in _blocks(text):
        if b_end - b_start > max_size:  # split an oversized block on line ends
            if cur:
                spans.append(tuple(cur)); cur = None
            s = b_start
            while s < b_end:
                e = min(s + max_size, b_end)
                if e < b_end:
                    cut = text.rfind("\n", s, e)
                    e = cut + 1 if cut > s else e
                spans.append((s, e)); s = e
            continue
        if cur is None:
            cur = [b_start, b_end]
        elif (b_end - cur[0] > max_size) or (strong and cur[1] - cur[0] >= min_size):
            spans.append(tuple(cur)); cur = [b_start, b_end]
        else:
            cur[1] = b_end
    if cur:
        spans.append(tuple(cur))
    spans = _merge_small(text, spans, min_size // 2, int(max_size * 1.5))
    return [_chunk(page, "struct", i, s, e) for i, (s, e) in enumerate(spans) if text[s:e].strip()]


def _merge_small(text: str, spans: list[tuple[int, int]], small: int, hard_max: int) -> list[tuple[int, int]]:
    """Attach tiny spans to a neighbour: a span that opens with a heading/Example goes to the
    next span (it introduces it); any other tiny span goes to the previous one."""
    spans = [list(s) for s in spans]
    i = 0
    while i < len(spans) and len(spans) > 1:
        s, e = spans[i]
        if len(text[s:e].strip()) >= small:
            i += 1
            continue
        first_line = text[s:e].strip().split("\n", 1)[0]
        to_next = (bool(_STRONG.match(first_line)) or _is_heading(first_line, None) or i == 0) and i + 1 < len(spans)
        if to_next and spans[i + 1][1] - s <= hard_max:
            spans[i + 1][0] = s
            del spans[i]
        elif i > 0 and e - spans[i - 1][0] <= hard_max:
            spans[i - 1][1] = e
            del spans[i]
        else:
            i += 1
    return [tuple(s) for s in spans]
