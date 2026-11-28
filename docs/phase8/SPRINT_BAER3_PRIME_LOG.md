# Phase 8 Sprint-Log: Baer-v3 (Kreuzgruppen-K-Promotion + 3. Richtung) & Primzahl-Schranke $L_{\mathrm{prim}}(p)$

- **Datum:** 2026-11-27
- **Branch:** `exp/phase8-sprint-baer3-prime` (Basis: `main @ 0bcbe2b`, PR `#50` nicht gemergt)
- **Umgebung:** Intel Xeon @ 2.30 GHz, 2 vCPU, Python 3.12 (`std`-only), `gcc` (`verifiers/ca_verify` lokal kompiliert). Hinweis: `ortools` ist in dieser VM nicht installiert (kein PyPI-Zugriff); CP-SAT wurde durch exakte kombinatorische Schranken, vollstaendige Aufzaehlung (`p = 3, m = 11`) und eine 30-s-Scratch-C-Tabu-Probe (`q = 9, v = 9`) ersetzt.
- **Außenwirkung:** keine. Geschuetzte Pfade unveraendert (`verifiers/SHA256SUMS` 3/3 OK, `git diff main -- verifiers/` leer, `verifiers/test_verifiers.py` 23/23 PASS).

---

## Teil A: Baustelle 1 — Baer-v3 auf `q = 9, 16, 25`

### A.1 Positivbefund: Kreuzgruppen-K-Promotion + Redundant-Slot-Recycling (`scripts/phase8_baer_v3_explore.py`)

**Mechanismus (deterministisch, `std`-only, ohne Loeser, ohne Zufall):**
Im Baer-v1/v2-Skelett bleiben bei $r$ dedizierten Vollgeraden-Symbolen $V_0, \dots, V_{r-1}$ auf $\{w_2 = 0\}$ ($a$-Seite) bzw. $\{w_1 = 0\}$ ($b$-Seite) genau $n - 1 - r$ freie Zeilen $L_{\mathrm{dst}}, L'_{\mathrm{dst}}$ uebrig. Befoerdert man auf jede solche freie Zeile eine $K$-Klasse $K^* = K(i_{\mathrm{src}}, j)$ aus einer $V_u$-Gruppe ($u = \mathrm{src} < r$, bzw. $i_{\mathrm{src}} = i_{\mathrm{dst}}$ bei $r = 0$) zu einer vollen Waagerechten auf $L_{\mathrm{dst}}$ ($a$-Seite) und $L'_{\mathrm{dst}}$ ($b$-Seite), gilt:

1. **Streichung auf $d = 0$:** $K^*$ benoetigt seine $n$ Punkte auf $d = 0, c_2 = i_{\mathrm{src}}$ nicht mehr (solange mindestens 1 unbefoerderte $K$-Klasse in Gruppe $i_{\mathrm{src}}$ verbleibt): Ersparnis **$-n$ Vertreter**.
2. **Recycling der $n$ redundanten $K^*$-Slots auf $d \neq 0$ (bei $\mathrm{src} = u < r$):**
   - Auf $w = i_{\mathrm{dst}} + i_{\mathrm{src}}\omega$ sind alle $n$ $a$-Slots von $K^*$ redundant (alle Paare $(K^*, K(i_{\mathrm{dst}}, *))$ sind bereits auf $L_{\mathrm{dst}}$ gedeckt) und werden an $a = V_u$ uebergeben $\Rightarrow$ deckt alle $n$ Paare $(V_u, K(i_{\mathrm{dst}}, *))$ **ohne Zusatzvertreter**.
   - Symmetrisch werden auf $w = i_{\mathrm{src}} + i_{\mathrm{dst}}\omega$ alle $n$ $b$-Slots von $K^*$ an $b = V_u$ uebergeben $\Rightarrow$ deckt $(K(i_{\mathrm{dst}}, *), V_u)$ **ohne Zusatzvertreter**.
3. **Recycling von $n - 1$ Slots auf $L_u$ und $L'_u$:** Auf $L_u$ ($a = V_u$) und $L'_u$ ($b = V_u$) benoetigt $K^*$ nur je $1$ seiner $n$ Punkte fuer $(V_u, K^*)$ bzw. $(K^*, V_u)$. Die uebrigen $n - 1$ Slots pro Seite decken balanciert-symmetrisch $\{V_0, \dots, V_{r-1}\}^2$, $(V_u, K_{\mathrm{promo}})$ und $(V_u, V_s) / (V_s, V_u)$ ohne Zusatzvertreter.
4. **Zero-Cost-Swaps & $c_2 = 0$-Diagonalsplits auf $d = 0$:** Verbleibende $(V_s, K)/(K, V_s)$ tauschen kostenfrei mit $(K, K)+(V_s, V_s)$ auf $c_2 \neq 0$; die $n - s$ redundanten Diagonaleintraege $(V_s, V_s)$ auf $c_2 = 0$ stehen fuer $+1$-Splits mit uebrigen symmetrischen Paaren bereit.

**Ergebnis (`13` strikt verbesserte Listen in `data/phase8_baer_v3/`, Laufzeit `1,10 s`, 2× byte-identisch):**

| `q` | `F` | `v` | Phase 7 §14 | Baer-v1 | Baer-v2 Ziel | **Baer-v3 (`|R|`)** | Delta vs. Ziel | Parameter `(r, promo)` | `--check-m` | `SHA-256` (Prefix) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | :---: | --- |
| 9 | 0 | 6 | 84 | 93 | 93 | **87** | `-6` | `(0, (0, 1))` | `0` Luecken | `e5b18f9e…` |
| 9 | 3 | 9 | 117 | 117 | 111 | **108** | `-3` | `(1, (0,))` | `0` Luecken | `3e0a03ac…` |
| 16 | 0 | 12 | 284 | 292 | 292 | **280** | `-12` | `(0, (0, 1, 2))` | `0` Luecken | `c36537ab…` |
| 16 | 1 | 13 | 301 | 304 | 292* | **284** | `-8` | `(1, (0, 0))` | `0` Luecken | `68770b9f…` |
| 16 | 2 | 14 | 322 | 320 | 300 | **298** | `-2` | `(1, (0, 0))` | `0` Luecken | `ea49fc7b…` |
| 16 | 3 | 15 | 347 | 336 | 318 | **316** | `-2` | `(1, (0, 0))` | `0` Luecken | `b5e410d2…` |
| 16 | 4 | 16 | 376 | 352 | 336 | **334** | `-2` | `(1, (0, 0))` | `0` Luecken | `d1a5a78b…` |
| 25 | 0 | 20 | 730 | 705 | 705 | **685** | `-20` | `(0, (0, 1, 2, 3))` | `0` Luecken | `6975f280…` |
| 25 | 1 | 21 | 761 | 725 | 705 | **690** | `-15` | `(1, (0, 0, 0))` | `0` Luecken | `96af41b0…` |
| 25 | 2 | 22 | 796 | 750 | 715 | **708** | `-7` | `(2, (0, 0))` | `0` Luecken | `57d0a27b…` |
| 25 | 3 | 23 | 835 | 775 | 739 | **733** | `-6` | `(2, (0, 1))` | `0` Luecken | `f23f6f82…` |
| 25 | 4 | 24 | 878 | 800 | 767 | **762** | `-5` | `(2, (0, 1))` | `0` Luecken | `8d9607ec…` |
| 25 | 5 | 25 | 925 | 825 | 795 | **791** | `-4` | `(2, (0, 1))` | `0` Luecken | `0ea8edaa…` |

*(Weitere deterministische Werte ohne Ablage: `q=9 v=7`: `90` vs. `91` §14 / `99` v1; `q=9 v=8`: `97` vs. `102` §14 / `104` Phase 7 CP-SAT / `108` v1. `*`: `q=16 v=13` war kein expliziter Zielwert im Auftrag; Baer-v2 mit `r=1` ergibt `292`.)*

- **Pruefungen der `13` Listen:** `scripts/phase7_lift.py --check-m` `13/13` `0` Luecken; `data/phase8_baer_v3/SHA256SUMS` `13/13 OK`; 2× byte-identisch gegen `/tmp/baer_v3_repro_check` (`diff` & `cmp -s` leer); `scripts/phase8/untergrenze.py listen` `0` Verletzungen von Lemma J und `L'(q)` (`q=9: 108 >= 96`, `q=16: 334 >= 296`, `q=25: 791 >= 711`).
- **E2E-Stichprobe (`t = 3` in `/tmp`, nicht abgelegt):** `R_q9_v9_baer3_m108.txt` $\to$ `CA(972; 3, 11, 9)` (`-45` gegen `results/phase8/CA_1017_3_11_9.txt`): `verifiers/ca_verify` Exit `0` (`0,00 s`), `verifiers/verify_independent.py` Exit `0` (`0,039 s`), Negativkontrolle (`971` Zeilen) beide Exit `1` (`117/165` Luecken).

### A.2 Negativbefunde: 3./4. Baer-Richtung, Ankerverschiebung $d^* \neq 0$, Kleinmodell `q = 9` & `F = 0`-Verschiebung

1. **Geometrische Obstruktion fuer 3./4. Baer-Richtung & Ankerverschiebung $d^* \neq 0$ bei fixen $K$-Klassen:**
   - Jede affine Baer-Unterebene durch $P_\infty$ trifft eine Baer-Untergerade $D \subset \mathbb{F}_q$ der Groesse $n + 1$.
   - Da $\{0\} \cup \{w_2 = 0\} = \mathbb{F}_n$ Teil der Baer-Untergeraden $\mathbb{F}_n \cup \{\infty\} \subset PG(1, q)$ ist und je zwei verschiedene Baer-Untergeraden sich in **hoechstens 2 Punkten** schneiden, gilt fuer **alle** `18` (`q=9`), `48` (`q=16`) bzw. `100` (`q=25`) Baer-Untergeraden in $\mathbb{F}_q$ exakt $|D \cap (\{0\} \cup \{w_2 = 0\})| \le 2$ (und $|D \cap \{w_2 = 0\}| \le 2$).
   - Damit laesst jede Baer-Ersatzklasse mindestens $n + 1 - \min(2, n - 1 - r)$ besetzte Waagerechte ($n$ Punkte je Zeile) plus die $r \cdot n$ fehlenden $(V, K)$-Paare gegen die $r$ Vollgeraden-Gruppen. Selbst bei maximal optimistischer Kreuzpaarung ergibt die exakte Untergrenze `LB_with_VK_splits = b0 + r*(r-1)*n + s*(min|S_a| + r)*n`:
     - `q = 9, v = 9`: `111, 117, 117` fuer `r = 0, 1, 2` (vs. Baer-v2 `111`; Baer-v3 `108`).
     - `q = 16, v = 16`: `340, 340, 348, 348` fuer `r = 0..3` (vs. Baer-v2 `336`; Baer-v3 `334`).
     - `q = 25, v = 25`: `805, 805, 805, 815, 815` fuer `r = 0..4` (vs. Baer-v2 `795`; Baer-v3 `791`).
   - Fazit: Bei fixierten $K$-Klassen unterbietet kein Ersatz von $d = 0$-Symbolen durch Baer-Unterebenen (3./4. Richtung oder $d^* \neq 0$) Baer-v2. Der Durchbruch entstand durch **Freigabe von $K$-Klassen** (Kreuzgruppen-K-Promotion).
2. **Kleinmodell `q = 9, v = 9` (Katalog & Scratch-Tabu-Probe):**
   - Vollstaendiger Katalog in `AG(2, 9)` durch $P_\infty$: `648` affine Baer-Unterebenen (Groesse `12`, alle `4` Richtungen, alle `9` Ankerzeilen, `18` Baer-Untergeraden, alle `81/81` Geraden geprueft) + `9` volle Waagerechte = `657` Mengen.
   - Symmetrische additive Translationsbahnen (`B_0 + (u*t, t)`): alle `5832` Bahnen bilden Bueschel `(1^8, 4)` je Zeile; bestes Bueschelpaar deckt `8/9` Differenzen $\Rightarrow |R| = 108 + 9 = 117$.
   - Scratch-C-WalkSAT/PAWS-Probe (`q9_tabu`, 1T, `30 s` ab Baer-v2 `111`, Seed `8001`): fand `110` (`0,186 s`), `109` (`0,211 s`, `--check-m` `0` Luecken; Sezierung lieferte die deterministische `108`-Konstruktion!) und erreichte bei `108` `best_unc = 1` (`13,3M` Zuege, `443k mv/s`). Random-Start (`Seed 8002`, `30 s`, `M = 110`): `best_unc = 5` (`12,1M` Zuege, `404k mv/s`).
3. **`F = 0` Verschiebung von $K$-Klassen auf $d = 0, c_2 = 0$:**
   - Nach Promotion der $n - 1$ $K$-Klassen (`87`, `280`, `685`) bleiben $n$ Fuell-Vertreter auf $d = 0, c_2 = 0$.
   - Exakte Pruefung aller affinen Verschiebungen $(c, d) \mapsto (c + rd - i\omega, d)$ einer verbleibenden $K$-Klasse auf $c_2 = 0$ ergibt mindestens `3` (`q=9`), `8` (`q=16`), `15` (`q=25`) Kollisionspunkte allein auf der $a$-Seite fuer $d \neq 0$, also Netto-Delta $\ge 0$ (`q=9`), $\ge +4$ (`q=16`), $\ge +10$ (`q=25`). Die letzten $n$ Fuell-Vertreter lassen sich so nicht einsparen.

---

## Teil B: Baustelle 2 — Primzahl-Untergrenze $L_{\mathrm{prim}}(p)$ (`scripts/phase8_prime_bound.py`)

Implementierung in reiner Standardbibliothek (`std`-only), Rechenzeit fuer alle `15` ungeraden Primzahlen `p in [3..53]`: **`1,47 s`** (`< 5 s`), exakt ganzzahlig ueber konkave $k$-Endpunktauswertung (`k in {1, k_max, p - alpha - beta}`, gegen volle Brute-Force-Aufzaehlung identisch bestaetigt).

| `p` | `L'(p)` | `L_prim(p)` | `L_prim(p) / p^2` | Opt. `(f_a, f_b; alpha, beta, k)` | Beste Liste im Repo (`v = p`) | Abstand |
| ---: | ---: | ---: | ---: | --- | --- | ---: |
| 3 | 11 | 11 | 1.2222 | `(2, 2; 0, 0, 2)` `[B=11, LB=11]` | – *(exakt min = 12)* | – |
| 5 | 30 | 31 | 1.2400 | `(3, 3; 2, 2, 1)` `[B=31, LB=29]` | `R_q5_m34.txt` (34) | 3 |
| 7 | 59 | 60 | 1.2245 | `(5, 5; 2, 2, 3)` `[B=57, LB=60]` | `R_q7_m68.txt` (68) | 8 |
| 11 | 142 | 145 | 1.1983 | `(7, 7; 4, 4, 3)` `[B=145, LB=144]` | `R_q11_m170.txt` (170) | 25 |
| 13 | 197 | 204 | 1.2071 | `(8, 8; 5, 5, 3)` `[B=204, LB=200]` | `R_q13_m238.txt` (238) | 34 |
| 17 | 334 | 347 | 1.2007 | `(11, 11; 6, 6, 5)` `[B=343, LB=347]` | `R_q17_m412.txt` (412) | 65 |
| 19 | 415 | 431 | 1.1939 | `(12, 12; 7, 7, 5)` `[B=431, LB=431]` | `R_q19_m513.txt` (513) | 82 |
| 23 | 604 | 637 | 1.2042 | `(14, 14; 9, 9, 5)` `[B=637, LB=625]` | `R_q23_m746.txt` (746) | 109 |
| 29 | 951 | 1006 | 1.1962 | `(18, 18; 11, 11, 7)` `[B=1006, LB=1000]` | `R_q29_m1190.txt` (1190) | 184 |
| 31 | 1084 | 1153 | 1.1998 | `(19, 19; 12, 12, 7)` `[B=1153, LB=1138]` | `R_q31_m1356.txt` (1356) | 203 |
| 37 | 1534 | 1635 | 1.1943 | `(23, 23; 14, 14, 9)` `[B=1635, LB=1629]` | `R_q37_m1942.txt` (1942) | 307 |
| 41 | 1877 | 2014 | 1.1981 | `(26, 26; 15, 15, 11)` `[B=1996, LB=2014]` | – | – |
| 43 | 2061 | 2208 | 1.1942 | `(27, 27; 16, 16, 11)` `[B=2201, LB=2208]` | – | – |
| 47 | 2454 | 2641 | 1.1956 | `(29, 29; 18, 18, 11)` `[B=2641, LB=2624]` | – | – |
| 53 | 3106 | 3349 | 1.1922 | `(33, 33; 20, 20, 13)` `[B=3349, LB=3347]` | – | – |

- **Listenpruefung (`data/phase7/`, `data/phase8/`, `data/phase8_repro/`):** Alle `16` Primzahl-Listen (`v = p`) geprueft, **`0` Verletzungen** (kleinster Abstand `3` bei `p = 5`: `34` gegen `31`).
- **Exakte Entscheidung `p = 3, m = 11` (`--check-p3`, `std`-only, ohne OR-Tools):**
  - Positivkontrolle auf Phase-6A-Multimenge (`m = 12`) mit derselben kanonischen Engine: **`PASS`** (`32` kanonische Loesungspaare).
  - Vollstaendige Aufzaehlung ueber alle `45` Punkt-Multimengen der Groesse `11` auf $\mathbb{F}_3^2$ (alle `9` mit einer 3-fachen + `36` mit zwei 2-fachen Multiplizitaeten, ohne affine Symmetriereduktion) × alle `28.501` kanonischen ternaeren Vektoren ($S(11, 3)$): `1.071` gueltige Einzelseiten, `13.410` Paartests, **`0` Loesungen** (`status=UNSAT_EXACT`, Laufzeit **`1,12 s`**).
  - Belegart: **vollstaendig durchgerechnet, `m = 11` fuer `p = 3` exakt ausgeschlossen $\Rightarrow \min |R|(3) = 12$** (schliesst den in `P8-U-EXAKT` nach `300 s` CP-SAT offenen Fall `q = 3`).

---

## Nachtrag Option A: Lifts & Dual-Verifikation in `/tmp/phase8_baer_v3/` (nicht committet)

Alle `9` Arrays wurden mit `scripts/phase7_lift.py` (`--check-m` `0` Luecken) **2× byte-identisch** erzeugt (Run 1: `16,516 s`, Run 2: `14,879 s`), mit `verifiers/ca_verify` (POS & NEG: letzte Zeile entfernt) geprueft und fuer alle `8` Task-1-Arrays zusaetzlich mit `verifiers/verify_independent.py` (POS & NEG) dual-verifiziert (`verifiers/SHA256SUMS` `3/3 OK`, `test_verifiers.py` `23/23 PASS`).

| Array (`/tmp/phase8_baer_v3/`) | `q, v, t, m` | Bytes | `SHA-256` | `ca_verify` POS / NEG | `verify_independent.py` POS / NEG | Status |
| --- | --- | ---: | --- | --- | --- | --- |
| `CA_972_3_11_9.txt` | `9, 9, 3, 108` | 21.384 | `a62790bb72e46e0dae80469ec9f2b741e404676ca72a76640223d6e4ee303d85` | `rc=0` (0,004 s) / `rc=1` (0,004 s) | `rc=0` (0,088 s) / `rc=1` (0,089 s) | **DUAL_PASS** |
| `CA_8748_4_11_9.txt` | `9, 9, 4, 108` | 192.456 | `3008bb9bc4568cc1dbca70b81052a629a89ff89c40ee64d3c4bd5ca22a396a8f` | `rc=0` (0,011 s) / `rc=1` (0,013 s) | `rc=0` (0,954 s) / `rc=1` (0,986 s) | **DUAL_PASS** |
| `CA_76288_4_18_14.txt` | `16, 14, 4, 298` | 3.093.248 | `e67727ccaa9a1ca70e49969f01cda02da8eb69b7aaea80806d9dc4ccf90a9b7c` | `rc=0` (0,480 s) / `rc=1` (0,484 s) | `rc=0` (76,11 s) / `rc=1` (75,41 s) | **DUAL_PASS** |
| `CA_80896_4_18_15.txt` | `16, 15, 4, 316` | 3.367.168 | `84dc29a46202c1326dfad3cad5f3bff4f755b383ce5be38b8de0462e00679ebb` | `rc=0` (0,554 s) / `rc=1` (0,549 s) | `rc=0` (86,72 s) / `rc=1` (86,69 s) | **DUAL_PASS** |
| `CA_17125_3_27_20.txt` | `25, 20, 3, 685` | 1.113.000 | `5b95db86df4d0141613b83bf261dbcfe98a4618a55ad6d1884d9b3ce5ec34e2e` | `rc=0` (0,177 s) / `rc=1` (0,176 s) | `rc=0` (11,09 s) / `rc=1` (11,28 s) | **DUAL_PASS** |
| `CA_17250_3_27_21.txt` | `25, 21, 3, 690` | 1.138.525 | `b8325aa4b4f3b3108669ab593be33ebc823afbd3fc164fb3a713537efca50eed` | `rc=0` (0,201 s) / `rc=1` (0,202 s) | `rc=0` (11,81 s) / `rc=1` (11,81 s) | **DUAL_PASS** |
| `CA_17700_3_27_22.txt` | `25, 22, 3, 708` | 1.187.075 | `be2beb22e229067524a18b3c3b337be824f9d5cff4a4f8e74fcbba8e480285b3` | `rc=0` (0,226 s) / `rc=1` (0,215 s) | `rc=0` (12,96 s) / `rc=1` (12,85 s) | **DUAL_PASS** |
| `CA_18325_3_27_23.txt` | `25, 23, 3, 733` | 1.248.025 | `0fc3b3d69a8a03bcc2c53fe362b258d708781b33b5d0e9db74b763962d8e28f6` | `rc=0` (0,057 s) / `rc=1` (0,059 s) | `rc=0` (13,84 s) / `rc=1` (13,78 s) | **DUAL_PASS** |
| `CA_494375_4_27_25.txt` | `25, 25, 4, 791` | 34.688.125 | `98c84010a0a91f862bfb1b94f6d9e80149441577c5605cb7070e453443dbf326` | `rc=0` (49,76 s) / `rc=1` (50,91 s) | **nicht gelaufen** (Shell-Cap) | **TEILCHECK** |
