---
name: create-knowledge-hub
description: Create standalone Markdown knowledge hubs for Obsidian following the bronze-silver-gold pattern and OKF 0.2. Use when setting up another personal library or a company hub; existing hubs need a separate migration.
---

# Create a knowledge hub

This package contains a portable generator and a knowledge-work contract.
All needed resources live in this directory. It doesn't assume a specific
hub already exists or that other repositories are accessible.

## Flow

1. Determine from context the destination directory, an ASCII identifier,
   the name, the owner, the kind (`personal` or `company`), and the topic.
   Ask follow-up questions only about data whose absence changes the
   ownership boundary or purpose. A new topic alone doesn't require a
   separate hub; independent work, access, and a separate publication
   cycle also justify one.
2. Read the [contract](assets/hub/SCHEMA.md) and the
   [profile rules](references/profile.md). Adapt the types to the use
   case after generating the hub; don't carry over a legal taxonomy
   automatically.
3. Use `.venv` in the engine repository or an agreed working directory,
   when the skill package has been moved. If it doesn't exist, create the
   environment with `python3 -m venv .venv` in that directory (Python
   3.10+). Use the system Python only to create the venv. Run the
   generator with the environment's interpreter, giving the path to this
   package:

   ```sh
   .venv/bin/python /path-to-skill/scripts/create_hub.py --dest /chosen/path/new-hub \
     --id new-hub --title "New hub" --kind personal \
     --owner "Owner" --domain "Topic"
   ```

   On Windows use `.venv/Scripts/python.exe`. No shell activation is
   needed. Don't overwrite a broken existing venv; report the problem. No
   global pip, pip --user, sudo pip, or --system-site-packages; install
   any packages only through the venv interpreter with `-m pip`. The
   generator needs no packages. `--dest` is relative to the invocation
   directory. `--dry-run` doesn't write the hub; creating the environment
   beforehand is a separate tool-setup step.
4. Check the configuration, indexes, and contract of the generated hub,
   including `profile_version: "0.2.2"` and
   `policy.remote_copy: "required_after_validated_task"`. This is the
   Git-copy obligation, not confirmation that it's configured. An existing
   directory is refused — don't remove it to work around that protection.
   Pick a new destination or prepare a migration if the user asked for
   one. In the new hub, create its own `.venv`, if it doesn't exist, via
   `python3 -m venv .venv` run from the hub directory. Don't copy the
   engine's environment. Run
   `<hub-directory>/.venv/bin/python -B <hub-directory>/scripts/validate_hub.py`
   (on Windows, the equivalent under `.venv/Scripts`) and show the JSON
   and exit code. A new scaffold should have zero violations. This is a
   check of the local profile's structure, not proof of future content
   quality.
5. Agree with the user on the remote repository and the data access scope,
   if that doesn't already follow from earlier agreements. The generator
   doesn't initialize Git: configuring it requires a stated destination
   and consent; don't create a public repo based on the hub's name alone.
   A hub inside a project uses that project's Git. With an agreed
   destination, make the first commit and push of the validated scaffold
   per the hub's AGENTS.md and confirm the commit on the remote. Without a
   configured copy, say clearly that the scaffold exists only locally and
   needs the configuration finished — don't present it as backed up.
6. Give the vault's location and three independent requests: adding
   material to bronze/silver, asking a question against the existing
   knowledge, and requesting a gold output from the existing knowledge.
   Adding material doesn't require a business goal. Don't call the
   scaffold itself a working automatic pipeline. Explain that the agent
   commits and pushes after checked tasks; there's no background backup
   process or recording copy kept outside Git.

The generator doesn't fetch material, doesn't initialize sync, doesn't
configure accounts, and doesn't change budgets. Sources and owner data
stay within their scope. Creating a hub doesn't imply consent to read
other hubs.

## Further work

The hub has its own AGENTS.md and SCHEMA.md and works without access to
this package. The user edits knowledge through conversation with the
agent. Record corrections as decisions, so future processing takes them
into account. Don't build an import mechanism, package distribution, or
sync between hubs. Additional context from a hub the user points to can be
noted as plain text in a piece of work; SCHEMA.md describes the rules for
local sources.
