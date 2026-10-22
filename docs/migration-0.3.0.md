# Opt-in content review for shared hubs — 0.2.2 → 0.3.0

Profile 0.3.0 adds one thing to the local contract: `policy.content_review`,
with two values. `"direct"` is today's behavior, unchanged — content
commits and pushes straight to the agreed main branch as a draft.
`"required_pr"` routes content through the same branch + PR + review
procedure already used for contract changes, with no self-merge. It's
independent of `kind` (`personal`/`company`), which describes a hub's
purpose, not how many people write to it.

This closes a gap for shared hubs: several agents or people editing the
same silver concurrently could silently overwrite or duplicate each
other's work, since "agree on a work split" was only prose, not a
mechanism. It also adds an explicit procedure for updating a long-lived,
already-pushed PR branch from a moving base — merging the base in as a
normal merge commit, never rebasing or force-pushing it, consistent with
this contract's existing no-force-push rule.

The engine doesn't know about existing hubs and doesn't update them
automatically. This repository, its PRs, or a merge alone don't protect
any existing hub. The procedure below is an explicit, separate task on the
designated hub.

## Adoption in an existing hub — 0.2.2 → 0.3.0

1. Check its contract, Git state, push address, branch, and agreed access.
   Keep local changes; don't run the generator on an existing directory.
2. On a separate branch, set `profile_version` to `0.3.0` in `hub.json`
   and add `"content_review": "direct"` to the existing `policy` map,
   keeping the other fields (`knowledge_editing`, `publication`,
   `external_actions`, `remote_copy`). **`"direct"` is the no-op choice**:
   it preserves exactly today's save behavior. Only use `"required_pr"`
   if the hub is deliberately gaining reviewers.
3. Review local modifications to `scripts/validate_hub.py`, if any exist
   — don't blindly overwrite them; the new validator only adds the
   `policy.content_review` requirement, it doesn't change the rest of the
   check.
4. Carry over from the template `SCHEMA.md` ("Autonomy and ownership": the
   `content_review` paragraph and the updated `policy` JSON example) and
   the matching fragments of `AGENTS.md` ("Ongoing remote copy": the new
   `content_review` paragraph, the content-routing sentence now
   conditional on it, and the new bullet on merging a moved base into an
   already-open PR branch). Resolve collisions with the hub's local
   policy; don't overwrite whole files.
5. If the hub is adopting `"required_pr"`, agree with the user on who
   reviews PRs and confirm branch protection on the actual remote (e.g.
   GitHub) if wanted — the validator only checks that the field has a
   valid value, it has no way to enforce review on the remote itself.
6. Run the local checks with the `.venv` interpreter (`validate_hub.py`,
   and `check_evidence.py` if content changed), commit and push to the
   agreed repository; confirm the commit is present on the remote and
   open a PR without auto-merge.

## Limits

Setting `content_review` to `"required_pr"` is a contract-level statement
of intent, not a technical lock — nothing in this repo's tooling prevents
an agent or a person from pushing straight to main regardless of the
field's value; the enforcement a team actually wants (e.g. a required
review before merge) has to be configured on the remote, outside this
repo's scope. Likewise, the "merge the base in, never rebase" rule for
open PR branches is instructional, not code-enforced: it exists because
this contract already refuses force-push unconditionally, and that
refusal isn't being relaxed here. Migration doesn't require reprocessing
existing content; it concerns only the contract and new work from this
point on.
