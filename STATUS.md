# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-24 (`main`-Sync Governance/Tracking aus `exp/ca-3-k-6` @ `8c210f2`; Start Phase 3: `exp/t3-target-scan`).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md).

## 0. Governance- & Branch-Status (`main`-Sync)

- **`main`-Sync:** Governance- und Tracking-Dateien (`GEMINI.md`, `AGENTS.md`, `STATUS.md`, `docs/RUN_LOG.md`) aus `exp/ca-3-k-6` (`8c210f2`) sauber auf `main` übernommen (ohne experimentelle Solver-Artefakte).
- **Abgeschlossene Such-Branches:**
  - `exp/ca-3-9-5` (`3ca3058`): **Abgeschlossen (Gate 1 ABORT)** — `G0-K1` PASS (`5,39 s`), danach Stagnation auf `(3, 9, 5)` (`2D`: 24/60 Orbits, 93 unc).
  - `exp/ca-3-k-6` (`8c210f2`): **Abgeschlossen (Gate 2 ABORT)** — `G0v6-3` PASS (`0,41 s`), `PSL(2,5)`/`PGL(2,5)` auf `(3, 13, 6)` für `N <= 486` ausgereizt (`3C-1`: 106 Restarts hart bei `best_D=3`; `3C-2`: `B=4` bei `29–32` `2-sym` offen).
- **Aktive Phase (Phase 3):** Start auf Branch `exp/t3-target-scan` — systematischer `t=3` Target-Scan (`v=4..14`, `k=6..35`) gegen `chrispbsmolen/ca-tools` zur Auswahl der nächsten Zielzelle samt Gate-0-Anker (noch kein Solver-Code).

## 1. Live-Stand `CA(N; 3, k, 6)` (`k = 7..14`, Referenz aus `exp/ca-3-k-6`)

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
| `(3, 9, 5)` (`exp/ca-3-9-5`) | **185** | **Abgeschlossen (Gate 1 ABORT)** | Einzelzell-Tabu/SA auf `exp/ca-3-9-5` (`3ca3058`) sauber beendet (`G0-K1` PASS 5,39s; `2D`: 24/60 orb, 93 unc) |
| `(3, 13, 6)` (`exp/ca-3-k-6`) | **490** | **Abgeschlossen (Gate 2 ABORT — ausgereizt)** | Gemischtes `PSL(2,5)` gekoppelt (3B) & entkoppelt (3C) sauber abgeschlossen: `A=5` über 160+ Basins hart bei `best_D=3`; `A=6, B=4` scheitert an `B=4` (`29–32` `2-sym` offen) |
| Phase 3 (`exp/t3-target-scan`) | — | **Aktiv (Target-Scan)** | Systematische Auswertung `t=3`, `v=4..14`, `k=6..35` inkl. Gruppen-Fingerprints, Sweet-Spot-Filter und Gate-0-Ankern |
| `(3, 9, 6)` | **361** | Offen / Sekundärkandidat | Weg zu `<= 360`: `CA(366; 3, 10, 6)` → Projektion `k=9` (`N=366`) + Row-Deletion (−6 Zeilen) |
| `(4, 9, 3)` | **135** | Wartend | Benötigt `t=4`-Solver (`AGL(1,3)`-Orbits) |

## 3. Verifier-Integrität & Gate-Archiv

- **Verifier-Integrität:** `verifiers/` strikt READ-ONLY (`sha256sum -c verifiers/SHA256SUMS` 3/3 OK, `python3 verifiers/test_verifiers.py` 23/23 PASS, `git diff main -- verifiers/` leer, `results/` sauber).
- **Gate-Archiv (`exp/ca-3-9-5` & `exp/ca-3-k-6`):**
  - `exp/ca-3-9-5`: Gate 0 PASS (`G0-K1` `CA(165; 3, 8, 5)` in `5,39 s`), Gate 1 ABORT (`2D-1..3`).
  - `exp/ca-3-k-6`: Gate 0 PASS (`G0v6-3` `CA(396; 3, 10, 6)` in `0,41 s`), Gate 2 ABORT (`3C-1`/`3C-2`).
