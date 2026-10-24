# Dataview-driven layer indexes, graph color groups — 0.5.1 → 0.6.0

Profile 0.6.0 fixes a real problem found by inspecting the first hubs
generated under earlier profiles in Obsidian: the four layer indexes
(`00-bronze/index.md`, `10-silver/index.md`, `20-gold/index.md`,
`90-decisions/index.md`) had been growing a markdown link per document,
on the reasonable but unstated assumption that "update the indexes"
meant maintaining a link list. At scale, that turns each layer index
into a high-degree hub node that every document in the layer connects
through — in Obsidian's Graph View this drowns out the real
concept-to-concept and concept-to-source connections, which is the
actual point of browsing the graph.

The fix: each layer index now carries a short description plus a
Dataview query (a fenced ` ```dataview ` block) that lists the layer's
documents by `type`/`title`/`status` dynamically. Nothing to hand-edit
per document — the query reflects reality on its own. `knowledge/index.md`
is unaffected: its four links (one per layer) are fixed in number and
never grow, so they don't cause the same problem.

This profile also adds, as new hubs' default, `.obsidian/graph.json`
with color groups per layer and a search filter excluding `index.md`/
`log.md` from the graph view — purely a human-viewing convenience, not
something the validator or the agent reads. And it adds a "Content
quality" rule against hand-wrapping prose at a fixed column width:
Obsidian's reading view renders a bare `\n` inside a paragraph as a real
line break (unlike strict CommonMark, which treats it as a space), so
manually word-wrapped prose shows up as choppy, mid-sentence breaks
instead of a flowing paragraph.

**No validator check, `hub.json` field, or document frontmatter shape
changed.** The layer indexes' content was never structurally enforced —
this is a convention fix, not a new contract requirement, so nothing in
`validate_hub.py` changed to go with it.

The engine doesn't know about existing hubs and doesn't update them
automatically. This repository, its PRs, or a merge alone don't protect
any existing hub. The procedure below is an explicit, separate task on
the designated hub.

## Adoption in an existing hub — 0.5.1 → 0.6.0

1. Check its contract, Git state, push address, branch, and agreed
   access. Keep local changes; don't run the generator on an existing
   directory.
2. On a separate branch, set `profile_version` to `0.6.0` in `hub.json`.
3. Replace each layer index's accumulated link list with the new
   description-plus-Dataview-query shape — copy the pattern from this
   repository's `skills/create-knowledge-hub/assets/hub/knowledge/*/index.md`
   templates, keeping the layer's own description text if it was
   customized. `knowledge/index.md` needs no change.
4. Carry over from the template `SCHEMA.md` (the updated "Documents and
   references" section, the new "Content quality" paragraph on
   paragraph wrapping) and `AGENTS.md` (the updated index-maintenance
   sentence), if the hub keeps its own copy. Resolve collisions with
   local policy; don't overwrite whole files.
5. Optional: add `.obsidian/graph.json` with per-layer color groups and
   the `index.md`/`log.md` exclusion filter — copy it from a freshly
   generated hub, or merge the `colorGroups`/`search` fields into an
   existing local `.obsidian/graph.json` if one already exists (Obsidian
   creates this file itself on first open; don't overwrite a vault's
   other local graph settings, like `scale` or `centerStrength`,
   wholesale).
6. No backfill required for existing documents' body text — the
   paragraph-wrapping rule only affects how new/edited prose is written
   going forward; don't rewrite already-correct content just to comply.
7. Run the local checks with the `.venv` interpreter, commit and push to
   the agreed repository; confirm the commit is present on the remote and
   open a PR without auto-merge.

## Limits

This is a convention and template fix, not a validator-enforced rule —
`validate_hub.py` doesn't check a layer index's content shape, and it
doesn't check whether a document's body avoids hand-wrapped paragraphs.
Both are agent-judgment conventions, same as most of this contract's
content-quality guidance. Dataview rendering itself needs the Dataview
community plugin; without it, Obsidian shows the raw query block instead
of a live table — this was already true for the optional Dataview
example in every generated hub's `README.md`.
