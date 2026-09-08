# Pierwsze przetwarzanie

Hub osobisty jest w osobnym repozytorium `personal-hub`, obok `master-hub`.
Otwórz go jako projekt i vault Obsidiana. Wybierz materiał tekstowy i zadanie,
do którego ma się przydać. Nie trzeba najpierw projektować całej taksonomii.

Przykładowe polecenie do agenta:

> Pracuj w repozytorium `personal-hub`. Przeczytaj `AGENTS.md`, `SCHEMA.md` i `hub.json`.
> Materiał wejściowy znajduje się w [podaj ścieżkę]. Chcę na jego podstawie
> przygotować [np. scenariusz rozmowy z potencjalnym klientem]. Zachowaj
> tekst w bronze wraz z pochodzeniem. Opracuj potrzebne koncepty silver
> i przygotuj jeden produkt gold. Wskaż źródła, warunki stosowania,
> niepewności oraz własne wnioski. Uaktualnij indeksy i dziennik. Pokaż mi
> propozycję do przeglądu; nie oznaczaj jej jako zatwierdzonej.

W nawiasach wpisz właściwą ścieżkę i cel. Agent może tworzyć lokalne wersje
robocze zgodnie z poleceniem; publikacja do innych hubów i uruchamianie
zewnętrznych działań są osobnymi operacjami.

Kolejne polecenie:

> W [wskazany dokument] popraw [opis]. Zapisz tę korektę w `90-decisions`
> wraz z zakresem i uzasadnieniem, a następnie sprawdź powiązane opracowania.

Na pierwszym etapie agent wykonuje te operacje według kontraktu. Generator
tworzy strukturę, nie wywołuje modelu i nie przetwarza źródeł.
