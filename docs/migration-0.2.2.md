# Uziemienie faktów, triage i Query/Archive w hubach — 0.2.1 → 0.2.2

Profil 0.2.2 dodaje cztery rzeczy do kontraktu lokalnego: nieblokujący raport
uziemienia faktów `scripts/check_evidence.py` (`hub.json` → `quality.evidence_script`),
ostrzeżenie `scripts/validate_hub.py` o plikach bronze nieodwołanych przez żadne
`sources[].resource`, formalny tryb Query/Archive oraz konwencję dyspozycji
triage przy dodawaniu materiału i bloku `Status: Disputed/Outdated` przy
pojedynczym twierdzeniu. Format OKF 0.2 i struktura bronze/silver/gold/decisions
pozostają bez zmian. Skrypt i rozstrzygnięcie o ziarnistości kontroli (cały
dokument, nie pojedynczy przypis) są adaptacją `scripts/check_evidence.py`
z [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki)
(MIT) — niezależnej implementacji tego samego pomysłu Karpathy'ego.

Silnik nie zna istniejących hubów i nie aktualizuje ich automatycznie. Samo
to repozytorium, jego PR-y ani merge nie zabezpieczają żadnego istniejącego
huba. Procedura poniżej jest jawnym, osobnym zadaniem na wskazanym hubie.

## Przyjęcie w istniejącym hubie — 0.2.1 → 0.2.2

1. Sprawdź jego kontrakt, stan Git, adres push, gałąź i uzgodniony dostęp.
   Zachowaj lokalne zmiany; nie uruchamiaj generatora na istniejącym katalogu.
2. Na osobnym branchu skopiuj `scripts/check_evidence.py` z
   `skills/create-knowledge-hub/assets/hub/scripts/check_evidence.py` w tym
   repozytorium do `scripts/check_evidence.py` huba. Przejrzyj lokalne
   modyfikacje `scripts/validate_hub.py`, jeśli jakieś istnieją — nie
   nadpisuj ich w ciemno; nowy walidator dodaje tylko wymóg
   `quality.evidence_script` i ostrzeżenie o osieroconych źródłach bronze,
   nie zmienia reszty kontroli.
3. W `hub.json` ustaw `profile_version` na `0.2.2` i dodaj do istniejącej
   mapy `quality` pole `"evidence_script": "scripts/check_evidence.py"`,
   zachowując pozostałe pola (`validator`, `metric`, `threshold`,
   `max_fix_iterations`).
4. Przenieś z szablonu `SCHEMA.md` (sekcja „Uziemienie faktów (Grounding
   Invariant)”, konwencja „Bez materiału” w logu, dyspozycje triage i krok
   kaskadowy w „Dodaj materiał do bazy”, blok `Status:` w „Jakość treści”,
   podsekcja „Odpowiedz na pytanie o bazę — Query” w „Praca agenta”) i
   odpowiadający fragment `AGENTS.md` („Bieżąca kopia zdalna” zostaje bez
   zmian; dopisz trzecie zadanie i krok `check_evidence.py` z „Obowiązkowa
   kontrola po redakcji”). Uzgodnij kolizje z lokalną polityką huba; nie
   nadpisuj całych plików.
5. Istniejące pliki bronze bez wcześniejszego odwołania przez
   `sources[].resource` nie są błędem wstecznym — po migracji
   `validate_hub.py` zacznie je zgłaszać jako ostrzeżenie. Przejrzyj je:
   dopisz odwołanie, jeśli materiał już jest w silver/gold, albo zaloguj
   „Bez materiału” zgodnie z nową konwencją (zob. SCHEMA.md), jeśli celowo
   nie weszły do wiki.
6. Wykonaj lokalne kontrole interpreterem `.venv` (`validate_hub.py` i
   `check_evidence.py`), commit i push do uzgodnionego repozytorium;
   potwierdź obecność commita na remote i otwórz PR bez auto-merge.

## Granice

`check_evidence.py` jest raportem, nie bramką: jego wynik nigdy nie wchodzi
do `violations` ani progu `quality.threshold`, nawet po migracji. Ostrzeżenie
o osieroconych źródłach bronze nie blokuje zielonego wyniku `validate_hub.py`
(próg 0 dotyczy wyłącznie błędów, nie ostrzeżeń) — to sygnał do przeglądu,
nie powód do zatrzymania pracy. Migracja nie wymaga ponownego przetworzenia
istniejącej treści silver/gold ani uzupełniania przypisów wstecz; dotyczy
wyłącznie kontraktu, narzędzi i nowej pracy od tego momentu.
