# Ongoing Git copy in hubs

Profile 0.2.1 declares in hub.json
`policy.remote_copy: "required_after_validated_task"`; AGENTS.md describes
carrying out this rule. A requested edit includes committing and pushing
to the agreed repository after a checked task and after consistent stages
of longer work. The agent confirms the commit on the remote. Missing Git,
a missing destination or access, a missing green validation, or a failed
push must not be hidden under a "done" report. An explicit instruction for
local-only work takes precedence.

The generator stays offline and doesn't assume repositories exist. During
first setup, the user states the destination and the permitted data
access; the agent doesn't create or make a repo public without consent. In
a hub embedded in a project, it uses that project's Git, without touching
someone else's changes and commits.

## Adoption in an existing hub — 0.2.0 → 0.2.1

This is a change to the local contract, configuration, and validator. The
OKF 0.2 format stays unchanged. The engine doesn't know about existing
hubs and doesn't update them automatically. Neither the field alone nor an
agent's note creates the user's consent for a specific remote. After the
user points to a hub and requests an update:

1. Check its contract, Git state, push address, branch, and agreed access.
   Keep local changes; don't run the generator on an existing directory.
2. On a separate branch, carry over the "Ongoing remote copy" section from
   the AGENTS.md template and the matching rule from "Autonomy and
   ownership" in SCHEMA.md. In SCHEMA.md also update the profile version
   and "Structure check" with the required `remote_copy` field; every
   instruction must describe 0.2.1. Resolve collisions with local policy;
   don't overwrite whole files.
3. In hub.json, set `profile_version` to `0.2.1` and add to the existing
   `policy` map `"remote_copy": "required_after_validated_task"`, keeping
   the other fields. Along with this, adopt the 0.2.1 validator from the
   template; review local modifications, don't blindly overwrite them. The
   new validator requires both declarations. Don't copy it into a 0.2.0
   hub without an agreed migration.
4. Update the hub's README with the version, rules, and copy limits. When a
   separately installed curate-knowledge-hub is used, update it only on
   request.
5. Run the local checks with the `.venv` interpreter, commit and push to
   the agreed repository; confirm the commit is present on the remote and
   open a PR without auto-merge.

A merge in master-hub alone doesn't protect any existing hub. A missing
field in an older hub doesn't trigger the new rule. A missing or different
value in a hub declaring 0.2.1 is a configuration error, not default
consent.

## Limits of the copy

There's no schedule or background process. The Git copy covers only
pushed, version-controlled files. External recordings, materials behind
links, ignored files, and work not yet pushed need their own separate
backup. Remote history isn't an independent copy resistant to the
repository being deleted. A green validator proves the structure, not that
a remote copy exists; the generator's tests don't prove the agent actually
performed the push.
