# Source freshness and supersession — 0.8.0 → 0.9.0

Bronze preserves the accepted version of an input; the contract has said
so since early on ("later versions as new files" in SCHEMA.md's
provenance table, "a source correction is a new version" in AGENTS.md).
In practice that rule had no name, no field, and no check behind it: an
agent refreshing a stale source had no formal way to say "this file
replaces that one," and nothing nudged anyone back to the silver/gold
documents still citing the old copy. This isn't automatic freshness
detection — no hashing, no polling, no fetching (see "Deliberately not
built" in the root README, which stays accurate: new knowledge still
enters only as a new file via ingest). It's the missing vocabulary and a
mechanical check around a workflow this project already committed to.

A related gap sits across the hub boundary: `external_refs[]` has no
file to point a `supersedes`-like field at, and the validator never
opens the other hub to check anything in it (see "Cross-hub
references" in SCHEMA.md — this is deliberate, not an oversight this
release fixes). `external_refs[].cited_as_of` doesn't close that gap;
it just records the one fact the citing hub actually has: when its own
agent last looked at the target. No check, no staleness computation —
a starting point for a human, not an automated one.

Profile 0.9.0 adds four optional fields, three on any document and one
on `external_refs[]` entries:

- `retrieved_at` — an ISO 8601 datetime with timezone, the "fetched this
  source on" fact, distinct from `generated.at`'s "transcribed/extracted
  this copy on."
- `source_ref` — a nonempty free-text version identifier for the
  retrieved copy: a Git commit hash, an HTTP ETag, a documented page
  revision, anything that pins down which version was captured.
- `supersedes` — a local file reference (same rules as
  `sources[].resource`) pointing at the old document this one replaces
  as the current version of the same source. Only makes sense between
  two `.md` documents, since only a document carries a `status` field.
- `external_refs[].cited_as_of` — an ISO 8601 date on a cross-hub
  citation entry, recording when the citing agent last looked at the
  target. Unlike `supersedes`, there's no mechanical check behind this
  one at all; see above.

`validate_hub.py` checks the pair mechanically: a `supersedes` target
whose own `status` isn't `deprecated` is a hard error — the old file has
to actually say it's superseded, not just be pointed at. A silver/gold
document whose `sources[].resource` still points at a file that's been
superseded gets a non-blocking warning naming the newer one. The warning
is the nudge; finding every affected citation and deciding whether (and
how) to update it is the existing cascade-update step in "Add material
to the base," now explicitly extended to cover this case too — not a new
automated process.

**No breaking CLI change.** All four fields are optional document
frontmatter, not `hub.json` or CLI surface — `create_hub.py`'s arguments
are unchanged.

## Adoption in an existing hub — 0.8.0 → 0.9.0

1. Check its contract, Git state, push address, branch, and agreed
   access. Keep local changes; don't run the generator on an existing
   directory.
2. On a separate branch, set `profile_version` to `0.9.0` in `hub.json`.
   No other `hub.json` field changes.
3. Carry over from the template `SCHEMA.md` (the new "Source freshness
   and supersession" section, the two new "Structure check" bullets, the
   cascade-effects sentence in "Add material to the base," and the new
   `cited_as_of` bullet in "Cross-hub references") and `AGENTS.md` (the
   extended paragraph on bronze versioning), if the hub keeps its own
   copies. Resolve collisions with local policy; don't overwrite whole
   files.
4. No backfill is required: existing bronze/silver/gold documents are
   valid as-is. The new fields only apply going forward, the next time a
   source is actually refreshed or a `retrieved_at`/`source_ref` is
   worth recording.
5. Run the local checks with the `.venv` interpreter to confirm the
   bump; a hub with no existing `supersedes` relationships sees no new
   errors or warnings from this release.
6. Commit and push to the agreed repository; confirm the commit is
   present on the remote and open a PR without auto-merge.

## Limits

`supersedes` is a one-directional pointer: the new file names the old
one, but the old file's frontmatter gains no backlink beyond its
`status: deprecated` flip — reading the old file alone doesn't show
where its successor lives. The citation warning is scoped to
`sources[].resource` uses found during this run; it doesn't chase a
chain of several supersessions back to a common ancestor, and two
different new files both claiming to supersede the same old one isn't
specially detected. `retrieved_at`/`source_ref` are plain metadata with
no mechanical freshness judgment attached — nothing computes "this is
stale" from them; that stays a human (or a later, separately-designed
mechanism's) call. `external_refs[].cited_as_of` doesn't even get that
much: the validator checks it's a well-formed date and nothing else,
since it can't open the target hub to compare against — it's a record
for a human to act on, not a signal anything here reacts to.
