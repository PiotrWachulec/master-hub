---
name: create-knowledge-hub
description: Twórz samodzielne huby wiedzy Markdown dla Obsidiana według wzorca bronze–silver–gold i OKF 0.2. Używaj przy zakładaniu kolejnej biblioteki osobistej lub huba firmy; istniejące huby wymagają osobnej migracji.
---

# Utwórz hub wiedzy

Ten pakiet zawiera przenośny generator i kontrakt pracy z wiedzą.
Wszystkie potrzebne zasoby znajdują się w tym katalogu. Nie zakłada
istnienia konkretnego huba ani dostępu do innych repozytoriów.

## Przebieg

1. Ustal z kontekstu katalog docelowy, identyfikator ASCII, nazwę, właściciela,
   rodzaj `personal` lub `company` i temat. Dopytaj tylko o dane, których brak
   zmienia granicę własności lub przeznaczenie. Sama nowa tematyka nie wymaga
   osobnego huba; uzasadniają go także niezależna praca, dostęp i cykl publikacji.
2. Przeczytaj [kontrakt](assets/hub/SCHEMA.md) oraz
   [zasady profilu](references/profile.md). Dostosuj typy do zastosowania
   po wygenerowaniu huba; nie przenoś automatycznie taksonomii prawnej.
3. Użyj `.venv` w repozytorium silnika lub uzgodnionym katalogu roboczym,
   gdy pakiet skilla jest przeniesiony. Jeśli go nie ma, utwórz środowisko
   poleceniem `python3 -m venv .venv` w tym katalogu (Python 3.10+).
   Systemowego Pythona używaj tylko do utworzenia venv. Uruchom generator
   interpreterem środowiska, podając ścieżkę do tego pakietu:

   ```sh
   .venv/bin/python /sciezka-do-skilla/scripts/create_hub.py --dest /wybrana/sciezka/nowy-hub \
     --id nowy-hub --title "Nowy hub" --kind personal \
     --owner "Właściciel" --domain "Temat"
   ```

   Na Windows użyj `.venv/Scripts/python.exe`. Nie wymaga to aktywacji powłoki.
   Nie nadpisuj niesprawnego istniejącego venv; zgłoś problem. Bez globalnego
   pip, pip --user, sudo pip i --system-site-packages; ewentualne paczki
   instaluj tylko przez interpreter venv z `-m pip`. Generator nie wymaga paczek.
   `--dest` jest względem katalogu wywołania. `--dry-run` nie zapisuje huba;
   wcześniejsze utworzenie środowiska to osobny krok przygotowania narzędzia.
4. Sprawdź konfigurację, indeksy i kontrakt wygenerowanego huba. Istniejący
   katalog jest odrzucany — nie usuwaj go, żeby ominąć tę ochronę. Wybierz
   nowy cel lub przygotuj migrację, jeśli użytkownik o nią poprosił.
   W nowym hubie utwórz własne `.venv`, jeśli go nie ma, przez
   `python3 -m venv .venv` uruchomione z katalogu huba. Nie kopiuj środowiska
   silnika. Uruchom `<katalog-huba>/.venv/bin/python -B <katalog-huba>/scripts/validate_hub.py`
   (na Windows odpowiednik w `.venv/Scripts`) i pokaż JSON
   oraz kod wyjścia. Nowy szkielet powinien mieć zero naruszeń. To kontrola
   struktury lokalnego profilu, nie dowód jakości przyszłych treści.
5. Ustal z użytkownikiem repozytorium zdalne i zakres dostępu do danych,
   jeśli nie wynika to z wcześniejszych uzgodnień. Generator nie inicjalizuje
   Git: jego konfiguracja wymaga wskazanego celu i zgody; nie twórz publicznego
   repo na podstawie samej nazwy huba. Hub w katalogu projektu używa jego Git.
   Przy uzgodnionym celu wykonaj pierwszy commit i push zwalidowanego szkieletu
   według AGENTS.md huba oraz potwierdź commit w remote. Bez skonfigurowanej
   kopii powiedz wyraźnie, że szkielet istnieje tylko lokalnie i wymaga
   dokończenia konfiguracji — nie przedstawiaj go jako zabezpieczonego.
6. Podaj lokalizację vaulta i dwa niezależne polecenia: dodanie materiału
   do bronze/silver oraz zamówienie wyniku gold z istniejącej wiedzy.
   Dodanie materiału nie wymaga celu biznesowego. Nie nazywaj
   samego szkieletu działającym automatycznym pipeline'em.
   Wyjaśnij, że agent robi commit i push po sprawdzonych zadaniach; nie ma
   procesu backupu w tle ani kopii nagrań przechowywanych poza Git.

Generator nie pobiera materiałów, nie inicjalizuje synchronizacji, nie
konfiguruje kont i nie zmienia budżetów. Źródła i dane właścicieli pozostają
w swoim zakresie. Tworzenie huba nie oznacza zgody na odczyt innych hubów.

## Dalsza praca

Hub ma własne AGENTS.md i SCHEMA.md i działa bez dostępu do tego pakietu.
Użytkownik redaguje wiedzę przez rozmowę z agentem. Korekty zapisuj jako
decyzje, żeby kolejne przetwarzanie je uwzględniało. Nie twórz mechanizmu
importu, dystrybucji pakietów ani synchronizacji między hubami. Dodatkowy
kontekst z huba wskazanego przez użytkownika można odnotować zwykłym tekstem
w opracowaniu; zasady lokalnych źródeł opisuje SCHEMA.md.
