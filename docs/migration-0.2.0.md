# Manual migration of the local profile 0.1.1 → 0.2.0

A procedure for the future, not a current task or a report of a completed
migration. The engine doesn't assume any hubs already exist. The steps
below apply only when the user points to an older hub in the future and
requests its update.

This is the historical procedure for 0.2.0: use the templates and
validator from commit `1acb58b29bb5058178660a3a374bfc6f47824517`, not from
the current main. The generator currently produces profile 0.5.0; adopting
it also requires [the explicit Git-copy configuration update](hub-git-backup.md)
(0.2.0 → 0.2.1), [grounding and Query/Archive](migration-0.2.2.md)
(0.2.1 → 0.2.2), [opt-in content review](migration-0.3.0.md)
(0.2.2 → 0.3.0), [stable cross-hub identity](migration-0.4.0.md)
(0.3.0 → 0.4.0), and [cross-hub citation](migration-0.5.0.md)
(0.4.0 → 0.5.0).

OKF stays at version 0.2. The change concerns the local contract: a
standalone structure validator, a documented frontmatter subset, and a
limited fix loop. This is not an automatic update of existing hubs. The
engine doesn't know their location or state.

## Scope and consent

The user points to a hub and requests the migration. Read its contract,
check for local changes and the Git state. Keep the previous version in
history/backup. Work on a separate branch; for unrelated changes, use an
agreed worktree or stop. Don't run the generator on an existing directory.

## Procedure

1. Copy `skills/create-knowledge-hub/assets/hub/scripts/validate_hub.py`
   to `scripts/validate_hub.py` in the target hub. Keep local scripts; a
   collision with an existing path needs review, not a blind overwrite.
2. Apply the "Structure check" section from the new SCHEMA.md template and
   the loop rules from the AGENTS.md template, keeping the hub's domain
   decisions and policy. The instructions and the check must be
   consistent; don't swap the whole contract.
3. In hub.json, keep the identity, concept_types, policy, and any extra
   fields. Change profile_version to `0.2.0` and add:

   ```json
   "quality": {
     "validator": "scripts/validate_hub.py",
     "metric": "violations",
     "threshold": 0,
     "max_fix_iterations": 5
   }
   ```

4. Prepare the hub's local `.venv`, if it doesn't exist
   (`python3 -m venv .venv`, Python 3.10+). Keep the existing environment,
   don't install packages globally. Add `.venv/` to the local .gitignore
   without overwriting other rules. Run
   `.venv/bin/python -B scripts/validate_hub.py` in the migrated hub
   (Windows: `.venv/Scripts/python.exe`). Keep the report before making
   fixes. The new validator may surface older inconsistencies.
5. Review and fix only the agreed structural scope. Typical changes:
   - inline YAML → block maps/lists or JSON flow; quoting tags;
   - generated.at dates with a timezone, but only when the real time is
     known;
   - missing sources and footnote definitions, without inventing
     attribution;
   - local, relative file paths instead of a URL in sources.resource;
   - dated, descending log.md entries; an empty log without the old
     instructional paragraph (the new log template has only a heading).
6. Re-check the whole hub. The 5-cycle limit rule applies here too; if the
   scope is larger, present the remaining violations and agree on the next
   stage, instead of lowering the threshold or declaring the migration
   done.
7. Review the diff: content, sources, statuses, and provenance history
   must be preserved. Update the profile information in the hub's README.
   Hand in the branch as a PR with the validator's report and the scope of
   changes. Don't merge it yourself.

## Cases that require stopping

- Bronze sources are accepted, immutable versions. The new profile doesn't
  grant consent to change them; don't "fix" them automatically. Present
  the violations to the user along with a proposal for an explicit
  representation migration that preserves the original (e.g. the original
  text plus a separate metadata note). Without consent, the migration
  stops.
- Don't fabricate generated.at, fake a full source from a summary, or copy
  external materials without permission.
- A hub with a different bundle_root or format needs a separately designed
  migration. This validator expects knowledge/ and local profile 0.2.0.
- Suspicion of a validator bug: stop the loop and report the example to
  the user. Changing the validator/threshold is a separate contract task,
  not a data fix.

## Limits of proof

A green result confirms only the described structural rules. No network
access means the script doesn't check URL availability; it also doesn't
check truthfulness, completeness, authenticity, or the meaning of links.
The validator and the contract files are editable, so they aren't a
standalone safeguard against a malicious change to the check. A PR review
remains the boundary for accepting the contract.
