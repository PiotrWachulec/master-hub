#!/usr/bin/env python3
"""Read-only validator of local hub profile 0.7.0, NOT a general OKF validator.

Python 3.10+, standard library only. The supported frontmatter/Markdown
subset and deliberate exclusions are documented in the hub's SCHEMA.md.
"""
from __future__ import annotations

from datetime import date, datetime
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


NAVIGATION_INDEXES = (
    'index.md', '00-bronze/index.md', '10-silver/index.md',
    '20-gold/index.md', '90-decisions/index.md',
)

NO_MATERIAL_RE = re.compile(r'^-\s*No material:\s*(\S+)', re.IGNORECASE)
UUID_RE = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')

# Line-start classification for check_paragraph_wrapping(). A list marker
# only counts directly followed by whitespace/end-of-line -- *emphasis* and
# **bold** at the start of a line are not list items.
HEADING_LINE_RE = re.compile(r'^#{1,6}(?:\s|$)')
ITEM_LINE_RE = re.compile(r'^(?:[-*+]|\d+[.)])(?:\s|$)')
QUOTE_LINE_RE = re.compile(r'^>')
FOOTNOTE_LINE_RE = re.compile(r'^\[\^')
TABLE_LINE_RE = re.compile(r'^\|')
WRAP_UNIT_LABELS = {'para': 'Paragraph', 'item': 'List item', 'quote': 'Quote'}


class SyntaxViolation(ValueError):
    def __init__(self, line: int, message: str):
        self.line = line
        super().__init__(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Non-finite JSON number is not supported: {value}")


def finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        reject_constant(value)
    return result


def scalar(raw: str, line: int):
    """Strings, JSON flow collections, or YAML single-quoted strings only."""
    raw = raw.strip()
    if not raw:
        raise SyntaxViolation(line, "Empty scalar; use an explicit quoted string")
    if raw[0] in '[{"':
        try:
            return json.loads(raw, object_pairs_hook=unique_object,
                              parse_constant=reject_constant, parse_float=finite_float)
        except ValueError as exc:
            raise SyntaxViolation(line, f"Unsupported/invalid JSON flow value: {exc}") from exc
    if raw.startswith("'"):
        if not re.fullmatch(r"'(?:[^']|'')*'", raw):
            raise SyntaxViolation(line, "Invalid single-quoted string")
        return raw[1:-1].replace("''", "'")
    if (raw[0] in '-?:,]}#&*!|>@`%' or re.search(r":\s|\s#|[\[\]{}]", raw)
            or raw.lower() in {"null", "true", "false", "yes", "no", "on", "off", "~"}
            or re.fullmatch(r"[+-]?(?:\d[\d_]*(?:\.[\d_]*)?|\.[\d_]+)(?:[eE][+-]?\d+)?", raw)
            or re.fullmatch(r"[+-]?(?:0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+|\.(?:inf|nan))", raw, re.I)):
        raise SyntaxViolation(line, "Unsupported YAML scalar; quote it or use JSON flow syntax")
    return raw


def parse_frontmatter(text: str):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != '---':
        return None, text, 0
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
    if end is None:
        raise SyntaxViolation(1, "Unclosed frontmatter")
    tokens = []
    for i, line in enumerate(lines[1:end], 2):
        if not line.strip():
            continue
        if '\t' in line:
            raise SyntaxViolation(i, "Tabs are not supported in frontmatter")
        indent = len(line) - len(line.lstrip(' '))
        if indent % 2:
            raise SyntaxViolation(i, "Indentation must use pairs of spaces")
        tokens.append((indent, line.strip(), i))

    def pair(raw, line):
        m = re.fullmatch(r'([A-Za-z_][A-Za-z0-9_-]*):(?:\s+(.*))?', raw)
        if not m:
            raise SyntaxViolation(line, "Expected key: value; unsupported YAML construct")
        return m.group(1), m.group(2)

    def mapping(pos, indent, initial=None):
        result = {} if initial is None else initial
        while pos < len(tokens) and tokens[pos][0] == indent:
            _, raw, line = tokens[pos]
            key, value = pair(raw, line)
            if key in result:
                raise SyntaxViolation(line, f"Duplicate key: {key}")
            result[key], pos = value_at(value, pos + 1, indent + 2, line)
        return result, pos

    def value_at(raw, pos, indent, line):
        if raw is not None:
            return scalar(raw, line), pos
        if pos >= len(tokens) or tokens[pos][0] != indent:
            raise SyntaxViolation(line, "Missing value or invalid indentation")
        return block(pos, indent)

    def block(pos, indent):
        if indent > 20:
            raise SyntaxViolation(tokens[pos][2], "Frontmatter nesting exceeds supported depth")
        if not tokens[pos][1].startswith('- '):
            return mapping(pos, indent)
        result = []
        while pos < len(tokens) and tokens[pos][0] == indent and tokens[pos][1].startswith('- '):
            _, raw, line = tokens[pos]
            raw = raw[2:]
            pos += 1
            if re.match(r'[A-Za-z_][A-Za-z0-9_-]*:(?:\s|$)', raw):
                key, value = pair(raw, line)
                value, pos = value_at(value, pos, indent + 4, line)
                item, pos = mapping(pos, indent + 2, {key: value})
            else:
                item = scalar(raw, line)
            result.append(item)
        return result, pos

    if not tokens:
        data = {}
    else:
        if tokens[0][0] != 0 or tokens[0][1].startswith('- '):
            raise SyntaxViolation(tokens[0][2], "Frontmatter must be a top-level mapping")
        data, pos = block(0, 0)
        if pos != len(tokens):
            raise SyntaxViolation(tokens[pos][2], "Unexpected indentation or unsupported YAML")
    return data, ''.join(lines[end + 1:]), end + 1


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


class Validator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.errors = []
        self.warnings = []
        self.referenced_resources = set()
        self.doc_keys = set()
        self.derive_found = {}

    def report(self, path, line, message, warning=False):
        item = {"file": str(path.relative_to(self.root)), "line": max(1, line),
                "message": message}
        (self.warnings if warning else self.errors).append(item)

    def local_file(self, doc, target, line, source=False):
        if not nonempty(target):
            self.report(doc, line, "Expected a nonempty file reference")
            return
        try:
            url = urlsplit(target)
            if url.scheme or url.netloc:
                if not source and url.scheme.lower() in {'http', 'https', 'mailto'}:
                    return  # No network calls or external URL verification.
                self.report(doc, line, "Expected a local file, not an external resource")
                return
            raw = unquote(url.path)
            if not raw:
                if not source and target.startswith('#'):
                    return  # Heading anchors are deliberately outside scope.
                self.report(doc, line, "Empty file reference")
                return
            if raw.startswith('/') or '\\' in raw:
                self.report(doc, line, "Use a relative portable file path")
                return
            candidate = doc.parent / raw
            resolved = candidate.resolve()
            if not resolved.is_relative_to(self.root):
                self.report(doc, line, "Reference escapes the hub")
                return
            if any(p.is_symlink() for p in (candidate, *candidate.parents) if p != self.root):
                self.report(doc, line, "Symlink references are not supported")
            elif not candidate.is_file():
                self.report(doc, line, f"Referenced file does not exist: {target}")
        except (ValueError, OSError, RuntimeError) as exc:
            self.report(doc, line, f"Invalid file reference: {exc}")

    def mask_code(self, doc, body, offset):
        masked, unclosed = self._mask_fences_and_spans(body, offset)
        if unclosed:
            self.report(doc, unclosed, "Unclosed fenced code block")
        return masked

    def _mask_fences_and_spans(self, body, offset):
        # Preserve offsets/newlines so diagnostics point into the original file.
        chars = list(body)
        fence = None
        start = 0
        for number, line in enumerate(body.splitlines(keepends=True), offset + 1):
            m = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)', line)
            if fence:
                if m and m[1][0] == fence[0] and len(m[1]) >= fence[1] and not m[2].strip():
                    fence = None
                for i in range(start, start + len(line)):
                    if chars[i] != '\n':
                        chars[i] = ' '
            elif m:
                fence = (m[1][0], len(m[1]), number)
                for i in range(start, start + len(line)):
                    if chars[i] != '\n':
                        chars[i] = ' '
            start += len(line)
        unclosed = fence[2] if fence else None
        masked = ''.join(chars)
        for m in re.finditer(r'(?<![\\`])(`+)(?!`)(.*?)(?<!`)\1(?!`)', masked, re.S):
            if re.search(r'\n\s*\n', m[2]):
                continue  # Code spans cannot hide links across separate paragraphs.
            for i in range(m.start(), m.end()):
                if chars[i] != '\n':
                    chars[i] = ' '
        return ''.join(chars), unclosed

    def markdown(self, doc, masked, offset, id_origins):
        text = masked
        line_at = lambda pos: offset + 1 + text.count('\n', 0, pos)
        # Unsupported link notations must not silently evade checks.
        for m in re.finditer(r'\[\[|<(?:a|img)\b', text, re.I):
            self.report(doc, line_at(m.start()), "Use standard Markdown links, not wikilinks/HTML links")
        definitions = {}
        work = list(text)
        for m in re.finditer(r'^ {0,3}\[\^([^\]\s]+)\]:', text, re.M):
            key = m[1]
            if key in definitions:
                self.report(doc, line_at(m.start()), f"Duplicate footnote definition: {key}")
            definitions[key] = line_at(m.start())
            work[m.start():m.end()] = ' ' * (m.end() - m.start())
        uses = {}
        for m in re.finditer(r'(?<!\\)\[\^([^\]\s]+)\]', ''.join(work)):
            uses.setdefault(m[1], line_at(m.start()))
        for key, line in uses.items():
            if key not in definitions:
                self.report(doc, line, f"Missing footnote definition: {key}")
            if key not in id_origins:
                self.report(doc, line, f"Footnote has no sources[].id or external_refs[].id: {key}")
        for key in sorted(set(id_origins) - uses.keys()):
            self.report(doc, 1, f"Unused {id_origins[key]}[].id: {key}", warning=True)

        def destination(raw, line):
            raw = raw.strip()
            # Balanced parentheses are handled by the caller. Spaces require <...>.
            m = re.fullmatch(r'<([^<>\n]+)>(?:\s+(?:"[^"\n]*"|\x27[^\x27\n]*\x27|\([^\n]*\)))?', raw)
            if not m:
                m = re.fullmatch(r'(\S+?)(?:\s+(?:"[^"\n]*"|\x27[^\x27\n]*\x27|\([^\n]*\)))?', raw)
            if not m:
                self.report(doc, line, "Unsupported or empty Markdown link destination")
                return
            self.local_file(doc, re.sub(r'\\([\\()\[\] ])', r'\1', m[1]), line)

        refs = {}
        for m in re.finditer(r'^ {0,3}\[([^\]\n]+)\]:[ \t]*(.*)$', text, re.M):
            if m[1].startswith('^'):
                continue
            key = ' '.join(m[1].split()).casefold()
            if key in refs:
                self.report(doc, line_at(m.start()), f"Duplicate link definition: {key}")
            refs[key] = m[2]
            destination(m[2], line_at(m.start()))
            work[m.start():m.end()] = ' ' * (m.end() - m.start())
        scanned = ''.join(work)

        def closing(start, left, right):
            depth = 1
            i = start + 1
            quote = None
            while i < len(scanned):
                c = scanned[i]
                if c == '\\':
                    i += 2
                    continue
                if left == '(' and c in '\"\x27' and (quote or scanned[i - 1].isspace()):
                    quote = None if quote == c else c if quote is None else quote
                if not quote:
                    if c == left:
                        depth += 1
                    elif c == right:
                        depth -= 1
                        if depth == 0:
                            return i
                i += 1
            return None

        i = 0
        while i < len(scanned):
            if scanned[i] == '\\':
                i += 2
                continue
            if scanned[i] != '[':
                i += 1
                continue
            end = closing(i, '[', ']')
            if end is None:
                i += 1
                continue
            label = scanned[i + 1:end]
            next_pos = end + 1
            if label.startswith('^'):
                i = next_pos
                continue
            if next_pos < len(scanned) and scanned[next_pos] == '(':
                close = closing(next_pos, '(', ')')
                if close is None:
                    self.report(doc, line_at(i), "Unclosed Markdown link")
                    i = next_pos + 1
                else:
                    destination(scanned[next_pos + 1:close], line_at(i))
                    i = close + 1
            elif next_pos < len(scanned) and scanned[next_pos] == '[':
                close = closing(next_pos, '[', ']')
                if close is None:
                    self.report(doc, line_at(i), "Unclosed reference link")
                    i = next_pos + 1
                else:
                    key = ' '.join((scanned[next_pos + 1:close] or label).split()).casefold()
                    if key not in refs:
                        self.report(doc, line_at(i), f"Missing link definition: {key}")
                    i = close + 1
            else:
                # Shortcut links are checked through their definitions above.
                i = next_pos

    def check_paragraph_wrapping(self, doc, masked, offset):
        """Non-blocking: flags manually line-wrapped paragraphs, list items,
        and quotes -- each should be one physical line, letting the viewer
        wrap it for display. Obsidian's reading view renders a bare '\\n'
        inside a paragraph as a real line break (unlike strict CommonMark),
        so hand-wrapped prose shows up as choppy, mid-sentence breaks.
        A heuristic on prose structure, not a structural correctness check
        -- kept as a warning, never a violation."""
        unit_type = unit_start = None
        unit_lines = 0

        def close_unit():
            nonlocal unit_type, unit_start, unit_lines
            if unit_type is not None and unit_lines > 1:
                self.report(doc, unit_start,
                             f"{WRAP_UNIT_LABELS[unit_type]} manually wrapped across "
                             f"{unit_lines} lines — write it as a single line; the "
                             "viewer wraps it for display", warning=True)
            unit_type = unit_start = None
            unit_lines = 0

        for number, line in enumerate(masked.splitlines(), offset + 1):
            if not line.strip():
                close_unit()
                continue
            if HEADING_LINE_RE.match(line) or FOOTNOTE_LINE_RE.match(line) or TABLE_LINE_RE.match(line):
                close_unit()
                continue
            if ITEM_LINE_RE.match(line):
                close_unit()
                unit_type, unit_start, unit_lines = 'item', number, 1
                continue
            if QUOTE_LINE_RE.match(line):
                close_unit()
                unit_type, unit_start, unit_lines = 'quote', number, 1
                continue
            # Plain prose: continues an open para/item/quote unit, or starts a new paragraph.
            if unit_type is not None:
                unit_lines += 1
            else:
                unit_type, unit_start, unit_lines = 'para', number, 1
        close_unit()

    def log(self, doc, text):
        previous = None
        active = False
        for number, line in enumerate(text.splitlines(), 1):
            if not line.strip() or (number == 1 and line.startswith('# ')):
                continue
            m = re.fullmatch(r'## (\d{4}-\d{2}-\d{2})\s*', line)
            if m:
                try:
                    current = date.fromisoformat(m[1])
                except ValueError:
                    self.report(doc, number, "Invalid log date")
                    continue
                if previous is not None and current >= previous:
                    self.report(doc, number, "Log dates must be unique, newest first")
                previous, active = current, True
            elif line.startswith('## ') or not active:
                self.report(doc, number, "Log entries require a ## YYYY-MM-DD heading")

    def document(self, doc, types):
        try:
            text = doc.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as exc:
            self.report(doc, 1, f"Cannot read UTF-8 document: {exc}")
            return
        try:
            fm, body, offset = parse_frontmatter(text)
        except (SyntaxViolation, RecursionError) as exc:
            self.report(doc, getattr(exc, 'line', 1), f"Frontmatter: {exc}")
            return  # A parse failure is always red, never a silent skip.
        position = lambda key: next((i for i, s in enumerate(text.splitlines(), 1)
                                    if re.match(rf'\s*(?:- )?{re.escape(key)}:', s)), 1)
        ids = {}
        relative = doc.relative_to(self.root / 'knowledge').as_posix()
        navigation_index = relative in NAVIGATION_INDEXES
        if relative == 'log.md':
            if fm is not None:
                self.report(doc, 1, "log.md must not contain frontmatter")
            self.log(doc, text)
        elif relative == 'index.md':
            if not isinstance(fm, dict) or fm.get('okf_version') != '0.2':
                self.report(doc, 1, 'Root index requires okf_version: "0.2"')
        elif not navigation_index:
            if fm is None:
                self.report(doc, 1, "Missing frontmatter")
                fm = {}
            for key in ('type', 'title', 'description', 'status'):
                if not nonempty(fm.get(key)):
                    self.report(doc, position(key), f"Missing/non-string field: {key}")
            if fm.get('type') not in types:
                self.report(doc, position('type'), "type is not in hub.json concept_types")
            if fm.get('status') not in ('draft', 'stable', 'deprecated'):
                self.report(doc, position('status'), "Invalid status")
            generated = fm.get('generated')
            if not isinstance(generated, dict) or not nonempty(generated.get('by')):
                self.report(doc, position('generated'), "generated requires nonempty by and at")
            timestamp = generated.get('at') if isinstance(generated, dict) else None
            try:
                if not isinstance(timestamp, str) or not re.match(r'^\d{4}-\d{2}-\d{2}T', timestamp):
                    raise ValueError()
                parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                if parsed.tzinfo is None or parsed.utcoffset() is None:
                    raise ValueError()
            except ValueError:
                self.report(doc, position('at'), "generated.at must be ISO 8601 datetime with timezone")
        # Validate sources whenever present, including indexes (not only required cases).
        fm = fm or {}
        layer = doc.relative_to(self.root / 'knowledge').parts[0]
        sources = fm.get('sources', [])
        if layer in ('10-silver', '20-gold') and not navigation_index and not sources:
            self.report(doc, position('sources'), "Silver/gold requires nonempty sources")
        if layer in ('10-silver', '20-gold') and not navigation_index:
            doc_key = fm.get('doc_key')
            if not nonempty(doc_key):
                self.report(doc, position('doc_key'), "Silver/gold requires a nonempty doc_key")
            elif not UUID_RE.fullmatch(doc_key):
                self.report(doc, position('doc_key'), "doc_key must be a UUID")
            elif doc_key in self.doc_keys:
                self.report(doc, position('doc_key'), f"Duplicate doc_key: {doc_key}")
            else:
                self.doc_keys.add(doc_key)
            classification = fm.get('classification')
            if classification is not None and classification not in (
                    'Public', 'Internal', 'Confidential', 'Secret'):
                self.report(doc, position('classification'),
                            "classification must be Public, Internal, Confidential, or Secret")
        if not isinstance(sources, list):
            self.report(doc, position('sources'), "sources must be a list")
        else:
            for source in sources:
                if not isinstance(source, dict):
                    self.report(doc, position('sources'), "Each source must be a mapping")
                    continue
                key = source.get('id')
                if not nonempty(key) or not re.fullmatch(r'[A-Za-z0-9_-]+', key):
                    self.report(doc, position('sources'), "Source id must use ASCII letters, digits, _ or -")
                elif key in ids:
                    self.report(doc, position('sources'), f"Duplicate sources[].id: {key}")
                else:
                    ids[key] = 'sources'
                resource = source.get('resource')
                self.local_file(doc, resource, position('resource'), source=True)
                if isinstance(resource, str) and resource.strip():
                    try:
                        candidate = (doc.parent / resource).resolve()
                        if candidate.is_relative_to(self.root):
                            self.referenced_resources.add(candidate)
                    except (ValueError, OSError, RuntimeError):
                        pass
        external_refs = fm.get('external_refs', [])
        if not isinstance(external_refs, list):
            self.report(doc, position('external_refs'), "external_refs must be a list")
        else:
            for ref in external_refs:
                if not isinstance(ref, dict):
                    self.report(doc, position('external_refs'), "Each external_refs entry must be a mapping")
                    continue
                key = ref.get('id')
                if not nonempty(key) or not re.fullmatch(r'[A-Za-z0-9_-]+', key):
                    self.report(doc, position('external_refs'),
                                "external_refs id must use ASCII letters, digits, _ or -")
                elif key in ids:
                    self.report(doc, position('external_refs'), f"Duplicate external_refs[].id: {key}")
                else:
                    ids[key] = 'external_refs'
                for field in ('hub', 'doc'):
                    value = ref.get(field)
                    if not isinstance(value, str) or not UUID_RE.fullmatch(value):
                        self.report(doc, position('external_refs'),
                                    f"external_refs[].{field} must be a UUID")
                operation = ref.get('operation')
                if operation not in ('cite', 'derive'):
                    self.report(doc, position('external_refs'),
                                'external_refs[].operation must be "cite" or "derive"')
                elif operation == 'derive' and nonempty(fm.get('doc_key')):
                    self.derive_found[doc] = fm.get('doc_key')
                classification = ref.get('classification')
                if classification not in ('Public', 'Internal', 'Confidential', 'Secret'):
                    self.report(doc, position('external_refs'),
                                "external_refs[].classification must be Public, Internal, "
                                "Confidential, or Secret")
                elif classification == 'Secret':
                    self.report(doc, position('external_refs'),
                                "external_refs[].classification must not be \"Secret\" — "
                                "Secret-classified material must not be externally referenced")
                if not nonempty(ref.get('note')):
                    self.report(doc, position('external_refs'), "external_refs[].note is required")
        masked, unclosed = self._mask_fences_and_spans(body, offset)
        if unclosed:
            self.report(doc, unclosed, "Unclosed fenced code block")
        self.markdown(doc, masked, offset, ids)
        if layer in ('10-silver', '20-gold') and not navigation_index:
            self.check_paragraph_wrapping(doc, masked, offset)

    def check_unreferenced_bronze(self, bundle: Path):
        bronze_dir = bundle / '00-bronze'
        if not bronze_dir.is_dir():
            return
        disposed = set()
        log_path = bundle / 'log.md'
        if log_path.is_file():
            try:
                text = log_path.read_text(encoding='utf-8')
            except (OSError, UnicodeError):
                text = ''
            for line in text.splitlines():
                m = NO_MATERIAL_RE.match(line.strip())
                if m:
                    disposed.add(m.group(1).strip('`,;.'))
        for path in sorted(p for ext in ('*.md', '*.txt') for p in bronze_dir.rglob(ext)):
            relative = path.relative_to(bundle).as_posix()
            if relative in NAVIGATION_INDEXES or relative in disposed:
                continue
            if path.resolve() not in self.referenced_resources:
                self.report(path, 1, "Bronze file not referenced by any sources[].resource "
                                      "and not logged as 'No material' in log.md", warning=True)

    def check_derive_requires_decision(self, bundle: Path):
        if not self.derive_found:
            return
        decisions_dir = bundle / '90-decisions'
        decision_text = ''
        if decisions_dir.is_dir():
            for path in sorted(decisions_dir.rglob('*.md')):
                if path.relative_to(bundle).as_posix() == '90-decisions/index.md':
                    continue
                try:
                    decision_text += path.read_text(encoding='utf-8') + '\n'
                except (OSError, UnicodeError):
                    continue
        for doc, doc_key in self.derive_found.items():
            if doc_key not in decision_text:
                self.report(doc, 1, "operation: derive requires a 90-decisions entry "
                                     f"mentioning this document's doc_key ({doc_key})")

    def run(self):
        config_path = self.root / 'hub.json'
        types = []
        try:
            if config_path.is_symlink():
                raise ValueError('hub.json must not be a symlink')
            if not config_path.is_file():
                raise ValueError('hub.json must be an existing regular file')
            config = json.loads(config_path.read_text(encoding='utf-8'),
                                object_pairs_hook=unique_object, parse_constant=reject_constant,
                                parse_float=finite_float)
            if not isinstance(config, dict):
                raise ValueError('hub.json must be an object')
            types = config.get('concept_types')
            if not isinstance(types, list) or not types or not all(nonempty(t) for t in types):
                types = []
                raise ValueError('concept_types must be a nonempty list of strings')
            if len(set(types)) != len(types):
                raise ValueError('Duplicate concept_types')
            if config.get('bundle_root') != 'knowledge' or config.get('okf_version') != '0.2':
                raise ValueError('This profile requires bundle_root=knowledge and okf_version=0.2')
            if config.get('profile_version') != '0.7.0':
                raise ValueError('This validator implements profile 0.7.0')
            hub_key = config.get('hub_key')
            if not isinstance(hub_key, str) or not UUID_RE.fullmatch(hub_key):
                raise ValueError('hub_key must be a UUID')
            if config.get('hub_category') not in ('competency', 'initiative'):
                raise ValueError('hub_category must be "competency" or "initiative"')
            if config.get('default_classification') not in (
                    'Public', 'Internal', 'Confidential', 'Secret'):
                raise ValueError('default_classification must be Public, Internal, '
                                 'Confidential, or Secret')
            policy = config.get('policy')
            if (not isinstance(policy, dict)
                    or policy.get('remote_copy') != 'required_after_validated_task'):
                raise ValueError('Profile 0.7.0 requires policy.remote_copy=required_after_validated_task')
            if policy.get('content_review') not in ('direct', 'required_pr'):
                raise ValueError('Profile 0.7.0 requires policy.content_review to be '
                                 '"direct" or "required_pr"')
            quality = config.get('quality', {})
            if (not isinstance(quality, dict) or quality.get('validator') != 'scripts/validate_hub.py'
                    or quality.get('metric') != 'violations' or type(quality.get('threshold')) is not int
                    or quality.get('threshold') != 0 or type(quality.get('max_fix_iterations')) is not int
                    or quality.get('max_fix_iterations', 0) <= 0
                    or quality.get('evidence_script') != 'scripts/check_evidence.py'):
                raise ValueError('Invalid quality contract (validator, metric, zero threshold, '
                                 'positive iteration budget, evidence_script)')
        except (OSError, UnicodeError, ValueError, RecursionError) as exc:
            self.report(config_path, 1, str(exc))
        bundle = self.root / 'knowledge'
        for relative in (*NAVIGATION_INDEXES, 'log.md'):
            if not (bundle / relative).is_file():
                self.report(bundle / relative, 1, "Required scaffold file is missing")
        if bundle.is_symlink():
            self.report(bundle, 1, "knowledge must not be a symlink")
            return
        # Walk explicitly: never follow symlinks and report directory read errors.
        def walk(folder):
            try:
                for path in sorted(folder.iterdir()):
                    if path.is_symlink():
                        self.report(path, 1, "Symlinks are not supported in knowledge")
                    elif path.is_dir():
                        walk(path)
                    elif path.suffix.lower() == '.md':
                        if not path.is_file():
                            self.report(path, 1, "Markdown documents must be regular files")
                        else:
                            self.document(path, types)
            except OSError as exc:
                self.report(folder, 1, f"Cannot scan directory: {exc}")
        walk(bundle)
        self.check_unreferenced_bronze(bundle)
        self.check_derive_requires_decision(bundle)


def main():
    validator = Validator(Path(__file__).resolve().parent.parent)
    if len(sys.argv) != 1:
        validator.report(validator.root / 'scripts/validate_hub.py', 1,
                         'No arguments supported; validates the hub containing this script')
    else:
        validator.run()
    result = {"violations": len(validator.errors), "errors": validator.errors,
              "warnings": validator.warnings}
    print(json.dumps(result, ensure_ascii=False))
    for label, items in (('error', validator.errors), ('warning', validator.warnings)):
        for item in items:
            print(f"{item['file']}:{item['line']}: {label}: {item['message']}", file=sys.stderr)
    return 1 if validator.errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
