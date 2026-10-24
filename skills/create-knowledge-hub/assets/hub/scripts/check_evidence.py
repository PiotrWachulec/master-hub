#!/usr/bin/env python3
"""Report-only grounding (evidence) check for the local hub profile 0.5.1.

The Grounding Invariant: every load-bearing fact in 10-silver/ and 20-gold/
(numbers, dates, direct quotes) must exist verbatim in the body of the
sources[].resource files that document cites. scripts/validate_hub.py
proves those resource links resolve; this script proves the claims built
on top of them are actually traceable. It never writes files and never
blocks: hub.json's quality gate (threshold/violations) lives entirely in
validate_hub.py. A listed "fidelity suspect" is a candidate, not a verdict
-- derived values and product names will show up here; judging them is the
reader's job.

Candidate-extraction regex design and the sources-level (not per-footnote)
matching granularity are adapted from scripts/check_evidence.py in
Astro-Han/karpathy-llm-wiki (MIT License,
https://github.com/Astro-Han/karpathy-llm-wiki), itself an implementation
of Karpathy's "LLM Wiki" idea. That project's README ("Design Boundaries"
section) explains why anchoring a claim to one specific source instead of
to the sum of a document's sources[] is deliberately out of scope: every
observed fidelity error was "value absent from the source", which a
whole-document check already catches; precise anchoring would only guard
against a failure mode that has not occurred. The same reasoning applies
here, so a candidate passes if it appears in ANY of the document's cited
sources, not necessarily the one nearest its footnote marker.

Coverage boundary (closed candidate set): candidates are
- quotes of 15+ characters (double-quoted "..."/"..." spans and body
  blockquotes)
- ISO dates (YYYY-MM-DD, YYYY-MM)
- specific numbers: thousands-grouped (10,000), dotted (2.1.80, 3.14),
  suffixed (42K, 99,9%), or 4+ digits (2026)
Small plain integers and exotic forms (signs, currencies, spelled-out
dates) are out of scope; they belong to the compile-time "locate before
you write" rule in SCHEMA.md and to human judgment review.

Text inside fenced code blocks, inline code, and the explanation line(s)
of a "> **Status: Disputed/Outdated**" block are excluded -- a disputed or
outdated claim's restatement is not a fact to re-verify, and a status
marker's own date is bookkeeping, not evidence.

Usage: check_evidence.py
Like validate_hub.py, this script takes no arguments: it always inspects
the hub containing it (its own parent/parent directory), so it keeps
working unmodified after being copied into any hub.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_hub import NAVIGATION_INDEXES, parse_frontmatter  # noqa: E402

NUMBER_TOKEN_RE = re.compile(
    r"(?:\d{1,3}(?:,\d{3})+(?:\.\d+)*(?:\s*[KMB%](?![A-Za-z]))?"
    r"|\d+(?:\.\d+)*(?:\s*[KMB%](?![A-Za-z]))?)(?![A-Za-z])"
)
SUFFIX_RE = re.compile(r"[KMB%]$")
DATE_RE = re.compile(r"\d{4}-\d{2}(?:-\d{2})?")
QUOTE_RES = [re.compile(r'"([^"\n]*)"'), re.compile(r"“([^”\n]*)”")]
STATUS_LINE_RE = re.compile(r"^>\s*\*\*Status:")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^[^\]]+\]:")
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
WS_RE = re.compile(r"\s+")
NO_MATERIAL_RE = re.compile(r"^-\s*No material:\s*(\S+)", re.IGNORECASE)

SCOPE_LAYERS = ("10-silver", "20-gold")


def normalize(text: str) -> str:
    return WS_RE.sub(" ", text).strip()


def fence_opener(line: str):
    m = FENCE_OPEN_RE.match(line)
    if not m:
        return None
    marker, info = m.groups()
    if marker[0] == "`" and "`" in info:
        return None
    return marker[0], len(marker)


def is_fence_closer(line: str, char: str, length: int) -> bool:
    m = FENCE_CLOSE_RE.match(line)
    return bool(m and m.group(1)[0] == char and len(m.group(1)) >= length)


def strip_fences(text: str) -> str:
    out = []
    fence_char = None
    fence_len = 0
    for line in text.splitlines():
        if fence_char:
            if is_fence_closer(line, fence_char, fence_len):
                fence_char = None
            continue
        opener = fence_opener(line)
        if opener:
            fence_char, fence_len = opener
            continue
        out.append(line)
    return "\n".join(out)


def strip_noise(text: str) -> str:
    text = INLINE_CODE_RE.sub(" ", text)
    text = LINK_RE.sub(r"\1", text)
    return text


def keep_number(token: str) -> bool:
    token = token.strip()
    if SUFFIX_RE.search(token) or "," in token or "." in token:
        return True
    return len(token) >= 4


def extract_numeric_date_candidates(line: str) -> list[tuple[str, str]]:
    line = strip_noise(line)
    date_matches = list(DATE_RE.finditer(line))
    candidates = [("date", m.group(0)) for m in date_matches]
    chars = list(line)
    for m in date_matches:
        chars[m.start():m.end()] = " " * (m.end() - m.start())
    masked = "".join(chars)
    candidates.extend(
        ("number", m.group(0)) for m in NUMBER_TOKEN_RE.finditer(masked) if keep_number(m.group(0))
    )
    return candidates


def extract_candidates(body: str) -> list[tuple[str, str]]:
    """Candidates from a document's frontmatter-stripped body only -- unlike
    the upstream script, there is no blockquote metadata header to carve out
    here (frontmatter already covers that role)."""
    text = strip_fences(body)
    candidates: list[tuple[str, str]] = []
    skip_status = False
    blockquote: list[str] = []
    paragraph: list[str] = []

    def flush_blockquote():
        if blockquote:
            joined = normalize(" ".join(blockquote))
            if len(joined) >= 15:
                candidates.append(("quote", joined))
            blockquote.clear()

    def flush_paragraph():
        if paragraph:
            joined = normalize(" ".join(paragraph))
            for quote_re in QUOTE_RES:
                candidates.extend(
                    ("quote", m.group(1)) for m in quote_re.finditer(joined)
                    if len(m.group(1).strip()) >= 15
                )
            paragraph.clear()

    for line in text.splitlines():
        stripped = line.strip()
        if STATUS_LINE_RE.match(stripped):
            flush_blockquote()
            flush_paragraph()
            skip_status = True
            continue
        if skip_status:
            if stripped.startswith(">"):
                continue
            skip_status = False
        if FOOTNOTE_DEF_RE.match(stripped):
            flush_blockquote()
            flush_paragraph()
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            content = strip_noise(stripped.lstrip(">").strip())
            blockquote.append(content)
            candidates.extend(extract_numeric_date_candidates(content))
            continue
        flush_blockquote()
        if not stripped:
            flush_paragraph()
            continue
        plain = strip_noise(line)
        candidates.extend(extract_numeric_date_candidates(plain))
        paragraph.append(plain)
    flush_blockquote()
    flush_paragraph()

    seen = set()
    unique = []
    for kind, value in candidates:
        value = value.strip().strip(".,;:()[]")
        key = (kind, value)
        if value and key not in seen:
            seen.add(key)
            unique.append(key)
    return unique


def contains(haystack: str, kind: str, value: str) -> bool:
    if kind == "quote":
        return value in haystack
    right = r"(?!-\d{2})" if kind == "date" and len(value) == 7 else ""
    pattern = r"(?<![\d.,])" + re.escape(value) + right + r"(?![A-Za-z0-9]|[.,]\d|%)"
    return re.search(pattern, haystack) is not None


def read_frontmatter(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None, ""
    try:
        fm, body, _ = parse_frontmatter(text)
    except (ValueError, RecursionError):
        return None, text
    return fm or {}, body


def resource_paths(fm: dict, doc: Path) -> list[Path]:
    sources = fm.get("sources") if isinstance(fm, dict) else None
    if not isinstance(sources, list):
        return []
    paths = []
    for source in sources:
        if isinstance(source, dict) and isinstance(source.get("resource"), str):
            paths.append((doc.parent / source["resource"]).resolve())
    return paths


def source_body(path: Path) -> str:
    _, body = read_frontmatter(path)
    return normalize(strip_fences(body))


def check_document(doc: Path):
    """Return (fidelity suspects, notes) for one silver/gold document."""
    fm, body = read_frontmatter(doc)
    if fm is None:
        return [], ["could not parse frontmatter"]
    resources = resource_paths(fm, doc)
    if not resources:
        return [], ["no sources field"]
    existing = [p for p in resources if p.is_file()]
    if not existing:
        return [], ["no resolvable sources[].resource"]
    pool = "\n".join(source_body(p) for p in existing)
    misses = [
        value for kind, value in extract_candidates(body)
        if not contains(pool, kind, normalize(value))
    ]
    return misses, []


def is_derived(fm: dict) -> bool:
    """True if any external_refs entry on this document is operation: derive.

    Caller passes fm or {} -- never None -- so a document with unparseable
    frontmatter still falls through to check_document() and lands in the
    existing "Documents without possible verification" section, instead
    of vanishing from the report or crashing the script.
    """
    refs = fm.get("external_refs")
    if not isinstance(refs, list):
        return False
    return any(isinstance(r, dict) and r.get("operation") == "derive" for r in refs)


def confidential_note_candidates(fm: dict) -> dict[str, list[str]]:
    """Fidelity-style candidates found inside Confidential external_refs notes.

    Reuses extract_candidates() -- normally run on a whole document body --
    on a single short note string. A degenerate but valid input for its
    paragraph-flush logic: a one-line string is just a one-paragraph body.
    Report-only, same "candidate, not verdict" framing as the rest of this
    script; applies to both cite and derive entries, independent of
    is_derived() above.
    """
    refs = fm.get("external_refs")
    if not isinstance(refs, list):
        return {}
    hits = {}
    for ref in refs:
        if not isinstance(ref, dict) or ref.get("classification") != "Confidential":
            continue
        note = ref.get("note")
        if not isinstance(note, str):
            continue
        candidates = [value for _, value in extract_candidates(note)]
        if candidates:
            hits[ref.get("id") or "?"] = candidates
    return hits


def iter_scope_documents(knowledge_dir: Path):
    for layer in SCOPE_LAYERS:
        layer_dir = knowledge_dir / layer
        if not layer_dir.is_dir():
            continue
        for path in sorted(layer_dir.rglob("*.md")):
            if path.relative_to(knowledge_dir).as_posix() not in NAVIGATION_INDEXES:
                yield path


def collect_referenced_resources(knowledge_dir: Path) -> set[Path]:
    referenced = set()
    for path in sorted(knowledge_dir.rglob("*.md")):
        fm, _ = read_frontmatter(path)
        for target in resource_paths(fm or {}, path):
            referenced.add(target)
    return referenced


def no_material_paths(log_path: Path) -> set[str]:
    if not log_path.is_file():
        return set()
    try:
        text = log_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return set()
    paths = set()
    for line in text.splitlines():
        m = NO_MATERIAL_RE.match(line.strip())
        if m:
            paths.add(m.group(1).strip("`,;."))
    return paths


def unreferenced_bronze(knowledge_dir: Path, root: Path) -> list[str]:
    bronze_dir = knowledge_dir / "00-bronze"
    if not bronze_dir.is_dir():
        return []
    referenced = collect_referenced_resources(knowledge_dir)
    disposed = no_material_paths(knowledge_dir / "log.md")
    orphans = []
    for path in sorted(p for ext in ("*.md", "*.txt") for p in bronze_dir.rglob(ext)):
        relative = path.relative_to(knowledge_dir).as_posix()
        if relative in NAVIGATION_INDEXES or relative in disposed:
            continue
        if path.resolve() not in referenced:
            orphans.append(path.relative_to(root).as_posix())
    return orphans


def main() -> int:
    if len(sys.argv) != 1:
        print("Arguments are not supported; the hub containing this script is checked.",
              file=sys.stderr)
    root = Path(__file__).resolve().parent.parent
    knowledge_dir = root / "knowledge"
    if not knowledge_dir.is_dir():
        print(f"No knowledge/ under {root}")
        return 0

    suspects: dict[str, list[str]] = {}
    notes: dict[str, list[str]] = {}
    derived: list[str] = []
    confidential_hits: dict[str, dict[str, list[str]]] = {}
    for doc in iter_scope_documents(knowledge_dir):
        label = doc.relative_to(root).as_posix()
        fm, _ = read_frontmatter(doc)
        fm = fm or {}
        # Confidential-note scan runs for every document, before any
        # continue below -- it must not be skipped for derived documents.
        hits = confidential_note_candidates(fm)
        if hits:
            confidential_hits[label] = hits
        if is_derived(fm):
            derived.append(label)
            continue
        misses, issues = check_document(doc)
        if misses:
            suspects[label] = misses
        if issues:
            notes[label] = issues

    print("# Evidence check (non-blocking)\n")
    print("## Fidelity suspects")
    suspect_count = 0
    for label, misses in suspects.items():
        print(f"\n{label}")
        for value in misses:
            print(f"- {value}")
            suspect_count += 1
    if suspect_count == 0:
        print("\n(none)")

    print("\n## Documents without possible verification")
    if notes:
        for label, issues in notes.items():
            for issue in issues:
                print(f"- {label}: {issue}")
    else:
        print("(none)")

    print("\n## Derived documents (not locally grounded, by design)")
    for label in derived:
        print(f"- {label}")
    if not derived:
        print("(none)")

    print("\n## External reference notes with specific figures (review before citing)")
    note_hit_count = 0
    for label, hits in confidential_hits.items():
        for ref_id, values in hits.items():
            for value in values:
                print(f"- {label} [{ref_id}]: {value}")
                note_hit_count += 1
    if note_hit_count == 0:
        print("(none)")

    print("\n## Unreferenced bronze sources")
    orphans = unreferenced_bronze(knowledge_dir, root)
    for path in orphans:
        print(f"- {path}")
    if not orphans:
        print("(none)")

    print(
        f"\n## Summary\n{suspect_count} fidelity suspect(s), "
        f"{len(notes)} document(s) without possible verification, "
        f"{len(derived)} derived document(s), "
        f"{note_hit_count} external reference note figure(s), "
        f"{len(orphans)} unreferenced bronze source(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
