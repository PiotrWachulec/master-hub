# Plan na teraz

## 1. Dodaj pierwszy materiał do istniejącego huba

Otwórz osobne repozytorium `personal-hub`, obok `master-hub`.
Podaj jeden materiał tekstowy. Agent zachowa źródło w bronze i rozwinie
wiki silver. Nie musisz określać celu biznesowego ani tworzyć gold.

[Przykładowe polecenia](first-run.md). Generator nie jest potrzebny.

## 2. Rozwijaj i koryguj wiedzę przez rozmowę

Przeczytaj opracowanie w Obsidianie albo edytorze. Powiedz agentowi, co poprawić.
Agent zapisze korekty i powody zmian, żeby nie zginęły przed kolejną sesją.
Dodawaj kolejne materiały, gdy ich potrzebujesz — powinny uzupełniać
i łączyć istniejącą wiedzę, a nie tworzyć zbiór niezależnych streszczeń.

## 3. Gdy pojawi się potrzeba, zamów gold

Poproś o wkład do ebooka, materiał do fiszek albo instrukcje dla automatu.
Agent wykorzysta istniejące silver i utworzy katalog gold pod zamówiony wynik,
z referencjami do źródeł. Nie musisz dostarczać kolejnego materiału ani czekać
na rozbudowanie całej bazy. Nowa koncepcja może dostać osobny katalog gold.

Dopiero rzeczywista praca pokaże, który uciążliwy krok warto zautomatyzować.

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
