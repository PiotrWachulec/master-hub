# New hub profile

`hub.json` configures the local pattern (version 0.5.0). It's not part of
the OKF standard. Policy declarations are instructions for the agent; the
generator doesn't install a process that technically enforces them.

| Field | Meaning |
|---|---|
| `id` | hub identifier, lowercase ASCII letters, digits, and hyphens |
| `title` | human-readable name |
| `kind` | `personal` or `company`; a description of purpose, not a permission |
| `owner` | owner/responsible party given by the user |
| `domain` | starting topic; may later span several fields. Can deliberately repeat across several sibling hubs (e.g. separate Compute, Kubernetes, and Networking hubs all sharing `domain: "Azure"`) as an informal grouping signal — there's no registry behind it, it's just a convention |
| `hub_key` | UUID v4, generated once by the generator, never edited — a stable, name-independent identity for this hub. Foundation for a future cross-hub citation mechanism; not consumed by anything yet |
| `hub_category` | `"competency"` (topic-based, cuts across clients/initiatives — Azure, Kubernetes, sales) or `"initiative"` (client/project-specific, cuts across competencies). Orthogonal to `kind`, which is about ownership, not content type |
| `default_classification` | one of `Public`/`Internal`/`Confidential`/`Secret`, required in 0.5.0: the fallback sensitivity level for any document that doesn't declare its own `classification`. The CLI argument is optional, defaulting to `"Confidential"` — fail-closed — but the field is always present in `hub.json` |
| `bundle_root` | `knowledge`, the boundary of OKF documents |
| `concept_types` | starter vocabulary; adapt it after the first material |
| `policy` | the automation stage for editing, publication, and external actions |
| `policy.remote_copy` | required in 0.2.1 as `required_after_validated_task`: commit and push after a checked task; the destination needs agreement |
| `policy.content_review` | required in 0.3.0 as `"direct"` (default) or `"required_pr"`: whether content is pushed straight to the agreed main branch or routed through a branch + PR + review like contract changes — independent of `kind` |
| `quality` | the local validator, the violations metric, a zero threshold, and a 5-cycle fix limit |
| `quality.evidence_script` | required in 0.2.2 as `scripts/check_evidence.py`: a non-blocking grounding report, outside the violations threshold |

Default types: Source, Concept, Method, Principle, Example, Synthesis,
Tool, Decision. They aren't a closed knowledge taxonomy. Add new types
when they distinguish things the audience actually needs, e.g. an
experiment, a metric, or a customer segment.

`doc_key` is a document-level field (not `hub.json`), required in 0.4.0
on every silver/gold document's frontmatter: a UUID v4, generated once
when the document is created, never edited afterward — the per-document
counterpart to `hub_key`. See SCHEMA.md's "Stable identity" section for
why path-based identity, fine within one hub, doesn't hold up across
hubs.

`classification` and `external_refs[]` are also document-level fields,
added in 0.5.0. `classification` is optional per document — one of the
same four values as `default_classification`, overriding the hub default
for that document when present. `external_refs[]` is the array that
records an actual cross-hub reference: `{id, hub, doc, classification,
operation, note}`, where `hub`/`doc` are the target's `hub_key`/`doc_key`
and `operation` is `"cite"` (read-only pointer) or `"derive"` (new,
locally-authored, anonymized content with a provenance trail). See
SCHEMA.md's "Cross-hub references" section for the full mechanics,
including the classification tiers' semantics and the hard `Secret`
block.

The skill directory can be copied in full. The templates are generator
resources. A template change applies to new hubs; an existing hub keeps
its own contract.

## Versioning

The three numbers in `profile_version` (`x.y.z`) carry real meaning, not
just an incrementing history log: **patch** (`x.y.Z`) is a docs-only
wording fix with no validator or contract-shape change; **minor**
(`x.Y.0`) is a genuinely new, backward-compatible capability — a new
contract field, a new validator check, a new script — shipped with its
own migration doc; **major** (`X.0.0`) is reserved for a breaking change
to the OKF bundle shape or an existing hub's directory structure. Profile
history below is in reverse order, newest first.

Every release gets an entry in `CHANGELOG.md` at the repository root
(`../../../CHANGELOG.md` from here) and an annotated Git tag (`vX.Y.Z`).
Write the changelog entry as part of the PR that bumps `profile_version`
(under "Unreleased" until merged, then retitled with the release date).
The tag can only be created afterward, on the actual merge commit once it
exists — push it right after merging, not as a later afterthought.

Profile 0.5.0 adds the cross-hub citation mechanism built on 0.4.0's
identity fields: a required `default_classification` in `hub.json`
(`Public`/`Internal`/`Confidential`/`Secret`, CLI argument optional,
defaulting to `"Confidential"`), an optional per-document
`classification`, and `external_refs[]` for Cite (read-only pointer) and
Derive (locally-authored, anonymized content with a provenance trail)
references to another hub's document. A `classification: "Secret"`
reference is always a hard validator error; any Derive requires a
`knowledge/90-decisions/` entry naming the deriving document's own
`doc_key`; a `Confidential` reference's free-text `note` is scanned
(non-blocking) for leaked figures. Citation only works once both hubs
are on ≥0.5.0. The adoption procedure for 0.4.0 → 0.5.0 is in
docs/migration-0.5.0.md in the generator repository.

Profile 0.4.0 adds stable identity: `hub_key` and `hub_category` in
`hub.json`, and a required `doc_key` on every silver/gold document. This
also changes the generator's CLI, not just `hub.json`'s shape — a new
required `--hub-category` argument breaks any existing script or
automation invoking `create_hub.py` with the old argument set. No
citation mechanism ships yet; this is the identity foundation a later
profile will build on. The adoption procedure for 0.3.0 → 0.4.0 is in
docs/migration-0.4.0.md in the generator repository.

Profile 0.3.0 adds `policy.content_review` (`"direct"` or
`"required_pr"`), letting content follow the same branch + PR + review
procedure as contract changes — for hubs with more than one contributor.
It defaults to `"direct"` for new hubs, so solo workflows are unaffected
unless someone deliberately opts in; it's independent of `kind`, which
describes a hub's purpose, not its number of contributors. The adoption
procedure for 0.2.2 → 0.3.0 is in docs/migration-0.3.0.md in the generator
repository.

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

Profile 0.2.1 adds the explicit Git-copy obligation in `policy.remote_copy`
and its check in the validator. This isn't authorization for any remote,
nor an automatic update of older hubs. The adoption procedure for
0.2.0 → 0.2.1 is in docs/hub-git-backup.md in the generator repository.

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
