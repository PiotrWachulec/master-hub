# Plan na teraz

## 1. Użyj istniejącego huba

Otwórz osobne repozytorium `personal-hub`, obok `master-hub`.
Podaj jeden materiał tekstowy i rezultat, którego potrzebujesz. Agent
przetworzy go tam: zachowa źródło w bronze, opracuje silver
i przygotuje produkt gold. Nie trzeba uruchamiać generatora.

Przykład: notatki o badaniu klientów → checklista przygotowania rozmowy.
[Prompt do pierwszego użycia](first-run.md).

## 2. Oceń wynik i popraw go przez rozmowę

Przeczytaj wynik w Obsidianie albo edytorze. Powiedz agentowi, co poprawić.
Agent zapisze korekty i powody zmian, żeby nie zginęły przed kolejną sesją.
Kończymy, kiedy materiał faktycznie pomaga Ci wykonać zadanie.

## 3. Powtórz z kolejnym materiałem

Sprawdź, czy nowa wiedza uzupełnia istniejącą. Dopiero wtedy wybierzmy
najbardziej uciążliwy krok i go zautomatyzujmy.

## Później — tylko gdy pojawi się potrzeba

| Zaobserwowana potrzeba | Możliwe rozszerzenie |
|---|---|
| Często ręcznie dostarczasz transkrypcje | Automatyczny dopływ tekstu |
| Powstają duplikaty lub psują się odsyłacze | Rejestr wejść i walidator |
| Inna firma/projekt potrzebuje niezależnej wiedzy | Osobny hub poza tym repozytorium |
| Kilka hubów korzysta z tych samych metod | Wersjonowane pakiety i propozycje aktualizacji |
| Sprawdzona procedura ma korzystać z bieżących danych | Agent operacyjny, początkowo proponujący działania |

Generator, kontrakt i pusty hub już istnieją. Automatyczne przetwarzanie,
migracje OKF i synchronizacja nie są zaimplementowane. Szczegółowa
[architektura](architecture.md) pozostaje punktem odniesienia na przyszłość.
