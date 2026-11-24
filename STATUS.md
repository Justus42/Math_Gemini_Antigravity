# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-24 (Abschluss Phase 3C / Gate 2 ABORT auf Branch `exp/ca-3-k-6`).
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
| `(3, 13, 6)` (`PSL(2,5)`) | **490** | **Abgeschlossen (Gate 2 ABORT — ausgereizt)** | Gemischtes `PSL(2,5)` gekoppelt (3B) & entkoppelt (3C) sauber abgeschlossen: `A=5` stößt über 160+ Basins (54+106 Restarts) hart bei `best_D=3` an; `A=6, B=4` löst `D=0` in `0,01 s`, scheitert aber an `B=4` (`29–32` `2-sym` offen) |
| `(3, 9, 6)` | **361** | Offen / Kandidat | Weg zu `<= 360`: `CA(366; 3, 10, 6)` → Projektion `k=9` (`N=366`) + Row-Deletion (−6 Zeilen) |
| `(3, 11, 6)` | **411** | Beobachtung | `psl25 A=4, B=5 @ 396` erreichte `16` `D1/D2`-Orbits (0 2-sym offen) |
| `(4, 9, 3)` | **135** | Wartend | Benötigt `t=4`-Solver (`AGL(1,3)`-Orbits) |

## 3. Gate-Status & Diagnose (`exp/ca-3-k-6`, Phase 3C)

- **Solver-Stand:** Entkoppelter 2-Stufen-Modus `--mode decoupled-psl25` (Stufe 1 `D1/D2`-only, Stufe 1.5 `D=0`-invariante `2-sym`-Minimierung, Stufe 2 `B`-only) implementiert; alle 7 Sanity-Checks inkl. `DecoupledPSL25` (2×10.000 Züge + Expansionsinvariante, `CA(396; 3, 10, 6)` direkt gelöst) mit **0 Abweichungen** bestanden.
- **Gate 0 (`v=6` Positivkontrolle):** **PASS** — `G0v6-3` löste `CA(396; 3, 10, 6)` (`psl25 A=4, B=5, const=6`, 90 Vars) in **0,41 s** (dual-verifiziert in `/tmp`).
- **Phase 3C & Gate 2 (`PSL(2,5)` auf `(3, 13, 6)`): ABORT / AUSGEREIZT**
  - `3C-1` (`decoupled-psl25 A=5`, `270,26 s`, `2,41M` Züge, `8.923 mv/s`, **106 Restarts**, `seed=9201`): **`best_D = 3`** (`0,1 s`/`0,2 s`), `s1_sols = 0`. Widerlegt die Kopplungshypothese eindeutig: Auch völlig ohne `2-sym`-Gewichte und mit kurzer Tenure (`3..6`/`5..8`) fällt `A=5` bei `k=13` nie unter `3` offene `D1/D2`-Orbits.
  - `3C-2` (`decoupled-psl25 A=6, B=4 @ 486`, Budget `120 s`, in R4 nach 47 min wegen Hänger extern abgebrochen; keine Checkpoints geschrieben): R1–R4 lösten Stage 1 (`best_D = 0`) je in `0,01 s`; Stage 1.5 (`2 s`, `D=0`-invariant) reduzierte `2-sym` kaum (`408→407`, `462→431`, `427→427`, `501→501`); Stage 2 (`B=4`, `5 s`, ~31–35k mv/s, 18–21 Restarts/Runde) blieb bei **`best_2sym = 29` (`exp = 870`, R1)** / `30` (R2) / `32` (R3) stecken.
  - **Gate-2-Urteil:** Reines/gemischtes `PSL(2,5)` (sowie `PGL(2,5)`) auf `CA(N; 3, 13, 6)` für `N <= 486` gilt als **ausgereizt und abgeschlossen** (`A=5` zu eng auf `D1/D2`, `A=6` erfordert `B >= 5` → `N >= 516 > 490`).
- **Verifier-Integrität:** `verifiers/` strikt READ-ONLY (`sha256sum -c verifiers/SHA256SUMS` 3/3 OK, `git diff main -- verifiers/` leer, `results/` sauber).


