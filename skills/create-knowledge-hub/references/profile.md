# Profil nowego huba

`hub.json` konfiguruje lokalny wzorzec (wersja 0.2.1). Nie jest elementem
standardu OKF. Deklaracje polityki są instrukcjami dla agenta; generator
nie instaluje procesu, który je technicznie egzekwuje.

| Pole | Znaczenie |
|---|---|
| `id` | identyfikator huba, małe litery ASCII, cyfry i myślniki |
| `title` | nazwa czytelna dla człowieka |
| `kind` | `personal` lub `company`; opis przeznaczenia, nie uprawnienie |
| `owner` | właściciel/odpowiedzialny podany przez użytkownika |
| `domain` | temat początkowy; może później obejmować kilka dziedzin |
| `bundle_root` | `knowledge`, granica dokumentów OKF |
| `concept_types` | początkowy słownik; dostosuj go po pierwszym materiale |
| `policy` | etap automatyzacji redakcji, publikacji i działań zewnętrznych |
| `policy.remote_copy` | w 0.2.1 wymagane `required_after_validated_task`: commit i push po sprawdzonym zadaniu; cel wymaga uzgodnienia |
| `quality` | lokalny walidator, metryka violations, próg 0 i limit 5 cykli naprawy |

Domyślne typy: Źródło, Koncept, Metoda, Zasada, Przykład, Synteza, Narzędzie,
Decyzja. Nie są zamkniętą taksonomią wiedzy. Nowe typy dodawaj, kiedy odróżniają
rzeczy potrzebne odbiorcy, np. eksperyment, metrykę lub segment klientów.

Katalog skilla można skopiować w całości. Szablony są zasobami generatora.
Zmiana szablonu dotyczy nowych hubów; istniejący hub zachowuje własny kontrakt.

Profil 0.2.1 dodaje jawny obowiązek kopii Git w policy.remote_copy oraz jego
kontrolę w walidatorze. Nie jest to uprawnienie do dowolnego remote ani
automatyczna aktualizacja starszych hubów. Procedura przyjęcia 0.2.0 → 0.2.1
jest w docs/hub-git-backup.md w repozytorium generatora.

Profil 0.2.0 dodał niezależny skrypt scripts/validate_hub.py do huba.
Format OKF pozostaje 0.2. Migracja z 0.1.1 jest ręczna i wymaga przeglądu
istniejących metadanych oraz ścieżek; procedura w docs/migration-0.2.0.md
w repozytorium generatora. Sam hub nie potrzebuje tego repozytorium do walidacji.

## Migracja istniejącego huba z 0.1.0 do 0.1.1

To aktualizacja instrukcji: dodawanie wiedzy i zamawianie gold stają się
niezależnymi działaniami. Nie zmienia formatu OKF 0.2 ani ścieżek dokumentów.
Po zgodzie użytkownika zaktualizuj AGENTS.md, SCHEMA.md, przykłady w README.md
i opisy w indeksach wiedzy, silver oraz gold, zachowując własne reguły i odsyłacze
huba. Następnie ustaw `profile_version` w hub.json na `0.1.1`.
Nie uruchamiaj ponownie generatora na istniejącym hubie; nie nadpisuj treści
ani ustawień Obsidiana. Sprawdź diff i zachowaj poprzedni stan w historii Git.
