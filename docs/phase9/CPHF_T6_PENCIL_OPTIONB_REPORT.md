# Phase 9B Option B: Strukturanalyse (`q = 5, 7, 8, 9`) & Exhaustiver Stage-1-Scan + Hitting-Set-Punktierung (`q = 11, 13`)

- **Datum:** 2026-11-28 (UTC)
- **Branch:** `exp/phase9-cphf-t6-pencil` (Fortsetzung ab Commit `4ae0b37`, PR `#55`)
- **Hardware:** `2 vCPUs` (`Intel Xeon @ 2.30 GHz`, AVX2, OpenMP, Linux x86_64)
- **Skripte:**
  - Schneller OpenMP-C-Scanner + exaktes Iterative-Deepening-Hitting-Set: [`scripts/phase9_t6_pencil_scan.c`](../../scripts/phase9_t6_pencil_scan.c) (`q in {5, 7, 8, 9, 11, 13}`, kompiliert mit `gcc -O3 -march=native -fopenmp -Wall -Wextra -lm`, 0 Warnungen)
  - AP-1-Strukturanalyse (`std`-only): [`scripts/phase9_ap1_analyze.py`](../../scripts/phase9_ap1_analyze.py)
  - Unabhängige Python-CPHF-Vollprüfung (`std`-only): [`scripts/phase9_cphf_t6_check.py`](../../scripts/phase9_cphf_t6_check.py) (erweitert um `q = 11, 13`)
- **Abgrenzung:** Rein lokal auf `exp/phase9-cphf-t6-pencil`. Keine Außenwirkung auf `ca-tools`, keine CA-Ausrollung für `q = 11, 13`, keine Änderungen an geschützten Pfaden.

---

## 1. AP 1: Bestandsaufnahme, Invarianten & Fehlerdiagnose (`q = 5, 7, 8, 9`)

### 1.1 Übersichtstabelle AP 1

| `q` | `k_full` | `unc=0` Treffer (roh) | Symmetrie-Bahnen (Swap, `Gal(K/F_p)`, Shift) | `min_unc` `(42 / 33 / 24)` | Exaktes `min_tau` (Greedy) | `k_punc = k_full - min_tau` | Gestrichene Spalten (`del_mask`) | Belegart |
|---:|---:|---:|---:|---|---:|---:|---|---|
| `5` | `12` | `916` (`m2=1: 754`, `m2=5: 162`) | `229` (`169×4, 39×2, 6×12, 15×6`) | `0` `(0 / 0 / 0)` | `0` (`0`) | `12` (`> N_5(1)=10`) | `[]` (`0x0`) | Stage-1 exhaustiv (`0,011 s`); `CA(31245;6,12,5)` lokal dual-verifiziert |
| `7` | `16` | `4` (`m2=1: 4`) | **`2`** (`2×2`, geometrisch verschieden!) | `0` `(0 / 0 / 0)` | `0` (`0`) | `16` (`> N_7(1)=13`) | `[]` (`0x0`) | Stage-1 exhaustiv (`0,297 s`); CPHF vollgeprüft (`8.008` Tupel), `ca_verify` offen |
| `8` | `18` | `0` | n/a | `9` `(0 / 9 / 0)` | **`4`** (`4`) | `14` (`= N_8(1)=14`) | `[0, 1, 4, 5]` (`0x33`) | Stage-1 exhaustiv (`2,048 s`); punktiertes `k=14` CPHF-vollgeprüft (`3.003` Tupel) |
| `9` | `20` | `0` | n/a | `30` `(10 / 10 / 10)` *(auch `0/30/0`)* | **`4`** (`4`, bei `unc=40`) | `16` (`= N_9(1)=16`) | `[0, 5, 10, 15]` (`0x8421`) | Stage-1 exhaustiv (`6,742 s`); punktiertes `k=16` CPHF-vollgeprüft (`8.008` Tupel) |

*(Hinweis zu `q = 9`: `min_unc = 30` liefert nur `exact tau = 5` [`k_punc = 15`]; das kleinste exakte Hitting-Set `tau = 4` [`k_punc = 16`] entsteht erst bei `unc = 40 [10/20/10]` mit `g1=(1,0), g2=(2,0), alpha=(0,4), beta=(0,8), m2=1`.)*

### 1.2 Algebraische Invarianten der `unc = 0`-Treffer (`q = 5` und `q = 7`)

- **Feld-Erzeuger:**
  - `q = 5` ($i^2 = 2$): $\zeta = (2, 1)$ (`MinPoly X^2 - 4X + 2`, `Tr = 4`, `N = 2`, `ord = 24`, $\zeta^6 = 2$ `ord 4`, $\zeta^4 = \eta = (3, 3)$ `ord 6`).
  - `q = 7` ($i^2 = 3$): $\zeta = (1, 1)$ (`MinPoly X^2 - 2X + 5`, `Tr = 2`, `N = 5`, `ord = 48`, $\zeta^8 = 5$ `ord 6`, $\zeta^6 = \eta = (5, 1)$ `ord 8`).
- **`q = 5` (`916` Treffer, `229` Bahnen):**
  - **Strikte Norm-Invariante (`916 / 916`, 100 %):** Bei ausnahmslos allen `916` Treffern sind sowohl $\mathrm{N}(\alpha) \in \{2, 3\}$ als auch $\mathrm{N}(\beta) \in \{2, 3\}$ **Nichtquadrate** in $\mathbb{F}_5^*$ (`ord(alpha), ord(beta) in {8, 24}`); zudem liegt $\alpha / \beta^2$ in `0 / 916` Fällen in $\mathbb{F}_5^*$. In `704 / 916` Fällen gilt $\mathrm{N}(\alpha) = \mathrm{N}(\beta)$, in `140 / 916` Fällen $g_1, g_2 \in U$ (Norm `1`).
- **`q = 7` (`4` Treffer → exakt `2` geometrisch verschiedene Bahnen der Größe `2`):**
  - Alle `4` Treffer haben `m2 = 1`, Sherwood-Hyperebenen (`N = 235.291`), $g_1, g_2 \in U$ ($\mathrm{N}(g_1) = \mathrm{N}(g_2) = 1$, sodass Konjugation $z \mapsto z^7$ und Bahn-Tausch $z \mapsto z^{-1}$ identisch wirken → Bahnlänge `2` statt `4`), und identische Nichtquadrat-Norm $\mathrm{N}(\alpha) = \mathrm{N}(\beta) = 5 \notin (\mathbb{F}_7^*)^2$ (`ord(alpha) = ord(beta) = 48`, beide primitiv in $\mathbb{F}_{49}^*$; $\alpha/\beta^2$ hat Norm `3`, `ord = 48`):
    1. **Bahn #1 (Größe 2):** `g1 = (0, 3) = zeta^12` (`X^2 + 1`, `ord 4`), `g2 = (2, 6) = zeta^30` (`X^2 - 4X + 1`, `ord 8`), `alpha = (1, 6) = zeta^7`, `beta = (5, 4) = zeta^37` — sowie Konjugiertes `(0,4), (2,1), (1,1), (5,3)`. Hier gilt `dep1 = [0, 72, 200, 232, 200, 72, 0]` (`sum = 776`).
    2. **Bahn #2 (Größe 2):** `g1 = (2, 1) = zeta^18` (`X^2 - 4X + 1`, `ord 8`), `g2 = (2, 1) = zeta^18`, `alpha = (1, 1) = zeta^1`, `beta = (5, 3) = zeta^19` — sowie Konjugiertes `(2,6), (2,6), (1,6), (5,4)`. Hier gilt `dep1 = [0, 56, 152, 368, 152, 56, 0]` (`sum = 784`).
  - **Befund:** Die 4 Treffer bei `q = 7` teilen sich dieselbe Zeile-2-Konfiguration (`dep2 = 824`), entsprechen aber **zwei projektiv nicht-isomorphen Zeile-1-Konfigurationen** (`dep1 = 776` vs. `784`, `(3,3)`-Defekte `232` vs. `368`).

### 1.3 Fehlerdiagnose bei `q = 8` und `q = 9` — Prüfung der Unterkörper-/Primzahlpotenz-Hypothese

- **Spaltenhäufigkeit & Unterkörper-Test:**
  - `q = 8` (`min_unc = 9`, `both = [0,0,0,9,0,0,0]`, `m2 = 1`): Exakt eine $\mathbb{Z}_9$-Bahn `A = [0, 2, 3], B = [0, 1, 3] (mod 9)`. Alle `18` Spalten treten exakt `3×` auf (`freq_A = [3,...,3]`, `freq_B = [3,...,3]`). Kein Unterschied zwischen $\mathbb{F}_4$-Unterkörper-Indizes (`k % 3 == 0`: Mittel `3,00`) und Rest (`3,00`).
  - `q = 9` (`min_unc = 30`, `m2 = 1`): Alle `20` Spalten treten exakt `9×` auf (`freq_A = [9,...,9]`, `freq_B = [9,...,9]`; `k % 2 == 0` vs. `1`: `9,00` vs. `9,00`; `u in {+-1}`: `[9, 9]`). Auch bei `min_tau`-Sieger (`unc = 40`): exakt `12×` je Spalte.
- **Datenbefund zur Hypothese:**
  1. **Unterkörper-Konzentration widerlegt:** Die ungedeckten 6-Tupel bei `q = 8, 9` (`m2 = 1`) sind wegen der $\mathbb{Z}_{q+1}$-Invarianz exakt gleichverteilt über alle Spalten; es gibt keine Häufung auf $\mathbb{F}_2$-/$\mathbb{F}_4$-/$\mathbb{F}_3$-Fixpunkten.
  2. **Reiner Primzahlpotenz-Effekt widerlegt:** Auch die Primzahlen `q = 11` (`min_unc = 12`) und `q = 13` (`min_unc = 42`) haben im gesamten Stage-1-Raum `0` Lösungen mit `unc = 0`.
  3. **Tragende strukturelle Effekte (empirisch über alle 6 Körper `q = 5, 7, 8, 9, 11, 13`):**
     - **Dichteskalierung:** Zufälliger Überlapp $|D_1||D_2|/|\mathrm{crit}|$ wächst wie $O(q^4)$ (`q=8: 181,8`, `q=9: 352,5`, `q=11: ~1100`, `q=13: ~2400`). Die Resonanz `g1, g2 in U`, `N(alpha) = N(beta)` (Nichtquadrat bei ungeradem `q`), `m2 = 1` drückt den Überlapp um Faktor `10–100`, reicht aber ab `q >= 8` nicht mehr für `unc = 0`.
     - **Charakteristik-2-Besonderheit (`q = 8`):** In $\mathbb{F}_8^*$ existiert kein Nichtquadrat (`x -> x^2` bijektiv), sodass die Nichtquadrat-Normbedingung für $(\alpha, \beta)$ entfällt (`N(alpha) = N(beta) = 2` ist Quadrat). Dennoch entsteht nur eine einzelne 9er-Bahn.
     - **Restklasse `q mod 4` (empirische Beobachtung, kein Beweis):** Bei `q ≡ 3 mod 4` (`q = 7, 11`, `-1` Nichtquadrat, `4 | q+1`) kollabieren `(4,2)` und `(2,4)` vollständig auf `0` und lassen nur `0` (`q=7`) bzw. `1` (`q=11`, `unc = 12`) `(3,3)`-Bahn übrig; bei `q ≡ 1 mod 4` (`q = 9, 13`) verbleiben mindestens `3` Bahnen (`unc = 30` bzw. `42`).

---

## 2. AP 2: Benchmarks, Exhaustiver Stage-1-Scan & Hitting-Set-Punktierung (`q = 11, 13`)

### 2.1 Verifikation des schnellen Kerns & Benchmarks

- **1:1-Gegenprüfung (`phase9_t6_pencil_scan check` vs. unabhängiges `phase9_cphf_t6_check.py`):** `2/2` Zufallskonfigurationen je `q in {5, 7, 8, 9}` über alle $\binom{2q+2}{6}$ 6-Tupel → **0 Abweichungen** (`8/8 PASS`).
- **Symmetriereduktion (`C_2 × C_2` auf Zeile 1 + simultaner Shift für `m2 != 1`):** Auf `q = 5, 7, 8, 9` gegen unreduzierten Scan (`--no-sym`) geprüft → identische globale `min_unc`, `best_tau` und `k_punc` (`0` Abweichungen).
- **Vorab-Benchmarks (2 Threads, OpenMP):**
  - `q = 11`: `n1_sym = 3.662` (aus `14.400`), `n2(m2=1) = 1.440`, `n2(m2!=1) = 1.440` (`m2 in {5, 7, 11}`), `1` R1-Build `0,442 ms`, geschätzt `~4–9 s` exhaustiv.
  - `q = 13`: `n1_sym = 7.142` (aus `28.224`), `n2(m2=1) = 2.352`, `n2(m2!=1) = 1.680` (`m2 in {3, 5, 9, 11, 13}`), `1` R1-Build `1,015 ms`, geschätzt `~20–45 s` exhaustiv.

### 2.2 Ergebnisse AP 2 (`q = 11` und `q = 13` — beide 100 % EXHAUSTIV)

| `q` | `k_full` | Suchraum-Abdeckung (Paare) | Laufzeit (2 Threads) | `zero_hits` | `min_unc` `(42 / 33 / 24)` | Exaktes `min_tau` (Greedy) | `k_punc = k_full - min_tau` | Vergleich Bai (`N = 2q^6 - q`) | Belegstatus |
|---:|---:|---|---:|---:|---|---:|---:|---|---|
| **`11`** | `24` | **EXHAUSTIV** (`5.273.280` `m2=1` + `5.273.280` `m2!=1` = `10.546.560` sym.-red. Paare) | `8,650 s` (`r1 1,52`, `r2 0,60`, `pA 0,36`, `pB 3,35`, `hs 2,82`) | `0` | **`12`** `(0 / 12 / 0)` | **`4`** (`5`, `exact=1`; `tau<=3` über alle `2.024` Tripel widerlegt) | **`20 / 24`** | **> Bai `k = 19` (`+1` Spalte bei `N = 3.543.111`)** | **Stage-1 exhaustiv + CPHF-vollgeprüft (`38.760` Tupel, `2×` byte-identisch); `ca_verify` offen** |
| **`13`** | `28` | **EXHAUSTIV** (`16.797.984` `m2=1` + `11.998.560` `m2!=1` = `28.796.544` sym.-red. Paare) | `43,864 s` (`r1 6,93`, `r2 2,42`, `pA 2,74`, `pB 29,25`, `hs 2,52`) | `0` | `42` `(14 / 14 / 14)` | **`7`** (`8`, `exact=1`; `tau<=6` für alle `250` Top-Kandidaten bis `unc=1092` widerlegt) | `21 / 28` | `< Bai k = 22` (`-1` Spalte bei `N = 9.653.605`) | **Stage-1 exhaustiv + CPHF-vollgeprüft (`54.264` Tupel, `2×` byte-identisch); `ca_verify` offen** |

**Ergebnis nach `m2`-Multiplikator (`min_unc`):**
- `q = 11`: `m2 = 1`: `12 (0/12/0)` | `m2 = 5`: `504` | `m2 = 7`: `480` | `m2 = 11`: `612`.
- `q = 13`: `m2 = 1`: `42 (14/14/14)` | `m2 = 3`: `1286` | `m2 = 5`: `1300` | `m2 = 9`: `1308` | `m2 = 11`: `1270` | `m2 = 13`: `1266`.

---

## 3. AP 3: Unabhängige CPHF-Vollprüfung des Treffers `q = 11, k = 20` (> Bai `k = 19`)

### 3.1 Treffer `CPHF(2; 20, 11, 6)` (`N = 3.543.111`)
- **Datei:** [`data/phase9_cphf_t6/cphf_q11_k20_punc.json`](../../data/phase9_cphf_t6/cphf_q11_k20_punc.json)
- **SHA-256:** `b5b9bfa5c40f027a545b248f58d78e9de160c110cc1f49d240c0e11006ee0852` (`2×` byte-identisch, `cmp -s PASS`)
- **Konstruktionsparameter** über $K = \mathbb{F}_{11}[i]/(i^2 - 2)$, $\zeta = (2, 1)$, $\eta = (3, 9)$:
  - `g1 = (6, 1)` (`N = 1`, `ord = 6`), `g2 = (3, 2)` (`N = 1`, `ord = 12`), `g3 = (1, 0)`
  - `alpha = (5, 2)` (`N = 6` Nichtquadrat, `ord = 40`), `beta = (1, 5)` (`N = 6` Nichtquadrat, `ord = 120`), `m2 = 1`
  - Vollmodell (`k = 24`): exakt `12` ungedeckte 6-Tupel (`A = [0, 3, 4], B = [0, 1, 4]` mod 12).
  - **Entfernte Spalten (`tau = 4`, `del_mask = 0xa0005`):** `[0, 2, 17, 19]` (Bahn A `{0, 2}` + Bahn B `{5, 7}` → exakte Partition der `12` Hyperkanten in `4 × 3` disjunkte Kanten; `kA = 10, kB = 10, k = 20`).
- **Unabhängige Python-Vollprüfung (`scripts/phase9_cphf_t6_check.py`, alle $\binom{20}{6} = 38.760$ 6-Tupel, `0,938 s`):**
  - `dep1 = [0, 215, 760, 870, 760, 215, 0]`, `dep2 = [210, 0, 778, 936, 778, 0, 210]`, **`both = [0, 0, 0, 0, 0, 0, 0]` (`unc = 0`)**.
  - Negativkontrolle (Spalte 0 auf Spalte 1 dupliziert): `unc = 3.060` (`FAIL`).
  - **Sherwood-Hyperebenen:** Zeile 1 `v1 = [1, 0, 0, 0, 0, 1]`, Zeile 2 `v2 = [1, 0, 0, 0, 0, 0]` → **`N = 2·11^6 - 11 = 3.543.111`**.
  - **Belegstatus:** `CPHF-vollgeprüft (C + unabhängiges Python), ca_verify offen` (kein CA-Rollout erzeugt).

### 3.2 Referenz-Punktierung `CPHF(2; 21, 13, 6)` (`< Bai k = 22`)
- **Datei:** [`data/phase9_cphf_t6/cphf_q13_k21_punc.json`](../../data/phase9_cphf_t6/cphf_q13_k21_punc.json) (`SHA-256: ff3350cf…`, `2×` byte-identisch).
- Parameter: `g1 = (10, 2)`, `g2 = (8, 5)`, `alpha = (11, 8)`, `beta = (12, 2)`, `m2 = 1`; `unc = 42 (14/14/14)`, entfernte Spalten `[0, 4, 10, 14, 15, 21, 25]` (`tau = 7`, `del_mask = 0x220c411`, `kA = 11, kB = 10, k = 21`).
- Unabhängige Python-Vollprüfung über alle $\binom{21}{6} = 54.264$ 6-Tupel (`1,301 s`): `unc = 0`, Negativkontrolle `unc = 3.876 FAIL`, Sherwood `N = 9.653.605`.

---

## 4. Empfehlung für den nächsten Schritt

1. **Priorität 1 (`q ≡ 3 mod 4` Resonanz-Scan auf `q = 19, 23` eingeschränkt auf den AP-1-Invarianten-Teilraum):** Da `q = 7 (unc=0, k=16)` und `q = 11 (unc=12, tau=4, k=20 > Bai 19)` beide `q ≡ 3 mod 4`, `m2 = 1`, `g1, g2 in U`, `N(alpha) = N(beta)` (Nichtquadrat) erfüllen, reduziert diese Invariante den Suchraum von $O(q^6)$ auf $O(q^3)$ (`(q+1)^2` für `(g1,g2) in U^2` × `(q+1)^2` für `(alpha, beta)` gleicher Norm), sodass ein gezielter Scan für `q = 19` (`k_full = 40`, `q ≡ 3 mod 4`) und `q = 17` (`k_full = 36`, `q ≡ 1 mod 4`) in Sekunden prüfbar ist.
2. **Priorität 2 (Tabellenabgleich & Freigabe):** Nach Freigabe Live-Abgleich von `(6, 12, 5)` (`31.245`), `(6, 16, 7)` (`235.291`) und `(6, 20, 11)` (`3.543.111`) gegen `chrispbsmolen/ca-tools` sowie CA-Rollout + `ca_verify` zunächst für `q = 7` (`235.291` Zeilen).
