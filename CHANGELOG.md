# Changelog

All notable changes to this project are documented here. The version
numbers below are the engine's `profile_version` (recorded in every
generated hub's `hub.json`) — this repository has no other versioned
artifact. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

Versioning policy (see `skills/create-knowledge-hub/references/profile.md`
for the full statement): **patch** (`x.y.Z`) is a docs-only fix with no
validator or contract-shape change; **minor** (`x.Y.0`) is a new,
backward-compatible capability shipped with its own migration doc;
**major** (`X.0.0`) is reserved for a breaking change to the OKF bundle
shape or an existing hub's directory structure.

## [Unreleased]

## [0.4.0] — 2026-10-22

### Added

- `hub_key` (UUID v4, `hub.json`): a stable, name-independent identity for
  a hub, generated once by the generator and never edited.
- `hub_category` (`"competency"` or `"initiative"`, `hub.json`): topic-
  based knowledge that cuts across clients, versus client/project-specific
  work — orthogonal to `kind`. New required `--hub-category` CLI arg.
- `doc_key` (UUID v4): required on every silver/gold document's
  frontmatter — the per-document counterpart to `hub_key`, stable across
  local renames/moves, unlike the path-based identity OKF otherwise uses.
- `docs/migration-0.4.0.md`.

### Changed

- `create_hub.py`'s CLI now requires `--hub-category`, with no default —
  breaks any existing script/automation calling the generator with the
  old argument set, not just a `hub.json` migration for existing hubs.

This profile ships identity only — no cross-hub citation mechanism yet.
`hub_key`/`doc_key` are the foundation a later profile will build on.

## [0.3.0] — 2026-10-22

### Added

- `policy.content_review` (`"direct"` default, or `"required_pr"`): lets
  content go through the same branch + PR + review procedure as contract
  changes, for hubs with more than one contributor. Independent of `kind`.
  Defaults to `"direct"`, so solo hubs are unaffected unless this is set
  explicitly.
- A documented procedure for updating an already-pushed, open-PR branch
  from a moved base: merge it in as a normal merge commit, never
  rebase/force-push — consistent with the contract's existing,
  unconditional no-force-push rule.
- A permanent "Versioning" policy statement in `references/profile.md`.
- `docs/migration-0.3.0.md`.

## [0.2.2] — 2026-10-21

### Added

- `scripts/check_evidence.py`: a non-blocking grounding (fidelity) report
  — verifies that numbers, dates, and quotes in `10-silver`/`20-gold`
  actually appear in their cited `00-bronze` sources. Adapted from
  `Astro-Han/karpathy-llm-wiki` (MIT).
- Source triage dispositions when adding material (New / Update /
  Disputed / No material) with a machine-readable log convention.
- A cascade-update step: after a primary article, search the rest of
  silver for the same entities and update materially affected documents.
- A formal, read-only **Query** action plus an explicit **Archive**
  action to save a synthesized answer into silver.
- A `Status: Disputed/Outdated` block for annotating a single claim,
  distinct from a document's whole-file `status` field.
- A `validate_hub.py` warning for bronze files not referenced by any
  `sources[].resource` and not logged as "No material".
- `LICENSE` (MIT).
- `docs/migration-0.2.2.md`.

### Changed

- The entire repository — documentation, code strings, test fixtures, and
  the two hand-authored SVG diagrams — translated from Polish to English
  for a global audience. The hub's own knowledge content is unaffected:
  `SCHEMA.md`/`AGENTS.md` now say explicitly that the contract being in
  English doesn't set the language of a hub's content.
- `quality.evidence_script` is now a required `hub.json` field.

## [0.2.1] — 2026-09-23

### Added

- `policy.remote_copy: "required_after_validated_task"`: an explicit,
  validator-checked obligation to commit and push after a completed,
  checked task and after consistent stages of longer work.
- `docs/hub-git-backup.md`, the adoption procedure for existing hubs.

## [0.2.0] — 2026-09-23

### Added

- `scripts/validate_hub.py`: a standalone, read-only structure validator
  shipped inside every hub (frontmatter subset, link/footnote/source
  checks, log format), with a `quality` contract (`violations` metric,
  zero threshold, a 5-cycle fix budget).
- A requirement to run all scripts inside a local `.venv`, never a system
  Python.
- `docs/migration-0.2.0.md`, the manual migration procedure from 0.1.1.

### Changed

- Removed cross-hub `imports`; restricted navigation-index exemptions.

## [0.1.1] — 2026-09-09

### Changed

- Split knowledge work into two independent actions: adding material
  (bronze → silver) no longer requires a stated goal, and requesting a
  gold output no longer requires adding new material first.
- Added the portable `curate-knowledge-hub` skill for working in an
  existing Git-backed hub (pull, contract reading, action selection,
  branch/PR delivery per `hub.json` policy) — content drafts commit
  directly to the agreed branch, only contract changes require a PR.
- Made the engine hub-independent: no registry of hubs, no assumptions
  about any hub's existence or location.

## [0.1.0] — 2026-09-08

### Added

- The initial `create-knowledge-hub` generator and the bronze/silver/gold
  architecture: bronze preserves sources, silver grows a connected wiki,
  gold holds outputs prepared for a specific use.

[Unreleased]: https://github.com/PiotrWachulec/master-hub/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/PiotrWachulec/master-hub/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/PiotrWachulec/master-hub/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/PiotrWachulec/master-hub/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/PiotrWachulec/master-hub/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/PiotrWachulec/master-hub/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/PiotrWachulec/master-hub/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/PiotrWachulec/master-hub/releases/tag/v0.1.0
