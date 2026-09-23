# Plan użycia narzędzia

1. Wskaż nowy katalog i utwórz hub generatorem. Dla istniejącego huba
   nie uruchamiaj generatora ponownie — pracuj według jego kontraktu.
   Uzgodnij repozytorium zdalne i dostęp; pierwszy commit i push szkieletu
   potwierdza uruchomienie kopii Git. Bez tego hub istnieje tylko lokalnie.
2. Otwórz hub jako projekt dla agenta. Dodaj jeden materiał, rozwijając
   bronze i silver bez obowiązkowego gold.
3. Agent sprawdza strukturę lokalnym walidatorem (profil 0.2.0), poprawia
   naruszenia w ramach limitu i przedstawia wynik. Przejrzyj treść i przekaż
   korekty przez rozmowę — zielona struktura nie zastępuje tego przeglądu.
   Agent wykonuje commit i push oraz potwierdza obecność commita w remote;
   brak kopii zgłasza jako niedokończony etap zadania.
4. Gdy pojawi się potrzeba, zamów konkretny rezultat gold.
5. Dopiero doświadczenie pokaże, jaki kolejny mechanizm jest potrzebny.

[Przykłady poleceń](first-run.md) · [Architektura](architecture.md)

## Rozwój silnika

Generator i skille nie utrzymują rejestru swoich użytkowników ani hubów.
Zmiany lokalnego kontraktu mają opis migracji; nie są propagowane automatycznie.
Walidator lokalnego profilu jest dostarczany w każdym nowym hubie.
Automatyczny ingest, synchronizacja, pełna walidacja OKF i operacyjne
integracje pozostają poza zakresem obecnej implementacji.
