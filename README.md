# Master Hub

Przenośne narzędzie do tworzenia i obsługi hubów wiedzy Markdown:
generator, skille, szablony i kontrakt pracy agenta.

To repozytorium nie przechowuje treści, rejestru ani konfiguracji konkretnych
hubów. Użytkownik wskazuje cel każdej operacji. Wygenerowany hub działa bez
dostępu do tego repozytorium.

## Środowisko Python

Skrypty i testy zawsze uruchamiamy w lokalnym `.venv`, również jeśli używają
tylko biblioteki standardowej. Jeśli `.venv` nie istnieje, w katalogu silnika
utwórz je przez `python3 -m venv .venv` (Python 3.10+). Systemowy Python
służy tylko do utworzenia środowiska; potem używaj `.venv/bin/python`.
Na Windows odpowiednikiem jest `.venv/Scripts/python.exe`.

Każdy hub tworzy własne środowisko po wygenerowaniu. Nie kopiujemy `.venv`
między projektami ani do Git. Nie nadpisujemy istniejącego, niesprawnego
środowiska. Nie instalujemy paczek globalnie, przez `pip --user` ani `sudo`.
Ewentualne zależności instalujemy przez `.venv/bin/python -m pip` bez
`--system-site-packages`. Generator, walidator i ich testy nie wymagają paczek.

## Utwórz hub

Poproś agenta o użycie [create-knowledge-hub](skills/create-knowledge-hub/SKILL.md)
i wskaż nowy katalog, nazwę, właściciela oraz temat. Albo uruchom
z katalogu master-hub (Python 3.10+, biblioteka standardowa):

```sh
.venv/bin/python skills/create-knowledge-hub/scripts/create_hub.py \
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

## Kopia zdalna właściwych hubów

Nowe huby zobowiązują agenta do commit i push po zakończonych, zwalidowanych
zadaniach oraz spójnych etapach dłuższej pracy. Nie trzeba osobno mówić
„wypychaj”. Cel i dostęp do repozytorium uzgadnia się przy pierwszej
konfiguracji; generator sam nie tworzy Git ani remote. Agent potwierdza
commit w repozytorium zdalnym lub zgłasza brak aktualnej kopii.
Obowiązek jest jawny w `hub.json` profilu 0.2.2:
`policy.remote_copy: "required_after_validated_task"`.

To instrukcja pracy agenta, nie backup w tle. Obejmuje wypchnięte pliki Git,
nie zewnętrzne nagrania czy pliki ignorowane. Istniejące huby nie zmieniają
się automatycznie: [jawne przyjęcie reguły](docs/hub-git-backup.md).

## Dwa przenośne skille

- [create-knowledge-hub](skills/create-knowledge-hub/SKILL.md) — tworzy nowy hub.
- [curate-knowledge-hub](skills/curate-knowledge-hub/SKILL.md) — obsługuje zadanie
  w istniejącym repozytorium Git według jego własnego kontraktu.

Skille nie są zainstalowane globalnie. Można przekazać agentowi ścieżkę do
SKILL.md albo przenieść cały wybrany pakiet. Sam merge w silniku nie zmienia
instrukcji istniejących hubów ani konfiguracji innych agentów.

## Wersje i możliwości

Format: OKF 0.2. Lokalny profil pracy: 0.2.2, zapisany w `hub.json`.
Zmiana szablonów obejmuje nowe huby; istniejące wymagają jawnej migracji.
Nie ma automatycznego migratora ani obowiązku natychmiastowego przyjęcia
każdej nowej wersji OKF.

Na przyszłość zachowujemy [procedurę migracji 0.1.1 → 0.2.0](docs/migration-0.2.0.md).
Przyjęcie kopii Git opisuje [aktualizacja 0.2.0 → 0.2.1](docs/hub-git-backup.md).
Uziemienie faktów, triage źródeł i Query/Archive opisuje
[aktualizacja 0.2.1 → 0.2.2](docs/migration-0.2.2.md).
Nie zakładamy obecnie żadnych istniejących hubów i nie wykonujemy migracji.
Dokument nie wymaga ani nie uruchamia rejestru hubów.

Działają generator, instrukcje redakcji, lokalny walidator struktury
i nieblokujący raport uziemienia faktów. Automatyczny ingest, synchronizacja,
pełny walidator OKF i integracje operacyjne nie są zaimplementowane.

### Świadomie niezbudowane

Po wzorze sekcji „Design Boundaries” w README `karpathy-llm-wiki` (zob.
„Inspiracje” niżej) — krótkie „dlaczego”, nie tylko „czego brak”:

- **Precyzyjne kotwiczenie cytatu do pojedynczego przypisu** w kontroli
  uziemienia faktów — realne błędy to niemal zawsze „wartość nieobecna w
  żadnym źródle dokumentu”, co łapie sprawdzenie całego dokumentu; kotwiczenie
  chroniłoby przed awarią, która w praktyce się nie zdarza.
- **Automatyczne wykrywanie świeżości po hashu źródeł bronze** — bronze jest
  niezmienne z definicji kontraktu; nowa wiedza i tak wchodzi jako nowy plik
  przez ingest, nie przez edycję istniejącego.
- **Numeryczne wyniki pewności/jakości treści** — fałszywa precyzja bez
  kalibracji; siła dowodu należy do prozy i przeglądu człowieka, nie do liczby.
- **Wyszukiwanie wektorowe lub grafowe po wiedzy** — przy skali pojedynczego
  huba grep i odczyt plików są wystarczające i bardziej przewidywalne; warto
  to dodać dopiero, gdy trafność mierzalnie spadnie.
- **Automatyczne haki i harmonogramy uruchomień** — należą do uprzęży agenta
  (hooki, cron), nie do przenośnego, narzędzio-agnostycznego skilla.

## Kontrola struktury w wygenerowanym hubie

W katalogu huba utwórz `.venv`, jeśli go nie ma (`python3 -m venv .venv`).
Potem uruchom:

```sh
.venv/bin/python -B scripts/validate_hub.py
```

Skrypt jest częścią huba. Nie potrzebuje generatora, sieci ani bibliotek
zewnętrznych i niczego nie zapisuje. Na stdout daje JSON, np.:

```json
{"violations": 0, "errors": [], "warnings": []}
```

Diagnostyka `plik:linia: komunikat` idzie na stderr. Kod wyjścia 0 oznacza
brak naruszeń. Kontrakt quality ustala próg 0 i maksymalnie 5 cykli
naprawa/kontrola po pierwszym sprawdzeniu. Zmiana kontroli wymaga osobnego
PR, nie może być sposobem na ukrycie błędów treści. To kontrola lokalnego,
udokumentowanego podzbioru formatu, nie dowód prawdziwości ani walidacja OKF.

Osobno, `.venv/bin/python -B scripts/check_evidence.py` daje nieblokujący
raport: czy liczby, daty i cytaty w `10-silver`/`20-gold` dają się znaleźć
w treści wskazanych źródeł bronze. Zawsze kończy się kodem 0 i nie wchodzi
do progu `violations` — podejrzenia ocenia człowiek, nie skrypt.

[Architektura](docs/architecture.md) · [Diagram przepływu](docs/architecture.svg) ·
[Opcjonalny model wielu hubów](docs/system-architecture.svg)

Testy w katalogu silnika: `.venv/bin/python -B -m unittest discover -s tests -v`.

Inspiracje: [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
[OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
i [karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) (Astro-Han,
MIT) — niezależna implementacja tego samego pomysłu, źródło wzorca
ingest/query/lint oraz bezpośrednia inspiracja dla `scripts/check_evidence.py`
i konwencji triage/Status wprowadzonych w profilu 0.2.2.
