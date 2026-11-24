# Covering-Array-Pilotprojekt (`Math_Gemini_Antigravity`)

## Problemdefinition

Ein **Covering Array** $\mathrm{CA}(N; t, k, v)$ ist eine $N \times k$-Matrix über dem Alphabet $\{0, 1, \dots, v - 1\}$, sodass für jede Wahl von $t$ Spalten ($C \subseteq \{0, \dots, k-1\}$, $|C| = t$) jedes der $v^t$ möglichen $t$-Tupel mindestens einmal als Zeile in der Projektion auf $C$ vorkommt. Insgesamt müssen also $\binom{k}{t} \cdot v^t$ Interaktionen abgedeckt sein.

Die **Covering Array Number** $\mathrm{CAN}(t, k, v)$ ist das kleinste $N$, für das ein $\mathrm{CA}(N; t, k, v)$ existiert. Ziel dieses Pilotprojekts ist es, für ausgewählte offene Zielzellen kleinere (oder strukturell neue) verifizierte Covering Arrays zu finden, wobei jeder Kandidat unabhängig doppelt verifiziert wird (siehe [`RULES.md`](RULES.md)).

## Zielzellen & aktueller Live-Stand

Stand geprüft am **2026-11-24** gegen:
- **Primärquelle (Live-Tabelle):** [`chrispbsmolen/ca-tools`](https://github.com/chrispbsmolen/ca-tools) (`table/ca_table.csv`, Commit `47596cf`, 2026-11-24)
- **Gegenprüfung ungemergter Bestwerte:** [`dzoba/covering-arrays-2026`](https://github.com/dzoba/covering-arrays-2026) (Commit `040a622`, 2026-10-21; Details in [`docs/phase1_dzoba_audit.md`](docs/phase1_dzoba_audit.md))

| Zielzelle `(t, k, v)` | Live-Stand `ca_table.csv` | Status in `ca_table.csv` | Stand `dzoba/covering-arrays-2026` | Ziel für Suche |
| --- | :---: | --- | --- | :---: |
| **`(4, 9, 3)`** | **135** | `VERIFIED` (2026-11-16, Smolen, aus `CA(405;5,10,3)`) & `CITED` (S1) | Nicht verbessert (`k=9` bleibt 135; Nachbar `k=8` ungemergt **129**) | $N \le 134$ |
| **`(3, 9, 5)`** | **185** | `VERIFIED` (2026-11-12, Smolen, via `k=10`) & `CITED` (S1) | Nicht verbessert (`k=9,10` bleibt 185; Nachbar `k=8` ungemergt **165**) | $N \le 184$ |
| **`(3, 9, 6)`** | **361** | `VERIFIED` (2026-11-12, Smolen, SA-Spaltenerweiterung) & `CITED` (S1) | Kein Eintrag (`v=6` nicht im Repo) | $N \le 360$ |

Weitere geprüfte Referenzzellen:
- `(4, 12, 3)`: Live-Stand **189** (`CITED` S1, Torres-Jimenez); kein Eintrag in `dzoba/covering-arrays-2026`.
- `(3, 11, 5)`: Live-Stand `ca_table.csv` **225** (via `k=12`), **aber ungemergter Bestwert `N = 218`** in `dzoba/covering-arrays-2026` (`arrays/CA_218_3_11_5.txt`).

## Repository-Struktur

- `verifiers/` — Dual-Verifier-Suite (**nach Phase 1 READ-ONLY**, siehe `RULES.md`):
  - `ca_verify.c` — offizieller C-Verifier aus `chrispbsmolen/ca-tools` (MIT; Binary `verifiers/ca_verify` wird lokal kompiliert)
  - `verify_independent.py` — vollständig unabhängiger Pure-Python-Stdlib-Verifier
  - `test_verifiers.py` — automatische Testsuite (gültige Baselines + 4 Defektklassen)
  - `SHA256SUMS` — SHA-256-Prüfsummen der Verifier-Quelldateien
- `baselines/` — verifizierte Referenz-Arrays für Tests und als Such-Ausgangspunkt (siehe `baselines/README.md`)
- `solvers/` — Such-Solver (ab Phase 2, ausschließlich auf Feature-Branches)
- `results/` — verifizierte Kandidaten inkl. SHA-256-Hashes und Verifikations-Logs
- `docs/` — Audits, Notizen und Analysen
- `RULES.md` — verbindliche Governance-, Verifikations- und Checkpointing-Regeln

## Reproduktionsbefehle

```bash
# 1. Integrität der Verifier-Quellen prüfen
sha256sum -c verifiers/SHA256SUMS

# 2. Offiziellen C-Verifier lokal kompilieren
gcc -O3 -pthread -Wall -o verifiers/ca_verify verifiers/ca_verify.c

# 3. Automatische Dual-Verifier-Testsuite ausführen
python3 verifiers/test_verifiers.py

# 4. Einzelnes Array mit BEIDEN Verifiern prüfen (Beispiel: Baseline CA(135; 4, 9, 3))
./verifiers/ca_verify baselines/CA_135_4_9_3.txt 4 3
python3 verifiers/verify_independent.py baselines/CA_135_4_9_3.txt 4 3 -n 135 -k 9

# 5. SHA-256-Prüfsummen der Baselines überprüfen
sha256sum baselines/CA_*.txt
```