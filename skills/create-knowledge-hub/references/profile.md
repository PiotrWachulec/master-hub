# Profil nowego huba

`hub.json` konfiguruje lokalny wzorzec (wersja 0.1.0). Nie jest elementem
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

Domyślne typy: Źródło, Koncept, Metoda, Zasada, Przykład, Synteza, Narzędzie,
Decyzja. Nie są zamkniętą taksonomią wiedzy. Nowe typy dodawaj, kiedy odróżniają
rzeczy potrzebne odbiorcy, np. eksperyment, metrykę lub segment klientów.

Katalog skilla można skopiować w całości. Szablony są zasobami generatora.
Zmiana szablonu dotyczy nowych hubów; istniejący hub zachowuje własny kontrakt.
