# Phase 8 Sprint-Log: Satz C.1/C.2, `q = 16` Spur-Baer-Hybrid & Kurz-Explore

- **Datum:** 2026-11-27
- **Branch:** `exp/phase8-bounds-q16hybrid` (Basis: `main @ 0bcbe2b`; PR `#50` und `#51` unberührt).
- **Hardware:** 2 vCPUs (`Intel Xeon @ 2.30 GHz`, Linux x86_64).
- **Außenwirkung:** keine. Kein GitHub-Actions-Lauf, kein Merge nach `main`.

---

## 1. Teil 1: Untergrenzen Satz C.1 & Satz C.2

- **Skript:** [`scripts/phase8_bounds_c1_c2.py`](../../scripts/phase8_bounds_c1_c2.py) (`std`-only, Laufzeit `1,710 s`, Voll-Enumeration-Selbsttest `p <= 17` und `q <= 25` `PASS`).
- **Beweisnotiz:** [`docs/phase8/NOTIZ_4_UNTERGRENZEN_C1_C2.md`](NOTIZ_4_UNTERGRENZEN_C1_C2.md).
- **Belegart:** Informelles Argument aus Vorwärts-Recherche, rechnerisch gegen Listen geprüft, Regel-2d-Prüfung am Sonntag offen.
- **Satz C.1 (`p = 3..53`, Asymptotik `91/68 ≈ 1.338235`):**
  `3:12, 5:34, 7:66, 11:163, 13:228, 17:388, 19:485, 23:710, 29:1128, 31:1289, 37:1837, 41:2256, 43:2481, 47:2961, 53:3764` (alle 9 Sollwerte exakt bestätigt).
- **Satz C.2 (`q = 4..81`, Asymptotik `q^2 + q^(3/2) - (9/8)q`):**
  `4:20, 9:99, 16:304, 25:725, 49:2694, 64:4542, 81:7206` (alle 5 Sollwerte exakt bestätigt).
- **Listenprüfung (`v = q`):** `16` Primzahl-Listen (C.1) und `17` Quadratzahl-Einträge (C.2, inkl. `R_q16_v16_trace_m332.txt` und `3` Baer-v3-Referenzen `q=9:108, q=16:334, q=25:791`) -> **`0` Verletzungen**.

---

## 2. Teil 2: `q = 16` Spur-Baer-Hybrid (`m = 315`, `m = 332`) & Dual-Verifikation

- **Skript:** [`scripts/phase8_q16_trace_hybrid.py`](../../scripts/phase8_q16_trace_hybrid.py) (`std`-only, feldunabhängig über `GeneralGF(16)`, `mod_poly = [1, 1, 0, 0, 1]`, `Fn = [0, 1, 6, 7]`, `om = 2`, `mu_a = 1`, `mu_b = 2`).
- **Erzeugte Listen (`data/phase8_q16_hybrid/`, 2× byte-identisch, `SHA256SUMS` `2/2 OK`):**
  - `R_q16_v15_trace_m315.txt` (`v = 15, m = 315`): `sha256: d41a746e0d09816f7cd73f0c721a25412b444633e2df3d3e581f7587309ce226`; `phase7_lift.py --check-m`: `315 rows, 18 columns, uncovered pairs = 0`.
  - `R_q16_v16_trace_m332.txt` (`v = 16, m = 332`): `sha256: 65317ce58a5b7354bd186915d494b13c5fb7cd4fea4bd42d4fb4cfd47ae74e28`; `phase7_lift.py --check-m`: `332 rows, 18 columns, uncovered pairs = 0`.
- **Dual-Verifikation `CA(80640; 4, 18, 15)` (in `/tmp/phase8_q16_hybrid/`, nicht committet):**
  - Erzeugung: `python3 scripts/phase7_lift.py --q 16 --v 15 --reps data/phase8_q16_hybrid/R_q16_v15_trace_m315.txt --t 4 --out /tmp/phase8_q16_hybrid/CA_80640_4_18_15.txt` (2× byte-identisch bestätigt).
  - SHA-256: `2d0f01684a21ade09faabb77ccd53b2bc752316e09cbd650a9becd08636e2143` (`80640` Zeilen × `18` Spalten).
  - `verifiers/ca_verify` (pos): **Exit 0** (`0,617 s`, `all 3060 column sets fully cover all 50625 tuples`).
  - `verifiers/ca_verify` (neg, letzte Zeile entfernt, `80639` Zeilen): **Exit 1** (`0,644 s`, `891/3060 column sets have gaps, 891 missing tuples`).
  - `verifiers/verify_independent.py` (pos): **Exit 0** (`98,771 s`, `154912500 total interactions`).
  - `verifiers/verify_independent.py` (neg, `80639` Zeilen): **Exit 1** (`98,959 s`, `missing 891/154912500 interactions across 891/3060 column sets`).
  - **Tabelleneinordnung (`ca-tools @ 697325b`, Vergleichswert `(4, 18, 15)` = `83519` [Bush-17]):** `80640 < 83519` (`-2879` Zeilen; lokal dual-verifiziert, Drittprüfung nach Regel 2d offen).

---

## 3. Teil 3: Kurz-Explore (`timeout <= 60 s` je Experiment)

### 3.1 `q = 16` Spur-Hybrid-Varianten (`scripts/phase8_q16_explore.py`)
- **Strukturanalysen (deterministisch):**
  - Basis `v = 14, m = 298` (1 Vollgerade `V_0` + 1 Spur-Set `V_1`) lokal konstruiert und mit `unc = 0` bestätigt.
  - **Profil 2 (`[8, 2^8]`, 8 Punkte auf `d = 0`, je 2 auf 8 Geraden `d != 0`):** projektiv aus derselben `F_2`-linearen Menge der Größe 25 konstruiert und als Blocking Set der Größe 24 verifiziert. Über alle 15 Geraden-Skalierungen `d -> s*d` schneiden höchstens `2/3` der 8 Geraden die 3 freien Geraden `d_free`, sodass mindestens `6` K-Geraden getroffen werden (`>= +12` Zusatzvertreter auf `d != 0` pro Symbol gegenüber `+0` bei `[8, 8, 8]`).
  - **Symmetrische 3-Trace-Tripel `(0,1)+(0,2)+(1,2)` für `v = 15`:** Voll-Scan findet `120` disjunkte Tripel (`ov = 0` auf `d_free`), aber wegen der Charakteristik-2-Kopplung der Zielmengen auf `d = 0` ergibt die exakte `d = 0`-Untergrenze inkl. K-Paarbedarf `>= 316` (`> 315`).
  - **4-Trace-Bilanz für `v = 16`:** `4 * 16 = 64` Punkte auf `48` freien Punkten erzwingen mindestens `+16` Überlapp pro Seite (`+32` gesamt -> `>= 336 > 332`).
  - **K-Promotion:** Einzel-Promotion einer Baer-K-Klasse (exakte 4×4-Partition ihrer 4 Geraden) verschlechtert bei festem 12-K-Gitter die Bilanz.
- **Lokale Tabu-Reduktions-Proben (je `14,00 s`, Gesamt `42,03 s <= 60 s`, Seeds `1614/1615/1616`):**
  - `v = 14` (`m = 298 -> 297`): `best_unc = 1` (`9.832.680` Auswertungen, `702.307 evals/s`) — erfolglos.
  - `v = 15` (`m = 315 -> 314`): `best_unc = 1` (`10.049.256` Auswertungen, `717.775 evals/s`) — erfolglos.
  - `v = 16` (`m = 332 -> 331`): `best_unc = 1` (`9.900.360` Auswertungen, `707.132 evals/s`) — erfolglos.
- **Belegart:** Strukturausschluss für die untersuchten Spezialfamilien (Profil 2 auf festem 12-K-Gitter; disjunkte 3-Trace-Tripel `>= 316`); heuristische Tabu-Suche erfolglos (Optimalität bleibt offen).

### 3.2 `p = 7, v = 7` Kurz-Probe (`scripts/phase8_p7_tabu.c`, kompiliert nach `/tmp/phase8_p7_tabu`)
- **Positivkontrolle (`m = 68`, Kaltstart ohne `--init`, 2 Threads, Seed `100`):** **`best_unc = 0` in `0,123 s`** (`3` Neustarts, `1.014.212 moves/s`, `19.198.583 evals/s`).
- **Suchlauf (`m = 67`, `--time 55`, extern `timeout 60`, 2 Threads, Seed `20261127`, Warmstarts ab `data/phase7/R_q7_m68.txt` + Skelett-/Zufalls-Kaltstarts):**
  - Laufzeit: `55,005 s` (kein Timeout).
  - Durchsatz: `58.656.854` Schritte (`1.066.401 moves/s`), `1.096.394.882` Auswertungen (`19.932.820 evals/s`), `1.411` Neustarts.
  - Bestwert: **`best_unc = 1`** (keine gültige `m = 67`-Liste gefunden; `m = 66` daher nicht gestartet).
- **Belegart:** Heuristische Suche erfolglos (`55 s`, `1,10 Mrd.` Auswertungen, Plateau `unc = 1`; Existenz von `m = 67` oder `m = 66` bleibt offen).

---

## 4. Verifier-Integrität

- `sha256sum -c verifiers/SHA256SUMS`: `3/3 OK`.
- `git diff main -- verifiers/`: leer.
- `python3 verifiers/test_verifiers.py`: `23/23 PASS`.
