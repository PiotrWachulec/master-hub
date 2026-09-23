# Bieżąca kopia Git w hubach

Profil 0.2.1 deklaruje w hub.json
`policy.remote_copy: "required_after_validated_task"`; AGENTS.md opisuje
wykonanie tej reguły. Zlecona redakcja obejmuje
commit i push do uzgodnionego repozytorium po sprawdzonym zadaniu oraz
spójnych etapach dłuższej pracy. Agent potwierdza commit w remote. Brak Git,
celu, dostępu, zielonej walidacji albo udanego push nie może być ukryty pod
raportem „gotowe”. Wyraźne polecenie pracy wyłącznie lokalnej ma pierwszeństwo.

Generator pozostaje offline i nie zakłada repozytoriów. Przy pierwszej
konfiguracji użytkownik wskazuje cel oraz dopuszczony dostęp do danych;
agent nie tworzy ani nie upublicznia repo bez zgody. W hubie osadzonym
w projekcie używa Git projektu, bez obejmowania cudzych zmian i commitów.

## Przyjęcie w istniejącym hubie — 0.2.0 → 0.2.1

To zmiana lokalnego kontraktu, konfiguracji i walidatora. Format OKF 0.2
pozostaje bez zmian. Silnik nie zna istniejących hubów i nie aktualizuje
ich automatycznie. Samo pole ani notatka agenta nie tworzą zgody użytkownika
na konkretny remote. Po wskazaniu huba i zleceniu aktualizacji:

1. Sprawdź jego kontrakt, stan Git, adres push, gałąź i uzgodniony dostęp.
   Zachowaj lokalne zmiany; nie uruchamiaj generatora na istniejącym katalogu.
2. Na osobnym branchu przenieś sekcję „Bieżąca kopia zdalna” z szablonu
   AGENTS.md i odpowiednią regułę z „Autonomia i własność” w SCHEMA.md.
   W SCHEMA.md uaktualnij też wersję profilu i „Kontrolę struktury” o
   wymagane pole remote_copy; wszystkie instrukcje muszą opisywać 0.2.1.
   Uzgodnij kolizje z lokalną polityką; nie nadpisuj całych plików.
3. W hub.json ustaw profile_version na `0.2.1` i dodaj do istniejącej mapy
   policy `"remote_copy": "required_after_validated_task"`, zachowując
   pozostałe pola. Wraz z tym przyjmij walidator 0.2.1 z szablonu; przejrzyj
   lokalne modyfikacje, nie nadpisuj ich w ciemno. Nowy walidator wymaga
   obu deklaracji. Nie kopiuj go do huba 0.2.0 bez uzgodnionej migracji.
4. Uzupełnij README huba o wersję, zasady i ograniczenia kopii. Gdy używany jest
   osobno zainstalowany curate-knowledge-hub, aktualizuj go tylko na zlecenie.
5. Wykonaj lokalne kontrole interpreterem `.venv`, commit i push do
   uzgodnionego repozytorium;
   potwierdź obecność commita na remote i otwórz PR bez auto-merge.

Sam merge w master-hub nie zabezpiecza żadnego istniejącego huba.
Brak pola w starszym hubie nie uruchamia nowej reguły. Brak albo inna wartość
w hubie deklarującym 0.2.1 jest błędem konfiguracji, nie domyślną zgodą.

## Granice kopii

Nie ma harmonogramu ani procesu w tle. Kopia Git obejmuje tylko wypchnięte
pliki wersjonowane. Zewnętrzne nagrania, materiały pod linkami, pliki
ignorowane i jeszcze niewypchnięta praca wymagają osobnego backupu.
Historia w remote nie jest niezależną kopią odporną na usunięcie repozytorium.
Zielony walidator dowodzi struktury, nie istnienia zdalnej kopii;
testy generatora nie dowodzą, że agent rzeczywiście wykonał push.
