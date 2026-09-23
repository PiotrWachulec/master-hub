# Plan użycia narzędzia

1. Wskaż nowy katalog i utwórz hub generatorem. Dla istniejącego huba
   nie uruchamiaj generatora ponownie — pracuj według jego kontraktu.
2. Otwórz hub jako projekt dla agenta. Dodaj jeden materiał, rozwijając
   bronze i silver bez obowiązkowego gold.
3. Przejrzyj opracowanie i przekaż korekty przez rozmowę.
4. Gdy pojawi się potrzeba, zamów konkretny rezultat gold.
5. Dopiero doświadczenie pokaże, jaki kolejny mechanizm jest potrzebny.

[Przykłady poleceń](first-run.md) · [Architektura](architecture.md)

## Rozwój silnika

Generator i skille nie utrzymują rejestru swoich użytkowników ani hubów.
Zmiany lokalnego kontraktu mają opis migracji; nie są propagowane automatycznie.
Automatyczny ingest, synchronizacja, pełna walidacja OKF i operacyjne
integracje pozostają poza zakresem obecnej implementacji.
