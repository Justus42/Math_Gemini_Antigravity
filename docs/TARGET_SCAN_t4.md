# Systematischer `t = 4` Target-Scan & Phase-5-Aufklärung (`docs/TARGET_SCAN_t4.md`)

Stand: **2026-11-25** | Branch: `exp/phase5-recon` | Reproduzierbares Analysescript: [`scripts/scan_t4_targets.py`](../scripts/scan_t4_targets.py) (Pure Python `std`-only).
Datenbasis: `chrispbsmolen/ca-tools` @ Commit `083a0933e3561625b2aad9bd19035ad76d783f03` (`2026-11-25T13:32:06Z`, Dateien `table/ca_table.csv.gz`, `table/ca_frame.csv`, `table/derived.csv`, `table/priority.csv`), rein lesend via `gh api` bezogen (`PR #88` unverändert; kein Schreibzugriff auf Fremd-Repos).
Regel-7-Konformität: Dieser Scan dient ausschließlich unabhängigen Tracks abseits von `PGL(2,q)+CCL` auf `t = 3`.

---

## 1. Methodik, Effektive Schranke `N_eff` & 2-vCPU-Verifikationsmodell

- **Effektive Bestgröße (`N_eff`):** Für jede Zelle `(t, k, v)` wird die exakte monotone Stair-Step-Hülle über alle drei Tabellen berechnet:
  $$N_{\text{eff}}(t, k, v) = \min_{k' \ge k}\; \min\big(N_{\text{ca\_table}}(k'),\; N_{\text{ca\_frame}}(k'),\; N_{\text{derived}}(k')\big)$$
  Ungültige Tiers (`DISPUTED`, `FAILED_PENDING_RECHECK`) werden ausgeschlossen; bei Gleichstand wird `VERIFIED` vor `CITED` und der kleinste Zeuge `k' >= k` gewählt.
  - **Abgleich `derived.csv` für `t = 4, v = 3..14, k <= 40`:** Nur eine einzige Zelle wird durch `derived.csv` strikt verbessert: **`(4, 25, 14)`** (`126.929` via `fuse` aus `CAN(4,25,15)=126.931` statt `126.935`).
- **2-vCPU-Verifikationsmodell** (Intel Xeon @ 2.30 GHz, 2 vCPUs, 7,8 GiB RAM, kalibriert aus [`STATUS.md`](../STATUS.md)):
  - `verifiers/ca_verify` (C, AVX2, 2 Threads): `~5,0e8` Plane-Row-Ops/s (`C(k, t-1) · N_eff · v · ceil(k/64)`).
  - `verifiers/verify_independent.py` (Python, 1 Thread — maßgeblicher Flaschenhals unter `RULES.md`-Dual-Verifikation): konservativ `3,5e6` Row-Tupel/s (`C(k,4)·N_eff`) bei `t = 4`, `4,5e6` bei `t = 3`, `2,8e6` bei `t = 5`.
  - **Filterkriterium `dual_60s`:** `est_ca_s + est_py_s <= 60,0 s` (entspricht bei `t = 4` grob `C(k,4)·N_eff <= 2,0e8` bzw. `C(k,4)·v^4 <= 7e7..1e8`). Von `288` gescannten `(4, k, v)`-Zellen (`v = 3..14`, `k = 5..max(28, 2v+2)`) erfüllen **`222`** das `<= 60 s`-Dual-Verifikationskriterium.

---

## 2. 2026-Belegungs-Audit für `t = 4, v = 3..14` (Sitjar / Bai / Canli / Smolen)

Prüfung aller Einträge mit `entered >= 2026-10-01` in `ca_table.csv.gz` (abgeglichen mit `priority.csv`) gegen offene `CITED (get=none)`-Zellen im niedrigen Spaltenbereich (`k <= 25`):

| `v` | Typ | `VER / Gesamt` (`ca_frame, k<=25`) | `2026`-Zeilen (alle `k`) | `2026`-bearbeitete `k <= 25` | Offene `CITED (get=none)` bei `k <= 25` | Dominierende `2026`-Quellen | Status-Bewertung |
| :-: | :---: | :---: | :---: | --- | --- | --- | --- |
| `3` | `PP` | `0 / 13` | `41` | `[9]` | `11, 12, 13, 15, 17, 20..23` | Smolen (35, Zyklotomie `k>=30`), Sitjar (2) | **Unberührt bei `k=11..23`** (`CITED` CPHF/TJ) |
| `4` | `PP` | `0 / 13` | `14` | `[6]` | `7, 8, 9, 12, 17, 18, 20..24` | Smolen (14, Zyklotomie/Tie) | **Weitgehend unberührt** (`k=7..24` komplett `CITED`) |
| `5` | `PP` | `4 / 10` | `19` | `[7, 8, 9, 18]` | `11, 14, 20, 22, 25` | Canli (13, gr. `k`), Sitjar (4), Bai (1) | Nischen bei `k=10..14` und `k=21..25` |
| **`6`** | **`NON_PP`** | **`18 / 19`** | **`77`** | **`5..25` (lückenlos)** | **`[]` (keine)** | **Sitjar (48), Smolen (16), Bai (13)** | **VOLL GESÄTTIGT (`k<=25`) — meiden** |
| `7` | `PP` | `1 / 6` | `68` | `[9, 15, 18, 19, 24]` | `15, 18, 19, 24` *(+ Plateaus `10..14, 16..17, 20..23`)* | `doi:10.3390/math12121908` (59 `CITED`), Canli (6), Sitjar (1) | **Unberührte CPHF-Plateaus** ab `k=10` |
| `8` | `PP` | `2 / 6` | `16` | `[10, 20, 22]` | `15, 19` *(Plateaus `11..15`, `16..19`)* | Canli (12, gr. `k`), Bai (2), Smolen (2) | **Unberührte `NEAR_BUSH`-Plateaus `k=11..19`** |
| `9` | `PP` | `2 / 6` | `14` | `[11, 24]` | `17, 21, 22` *(Plateaus `12..17`, `18..21`)* | Canli (12, gr. `k`), Bai (2) | **Unberührte `NEAR_BUSH`-Plateaus `k=12..22`** |
| **`10`** | **`NON_PP`** | **`7 / 19`** | **`33`** | `[5, 6, 13, 21..25]` | **`7..12`, `14..17`, `20`** *(Plateau `18..20`)* | Sitjar (22), Bai (9), Smolen (1), LaVerdi (1) | **Klare unberührte Mittel-Nische `k=14..20`** (plus `k=7..12`) |
| `11` | `PP` | `1 / 5` | `18` | `[12, 13]` | `14, 20, 24` *(Plateaus `15..20`, `21..24`)* | Canli (10, gr. `k`), Bai (5), `arXiv:2510.13122` (2) | **Unberührte `NEAR_BUSH`-Plateaus `k=14..21`** |
| **`12`** | **`NON_PP`** | **`2 / 12`** | **`22`** | `[5, 6, 15]` | **`7..14`, `21`** *(Plateau `16..21`)* | Sitjar (12), Bai (9), Smolen (1) | **Große unberührte Nische `k=16..21`** (`54.923`, `+14.447` Sprung) |
| `13` | `PP` | `1 / 3` | `18` | `[14, 15]` | `21` *(Plateau `16..21`)* | Canli (9, gr. `k`), Bai (7), `arXiv:2510.13122` (1) | **Unberührtes `NEAR_BUSH`-Plateau `k=16..18`** (`<=60s`) |
| **`14`** | **`NON_PP`** | **`4 / 18`** | **`15`** | `[5, 6, 19, 24, 25]` | **`7..18`, `20`** | Bai (7), Sitjar (4), Smolen (4) | `k=7..17` offen & `<=46s`; `k>=18` `py > 72 s` |

---

## 3. Strukturmuster bei `t = 4`: Nicht-Primzahlpotenzen & `NEAR_BUSH` (`k = v+2..2v`)

### 3.1 Primzahlpotenzen knapp oberhalb der Bush-Breite (`k = v+2 .. 2v`)
Für alle Primzahlpotenzen `q in {7, 8, 9, 11, 13}` zeigt die Tabelle am Commit `083a093` ein einheitliches dreistufiges Muster:
1. **`k = q + 1` (Bush-/Reed-Solomon-OA):** Exakt `N = q^4` (`1,00×`, `VERIFIED`/`file`).
2. **`k = q + 2` (`+1` über Bush):** Bereits im Nov. 2026 durch Grad-2-Polynom- bzw. Coset-/Postop-Konstruktionen auf **`1,48–1,50 × q^4`** gedrückt (`VERIFIED`: `(4,9,7)=3.556`, `(4,10,8)=6.101`, `(4,11,9)=9.801`, `(4,13,11)=21.901`, `(4,15,13)=42.757`).
3. **`k = q + 3` (`+2` über Bush) bis `2q`:** Durchgehend ein **scharfer Sprung (`+903` bis `+12.168` Zeilen)** direkt auf mehrspaltige `CITED (get=none)`-Plateaus aus 3-Restricted-SCPHF / CPHF bei **`1,86–1,92 × q^4`**:
   - **`v = 7` (`k_oa = 8`):** `k = 10..15` flach bei **`4.459` (`1,86×`)**, `dN = +903`, `dual = 0,28–1,7 s`; zweiter Sprung an der `CPHF(2)→CPHF(3)`-Kante bei **`k = 20..24: 6.517` (`2,71×`, `dN = +1.722`, `dual = 9,0–20 s`)**.
   - **`v = 8` (`k_oa = 9`):** `k = 11..15` flach bei **`7.680` (`1,88×`)**, `dN = +1.579`, `dual = 0,74–3,1 s`; `k = 16..19: 8.128` (`1,98×`, `dual = 4,3–8,5 s`).
   - **`v = 9` (`k_oa = 10`):** `k = 12..17` flach bei **`12.393` (`1,89×`)**, `dN = +2.592`, `dual = 1,8–8,6 s`; `k = 18..21: 13.041` (`1,99×`, `dual = 11,6–23,4 s`).
   - **`v = 11` (`k_oa = 12`):** `k = 14: 27.544` (`1,88×`, `dN = +5.643`, `dual = 8,1 s`), `k = 15..20: 27.951` (`1,91×`, `dual = 11,2–39,4 s`), `k = 21: 29.161` (`1,99×`, `dual = 50,7 s`).
   - **`v = 13` (`k_oa = 14`):** `k = 16..18` (Teil des `k = 16..21`-Plateaus) bei **`54.925` (`1,92×`)**, `dN = +12.168`, `dual = 29,4–49,2 s` (`k >= 19` überschreitet `60 s` in `verify_independent.py`).
   - **Kleinere Primzahlpotenzen `v = 4, 5`:** Bei `v = 4` sind alle Zellen `k = 7..25` `CITED (get=none)` (`k=7: 384`, `k=8: 416`, `k=9: 448`, `k=10..12: 496`, `k=13..17: 508`, steiler `CPHF(2)→CPHF(3)`-Sprung bei **`k = 18: 703` (`2,75×`, `+195`, `dual = 0,6 s`)**). Bei `v = 5` liegt der `CPHF(2)→CPHF(3)`-Sprung bei **`k = 21..22: 1.745` (`2,79×`, `+496`, `dual = 3,0–3,7 s`)**, und `k = 10..11 (1.125)` sowie `k = 12..14 (1.225)` sind `CITED (get=none)` (`dual <= 0,35 s`).

### 3.2 Nicht-Primzahlpotenzen (`v in {6, 10, 12, 14}`)
- **`v = 6` (`v^4 = 1.296`):** Vollständig durch 2026-Beiträge (Sitjar/Bai/Smolen) abgedeckt (`k = 6..25` durchgängig `VERIFIED`). Keine attraktive Einstiegsnische.
- **`v = 10` (`v^4 = 10.000`):** Nach `k = 7..12` (`12.855..14.562`, `1,29–1,46×`, `OA(11^4)`-Fuse, `CITED`) und LaVerdis `k = 13` (`20.383`, `VERIFIED`) liegt eine **komplett unberührte `CITED (get=none)`-Zone bei `k = 14..20`**:
  - `k = 14`: `23.889` (`2,39×`, `+3.506`, `OA-fuse³`, `dual = 7,0 s`)
  - `k = 15..17`: `27.233 / 27.513 / 27.859` (`2,72–2,79×`, `SCPHF-fuse`, `dual = 10,9–19,3 s`)
  - `k = 18..20`: Plateau `27.949` (`2,79×`, `3-Restricted SCPHF fuse`, `dual = 24,9–39,3 s`).
- **`v = 12` (`v^4 = 20.736`):** `k = 7..14` sitzt auf `OA(13^4)`-Fuse (`25.875..28.486`, `1,25–1,37×`, `CITED`); Sitjar erreichte `k = 15: 40.476` (`1,95×`, `VERIFIED`). Direkt dahinter folgt der **größte absolute Sprung im `<= 60 s`-Fenster**: **`k = 16..21` bei `54.923` (`2,65×`, `dN = +14.447`, `CITED` 3-Restricted SCPHF fuse)**, wovon `k = 16..18` in `29,3–49,1 s` dual-verifizierbar sind (`ca_verify` jeweils `0,74–1,08 s`).
- **`v = 14` (`v^4 = 38.416`):** `k = 7..17` sind `CITED (get=none)` (`1,22–1,70×`, `augmentOA` bzw. `OA(16^4)`-Fuse², `dual = 0,5–45,8 s`); ab dem großen Sprung `k = 18` (`82.993`, `2,16×`, `+17.585`) liegt `ca_verify` zwar bei `1,9 s`, `verify_independent.py` jedoch bei `~73 s` (außerhalb des `<= 60 s`-Filters).

---

## 4. Top-15-Kandidatenliste (`t = 4`, `v = 3..14`, Dual-Verifikation `<= 60 s`)

Erzeugt durch [`scripts/scan_t4_targets.py`](../scripts/scan_t4_targets.py) (dedupliziert pro `(v, N_eff)`-Plateau, reine harte Kennzahlen: Offenheit `CITED/none`, Verhältnis `N_eff / v^4`, Sprung `ΔN / v^4` & Plateaubreite, `NON_PP`/`NEAR_BUSH`-Klasse, 2-vCPU-Dual-Verifikationszeit `<= 60 s`, Abzug bei 2026-Sättigung).

| # | Score | Zelle `(4, k, v)` | Plateau `k` (`<=60s`) | `N_eff` (`083a093`) | `N_eff / v^4` | Sprung `ΔN` | `Tier / Get` | Klasse | `C(k,4)·v^4` | Gesch. `ca / py` (s) | Quelle (`ca_table` / Familie) |
| :-: | :-: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| **1** | `92,2` | **`(4, 16, 12)`** | `16..18` *(ges. ..21)* | `54.923` | `2,65×` | `+14.447` | `CIT / none` | `NON_PP` | `37.739.520` | `0,74 / 28,6` | `S1`: `scphfCA` (3-Restr. fuse) |
| **2** | `83,7` | **`(4, 15, 10)`** | `15` | `27.233` | `2,72×` | `+3.344` | `CIT / none` | `NON_PP` | `13.650.000` | `0,25 / 10,6` | `S1`: `scphfCA` (WC Tabu fuse) |
| **3** | `82,7` | **`(4, 12, 9)`** | `12..17` | `12.393` | `1,89×` | `+2.592` | `CIT / none` | `NEAR_BUSH` | `3.247.695` | `0,05 / 1,8` | `S1`: `scphfCA` (3-Restr. RE) |
| **4** | `82,3` | **`(4, 11, 8)`** | `11..15` | `7.680` | `1,88×` | `+1.579` | `CIT / none` | `NEAR_BUSH` | `1.351.680` | `0,02 / 0,7` | `S1`: `scphfCA` (3-Restr. RE) |
| **5** | `82,1` | **`(4, 24, 3)`** | `24..27` | `337` | `4,16×` | `+41` | `CIT / none` | `PP` | `860.706` | `0,01 / 1,0` | `S1`: `cphfCA` (3-stage) |
| **6** | `81,8` | **`(4, 10, 7)`** | `10..15` | `4.459` | `1,86×` | `+903` | `CIT / none` | `NEAR_BUSH` | `504.210` | `0,01 / 0,3` | `S1/S7`: `cphfCA` (TJ-IM 2024) |
| **7** | `81,2` | **`(4, 20, 7)`** | `20..24` | `6.517` | `2,71×` | `+1.722` | `CIT / none` | `PP` (`CPHF3`) | `11.632.845` | `0,10 / 9,0` | `S7`: `cphfCA` (TJ-IM 2024) |
| **8** | `79,0` | **`(4, 21, 5)`** | `21..22` | `1.745` | `2,79×` | `+496` | `CIT / none` | `PP` (`CPHF3`) | `3.740.625` | `0,02 / 3,0` | `S1`: `cphfCA` |
| **9** | `78,7` | **`(4, 14, 10)`** | `14` | `23.889` | `2,39×` | `+3.506` | `CIT / none` | `NON_PP` | `10.010.000` | `0,17 / 6,8` | `S1`: `SCA_Busht` (`OA fuse³`) |
| **10** | `78,2` | **`(4, 18, 3)`** | `18..20` | `271` | `3,35×` | `+34` | `CIT / none` | `PP` | `247.860` | `0,01 / 0,2` | `S1`: `cphfCA` (3-stage) |
| **11** | `78,2` | **`(4, 18, 10)`** | `18..20` | `27.949` | `2,79×` | `+90` | `CIT / none` | `NON_PP` | `30.600.000` | `0,46 / 24,4` | `S1`: `scphfCA` (3-Restr. fuse) |
| **12** | `77,9` | **`(4, 16, 13)`** | `16..18` *(ges. ..21)* | `54.925` | `1,92×` | `+12.168` | `CIT / none` | `NEAR_BUSH` | `51.981.020` | `0,80 / 28,6` | `S1`: `scphfCA` (3-Restr. RE) |
| **13** | `77,4` | **`(4, 16, 10)`** | `16` | `27.513` | `2,75×` | `+280` | `CIT / none` | `NON_PP` | `18.200.000` | `0,31 / 14,3` | `S1`: `scphfCA` (WC Tabu fuse) |
| **14** | `76,7` | **`(4, 18, 4)`** | `18` | `703` | `2,75×` | `+195` | `CIT / none` | `PP` (`CPHF3`) | `783.360` | `0,01 / 0,6` | `S1`: `cphfCA` (3-stage) |
| **15** | `76,0` | **`(4, 16, 8)`** | `16..19` | `8.128` | `1,98×` | `+448` | `CIT / none` | `NEAR_BUSH` | `7.454.720` | `0,07 / 4,2` | `S1`: `scphfCA` (2-Restr. RE) |

*(Ergänzung außerhalb Top 15: **`(4, 14, 11)`** [`27.544`, `1,88×`, `dN=+5.643`, `dual=8,1 s`] und **`(4, 15..20, 11)`** [`27.951`, `1,91×`, `dual=11,2–39,4 s`] gehören strukturell direkt zur selben `NEAR_BUSH`-Familie wie #3, #4, #6, #12.)*

### 4.1 Nüchterne Einordnung der aussichtsreichsten `t = 4`-Ansätze
1. **Direktester Experiment-Prototyp (`NEAR_BUSH` `k = q+3` auf `v = 7, 8, 9` — Plätze #6, #4, #3):** Kleinste Verifikationskosten (`0,3–1,8 s` dual), sauberste algebraische Struktur über `GF(q)` (z. B. lineare Cosets / Polynomfamilien / verallgemeinerte CPHF-Blöcke jenseits `k = q+2`, um die `1,86–1,89×`-Schwelle zu unterbieten — und selbst ein Treffer *auf* `4.459 / 7.680 / 12.393` schließt eine offene `CITED`-Zelle aus Issue #86).
2. **`CPHF(2)→CPHF(3)`-Stufe (`(4, 18, 4)=703`, `(4, 21, 5)=1.745`, `(4, 20, 7)=6.517` — Plätze #14, #8, #7):** Sehr geringe Verifikationszeit (`0,6–9,0 s`); ein modifizierter `CPHF(2)`-Plus-Repair- oder partieller `CPHF(3)`-Ansatz (bzw. `AGL(1,q)`-/lineare Coset-Suche auf `v=4, 5`) adressiert Sprünge von `2,0×` auf `2,7–2,8×`.
3. **Nicht-Primzahlpotenzen (`(4, 14..20, 10)` und `(4, 16..18, 12)` — Plätze #1, #2, #9, #11, #13):** Hohe absolute Zeilen-Sprünge (`+3.344` bis `+14.447`) auf `CITED`-Einträgen; ein `q=11`→`v=10`- bzw. `q=13`→`v=12`-Fuse auf Basis besserer `NEAR_BUSH`-Arrays (`v=11, 13`) koppelt Track A und Track B direkt (fremde Vorarbeit: Colbourn/Sherwood-CPHF & Symbol-Fusion).

---

## 5. Bonus-Prüfung A: `t = 3`, Nicht-`q+1`-Alphabete (`v in {15, 21, 22}`)

Alle drei Alphabete erfüllen `v - 1 in {14, 20, 21}` (keine Primzahlpotenzen), liegen also **strikt außerhalb** der `PGL(2,q)+CCL`-Bauart (Regel-7-Sperre unberührt). `derived.csv` liefert für `k <= 50` keine strikt besseren Schranken.

| `v` (`v^3`) | Dominante OA-Fuse-Basis (niedrige `k`) | Größte offene `CITED (get=none)`-Lücken (`dual <= 60 s`) | `N_eff` (`× v^3`) | Sprung `ΔN` | Gesch. Dual-Verif. | Aktuelle Konstruktion (`ca_frame`) |
| :---: | --- | --- | :---: | :---: | :---: | --- |
| **`15`** (`3.375`) | `OA(16^3)`-Fuse bis `k=18` (`4.087`, `1,21×`); `k=19` `VER` (`5.704`) | `k = 20` / `k = 21..22` / **`k = 23..36`** | `6.459` (`1,91×`) / `7.460` (`2,21×`) / **`7.550..7.657` (`2,24–2,27×`)** | `+755` / `+1.001` / `+90` | `1,7–11,3 s` | `OA-fuse⁴` / `PHF` / **`CK doubling`** |
| **`21`** (`9.261`) | `OA(23^3)`-Fuse² bis `k=24` (`12.140`, `1,31×`) | `k = 25..26` / `k = 27..28` / **`k = 29..40`** | `15.392..15.436` (`1,66×`) / `19.052..19.112` (`2,06×`) / **`22.210..22.381` (`2,40–2,42×`)** | `+3.252` / `+3.616` / `+3.098` | `8,1–46,1 s` | `OA-fuse⁴..⁶` / **`CK doubling`** |
| **`22`** (`10.648`) | `OA(23^3)`-Fuse bis `k=24` (`12.165`, `1,14×`, `file`) | `k = 25..26` / `k = 27..28` / **`k = 29..40`** | `15.517..15.533` (`1,46×`) / `19.327..19.376` (`1,82×`) / **`23.136..23.190` (`2,17–2,18×`)** | `+3.352` / `+3.794` / `+3.760` | `8,1–47,9 s` | `OA-fuse³..⁵` / **`CK doubling`** |

- **Bewertung:** Große `CITED`-Lücken liegen geschlossen ab `k = 20..36` (`v = 15`) sowie ab `k = 25..40` (`v = 21, 22`), durchgehend dual-verifizierbar in `< 48 s`. Anders als bei `v = q + 1` fehlt hier eine kleine scharf 3-transitive Gruppe (`|PSL(4,2)| = 20.160` auf 15 Punkten und `|M_22| = 443.520` auf 22 Punkten sind größer als `N_eff`), sodass primär **Symbol-Fusion über verbesserte `v = 16`- bzw. `v = 23/25`-Arrays**, **CPHF/PHF** oder **zyklische/Produkt-Konstruktionen** in Frage kommen.

---

## 6. Bonus-Prüfung B: `t = 5, v = 12, k = 6..16` (Mathieu-Gruppe `M_12`)

`M_12` wirkt scharf 5-transitiv auf 12 Symbolen (`|M_12| = 12·11·10·9·8 = 95.040` vs. `12^5 = 248.832`). Zerlegung von `{0..11}^5` in `M_12`-Orbits nach Anzahl verschiedener Symbole `m`:
- `m = 5` (`S(5,5) = 1` Muster): Orbitgröße **`95.040`** (`95.040` Tupel)
- `m = 4` (`S(5,4) = 10` Muster): Orbitgröße **`11.880`** (`118.800` Tupel)
- `m = 3` (`S(5,3) = 25` Muster): Orbitgröße **`1.320`** (`33.000` Tupel)
- `m = 2` (`S(5,2) = 15` Muster): Orbitgröße **`132`** (`1.980` Tupel)
- `m = 1` (`S(5,1) = 1` Muster): Orbitgröße **`12`** (`12` Tupel)

Exakte tabellarische Gegenüberstellung mit der unteren Schranke allein aus `5-sym` (`A_5 >= 1` für `k<=12`, `>= 2` für `k>=13`) + minimal benötigten `4-sym`-Startern `B_4_min` (über maximal balancierte 4-Symbol-Partition von `k`, noch **ohne** die zusätzlich nötigen `3/2/1-sym`-Zeilen von `>= 35.000`):

| `k` | `N_eff` (`083a093`) | `N_eff / 12^5` | `Tier / Get` | Konstruktion (`ca_frame`) | `C(k,5)·12^5` | Gesch. `ca / py` (s) | `M_12` Boden `5+4-sym` (`A_5, B_4`) | Spielraum `N_eff - Boden` | Nüchterne Machbarkeit `M_12` |
| :-: | :---: | :---: | :---: | --- | :---: | :---: | :---: | :---: | --- |
| `6` | `248.832` | `1,00×` | `VER / file` | `OA(12^5)` (`derive`) | `1,49M` | `0,1 / 0,5` | `273.240` (`1, 15`) | `−24.408` | **Arithmetisch ausgeschlossen** |
| `7` | `294.080` | `1,18×` | `CIT / none` | `Augment OA` | `5,23M` | `0,2 / 2,2` | `308.880` (`1, 18`) | `−14.800` | **Arithmetisch ausgeschlossen** |
| `8` | `318.386` | `1,28×` | `CIT / none` | `Augment OA` | `13,93M` | `0,5 / 6,4` | `308.880` (`1, 18`) | `+9.506` | **Ausgeschlossen** (mit `3/2/1-sym >= 35k` über `343k`) |
| `9` | `343.426` | `1,38×` | `CIT / none` | `Augment OA` | `31,35M` | `1,0 / 15,5` | `344.520` (`1, 21`) | `−1.094` | **Arithmetisch ausgeschlossen** |
| `10..12` | `366.175..370.873` | `1,47–1,49×` | `CIT / none` | `OA(13^5)`-Fuse (`NCK`) | `62,7M..197M` | `1,8–4,4 / 33–105` | `380.160..392.040` (`1, 24..25`) | `−13.985..−23.646` | **Arithmetisch ausgeschlossen** |
| `13..14` | `371.076..371.273` | `1,49×` | `CIT / none` | `OA(13^5)`-Fuse (`NCK`) | `320M..498M` | `6,4–8,9 / 171–266` | `498.960..510.840` (`2, 26..27`) | `−127.884..−139.567` | **Arithmetisch ausgeschlossen** |
| `15` | `527.205` | `2,12×` | `VER / file` | `postop` | `747M` | `17,3 / 565` | `510.840` (`2, 27`) | `+16.365` | **Praktisch ausgeschlossen** (`3/2/1-sym` > `+16k`; `py ~ 9 min`) |
| `16` | `713.888` | `2,87×` | `VER / file` | `postop` | `1,09G` | `31,2 / 1.114` | `510.840` (`2, 27`) | **`+203.048`** | Arithmetisch offen, aber **unpraktisch auf 2 vCPUs** (`~25 MB`-Datei, `py_verify ~ 18 min`) |

**Fazit Bonus B (`M_12`):** Für den gesamten Bereich `k = 6..15` ist eine naive `M_12`-Orbitkonstruktion durch das sehr enge `OA(13^5)`-Fuse-Plateau (`<= 371.273`) bzw. `k=15` (`527.205`) rechnerisch blockiert. Erst ab `k = 16` (`713.888`) entsteht theoretischer Spielraum, der jedoch unser 60-s-Dual-Verifikationsbudget massiv überschreitet (`~18 min` in `verify_independent.py`). **Keine Empfehlung als Phase-5-Track.**

---

## 7. Watch-Out / Vermeidungsliste (Phase 5)

- **`t = 4, v = 6, k <= 25`:** Vollständig durch 2026-Einträge (Sitjar/Bai/Smolen) gesättigt (`0` offene `CITED`-Zellen). Meiden.
- **`t = 5, v = 12, k = 6..15` (`M_12`):** Durch `4-sym`-Orbitkosten (`11.880`/Starter) arithmetisch gegen `OA(13^5)`-Fuse blockiert; ab `k = 16` außerhalb des 2-vCPU-Verifikationsbudgets. Meiden.
- **`t = 4, v = 14, k >= 18` & `t = 4, v = 12, k >= 19`:** `ca_verify` bleibt zwar unter `8 s`, aber `verify_independent.py` überschreitet `60 s` (`73–459 s`). Nur sekundär berücksichtigen.
- **Regel-7-Sperre (`t = 3`, `PGL(2,q)+CCL`):** Bis zum Prüfbericht zu `chrispbsmolen/ca-tools#88` strikt gesperrt.
