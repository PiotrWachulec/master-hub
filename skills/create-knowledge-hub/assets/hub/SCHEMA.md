# Kontrakt przetwarzania wiedzy — profil 0.1.0

Ten kontrakt opisuje pracę w jednym hubie. Bundle OKF 0.2 obejmuje wyłącznie
`knowledge/`. Konfiguracja i instrukcje w katalogu nadrzędnym nie należą
do bundle'a. Dodatkowe reguły poniżej są lokalnym profilem pracy, nie wymaganiami OKF.

## Warstwy i pochodzenie

| Miejsce | Zawartość | Zasada pracy |
|---|---|---|
| `00-bronze` | tekstowe wersje źródeł po ekstrakcji/transkrypcji | zachowuj wejście; kolejne wersje jako nowe pliki |
| `10-silver` | pojęcia, zasady, syntezy, sprzeczności | rozwijaj istniejącą wiedzę z zachowaniem atrybucji |
| `20-gold` | produkty dla konkretnego zastosowania | opisuj odbiorcę, sposób użycia i ograniczenia |
| `90-decisions` | korekty i decyzje użytkownika | zapisuj zakres, powód i dokumenty objęte decyzją |
| `imports` | przyszłe lokalne kopie wydań innych hubów | zachowuj oryginał importu; adaptacje twórz osobno |

Nowy materiał musi mieć identyfikację pochodzenia. Dla nagrania zachowaj
lokalizację oryginału, wersję transkrypcji i znaczniki czasu, jeśli są dostępne.
Zapisuj braki tych informacji zamiast je wymyślać. Nie sprowadzaj źródła do
streszczenia przed zachowaniem dostępnego pełnego tekstu w bronze.

## Dokumenty i odsyłacze

Każdy `.md` w bundle'u poza `index.md` i `log.md` ma frontmatter YAML.
Lokalnie wymagamy `type`, `title`, `description`, jawnego `status` i informacji
`generated` zgodnej z rzeczywistym autorstwem. Silver i gold wymagają `sources`.
Typy startowe są w `hub.json`; można je świadomie rozszerzać.

Przykład szkieletu nowego konceptu — wartości czasu i autorstwa trzeba
zastąpić rzeczywistymi danymi, a wskazane źródło musi istnieć:

```yaml
---
type: Metoda
title: Rozmowa o problemie klienta
description: Scenariusz zbierania konkretnych przykładów problemu.
tags: [marketing, badania]
status: draft
sources:
  - id: material-a
    resource: ../00-bronze/material-a-v1.md
    title: Materiał wejściowy A
---
```

Przy faktycznym zapisie dodaj `generated: {by: ..., at: ...}` z poprawnym
aktorem (np. `process:nazwa`, `human:identyfikator` lub `producent/wersja`)
i czasem ISO 8601 ze strefą. Nie kopiuj fikcyjnej nazwy modelu z przykładów.

W treści przypis `[^material-a]` łączy twierdzenie z `sources[].id`.
Definicja przypisu precyzuje stronę, sekcję lub czas. Stosuj standardowe
względne odsyłacze Markdown i stabilne nazwy plików ASCII. Przy przeniesieniu
pliku aktualizuj odsyłacze i wskazania źródeł. Identyfikacja konceptu w OKF
wynika ze ścieżki względem korzenia bundle'a.

`index.md` zawiera odsyłacze i krótkie opisy. Jedynie główny indeks bundle'a
ma frontmatter `okf_version: "0.2"`. `log.md` ma wpisy pod datami YYYY-MM-DD,
najnowsze na górze, bez frontmatteru. Log dokumentuje zmiany; nie zastępuje
źródeł ani decyzji użytkownika.

## Jakość treści

- Zachowuj warunki stosowania, wyjątki i rozbieżności między źródłami.
- Oznaczaj własną syntezę lub hipotezę jawnie. Wypełnienie luki wymaga
  materiału źródłowego albo wyraźnie opisanej hipotezy, nie pozorowanej atrybucji.
- Gold oznacza przygotowanie do użycia, a nie automatyczne zatwierdzenie.
  Dla procedur oddziel instrukcję działania, uzasadnienie i materiały pomocnicze,
  jeśli poprawia to użyteczność.
- Rozmowa zakończona wartościową analizą może zasilić wiki, z zachowaniem
  pochodzenia i rozróżnieniem decyzji, obserwacji i twierdzeń.

## Praca agenta

1. Przyjmij źródło w nowym pliku bronze. Sprawdź dostępne wejścia, żeby
   uniknąć duplikatu. Automatyczny rejestr hashy jest planowany, nie zainstalowany.
2. Przeczytaj indeksy, powiązane koncepty i decyzje użytkownika. Dobieraj
   kontekst do zadania; nie ładuj całej biblioteki bez potrzeby.
3. Opracuj propozycję zmian silver. W razie kilku opisów tego samego pojęcia
   połącz źródła i perspektywy, zachowując rozbieżności.
4. Zbuduj lub uaktualnij potrzebne gold, sprawdź odsyłacze i przypisy,
   uzupełnij indeksy i log. Sprawdzenie struktury nie dowodzi prawdziwości.
5. Przedstaw zmiany i kwestie otwarte. Zapisz otrzymane korekty i decyzje
   w `90-decisions`, żeby kolejne przebiegi je uwzględniały.

W przypadku pracy równoległej wyniki robocze mają oddzielne miejsca zapisu;
jedno uzgodnione scalanie publikuje wynik. Nie uruchamiaj dodatkowych agentów
wyłącznie dlatego, że kontrakt opisuje możliwość pracy równoległej.

## Zatwierdzanie i zmiany

`status` ma wartości `draft`, `stable`, `deprecated`. Początkowo opracowania
agenta są `draft`. Przejście do `stable` opiera się na decyzji użytkownika
lub późniejszej, wyraźnie ustalonej polityce danego procesu.

Pole `verified` opisuje sprawdzenie treści, nie samą zgodę na jej użycie.
Agent nie nadaje sobie ludzkiej weryfikacji. Może zapisać rzeczywisty wynik
przeglądu użytkownika, wskazując decyzję i zakres sprawdzonej treści.
Po zmianie merytorycznej wcześniejsza weryfikacja zostaje w historii starej
wersji; nowa wymaga ponownego sprawdzenia. Przyszły mechanizm zatwierdzania
powinien wiązać decyzję z hashem treści.

Opcjonalne `stale_after` określa potrzebę przeglądu w czasie. Nie odnawiaj
aktualności tylko dlatego, że dokument został ponownie wygenerowany.

## Autonomia i własność

Trzy osobne zakresy: redakcja wiki, publikacja do innych hubów oraz działania
operacyjne. `hub.json` opisuje początkową politykę: agent przygotowuje lokalne
wersje robocze, publikacja wymaga przyjęcia, działania zewnętrzne są wyłączone.
To instrukcja pracy, a nie techniczna kontrola uprawnień.

Nie włączaj do huba danych innego właściciela bez zadania, które je obejmuje.
Nie kopiuj sekretów do wiedzy. Przy imporcie przyszłych pakietów zachowuj
wersję i pochodzenie, a lokalne adaptacje zapisuj poza kopią importowaną.
Zmiana wiedzy nie daje uprawnienia do zmiany budżetu ani konfiguracji firmy.
