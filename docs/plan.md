# Tool usage plan

1. Point to a new directory and create a hub with the generator. For an
   existing hub, don't re-run the generator — work per its own contract.
   Agree on a remote repository and access; the first commit and push of
   the scaffold confirms the Git copy is running. Without that, the hub
   exists only locally.
2. Open the hub as a project for the agent. Add one piece of material,
   extending bronze and silver without requiring gold.
3. The agent checks the structure with the local validator (profile
   0.6.0), fixes violations within the limit, and presents the result;
   separately, the non-blocking `scripts/check_evidence.py` shows
   suspected gaps in source coverage. Review the content and hand over
   corrections through conversation — a green structure doesn't replace
   that review. The agent commits and pushes and confirms the commit is
   present on the remote; it reports a missing copy as an unfinished stage
   of the task.
4. Ask the base what it already knows ("What do I know about X?") — the
   agent answers with links, without writing; "archive this answer" saves
   it as a new silver document.
5. When the need arises, request a specific gold result.
6. Only experience will show what mechanism is needed next.

[Example requests](first-run.md) · [Architecture](architecture.md)

## Engine development

The generator and the skills don't keep a registry of their users or
hubs. Local-contract changes come with a migration description; they
aren't propagated automatically. The local-profile validator ships in
every new hub. Automatic ingest, sync, full OKF validation, and
operational integrations stay out of scope for the current
implementation.
