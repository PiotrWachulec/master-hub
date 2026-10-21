# Three requests for everyday work

Work in the hub the user points to, not in the engine repository. Open
the hub directory as a project, optionally as an Obsidian vault. An
existing hub doesn't need the generator run again.

## 1. Add material — without stating a use

> Add material from [path] to the knowledge base. Keep the text, or a
> reference to the original, and the transcript in bronze. Analyze it and
> fold it into the silver wiki: connect the concepts to known knowledge,
> keep sources, examples, exceptions, and contradictions. Don't create
> gold yet.

A path to a note or a transcript is enough. Further material extends the
same base; you don't need to know yet how you'll use it.

## 2. Ask the base what it already knows

> What do I know about [topic]? Answer with links to the wiki.

By default this writes nothing — the agent searches the index and the
full text of silver/gold and answers in the conversation. When the answer
is worth keeping:

> Archive this answer in my base.

The agent saves it as a new silver document with references to the cited
articles, without creating a new bronze source — it's a synthesized
answer, not source material.

## 3. Request a result from existing knowledge

> Prepare a contribution to an ebook about [XYZ] from my knowledge base,
> in the form of [description]. Create a gold directory for this ebook.
> Base it on silver, keep references to my source material. For missing
> details or quotes, go back to bronze. Point out gaps and your own
> hypotheses.

Or:

> Prepare material for flashcards about [XYZ] in question-answer form,
> with references to sources, in a separate gold directory.

You don't need a new input. If you're changing the concept, you can ask:

> From the same knowledge, prepare an ebook variant for [a different
> audience]. Save it in a new gold directory, keeping the previous result.

## Corrections and scope of work

> In [the specified document], fix [description]. Record this correction
> in `90-decisions` with its scope and rationale, then check related
> drafts.

You can also request adding material and a specific result in a single
request. This isn't a mandatory flow for every import.

The agent reads `AGENTS.md`, `SCHEMA.md`, `hub.json`, and the knowledge
index, updates the relevant indexes and the log, and presents new drafts
for review. Under profile 0.2.2 it also runs the local validator and a
limited fix loop per the contract, and after editing silver/gold, also
the non-blocking `scripts/check_evidence.py` report. A missing check, or
violations after the limit is exhausted, stop the work; they aren't
reported as success. Publishing drafts and external actions require a
separate request.

At this stage, the agent does the work per the contract. The generator
creates the structure; it doesn't call a model and doesn't process
sources.

## Optional: browsing in Obsidian

The community plugin [Dataview](https://github.com/blacksmithgu/obsidian-dataview)
lets you query documents' frontmatter without changing files or the
contract, e.g. a list of drafts in silver (`TABLE status, title FROM
"knowledge/10-silver" WHERE status = "draft"`). This is purely a human
viewing layer — the agent and the validator neither require nor use it.
