---
name: create-knowledge-hub
description: Twórz samodzielne huby wiedzy Markdown dla Obsidiana według wzorca bronze–silver–gold i OKF 0.2. Używaj przy zakładaniu kolejnej biblioteki osobistej lub huba firmy; istniejące huby wymagają osobnej migracji.
---

# Utwórz hub wiedzy

Ten pakiet zawiera generator i kontrakt pracy wyprowadzony z Founders
Workbooks. Wszystkie potrzebne zasoby znajdują się w tym katalogu.

## Przebieg

1. Ustal z kontekstu katalog docelowy, identyfikator ASCII, nazwę, właściciela,
   rodzaj `personal` lub `company` i temat. Dopytaj tylko o dane, których brak
   zmienia granicę własności lub przeznaczenie. Sama nowa tematyka nie wymaga
   osobnego huba; uzasadniają go także niezależna praca, dostęp i cykl publikacji.
2. Przeczytaj [kontrakt](assets/hub/SCHEMA.md) oraz
   [zasady profilu](references/profile.md). Dostosuj typy do zastosowania
   po wygenerowaniu huba; nie przenoś automatycznie taksonomii prawnej.
3. Uruchom skrypt ścieżką względem tego pakietu:

   ```sh
   python3 scripts/create_hub.py --dest /wybrana/sciezka/nowy-hub \
     --id nowy-hub --title "Nowy hub" --kind personal \
     --owner "Właściciel" --domain "Temat"
   ```

   To przykład uruchomienia z katalogu skilla. Z innego katalogu podaj pełną
   ścieżkę skryptu. `--dest` jest zawsze względem katalogu wywołania. Skrypt
   potrzebuje Pythona 3.10+, bez bibliotek dodatkowych. `--dry-run` nic nie zapisuje.
4. Sprawdź konfigurację, indeksy i kontrakt wygenerowanego huba. Istniejący
   katalog jest odrzucany — nie usuwaj go, żeby ominąć tę ochronę. Wybierz
   nowy cel lub przygotuj migrację, jeśli użytkownik o nią poprosił.
5. Podaj lokalizację vaulta i polecenie pierwszego przetwarzania. Nie nazywaj
   samego szkieletu działającym automatycznym pipeline'em.

Generator nie pobiera materiałów, nie inicjalizuje synchronizacji, nie
konfiguruje kont i nie zmienia budżetów. Źródła i dane właścicieli pozostają
w swoim zakresie. Tworzenie huba nie oznacza zgody na import danych z innych hubów.

## Dalsza praca

Hub ma własne AGENTS.md i SCHEMA.md i działa bez dostępu do tego pakietu.
Użytkownik redaguje wiedzę przez rozmowę z agentem. Korekty zapisuj jako
decyzje, żeby kolejne przetwarzanie je uwzględniało. Współdzielony silnik,
importy pakietów i automatyzacje operacyjne rozwijaj jako oddzielne funkcje.
