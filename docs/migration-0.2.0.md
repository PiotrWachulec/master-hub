# Ręczna migracja lokalnego profilu 0.1.1 → 0.2.0

Procedura na przyszłość, nie bieżące zadanie ani raport z wykonanej migracji.
Silnik nie zakłada, że istnieją już jakiekolwiek huby. Poniższe kroki stosuje się wyłącznie wtedy,
gdy użytkownik w przyszłości wskaże starszy hub i zleci jego aktualizację.

To historyczna procedura dla 0.2.0: użyj szablonów i walidatora z commita
`1acb58b29bb5058178660a3a374bfc6f47824517`, nie z bieżącego main.
Generator tworzy obecnie profil 0.2.2; jego przyjęcie wymaga dodatkowo
[jawnej aktualizacji konfiguracji kopii Git](hub-git-backup.md) (0.2.0 → 0.2.1)
oraz [uziemienia faktów i Query/Archive](migration-0.2.2.md) (0.2.1 → 0.2.2).

OKF pozostaje w wersji 0.2. Zmiana dotyczy lokalnego kontraktu:
samodzielnego walidatora struktury, udokumentowanego podzbioru frontmattera
i ograniczonej pętli naprawy. To nie automatyczna aktualizacja istniejących
hubów. Silnik nie zna ich lokalizacji ani stanu.

## Zakres i zgoda

Użytkownik wskazuje hub i zleca migrację. Przeczytaj jego kontrakt, sprawdź
lokalne zmiany i stan Git. Zachowaj poprzednią wersję w historii/backupie.
Pracuj na osobnym branchu; przy niepowiązanych zmianach użyj uzgodnionego
worktree albo zatrzymaj się. Nie uruchamiaj generatora na istniejącym katalogu.

## Procedura

1. Skopiuj `skills/create-knowledge-hub/assets/hub/scripts/validate_hub.py`
   do `scripts/validate_hub.py` w docelowym hubie. Zachowaj lokalne skrypty;
   kolizja istniejącej ścieżki wymaga przeglądu, nie nadpisania w ciemno.
2. Zastosuj sekcję „Kontrola struktury” nowego szablonu SCHEMA.md i reguły
   pętli z szablonu AGENTS.md, zachowując domenowe decyzje oraz politykę huba.
   Instrukcje i kontrola muszą być spójne; nie wymieniaj całego kontraktu.
3. W hub.json zachowaj tożsamość, concept_types, policy i dodatkowe pola.
   Zmień profile_version na `0.2.0` i dodaj:

   ```json
   "quality": {
     "validator": "scripts/validate_hub.py",
     "metric": "violations",
     "threshold": 0,
     "max_fix_iterations": 5
   }
   ```

4. Przygotuj lokalne `.venv` huba, jeśli go nie ma (`python3 -m venv .venv`,
   Python 3.10+). Zachowaj istniejące środowisko, nie instaluj paczek globalnie.
   Uzupełnij lokalny .gitignore o `.venv/`, nie nadpisując innych reguł.
   Uruchom `.venv/bin/python -B scripts/validate_hub.py` w migrowanym hubie
   (Windows: `.venv/Scripts/python.exe`). Zachowaj
   raport przed naprawami. Nowy walidator może ujawnić starsze niezgodności.
5. Przejrzyj i popraw wyłącznie uzgodniony zakres struktury. Typowe zmiany:
   - inline YAML → blokowe mapy/listy albo JSON flow; cytowanie tagów;
   - daty generated.at ze strefą, ale tylko gdy rzeczywisty czas jest znany;
   - brakujące źródła i definicje przypisów, bez wymyślania atrybucji;
   - lokalne, względne ścieżki do plików zamiast URL w sources.resource;
   - datowane, malejąco uporządkowane wpisy log.md; pusty log bez starego
     akapitu instruktażowego (wzór nowego logu zawiera tylko nagłówek).
6. Ponownie sprawdź cały hub. Reguła limitu 5 cykli obowiązuje również tutaj;
   jeśli zakres jest większy, przedstaw pozostałe naruszenia i uzgodnij
   następny etap, zamiast obniżać próg lub ogłaszać migrację ukończoną.
7. Przejrzyj diff: treści, źródła, statusy i historia pochodzenia muszą być
   zachowane. Zaktualizuj informację o profilu w README huba. Oddaj branch
   jako PR z raportem walidatora i zakresem zmian. Nie merguj samodzielnie.

## Przypadki wymagające zatrzymania

- Źródła bronze są przyjętymi, niemutowalnymi wersjami. Nowy profil nie daje
  zgody na ich zmianę; nie „naprawiaj” ich automatycznie. Przedstaw użytkownikowi
  naruszenia i propozycję jawnej migracji reprezentacji z zachowaniem oryginału
  (np. oryginalny tekst i osobna notatka metadanych). Bez zgody migracja stoi.
- Nie wolno fabrykować generated.at, udawać pełnego źródła na podstawie
  streszczenia ani kopiować zewnętrznych materiałów bez uprawnień.
- Hub o innym bundle_root lub formacie potrzebuje osobno zaprojektowanej
  migracji. Ten walidator oczekuje knowledge/ i lokalnego profilu 0.2.0.
- Podejrzenie błędu walidatora: zatrzymaj pętlę i zgłoś przykład do użytkownika.
  Zmiana walidatora/progu jest osobnym zadaniem kontraktowym, nie naprawą danych.

## Granice dowodu

Zielony wynik potwierdza tylko opisane reguły strukturalne. Brak sieci oznacza,
że skrypt nie sprawdza dostępności URL-i; nie sprawdza też prawdziwości,
kompletności, autentyczności ani znaczenia powiązań. Walidator i pliki
kontraktu są edytowalne, więc nie są samodzielnym zabezpieczeniem przed
złośliwą zmianą kontroli. Przegląd PR pozostaje granicą przyjęcia kontraktu.
