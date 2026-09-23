#!/usr/bin/env python3
"""Create a standalone knowledge hub. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

PROFILE_VERSION = "0.2.1"
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
        for path in sorted(ASSETS.rglob("*"))
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc'
    }
    required = ("SCHEMA.md", "AGENTS.md", "scripts/validate_hub.py")
    if any(Path(name) not in files for name in required):
        raise ValueError("Brakuje kontraktu lub walidatora w assets/hub; przenieś cały katalog skilla.")
    config = {
        "profile_version": PROFILE_VERSION,
        "okf_version": "0.2",
        "id": args.id,
        "title": args.title,
        "kind": args.kind,
        "owner": args.owner,
        "domain": args.domain,
        "bundle_root": "knowledge",
        "quality": {
            "validator": "scripts/validate_hub.py",
            "metric": "violations",
            "threshold": 0,
            "max_fix_iterations": 5,
        },
        "concept_types": ["Źródło", "Koncept", "Metoda", "Zasada", "Przykład",
                          "Synteza", "Narzędzie", "Decyzja"],
        "policy": {
            "knowledge_editing": "agent_drafts_with_user_review",
            "publication": "explicit_acceptance",
            "external_actions": "disabled",
            "remote_copy": "required_after_validated_task",
        },
    }
    files[Path("hub.json")] = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    files[Path("README.md")] = (
        f"# {args.title}\n\n"
        f"Właściciel: {args.owner}. Temat początkowy: {args.domain}.\n\n"
        "Otwórz ten katalog jako osobny vault w Obsidianie. "
        "Zacznij od [indeksu wiedzy](knowledge/index.md).\n\n"
        "## Dwa niezależne zadania dla agenta\n\n"
        "> Dodaj materiał z [ścieżka] do bazy wiedzy.\n\n"
        "Agent zachowuje źródło w bronze i rozwija połączoną wiki silver. "
        "Nie musisz podawać celu biznesowego; gold jeszcze nie powstaje.\n\n"
        "> Przygotuj z mojej bazy wiedzy materiał do [ebooka / fiszek / automatu] "
        "o [temat], w formie [opis].\n\n"
        "Agent korzysta z istniejącego silver i tworzy katalog gold pod zamówiony "
        "wynik, z referencjami do źródeł. Nie potrzebuje nowego wejścia. "
        "Po brakujące szczegóły i cytaty wraca do bronze. Nowa koncepcja może "
        "mieć nowy katalog gold bez nadpisywania poprzedniego.\n\n"
        "Możesz zamówić oba działania razem. Agent czyta kontrakt, aktualizuje "
        "indeksy oraz log i pokazuje propozycje do przeglądu. "
        "Hub jest pustym szkieletem; "
        "automatyczne przetwarzanie, publikacja i integracje nie są zainstalowane.\n\n"
        "Kontrakt: [SCHEMA.md](SCHEMA.md). Konfiguracja: [hub.json](hub.json). "
        "Reguły polityki opisują pracę agenta, nie techniczne uprawnienia. "
        "Korekty przekazuj agentowi; ich trwały zapis trafia do "
        "[decyzji](knowledge/90-decisions/index.md).\n\n"
        "## Kontrola struktury\n\n"
        "Skrypty Python uruchamiaj zawsze w lokalnym `.venv`. Jeśli go nie ma, "
        "w katalogu huba wykonaj `python3 -m venv .venv` (Python 3.10+). "
        "Nie nadpisuj niesprawnego środowiska. Nie instaluj paczek globalnie, "
        "przez pip --user/sudo pip ani z --system-site-packages. "
        "Walidator nie potrzebuje dodatkowych paczek. Następnie uruchom "
        "`.venv/bin/python -B scripts/validate_hub.py` z katalogu huba "
        "(Windows: `.venv/Scripts/python.exe`). Z innego katalogu podaj pełne "
        "ścieżki do interpretera i skryptu. JSON na stdout zawiera "
        "`violations`, `errors`, `warnings`; diagnostyka jest na stderr. "
        "Sukces wymaga kodu 0 i `violations == 0`. Zielony wynik potwierdza "
        "wyłącznie strukturę lokalnego profilu, nie treść ani cały standard OKF. "
        "Pętla naprawy i jej limit są opisane w AGENTS.md oraz SCHEMA.md.\n\n"
        "## Bieżąca kopia zdalna\n\n"
        "Po zakończonym, zwalidowanym zadaniu oraz spójnych etapach dłuższej "
        "pracy agent wykonuje commit i push do uzgodnionego repozytorium, "
        "bez dodatkowego polecenia. Potwierdza commit w remote albo zgłasza "
        "brak aktualnej kopii zdalnej. Wyraźne polecenie pracy lokalnej ma "
        "pierwszeństwo. Szczegóły i granice uprawnień opisuje "
        "[AGENTS.md](AGENTS.md).\n\n"
        "Generator nie inicjalizuje Git ani remote: przy pierwszym uruchomieniu "
        "uzgodnij z agentem cel i dostęp, aby wykonać pierwszy commit i push. "
        "Do tego czasu szkielet jest tylko lokalny. To nie backup w tle; "
        "kopia nie obejmuje zewnętrznych nagrań, plików ignorowanych ani "
        "niewypchniętych zmian. Wymagają osobnego zabezpieczenia.\n\n"
        f"Wygenerowano według profilu {PROFILE_VERSION}. "
        "Ten katalog nie wymaga dostępu do generatora ani nadrzędnego repozytorium.\n"
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
