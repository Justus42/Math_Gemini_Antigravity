# Phase 9B Pilot: Hyperebenen-Büschel `CPHF(2; 2q+2, q, 6)` (`docs/phase9/CPHF_T6_PENCIL_LOG.md`)

- **Datum:** 2026-11-28 (UTC)
- **Branch:** `exp/phase9-cphf-t6-pencil` (Basis `main @ 0bcbe2b`)
- **Hardware:** `2 vCPUs` (`Intel Xeon @ 2.30 GHz`, AVX2, Linux x86_64)
- **Programme:**
  - C-Prüfer/Scanner: [`scripts/phase9_cphf_t6_pencil.c`](../../scripts/phase9_cphf_t6_pencil.c) (kompiliert mit `gcc -O3 -march=native -Wall -Wextra -pthread -lm`, 0 Warnungen)
  - Unabhängige Python-Referenz (`std`-only): [`scripts/phase9_cphf_t6_check.py`](../../scripts/phase9_cphf_t6_check.py)
- **Abgrenzung:** Rein lokaler Pilotlauf. Kein Abgleich mit `chrispbsmolen/ca-tools`, kein GitHub-Actions-Lauf, kein Merge nach `main`, keine Literatur- oder Neuheitsaussage.

---

## 1. Endliche Körper und Parametrisierung

Für $q \in \{5, 7, 8, 9\}$ wird $K = \mathbb{F}_{q^2} = \mathbb{F}_q[i]/(i^2 - p_1 i - p_0)$ in fester $\mathbb{F}_q$-Basis $\{1, i\}$ mit primitivem Element $\zeta \in K^*$ (Ordnung $q^2 - 1$) und Norm-1-Erzeuger $\eta = \zeta^{q-1}$ (Ordnung $q + 1$) verwendet:

| `q` | $\mathbb{F}_q$ | $K = \mathbb{F}_{q^2}$ | $\zeta$ | $\eta = \zeta^{q-1}$ | $k = 2q + 2$ | $\binom{k}{6}$ | $N_q(1) = q + 1 + \lfloor 2\sqrt{q} \rfloor$ |
|---:|---|---|---|---|---:|---:|---:|
| `5` | $\mathbb{F}_5$ | $i^2 = 2$ | `(2, 1)` | `(3, 3)` | `12` | `924` | `10` |
| `7` | $\mathbb{F}_7$ | $i^2 = 3$ | `(1, 1)` | `(5, 1)` | `16` | `8008` | `13` |
| `8` | $\mathbb{F}_2[x]/(x^3+x+1)$ | $i^2 = i + 1$ | `(2, 1)` | `(6, 4)` | `18` | `18564` | `14` |
| `9` | $\mathbb{F}_3[x]/(x^2+1)$ (`a0+3a1`) | $i^2 = 1 + x$ (`4`) | `(3, 1)` | `(7, 7)` | `20` | `38760` | `16` |

**Zeile 1 (`Sym^5`-Normalkurven):**
- Bahn A (`k = 0..q`, $w = \zeta^k$): `R1_A(k) = coords(w^5, w^(4+q), w^(3+2q))` $\in \mathbb{F}_q^6$.
- Bahn B (`k = 0..q`, Diagonal-Twist $(g_1, g_2, g_3) \in (K^*)^3$, normiert $g_3 = 1$): `R1_B(k) = coords(g1*w^5, g2*w^(4+q), g3*w^(3+2q))` $\in \mathbb{F}_q^6$.

**Zeile 2 (Hyperebenen-Büschel in `PG(5, q)`):**
- Bahn A in $H_1$ (`k = 0..q`, $u = \eta^k$): `R2_A(k) = (coords(u^2), coords(u), 1, 0)`.
- Bahn B in $H_2$ (`k = 0..q`, $u = \eta^{(m_2 k + d_2) \bmod (q+1)}$, $\gcd(m_2, q+1) = 1$): `R2_B(k) = (coords(alpha*u^2), coords(beta*u), 0, 1)`.

**Äquivalenzreduktion in Stufe 1 (ohne Einschränkung der Allgemeinheit):**
1. Für alle $(g_1, g_2, g_3, m_1, d_1, \mathrm{frob}_1, \alpha, \beta, m_2, d_2)$ lässt sich Spalten-Umnummerierung auf Bahn B nutzen, um $m_1 = 1$ zu setzen ($m_2 \leftarrow m_2 m_1^{-1} \bmod (q+1)$); Frobenius $w \mapsto w^q$ erfüllt $(\zeta^k)^q = (\zeta^{q+1})^k \zeta^{-k} \propto \zeta^{-k}$ (projektiv identisch zu $m_1 = -1 \equiv q \pmod{q+1}$).
2. Wegen $\gcd(3 + 2q, q + 1) = 1$ lässt sich $g_3$ durch Diagonal-Basiswechsel auf Zeile 1 (Bahn-A-Shift $+r$) auf $g_3 = 1$ normieren; der Gegen-Shift auf Zeile 2 Bahn A wird durch $\mathrm{diag}(\eta^{2r}, \eta^r, 1, 1)$ in $(\alpha, \beta)$ absorbiert. Ebenso absorbiert $(\alpha, \beta)$ jedes $d_2$ über $(\alpha \eta^{2 d_2}, \beta \eta^{d_2})$ und jedes $d_1$ über $(g_1, g_2, g_3)$.
3. Skalierung $(\alpha, \beta) \mapsto (\lambda \alpha, \lambda \beta)$ mit $\lambda \in \mathbb{F}_q^*$ ändert keinen 6x6-Rang von Zeile 2 (kompensiert durch Skalierung der letzten Koordinate $e_2$). Damit genügt $\alpha \in \{\zeta^0, \dots, \zeta^q\}$, $\beta \in K^*$, alle koprimen $m_2$.
4. Die Splits `(6,0)` und `(0,6)` haben in Zeile 1 stets Rang 6 (Grad-5-Normalkurven); `(5,1)` und `(1,5)` haben in Zeile 2 stets Rang 6 (Grad-4-Normalkurven in $H_1, H_2$). Alle Treffer wurden dennoch über sämtliche $\binom{k}{6}$ 6-Tupel voll geprüft.

---

## 2. Gate 0 (Pflichtprüfung vor dem Scan)

Befehl: `python3 scripts/phase9_cphf_t6_check.py --gate0 --c-bin /tmp/phase9_cphf_t6_pencil`

1. **Analytisches Beispiel `q = 5`, `g1 = (1,2)`, `g2 = (2,1)`, `alpha = (1,1)`, `beta = (2,1)` über $\mathbb{F}_5[i]/(i^2-2)$:**
   - Zeile 1 allein (`a = 0..6`): `dep1 = [0, 0, 72, 144, 60, 0, 0]` → exakt `0` abhängige `(6,0)`-, `(0,6)`-, `(5,1)`-, `(1,5)`-Tupel (**PASS**).
   - Zeile 2 allein (`a = 0..6`): `dep2 = [1, 0, 51, 96, 39, 0, 1]` → exakt `0` abhängige `(5,1)`-, `(1,5)`-Tupel und exakt `1` `(6,0)`- sowie `1` `(0,6)`-Tupel (**PASS**).
   - Doppelt abhängig: `both = [0, 0, 12, 42, 18, 0, 0]` (`sum = 72`).
2. **Gegenprüfung C vs. unabhängige Python-Referenz (Seed `20261128`):**
   - `q = 5`: Gate-0-Beispiel + `5` Zufallskonfigurationen (inkl. variierter `m1, d1, frob1, m2, d2`) → **`6/6` 100 % Übereinstimmung** in allen 7 Splits von `dep1`, `dep2`, `both`.
   - `q = 7`: `5` Zufallskonfigurationen (inkl. variierter `m1, d1, frob1, m2, d2`) → **`5/5` 100 % Übereinstimmung** in allen 7 Splits von `dep1`, `dep2`, `both`.
   - **Gate-0-Status: PASS (`11/11`)**.

---

## 3. Stufe 1: Vollständiger parametrischer Scan (`q in {5, 7, 8, 9}`)

Alle vier Körper wurden mit `2` Threads über den gesamten reduzierten Parameterraum **vollständig (EXHAUSTIVE)** durchgerechnet (`--timeout 85`, harter Shell-Cap `90 s`, kein Timeout).

| `q` | `k = 2q+2` | `n1` × `n2` (Paare) | Laufzeit | Durchsatz | `zero_hits` | `min_both` `(42 / 33 / 24)` | Split-Minima `(42, 33, 24)` | `best k_punc` vs. $N_q(1)$ | Best-Parameter `(g1, g2, alpha, beta, m2)` | Belegart |
|---:|---:|---:|---:|---:|---:|---|---|---:|---|---|
| `5` | `12` | `576 × 288 = 165.888` | `0,012 s` | `13,76 M/s` | **`916`** | **`0`** `(0 / 0 / 0)` | `(0, 0, 0)` | **`12 / 12`** (`> 10`) | `(0,1), (1,0), (2,1), (0,2), m2=1` | **Vollständig; `unc=0`-Treffer verifiziert** |
| `7` | `16` | `2.304 × 1.536 = 3.538.944` | `0,440 s` | `8,05 M/s` | **`4`** | **`0`** `(0 / 0 / 0)` | `(0, 0, 0)` | **`16 / 16`** (`> 13`) | `(0,4), (2,1), (1,1), (5,3), m2=1` | **Vollständig; `unc=0`-Treffer verifiziert** |
| `8` | `18` | `3.969 × 3.402 = 13.502.538` | `2,580 s` | `5,23 M/s` | `0` | `9` `(0 / 9 / 0)` | `(0, 0, 0)` | `14 / 18` (`= 14`) | `(2,4), (4,2), (0,6), (7,2), m2=1` | **Vollständig im parametrischen Raum; `unc=0` ausgeschlossen** |
| `9` | `20` | `6.400 × 3.200 = 20.480.000` | `8,437 s` | `2,43 M/s` | `0` | `30` `(0 / 30 / 0)` | `(0, 0, 0)` | `16 / 20` (`= 16`) | `(5,5), (8,3), (7,2), (8,8), m2=1` *(k_punc 16 bei `(1,0),(2,0),(0,4),(0,8), m2=1`, `both=40`)* | **Vollständig im parametrischen Raum; `unc=0` ausgeschlossen** |

**Strukturbefund Stufe 1:**
- Bei `q = 5` (`k = 12`) und `q = 7` (`k = 16`) liefert das $\mathbb{Z}_{q+1}$-invariante Hyperebenen-Büschel (`m2 = 1`) bereits **ohne Symmetriebrechung** vollständige `CPHF(2; 2q+2, q, 6)` mit `unc = 0` (`916` Treffer bei `q = 5`, exakt `4` Treffer bei `q = 7`). Bei `q = 7` erreicht `k = 16` direkt die volle Spaltenzahl `2q + 2 = 16` (Vergleichswert: Bai Genus-2 `k = 16`, Elliptisch `k = 13`).
- Bei `q = 8` (`k = 18`) verbleibt im Optimum genau **eine** $\mathbb{Z}_9$-Bahn aus `9` `(3,3)`-Tupeln (`A = [0,2,3], B = [0,1,3]` mod 9) bei `0` Konflikten in `(4,2)` und `(2,4)`; die exakte minimale Hitting-Set-Größe dieser 9-zyklischen 6-Hyperkanten ist `4`, also `k_punc = 14 = N_8(1)`.
- Bei `q = 9` (`k = 20`) verbleiben `30` `(3,3)`-Tupel (`3` $\mathbb{Z}_{10}$-Bahnen) bei `0` Konflikten in `(4,2)` und `(2,4)`; bestes `k_punc = 16 = N_9(1)` (erreicht bei `both = 40`, `del_mask = 0x8421`).

---

## 4. Stufe 2: Symmetriebrechung (`q = 8, k = 18` und `q = 9, k = 20`)

Da `q = 5` und `q = 7` bereits in Stufe 1 `min_both = 0` erreichten, lief Stufe 2 für `q = 8` (`k = 18`) und `q = 9` (`k = 20`), jeweils mit Warmstart aus dem Stufe-1-Minimum (`G = diag(g1, g2, 1)`, `M = diag(alpha, beta)`, `pi = id`) und zufälligen Restarts (`Seed = 20261128`, `--timeout 85`, harter Shell-Cap `90 s`, je `1` Thread parallel auf 2 vCPUs):

| `q` | `k` | Teil 2A (`pi in S_{q+1}`) | Teil 2B (`G in GL(6, F_q)`) | Teil 2C (`Alt (M in GL(4, F_q), pi) + G`) | Bestwert `min_both` | `k_punc` | Belegart |
|---:|---:|---|---|---|---|---:|---|
| `8` | `18` | `best=9`, `363.476` Evals (`3,045 s`) | `best=9`, `83` Restarts, `289.003` Evals (`6,7 k/s`, `43,061 s`) | `best=9`, `78` Runden, `154.334` M-Evals (`85,036 s` ges.) | `9` `(0 / 9 / 0)` | `14 / 18` | **Heuristische Suche erfolglos** (keine Verbesserung über Stufe 1; generische `GL`-Perturbationen brechen die `(4,2)/(2,4)`-Resonanz) |
| `9` | `20` | `best=30`, `369.251` Evals (`5,998 s`) | `best=30`, `70` Restarts, `124.398` Evals (`3,2 k/s`, `38,824 s`) | `best=30`, `57` Runden, `68.457` M-Evals (`85,085 s` ges.) | `30` `(0 / 30 / 0)` | `15 / 20` *(Stufe 1: `16 / 20`)* | **Heuristische Suche erfolglos** (keine Verbesserung über Stufe 1) |

---

## 5. Stufe 3: Direkte punktierte Zielsuche (`q = 8` und `q = 9`)

Kurzer Machbarkeits-Check (`15 s` je Ziel, `Seed = 20261128`, `30 s` Wall-Clock gesamt) mit direkter SA-Optimierung über `(G in GL(6, F_q), M in GL(4, F_q), pi)` auf eingeschränkten Spaltenteilmengen `kA + kB > N_q(1)`:

| `q` | Ziel `k (kA + kB)` | `min_dep2` | Restarts | Evals (Durchsatz) | Laufzeit | `best_both` `(42 / 33 / 24)` | Belegart |
|---:|---|---:|---:|---|---:|---|---|
| `8` | `15 (8 + 7)` | `378` | `100` | `372.729` (`24,8 k/s`) | `15,000 s` | `21` `(7 / 11 / 3)` | **Heuristische Suche erfolglos** |
| `8` | `16 (8 + 8)` | `638` | `56` | `207.897` (`13,8 k/s`) | `15,012 s` | `45` `(15 / 19 / 11)` | **Heuristische Suche erfolglos** |
| `9` | `17 (9 + 8)` | `977` | `40` | `148.121` (`9,9 k/s`) | `15,035 s` | `72` `(23 / 26 / 23)` | **Heuristische Suche erfolglos** |
| `9` | `18 (9 + 9)` | `1477` | `25` | `92.550` (`6,2 k/s`) | `15,000 s` | `120` `(37 / 50 / 33)` | **Heuristische Suche erfolglos** |

---

## 6. Verifizierte `unc = 0`-Treffer & Reproduzierbarkeit

Beide Treffer liegen unter [`data/phase9_cphf_t6/`](../../data/phase9_cphf_t6/) mit [`SHA256SUMS`](../../data/phase9_cphf_t6/SHA256SUMS) (`2/2 OK`) und wurden `2×` deterministisch byte-identisch (`cmp -s PASS`) erzeugt:

### 6.1 `CPHF(2; 12, 5, 6)` → `CA(31245; 6, 12, 5)` (Sherwood-Form)
- **Datei:** [`data/phase9_cphf_t6/cphf_q5_k12_stage1.json`](../../data/phase9_cphf_t6/cphf_q5_k12_stage1.json)
- **SHA-256 (CPHF):** `929e41e526d662c6d49fcc48092a8d688eae9402bc5a9f94b73dc1e516240012`
- **Parameter:** `g1 = (0, 1)`, `g2 = (1, 0)`, `g3 = (1, 0)`, `alpha = (2, 1)`, `beta = (0, 2)`, `m2 = 1`
- **Unabhängige Python-CPHF-Prüfung (`scripts/phase9_cphf_t6_check.py`, alle `924` 6-Tupel, `0,021 s`):**
  - `dep1 = [0, 6, 24, 74, 12, 6, 0]`, `dep2 = [1, 0, 33, 24, 33, 0, 1]`, **`both = [0, 0, 0, 0, 0, 0, 0]` (`unc = 0`)**.
  - Negativkontrolle (Spalte 0 auf Spalte 1 dupliziert): `unc = 210` (`FAIL`).
  - **Sherwood-Hyperebenen gefunden:** Zeile 1 `v1 = [1, 0, 0, 0, 1, 4]`, Zeile 2 `v2 = [1, 0, 0, 0, 0, 1]` → `N = 2·5^6 - 5 = 31.245` Zeilen.
- **Ausgerolltes Covering Array (`/tmp/phase9_cphf_t6/CA_31245_6_12_5.txt`, nicht eingecheckt):**
  - **SHA-256 (CA):** `531bb47fcd4852889500a87dee19cd10a5426347bab6a45ba32971aa29b7ebd6`
  - **Verifier 1 (`./verifiers/ca_verify`):** Positiv `Exit 0` (`0,33 s`, alle `924` Spaltenmengen decken alle `15.625` Tupel); Negativkontrolle (`sed '1s/0/1/'`) `Exit 1` (`0,33 s`, `357/924` Lücken).
  - **Verifier 2 (`python3 verifiers/verify_independent.py`):** Positiv `Exit 0` (`10,0965 s`, `14.437.500` Interaktionen); Negativkontrolle `Exit 1` (`8,9135 s`, `357/14.437.500` Lücken).
  - **Belegart:** Lokal dual-verifiziertes `CA(31245; 6, 12, 5)` (Drittprüfung, Literaturprüfung und Live-Tabellenvergleich gegen `ca-tools` stehen aus).

### 6.2 `CPHF(2; 16, 7, 6)` (Sherwood-Form: `N = 235.291`)
- **Datei:** [`data/phase9_cphf_t6/cphf_q7_k16_stage1.json`](../../data/phase9_cphf_t6/cphf_q7_k16_stage1.json)
- **SHA-256 (CPHF):** `907408aede54029d68055dec6adcb3016ebd41bfdf873236f54388b1a6cf97bb`
- **Parameter:** `g1 = (0, 4)`, `g2 = (2, 1)`, `g3 = (1, 0)`, `alpha = (1, 1)`, `beta = (5, 3)`, `m2 = 1`
- **Unabhängige Python-CPHF-Prüfung (`scripts/phase9_cphf_t6_check.py`, alle `8.008` 6-Tupel, `0,181 s`):**
  - `dep1 = [0, 72, 200, 232, 200, 72, 0]`, `dep2 = [28, 0, 240, 288, 240, 0, 28]`, **`both = [0, 0, 0, 0, 0, 0, 0]` (`unc = 0`)**.
  - Negativkontrolle (Spalte 0 auf Spalte 1 dupliziert): `unc = 1001` (`FAIL`).
  - **Sherwood-Hyperebenen gefunden:** Zeile 1 `v1 = [1, 0, 0, 0, 1, 4]`, Zeile 2 `v2 = [1, 0, 0, 0, 2, 0]` → `N = 2·7^6 - 7 = 235.291` Zeilen.
  - **Belegart:** CPHF-Matrizen in C und unabhängigem Python über alle `8.008` 6-Tupel verifiziert (`unc = 0`, `2×` byte-identisch); ausgerolltes `CA(235291; 6, 16, 7)` noch nicht über `verifiers/ca_verify` / `verify_independent.py` geprüft; Live-Tabellenvergleich und Literaturprüfung stehen aus.

---

## 7. Verifier-Integrität

- `sha256sum -c verifiers/SHA256SUMS`: `3/3 OK`
- `git diff main -- verifiers/`: leer
- `python3 verifiers/test_verifiers.py`: `23/23 PASS`
