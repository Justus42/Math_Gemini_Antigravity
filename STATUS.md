# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-24 (Abschluss `P3-SCAN1` auf Branch `exp/t3-target-scan`; vollständiger Bericht siehe [`docs/TARGET_SCAN_t3.md`](docs/TARGET_SCAN_t3.md)).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md).

## 0. Governance- & Branch-Status

- **`main`-Sync:** Governance- und Tracking-Dateien (`GEMINI.md`, `AGENTS.md`, `STATUS.md`, `docs/RUN_LOG.md`) aus `exp/ca-3-k-6` (`8c210f2`) auf Commit `40b71ce` synchronisiert und wegen HTTP-403-Schutz auf `main` als Branch `chore/sync-main-docs` gepusht (zur PR-Übernahme nach `main`).
- **Abgeschlossene Such-Branches:**
  - `exp/ca-3-9-5` (`3ca3058`): **Abgeschlossen (Gate 1 ABORT)** — `G0-K1` PASS (`5,39 s`), Stagnation auf `(3, 9, 5)` (`2D`: 24/60 Orbits, 93 unc).
  - `exp/ca-3-k-6` (`8c210f2`): **Abgeschlossen (Gate 2 ABORT)** — `G0v6-3` PASS (`0,41 s`), `PSL(2,5)`/`PGL(2,5)` auf `(3, 13, 6)` für `N <= 486` ausgereizt (`3C-1`: `best_D=3` über 106 Restarts; `3C-2`: `B=4` bei `29–32` `2-sym` offen).
- **Aktive Phase (`exp/t3-target-scan`):** Systematischer `t=3` Target-Scan (`P3-SCAN1`, `v=4..14`, `k=6..35` gegen `ca-tools` @ `4f3c95d`) **abgeschlossen** — noch kein Rust-Solver gestartet; wartet auf gemeinsame Festlegung von Zielzelle und Gate-0-Design.

## 1. Live-Stand `CA(N; 3, k, 6)` (`k = 7..14`, aktualisiert @ `4f3c95d`)

Abgerufen via `gh api` aus `chrispbsmolen/ca-tools` (`table/ca_table.csv.gz` @ `4f3c95d`, `2026-11-25T00:10:02Z`; true min über `k' >= k`):

| Zelle `(3, k, 6)` | Live-Min `N` | `tier` | Konstruktion / Herkunft |
| :---: | :---: | :---: | --- |
| `(3, 7, 6)` | **290** | `CITED` | Torres Jimenez |
| `(3, 8, 6)` | **301** | `CITED` | Torres Jimenez |
| `(3, 9, 6)` | **341** | `VERIFIED` | Row-deletion SA + Tabu (`laverdi-2026-11`, `2026-11-24`, −20 gegenüber `361`) |
| `(3, 10, 6)` | **366** | `VERIFIED` | Iterative row deletion + Nurmela-Tabu aus 396-row `PSL(2,5)` (`A=4, B=5, const=6`) |
| `(3, 11, 6)` | **411** | `VERIFIED` | Row deletion + conflict-tabu/BE-PAWS aus `418` (aus 426-row `PSL(2,5)`) |
| `(3, 12, 6)` | **456** | `VERIFIED` | Reines `PSL(2,5)` (`A=5, B=5, const=6` = 456 Zeilen) |
| `(3, 13, 6)` | **490** | `CITED` | Torres Jimenez |
| `(3, 14, 6)` | **498** | `CITED` | Chateauneuf-Kreher doubling postop NCK |

## 2. Ziel-Landkarte & Track-Status

| Track / Zelle | Live-Rekord | Status | Kurzfazit |
| --- | :---: | --- | --- |
| `(3, 9, 5)` (`exp/ca-3-9-5`) | **185** | **Abgeschlossen (Gate 1 ABORT)** | Einzelzell-Tabu/SA auf `exp/ca-3-9-5` (`3ca3058`) beendet (`G0-K1` PASS `5,39 s`) |
| `(3, 13, 6)` (`exp/ca-3-k-6`) | **490** | **Abgeschlossen (Gate 2 ABORT)** | `PSL(2,5)`/`PGL(2,5)` für `N <= 486` ausgereizt (`G0v6-3` PASS `0,41 s`) |
| **`(3, 15..18, 10)` (`PGL(2,9)`)** | **2205 / 2232** | **Top-Kandidat #1–#4 (Scan)** | `A=2` deckt `3-sym` deterministisch bis `k=18`; `B=8→2170` (`-35/-62`, konstruktiv mit `bin=45` gesichert), `B=6..7→1990/2080` rein binär suchbar (`1.820–3.264` Orbits); Gate-0: `k=10` (`V=70`) / `k=13` (`V=78`) |
| **`(3, 16..20, 12)` (`PGL(2,11)`)** | **3564–3806** | **Top-Kandidat #5–#8, #11 (Scan)** | Alle `CITED` (`OA-Fuse⁴`/`CK`); `A=2` deterministisch bis `k=22`; `B=6..8→3444/3576/3708` (`-39` bis `-120`) |
| `(3, 13..14, 9)` (`PSL(2,8)`) / `(3, 14, 10)` (`PGL(2,9)`) | **1377 / 1885** | Strikt `V<=95` (#9, #10, #14) | `A=2, B=4` (`V=78..84`), aber eng auf `2-sym` (`bc2 = 1.16–1.19`) |
| `(3, 9, 6)` | **341** | Herabgestuft | Am `2026-11-24` bereits auf `341` verbessert (`laverdi-2026-11`) |
| `(4, 9, 3)` | **135** | Wartend | Benötigt `t=4`-Solver (`AGL(1,3)`-Orbits) |

## 3. Verifier-Integrität & Gate-Archiv

- **Verifier-Integrität:** `verifiers/` strikt READ-ONLY (`sha256sum -c verifiers/SHA256SUMS` 3/3 OK, `python3 verifiers/test_verifiers.py` 23/23 PASS, `git diff main -- verifiers/` leer, `results/` sauber).
- **Gate-Archiv:**
  - `exp/ca-3-9-5`: Gate 0 PASS (`G0-K1` `CA(165; 3, 8, 5)` in `5,39 s`), Gate 1 ABORT (`2D-1..3`).
  - `exp/ca-3-k-6`: Gate 0 PASS (`G0v6-3` `CA(396; 3, 10, 6)` in `0,41 s`), Gate 2 ABORT (`3C-1`/`3C-2`).
  - `exp/t3-target-scan`: Target-Scan `P3-SCAN1` PASS (`docs/TARGET_SCAN_t3.md`); Gate 0 für Zielzelle noch offen (vor Solver-Bau festzulegen).

