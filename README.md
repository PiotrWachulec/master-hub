# Master Hub

A portable tool for creating and working with Markdown knowledge hubs:
generator, skills, templates, and an agent working contract.

This repository doesn't store the content, registry, or configuration of
any specific hubs. The user points to the target of each operation. A
generated hub works without access to this repository.

## Python environment

Scripts and tests always run inside the local `.venv`, even when they only
use the standard library. If `.venv` doesn't exist, create it in the
engine directory with `python3 -m venv .venv` (Python 3.10+). The system
Python is only for creating the environment; afterward use
`.venv/bin/python`. On Windows the equivalent is `.venv/Scripts/python.exe`.

Every hub creates its own environment after being generated. We don't copy
`.venv` between projects or into Git. We don't overwrite an existing,
broken environment. We don't install packages globally, via `pip --user`,
or `sudo`. Any dependencies are installed via `.venv/bin/python -m pip`
without `--system-site-packages`. The generator, the validator, and their
tests need no packages.

## Create a hub

Ask the agent to use [create-knowledge-hub](skills/create-knowledge-hub/SKILL.md)
and point it to a new directory, a name, an owner, and a topic. Or run it
from the master-hub directory (Python 3.10+, standard library):

```sh
.venv/bin/python skills/create-knowledge-hub/scripts/create_hub.py \
  --dest /chosen/path/new-hub \
  --id new-hub --title "New hub" --kind personal \
  --owner "Owner" --domain "Topic"
```

The destination directory must be new. `--dry-run` shows the plan without
writing. The generator doesn't initialize Git or a remote repository.
Choosing `personal` or `company` describes the purpose, it doesn't
configure permissions.

## Work in the hub

Open the generated directory as a project for the agent, optionally as an
Obsidian vault. Three independent requests:

> Add material from [path] to the knowledge base.

The source lands in bronze, and the knowledge in the connected silver
wiki. This requires no business goal and no gold creation.

> What do I know about [topic]? Answer with links to the wiki.

The agent searches the index and the full text of silver/gold and answers
in the conversation, writing nothing by default. On request, it archives
the answer as a new silver document.

> Prepare material for [goal] about [topic], in the form of [description].

The agent uses the existing silver and creates the matching gold with
references. A new concept can get a new directory without overwriting the
previous one.

[Example requests](docs/first-run.md) · [Usage plan](docs/plan.md)

## Remote copy of real hubs

New hubs commit the agent to committing and pushing after completed,
validated tasks and after consistent stages of longer work. You don't need
to separately say "push it." The destination and repository access are
agreed during the first setup; the generator itself doesn't create Git or
a remote. The agent confirms the commit on the remote repository or
reports a missing current copy. The obligation is explicit in `hub.json`
under profile 0.3.0: `policy.remote_copy: "required_after_validated_task"`.

This is a working instruction for the agent, not a background backup. It
covers pushed Git files, not external recordings or ignored files.
Existing hubs don't change automatically: [explicit rule adoption](docs/hub-git-backup.md).

By default content pushes straight to the agreed main branch as a draft
(`policy.content_review: "direct"`). For a hub with more than one
contributor, switch it to `"required_pr"` so content goes through a
branch and PR too, same as contract changes — solo hubs are unaffected
unless this is set explicitly.

## Two portable skills

- [create-knowledge-hub](skills/create-knowledge-hub/SKILL.md) — creates a new hub.
- [curate-knowledge-hub](skills/curate-knowledge-hub/SKILL.md) — handles a
  task in an existing Git repository per its own contract.

The skills aren't installed globally. You can hand the agent a path to
SKILL.md or move the whole chosen package. A merge in the engine alone
doesn't change the instructions of existing hubs or other agents'
configuration.

## Versions and capabilities

Format: OKF 0.2. Local working profile: 0.3.0, recorded in `hub.json`.
Template changes affect new hubs; existing ones need an explicit
migration. There's no automatic migrator, nor an obligation to adopt every
new OKF version immediately.

For the future we keep the [0.1.1 → 0.2.0 migration procedure](docs/migration-0.2.0.md).
Adopting the Git copy is described in the [0.2.0 → 0.2.1 update](docs/hub-git-backup.md).
Grounding, source triage, and Query/Archive are described in the
[0.2.1 → 0.2.2 update](docs/migration-0.2.2.md). Opt-in PR review for
shared hubs is described in the
[0.2.2 → 0.3.0 update](docs/migration-0.3.0.md). We currently assume no
existing hubs and perform no migrations. This document neither requires
nor runs a hub registry.

The generator, the editing instructions, the local structure validator,
and the non-blocking grounding report all work. Automatic ingest, sync, a
full OKF validator, and operational integrations are not implemented.

### Deliberately not built

Following the "Design Boundaries" section in the `karpathy-llm-wiki`
README (see "Inspirations" below) — a short "why," not just "what's
missing":

- **Anchoring a quote precisely to a single footnote** in the grounding
  check — real errors are almost always "value absent from any source in
  the document," which a whole-document check already catches; precise
  anchoring would only guard against a failure mode that doesn't occur in
  practice.
- **Automatic freshness detection via a hash of bronze sources** — bronze
  is immutable by the contract's own definition; new knowledge enters as a
  new file via ingest anyway, not by editing an existing one.
- **Numeric confidence/quality scores for content** — false precision
  without calibration; the strength of evidence belongs in the prose and
  in human review, not in a number.
- **Vector or graph search over the knowledge** — at the scale of a single
  hub, grep and reading files are sufficient and more predictable; worth
  adding only once recall measurably degrades.
- **Automatic hooks and run schedules** — those belong to the agent
  harness (hooks, cron), not to a portable, tool-agnostic skill.

## Structure check in a generated hub

In the hub directory, create `.venv` if it doesn't exist
(`python3 -m venv .venv`). Then run:

```sh
.venv/bin/python -B scripts/validate_hub.py
```

The script is part of the hub. It needs no generator, network, or external
libraries, and writes nothing. It gives JSON on stdout, e.g.:

```json
{"violations": 0, "errors": [], "warnings": []}
```

Diagnostics `file:line: message` go to stderr. Exit code 0 means no
violations. The quality contract sets a threshold of 0 and at most 5
fix/check cycles after the first check. Changing the check requires a
separate PR; it must never be a way to hide content errors. This is a
check of a local, documented subset of the format, not proof of
truthfulness or OKF validation.

Separately, `.venv/bin/python -B scripts/check_evidence.py` gives a
non-blocking report: whether numbers, dates, and quotes in
`10-silver`/`20-gold` can be found in the content of the referenced bronze
sources. It always exits with code 0 and never counts toward the
`violations` threshold — a human judges the suspects, not the script.

[Architecture](docs/architecture.md) · [Flow diagram](docs/architecture.svg) ·
[Optional multi-hub model](docs/system-architecture.svg)

Tests in the engine directory: `.venv/bin/python -B -m unittest discover -s tests -v`.

Inspirations: [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
[OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md),
and [karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) (Astro-Han,
MIT) — an independent implementation of the same idea, the source of the
ingest/query/lint pattern, and the direct inspiration for
`scripts/check_evidence.py` and the triage/Status conventions introduced in
profile 0.2.2.

## License

[MIT](LICENSE).
