# Bieżąca kopia Git w hubach

Reguła jest dostarczana w AGENTS.md nowych hubów: zlecona redakcja obejmuje
commit i push do uzgodnionego repozytorium po sprawdzonym zadaniu oraz
spójnych etapach dłuższej pracy. Agent potwierdza commit w remote. Brak Git,
celu, dostępu, zielonej walidacji albo udanego push nie może być ukryty pod
raportem „gotowe”. Wyraźne polecenie pracy wyłącznie lokalnej ma pierwszeństwo.

Generator pozostaje offline i nie zakłada repozytoriów. Przy pierwszej
konfiguracji użytkownik wskazuje cel oraz dopuszczony dostęp do danych;
agent nie tworzy ani nie upublicznia repo bez zgody. W hubie osadzonym
w projekcie używa Git projektu, bez obejmowania cudzych zmian i commitów.

## Przyjęcie w istniejącym hubie

To aktualizacja instrukcji, nie zmiana formatu danych, hub.json ani
walidatora profilu 0.2.0. Silnik nie zna istniejących hubów i nie aktualizuje
ich automatycznie. Po wskazaniu konkretnego huba i zleceniu aktualizacji:

1. Sprawdź jego kontrakt, stan Git, adres push, gałąź i uzgodniony dostęp.
   Zachowaj lokalne zmiany; nie uruchamiaj generatora na istniejącym katalogu.
2. Na osobnym branchu przenieś sekcję „Bieżąca kopia zdalna” z szablonu
   AGENTS.md i odpowiednią regułę z „Autonomia i własność” w SCHEMA.md.
   Uzgodnij kolizje z lokalną polityką; nie nadpisuj całych plików.
3. Uzupełnij README huba o zasady i ograniczenia kopii. Gdy używany jest
   osobno zainstalowany curate-knowledge-hub, aktualizuj go tylko na zlecenie.
4. Wykonaj lokalne kontrole, commit i push do uzgodnionego repozytorium;
   potwierdź obecność commita na remote i otwórz PR bez auto-merge.

Sam merge w master-hub nie zabezpiecza żadnego istniejącego huba.

## Granice kopii

Nie ma harmonogramu ani procesu w tle. Kopia Git obejmuje tylko wypchnięte
pliki wersjonowane. Zewnętrzne nagrania, materiały pod linkami, pliki
ignorowane i jeszcze niewypchnięta praca wymagają osobnego backupu.
Historia w remote nie jest niezależną kopią odporną na usunięcie repozytorium.
Zielony walidator dowodzi struktury, nie istnienia zdalnej kopii;
testy generatora nie dowodzą, że agent rzeczywiście wykonał push.
