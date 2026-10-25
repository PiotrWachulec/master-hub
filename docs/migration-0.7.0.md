# Hard-wrapped-paragraph warning — 0.6.0 → 0.7.0

Profile 0.6.0 added guidance against manually hand-wrapping prose at a
fixed column width — Obsidian's reading view renders a bare `\n` inside a
paragraph as a real line break, unlike strict CommonMark, so wrapped
prose shows up as choppy, mid-sentence breaks instead of a flowing
paragraph. That guidance was unenforced: an agent could claim "fixed,
`validate_hub.py` reports 0 violations" without the content actually
being fixed, since nothing checked for it. This happened twice in a real
hub before it was caught by direct content inspection, not by the
validator.

Profile 0.7.0 closes that gap with a new, **non-blocking** check:
`validate_hub.py` now classifies each line of a silver/gold document's
body (heading, list item, quote, footnote, table row, or plain prose)
and flags a paragraph, list item, or blockquote that spans more than one
physical source line as a warning. It's deliberately a warning, not a
violation: this is a heuristic on prose structure, not a structural
correctness check, and a fragile classifier blocking real work would
just recreate the same false-"0 violations" trust problem in the other
direction. A blockquote written the conventional way — `>` on every
physical line — is never flagged; only a unit built by genuinely
hard-wrapping plain prose is.

**No validator-blocking (`violations`) check, `hub.json` field, or
document frontmatter shape changed.** The `quality.threshold: 0` gate is
unaffected — a hub with wrapped paragraphs still validates green; they
just show up in `warnings` now, where they didn't before.

The engine doesn't know about existing hubs and doesn't update them
automatically. This repository, its PRs, or a merge alone don't protect
any existing hub. The procedure below is an explicit, separate task on
the designated hub.

## Adoption in an existing hub — 0.6.0 → 0.7.0

1. Check its contract, Git state, push address, branch, and agreed
   access. Keep local changes; don't run the generator on an existing
   directory.
2. On a separate branch, set `profile_version` to `0.7.0` in `hub.json`.
3. Copy the updated `scripts/validate_hub.py` from this repository's
   `skills/create-knowledge-hub/assets/hub/scripts/validate_hub.py` over
   the hub's own copy — review local modifications first if any exist;
   the new version only adds the paragraph-wrapping check and the
   refactor that lets it reuse the existing code-fence masking, it
   doesn't change anything else.
4. Carry over from the template `SCHEMA.md` (the new sentence in
   "Content quality" and the new bullet in "Structure check") and
   `AGENTS.md` (the new paragraph on writing one physical line per
   paragraph/list item/blockquote, and on not trusting a clean
   `validate_hub.py` run alone for this specific class of claim), if the
   hub keeps its own copies. Resolve collisions with local policy; don't
   overwrite whole files.
5. Run the local checks with the `.venv` interpreter. Existing
   hard-wrapped content, if any, will now show up under `warnings` —
   review and reflow it at your own pace; it was never a validator
   failure and still isn't one under 0.7.0. No backfill is required to
   adopt the profile itself.
6. Commit and push to the agreed repository; confirm the commit is
   present on the remote and open a PR without auto-merge.

## Limits

This check is a line-classification heuristic, not a parser of Markdown
semantics. It doesn't understand indentation-based nested list
continuations (an indented continuation line under a list item is
classified as a new, separate paragraph, not as part of that item), and
it has no notion of language or script — the same classification rules
apply regardless of whether the content is in a space-delimited language
or not. It's a warning specifically so these limits don't block real
work: treat a flagged line as a candidate worth a human glance, not a
verdict.
