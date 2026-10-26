# Knowledge processing contract — profile 0.9.0

This contract describes work inside a single hub. The OKF 0.2 bundle covers
only `knowledge/`. Configuration and instructions in the parent directory
are not part of the bundle. The additional rules below are a local working
profile, not OKF requirements.

## Layers and provenance

| Location | Contents | Working rule |
|---|---|---|
| `00-bronze` | text versions of sources after extraction/transcription | preserve the input; later versions as new files |
| `10-silver` | concepts, principles, syntheses, contradictions | extend existing knowledge while preserving attribution |
| `20-gold` | outputs for a specific use case | describe the audience, how to use it, and the limitations |
| `90-decisions` | corrections and user decisions | record the scope, reason, and the documents covered by the decision |

New material must carry provenance identification. For a recording, keep
the original's location, the transcription version, and timestamps, if
available. Record gaps in that information instead of inventing it. Don't
reduce a source to a summary before the available full text is preserved
in bronze.

### Source freshness and supersession

A document may optionally record `retrieved_at` (an ISO 8601 datetime
with timezone — the "fetched this source on" fact, distinct from
`generated.by`/`generated.at`'s "transcribed/extracted this copy on")
and `source_ref` (a nonempty free-text version identifier for the
retrieved copy — a Git commit hash, an HTTP ETag, a documented page
revision, anything that pins down which version was captured). Both
are optional; add them when the source actually carries a meaningful
version signal, not by inventing one when it doesn't.

When a source changes and the hub needs a fresher copy, add a new
bronze file rather than editing the old one in place — bronze
preserves the accepted version of an input (see AGENTS.md). Point the
new file's `supersedes` field at the old one (a local file reference,
same rules as `sources[].resource`), and set the old file's own
`status` to `deprecated`. `validate_hub.py` enforces the second half
of that pair: a `supersedes` target whose `status` isn't `deprecated`
is a hard error — a "this replaces that" claim the old file doesn't
actually reflect is worse than no claim at all. A silver/gold document
whose `sources[].resource` still points at a superseded bronze file
gets a non-blocking warning naming the newer file; act on it with the
cascade-update step in "Add material to the base" below. `supersedes`
only makes sense between documents that carry a `status` field, so it
points at another `.md` document, not a raw `.txt` dump.

Example:

```yaml
---
type: Source
title: Vendor pricing page (2026-10)
description: Captured pricing tiers, refreshed from the 2026-04 version.
status: stable
generated:
  by: human:editor
  at: 2026-10-24T10:00:00Z
retrieved_at: 2026-10-24T09:40:00Z
source_ref: page revision 2026-10-18
supersedes: vendor-pricing-page-2026-04.md
---
```

## Documents and references

Every `.md` file in the bundle has YAML frontmatter with document metadata,
except for the closed list of navigation files and the main log (paths
relative to the hub):

- `knowledge/index.md`;
- `knowledge/00-bronze/index.md`;
- `knowledge/10-silver/index.md`;
- `knowledge/20-gold/index.md`;
- `knowledge/90-decisions/index.md`;
- `knowledge/log.md`.

Other files named `index.md` or `log.md`, e.g.
`knowledge/20-gold/ebook/index.md`, are ordinary documents, not exceptions.
Locally we require `type`, `title`, `description`, an explicit `status`,
and `generated` information matching real authorship. Silver and gold
also require `sources` and a `doc_key`. The starter types are in
`hub.json`; they can be deliberately extended.

Example skeleton for a new concept — the time, authorship, and `doc_key`
values must be replaced with real data, and the referenced source must
exist:

```yaml
---
type: Method
title: Customer problem interview
description: Scenario for gathering concrete examples of the problem.
tags: ["marketing", "research"]
status: draft
doc_key: 7c1e2b9a-4f3d-4a11-9c0e-2a6b8d5f10e4
sources:
  - id: material-a
    resource: ../00-bronze/material-a-v1.md
    title: Input material A
---
```

When actually writing, add a `generated` block with `by` and `at` fields,
with a correct actor (e.g. `process:name`, `human:identifier`, or
`vendor/version`) and an ISO 8601 timestamp with timezone. Don't copy a
fictitious model name from the examples. Generate `doc_key` the same way —
with the real tool, not invented: run
`.venv/bin/python -c "import uuid; print(uuid.uuid4())"` in the hub and
use that value.

In the text, the footnote `[^material-a]` links a claim to `sources[].id`.
The footnote definition specifies the page, section, or time, **and
includes a clickable relative Markdown link to the cited resource**, not
page/section prose alone — e.g. `[^material-a]: Section 2. [Source](../00-bronze/material-a-v1.md)`.
`sources[].resource` in frontmatter is what the validator checks for
existence; it's a plain YAML string, not something Obsidian's Graph View
resolves into an edge, and wikilinks aren't supported in this contract
(see the link-checking rules below) — so the footnote's own Markdown link
is what makes a silver/gold document visibly connect to its bronze
sources when browsing the vault. Use standard relative Markdown links and
stable ASCII file names. When moving a file, update links and source
pointers. A concept's identity in OKF comes from its path relative to the
bundle root.

## Stable identity

`doc_key` and `hub.json`'s `hub_key` exist because paths and names can
change but a stable reference target shouldn't. Within one hub, a moved
or renamed file is fine — `validate_hub.py` sees every link and every
file in the same run and catches a broken reference immediately, so
OKF's path-based identity (above) is a safe foundation for intra-hub
links. Nothing today plays that same role *across* hubs: if a cross-hub
reference pointed at a file path instead, a rename on the other end could
break it silently, forever, with no validator on either side ever seeing
both halves of the link to catch it. `doc_key` doesn't change how
intra-hub links or footnotes work — it's additive, generated once when a
document is created, and never touched again regardless of later renames
or moves.

`hub_key` and `doc_key` are the foundation the citation mechanism below is
built on — see "Cross-hub references."

The navigation indexes from the list above don't replace knowledge
documents. `knowledge/index.md` is the one exception that holds static
links — four, one per layer, fixed in number — and requires
`okf_version: "0.2"` frontmatter. The four layer indexes
(`00-bronze/index.md`, `10-silver/index.md`, `20-gold/index.md`,
`90-decisions/index.md`) don't require document metadata, and don't hold
a manually maintained list of links either: each one carries a short
layer description plus a Dataview query (a fenced ` ```dataview ` block)
that lists that layer's documents by `type`/`title`/`status` dynamically.
Adding or removing a document never requires editing its layer's
index — the query reflects the current state on its own, and a growing
hand-written link list would otherwise turn that index into a
high-degree hub node that dominates Obsidian's Graph View, crowding out
the real concept-to-concept and concept-to-source connections. Dataview
is a purely optional viewing layer: the agent and the validator never
read it, and without the plugin installed, Obsidian just shows the raw
query block instead of a rendered table. `knowledge/log.md` has entries
under `YYYY-MM-DD` dates, newest first, with no frontmatter. The log
documents changes; it doesn't replace sources or user decisions.

The "No material" disposition (see "Add material to the base" below) is
recorded as a separate line under the date, in the format `- No material:
<path relative to knowledge/>`, e.g.
`- No material: 00-bronze/newsletter-2025-03.md`. This path is
machine-readable: `scripts/validate_hub.py` and `scripts/check_evidence.py`
exclude a bronze file marked this way from the warning about sources not
referenced by any `sources[].resource`.

## Cross-hub references

`hub_key` and `doc_key` make it safe to point at another hub's document
without depending on its current path or title. This section defines how:
a closed classification system that decides what's safe to move across a
hub boundary at all, and `external_refs[]`, the frontmatter array that
records an actual reference once classification says it's allowed.

### Classification

Every hub has a `default_classification` in `hub.json` — one of `Public`,
`Internal`, `Confidential`, `Secret`. A document's own `classification`
frontmatter field is optional and overrides the hub default for that one
document when present; when absent, the hub default applies. The four
levels:

- **Public** — citable and quotable anywhere, including in an
  external-facing deliverable, with no further handling.
- **Internal** — fine to reference across the user's own hubs, but not
  meant to land verbatim in something that leaves the user's hands (a
  client-facing document, a public page).
- **Confidential** — never copied verbatim across a hub boundary.
  Reference it only by pointer (a `cite` entry whose `note` stays
  abstract) or use it as the basis for a `derive` entry that writes new,
  anonymized content. See "Cite vs. Derive" below.
- **Secret** — never referenced cross-hub at all, not even by pointer or
  acknowledgment. An `external_refs[]` entry with `classification:
  "Secret"` is always a hard validator error, regardless of the target
  or the `operation`: declaring the citation is itself the violation.

Classification is declared, not inferred — the validator trusts the
value it's given. It's agent judgment and user review that decide
whether a document is marked correctly in the first place, same as every
other frontmatter field in this contract.

### `external_refs[]`

A silver or gold document may carry an `external_refs[]` array alongside
`sources[]`. Each entry:

```yaml
external_refs:
  - id: azure-bluegreen
    hub: 3f29b9b2-6e1a-4b7e-9a2a-8e4b1f0c7d21
    doc: 7c1e2b9a-4f3d-4a11-9c0e-2a6b8d5f10e4
    classification: Internal
    operation: cite
    note: "Blue-green deployment pattern, cited from a competency hub."
```

- `id` shares the same uniqueness and footnote namespace as
  `sources[].id` — `[^azure-bluegreen]` in the body resolves against
  either array, and an `id` can't be reused between them.
- `hub` / `doc` are the target's `hub_key` / `doc_key`. The validator
  only checks they're UUID-shaped; it never opens, fetches, or otherwise
  reads the other hub. It can't tell you whether the target document
  still exists, still means what the `note` says it means, or is itself
  classified consistently with this reference — that's a judgment made
  once, by whoever adds the entry, the same way `content_review`'s
  branch-merge rule and `remote_copy`'s push obligation are agent
  judgment calls the validator can't verify from inside one hub.
- `classification` is the level asserted for the cited material in this
  reference. Always required; always a hard error when `"Secret"`.
- `operation` is `"cite"` or `"derive"`, required, with no default — a
  field this consequential doesn't get a silent fallback, the same
  reasoning behind `hub_category` and `content_review` having none.
- `note` is required, non-empty prose explaining the reference. It must
  never name the source hub or client in plain text, even for a `derive`
  entry that deliberately keeps a provenance trail — see below.

### Cite vs. Derive

**Cite** is a read-only pointer: nothing from the target is copied in.
The citing document says, in its own words, what the cited material is
and why it's relevant; the `[^id]` footnote and the `hub`/`doc` pair are
the actual reference.

**Derive** is not a copy either. It's new, original content the agent
writes locally — in bronze or silver, under the same rules as any other
material — generalizing or anonymizing something from the target hub so
the result is safe to hold in this one. The `note` is where that
anonymization gets explained ("figures generalized to a range, client
identity removed"), but, like `cite`, it must never say which hub or
client the material came from. Traceability survives entirely in the
opaque `hub`/`doc` UUIDs: anyone holding both hubs can follow the link;
no one reading only this hub's content ever sees the source named.

`operation` always describes *this citing document's own authorship
act* toward the referenced hub/doc — never a claim about the target
document's provenance. A cited document could itself be the product of
some other Derive in its own hub; that has no bearing on whether *this*
particular reference is a Cite or a Derive.

Every `derive` entry anywhere in the hub requires a corresponding entry
in `knowledge/90-decisions/` whose text literally mentions the deriving
document's own `doc_key`. Not just the existence of some decision file —
`validate_hub.py` reads every non-index document under `90-decisions/`
and reports a violation unless the specific `doc_key` string shows up
somewhere in that text. This keeps the check from being permanently
satisfied by one old, unrelated decision the hub happens to already
have; it's still a presence/pattern check, not proof the anonymization
itself is adequate — that remains a human judgment the decision entry
should actually record.

A `Confidential` `external_refs[].note` is also scanned mechanically by
`check_evidence.py`, reusing its existing number/date candidate
extraction, and flagged (non-blocking) if it contains a high-signal
figure. The `Secret` hard-block in `validate_hub.py` only catches a
reference that admits its own classification; the likelier real mistake
is a `Confidential` citation whose free-text `note` leaks a specific
number or date that was supposed to stay abstracted. This check exists
for that gap.

### Scope and rollout

Cross-hub edits go through the hub's existing `policy.content_review`
like any other content change — there's no special routing for an
`external_refs[]` edit, and no code treats one differently from a
same-hub edit.

This is not the same mechanism 0.2.0 removed. Cross-hub `imports` was
content *sync* — copying or merging another hub's knowledge wholesale,
with the risk that a rename or edit on one side silently diverged from
the other with no validator watching both. Cite is a pointer, not a
copy; Derive is deliberately-authored new content with an explicit
provenance note. Neither re-introduces the sync problem 0.2.0 was
removing.

Citation needs both hubs on profile ≥0.5.0: the target needs a
`doc_key`, which only exists from 0.4.0 onward, and the citing hub needs
the `external_refs[]` schema itself, which starts here. A single hub
upgrading alone gains nothing from this section until a second hub is
also ready to be a citation target.

## Structure check

`.venv/bin/python -B scripts/validate_hub.py` checks the hub containing the
script, not the current working directory. Python 3.10+, standard library
only, no network access, no writes. This is a validator for local profile
0.9.0, not the full OKF. Scripts always run inside the local virtual
environment. If `.venv` doesn't exist, the agent creates it beforehand with
`python3 -m venv .venv` in the hub directory. On Windows the interpreter is
at `.venv/Scripts/python.exe`. No system-wide installs; any packages only
through the venv interpreter with `-m pip`. The validator doesn't create
the environment or install anything.

Checks:

- the required scaffold files, the `hub.json` configuration, and every
  `.md` file under knowledge;
- `profile_version: "0.9.0"` and
  `policy.remote_copy: "required_after_validated_task"`;
- document frontmatter (outside the closed exception list above): `type`,
  `title`, `description`, `status`, `generated`; `type` must be in
  `concept_types`, `status` must be one of `draft`/`stable`/`deprecated`;
- `generated.by` is a non-empty string, `generated.at` is an ISO 8601 date
  and time with `T` and a timezone (e.g. `2026-09-23T12:00:00Z` or
  `2026-09-23T14:00:00+02:00`);
- non-empty `sources` in silver and gold documents, unique ids, existing
  files pointed to by `resource`; `id` consists of ASCII letters, digits,
  `_` and `-`;
- used footnotes have a definition and a `sources[].id`; unused ids
  produce a warning;
- relative Markdown links point to existing files;
- the main `knowledge/index.md` declares `okf_version: "0.2"`;
- `knowledge/log.md` has no frontmatter; entries sit under `## YYYY-MM-DD`
  headings, with valid, non-repeating dates from newest to oldest. An
  empty log may contain only the H1 heading and blank lines;
- a file under `00-bronze` not referenced by any `sources[].resource` and
  not logged as "No material" produces a warning, not an error (see
  "Grounding Invariant" below);
- in silver/gold documents, a manually wrapped paragraph, list item, or
  blockquote produces a warning, not an error (see "Content quality");
- `hub.json`'s `conventions` list and the `conventions/` directory stay
  consistent: a declared name with no file is an error, a file with no
  declaration is a warning (see "Conventions").
- if present, `retrieved_at` is an ISO 8601 datetime with timezone, and
  `source_ref` is a nonempty string;
- if present, `supersedes` points to an existing local document, not to
  itself, and that document's `status` is `deprecated`, else an error;
  a silver/gold source pointing at a superseded bronze file produces a
  warning, not an error (see "Source freshness and supersession").

stdout output is a single JSON object: `violations` (error count), `errors`
and `warnings` (lists of `file`, `line`, `message` objects). stderr
contains readable `file:line: error/warning: message` lines. Exit code 0
occurs only when `violations == 0`. Warnings don't increase `violations`.
In `hub.json`:

```json
"quality": {
  "validator": "scripts/validate_hub.py",
  "metric": "violations",
  "threshold": 0,
  "max_fix_iterations": 5,
  "evidence_script": "scripts/check_evidence.py"
}
```

The agent runs the first check, then at most 5 fix/check cycles. After
exhausting the budget, or on suspicion of a checker bug, it stops and
presents the result to the user. It doesn't fix files outside the assigned
scope. It doesn't modify the validator, the threshold, the budget, or
contract rules to get a green result. Changing the check requires a
separate request, a branch, and a PR without auto-merge. Content/sources
must not be deleted, and metadata must not be falsified, just to get a
result.

As in the quality rules below, green doesn't confirm the truthfulness of
the content. Files and settings are editable: this rule isn't a
system-level safeguard against an author who could change the validator's
code. Protection for contract changes comes from a separate review
process; the validator doesn't prove completeness or authenticity.

### Supported frontmatter subset

Frontmatter starts on the first line with `---` and ends on a separate
`---` line. At the top is a map. ASCII keys: letters or `_`, then also
digits and `-`. Duplicate keys are an error, including in inline maps.
Indentation: multiples of two spaces, exactly two per level; no tabs. Up
to 10 levels of indentation. Blank lines are allowed.

- Text values: a single line of unquoted text, a JSON string in double
  quotes, or a single-quoted string (an internal apostrophe as `''`).
  `: ` and ` #` require quoting.
- Block maps `key:` with fields one level deeper, and lists `- value` or
  `- key: value` with further fields at the next level.
- Inline collections only in JSON syntax, e.g. `["tag-a", "tag-b"]` and
  `{"by": "human:editor", "at": "2026-09-23T12:00:00Z"}`. JSON also allows
  finite numbers, bool, and null, but required text fields of the document
  must still be non-empty strings.
- Unquoted numbers and YAML words like true/null/yes/no are not text under
  this profile; quote them. ISO dates can be written as text without
  quotes.
- YAML comments, anchors/aliases, merge keys, YAML tags, `|`/`>` blocks,
  multiline scalars, and non-JSON inline collections are unsupported. The
  parser reports a violation; it never silently ignores such a construct.

Example block (replace the author and time with real values when writing):

```yaml
generated:
  by: human:editor
  at: 2026-09-23T12:00:00Z
sources:
  - id: material-a
    resource: ../00-bronze/material-a-v1.md
    title: Input material A
```

### Scope of links and sources

`resource` must point to a local file inside the hub, relative to the
document. Record the origin URL separately, e.g. `origin_url` in the
bronze note. A bare URL in `sources.resource` isn't enough for this local
check. Raw text can be kept as `.txt` and described by a bronze note with
metadata; don't change a historical source just to satisfy new rules.

Hubs stay independent: there's no `imports` directory, knowledge packages,
or sync between hubs. When the user points to an additional hub as
material for a task, it can be read without copying its knowledge. Write
the result only into the designated target hub. Record a supporting trace
as plain text in the content, e.g. "Additional context: sales hub, SPIN
document, read 2026-09-23"; add the version if known. This doesn't require
a YAML field or a Markdown link between repositories. This note isn't
checked by the validator and doesn't replace required local sources or
footnotes. Don't add fake local sources: if a piece of work relies solely
on another hub, report the limitation of the current contract instead of
claiming correct local attribution.

Inline links (including images), reference links `[text][id]`, `[id][]`,
and `[id]` with a definition `[id]: path` are checked. A link definition
fits on one line; an optional title in quotes or parentheses. Write paths
with spaces inside `<...>` or URL-encoded. Nested brackets in labels and
paths, and backslash escapes, are supported. Footnotes take the form
`[^id]` and a separate definition `[^id]: ...`; the definition alone
doesn't count as a use.

`#heading` fragments and query strings aren't validated; only the file is
checked. HTTP/HTTPS/mailto links aren't visited. Absolute paths, escaping
outside the hub, symlinks inside knowledge and in link targets, and
wikilinks/HTML a/img are errors. Examples inside fenced code blocks
(backticks or tildes, at the top level) and inline code aren't links; an
unclosed fence is an error. Indented code is not exempt from checking —
use fenced code for literal examples. This is a documented Markdown
profile, not a full CommonMark parser.

## Grounding Invariant

Every load-bearing number, date, and direct quote in `10-silver` and
`20-gold` must be found verbatim in the content of the files pointed to by
that document's `sources[].resource`. Compilation *establishes* this
invariant (locate the value before writing — see "Content quality" below);
`scripts/check_evidence.py` *verifies* it after the fact: it greps
high-signal numbers (suffixed or large, decimal, ISO dates, longer quotes)
in the combined content of all the document's `sources[].resource`. The
rest — small, ambiguous values — stays with the compile-time rule and
human judgment.

This is a report, not a quality gate: the script always exits with code 0
and never counts toward `violations` or the `hub.json` threshold. A
"fidelity suspect" is a candidate, not a verdict — derived values and
proper names will show up too; judging them is the reader's job. Run
`.venv/bin/python -B scripts/check_evidence.py` from the hub directory (no
arguments — the script always checks the hub it lives in, like
`validate_hub.py`). The report also lists `00-bronze` files not referenced
by any `sources[].resource` and not logged as "No material" — the same
warning `validate_hub.py` gives.

The check tests a candidate against the sum of all the document's
`sources[].resource`, not against the one source nearest a specific
`[^id]` footnote. This is a deliberate choice: real grounding errors are
almost always "value absent from any source," which a whole-document check
already catches; anchoring precisely to a single footnote would only guard
against a failure mode that doesn't occur in practice. This script and the
above decision are an adaptation of `scripts/check_evidence.py` from
`Astro-Han/karpathy-llm-wiki` (MIT) — an independent implementation of the
same Karpathy idea, with a different (blockquote-based, no-frontmatter)
document convention. See "Inspirations" in the generator repository's
README.

## Content quality

- Preserve applicability conditions, exceptions, and discrepancies between
  sources.
- Mark your own synthesis or hypothesis explicitly. Filling a gap requires
  source material or a clearly labeled hypothesis, not simulated
  attribution.
- Gold means prepared for use, not automatic approval. For procedures,
  separate the action steps, the rationale, and supporting materials, if
  that improves usability.
- A conversation that ends with a valuable analysis can feed the wiki,
  preserving provenance and distinguishing decisions, observations, and
  claims.
- Content preserves the language of the source material. Don't translate
  bronze/silver/gold into English or any other language unless the user
  explicitly asks for it — this contract being written in English doesn't
  set the language of the knowledge itself.
- Write each paragraph as a single logical line in the source file — don't
  manually wrap prose at a fixed column width with a line break every
  ~80-100 characters. A single `\n` inside a paragraph isn't always a
  soft break: Obsidian's default reading view (unlike strict CommonMark)
  renders it as a real line break, so hand-wrapped prose shows up as
  choppy, mid-sentence breaks instead of a flowing paragraph. Let the
  editor or viewer wrap text for display; break the source only between
  paragraphs (a blank line) or for genuine structure (a list item, a
  blockquote). `validate_hub.py` flags a manually wrapped paragraph,
  list item, or blockquote (a unit spanning more than one physical
  line) as a non-blocking warning — a heuristic on prose structure, not
  a structural correctness check, so it's a candidate for review, never
  a violation. A blockquote written the conventional way, with `>` on
  every physical line, isn't flagged; only a unit built by hard-wrapping
  plain prose is.
- When a new source challenges or invalidates a specific claim, don't
  silently overwrite it. Mark it with a block inserted directly under the
  claim, separate from the whole document's `status` field (the latter
  describes the whole file, not a single sentence):

  ```
  > **Status: Disputed**
  > {the competing claims, each with source attribution}

  > **Status: Outdated** (YYYY-MM-DD)
  > {what changed and what the current understanding is, with attribution}
  ```

  The old text stays in place, only flagged — the wiki's history doesn't
  disappear. `scripts/check_evidence.py` skips the explanation under such
  a block when looking for evidence; it's an editorial annotation, not a
  claim to re-ground.

## Conventions

A hub can declare optional, pluggable style or language conventions on
top of this contract — plain Markdown files, not a vendor-specific
skill format, so any agent that reads `AGENTS.md` and follows its
instructions picks them up, regardless of which model or tool it runs
on. This exists because a rule like "this project's dash character is a
plain hyphen, not an en dash" is a deliberate choice for *this* hub, not
something every hub in every language should be forced to follow — it
doesn't belong in the universal contract above.

`hub.json`'s `conventions` field is a list of names. Each name `<name>`
must have a corresponding `conventions/<name>.md` file at the hub
root — outside `knowledge/`, since the OKF bundle boundary doesn't cover
this. Declaring a name with no matching file is a hard error, the same
severity class as a missing `sources[].resource`: a dead reference.
A `conventions/<name>.md` file present on disk but never declared
produces a warning, not an error, since it might be mid-addition.

A convention can come from two places, and the validator treats them
identically once they're in the hub:

- the generator's own library
  (`skills/create-knowledge-hub/assets/conventions/`), requested at
  creation time via `--conventions name1,name2`;
- added by hand later — create `conventions/<name>.md` and add `<name>`
  to `hub.json`'s `conventions` list. Nothing distinguishes an
  engine-seeded convention from a hand-added one once it's registered.

A convention file is plain prose guidance for the agent, read via
`AGENTS.md` before writing content — it isn't itself validated for
content, and the validator has no opinion on what it says. Some
well-known convention names additionally get an optional, non-blocking
mechanical backstop in `validate_hub.py`. Currently: `polish-typography`,
which flags a Unicode en dash "–" or em dash "—" in silver/gold body
text (prose, list items, headings, and blockquotes alike — not just
fenced code, which stays excluded) as a warning, since this project
uses a plain hyphen "-" as its dash character. A declared convention
with no matching backstop is purely advisory, and that's expected —
most convention names will never need one.

## Agent work

These are three independent actions. Combine them only when the user asks
for several at once. In each, pull context through indexes, related
concepts, and earlier user decisions; don't load the whole library without
need.

### Add material to the base — bronze and silver

1. Accept the source into a new bronze file. Check existing inputs to
   avoid a duplicate. An automatic hash registry is planned, not
   installed. When the source is a fresher copy of something already in
   bronze, add it as a new file with `supersedes` pointing at the old
   one, and set the old file's `status` to `deprecated` — see "Source
   freshness and supersession" above.
2. Before editing silver, determine the disposition by searching the
   existing wiki for the source's key concepts and synonyms: **New** (new
   articles), **Update** (merge into existing ones), **Disputed**
   (contradicts existing content — can combine with New/Update, see the
   `Status:` block in "Content quality"), **No material** (nothing beyond
   what the wiki already has — excludes the others). For "No material,"
   leave the file in bronze, log the disposition in the format from
   "Documents and references," and stop; don't force an article out of a
   thin source.
3. Extend the connected silver wiki: concepts, methods, examples, and
   syntheses with references to sources. Merge new information with
   existing content, preserving applicability conditions, exceptions, and
   discrepancies. This is reusable knowledge, not just a separate summary
   of each input or a shortcut for one future output.
4. Check for cascade effects: search the whole silver layer for the same
   entities and aliases (don't stop at the index) and update every
   materially affected document, refreshing its Updated date. On a
   contradiction, mark both places with a `Status:` block and cross-link
   them, instead of silently overwriting the older entry. After
   superseding a bronze file, this search also covers every silver/gold
   document still citing the old one — `validate_hub.py` surfaces these
   as a non-blocking warning naming the newer file, but finding and
   updating the citations themselves is this step, not an automatic
   process.
5. Don't require a business goal and don't create gold. If new knowledge
   affects existing gold, point that out and propose an update; don't
   apply it automatically without a request.

### Answer a question about the base — Query

By default this writes nothing; it's a separate action from the other two.

1. Search `knowledge/index.md` and the full text of silver/gold for the
   question's topic and its synonyms before concluding the base has no
   knowledge — and say explicitly that both were searched. Don't base the
   answer on the model's own knowledge when the base has material on the
   topic.
2. Answer in the conversation, citing links to silver/gold articles. Don't
   write files until the user explicitly asks for it.
3. On the request "archive this answer," save it as a new document in
   `10-silver` (type `Synthesis`, `sources[]` pointing to the cited
   silver/gold articles — not bronze, since this isn't primary source
   material) and add an entry to `knowledge/log.md`. `10-silver/index.md`
   needs no edit — its Dataview query picks the new document up on its
   own. Always a new document; don't merge the archive into an existing
   article, since it's a synthesized answer, not source material.

### Prepare material for a specific purpose — gold

1. Determine the result, topic, and required form from the request. Use
   the existing silver; don't require adding new source material.
2. Create a directory under `20-gold`, e.g. `ebook-on-xyz`,
   `flashcards-xyz`, or `instagram-posts-materials`, and prepare the
   requested output. Keep references to silver and the provenance path to
   the sources in bronze.
3. For missing details and exact quotes, go back to the relevant bronze
   sources. Don't re-analyze all the raw data from scratch. If the base
   isn't enough, point out the gaps; don't replace them with invented
   facts or citations.
4. When the concept changes, create a new gold directory, keeping the
   previous result. Update the existing one when the user asks for a
   correction or update to it. Don't create directories speculatively;
   don't impose the PARA model.

After each action, check links and footnotes, update the relevant indexes
and the log. Present the changes and open questions. A structure check
doesn't prove the content is true. Record corrections and decisions you
receive in `90-decisions`, so future runs take them into account.

For parallel work, drafts have separate save locations; one agreed-upon
merge publishes the result. Don't launch additional agents just because
the contract describes the possibility of parallel work.

## Approval and changes

`status` has the values `draft`, `stable`, `deprecated`. Initially, an
agent's drafts are `draft`. Moving to `stable` rests on a user decision or
a later, explicitly established policy for that process.

The `verified` field describes a content check, not mere consent to use
it. The agent doesn't grant itself human verification. It may record the
actual result of a user's review, indicating the decision and the scope
of content checked. After a substantive change, the earlier verification
stays in the old version's history; the new one requires a fresh check. A
future approval mechanism should tie the decision to a content hash.

The optional `stale_after` marks the need for a review over time. Don't
renew freshness just because the document was regenerated.

## Autonomy and ownership

Three separate scopes: wiki editing, publishing drafts, and operational
actions. `hub.json` describes the initial policy: the agent prepares
drafts, publication requires acceptance, operational actions are disabled.
This is a working instruction, not a technical permission control.

```json
"policy": {
  "knowledge_editing": "agent_drafts_with_user_review",
  "publication": "explicit_acceptance",
  "external_actions": "disabled",
  "remote_copy": "required_after_validated_task",
  "content_review": "direct"
}
```

`remote_copy` explicitly states the Git-copy obligation, independent of
the other two scopes: `publication` concerns accepting drafts for
publication, and `external_actions` concerns operational actions, e.g.
changing a campaign budget. The field doesn't pick a remote and doesn't
authorize sending to just any destination. It's required under profile
0.9.0. A missing or different value is a contract inconsistency, not a
local-work mode. An instruction for local-only work is an exception for
the task, not a configuration change. An older hub without this field
hasn't automatically adopted this rule; it needs an explicit contract
update.

`content_review` decides how content (sources, drafts, indexes, log,
decisions) gets saved, independent of `kind` — `kind` describes a hub's
purpose, not its number of contributors, so it isn't a proxy for this.
`"direct"` is today's behavior: content commits and pushes straight to the
agreed main branch as a draft, same as before this field existed.
`"required_pr"` routes content through the same branch + PR + review
procedure already used for contract changes, with no self-merge — useful
once more than one person or agent writes to the same hub, to avoid
silent overwrites. It's required under profile 0.9.0, with the same rule
as `remote_copy`: a missing or different value is a contract
inconsistency, not a default, and an older hub without the field hasn't
adopted either value automatically.

Saving drafts to the agreed Git repository is part of editing, not
publishing drafts or an operational system action. The agent commits and
pushes after every completed, checked task, and after consistent stages
of longer work, per the "Ongoing remote copy" section in AGENTS.md. It
doesn't wait for a separate push request; it does respect an instruction
for local-only work. A missing confirmed push requires an explicit report
that there's no current copy. The validator doesn't check Git or backups.
The copy covers only pushed, version-controlled files, not external
originals. The generator doesn't configure a remote.

Don't bring another owner's data into the hub without a task that covers
it. Don't copy secrets into the knowledge base. Reading another hub
doesn't imply consent to change it or move its content into the target
hub. Changing knowledge doesn't grant authority to change a budget or
company configuration.
