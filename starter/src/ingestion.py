"""Read and normalize the PDF corpus; keep page traceability and log problems."""
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader

from .models import DocumentPage

# Bracket-piece glyphs (U+239B..U+23AD) that pypdf emits for large parentheses.
_BRACKET_PIECES = re.compile("[⎛-⎭]")
_FOOTER = "This OpenStax book is available for free at http://cnx.org/content/col11964/1.2"
# Running header/footer, e.g. "160 Chapter 2 | Limits" or "Chapter 2 | Limits 161".
_RUNNING = re.compile(r"^(?:(\d+) )?Chapter \d+ \| [A-Za-z ]+?(?: (\d+))?$")
# Lone "check your learning" counters such as "2.11" printed in the margin.
_MARGIN_COUNTER = re.compile(r"^\d+\.\d+$")
_SECTION_TITLE = re.compile(r"^(\d+)\.(\d+)\.\s*(.+?)\*?$")
_EXERCISES = re.compile(r"^\d+\.\d+ EXERCISES$", re.M)


def normalize_text(text: str) -> tuple[str, int | None]:
    """NFKC-normalize, drop running headers/footers and glyph noise, keep line structure.

    Returns the cleaned text and the printed page number found in the running header.
    """
    text = unicodedata.normalize("NFKC", text)
    text = _BRACKET_PIECES.sub("", text)
    printed_page = None
    lines = []
    for raw in text.splitlines():
        line = re.sub(r"[ \t]+", " ", raw).strip()
        if not line or line == _FOOTER or _MARGIN_COUNTER.match(line):
            continue
        running = _RUNNING.match(line)
        if running:
            printed_page = int(running.group(1) or running.group(2))
            continue
        lines.append(line)
    return "\n".join(lines), printed_page


def read_sections(reader: PdfReader) -> list[dict]:
    """Section page ranges taken from the PDF outline (bookmarks), not guessed."""
    flat = []

    def walk(items, chapter_title=None):
        for item in items:
            if isinstance(item, list):
                walk(item, chapter_title)
                continue
            title = unicodedata.normalize("NFKC", item.title).replace(" ", " ")
            page = reader.get_destination_page_number(item) + 1
            if title.startswith("Chapter"):
                chapter_title = title
            flat.append({"title": title, "start": page, "chapter_title": chapter_title})

    walk(reader.outline)
    flat.sort(key=lambda x: x["start"])
    sections = []
    for i, entry in enumerate(flat):
        m = _SECTION_TITLE.match(entry["title"])
        if not m or not entry["chapter_title"] or not entry["chapter_title"].startswith("Chapter"):
            continue
        nxt = next((e["start"] for e in flat[i + 1:] if e["start"] > entry["start"]), len(reader.pages) + 1)
        sections.append({
            "chapter": int(m.group(1)),
            "chapter_title": entry["chapter_title"].split(". ", 1)[-1].rstrip("*"),
            "section": f"{m.group(1)}.{m.group(2)}",
            "section_title": m.group(3).strip(),
            "start_page": entry["start"],
            "end_page": nxt - 1,
        })
    return sections


def load_pdf(path: Path, document_id: str, source: str, sections_wanted: list[str],
             min_chars: int = 200) -> tuple[list[DocumentPage], list[dict], list[dict]]:
    """Extract every physical page of the wanted sections.

    Returns (pages, section_ranges, log). Pages with too little text are logged and skipped.
    """
    reader = PdfReader(str(path))
    sections = [s for s in read_sections(reader) if s["section"] in sections_wanted]
    missing = set(sections_wanted) - {s["section"] for s in sections}
    if missing:
        raise ValueError(f"Sections not found in PDF outline: {sorted(missing)}")
    pages, log = [], []
    for sec in sections:
        in_exercises = False
        for number in range(sec["start_page"], sec["end_page"] + 1):
            try:
                raw = reader.pages[number - 1].extract_text() or ""
            except Exception as exc:  # keep going, but record the failure
                log.append({"page": number, "level": "error", "message": f"extract failed: {exc}"})
                continue
            text, printed = normalize_text(raw)
            if _EXERCISES.search(text):
                in_exercises = True
            if len(text) < min_chars:
                log.append({"page": number, "level": "warning",
                            "message": f"only {len(text)} chars after normalization; skipped"})
                continue
            if printed is None:
                log.append({"page": number, "level": "info", "message": "printed page number not found"})
            pages.append(DocumentPage(
                document_id=document_id, source=source, page=number, text=text,
                metadata={"printed_page": printed, "chapter": sec["chapter"],
                          "chapter_title": sec["chapter_title"], "section": sec["section"],
                          "section_title": sec["section_title"],
                          "page_type": "exercises" if in_exercises else "text"}))
    return pages, sections, log
