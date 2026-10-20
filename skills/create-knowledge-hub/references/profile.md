# New hub profile

`hub.json` configures the local pattern (version 0.2.2). It's not part of
the OKF standard. Policy declarations are instructions for the agent; the
generator doesn't install a process that technically enforces them.

| Field | Meaning |
|---|---|
| `id` | hub identifier, lowercase ASCII letters, digits, and hyphens |
| `title` | human-readable name |
| `kind` | `personal` or `company`; a description of purpose, not a permission |
| `owner` | owner/responsible party given by the user |
| `domain` | starting topic; may later span several fields |
| `bundle_root` | `knowledge`, the boundary of OKF documents |
| `concept_types` | starter vocabulary; adapt it after the first material |
| `policy` | the automation stage for editing, publication, and external actions |
| `policy.remote_copy` | required in 0.2.1 as `required_after_validated_task`: commit and push after a checked task; the destination needs agreement |
| `quality` | the local validator, the violations metric, a zero threshold, and a 5-cycle fix limit |
| `quality.evidence_script` | required in 0.2.2 as `scripts/check_evidence.py`: a non-blocking grounding report, outside the violations threshold |

Default types: Source, Concept, Method, Principle, Example, Synthesis,
Tool, Decision. They aren't a closed knowledge taxonomy. Add new types
when they distinguish things the audience actually needs, e.g. an
experiment, a metric, or a customer segment.

The skill directory can be copied in full. The templates are generator
resources. A template change applies to new hubs; an existing hub keeps
its own contract.

Profile 0.2.1 adds the explicit Git-copy obligation in `policy.remote_copy`
and its check in the validator. This isn't authorization for any remote,
nor an automatic update of older hubs. The adoption procedure for
0.2.0 → 0.2.1 is in docs/hub-git-backup.md in the generator repository.

Profile 0.2.2 adds the reporting (non-blocking) grounding script
`scripts/check_evidence.py`, the "No material" disposition convention in
the log, a validator warning about orphaned bronze sources, the formal
Query/Archive action, and the `Status: Disputed/Outdated` block for a
single claim. The script, and the decision about the check's granularity
(the whole document, not a single footnote), are an adaptation of
`scripts/check_evidence.py` from Astro-Han/karpathy-llm-wiki (MIT) — an
independent implementation of the same Karpathy idea. The adoption
procedure for 0.2.1 → 0.2.2 is in docs/migration-0.2.2.md in the generator
repository.

Profile 0.2.0 added the standalone script `scripts/validate_hub.py` to the
hub. The OKF format stays at 0.2. Migration from 0.1.1 is manual and
requires reviewing existing metadata and paths; the procedure is in
docs/migration-0.2.0.md in the generator repository. The hub itself
doesn't need that repository to validate.

## Migrating an existing hub from 0.1.0 to 0.1.1

This is an instruction update: adding knowledge and requesting gold become
independent actions. It doesn't change the OKF 0.2 format or document
paths. With the user's consent, update AGENTS.md, SCHEMA.md, the examples
in README.md, and the descriptions in the knowledge, silver, and gold
indexes, while keeping the hub's own rules and links. Then set
`profile_version` in hub.json to `0.1.1`. Don't re-run the generator on an
existing hub; don't overwrite content or Obsidian settings. Check the diff
and keep the previous state in Git history.
