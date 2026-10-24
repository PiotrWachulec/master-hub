# Gold

Material created on request for a specific use, in separate directories:
e.g. a contribution to an ebook, flashcard material, or instructions for
an automation. Built from existing silver, with references and a
provenance path to the sources in bronze; they don't require a new input.
A new concept can get its own directory without overwriting the previous
result. We don't create empty directories speculatively. Being ready for
use is not a content verification or consent for external actions.

```dataview
TABLE title, status, description
FROM "knowledge/20-gold"
WHERE type
SORT file.name ASC
```

This table needs the Dataview community plugin to render; without it,
Obsidian shows the raw query block instead. It's a human viewing layer
only — the agent and the validator don't read it. Browse the folder
directly, or see SCHEMA.md's "Documents and references" section for the
contract.
