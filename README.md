# Master Hub

To repozytorium zawiera generator, szablony i dokumentację. Właściwa praca
z wiedzą odbywa się w osobnym repozytorium
[personal-hub](https://github.com/PiotrWachulec/personal-hub).

```text
Repos/
  master-hub/     generator, szablony, dokumentacja; własny Git
  personal-hub/   Twoja biblioteka wiedzy; własny Git i vault Obsidiana
```

Repozytoria są niezależne. Nie ma submodułów, dowiązań ani wspólnego katalogu `.git`.

## Jak zacząć

Otwórz `../personal-hub` jako projekt do pracy z agentem i jako vault
w Obsidianie. Masz dwa niezależne polecenia:

> Dodaj materiał z [ścieżka] do bazy wiedzy.

Agent zachowuje źródło w bronze i rozwija połączoną wiki w silver.
Nie musisz jeszcze wiedzieć, do czego użyjesz tej wiedzy. Gold nie powstaje.

> Przygotuj z mojej bazy wiedzy materiał do ebooka o [XYZ], w formie [opis].

Agent korzysta z istniejącego silver i tworzy katalog gold pod ten rezultat,
z referencjami do źródeł. Nie musisz dodawać kolejnego materiału.
Zmiana koncepcji może dać nowy katalog gold, bez nadpisania poprzedniego.

Ty czytasz i mówisz, co poprawić. Nie musisz uruchamiać generatora ani poznawać
całej architektury. Oba działania można też zamówić w jednej rozmowie.

`../personal-hub` jest już utworzonym, pustym hubem do pracy z agentem.
Do codziennego przetwarzania materiałów nie potrzebujesz otwierać master-hub.

[Krótki plan](docs/plan.md) · [Dokładniejszy prompt](docs/first-run.md)

## Kolejne huby — kiedy będą potrzebne

Każdy nowy hub ma powstawać poza tym projektem, w osobnym katalogu
i osobnym repozytorium, np. `../marketing-lab`. Hub osobisty jest już
wydzielony do `../personal-hub` i nie wymaga dostępu do generatora.

Wystarczy poprosić agenta: „Utwórz osobny hub marketing-lab obok master-hub”.
Generator tworzy pliki. Inicjalizacja Git i ewentualnego zdalnego repozytorium
to osobne kroki. Nie tworzymy teraz kolejnego huba.

<details>
<summary>Polecenie generatora i skill</summary>

Z katalogu master-hub, Python 3.10+, bez dodatkowych bibliotek:

```sh
python3 skills/create-knowledge-hub/scripts/create_hub.py \
  --dest ../marketing-lab \
  --id marketing-lab \
  --title "Laboratorium marketingu" \
  --kind personal \
  --owner "Piotr" \
  --domain marketing
```

`--dry-run` pokazuje plan bez zapisu. Katalog docelowy musi być nowy.
Dla firmy użyj `--kind company` i jej właściciela. Rodzaj huba jest opisem,
nie kontrolą uprawnień; osobno konfigurujemy dostępy.

[Skill](skills/create-knowledge-hub/SKILL.md) razem ze skryptem i szablonami
jest przenośnym katalogiem. Nie został zainstalowany globalnie. Agent może
go użyć po przeczytaniu tego pliku bez ponownego projektowania huba.

</details>

## Aktualizacja OKF

Obecny profil korzysta z OKF 0.2. Wersja jest zapisana w `hub.json` i głównym
`knowledge/index.md`. Aktualizacja szablonów obejmie nowe huby. Dla istniejących
potrzebna będzie osobna migracja zależna od zmian specyfikacji.

Nie ma jeszcze automatycznego migratora. Sama zmiana numeru wersji nie migruje
dokumentów. Przed migracją zachowujemy poprzedni stan, sprawdzamy zmiany na
kopii i dopiero przyjmujemy wynik. Nie musimy wdrażać każdej nowej wersji od razu.

## Co działa, a co zostawiamy na później

Gotowe: generator, kontrakt pracy agenta i osobne repozytorium huba osobistego. Przetwarzanie
wykonuje agent według kontraktu. Automatyczny ingest, walidator OKF,
synchronizacja i integracje operacyjne nie są zaimplementowane.

[Opis przepływu wiedzy](docs/architecture.md) i [diagram](docs/architecture.svg)
pokazują prosty model: bronze → rozwijana wiki w silver → różne materiały gold.
Zachowany jest również [wcześniejszy diagram całego systemu](docs/system-architecture.svg),
obejmujący huby, dystrybucję wiedzy i agentów operacyjnych.

Testy generatora: `python3 -B -m unittest discover -s tests -v`.

Inspiracje: [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
[OKF 0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
i lokalny projekt `../founders-workbooks`.
