# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-24 (Abschluss Phase 3A auf Branch `exp/ca-3-k-6`).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md).

## 1. Live-Stand `CA(N; 3, k, 6)` (`k = 7..14`)

Abgerufen via `gh api` aus `chrispbsmolen/ca-tools` (`table/ca_table.csv`, 2026-11-24; true min über `k' >= k`):

| Zelle `(3, k, 6)` | Live-Min `N` | `tier` | Konstruktion / Herkunft |
| :---: | :---: | :---: | --- |
| `(3, 7, 6)` | **290** | `CITED` | Torres Jimenez |
| `(3, 8, 6)` | **301** | `CITED` | Torres Jimenez |
| `(3, 9, 6)` | **361** | `CITED` | Torres Jimenez (`baselines/CA_361_3_9_6.txt`) |
| `(3, 10, 6)` | **366** | `VERIFIED` | Iterative row deletion + Nurmela-Tabu aus 396-row `PSL(2,5)` (`A=4, B=5, const=6`) |
| `(3, 11, 6)` | **411** | `VERIFIED` | Row deletion + conflict-tabu/BE-PAWS aus `418` (aus 426-row `PSL(2,5)`) |
| `(3, 12, 6)` | **456** | `VERIFIED` | Reines `PSL(2,5)` (`A=5, B=5, const=6` = 456 Zeilen) |
| `(3, 13, 6)` | **490** | `CITED` | Torres Jimenez |
| `(3, 14, 6)` | **498** | `CITED` | Chateauneuf-Kreher doubling postop NCK |

## 2. Ziel-Landkarte & Track-Status

| Track / Zelle | Live-Rekord | Status | Kurzfazit |
| --- | :---: | --- | --- |
| `(3, 9, 5)` | **185** | **Abgeschlossen (Gate 1 ABORT)** | Einzelzell-Tabu/SA auf `exp/ca-3-9-5` (`3ca3058`) sauber beendet (`G0-K1` PASS 5,39s; `2D`: 24/60 orb, 93 unc) |
| **`(3, 13, 6)` (heißester Treffer-Kandidat)** | **490** | **Aktiv (`exp/ca-3-k-6`)** | **`psl25 (A=5, B=6) @ 486` erreichte `3` Orbits in `1,3 s`**; `A=5, B=5 @ 456` erreichte `5` Orbits in `7,1 s`! |
| `(3, 9, 6)` | **361** | **Aktiv (`exp/ca-3-k-6`)** | `N=336` (`pgl25 A=2,B=3`: 40 orb; `psl25 A=4,B=3`: 19 orb) zu knapp an `B=3`; Weg zu `<= 360`: `psl25 A=4,B=4 @ 366` + Row-Deletion |
| `(3, 11, 6)` | **411** | Beobachtung | `psl25 A=4, B=5 @ 396` erreichte `16` `D1/D2`-Orbits (0 2-sym offen) |
| `(4, 9, 3)` | **135** | Wartend | Benötigt `t=4`-Solver (`AGL(1,3)`-Orbits) |

## 3. Gate-Status (`exp/ca-3-k-6`, Phase 3A)

- **Sanity-Checks (10.000 Züge):** `PGL25` (`120*D + 30*2sym`) und `PSL25` (`60*(D1+D2) + 30*2sym`) je **0 Abweichungen** + exakte gewichtete Expansionsinvariante bestätigt.
- **Gate 0 (`v=6` Positivkontrolle):** **PASS** — `G0v6-3` löste `CA(396; 3, 10, 6)` (`psl25 A=4, B=5, const=6`, 90 Vars) in **0,41 s** (`3.975` Züge) und bestand **beide eingefrorenen Verifier** (`ca_verify` rc=0, `verify_independent.py` rc=0 in `/tmp`).
- **Phase 3A (10,00 min gesamt):**
  - `3A-1` (`pgl25 A=2,B=3 @ 336, k=9`, 2 min): `40` Orbits (17 Basins) — strukturell zu eng.
  - `3A-2` (`psl25 A=4,B=3 @ 336, k=9`, 4 min): `19` Orbits (22 Basins) — `B=3` zu knapp.
  - `3A-3a` (`psl25 A=4,B=5 @ 396, k=11`, 2 min): `16` `D1/D2`-Orbits (0 2-sym offen).
  - `3A-3b1` (`psl25 A=5,B=5 @ 456, k=13`, 60 s): **`5` `D1/D2`-Orbits** (`@7,1 s`, **−34 unter Live-Rekord 490**!).
  - `3A-3b2a` (`psl25 A=6,B=4 @ 486, k=13`, 30 s): `12` Orbits.
  - `3A-3b2b` (`psl25 A=5,B=6 @ 486, k=13`, 30 s): **`3` `D1/D2`-Orbits** (`@1,3 s` auf beiden Threads, **−4 unter Live-Rekord 490**!).
- **Verifier-Integrität:** `verifiers/` strikt READ-ONLY (`sha256sum -c verifiers/SHA256SUMS` 3/3 OK, `git diff main -- verifiers/` leer, `test_verifiers.py` 23/23 PASS, `results/` sauber).
