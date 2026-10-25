# Pluggable conventions — 0.7.0 → 0.8.0

The engine's own contract stays deliberately language-neutral: content
in any hub keeps the language of its source material, and nothing above
assumes one script, one typographic convention, or one dash character.
But a real hub inevitably develops its own, legitimate style preferences
that *are* language- or project-specific — e.g. this project's choice to
use a plain hyphen "-" as its dash character in Polish-language content,
not the Unicode en dash or em dash that's otherwise common, arguably
more "correct," editorial typography in Polish publishing. That kind of
rule doesn't belong baked into the universal contract, which every hub
in every language inherits whether it wants it or not — but it's still
worth capturing somewhere a working agent will actually read, and
ideally with a mechanical backstop so an agent's claim of "fixed it" can
be checked rather than trusted blindly.

Profile 0.8.0 adds `conventions/`: a hub-root directory of plain
Markdown files, each one an optional, named, pluggable convention. A
hub declares which ones are active in `hub.json`'s new `conventions`
field — a list of names, each needing a matching
`conventions/<name>.md` file. Deliberately plain Markdown, not a
vendor-specific Claude Skill format: any agent that reads `AGENTS.md`
(which already instructs reading `conventions/<name>.md` files for every
declared name before writing content) picks this up regardless of which
model or tool it runs on.

A convention can come from two places, and the validator treats them
identically once they're in the hub: the generator's own library
(`skills/create-knowledge-hub/assets/conventions/`, requested at
creation time via the optional `--conventions name1,name2` CLI
argument), or added by hand later — create `conventions/<name>.md` and
add `<name>` to `hub.json`'s `conventions` list. A convention file is
plain prose guidance; it isn't validated for content. Some well-known
names additionally get an optional, non-blocking mechanical backstop in
`validate_hub.py` — ships one for now, `polish-typography`, which flags
a Unicode en dash "–" or em dash "—" in silver/gold body text (prose,
list items, headings, and blockquotes alike) as a warning. A declared
convention with no matching backstop is purely advisory, and that's the
expected default for most convention names, including any custom,
hub-specific one someone adds later.

**No breaking CLI change.** `--conventions` is optional with a safe
default (an empty list) — any existing script or automation invoking
`create_hub.py` keeps working unchanged.

The engine doesn't know about existing hubs and doesn't update them
automatically. This repository, its PRs, or a merge alone don't protect
any existing hub. The procedure below is an explicit, separate task on
the designated hub.

## Adoption in an existing hub — 0.7.0 → 0.8.0

1. Check its contract, Git state, push address, branch, and agreed
   access. Keep local changes; don't run the generator on an existing
   directory.
2. On a separate branch, set `profile_version` to `0.8.0` in `hub.json`
   and add the new top-level field:
   - `conventions`: `[]` if the hub needs none yet, or a list of names
     if it already has (or should have) specific style preferences
     worth capturing — e.g. `["polish-typography"]` for a
     Polish-language hub using a plain hyphen as its dash character.
3. For each name added to `conventions`, create the matching
   `conventions/<name>.md` file — copy from this repository's
   `skills/create-knowledge-hub/assets/conventions/` if a matching one
   exists there (currently just `polish-typography`), or write a new one
   describing the hub's own existing, deliberate style choice.
4. Carry over from the template `SCHEMA.md` (the new "Conventions"
   section, and the new bullet in "Structure check") and `AGENTS.md`
   (the new paragraph on reading declared convention files), if the hub
   keeps its own copies. Resolve collisions with local policy; don't
   overwrite whole files.
5. Run the local checks with the `.venv` interpreter — confirm any
   declared convention's file exists (hard error if not) and that
   `polish-typography`, if declared, doesn't immediately flag a backlog
   of existing content; review and fix at your own pace; it's a warning,
   not a release blocker. No backfill is required to adopt the profile
   itself.
6. Commit and push to the agreed repository; confirm the commit is
   present on the remote and open a PR without auto-merge.

## Limits

A convention file's content isn't checked by the validator at all — only
its existence, and only when declared. A convention with no matching
mechanical backstop (the common case) is pure prose the agent is trusted
to apply; nothing enforces it beyond that trust. The `polish-typography`
backstop itself is a plain Unicode character scan, not real typographic
analysis — it won't catch a hyphen used incorrectly for something other
than a dash, and it only fires when the convention is declared, exactly
as designed (a hub in a different language was never meant to inherit
this rule).
