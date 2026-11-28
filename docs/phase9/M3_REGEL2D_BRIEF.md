# Phase 9 / PR #54 — Regel-2d-Prüfmappe (`M_3(R_3)`, `k = q + 3`, `3 <= t <= q`)

- **Branch / Stand:** `exp/phase9-biaffine-3d` (Basis `159dfa4`, PR `#54`), Datum `2026-11-28`.
- **Zweck:** Selbsttragende Prüfliste für einen unabhängigen Prüfer-Chat / ein unbeteiligtes Drittmodell nach [`RULES.md`](../../RULES.md) Regel 2d. **Keine neuen Behauptungen, keine Ablage in `results/`, keine Außenwirkung; Regel 2c (Literaturprüfung) & Regel 2d (Drittprüfung) stehen aus.**
- **Verifier-Integrität (READ-ONLY):** `sha256sum -c verifiers/SHA256SUMS` `3/3 OK`, `git diff main -- verifiers/` leer, `python3 verifiers/test_verifiers.py` `23/23 PASS`, `data/phase9_m3/SHA256SUMS` `22/22 OK`.

---

## 1. Zu prüfende Aussagen (Checkliste für Regel 2d)

### A. [`M3_DETERMINISTIC_CONSTRUCTION_PROOF.md`](M3_DETERMINISTIC_CONSTRUCTION_PROOF.md) (`scripts/phase9_m3_lift.py`, `scripts/phase9_m3_construct.py`)
- [ ] **Satz 1 (Übersetzungssatz, §1.2):** `M_3^(t)(R_3)` ist genau dann ein `CA(|R_3| q^(t-3); t, q+3, q)`, wenn `R_3` die Bedingungen Typ 0–3 über `(D_1^(t), N_2^(t))` (`tspec`) erfüllt; `check_m3(full-bg3) = 0` (`D_1 = N_2 = F_q^2`) impliziert Gültigkeit für alle `3 <= t <= q` (inkl. Randfall `t = 3`, `g = 0`).
- [ ] **Lemma 1 (§1.3):** Körperunabhängige hinreichende Bedingung `suff = 0` (`(S0)`–`(S3)`: volle `x,y,z`-Punkte, volle `z`-Ebenen für Typ 1, volle `x`-Geraden für Typ 2, volle `(a,b,c)`-Tripel) impliziert `check_m3(full-bg3) = 0` für jede Primzahlpotenz `q`.
- [ ] **Satz 2 (§2.4):** Für jedes `q >= 3` und `1 <= e = q - r <= floor((q-1)/2)` ist `Phi` bijektiv auf `U` (auch für gerades `q`), `AP3(q, q-e) = q^2 - 3qe + kappa(q,e) - q + e` (`kappa = floor(5e^2/2)` ungerade / `ceil(5e^2/2)` gerade), `m_raw(q, e) = 2q^3 - q^2 e + kappa(q,e)q - q^2 + qe`, optimal bei `e* = floor((q+1)/5)` mit Asymptotik **`19/10 q^3 - 4/5 q^2 + O(q)`** (nicht `49/27`).
- [ ] **Satz 3 (§3):** Für jede Primzahlpotenz `q >= 5` und `1 <= e < (q-2)/2` liefert `build_m3_for_params` kollisionsfrei `suff = 0`; Kernpunkt ist die Hall-Bedingung (`deg(c) >= q - 2`, `deg(x) >= q - 2e`) für die `1P`-Bijektionen auf `z*`.
- [ ] **Satz 4 (§4.1):** Im balancierten Light+Heavy-`x`-Geraden-LP (`l=1/3, h=2/3`, Bonferroni 1. Ordnung) sind **`46/27`** (frei, 9-Term-Dual `y*`) und **`49/27`** (ohne `3P` in `LLL/LLH`, 5-Term-Dual) exakte rationale Optima.

### B. [`M3_46_27_IMPROVEMENT_REPORT.md`](M3_46_27_IMPROVEMENT_REPORT.md) (`scripts/phase9_m3_cyclic_opt.py`, `scripts/phase9_m3_search.c`)
- [ ] **`k`-Block-idempotent-freie PLS (§2.1):** Für `k | q` und idempotentes `L_k` gilt `m_raw(q, k) = (2 - 1/k + 2/k^2) q^3 - (1 - 1/k) q^2`; speziell `k = 4` ergibt **`15/8 q^3 - 3/4 q^2`** (`1,875 q^3 < 1,90 q^3`; `k = 5`: `47/25 q^3`).
- [ ] **`3P`-Splitting (§1.1, §2.1):** Ersetzen eines `3P`-Punktes an Spalte `x` (bei >= 1 ungespaltener Spalte `x'`) durch 3 passende `U`-Tripel auf derselben Zeile `(y, z)` erhält `suff = 0` und spart exakt `1` Punkt; erklärt `q = 9: m = 1319 < 1323 = 49/27 * 9^3` bei `0/243` Nicht-`x`-Paaren.
- [ ] **`B1_full` Nicht-Übertragbarkeit (§1.2):** Ersetzen des 2D-Baer-Gitters durch eine beliebige 2D-`M(R)`-Liste der Dichte `c_2` ergibt `(c_2 + 20/27) q^3 + O(q^2)`; mit Phase-8-Untergrenze `c_2 >= 91/68` folgt `>= 2,079 q^3 > 2 q^3` (keine Übertragung auf Primzahlen).
- [ ] **Korrekturvermerk zu §1.1:** Die dort gelisteten Aggregat-LP-Werte `LP_2P = 1885/1107` und `LP_2P_no3PLL = 143/81` wurden in Dokument C als Aggregat-Artefakte widerlegt.

### C. [`M3_H2PLHH_OBSTRUCTION_REPORT.md`](M3_H2PLHH_OBSTRUCTION_REPORT.md) (`scripts/phase9_m3_h2plhh.py`)
- [ ] **Obstruktion 1 (Zeilen-Vielfachheit auf `z*`, §2):** Auf jeder Zeile `y` von `z*` gilt `u_b + u_c + w >= h` (zyklisch, `h = 2/3`); das zeilen-gekoppelte Rational-LP liefert frei **`46/27` (`H_2P = 0`)** (widerlegt `1885/1107`), ohne `3P_LL` **`1879/1053`** (widerlegt `143/81`), und für `s = 1/3` **`49/27`**.
- [ ] **Obstruktion 2 (`HHH`-3-Zylinder-Überlappung, §2):** Deckelung der `H_1HH`-Quote auf `<= 1/2` hebt das zeilen-gekoppelte `no-3P-LL`-LP auf **`49/27`**.
- [ ] **Obstruktion 3 (Light-Plane-Starvation auf `z(a_0)`, §2):** Ein voller Block `H_2P_a(a_0; B_H, C_H)` erzwingt `pad(a_0) >= (1/3) q^2` auf `z(a_0)` -> LP kollabiert auf **`49/27` (`H_2P = 0`)**; verteiltes `H_2P_a` über Zeilen `y = u` von `z(a_0)` bricht `Typ 2` an `q - 1` von `q` Normalen (`q = 7..13` geprüft).

---

## 2. Explizite Liste aller offenen Beweispunkte (`[OFFEN]`)

| ID | Offener Punkt | Aktuelle Belegart | Was für einen allgemeinen Beweis fehlt |
| :---: | --- | --- | --- |
| **`P1`** (`[OFFEN 1]`) | **`exh(q) + pad_light(q) = o(q^3)`** (damit `m_det(q) < 2q^3 - q^2` bzw. `< 15/8 q^3` für alle `q >= 7`) | Numerisch belegt bis `q = 25` (`10/10` Primzahlpotenzen) | Kein analytischer Beweis für `exh(q) = o(q^3)` der deterministischen Greedy-Platzierung + Relokation auf `z*` (insb. für `q > 25` / `q > 31`). |
| **`P2`** (`[OFFEN 2]`) | **`pad_light = 0` ab `q >= 9`** | Numerisch `0` für `q in {5,7,9,11,13,16,17,19,23,25}` (`2` nur `q = 8`) | Analytische Zählschranke für verfügbare `U`-Tripel je Light-Symbol vs. ungematchte Light-Slots. |
| **`P3`** (`[OFFEN 3]`) | **Rundungs- & Randfälle (`q mod 3, 5, k`)** | Rechnerisch geprüft `q <= 25` (`construct_best`, `cyclic_opt`) | Formale Prüfung aller Restklassen bei `q mod k != 0` (`k`-Block-Greedy) und der Suchreduktion (`c_shift = (2q)//3`) ab `q > 13`. |
| **`P4`** (`[OFFEN 4]`) | **Numerische Prüfgrenzen** | `check_m3 = 0` exakt für `q <= 17`; `q in {19, 23, 25}` nur `suff = 0`; `q > 25` / `q > 31` ungeprüft | Exaktes `check_m3` für `q >= 19` nur unter Voraussetzung von Lemma 1; für `q > 25` keine Läufe. |
| **`P5`** | **Externe Governance (Regel 2c & 2d)** | Offen | Drittprüfung aller Texte & Arrays (Regel 2d) sowie Literaturprüfung (Regel 2c) vor jeder Ablage in `results/` oder Außenmeldung. |

---

## 3. Übersicht aller dual-verifizierten `M_3`-Bestwerte auf PR #54 (in `/tmp/phase9_m3/`, `10/10 PASS`)

Alle `10` Zellen stammen aus den `5` PAWS-Bestwert-Seeds `data/phase9_m3/R3_q*_fullbg3_opt_paws_m*.txt`, wurden `2×` byte-identisch geliftet, mit beiden unveränderten Verifiern (`ca_verify` + `verify_independent.py`) positiv (`rc = 0/0`) und negativ (`N - 1`, `rc = 1/1`) bestanden und liegen strikt unter `ca-tools @ b689967` (`2026-11-28T02:10:53Z`, `0` offene PRs) sowie unter dem `50 MiB`-Dateilimit. **Belegart: `Dual-Verify PASS (in /tmp)` / `Regel-2d offen`.**

| `q` | `k` | `t` | `m` | **`N`** | Größe (MiB) | `ca-tools@b689967` (`k'`) | **`-Delta`** | Array SHA-256 (Prefix, 16 Hex; voll im Log) | Seed SHA-256 (Prefix) |
|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `7` | `10` | `4` | `607` | **`4.249`** | `0,0810` | `4.459` (`15`) | **`-210`** | `5a1243a2bb01f3f5` | `662191d6347614de` |
| `7` | `10` | `5` | `607` | **`29.743`** | `0,5673` | `31.213` (`13`) | **`-1.470`** | `0ada022c05c540eb` | `662191d6347614de` |
| `7` | `10` | `6` | `607` | **`208.201`** | `3,9711` | `218.491` (`13`) | **`-10.290`** | `52f7706d45d4f459` | `662191d6347614de` |
| `8` | `11` | `4` | `914` | **`7.312`** | `0,1534` | `7.680` (`15`) | **`-368`**\* | `5fc8b4a2c45e2b4c` | `7b777bb8998834f5` |
| `8` | `11` | `5` | `914` | **`58.496`** | `1,2273` | `61.440` (`14`) | **`-2.944`** | `bfb0def6281d2945` | `7b777bb8998834f5` |
| `9` | `12` | `4` | `1.319` | **`11.871`** | `0,2717` | `12.393` (`17`) | **`-522`** | `774bff33af29ecfb` | `19ab9ff1b20eec11` |
| `9` | `12` | `5` | `1.319` | **`106.839`** | `2,4454` | `111.537` (`16`) | **`-4.698`** | `c8515e10248c1772` | `19ab9ff1b20eec11` |
| `11` | `14` | `4` | `2.417` | **`26.587`** | `0,7422` | `27.544` (`14`) | **`-957`** | `7ff2e3c747d8d637` | `cb3ceece0b67e84e` |
| `11` | `14` | `5` | `2.417` | **`292.457`** | `8,1646` | `307.461` (`18`) | **`-15.004`** | `d3d861ee8e6a8999` | `cb3ceece0b67e84e` |
| `13` | `16` | `4` | `4.026` | **`52.338`** | `1,7814` | `54.925` (`21`) | **`-2.587`** | `8db4c6c94cf87174` | `26f2d265008b19b2` |

*\*Hinweis zu `(4, 11, 8)`: Lokal in `results/t4_nearbush/` existiert `CA(7056; 4, 11, 8) < 7312` (Regel 3 beachten).*
- **Überholte frühere Dual-Verify-Zellen auf diesem Branch** (ersetzt durch obige PAWS-Bestwerte): `q=7 m=620` (`t=4,5,6`), `q=8 m=930` (`t=4,5`), `q=9 m=1324` (`t=4`), `q=11 m=2454` (`t=4`), `q=13 m=4088` (`t=4`).
- **Ungeliftete `check_m3=0`-Zellen (`q <= 13`, CI-Kandidaten):** `q=8 t=6` (`467.968`, ~`9,8 MiB`, `py ~2,5 min`/Lauf), `q=9 t=6` (`961.551`, ~`22,0 MiB`, `py ~10–12 min`/Lauf), `q=13 t=5` (`680.394`, ~`23,2 MiB`, `ca ~1 min`, `py ~25–30 min`/Lauf); `q=11 t=6` (`~94 MiB`) & `q=13 t=6` (`~301 MiB`) überschreiten `50 MiB`.

---

## 4. Repro-Befehle für den Prüfer (vollständige Hashes in [`M3_DETERMINISTISCH_LOG.md`](M3_DETERMINISTISCH_LOG.md) §6 & [`M3_46_27_IMPROVEMENT_REPORT.md`](M3_46_27_IMPROVEMENT_REPORT.md) §3)

```bash
sha256sum -c verifiers/SHA256SUMS && git diff main -- verifiers/ && python3 verifiers/test_verifiers.py
(cd data/phase9_m3 && sha256sum -c SHA256SUMS)
python3 scripts/phase9_m3_lift.py --q 11 --t 5 --mode full-bg3 --reps data/phase9_m3/R3_q11_fullbg3_opt_paws_m2417.txt --check-m3 --lift --out /tmp/CA_292457_5_14_11.txt
./verifiers/ca_verify /tmp/CA_292457_5_14_11.txt 5 11 2 && python3 verifiers/verify_independent.py /tmp/CA_292457_5_14_11.txt 5 11 -n 292457 -k 14
python3 scripts/phase9_m3_h2plhh.py --qs 7,8,9,11,13,16,17,19,23,25 --check-m3-max 13
```
