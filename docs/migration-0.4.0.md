# Stable cross-hub identity — 0.3.0 → 0.4.0

Profile 0.4.0 adds stable identity, independent of anything that can be
renamed: `hub_key` and `hub_category` in `hub.json`, and a required
`doc_key` on every silver/gold document. It ships **identity only** —
there is no citation mechanism yet, no field for referencing another
hub's `hub_key`/`doc_key` from within a document. That's deliberately
left for a later profile; this one is usable and complete on its own as
a foundation, not a half-built feature.

**This also changes the generator's CLI, not just `hub.json`'s shape.**
`create_hub.py` now requires a new `--hub-category` argument
(`"competency"` or `"initiative"`), with no default — any existing
script or automation invoking the generator with the old argument set
will fail until it's updated. This is separate from, and in addition to,
the `hub.json` migration below for hubs that already exist.

The engine doesn't know about existing hubs and doesn't update them
automatically. This repository, its PRs, or a merge alone don't protect
any existing hub. The procedure below is an explicit, separate task on
the designated hub.

## Adoption in an existing hub — 0.3.0 → 0.4.0

1. Check its contract, Git state, push address, branch, and agreed
   access. Keep local changes; don't run the generator on an existing
   directory.
2. On a separate branch, set `profile_version` to `0.4.0` in `hub.json`
   and add two new top-level fields:
   - `hub_key`: generate a fresh UUID (`.venv/bin/python -c "import uuid;
     print(uuid.uuid4())"`) — **never** copy one from another hub, even a
     related one.
   - `hub_category`: `"competency"` or `"initiative"`, chosen
     deliberately — there's no safe default to fall back on.
3. Review local modifications to `scripts/validate_hub.py`, if any exist
   — don't blindly overwrite them; the new validator only adds the
   `hub_key`/`hub_category`/`doc_key` checks, it doesn't change the rest.
4. Carry over from the template `SCHEMA.md` (the new "Stable identity"
   section, the `doc_key` requirement and example in "Documents and
   references") and `references/profile.md`'s field table, if the hub
   keeps its own copy. Resolve collisions with local policy; don't
   overwrite whole files.
5. **Backfill `doc_key` on every existing silver/gold document** — a
   one-time pass, generating a fresh UUID per document the same way as
   step 2. There's no ordering constraint and nothing to coordinate with
   other hubs yet, since nothing references these keys until a future
   profile adds a citation mechanism.
6. Run the local checks with the `.venv` interpreter, commit and push to
   the agreed repository; confirm the commit is present on the remote and
   open a PR without auto-merge.

## Limits

This profile has no consumer for `hub_key`/`doc_key` yet — they exist so
a future citation mechanism has something stable to point at, not because
anything reads them today. Don't build an ad hoc citation convention on
top of them in the meantime; wait for the profile that defines one.
Migration doesn't require reprocessing existing content beyond the
`doc_key` backfill in step 5; it doesn't touch bronze, sources, or
footnotes.
