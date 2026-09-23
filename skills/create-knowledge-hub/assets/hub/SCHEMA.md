# Kontrakt przetwarzania wiedzy — profil 0.2.0

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

Nowy materiał musi mieć identyfikację pochodzenia. Dla nagrania zachowaj
lokalizację oryginału, wersję transkrypcji i znaczniki czasu, jeśli są dostępne.
Zapisuj braki tych informacji zamiast je wymyślać. Nie sprowadzaj źródła do
streszczenia przed zachowaniem dostępnego pełnego tekstu w bronze.

## Dokumenty i odsyłacze

Każdy `.md` w bundle'u ma frontmatter YAML z metadanymi dokumentu, poza
zamkniętą listą plików nawigacyjnych i głównym logiem (ścieżki względem huba):

- `knowledge/index.md`;
- `knowledge/00-bronze/index.md`;
- `knowledge/10-silver/index.md`;
- `knowledge/20-gold/index.md`;
- `knowledge/90-decisions/index.md`;
- `knowledge/log.md`.

Inne pliki nazwane `index.md` lub `log.md`, np.
`knowledge/20-gold/ebook/index.md`, są zwykłymi dokumentami, nie wyjątkami.
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
tags: ["marketing", "badania"]
status: draft
sources:
  - id: material-a
    resource: ../00-bronze/material-a-v1.md
    title: Materiał wejściowy A
---
```

Przy faktycznym zapisie dodaj blok `generated` z polami `by` i `at`, z poprawnym
aktorem (np. `process:nazwa`, `human:identyfikator` lub `producent/wersja`)
i czasem ISO 8601 ze strefą. Nie kopiuj fikcyjnej nazwy modelu z przykładów.

W treści przypis `[^material-a]` łączy twierdzenie z `sources[].id`.
Definicja przypisu precyzuje stronę, sekcję lub czas. Stosuj standardowe
względne odsyłacze Markdown i stabilne nazwy plików ASCII. Przy przeniesieniu
pliku aktualizuj odsyłacze i wskazania źródeł. Identyfikacja konceptu w OKF
wynika ze ścieżki względem korzenia bundle'a.

Indeksy nawigacyjne z powyższej listy zawierają odsyłacze i krótkie opisy,
nie zastępują dokumentów wiedzy. Główny indeks bundle'a wymaga frontmattera
`okf_version: "0.2"`; indeksy warstw nie wymagają metadanych dokumentu.
`knowledge/log.md` ma wpisy pod datami YYYY-MM-DD,
najnowsze na górze, bez frontmatteru. Log dokumentuje zmiany; nie zastępuje
źródeł ani decyzji użytkownika.

## Kontrola struktury

`.venv/bin/python -B scripts/validate_hub.py` sprawdza hub zawierający skrypt,
nie bieżący katalog wywołania. Python 3.10+, tylko biblioteka standardowa,
bez sieci i bez zapisu. To walidator lokalnego profilu 0.2.0, nie całego OKF.
Skrypty uruchamiamy wyłącznie w lokalnym środowisku wirtualnym. Jeśli `.venv`
nie istnieje, agent tworzy je wcześniej przez `python3 -m venv .venv`
w katalogu huba. Na Windows interpreter jest w `.venv/Scripts/python.exe`.
Bez instalacji systemowych; ewentualne paczki wyłącznie przez interpreter
venv z `-m pip`. Walidator nie tworzy środowiska ani niczego nie instaluje.

Sprawdza:

- wymagane pliki szkieletu, konfigurację hub.json i wszystkie `.md` w knowledge;
- frontmatter dokumentów (poza zamkniętą listą wyjątków powyżej): type, title, description,
  status, generated; typ należy do concept_types, status do draft/stable/deprecated;
- generated.by jest niepustym tekstem, generated.at to data i czas ISO 8601
  z `T` i strefą (np. `2026-09-23T12:00:00Z` lub `2026-09-23T14:00:00+02:00`);
- niepuste sources w dokumentach silver i gold, unikalne id, istniejące pliki
  wskazane przez resource; id składa się z liter ASCII, cyfr, `_` i `-`;
- użyte przypisy mają definicję oraz sources[].id; nieużyte id dają ostrzeżenie;
- względne odsyłacze Markdown prowadzą do istniejących plików;
- główny knowledge/index.md deklaruje okf_version: "0.2";
- knowledge/log.md nie ma frontmattera; wpisy są pod nagłówkami `## YYYY-MM-DD`,
  z poprawnymi, niepowtarzającymi się datami od najnowszej do najstarszej.
  Pusty log może zawierać tylko nagłówek H1 i puste linie.

Wyjście stdout jest jednym obiektem JSON: violations (liczba błędów), errors
i warnings (listy obiektów file, line, message). Stderr zawiera czytelne
linie `plik:linia: error/warning: komunikat`. Kod 0 występuje tylko przy
violations == 0. Ostrzeżenia nie zwiększają violations. W hub.json:

```json
"quality": {
  "validator": "scripts/validate_hub.py",
  "metric": "violations",
  "threshold": 0,
  "max_fix_iterations": 5
}
```

Agent wykonuje pierwszą kontrolę, potem najwyżej 5 cykli naprawa/kontrola.
Po wyczerpaniu limitu albo przy podejrzeniu błędu sprawdzania zatrzymuje się
i przedstawia wynik użytkownikowi. Nie naprawia plików spoza zleconego zakresu.
Nie modyfikuje walidatora, progu, budżetu ani reguł kontraktu w celu uzyskania
zielonego. Zmiana kontroli wymaga osobnego zlecenia, brancha i PR bez auto-merge.
Nie wolno usuwać treści/źródeł ani fałszować metadanych tylko dla wyniku.

Jak w zasadach jakości poniżej, zielone nie potwierdza prawdziwości treści.
Pliki i ustawienia są edytowalne: ta reguła nie jest zabezpieczeniem systemowym
przed autorem mogącym zmienić kod walidatora. Ochronę zmian kontraktu zapewnia
osobny proces przeglądu; walidator nie dowodzi kompletności lub autentyczności.

### Obsługiwany podzbiór frontmattera

Frontmatter zaczyna się w pierwszej linii `---` i kończy osobną linią `---`.
Na górze jest mapa. Klucze ASCII: litery lub `_`, dalej także cyfry i `-`.
Duplikaty kluczy są błędem, także w mapach inline. Wcięcia: wielokrotności
dwóch spacji, każdy poziom dokładnie dwa; bez tabulatorów. Maksymalnie
10 poziomów wcięcia. Puste linie są dozwolone.

- Wartości tekstowe: pojedyncza linia niecytowanego tekstu, string JSON
  w podwójnych cudzysłowach albo string w pojedynczych cudzysłowach
  (apostrof wewnątrz jako `''`). `: ` i ` #` wymagają cytowania.
- Mapy blokowe `key:` z polami o poziom głębiej i listy `- wartość`
  lub `- key: wartość` z kolejnymi polami na następnym poziomie.
- Kolekcje inline wyłącznie w składni JSON, np. `["tag-a", "tag-b"]`
  oraz `{"by": "human:editor", "at": "2026-09-23T12:00:00Z"}`.
  W JSON dopuszczone są też liczby skończone, bool i null, ale wymagane
  tekstowe pola dokumentu nadal muszą być niepustymi stringami.
- Niecytowane liczby i słowa YAML takie jak true/null/yes/no nie są tekstem
  profilu; użyj cudzysłowów. Daty ISO można zapisać jako tekst bez cudzysłowów.
- Komentarze YAML, anchory/aliasy, merge keys, tagi YAML, bloki `|`/`>`,
  wieloliniowe scalars i nie-JSON-owe kolekcje inline są nieobsługiwane.
  Parser zgłasza naruszenie, nigdy nie ignoruje takiej konstrukcji.

Przykładowy blok (przy zapisie zastąp autora i czas rzeczywistymi):

```yaml
generated:
  by: human:editor
  at: 2026-09-23T12:00:00Z
sources:
  - id: material-a
    resource: ../00-bronze/material-a-v1.md
    title: Materiał wejściowy A
```

### Zakres odsyłaczy i źródeł

Resource musi wskazywać lokalny plik w obrębie huba, względnie do dokumentu.
URL pochodzenia zapisuj osobno, np. origin_url w notatce bronze. Sam URL
w sources.resource nie wystarcza do tej lokalnej kontroli. Surowy tekst można zachować jako
`.txt` i opisać notatką bronze z metadanymi; nie zmieniaj historycznego źródła
tylko po to, aby spełnić nowe reguły.

Huby pozostają niezależne: nie ma katalogu imports, pakietów wiedzy ani
synchronizacji między hubami. Gdy użytkownik wskaże dodatkowy hub jako
materiał do zadania, można go czytać bez kopiowania jego wiedzy. Wynik
zapisuj wyłącznie we wskazanym hubie docelowym. Pomocniczy ślad zapisz
zwykłym tekstem w treści, np. „Kontekst dodatkowy: hub sprzedażowy,
dokument SPIN, odczyt 2026-09-23”; wersję dopisz, jeśli jest znana.
Nie wymaga to pola YAML ani odsyłacza Markdown między repozytoriami.
Ten opis nie jest sprawdzany przez walidator i nie zastępuje wymaganych
lokalnych sources ani przypisów. Nie dopisuj pozornych lokalnych źródeł:
jeśli opracowanie opiera się wyłącznie na innym hubie, zgłoś ograniczenie
obecnego kontraktu zamiast deklarować poprawną lokalną atrybucję.

Linki inline (także obrazy), odsyłacze referencyjne `[opis][id]`, `[id][]`
i `[id]` z definicją `[id]: ścieżka` są sprawdzane. Definicja odsyłacza mieści
się w jednej linii; tytuł opcjonalny w cudzysłowach lub nawiasach. Ścieżki
ze spacjami zapisuj w `<...>` lub z kodowaniem URL. Obsługiwane są zagnieżdżone
nawiasy w etykietach i ścieżkach oraz backslash escapes. Przypisy mają postać
`[^id]` i osobną definicję `[^id]: ...`; definicja sama nie liczy się jako użycie.

Fragmenty `#naglowek` i query nie są walidowane, sprawdzany jest plik.
Linki HTTP/HTTPS/mailto nie są odwiedzane. Ścieżki absolutne, ucieczka poza hub,
symlinki w knowledge i celach odsyłaczy oraz wikilinki/HTML a/img są błędami.
Przykłady w blokach kodu fenced (backticks lub tyldy, na głównym poziomie)
i inline code nie są odsyłaczami; niedomknięty fence jest błędem. Indented code
nie jest wyłączany ze sprawdzania — dla dosłownych przykładów używaj fenced code.
To udokumentowany profil Markdown, nie pełny parser CommonMark.

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

To dwa niezależne działania. Łącz je tylko wtedy, gdy użytkownik zamawia oba.
W każdym dobieraj kontekst przez indeksy, powiązane koncepty i wcześniejsze
decyzje użytkownika; nie ładuj całej biblioteki bez potrzeby.

### Dodaj materiał do bazy — bronze i silver

1. Przyjmij źródło w nowym pliku bronze. Sprawdź dostępne wejścia, żeby
   uniknąć duplikatu. Automatyczny rejestr hashy jest planowany, nie zainstalowany.
2. Rozwiń połączoną wiki silver: pojęcia, metody, przykłady i syntezy z referencjami
   do źródeł. Łącz nowe informacje z istniejącymi, zachowując warunki stosowania,
   wyjątki i rozbieżności. To wiedza wielokrotnego użycia, nie tylko osobne
   streszczenie każdego wejścia ani skrót pod jeden przyszły wynik.
3. Nie wymagaj celu biznesowego i nie twórz gold. Jeśli nowa wiedza wpływa
   na istniejące gold, wskaż to i zaproponuj aktualizację; nie wdrażaj jej
   automatycznie bez zlecenia.

### Przygotuj materiał do konkretnego celu — gold

1. Ustal rezultat, temat i potrzebną formę z polecenia. Korzystaj z istniejącego
   silver; nie wymagaj dodania nowego materiału źródłowego.
2. Utwórz katalog w `20-gold`, np. `ebook-o-xyz`, `fiszki-xyz` lub
   `instagram-posts-materials`, i przygotuj zamówione opracowanie.
   Zachowaj referencje do silver oraz ścieżkę pochodzenia do źródeł w bronze.
3. Po brakujące szczegóły i dokładne cytaty sięgnij do odpowiednich źródeł
   bronze. Nie analizuj od nowa wszystkich surowych danych. Jeśli baza nie
   wystarcza, wskaż braki; nie zastępuj ich zmyślonymi faktami lub przypisami.
4. Przy zmianie koncepcji twórz nowy katalog gold, zachowując poprzedni wynik.
   Aktualizuj istniejący, gdy użytkownik prosi o jego korektę lub aktualizację.
   Nie twórz katalogów na zapas; nie narzucaj modelu PARA.

Po każdym działaniu sprawdź odsyłacze i przypisy, uzupełnij odpowiednie indeksy
i log. Przedstaw zmiany i kwestie otwarte. Sprawdzenie struktury nie dowodzi
prawdziwości treści. Otrzymane korekty i decyzje zapisuj w `90-decisions`,
żeby kolejne przebiegi je uwzględniały.

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

Trzy osobne zakresy: redakcja wiki, publikacja opracowań oraz działania
operacyjne. `hub.json` opisuje początkową politykę: agent przygotowuje lokalne
wersje robocze, publikacja wymaga przyjęcia, działania zewnętrzne są wyłączone.
To instrukcja pracy, a nie techniczna kontrola uprawnień.

Nie włączaj do huba danych innego właściciela bez zadania, które je obejmuje.
Nie kopiuj sekretów do wiedzy. Odczyt innego huba nie oznacza zgody na jego
zmianę ani przeniesienie jego zawartości do huba docelowego.
Zmiana wiedzy nie daje uprawnienia do zmiany budżetu ani konfiguracji firmy.
