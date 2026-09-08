#!/usr/bin/env python3
"""Create a standalone knowledge hub. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

PROFILE_VERSION = "0.1.0"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "hub"


def nonempty(value: str) -> str:
    value = value.strip()
    if not value or any(ord(char) < 32 for char in value):
        raise argparse.ArgumentTypeError("Wartość musi być niepustym tekstem w jednej linii.")
    return value


def hub_id(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise argparse.ArgumentTypeError("ID: małe litery ASCII, cyfry i pojedyncze myślniki.")
    return value


def build_files(args: argparse.Namespace) -> dict[Path, str]:
    files = {
        path.relative_to(ASSETS): path.read_text(encoding="utf-8")
        for path in sorted(ASSETS.rglob("*")) if path.is_file()
    }
    if Path("SCHEMA.md") not in files or Path("AGENTS.md") not in files:
        raise ValueError("Brakuje szablonów assets/hub; przenieś cały katalog skilla.")
    config = {
        "profile_version": PROFILE_VERSION,
        "okf_version": "0.2",
        "id": args.id,
        "title": args.title,
        "kind": args.kind,
        "owner": args.owner,
        "domain": args.domain,
        "bundle_root": "knowledge",
        "concept_types": ["Źródło", "Koncept", "Metoda", "Zasada", "Przykład",
                          "Synteza", "Narzędzie", "Decyzja"],
        "policy": {
            "knowledge_editing": "agent_drafts_with_user_review",
            "publication": "explicit_acceptance",
            "external_actions": "disabled",
        },
    }
    files[Path("hub.json")] = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    files[Path("README.md")] = (
        f"# {args.title}\n\n"
        f"Właściciel: {args.owner}. Temat początkowy: {args.domain}.\n\n"
        "Otwórz ten katalog jako osobny vault w Obsidianie. "
        "Zacznij od [indeksu wiedzy](knowledge/index.md).\n\n"
        "## Pierwsze zadanie dla agenta\n\n"
        "> Przeczytaj AGENTS.md, SCHEMA.md i hub.json. Opracuj wskazany przeze mnie "
        "materiał tekstowy: zachowaj go w bronze, zbuduj powiązane silver i jeden "
        "produkt gold do podanego celu. Pokaż źródła, niepewności i propozycję "
        "do przeglądu. Aktualizuj indeksy oraz log.\n\n"
        "Podaj agentowi ścieżkę źródła oraz cel. Hub jest pustym szkieletem; "
        "automatyczne przetwarzanie, publikacja i integracje nie są zainstalowane.\n\n"
        "Kontrakt: [SCHEMA.md](SCHEMA.md). Konfiguracja: [hub.json](hub.json). "
        "Reguły polityki opisują pracę agenta, nie techniczne uprawnienia. "
        "Korekty przekazuj agentowi; ich trwały zapis trafia do "
        "[decyzji](knowledge/90-decisions/index.md).\n\n"
        f"Wygenerowano według profilu {PROFILE_VERSION}. "
        "Ten katalog nie wymaga dostępu do generatora ani nadrzędnego repozytorium.\n"
    )
    files[Path(".gitignore")] = (
        ".DS_Store\n.runtime/\n.obsidian/workspace.json\n"
        ".obsidian/workspaces.json\n.env\n.env.*\n!.env.example\n"
    )
    files[Path(".obsidian/app.json")] = json.dumps(
        {"useMarkdownLinks": True, "newLinkFormat": "relative"}, indent=2
    ) + "\n"
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, required=True, help="Nowy katalog huba")
    parser.add_argument("--id", type=hub_id, required=True)
    parser.add_argument("--title", type=nonempty, required=True)
    parser.add_argument("--kind", choices=("personal", "company"), required=True)
    parser.add_argument("--owner", type=nonempty, required=True)
    parser.add_argument("--domain", type=nonempty, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    # Inspect the supplied path before resolving: also refuse dangling symlinks.
    destination = args.dest.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        parser.error(f"Katalog docelowy już istnieje; nic nie zmieniono: {destination}")
    try:
        files = build_files(args)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"{'Plan' if args.dry_run else 'Tworzenie'}: {destination}")
    for relative in sorted(files):
        print(f"  {relative}")
    if args.dry_run:
        print(f"{len(files)} plików. Nie zapisano zmian.")
        return 0
    try:
        destination.mkdir(parents=True, exist_ok=False)
        for relative, contents in files.items():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8") as handle:
                handle.write(contents)
    except OSError as exc:
        print(f"Błąd zapisu: {exc}. Sprawdź {destination}; może zawierać "
              "częściowy wynik. Nie usunięto żadnych plików.", file=sys.stderr)
        return 1
    print(f"Gotowe: {len(files)} plików. Otwórz katalog huba w Obsidianie.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
