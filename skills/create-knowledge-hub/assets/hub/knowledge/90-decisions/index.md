# Decisions and corrections

Record significant user remarks, design decisions, acceptance or rejection
of a proposal, and the scope of an actual content review here. Each entry
has type `Decision`, a date, a reason, and links to the documents it
covers.

```dataview
TABLE title, status, description
FROM "knowledge/90-decisions"
WHERE type
SORT file.name ASC
```

This table needs the Dataview community plugin to render; without it,
Obsidian shows the raw query block instead. It's a human viewing layer
only — the agent and the validator don't read it. Browse the folder
directly, or see SCHEMA.md's "Documents and references" section for the
contract. An empty table here is not an approval of future knowledge —
initializing the hub doesn't accept anything in advance.
