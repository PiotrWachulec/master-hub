# Bronze

Text sources accepted into the hub. We keep every accepted version and its
provenance. A new transcription is a new version of the input.

```dataview
TABLE title, status, description
FROM "knowledge/00-bronze"
WHERE type
SORT file.name ASC
```

This table needs the Dataview community plugin to render; without it,
Obsidian shows the raw query block instead. It's a human viewing layer
only — the agent and the validator don't read it. Browse the folder
directly, or see SCHEMA.md's "Documents and references" section for the
contract.
