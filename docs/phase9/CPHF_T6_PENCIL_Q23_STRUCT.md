# Phase 9B Option A+: Algebraische Struktur der `3(q+1)/2`-Punktierung (`q = 13, 17, 19`) & Slice-Scans `q = 23, 29`

- **Datum:** 2026-11-28 (UTC)
- **Branch:** `exp/phase9-cphf-t6-pencil` (Fortsetzung ab Commit `5f6ee31`, PR `#55`)
- **Hardware:** `2 vCPUs` (`Intel Xeon @ 2.30 GHz`, AVX2, OpenMP, Linux x86_64)
- **Erweiterte Programme:**
  - OpenMP-Scanner [`scripts/phase9_t6_pencil_scan.c`](../../scripts/phase9_t6_pencil_scan.c) (erweitert auf `q in {23, 29}`, `MAX_Q=29, MAX_K=60, SHORT_WORDS=8`, 0 Warnungen; 1:1-Regressionsprüfung auf `q=17 sq-norm` identisch)
  - Eigenständiger C-CPHF-Vollprüfer [`scripts/phase9_cphf_t6_verify.c`](../../scripts/phase9_cphf_t6_verify.c) (`V_MAX_Q=29`, 0 Warnungen)
  - Python-Referenz [`scripts/phase9_cphf_t6_check.py`](../../scripts/phase9_cphf_t6_check.py) (erweitert um `q = 23` [$i^2=5, \zeta=(1,1)$] und `q = 29` [$i^2=2, \zeta=(1,4)$])
- **Abgrenzung:** Strikt lokal auf `exp/phase9-cphf-t6-pencil`. Keine Schreibvorgänge auf `ca-tools`, keine CA-Ausrollung, keine Änderungen an geschützten Pfaden.

---

## 1. AP 1: Exakte 1-Parameter-Reduktion & Struktur der `tau = (q+1)/2` gestrichenen Spalten (`q = 13, 17, 19`)

### 1.1 Exakte 1-Parameter-Familie (Befund über alle `q = 7..29`)

Ausnahmslos **alle** optimalen `inv`- und `sq-norm`-Konfigurationen bei `q in {7, 9, 11, 13, 17, 19, 23, 29}` — einschließlich `12/12` Ausreißern (`unc < 6.000`) unter `167.040` Paaren bei `q = 23` und `15/15` Ausreißern (`unc < 15.000`) unter `406.800` Paaren bei `q = 29` — liegen auf einer einzigen **1-Parameter-Kurve** mit ganzzahligem Parameter $t \in \{1, \dots, q\}$ (bzw. $r \equiv (3+2q)t \bmod (q+1)$, $1 \le r \le (q+1)/2$ bis auf Frobenius):

$$g_2 = \eta^t,\qquad g_1 = g_2^2 = \eta^{2t},\qquad c := \zeta^{(3+2q)t} \in K^* \setminus \mathbb{F}_q^*,\qquad \gamma := c^q,\qquad \alpha = \gamma \eta^{-2t},\qquad \beta = \gamma \eta^{-t}.$$

Nach der reinen Spalten-Umnummerierung $k \mapsto k + t \pmod{q+1}$ auf Bahn B kollabiert das 4-Parameter-Modell exakt zu:
- **Zeile 1:** $R_{1,B}'(k) = \mathrm{coords}\!\big(c \cdot (w_k^5,\; w_k^{4+q},\; w_k^{3+2q})\big)$ (`K`-Skalarmultiplikation um $c$ auf Bahn A; für jedes $k$ spannen $R_{1,A}(k), R_{1,B}'(k)$ dieselbe 2-dim. $\mathbb{F}_q$-Ebene $K \cdot v(k)$ auf).
- **Zeile 2:** $R_{2,B}'(k) = (\mathrm{coords}(c^q u_k^2),\; \mathrm{coords}(c^q u_k),\; 0,\; 1)$ (Frobenius-Konjugierte $\gamma = c^q \propto_{\mathbb{F}_q^*} c^{-1}$).
- **Norm-Parität:** Ungerades $r$ (bzw. $t$) entspricht exakt `inv` ($\mathrm{N}(\alpha)=\mathrm{N}(\beta)$ Nichtquadrat), gerades $r$ exakt `sq-norm` (Quadrat-Norm).

### 1.2 Algebraische Struktur der `tau = (q+1)/2`-Punktierungen (`q = 13, 17, 19`)

| `q` | `q mod 4` | `n = q+1` | 1-Param-`r` (`t`) | `unc` vor Punktierung `(42/33/24)` | Struktur der ungedeckten `Z_n`-Orbits (ausgerichtet `A, B-t`) | Explizite `tau = (q+1)/2`-Streichregel | Resultierendes `k = 3(q+1)/2` | Direkter Test `unc = 0` |
|---:|---:|---:|---|---|---|---|---:|---|
| `13` | `1` | `14` | `r = 6` (`t = 8`, `sq-norm`) | `84` `(0 / 84 / 0)` (`6` Orbits) | Jedes `(3,3)`-Tripel enthält sowohl gerade als auch ungerade Indizes in `A` **und** in `B-t` (`5/6` Orbits enthalten Antipodenpaar $\{x, x+7\}$) | `del A_even` (`7` Spalten in Block 1, `0` in Block 2) **oder** `del B_even` | `21 / 28` (`< Bai 22`) | **PASS (`unc = 0`)** |
| **`17`** | **`1`** | **`18`** | **`r = 4` (`t = 14`, `sq-norm`)** | **`198` `(0 / 198 / 0)`** (`11` Orbits) | Jedes `(3,3)`-Tripel enthält beide Paritäten in `A` **und** in `B-t` (`7/11` Orbits mit Antipodenpaar $\{x, x+9\}$; `0` einfarbige Tripel) | **`del A_even` (`[0,2,4,6,8,10,12,14,16]`, `9` Spalten in Block 1, `0` in Block 2)** oder `del B_even` | **`27 / 36` (`> Bai 26`)** | **PASS (`unc = 0`, `296.010` Tupel C+Python)** |
| `19` | `3` | `20` | `r = 10` (`t = 10`, `sq-norm`, `c = i`) | `360` `(40 / 280 / 40)` (`18` Orbits) | Alle `18/18` Orbits (`2` `(4,2)`, `14` `(3,3)`, `2` `(2,4)`) treffen alle `4` Restklassen `{0,1,2,3} mod 4` in `A ∪ (B-10)` | `del A%4==0` (`[0,4,8,12,16]`) **und** `del B%4==2` (`[2,6,10,14,18]`, d.h. `(B-10)%4==0`), `5 + 5 = 10` Spalten | `30 / 40` (`= Bai 30`) | **PASS (`unc = 0`, `593.775` Tupel C)** |

### 1.3 Direkter Hypothesentest der `3(q+1)/2`-Regeln auf `q = 23` und `q = 29` — **Widerlegt**

- **Direkter Test `del A_even` (und `del A%4==0 & B%4==sh` für `4 | n`) über alle $r \in \{1, \dots, q\}$ der 1-Parameter-Familie:**
  - `q = 23` (`n = 24`, Ziel `k = 36`): **`0` Treffer** (`del A_even` lässt mindestens `8` `(a1=1)`-Orbits bei `r = 11` übrig; alle `4` `mod-4`-Shifts scheitern).
  - `q = 29` (`n = 30`, `29 ≡ 1 mod 4`, Ziel `k = 45`): **`0` Treffer** (`del A_even` lässt mindestens `16` `(a1=1)`-Orbits bei `r = 11` bzw. `17` bei `r = 10` übrig; `(2,4)`-Defekte verschwinden ab `q = 23` nicht mehr).
- **Ursache (empirisch, Belegart `Beobachtung` + exakte Rechnung für `q = 23`):** Die Zahl der ungedeckten `Z_{q+1}`-Orbits im besten 1-Parameter-Punkt wächst überproportional (`q=7: 0`, `q=11: 1`, `q=13: 3/6`, `q=17: 7/11`, `q=19: 9/18`, `q=23: 15/23`, `q=29: 30/37`). Ab `q = 23` kollabieren `(4,2)`/`(2,4)` nicht mehr auf `0` (`pure33_cnt = 0` im gesamten `inv ∪ sq-norm`-Raum für `q = 23` und `q = 29`). Eine allgemeine `3(q+1)/2`-Konstruktion existiert in diesem Stage-1-Modell **nicht**.

---

## 2. AP 2: Benchmarks, Exhaustive Slice-Scans & Exaktes Hitting-Set (`q = 23` und `q = 29`)

### 2.1 Benchmarks (2 Threads, OpenMP, `OrbitTable`)

- **`q = 23` (`k_full = 48`):** `415.160` Orbits (`140` kurz, `ow = 6.485`), `n1 = 290 × n2 = 288 = 83.520` sym.-red. Paare je Norm-Slice (`165.888` roh), `init = 0,011 s`, `1` Build `4,26 ms`, Schätzung `2,79 s` (ohne DFS).
- **`q = 29` (`k_full = 60`):** `1.344.310` Orbits (`220` kurz, `ow = 21.004`), `n1 = 452 × n2 = 450 = 203.400` sym.-red. Paare je Norm-Slice (`405.000` roh), `init = 0,035 s`, `1` Build `14,88 ms`, Schätzung `15,99 s` (ohne DFS).

### 2.2 Vollständige Ergebnisse `q = 23` und `q = 29`

| `q` | Slice | Abdeckung (Paare) | Laufzeit (2T) | `avg_unc` | `min_unc` `(42/33/24)` | Best `tau` (Belegstatus) | `k_punc` | Vergleich `ca-tools @ b689967` |
|---:|---|---|---:|---:|---|---|---:|---|
| **`23`** | **`inv`** | **100 %** (`83.520` sym.) | `47,698 s` (`scan 2,74`, `hs 44,96`) | `20189,6` | **`360` `(48/264/48)`** (`r=5`: `g1=(8,10), g2=(19,16), a=(10,4), b=(4,6)`) | **`16` PROVEN EXACT** (DFS 0 Abbrüche: `r=5,1` exakt `16`; `r=11,7` `>=17`; Greedy `17`) | **`32 / 48`** (`= 4(q+1)/3`) | **`= Bai k = 32`** (`296.071.755`; `< k=33: 296.071.777`, `< k=34: 444.107.665`) |
| `23` | `sq-norm` | **100 %** (`83.520` sym.) | `49,529 s` (`scan 2,78`, `hs 46,75`) | `21530,3` | `552` `(72/408/72)` (`r=2`: `g1=(12,1), g2=(15,10), a=(1,3), b=(4,9)`) | **`17` PROVEN EXACT** (DFS 0 Abbrüche `>=17`; WalkSAT `tau=17`, Greedy `18`) | `31 / 48` | `< Bai k = 32` (`-1`) |
| `29` | `inv` | **100 %** (`203.400` sym.) | `16,532 s` (`--max-tau 0`) | `50516,9` | `900` `(180/540/180)` (`r=25`, `pure33_cnt=0`) | `<= 24` (Perioden-Coset `p=5`, `r=5,13,7`; Greedy `26`; `tau=15` widerlegt) | `36 / 60` (`45` nicht erreicht) | `v = 29` außerhalb `ca-tools @ b689967` (`t=6` max `v=25`) |
| `29` | `sq-norm` | **100 %** (`203.400` sym.) | `15,618 s` (`--max-tau 0`) | `52482,8` | `1110` `(150/810/150)` (`r=10`, `pure33_cnt=0`) | `<= 24` (Greedy `24`, Perioden-Coset `30`; `tau=15` widerlegt) | `36 / 60` (`45` nicht erreicht) | `v = 29` außerhalb `ca-tools @ b689967` |

**Wichtiges Detail zu `q = 23`:** Der exakte DFS-Prüfer (mit $\mathbb{Z}_{24}$-Symmetriebrechung, 0 Abbrüche bei `node_limit = 5M`) beweist `tau = 16` (`k = 32`) exakt für `r = 5` (`unc = 360`) und `r = 1` (`unc = 456`) sowie `tau >= 17` (`k <= 31`) für alle übrigen 1-Parameter-Ausreißer (`r = 11, 2, 7, 8`). Damit ist **`k >= 33` (insbesondere `k >= 34` und `k = 36`) im gesamten `inv ∪ sq-norm`-Teilraum bei `q = 23` ausgeschlossen** (für die 6 niedrigsten Ausreißer exakt bewiesen; alle übrigen `167.028` Paare haben `unc >= 1.224` bzw. `>= 9.968`).

---

## 3. AP 3: Unabhängige `C(k, 6)`-Vollprüfung & Read-only `ca-tools`-Abgleich (`v = 23, t = 6`)

### 3.1 Unabhängige C-Vollprüfung des Bestwerts `q = 23, k = 32` (`= Bai 32`)

Da `q = 23` das Ziel `k_punc >= 34` nicht erreicht (sondern Bai `k = 32` exakt einstellt), wurde die Matrix gemäß AP 3.1 **nicht** unter `data/phase9_cphf_t6/` abgelegt, sondern als Konsistenz- und Negativkontrolle unter `/tmp/phase9_q23_q29/` vollständig geprüft:
- **Konfiguration:** `q = 23`, `g1 = (8,10), g2 = (19,16), alpha = (10,4), beta = (4,6), m2 = 1` (`r = 5`), `del_A = [0,3,6,9,12,15,18,21]` (`0 mod 3`), `del_B = [2,5,8,11,14,17,20,23]` (`(B-5) ≡ 0 mod 3`), `k = 16 + 16 = 32`.
- **Unabhängiger C-Prüfer ([`scripts/phase9_cphf_t6_verify.c`](../../scripts/phase9_cphf_t6_verify.c), 2 Threads):**
  - Positiv (`k = 32`): **`906.192` 6-Tupel in `0,2011 s`, `unc = 0` (`PASS`)**, `dep1 = [0,2912,8736,10920,8736,2912,0]`, `dep2 = [8008,0,9184,11824,9184,0,8008]`, `both = [0,0,0,0,0,0,0]`, Sherwood-Hyperebenen `R1=[1,0,0,0,0,1]`, `R2=[1,0,0,0,0,0]` → `N = 2·23^6 - 23 = 296.071.755`.
  - Negativkontrolle (wieder hinzugenommene gestrichene Spalte `A[0]`, also `k = 33`): **`1.107.568` 6-Tupel in `0,2444 s`, `unc = 8` (`both = [0,0,1,6,1,0,0]`, `FAIL` erwartet)**; zudem Duplikatspalte `27.405 FAIL`, Nullspalte `169.911 FAIL`.
  - **Kein CA-Rollout** (`ca_verify` offen).

### 3.2 Read-only Live-Abgleich `chrispbsmolen/ca-tools @ b689967` (`t = 6, v = 23` & `v = 29`)

| `v` | `k` | `ca-tools @ b689967` (`ca_frame.csv` / `derived.csv`) | Quelle in `ca-tools` | Unser Stage-1-Bestwert (`2q^6 - q`) | Bewertung |
|---:|---:|---:|---|---|---|
| `23` | `32` | `296.071.755` | Bai Singer (`2·23^6 - 23`) | **`296.071.755`** (`k = 32`, `unc = 0` C-vollgeprüft) | Gleichstand mit Bai `k = 32` |
| `23` | `33` | `296.071.777` | Bai elliptischer Zwei-Block | nicht erreicht (`k <= 32` exakt bewiesen) | dominiert |
| `23` | `34` | `444.107.665` | WCS (`CPHF IPO 3`) | nicht erreicht | nicht erreicht |
| `23` | `36` | `488.281.245` | Bai elliptisch `q = 25` (`derived.csv` fuse) | nicht erreicht (`3(q+1)/2` widerlegt) | nicht erreicht |
| `29` | `40..45` | *(nicht in Tabelle)* | `ca-tools @ b689967` endet bei `v = 25` für `t = 6` | `k = 36 / 60` (`45` widerlegt) | außerhalb Tabelle |

---

## 4. Gesamtfazit Phase 9B Stage-1-Familie (`q = 5..29`)

1. **Verbleibende echte Verbesserungen unter `ca-tools @ b689967`:** **`(6, 20, 11)`** (`3.543.111` vs. `5.300.031`, `−1.756.920` / `−33,15 %`, [`cphf_q11_k20_punc.json`](../../data/phase9_cphf_t6/cphf_q11_k20_punc.json)) und **`(6, 27, 17)`** (`48.275.121` vs. `72.412.673`, `−24.137.552` / `−33,33 %`, [`cphf_q17_k27_punc.json`](../../data/phase9_cphf_t6/cphf_q17_k27_punc.json)), beide doppelt unabhängig (`C` + `Python`) über alle $\binom{k}{6}$ 6-Tupel vollgeprüft (`ca_verify`, Drittprüfung und Literaturprüfung offen).
2. **Kein allgemeiner `3(q+1)/2`-Satz im Stage-1-Modell:** Durch `q = 23` (exakt `k = 32 < 36`) und `q = 29` (`k = 36 < 45`) eindeutig widerlegt. Eine theoretische Ausarbeitung eines allgemeinen `3(q+1)/2`-Beweises entfällt damit; sinnvolle nächste Schritte sind Drittprüfung/Einreichungsform für `(6, 20, 11)` und `(6, 27, 17)` oder Wechsel des Forschungspfads (z. B. PR `#54` / modifizierte Zeile-2-Konstruktion).
