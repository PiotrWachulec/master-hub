# Master Hub

Przenośne narzędzie do tworzenia i obsługi hubów wiedzy Markdown:
generator, skille, szablony i kontrakt pracy agenta.

To repozytorium nie przechowuje treści, rejestru ani konfiguracji konkretnych
hubów. Użytkownik wskazuje cel każdej operacji. Wygenerowany hub działa bez
dostępu do tego repozytorium.

## Utwórz hub

Poproś agenta o użycie [create-knowledge-hub](skills/create-knowledge-hub/SKILL.md)
i wskaż nowy katalog, nazwę, właściciela oraz temat. Albo uruchom
z katalogu master-hub (Python 3.10+, biblioteka standardowa):

```sh
python3 skills/create-knowledge-hub/scripts/create_hub.py \
  --dest /wybrana/sciezka/nowy-hub \
  --id nowy-hub --title "Nowy hub" --kind personal \
  --owner "Właściciel" --domain "Temat"
```

Katalog docelowy musi być nowy. `--dry-run` pokazuje plan bez zapisu.
Generator nie inicjalizuje Git ani repozytorium zdalnego. Wybór `personal`
lub `company` opisuje przeznaczenie, nie konfiguruje uprawnień.

## Pracuj w hubie

Otwórz wygenerowany katalog jako projekt dla agenta, opcjonalnie jako vault
Obsidiana. Dwa niezależne polecenia:

> Dodaj materiał z [ścieżka] do bazy wiedzy.

Źródło trafia do bronze, a wiedza do połączonej wiki silver. Nie wymaga to
celu biznesowego ani tworzenia gold.

> Przygotuj z mojej bazy materiał do [cel] o [temat], w formie [opis].

Agent korzysta z istniejącego silver i tworzy odpowiedni gold z referencjami.
Nowa koncepcja może dostać nowy katalog bez nadpisywania poprzedniego.

[Przykłady poleceń](docs/first-run.md) · [Plan użycia](docs/plan.md)

## Dwa przenośne skille

- [create-knowledge-hub](skills/create-knowledge-hub/SKILL.md) — tworzy nowy hub.
- [curate-knowledge-hub](skills/curate-knowledge-hub/SKILL.md) — obsługuje zadanie
  w istniejącym repozytorium Git według jego własnego kontraktu.

Skille nie są zainstalowane globalnie. Można przekazać agentowi ścieżkę do
SKILL.md albo przenieść cały wybrany pakiet. Sam merge w silniku nie zmienia
instrukcji istniejących hubów ani konfiguracji innych agentów.

## Wersje i możliwości

Format: OKF 0.2. Lokalny profil pracy ma osobną wersję w `hub.json`.
Zmiana szablonów obejmuje nowe huby; istniejące wymagają jawnej migracji.
Nie ma automatycznego migratora ani obowiązku natychmiastowego przyjęcia
każdej nowej wersji OKF.

Działają generator i instrukcje redakcji. Automatyczny ingest, synchronizacja,
pełny walidator OKF i integracje operacyjne nie są zaimplementowane.

[Architektura](docs/architecture.md) · [Diagram przepływu](docs/architecture.svg) ·
[Opcjonalny model wielu hubów](docs/system-architecture.svg)

Testy: `python3 -B -m unittest discover -s tests -v`.

Inspiracje: [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
i [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md).
