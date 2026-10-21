# Grounding, triage, and Query/Archive in hubs — 0.2.1 → 0.2.2

Profile 0.2.2 adds four things to the local contract: the non-blocking
grounding report `scripts/check_evidence.py` (`hub.json` →
`quality.evidence_script`), a `scripts/validate_hub.py` warning about
bronze files not referenced by any `sources[].resource`, the formal
Query/Archive mode, and the triage disposition convention for adding
material plus the `Status: Disputed/Outdated` block for a single claim.
The OKF 0.2 format and the bronze/silver/gold/decisions structure stay
unchanged. The script, and the decision about the check's granularity (the
whole document, not a single footnote), are an adaptation of
`scripts/check_evidence.py` from
[Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki)
(MIT) — an independent implementation of the same Karpathy idea.

The engine doesn't know about existing hubs and doesn't update them
automatically. This repository, its PRs, or a merge alone don't protect
any existing hub. The procedure below is an explicit, separate task on the
designated hub.

## Adoption in an existing hub — 0.2.1 → 0.2.2

1. Check its contract, Git state, push address, branch, and agreed access.
   Keep local changes; don't run the generator on an existing directory.
2. On a separate branch, copy `scripts/check_evidence.py` from
   `skills/create-knowledge-hub/assets/hub/scripts/check_evidence.py` in
   this repository to `scripts/check_evidence.py` in the hub. Review any
   local modifications to `scripts/validate_hub.py`, if they exist — don't
   blindly overwrite them; the new validator only adds the
   `quality.evidence_script` requirement and the warning about orphaned
   bronze sources, it doesn't change the rest of the check.
3. In `hub.json`, set `profile_version` to `0.2.2` and add to the existing
   `quality` map the field `"evidence_script": "scripts/check_evidence.py"`,
   keeping the other fields (`validator`, `metric`, `threshold`,
   `max_fix_iterations`).
4. Carry over from the template `SCHEMA.md` (the "Grounding Invariant"
   section, the "No material" log convention, the triage dispositions and
   the cascade step in "Add material to the base," the `Status:` block in
   "Content quality," the "Answer a question about the base — Query"
   subsection in "Agent work") and the matching fragment of `AGENTS.md`
   ("Ongoing remote copy" stays unchanged; add the third task and the
   `check_evidence.py` step from "Mandatory check after editing"). Resolve
   collisions with the hub's local policy; don't overwrite whole files.
5. Existing bronze files with no prior reference via `sources[].resource`
   aren't a retroactive error — after migration, `validate_hub.py` will
   start reporting them as a warning. Review them: add a reference if the
   material is already in silver/gold, or log it as "No material" per the
   new convention (see SCHEMA.md) if it deliberately never entered the
   wiki.
6. Run the local checks with the `.venv` interpreter (`validate_hub.py`
   and `check_evidence.py`), commit and push to the agreed repository;
   confirm the commit is present on the remote and open a PR without
   auto-merge.

## Limits

`check_evidence.py` is a report, not a gate: its result never counts
toward `violations` or the `quality.threshold`, even after migration. The
warning about orphaned bronze sources doesn't block a green
`validate_hub.py` result (the threshold of 0 applies only to errors, not
warnings) — it's a signal for review, not a reason to stop work. The
migration doesn't require reprocessing existing silver/gold content or
retrofitting footnotes; it concerns only the contract, the tooling, and
new work from this point on.
