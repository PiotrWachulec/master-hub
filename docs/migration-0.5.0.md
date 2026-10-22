# Cross-hub citation — 0.4.0 → 0.5.0

Profile 0.5.0 builds the citation mechanism that 0.4.0 deliberately left
for later: a closed classification system (`Public`/`Internal`/
`Confidential`/`Secret`) and `external_refs[]`, the frontmatter array
that lets a document **Cite** (read-only pointer) or **Derive**
(locally-authored, anonymized content with a provenance trail) material
from another hub's `hub_key`/`doc_key`. See `SCHEMA.md`'s "Cross-hub
references" section for the full mechanics.

**This also changes the generator's CLI, but with a safe default, unlike
0.4.0's `--hub-category`.** `create_hub.py` gains a new
`--default-classification` argument (`Public`/`Internal`/`Confidential`/
`Secret`), but it's optional — omitting it defaults to `"Confidential"`,
the fail-closed choice. Existing scripts or automation invoking the
generator without this argument keep working unchanged.

**Citation is unusable until a second hub is also ready.** Unlike 0.4.0,
which is a complete, useful foundation on its own, this profile only does
something once the hub being cited is itself on ≥0.5.0 with a `doc_key`
on the target document (which in turn requires that hub to be on ≥0.4.0).
Upgrading one hub alone adds a field nothing uses yet.

The engine doesn't know about existing hubs and doesn't update them
automatically. This repository, its PRs, or a merge alone don't protect
any existing hub. The procedure below is an explicit, separate task on
the designated hub.

## Adoption in an existing hub — 0.4.0 → 0.5.0

1. Check its contract, Git state, push address, branch, and agreed
   access. Keep local changes; don't run the generator on an existing
   directory.
2. On a separate branch, set `profile_version` to `0.5.0` in `hub.json`
   and add one new top-level field:
   - `default_classification`: `"Public"`, `"Internal"`, `"Confidential"`,
     or `"Secret"`, chosen deliberately. `"Confidential"` is the
     fail-closed choice if the hub's content hasn't been reviewed with
     this new field in mind; a hub that's already vetted everything as
     safe to cite elsewhere can choose a looser default.
3. Review local modifications to `scripts/validate_hub.py` and
   `scripts/check_evidence.py`, if any exist — don't blindly overwrite
   them; the new versions only add the `default_classification`/
   `classification`/`external_refs[]` checks and the Confidential-note
   scan, they don't change the rest.
4. Carry over from the template `SCHEMA.md` (the new "Cross-hub
   references" section) and `references/profile.md`'s field table and
   paragraph, if the hub keeps its own copy. Resolve collisions with
   local policy; don't overwrite whole files.
5. No backfill is required. `classification` and `external_refs[]` are
   both optional on every document — nothing retroactive is needed on
   existing content, unlike 0.4.0's one-time `doc_key` backfill.
6. Run the local checks with the `.venv` interpreter, commit and push to
   the agreed repository; confirm the commit is present on the remote and
   open a PR without auto-merge.

## Limits

`validate_hub.py` checks the shape of an `external_refs[]` entry only —
that `hub`/`doc` look like UUIDs, that `operation`/`classification`/
`note` are present and well-formed. It never opens, fetches, or reads the
other hub, and can't confirm the target document still exists or is
classified consistently with the reference. The `Confidential`-note
figure scan in `check_evidence.py` and the `90-decisions`-for-Derive
check are both presence/pattern checks, not proof that a `note` is
actually anonymized well enough, or that a Derive's write-up is adequate.
Migration doesn't require reprocessing existing content; it doesn't touch
bronze, sources, or footnotes beyond whatever new `external_refs[]`
entries are added deliberately after the upgrade.
