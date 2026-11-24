# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-24 (Abschluss Gate 0 & Phase 2D auf Branch `exp/ca-3-9-5`).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md).

## 1. Ziel-Landkarte

Referenz-Audit: [`docs/phase1_dzoba_audit.md`](docs/phase1_dzoba_audit.md) (gegen `chrispbsmolen/ca-tools` Commit `47596cf` & `dzoba/covering-arrays-2026` Commit `040a622`).

| Priorität | Zielzelle `(t, k, v)` | Live-Rekord | Ziel / Stretch | Status |
| :---: | :---: | :---: | :---: | --- |
| **1** | `(3, 9, 5)` | **185** (via `k=10`) | `<= 184` / `<= 180` | **Gate 1 ABGEBROCHEN** (Einzelzell-Tabu/SA-Klasse ausgeschöpft; Pivot empfohlen) |
| **2 (nächstes Ziel)** | `(3, 9, 6)` | **361** | `<= 360` | Bereit für Pivot (gleiche `t=3`-Engine, direkte Prüfung möglicher Symmetriegruppen/Reduktion) |
| **3** | `(4, 9, 3)` | **135** | `<= 134` | Wartend (Nachbar `(4,8,3)=129` in `dzoba`, benötigt `t=4`-Solver) |

## 2. Zusammenfassung der Läufe & Diagnosen auf `(3, 9, 5)`

Alle Läufe auf `(3, 9, 5)` blieben **heuristische Fehlversuche** (kein Nichtexistenzbeweis):
- **Phase 2A (`e18b9b5`, 3 min):** `reduce` ab `CA_185_3_10_5` bei `unc = 28` (starrer AGL(1,5)-Kristall, min $\Delta = +3$); `extend @ 184` bei `96`; `orbit z5 @ 180` bei `53` Orbits.
- **Phase 2B (`3219117`, 14 min):** Geometrisches SA (`1.80 -> 0.05`) erreichte `27` Orbits (`g10 @ 175`) und `48` Orbits (`z5 @ 180`), fror unter $T \approx 0{,}15$ ein; Hybrid-Anhängen von 9 bzw. 4 freien Zeilen an offene `g10`/`z5`-Orbits blieb strukturell begrenzt (`198` bzw. `205`).
- **Phase 2C (`651804c`, 14 min):** Erstversion `tabu-cw` erlitt CW-Gewichts-Blowup (`64:1` / `8:1`); Fix auf fraktionales SWT (`BASE_W=16..MAX_W=26`, max. $1{,}625\times$) in `651804c`.
- **Gate 0 & Phase 2D (14,5 min):**
  - `G0-K1` (`agl5` auf `CA(165; 3, 8, 5)`): **`unc == 0` in 5,39 s**, dual-verifiziert in `/tmp` → beweist Korrektheit & Stärke des Solvers in kompakten Orbiträumen (~64 Variablen).
  - `G0-K2` (`g10` auf bekannt lösbarem `CA(165; 3, 8, 5)`, 90 s): **`16` Orbits** (`cur=20..22`, ab `0,4 s` Plateau) → belegt scharf die Skalierungsgrenze von Einzelzell-`tabu-cw` ab ~128 Variablen.
  - `2D-1` (`g10 @ 175`, 4 min): neuer `g10`-Bestwert **`24` Orbits** (`240` Tripel, nach `3,9 s`, stabil im Full-Scan `cur=30..34`).
  - `2D-2` (`z5 @ 180`, 4 min): **`60` Orbits** (`300` Tripel, kein Blowup, `cur=66..76`).
  - `2D-3` (`extend @ 184`, 4 min): neuer `extend`-Bestwert **`93` Tripel** (S1 nach `2,5 s`, S2 im Full-Scan `cur=94..109` ohne weiteren Durchbruch).

## 3. Harte Gates & Urteil

- **Gate 0 (Positivkontrolle `CA(165; 3, 8, 5)`):**
  - Kontrolle 1 (`agl5`): **PASS** (`unc == 0` in `5,39 s`, Dual-Verifikation bestanden).
  - Kontrolle 2 (`g10`): **DIAGNOSE-WARNUNG** (`16` Orbits vs. Ziel `<= 4` auf bekannt lösbarer Instanz).
- **Gate 1 (Abbruchkriterium Phase 2D auf `(3, 9, 5)`):**
  - Kriterium: mindestens ein Lauf `<= 5` Orbits oder `<= 15` ungedeckte Tripel.
  - Ergebnis: `24` Orbits (`g10`), `60` Orbits (`z5`), `93` Tripel (`extend`).
  - **URTEIL: SAUBERER ABBRUCH (FAIL) für Einzelzell-Tabu/SA auf `(3, 9, 5)`.**
  - **Nächster Schritt (Entscheidung):** Entweder **Pivot** zur nächsten Zielzelle (`(3, 9, 6)` @ 361 mit bestehendem `t=3`-Solver bzw. `(4, 9, 3)` @ 135 mit `t=4` + `AGL(1,3)`/`G`-Orbits, wo kompakte Orbiträume wie in `G0-K1` glänzen!) ODER **echter Methodenwechsel** auf `(3, 9, 5)` (z. B. SAT/MaxSAT/CP-Solver oder 2-Zell-/Row-Replace-Nachbarschaften statt Einzelzell-Tabu).
