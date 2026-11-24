# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-24 (Abschluss Phase 3B auf Branch `exp/ca-3-k-6`).
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
| **`(3, 13, 6)` (Primärfokus)** | **490** | **Aktiv (`exp/ca-3-k-6`)** | Phase 3B (10 min, 157 Restarts): `psl25 A=5,B=6 @ 486` blieb bei **3 `D1/D2`** (`0` 2-sym); `A=5,B=5 @ 456` bei **5 `D1/D2`** (`0` 2-sym); `A=6,B=4 @ 486` drückte `D1/D2` auf **1**, ließ aber **10 `2-sym`** offen |
| `(3, 9, 6)` | **361** | Zurückgestellt | Weg zu `<= 360`: `CA(366; 3, 10, 6)` → Projektion `k=9` (`N=366`) + Row-Deletion (−6 Zeilen) |
| `(3, 11, 6)` | **411** | Beobachtung | `psl25 A=4, B=5 @ 396` erreichte `16` `D1/D2`-Orbits (0 2-sym offen) |
| `(4, 9, 3)` | **135** | Wartend | Benötigt `t=4`-Solver (`AGL(1,3)`-Orbits) |

## 3. Gate-Status & Diagnose (`exp/ca-3-k-6`, Phase 3B)

- **Solver-Upgrade:** Deterministisches Multi-Start `--restart-stag K` in `orbit.rs` & `proj_orbit.rs` integriert; alle 6 Sanity-Checks (`CaState`, `Z5`, `G10`, `AGL5`, `PGL25`, `PSL25`) mit **0 Abweichungen** bestanden.
- **Gate 0 (`v=6` Positivkontrolle):** **PASS** — `G0v6-3` löste `CA(396; 3, 10, 6)` (`psl25 A=4, B=5, const=6`, 90 Vars) in **0,41 s** (`3.975` Züge, dual-verifiziert in `/tmp`).
- **Phase 3B (10,01 min gesamt, kein `unc == 0`-Treffer):**
  - `3B-1` (`psl25 A=5,B=6 @ 486`, 3 min, 54 Restarts): **`3` `D1/D2` + `0` `2-sym`** (`exp=180`, in `0,2 s`/`1,4 s` erreicht, `cur=8..23`).
  - `3B-2` (`pgl25 A=3,B=4 @ 486`, 2 min, 52 Restarts): **`3` `D` + `30` `2-sym`** (`exp=1260`).
  - `3B-3` (`psl25 A=5,B=5 @ 456`, 3 min, 27 Restarts): **`5` `D1/D2` + `0` `2-sym`** (`exp=300`, `cur=20..37`).
  - `3B-4` (`psl25 A=6,B=4 @ 486`, 2 min, 24 Restarts): **`1` `D1/D2` + `10` `2-sym`** (`exp=360`).
- **Zentrale strukturelle Diagnose:**
  1. Bei gekoppelter Suche werden `A=5`-General-Starter durch `2-sym`-Gewichte (`16` vs. `32`) ausgebremst: Ein General-Zug, der 1 `D1/D2`-Orbit schließt (`−32`), aber 3 `2-sym`-Orbits öffnet (`+48`), wirkt `+16` bergauf — obwohl `B=5/6` diese `2-sym`-Orbits sofort trivial schließen könnte!
  2. Da Binär-Starter (`B`) **niemals** `D1/D2`-Orbits beeinflussen, lässt sich `PSL(2,5)` **exakt entkoppeln**: erst das reine **65-Variablen-Subproblem `A=5` nur auf den 572 `D1/D2`-Orbits** auf `0` lösen (ohne `2-sym`-Gewichtsbremse, kürzere Tenure `3..6`), danach `B=5` (`N=456`, −34 Zeilen!) oder `B=6` (`N=486`, −4 Zeilen!) auf die restlichen `2-sym`-Orbits optimieren!
- **Verifier-Integrität:** `verifiers/` strikt READ-ONLY (`sha256sum -c verifiers/SHA256SUMS` 3/3 OK, `git diff main -- verifiers/` leer, `test_verifiers.py` 23/23 PASS, `results/` sauber).

