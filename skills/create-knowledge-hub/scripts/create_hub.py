#!/usr/bin/env python3
"""Create a standalone knowledge hub. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import uuid

PROFILE_VERSION = "0.5.1"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "hub"


def nonempty(value: str) -> str:
    value = value.strip()
    if not value or any(ord(char) < 32 for char in value):
        raise argparse.ArgumentTypeError("Value must be non-empty, single-line text.")
    return value


def hub_id(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise argparse.ArgumentTypeError("ID: lowercase ASCII letters, digits, and single hyphens.")
    return value


def build_files(args: argparse.Namespace) -> dict[Path, str]:
    files = {
        path.relative_to(ASSETS): path.read_text(encoding="utf-8")
        for path in sorted(ASSETS.rglob("*"))
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc'
    }
    required = ("SCHEMA.md", "AGENTS.md", "scripts/validate_hub.py", "scripts/check_evidence.py")
    if any(Path(name) not in files for name in required):
        raise ValueError("Missing contract or validator in assets/hub; move the whole skill directory.")
    config = {
        "profile_version": PROFILE_VERSION,
        "okf_version": "0.2",
        "id": args.id,
        "title": args.title,
        "kind": args.kind,
        "owner": args.owner,
        "domain": args.domain,
        "hub_key": str(uuid.uuid4()),
        "hub_category": args.hub_category,
        "default_classification": args.default_classification,
        "bundle_root": "knowledge",
        "quality": {
            "validator": "scripts/validate_hub.py",
            "metric": "violations",
            "threshold": 0,
            "max_fix_iterations": 5,
            "evidence_script": "scripts/check_evidence.py",
        },
        "concept_types": ["Source", "Concept", "Method", "Principle", "Example",
                          "Synthesis", "Tool", "Decision"],
        "policy": {
            "knowledge_editing": "agent_drafts_with_user_review",
            "publication": "explicit_acceptance",
            "external_actions": "disabled",
            "remote_copy": "required_after_validated_task",
            "content_review": "direct",
        },
    }
    files[Path("hub.json")] = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    files[Path("README.md")] = (
        f"# {args.title}\n\n"
        f"Owner: {args.owner}. Starting topic: {args.domain}.\n\n"
        f"Hub key (for other hubs to cite this one): "
        f"`{config['hub_key']}`. Category: `{args.hub_category}`. "
        f"Default classification: `{args.default_classification}`.\n\n"
        "Other hubs can cite this one's documents (read-only) or derive "
        "anonymized content from them — see `SCHEMA.md`'s \"Cross-hub "
        "references\" section for the mechanics and the classification "
        "rules.\n\n"
        "Open this directory as a separate vault in Obsidian. "
        "Start with the [knowledge index](knowledge/index.md).\n\n"
        "## Three independent actions for the agent\n\n"
        "> Add material from [path] to the knowledge base.\n\n"
        "The agent keeps the source in bronze and extends the connected "
        "silver wiki. You don't need to state a business goal; gold isn't "
        "created yet.\n\n"
        "> What do I know about [topic]? Answer with links to the wiki.\n\n"
        "The agent searches the index and the full text of silver/gold and "
        "answers in the conversation, writing nothing. On an explicit "
        "\"Archive this answer\" request, it saves it as a new silver "
        "document with references to the cited articles.\n\n"
        "> Prepare material for [an ebook / flashcards / an automation] "
        "about [topic], in the form of [description].\n\n"
        "The agent uses the existing silver and creates a gold directory "
        "for the requested output, with references to sources. It doesn't "
        "need a new input. For missing details and quotes it goes back to "
        "bronze. A new concept can get a new gold directory without "
        "overwriting the previous one.\n\n"
        "You can request several actions together. The agent reads the "
        "contract, updates the indexes and the log, and shows proposals "
        "for review. The hub is an empty scaffold; automatic processing, "
        "publication, and integrations aren't installed.\n\n"
        "Contract: [SCHEMA.md](SCHEMA.md). Configuration: [hub.json](hub.json). "
        "The policy rules describe the agent's work, not technical "
        "permissions. Hand corrections to the agent; their lasting record "
        "goes into [decisions](knowledge/90-decisions/index.md).\n\n"
        "## Optional: browsing in Obsidian\n\n"
        "The community plugin [Dataview](https://github.com/blacksmithgu/obsidian-dataview) "
        "(Settings → Community plugins → Browse → \"Dataview\") lets you "
        "query frontmatter without changing files or the contract, e.g. a "
        "list of drafts in silver:\n\n"
        "````\n"
        "```dataview\n"
        "TABLE status, title FROM \"knowledge/10-silver\" WHERE status = \"draft\"\n"
        "```\n"
        "````\n\n"
        "This is purely a human viewing layer; the agent and the validator "
        "don't use it.\n\n"
        "## Structure check\n\n"
        "Always run Python scripts in the local `.venv`. If it doesn't "
        "exist, run `python3 -m venv .venv` (Python 3.10+) in the hub "
        "directory. Don't overwrite a broken environment. Don't install "
        "packages globally, via pip --user/sudo pip, or with "
        "--system-site-packages. The validator needs no extra packages. "
        "Then run `.venv/bin/python -B scripts/validate_hub.py` from the "
        "hub directory (Windows: `.venv/Scripts/python.exe`). From another "
        "directory, give full paths to the interpreter and the script. The "
        "stdout JSON contains `violations`, `errors`, `warnings`; "
        "diagnostics go to stderr. Success requires code 0 and "
        "`violations == 0`. A green result confirms only the local "
        "profile's structure, not the content or the full OKF standard. "
        "The fix loop and its limit are described in AGENTS.md and "
        "SCHEMA.md.\n\n"
        "`.venv/bin/python -B scripts/check_evidence.py` is a separate, "
        "non-blocking report: it checks whether numbers, dates, and quotes "
        "in silver/gold can actually be found in the referenced bronze "
        "sources. It doesn't count toward the `violations` threshold; "
        "suspects need a human review, not an automatic fix.\n\n"
        "## Ongoing remote copy\n\n"
        "After a completed, validated task and after consistent stages of "
        "longer work, the agent commits and pushes to the agreed "
        "repository, with no extra instruction needed. It confirms the "
        "commit on the remote or reports a missing current remote copy. An "
        "explicit instruction for local-only work takes precedence. "
        "Details and the limits of its authority are described in "
        "[AGENTS.md](AGENTS.md).\n\n"
        "By default, content pushes straight to the agreed main branch as "
        "a draft (`policy.content_review: \"direct\"`). For a shared hub, "
        "switch it to `\"required_pr\"` in `hub.json` so content goes "
        "through a branch and PR too, same as contract changes — see "
        "`policy.content_review` in [SCHEMA.md](SCHEMA.md).\n\n"
        "The generator doesn't initialize Git or a remote: on first run, "
        "agree with the agent on a destination and access so the first "
        "commit and push can happen. Until then, the scaffold is local "
        "only. This isn't a background backup; the copy doesn't cover "
        "external recordings, ignored files, or unpushed changes. Those "
        "need their own separate protection.\n\n"
        f"Generated under profile {PROFILE_VERSION}. "
        "This directory needs no access to the generator or to a parent repository.\n"
    )
    files[Path(".gitignore")] = (
        ".DS_Store\n.venv/\n__pycache__/\n*.pyc\n.runtime/\n.obsidian/workspace.json\n"
        ".obsidian/workspaces.json\n.env\n.env.*\n!.env.example\n"
    )
    files[Path(".obsidian/app.json")] = json.dumps(
        {"useMarkdownLinks": True, "newLinkFormat": "relative"}, indent=2
    ) + "\n"
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, required=True, help="New hub directory")
    parser.add_argument("--id", type=hub_id, required=True)
    parser.add_argument("--title", type=nonempty, required=True)
    parser.add_argument("--kind", choices=("personal", "company"), required=True)
    parser.add_argument("--owner", type=nonempty, required=True)
    parser.add_argument("--domain", type=nonempty, required=True)
    parser.add_argument("--hub-category", dest="hub_category",
                        choices=("competency", "initiative"), required=True)
    parser.add_argument("--default-classification", dest="default_classification",
                        choices=("Public", "Internal", "Confidential", "Secret"),
                        default="Confidential")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    # Inspect the supplied path before resolving: also refuse dangling symlinks.
    destination = args.dest.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        parser.error(f"Destination directory already exists; nothing was changed: {destination}")
    try:
        files = build_files(args)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"{'Plan' if args.dry_run else 'Creating'}: {destination}")
    for relative in sorted(files):
        print(f"  {relative}")
    if args.dry_run:
        print(f"{len(files)} files. No changes written.")
        return 0
    try:
        destination.mkdir(parents=True, exist_ok=False)
        for relative, contents in files.items():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8") as handle:
                handle.write(contents)
    except OSError as exc:
        print(f"Write error: {exc}. Check {destination}; it may contain "
              "a partial result. No files were removed.", file=sys.stderr)
        return 1
    print(f"Done: {len(files)} files. Open the hub directory in Obsidian.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
