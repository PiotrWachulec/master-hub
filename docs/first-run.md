# Trzy polecenia do codziennej pracy

Pracuj w hubie wskazanym przez użytkownika, nie w repozytorium silnika.
Otwórz katalog huba jako projekt, opcjonalnie jako vault Obsidiana.
Istniejący hub nie wymaga ponownego uruchamiania generatora.

## 1. Dodaj materiał — bez określania zastosowania

> Dodaj materiał z [ścieżka] do bazy wiedzy. Zachowaj tekst lub referencję
> do oryginału i transkrypcję w bronze. Przeanalizuj go i włącz do wiki silver:
> połącz pojęcia ze znaną wiedzą, zachowaj źródła, przykłady, wyjątki
> i sprzeczności. Nie twórz jeszcze gold.

Wystarczy ścieżka do notatki lub transkrypcji. Kolejne materiały rozwijają
tę samą bazę; nie musisz jeszcze wiedzieć, jak je wykorzystasz.

## 2. Zapytaj bazę o to, co już wie

> Co wiem o [temat]? Odpowiedz z linkami do wiki.

Domyślnie nic nie zapisuje — agent przeszukuje indeks i pełny tekst silver/gold
i odpowiada w rozmowie. Gdy odpowiedź jest warta zachowania:

> Zarchiwizuj tę odpowiedź w mojej bazie.

Agent zapisuje ją jako nowy dokument silver z odwołaniami do cytowanych
artykułów, bez tworzenia nowego źródła bronze — to zsyntetyzowana odpowiedź,
nie materiał źródłowy.

## 3. Zamów rezultat z istniejącej wiedzy

> Przygotuj z mojej bazy wiedzy wkład do ebooka o [XYZ], w formie [opis].
> Utwórz katalog gold pod ten ebook. Oprzyj go na silver, zachowaj referencje
> do moich materiałów źródłowych. Po brakujące szczegóły lub cytaty sięgnij
> do bronze. Wskaż luki i własne hipotezy.

Albo:

> Przygotuj materiał do fiszek o [XYZ] w formie pytanie–odpowiedź,
> z referencjami do źródeł, w osobnym katalogu gold.

Nie potrzebujesz nowego wejścia. Jeśli zmieniasz koncepcję, możesz poprosić:

> Z tej samej wiedzy przygotuj wariant ebooka dla [inny odbiorca].
> Zapisz go w nowym katalogu gold, zachowując poprzedni wynik.

## Korekty i zakres pracy

> W [wskazany dokument] popraw [opis]. Zapisz tę korektę w `90-decisions`
> wraz z zakresem i uzasadnieniem, a następnie sprawdź powiązane opracowania.

Możesz też zamówić dodanie materiału i konkretny rezultat w jednym poleceniu.
Nie jest to obowiązkowy przebieg każdego importu.

Agent czyta `AGENTS.md`, `SCHEMA.md`, `hub.json` i indeks wiedzy,
aktualizuje odpowiednie indeksy oraz log, a nowe opracowania przedstawia jako
wersje robocze do przeglądu. W profilu 0.2.2 uruchamia lokalny walidator
i ograniczoną pętlę naprawy zgodnie z kontraktem, a po redakcji silver/gold
dodatkowo nieblokujący raport `scripts/check_evidence.py`. Brak kontroli lub
naruszenia po wyczerpaniu limitu zatrzymują pracę; nie są raportowane jako
sukces. Publikacja opracowań i działania zewnętrzne wymagają osobnego zlecenia.

Na tym etapie pracę wykonuje agent według kontraktu. Generator tworzy
strukturę, nie wywołuje modelu i nie przetwarza źródeł.

## Opcjonalnie: przeglądanie w Obsidianie

Wtyczka społecznościowa [Dataview](https://github.com/blacksmithgu/obsidian-dataview)
pozwala odpytywać frontmatter dokumentów bez zmian w plikach ani w kontrakcie,
np. lista szkiców w silver (`TABLE status, title FROM "knowledge/10-silver"
WHERE status = "draft"`). To wyłącznie warstwa podglądu dla człowieka — agent
i walidator jej nie wymagają ani nie używają.
