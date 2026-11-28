# Phase 9B Option 1+: Invarianten-Validierung (`q = 5..13`), Slice-Scan `q = 19, 17` & Live-`ca-tools`-Abgleich (`t = 6`)

- **Datum:** 2026-11-28 (UTC)
- **Branch:** `exp/phase9-cphf-t6-pencil` (Fortsetzung ab Commit `13ba09d`, PR `#55`)
- **Hardware:** `2 vCPUs` (`Intel Xeon @ 2.30 GHz`, AVX2, OpenMP, Linux x86_64)
- **Programme:**
  - OpenMP-C-Scanner mit `OrbitTable`, `--slice inv|sq-norm|diff-norm|non-u`, `ctrl-m2ne1` und 64-Bit-Exact-Hitting-Set (mit `Z_{q+1}`-Symmetriebrechung & Unit-Propagation): [`scripts/phase9_t6_pencil_scan.c`](../../scripts/phase9_t6_pencil_scan.c) (`gcc -O3 -march=native -fopenmp -Wall -Wextra`, 0 Warnungen)
  - Eigenständiger unabhängiger C-CPHF-Vollprüfer (0 geteilter Code mit Scanner): [`scripts/phase9_cphf_t6_verify.c`](../../scripts/phase9_cphf_t6_verify.c) (`gcc -O3 -fopenmp -Wall -Wextra`, 0 Warnungen)
  - Unabhängige Python-Referenzprüfung (`std`-only, erweitert um `q = 17, 19`): [`scripts/phase9_cphf_t6_check.py`](../../scripts/phase9_cphf_t6_check.py)
- **Abgrenzung:** Strikt lokal auf `exp/phase9-cphf-t6-pencil`. Live-Abgleich gegen `chrispbsmolen/ca-tools` ausschließlich lesend (`gh api`, 0 Schreibvorgänge, 0 Außenwirkung). Keine CA-Ausrollung für `q = 7, 11, 17, 19`; `ca_verify` bleibt für diese Zellen offen.

---

## 1. AP 1: Parameterdefinition & Validierung des Invarianten-Teilraums (`q = 5..13`)

### 1.1 Exakte Parameterdefinition im C-Scanner

Sei $K = \mathbb{F}_{q^2} = \mathbb{F}_q[i]$ mit fester $\mathbb{F}_q$-Basis $\{1, i\}$ (Koordinatenabbildung $\mathrm{coords}(a + b i) = (a, b) \in \mathbb{F}_q^2$), $\zeta \in K^*$ ein primitives Element (Ordnung $q^2 - 1$), $\eta := \zeta^{q-1} \in U := \{u \in K^* : \mathrm{N}_{K/\mathbb{F}_q}(u) = u^{q+1} = 1\}$ (Ordnung $q + 1$) und $w_k := \zeta^k$, $u_k := \eta^k$ für $k \in \{0, \dots, q\}$:

- **Zeile 1 (`Sym^5`-Normalkurven-Paar, Parameter $g_1, g_2 \in K^*$, Normierung $g_3 = 1$):**
  - Bahn A ($k = 0 \dots q$): $R_{1,A}(k) = \mathrm{coords}(w_k^5,\; w_k^{4+q},\; w_k^{3+2q}) \in \mathbb{F}_q^6$.
  - Bahn B ($k = 0 \dots q$): $R_{1,B}(k) = \mathrm{coords}(g_1 w_k^5,\; g_2 w_k^{4+q},\; w_k^{3+2q}) \in \mathbb{F}_q^6$.
- **Zeile 2 (Hyperebenen-Büschel in $\mathrm{PG}(5, q)$, Parameter $\alpha, \beta \in K^*$, Multiplikator $m_2 \in (\mathbb{Z}/(q+1)\mathbb{Z})^*$):**
  - Bahn A in $H_1$ ($k = 0 \dots q$): $R_{2,A}(k) = (\mathrm{coords}(u_k^2),\; \mathrm{coords}(u_k),\; 1,\; 0) \in \mathbb{F}_q^6$.
  - Bahn B in $H_2$ ($k = 0 \dots q$, $v_k := \eta^{m_2 k \bmod (q+1)}$): $R_{2,B}(k) = (\mathrm{coords}(\alpha v_k^2),\; \mathrm{coords}(\beta v_k),\; 0,\; 1) \in \mathbb{F}_q^6$.
- **Normierung & Teilräume (`m2 = 1`):** Wegen simultaner Skalierung auf Bahn B wird $\alpha$ bis auf $\mathbb{F}_q^*$-Skalar auf Coset-Vertreter $\zeta^r$ ($r \in \{0, \dots, q\}$) reduziert; die $\mathbb{Z}_{q+1}$-Schift- und $C_2 \times C_2$-Symmetrie (Bahn-Tausch + Frobenius) halbiert bzw. viertelt den Suchraum exakt ohne Verlust.
  - **`inv` ($S_{\mathrm{inv}}$):** $g_1, g_2 \in U$, $\mathrm{N}(\alpha) = \mathrm{N}(\beta) \notin (\mathbb{F}_q^*)^2$ (Nichtquadrat-Norm bei ungeradem $q$; für $q = 8$ entfällt Nichtquadrat), $m_2 = 1$.
  - **`sq-norm` ($S_{\mathrm{sq}}$):** $g_1, g_2 \in U$, $\mathrm{N}(\alpha) = \mathrm{N}(\beta) \in (\mathbb{F}_q^*)^2$ (Quadrat-Norm), $m_2 = 1$.

### 1.2 Validierung auf exhaustiven Daten (`q = 5, 7, 8, 9, 11, 13`)

| `q` | `q mod 4` | `k_full` | Exhaustiv: `min_unc` `(42/33/24)` | Exhaustiv: exaktes `min_tau` (`k_punc`) | `inv` ($S_{\mathrm{inv}}$): `min_unc` / `min_tau` (`k_punc`) | `sq-norm` ($S_{\mathrm{sq}}$): `min_unc` / `min_tau` (`k_punc`) | Anteil `unc=0` bzw. Best-`tau` in `S_inv` |
|---:|---:|---:|---|---|---|---|---|
| `5` | `1` | `12` | `0` `(0/0/0)` | `0` (`12`) | `0` `(0/0/0)` / `0` (`12`) | `6` `(0/6/0)` / `2` (`10`) | `78 / 916` `unc=0` in `S_inv` (`39` sym.-red. Paare) |
| `7` | `3` | `16` | `0` `(0/0/0)` | `0` (`16`) | `0` `(0/0/0)` / `0` (`16`) | `24` `(0/24/0)` / `4` (`12`) | **`4 / 4` (100 %)** `unc=0` in `S_inv`; außerhalb `min_unc=24, tau=4` |
| `8` | `0` (char 2) | `18` | `9` `(0/9/0)` | `4` (`14`) | `9` `(0/9/0)` / `4` (`14`) *(alle gleichen Normen)* | *(identisch in char 2)* | Best-`unc` & Best-`tau` in `g1,g2 in U, N(a)=N(b), m2=1`; außerhalb `min_unc=66, tau=5` |
| `9` | `1` | `20` | `30` `(10/10/10)` | `4` (`16`, bei `unc=40`) | `30` `(10/10/10)` / **`4`** (`16`) | `30` `(0/30/0)` / `5` (`15`) | Best-`tau=4` in `S_inv`; außerhalb `min_unc=30, min_tau=5` |
| `11` | `3` | `24` | `12` `(0/12/0)` | **`4`** (`20 > Bai 19`) | `12` `(0/12/0)` / **`4`** (`20`) | `72` `(0/72/0)` / `6` (`18`) | Best-`unc=12` & Best-`tau=4` in `S_inv`; außerhalb `min_unc=72, min_tau=6` |
| `13` | `1` | `28` | `42` `(14/14/14)` | `7` (`21 < Bai 22`) | `42` `(14/14/14)` / **`7`** (`21`) | `84` `(0/84/0)` / **`7`** (`21`) | Best-`tau=7` sowohl in `S_inv` als auch in `S_sq` (Gleichstand!) |

**Befund AP 1:** Für `q in {5, 7, 8, 9, 11, 13}` enthält $S_{\mathrm{inv}}$ stets den global besten `min_unc`- und `min_tau`-Wert des gesamten exhaustiven Stage-1-Raums. Bemerkenswert ist bereits bei `q = 13` der Gleichstand in `min_tau = 7` zwischen $S_{\mathrm{inv}}$ (`unc = 42 [14/14/14]`) und $S_{\mathrm{sq}}$ (`unc = 84 [0/84/0]`, reines `(3,3)`-Spektrum!).

---

## 2. AP 2: Benchmarks, Slice-Scans & Anti-Tunnelblick-Kontrollen (`q = 19` und `q = 17`)

### 2.1 Verifikation des erweiterten Scanners & Benchmarks

- **1:1-Gegenprüfung (`phase9_t6_pencil_scan scan --slice inv` vs. exhaustiver Option-B-Kern):**
  - `q = 7`: `min_unc = 0, zero_hits = 2 (sym)` (`0,002 s`), `0` Abweichungen.
  - `q = 11`: `min_unc = 12 (0/12/0), exact min_tau = 4, k_punc = 20` (`0,166 s`), `0` Abweichungen.
  - `q = 13`: `min_unc = 42 (14/14/14), exact min_tau = 7, k_punc = 21` (`0,230 s`), `0` Abweichungen.
- **Vorab-Benchmarks (2 Threads, OpenMP, `OrbitTable`):**
  - `q = 19` ($i^2 = 2$, $\zeta = (2,1)$, $\eta = (3,17)$, `k_full = 40`): `157.080` $\mathbb{Z}_{20}$-Orbits (`90` kurze Orbits, `ow = 2.454` `uint64_t`-Wörter); `n1 = 202 × n2 = 200 = 40.400` sym.-red. Paare je Norm-Slice (`80.000` roh); `1` Build `1,73 ms`, Gesamtscan `~4 s`.
  - `q = 17` ($i^2 = 3$, $\zeta = (3,1)$, $\eta = (2,16)$, `k_full = 36`): `89.052` $\mathbb{Z}_{18}$-Orbits (`78` kurze Orbits, `ow = 1.392` `uint64_t`-Wörter); `n1 = 164 × n2 = 162 = 26.568` sym.-red. Paare je Norm-Slice (`52.488` roh); `1` Build `1,01 ms`, Gesamtscan `~4 s`.

### 2.2 Vollständige Ergebnisse `q = 19` (`19 ≡ 3 mod 4`) und `q = 17` (`17 ≡ 1 mod 4`)

*(Alle `inv`- und `sq-norm`-Scans sind **100 % exhaustiv** über ihren jeweiligen Slice; `diff-norm`, `non-u` und `ctrl-m2ne1` sind deterministische Anti-Tunnelblick-Kontroll-Samples. Hitting-Set-Obergrenze `--max-tau 11`, exakte `Z_{q+1}`-Symmetriebrechung.)*

| `q` | Slice / Kontrolle | Abdeckung (Paare) | Laufzeit | `avg_unc` | `min_unc` `(42/33/24)` | Best `tau` (`exact` / `greedy`) | `k_punc` | Vergleich Bai (`N = 2q^6 - q`) | Belegart |
|---:|---|---|---:|---:|---|---|---:|---|---|
| `19` | `inv` ($S_{\mathrm{inv}}$) | **100 %** (`40.400` sym.) | `4,022 s` | `9482,2` | `180` `(40/100/40)` | `12` (`exact=1`, `gr=12`, bei `unc=240`) | `28 / 40` | `< Bai 30` (`-2`) | Slice exhaustiv, exaktes `min_tau` |
| `19` | **`sq-norm` ($S_{\mathrm{sq}}$)** | **100 %** (`40.400` sym.) | `4,553 s` | `10399,8` | `360` `(40/280/40)` | **`10`** (`exact=1`, `gr=14`) | **`30 / 40`** | **`= Bai 30`** (`N = 94.091.743`) | Slice exhaustiv + unabhängige `C(30,6)`-Vollprüfung |
| `19` | `diff-norm` (Kontrolle) | Sample (`40.400` Paare) | `3,619 s` | `9965,9` | `6700` `(2120/3280/1680)` | `18` (`exact=0`, `gr=18`) | `22 / 40` | `< Bai 30` (`-8`) | Kontroll-Sample |
| `19` | `non-u` (Kontrolle) | Sample (`20.000` Paare) | `3,494 s` | `8907,2` | `7050` `(2150/2820/2080)` | `19` (`exact=0`, `gr=19`) | `21 / 40` | `< Bai 30` (`-9`) | Kontroll-Sample |
| `19` | `ctrl-m2ne1` (`m2=3,19`) | `100` Paare × `20k` MC | `< 2 s` | `~9700` | `est ~5182` | n/a | n/a | deutlich schlechter | MC-Kontrolle |
| `17` | `inv` ($S_{\mathrm{inv}}$) | **100 %** (`26.568` sym.) | `4,127 s` | `6090,9` | `126` `(18/90/18)` | `11` (`exact=1`, `gr=12`) | `25 / 36` | `< Bai 26` (`-1`) | Slice exhaustiv, exaktes `min_tau` |
| **`17`** | **`sq-norm` ($S_{\mathrm{sq}}$)** | **100 %** (`26.568` sym.) | **`4,205 s`** | `6774,2` | **`198` `(0/198/0)`** | **`9`** (`exact=1`, `gr=9`) | **`27 / 36`** | **`> Bai 26` (`+1` Spalte, `N = 48.275.121`)** | **Slice exhaustiv + doppelt unabhängig `C(27,6)`-vollgeprüft (C + Python); `ca_verify` offen** |
| `17` | `diff-norm` (Kontrolle) | Sample (`32.800` Paare) | `4,293 s` | `6405,1` | `4122` `(1098/1674/1350)` | `16` (`exact=0`, `gr=16`) | `20 / 36` | `< Bai 26` (`-6`) | Kontroll-Sample |
| `17` | `non-u` (Kontrolle) | Sample (`16.200` Paare) | `4,141 s` | `5676,6` | `4212` `(1170/1728/1314)` | `16` (`exact=0`, `gr=16`) | `20 / 36` | `< Bai 26` (`-6`) | Kontroll-Sample |
| `17` | `ctrl-m2ne1` (`m2=5,17`) | `100` Paare × `20k` MC | `< 2 s` | `~8900` | `est ~4166` | n/a | n/a | deutlich schlechter | MC-Kontrolle |

### 2.3 Zentrale Befunde aus AP 2 (Beobachtung, kein Beweis)

1. **Anti-Tunnelblick-Kontrolle `sq-norm` übertrifft den engen `inv`-Slice bei beiden Körpern (`q = 17` und `q = 19`) um jeweils `+2` Spalten:**
   - Die Nichtquadrat-Bedingung (`inv`) minimiert zwar `min_unc` (`126` bei `q=17`, `180` bei `q=19`), aber der **Quadrat-Norm-Gleichnorm-Slice `sq-norm`** ($g_1, g_2 \in U$, $\mathrm{N}(\alpha) = \mathrm{N}(\beta) \in (\mathbb{F}_q^*)^2$, $m_2 = 1$) liefert durch regulärere Überlappungs-Hypergraphen strikt kleinere Hitting-Sets (`tau = 9` statt `11` bei `q = 17`; `tau = 10` statt `12` bei `q = 19`).
   - Beide Gleichnorm-Slices zusammen ($S_{\mathrm{eq}} := S_{\mathrm{inv}} \cup S_{\mathrm{sq}}$) dominieren alle Kontrollen außerhalb (`diff-norm`, `non-u`, `m2 != 1`) um Faktor `20–40` bei `min_unc` und um `6–9` Spalten bei `k_punc`.
2. **Widerlegung der naiven `q ≡ 3 mod 4`-Hypothese:**
   - Bei `q = 19` (`19 ≡ 3 mod 4`) kollabierten `(4,2)` und `(2,4)` *nicht* auf `0` (im Gegensatz zu `q = 7, 11`), und es ergab sich `k_punc = 30 = Bai 30`.
   - Stattdessen trat der reine `(3,3)`-Kollaps (`42 = 0, 24 = 0`) bei **`q = 17` (`17 ≡ 1 mod 4`) in `sq-norm`** auf (`unc = 198 [0/198/0]`), und genau dort wurde **Bai `k = 26` mit `k_punc = 27` überboten**.
3. **Geometrische Struktur der Hitting-Sets bei `q = 17` und `q = 19`:**
   - **`q = 17, k = 27` (`sq-norm`):** `g1 = (15, 1)` ($\mathrm{N}=1, \mathrm{ord}=9$), `g2 = (12, 5)` ($\mathrm{N}=1, \mathrm{ord}=9$), `alpha = (6, 10)` ($\mathrm{N}=8 \in (\mathbb{F}_{17}^*)^2, \mathrm{ord}=48$), `beta = (1, 14)` ($\mathrm{N}=8, \mathrm{ord}=144$), `m2 = 1`. Alle `198` ungedeckten `(3,3)`-Tupel treffen die `9` geraden Spalten von Bahn A (`del_A = [0,2,4,6,8,10,12,14,16]`, `del_B = []`, `del_mask = 0x15555`). Damit verbleiben $9 + 18 = 27 = \frac{3}{2}(q + 1)$ Spalten.
   - **`q = 19, k = 30` (`sq-norm`):** `g1 = (1, 0)` ($\mathrm{ord}=1$), `g2 = (18, 0) = -1` ($\mathrm{ord}=2$), `alpha = (0, 1) = i` ($\mathrm{N}=17 \in (\mathbb{F}_{19}^*)^2, \mathrm{ord}=36$), `beta = (0, 18) = -i` ($\mathrm{N}=17, \mathrm{ord}=36$), `m2 = 1`. Das minimale Hitting-Set `del_mask = 0x4444411111` streicht genau jede 4. Spalte je Bahn (`del_A = [0,4,8,12,16]`, `del_B = [2,6,10,14,18]`, `tau = 10 = (q+1)/2`, `k = 30 = 3(q+1)/2`).

---

## 3. AP 3: Unabhängige CPHF-Vollprüfung & Read-only Live-`ca-tools`-Abgleich

### 3.1 Treffer `CPHF(2; 27, 17, 6)` (`data/phase9_cphf_t6/cphf_q17_k27_punc.json`)

- **Datei & Prüfsumme:** [`data/phase9_cphf_t6/cphf_q17_k27_punc.json`](../../data/phase9_cphf_t6/cphf_q17_k27_punc.json), `SHA-256 = aaf92b7da276c018cb16b4939ae3f40760b439fc5a63d581cac8fc717ec930d9` (`3×` byte-identisch reproduziert: Erstlauf `3,851 s`, Repro 1 `3,840 s`, Repro 2 nach Symmetriebrechung `4,189 s`, `cmp -s PASS`).
- **Doppelte unabhängige CPHF-Vollprüfung über alle $\binom{27}{6} = 296.010$ 6-Tupel:**
  1. **Eigenständiger C-Prüfer (`scripts/phase9_cphf_t6_verify.c`, 2 Threads, `0,0312 s`):**
     - `unc = 0 / 296.010` (`PASS`), `dep1 = [0, 4464, 6246, 2844, 1080, 153, 0]`, `dep2 = [18564, 0, 6480, 3744, 909, 0, 84]`, `both = [0, 0, 0, 0, 0, 0, 0]`.
     - Negativkontrolle 1 (duplizierte Spalte `0 -> 1`): `unc = 12.650` (`FAIL` erwartet).
     - Negativkontrolle 2 (Nullspalte `0`): `unc = 65.780` (`FAIL` erwartet).
     - Sherwood-Hyperebenen: `R1 = [1, 0, 0, 0, 0, 8]`, `R2 = [1, 0, 0, 0, 0, 0]` $\implies$ $N = 2 \cdot 17^6 - 17 = 48.275.121$.
  2. **Unabhängige Python-Referenz (`scripts/phase9_cphf_t6_check.py --verify-json`, `7,251 s`):**
     - **100 % bit-identische Übereinstimmung** aller Vektoren (`unc = 0`, identisches `dep1`, `dep2`, `both`, Negativkontrolle `12.650 FAIL`, identische Sherwood-Hyperebenen `N = 48.275.121`).
  3. **1:1-Querprüfung des C-Prüfers auf bestehenden Treffern:**
     - `cphf_q11_k20_punc.json` (`38.760` Tupel, `0,0043 s`): 100 % identisch zu Python (`unc = 0`, `dep1=[0,215,760,870,760,215,0]`, `dep2=[210,0,778,936,778,0,210]`, neg `3.060 FAIL`, Sherwood `N = 3.543.111`).
     - `cphf_q13_k21_punc.json` (`54.264` Tupel, `0,0059 s`): 100 % identisch zu Python (`unc = 0`).
     - `/tmp/phase9_q19_q17/cphf_q19_k30_punc.json` (`593.775` Tupel, `0,0610 s`): `unc = 0`, neg dup `20.475 FAIL`, neg zero `118.755 FAIL`, Sherwood `N = 94.091.743`.

### 3.2 Read-only Live-Abgleich gegen `chrispbsmolen/ca-tools` (`t = 6`)

- **Geprüfter Stand:** `chrispbsmolen/ca-tools @ b68996787557cb79153f2d0ca9640aa821c57e52` (`2026-11-28T02:10:53Z`), `0` offene Pull Requests. Geprüfte Dateien (lokal nur in `/tmp/ca_tools_ro/`): `table/ca_frame.csv`, `table/ca_table.csv.gz`, `table/derived.csv` (`0` relevante `derived.csv`-Einträge für `t = 6` in unseren Bereichen).

| `v = q` | Unser `k` | Unser Sherwood-`N = 2q^6 - q` | Live-`ca-tools @ b689967` an Zelle `(6, k, v)` (effektiv) | Benachbarte Einträge in `ca_frame.csv` | Differenz `ΔN` | Bewertung (Belegstatus) |
|---:|---:|---:|---:|---|---:|---|
| `5` | `12` | `31.245` | `30.625` (`TJ-IM`) | `k=11: 28.125`, `k=12: 30.625` | `+620` | größer als Tabelle (CA lokal dual-verifiziert) |
| `7` | `16` | `235.291` | `232.897` (`genus-2`, `2q^6 - q^4`) | `k=16: 232.897` | `+2.394` | größer als Tabelle (CPHF vollgeprüft, `ca_verify` offen) |
| **`11`** | **`20`** | **`3.543.111`** | **`5.300.031`** (`CL` bei `k = 21`; `k = 20` fehlt) | `k=19: 3.543.111` (Bai), `k=21: 5.300.031` (CL) | **`−1.756.920` (`−33,15 %`)** | **kleiner als Tabelle am Commit `b689967` (CPHF vollgeprüft in C+Python; `ca_verify` & Drittprüfung offen)** |
| `13` | `21` | `9.653.605` | `9.653.605` (`Bai` bei `k = 22`) | `k=22: 9.653.605` (Bai), `k=23: 14.480.401` (CLS) | `0` (dominiert) | dominiert durch Bai `k = 22` |
| **`17`** | **`27`** | **`48.275.121`** | **`72.412.673`** (`CLS` bei `k = 27`) | `k=26: 48.275.121` (Bai), `k=27: 72.412.673` (CLS) | **`−24.137.552` (`−33,33 %`)** | **kleiner als Tabelle am Commit `b689967` (CPHF vollgeprüft in C+Python; `ca_verify` & Drittprüfung offen)** |
| `19` | `30` | `94.091.743` | `94.091.743` (`Bai` bei `k = 30`) | `k=30: 94.091.743` (Bai), `k=31: 141.137.641` (WCS) | `0` | Gleichstand mit Bai `k = 30` (CPHF vollgeprüft; nicht im Repo abgelegt) |

**Hinweis zur Größenordnung (`ca-tools`-Einreichungsregeln):**
- Ein ausgerolltes `CA(3.543.111; 6, 20, 11)` wäre `~180 MB` groß (über `50 MiB` Einzeldatei-Limit), und `CA(48.275.121; 6, 27, 17)` wäre `~3,6 GB` groß. Beide kommen daher nur über CPHF-/Generator-Einreichung (oder externe Verifikation nach `ca-tools`-Regeln) in Betracht; **externe Einreichungs-Sperre bleibt aktiv**, keine Außenwirkung.
