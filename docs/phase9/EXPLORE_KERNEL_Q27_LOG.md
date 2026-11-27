# Phase 9 Vorarbeit: Ausbruch aus Kern $K_t$ ($q = 5, 7$) und Kubik-Check ($q = 27$)

- **Datum:** 2026-11-27
- **Branch:** `exp/phase9-kernel-breakout` (Basis: `main @ 0bcbe2b`)
- **Hardware:** `Intel(R) Xeon(R) CPU @ 2.30GHz`, `2` vCPU (`1` Thread/Core)
- **Verifiers:** `sha256sum -c verifiers/SHA256SUMS` `3/3 OK`, `git diff main -- verifiers/` leer, `python3 verifiers/test_verifiers.py` `23/23 PASS`
- **Außenwirkung:** keine. Kein Push nach `ca-tools`, kein GitHub-Actions-Lauf, kein Merge nach `main`; PR `#50/#51/#52` und geschützte Pfade unverändert.

---

## Experiment 1: Ausbruch aus Kern $K_t$ (Sitjar Lemma 1, $q = 5, 7$)

### 1.1 Solver & Selbsttest

Solver: [`scripts/phase9_coset_search.c`](../../scripts/phase9_coset_search.c) (C, `-O3 -march=native -pthread`, `std`-only, lokal kompiliert nach `/tmp/phase9/coset_search`).
- Berechnet zu jedem $t$-Spaltentupel $S \in \binom{[k]}{t}$ exakt die $2 \times t$-Prüfmatrix $H_S$ über $\mathbb{F}_q$ mit $H_S (G|_S)^T = 0$ und $\operatorname{rang}(G|_S) = d = t - 2$.
- Normiert alle Vertreter auf $s_i[0 \dots d-1] = 0$ ($k - d$ freie Koordinaten in $\mathbb{F}_q$).
- Suchverfahren: Parallel Tempering (`8` Replikate pro Thread, `2` Threads, geometrische Temperaturleiter $T \in [0.14, 1.80]$, gemischte globale `1`-Flips und fokussierte `1`/`2`-Flips). Unterstützt freie Vertreter (`scale_inv = 0`) sowie $\mathbb{F}_q^*$-skalierungsinvariante Orbits (`--scale-inv`, `M = has_zero + active * (q - 1)`, Zielmenge `q + 1` Strahlen in $\mathrm{PG}(1, q)$ zzgl. Nullsyndrom bei `has_zero = 0`).
- **Inkrementeller Selbsttest (`--selftest`):** `5000/5000` zufällige `1`- und `2`-Flips exakt gegen Neuberechnung ab Null geprüft (`PASS` auf allen fünf Codes `c0, c1, c2, all1_5, all1_7` sowie `--scale-inv` mit `has_zero = 0, 1`).
- **Harter Shell-Cap:** jeder einzelne Suchlauf mit `timeout 60` (`--time 58`).

### 1.2 Ergebnisse (1a, 1b, 1c)

| Teil | Code / Modus | Ziel `CA(N; t, k, v)` | `m` (aktive Vektoren) | Modus | Laufzeit | Evals (`evals/s`) | Ergebnis | Belegart |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| 1a (Kontrolle) | `C_0` (`K_4`, 2 Nullspalten) | `CA(850; 4, 7, 5)` | `34` (`34`) | frei | `0,167 s` | `1,29M` (`7,75M/s`) | **`FOUND unc=0`**, Prune `deleted=0` (`850`) | **Dual-verifiziert** (`/tmp/phase9/CA_850_4_7_5_c0.txt`, SHA `fb1fdfce…2b2c0`); Prune `0` Zeilen |
| 1a | `C_0` (`K_4`, 2 Nullspalten) | `CA(825; 4, 7, 5)` | `33` (`33`) | frei (ohne 2D-Bindung) | `58,018 s` | `505,7M` (`8,72M/s`) | **`TIMEOUT (best_unc=6)`** | Heuristische Suche erfolglos (60 s Cap) |
| 1a | `C_1` (`G_1`, 0 Nullspalten) | `CA(825; 4, 7, 5)` | `33` (`33`) | frei | `58,024 s` | `472,6M` (`8,15M/s`) | **`TIMEOUT (best_unc=16)`** | Heuristische Suche erfolglos (60 s Cap) |
| 1a | `C_1` (`G_1`, 0 Nullspalten) | `CA(825; 4, 7, 5)` | `33` (`1 + 8` Orbits) | `--scale-inv` | `58,035 s` | `344,9M` (`5,94M/s`) | **`TIMEOUT (best_unc=2)`** | Heuristische Suche erfolglos (60 s Cap; `2/210` Strahlen offen) |
| 1a | `C_1` (`G_1`, 0 Nullspalten) | `CA(850; 4, 7, 5)` | `34` (`34`) | frei | `58,020 s` | `424,3M` (`7,31M/s`) | **`TIMEOUT (best_unc=6)`** | Heuristische Suche erfolglos (60 s Cap; Prune n/a) |
| 1a | `C_2` (`G_2`, 1 Nullspalte) | `CA(825; 4, 7, 5)` | `33` (`33`) | frei | `58,031 s` | `421,9M` (`7,27M/s`) | **`TIMEOUT (best_unc=20)`** | Heuristische Suche erfolglos (60 s Cap) |
| 1a | `C_2` (`G_2`, 1 Nullspalte) | `CA(825; 4, 7, 5)` | `33` (`1 + 8` Orbits) | `--scale-inv` | `58,024 s` | `324,3M` (`5,59M/s`) | **`TIMEOUT (best_unc=6)`** | Heuristische Suche erfolglos (60 s Cap; `6/210` Strahlen offen) |
| 1a | `C_2` (`G_2`, 1 Nullspalte) | `CA(850; 4, 7, 5)` | `34` (`34`) | frei | `58,009 s` | `415,9M` (`7,17M/s`) | **`TIMEOUT (best_unc=18)`** | Heuristische Suche erfolglos (60 s Cap; Prune n/a) |
| 1b (Gate 0) | `all1_5` (`[7,1]`, 0 Nullsp.) | `CA(165; 3, 7, 5)` | `33` (`33`) | frei (SA) | `58,002 s` | `668,5M` (`11,52M/s`) | **`TIMEOUT (best_unc=14)`** | Heuristische Suche erfolglos (unstrukturiert) |
| 1b (Gate 0) | `all1_5` (`[7,1]`, 0 Nullsp.) | `CA(165; 3, 7, 5)` | `33` (`1 + 8` Orbits) | `--scale-inv` | `7,708 s` | `55,4M` (`7,18M/s`) | **`FOUND unc=0`** | **Gate 0 PASS, dual-verifiziert** (`/tmp/phase9/CA_165_3_7_5_all1.txt`, SHA `d36af121…43754`, Neg. `20/35` Lücken `FAIL`) |
| 1b (Ziel) | `all1_5` (`[7,1]`, 0 Nullsp.) | `CA(160; 3, 7, 5)` | `32` (`8` Orbits) | `--scale-inv` | `58,016 s` | `468,5M` (`8,07M/s`) | **`TIMEOUT (best_unc=8)`** | Heuristische Suche erfolglos (60 s Cap) |
| 1b (Ziel) | `all1_5` (`[7,1]`, 0 Nullsp.) | `CA(160; 3, 7, 5)` | `32` (`32`) | frei | `58,026 s` | `490,9M` (`8,46M/s`) | **`TIMEOUT (best_unc=17)`** | Heuristische Suche erfolglos (60 s Cap) |
| 1c (Ziel) | `all1_7` (`[9,1]`, 0 Nullsp.) | `CA(455; 3, 9, 7)` | `65` (`65`) | frei | `58,037 s` | `297,4M` (`5,12M/s`) | **`TIMEOUT (best_unc=355)`** | Heuristische Suche erfolglos (60 s Cap) |
| 1c (Vergl.) | `all1_7` (`[9,1]`, 0 Nullsp.) | `CA(462; 3, 9, 7)` | `66` (`66`) | frei | `58,014 s` | `295,7M` (`5,10M/s`) | **`TIMEOUT (best_unc=329)`** | Heuristische Suche erfolglos (60 s Cap) |
| 1c (Vergl.) | `all1_7` (`[9,1]`, 0 Nullsp.) | `CA(462; 3, 9, 7)` | `66` (`11` Orbits) | `--scale-inv` | `58,043 s` | `285,7M` (`4,92M/s`) | **`TIMEOUT (best_unc=12)`** | Heuristische Suche erfolglos (60 s Cap; `12/756` Ziele offen) |
| 1c (Bonus) | `all1_7` (`[9,1]`, 0 Nullsp.) | `CA(469; 3, 9, 7)` | `67` (`1 + 11` Orbits) | `--scale-inv` | `58,053 s` | `262,5M` (`4,52M/s`) | **`TIMEOUT (best_unc=6)`** | Heuristische Suche erfolglos (60 s Cap; `6/672` Strahlen offen) |
| 1c (Bonus) | `all1_7` (`[9,1]`, 0 Nullsp.) | `CA(427; 3, 9, 7)` | `61` (`1 + 10` Orbits) | `--scale-inv` | `58,056 s` | `265,8M` (`4,58M/s`) | **`TIMEOUT (best_unc=12)`** | Heuristische Suche erfolglos (60 s Cap; `12/672` Strahlen offen) |

### 1.3 Nüchterne Auswertung von Experiment 1

1. **Kein Durchbruch unter `825` (`4,7,5`), `165` (`3,7,5`) oder `462` (`3,9,7`)** im 60-s-Budget. Alle Suchabbrüche sind heuristische Timeouts; nichts ist mathematisch ausgeschlossen.
2. **Ursache im freien Suchraum:** Auf `C_0` (`K_4`, zwei Nullspalten) löst Parallel Tempering `m = 34` in `0,167 s`, weil die zwei Nullspalten von den `5` MDS-Spalten entkoppeln. Ohne zwei Nullspalten (`C_1`, `C_2`, `all1_5`, `all1_7`) sind alle `35` bzw. `84` Spaltentupel stark gekoppelt; die unstrukturierte Suche friert bei `best_unc = 6..20` (`q = 5`) bzw. `329..355` (`q = 7`) ein.
3. **Wirkung der Skalierungsinvarianz (`--scale-inv`):** Reduktion auf $\mathbb{F}_q^*$-Orbits reproduziert das bekannte `CA(165; 3, 7, 5)` (Gate 0) in `7,708 s` (dual-verifiziert) und drückt `C_1 m = 33` auf `best_unc = 2` sowie `all1_7 m = 67` (`469 < 472`) auf `best_unc = 6`, reicht im 60-s-Limit aber nicht für einen neuen Treffer.
4. **Redundanz-Streichung (`m = 34`):** Auf `CA(850; 4, 7, 5)` aus `C_0` lassen sich über `101` gierige Durchläufe `0` Zeilen streichen (`pruned_N = 850`).

---

## Experiment 2: Kubischer Körper $q = 27$ ($\mathbb{F}_3$-lineare Spur-Blocking-Sets in $\mathrm{PG}(2, 27)$ / $\mathrm{AG}(2, 27)$)

### 2.1 Exakte Geometrie von $B_{\mathrm{tr}}$ in $\mathrm{PG}(2, 27)$

Skript: [`scripts/phase9_q27_trace_check.py`](../../scripts/phase9_q27_trace_check.py) (`std`-only, `GeneralGF(27)` aus [`scripts/gen_general_tqv.py`](../../scripts/gen_general_tqv.py), irreduzibles Polynom $X^3 + 2X + 1$ über $\mathbb{F}_3$, Teilkörper $\mathbb{F}_3 = \{0, 1, 2\}$).

Standard-Spur-Blocking-Set vom Rédei-Typ über $\mathrm{Tr}_{\mathbb{F}_{27}/\mathbb{F}_3}(x) = x + x^3 + x^9$:
$$B_{\mathrm{tr}} = \{(x : \mathrm{Tr}(x) : 1) \mid x \in \mathbb{F}_{27}\} \cup \{\mathrm{norm}(x : \mathrm{Tr}(x) : 0) \mid x \in \mathbb{F}_{27}^\times\} \subset \mathrm{PG}(2, 27).$$

- **Größe:** $|B_{\mathrm{tr}}| = 27 + 10 = 37$ (affin nach Entfernen einer Tangente $L_\infty$ durch $P_\infty \in B_{\mathrm{tr}}$: $|A| = 36$).
- **Sekantenverteilung über alle `757` Geraden von $\mathrm{PG}(2, 27)$:**
  - `1`-Sekanten (Tangenten): `672`
  - `4`-Sekanten: `81`
  - `10`-Sekanten: `4` (alle `4` laufen durch $(1:0:0)$: $Z = 0$ sowie $Y = c Z$ für $c \in \mathbb{F}_3$)
  - `0`-Sekanten: `0` (Blockierungsmenge), min. Tangenten je Punkt: `18` (minimal).
- **Exakte Waagerechten-Profile $(m, \text{Punktverteilung})$ für alle Paare $(P_\infty, L_\infty)$ mit $P_\infty \in B_{\mathrm{tr}}$ und Tangente $L_\infty$:**

| Profil | $m$ (getroffene Waagerechte) | Punktverteilung auf Waagerechten (Summe `36`) | Lemma-J-Schlupf $|A| - (q + m - 1)$ | Punkte $P_\infty \in B_{\mathrm{tr}}$ | Tangenten je $P_\infty$ | Paare $(P_\infty, L_\infty)$ | Affine Prüfung (`729` Geraden) |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| Profil A | `4` | `(9, 9, 9, 9)` | `6` | `1` (`(1, 0, 0)`) | `24` | `24` | `0` Lücken (`PASS`) |
| Profil B | `10` | `(9, 3, 3, 3, 3, 3, 3, 3, 3, 3)` | `0` (Gleichheit) | `36` | `18` | `648` | `0` Lücken (`PASS`) |

### 2.2 Universelle LP-/Paar-Untergrenzen im Modell $M(R)$ (Klassengröße `36`)

| Profil | $v = 24$ (Basis `930`) | $v = 25$ (Basis `968`) | $v = 27$ |
| --- | ---: | ---: | ---: |
| Profil A (`m = 4`, `(9^4)`) | `>= 864` | `>= 896` | `>= 972` |
| Profil B (`m = 10`, `(9, 3^9)`) | `>= 738` | `>= 774` | `>= 837` |

*(Hinweis zu Profil A: Je leichter Waagerechter passen höchstens `3` disjunkte Klassen (`3 * 9 = 27`), also höchstens `9` Symbolpaare; über `26` Waagerechte sind das höchstens `234` Paare, was bei `v = 24` mindestens `576 - 234 = 342` Paare auf $d = 0$ erzwingt (`|R| >= 702 + 342 = 1044 > 930`). Profil B trägt hingegen `9` disjunkte Klassen je leichter Waagerechter (`9 * 3 = 27`), also bis zu `27` Paare je Waagerechter.)*

### 2.3 Kubisches Spur-Gitter (`Cubic Trace Grid`) im Modell $M(R)$ für $q = 27$

Mit Profil B (`m = 10`, Größe `36`) entsteht eine deterministische Konstruktion ohne Löser:
- Zwei $\mathbb{F}_3$-unabhängige Spur-Hyperebenen $H_a = \{w : \mathrm{Tr}(w) = 0\}$ (`a_dir = 1`) und $H_b = \{w : \mathrm{Tr}(3w) = 0\}$ (`b_dir = 3`), gemeinsamer Kern $w_k = 1$.
- **18 `a`-Klassen (`0..17`):** je `9` disjunkte Klassen auf $W_1 = \{1/w : \mathrm{Tr}(w) = 1\}$ und $W_2 = \{1/w : \mathrm{Tr}(w) = 2\}$ durch Verschiebung $t \in \mathbb{F}_{27}/\mathbb{F}_3$; decken `486` Punkte auf $d \ne 0$ mit Maximalvielfachheit `1` und lassen `8` Waagerechte $W_0$ leer.
- **18 `b`-Klassen (`0..17`):** analog auf $W_1', W_2'$ mit $s_b / s_a \notin \mathbb{F}_3$ und $(c_{0,b} - c_{0,a}) w_k \notin \mathbb{F}_3 s_a + \mathbb{F}_3 s_b$. Dadurch treffen sich **alle `18 x 18 = 324` Klassenpaare in genau `1` Punkt auf $d \ne 0$**.
- **Vollgeraden-Symbole:** Die ersten `6` Vollgeraden-Symbole (`18..23`) jeder Seite sitzen auf den `6` freien Waagerechten $W_0 \setminus W_0'$ bzw. $W_0' \setminus W_0$ (statt auf $d = 0$, was `162` Vertreter spart); die `2` gemeinsam freien Waagerechten $W_0 \cap W_0'$ (`54` Punkte) nehmen bis zu `54` Paare zwischen Vollgeraden-Symbolen auf; die übrigen `v - 24` Vollgeraden-Symbole (`24..v-1`) sitzen auf $d = 0$.

#### Ergebnisse & Prüfung (`scripts/phase9_q27_trace_check.py`, `scripts/phase7_lift.py --check-m`, `scripts/phase8/untergrenze.py`)

| $v$ | Parameter `(sc_a1, c0_a1, sc_a2, c0_a2, sc_b1, c0_b1, sc_b2, c0_b2)` | Basis Phase 8 (`data/phase8_repro/`) | Neu `|R|` | Delta `|R|` | `M(R)` Lücken (`phase7_lift.py --check-m`) | Vorhersage $t = 4$ (`|R| * 729`) vs. Tabelle `@ 697325b` | Datei & SHA-256 |
| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| `24` | `(1, 0, 1, 3, 4, 12, 4, 18)` | `930` | **`923`** | **`-7`** | `0` (`PASS`) | `672.867` (Phase 8: `677.970`; Tabelle: `707.271`) | `data/phase9_explore/R_q27_v24_m923.txt` (`29d6f580…3657`) |
| `25` | `(1, 0, 3, 5, 5, 9, 9, 3)` | `968` | **`948`** | **`-20`** | `0` (`PASS`) | `691.092` (Phase 8: `705.672`; Tabelle: `707.273`) | `data/phase9_explore/R_q27_v25_m948.txt` (`3c34b7e0…98e6`) |
| `26` | `(1, 0, 3, 5, 5, 9, 9, 3)` | – | `984` | – | `0` (eigener Zähler) | `717.336` (nicht abgelegt) | nicht gespeichert |
| `27` | `(1, 0, 3, 5, 5, 9, 9, 3)` | – | `1023` | – | `0` (eigener Zähler) | `745.767` (nicht abgelegt) | nicht gespeichert |

- **Determinismus (2× byte-identisch):** `cmp -s` `PASS` für beide abgelegten Listen (`0,574 s` Erstlauf / `0,569 s` Repro), `data/phase9_explore/SHA256SUMS` `2/2 OK`.
- **Lemma-J-Prüfung (`scripts/phase8/untergrenze.py listen`):** `0` Verletzungen (`2/2`), je `18 / 18` Klassen ohne volle Waagerechte, kleinster Lemma-J-Schlupf `0`.
- **Belegart:** Deterministische Listenkonstruktion, `M(R)` `0` Lücken in zwei unabhängigen Zählern (`phase9_q27_trace_check.py`, `scripts/phase7_lift.py --check-m`); alle abgeleiteten Arrays für $t \ge 3$ sind **Vorhersage** (nicht geliftet/dual-verifiziert). Literaturprüfung nach `RULES.md` Regel 2c und Drittprüfung stehen aus.

---

## Nachtrag: Angepasste Option A (`q = 27` Lifts `t = 3, 4`) und 180-s-Läufe (`all1_7 m = 67`, `C_1 m = 33`)

### N.1 `q = 27` End-to-End-Lifts in `/tmp/phase9/` (nicht committet)

| Datei (`/tmp/phase9/`) | `(t, k, v)` | `N` | Dateigröße Bytes (`MiB`, `<= 50 MiB`?) | SHA-256 | `ca_verify` POS / NEG (1 Zeile entf.) | `verify_independent.py` POS / NEG |
| --- | --- | ---: | ---: | --- | --- | --- |
| `CA_24921_3_29_24.txt` | `(3, 29, 24)` | `24.921` | `1.825.875` (`1,7413 MiB`, ja) | `33954168f61a0b35b92b0e507d83ac328e9a88e19fb39b9b6b439c823abfe90e` | Exit `0` (`0,06 s`) / Exit `1` (`191/3654` Lücken) | Exit `0` (`21,96 s`) / Exit `1` (`191` Lücken, `22,43 s`) |
| `CA_25596_3_29_25.txt` | `(3, 29, 25)` | `25.596` | `1.901.790` (`1,8137 MiB`, ja) | `1d155be3938de02fbcf3c07bdd2a21c8c477f35d6cde2d86c533a080e95fda74` | Exit `0` (`0,06 s`) / Exit `1` (`2434/3654` Lücken) | Exit `0` (`23,61 s`) / Exit `1` (`2434` Lücken, `23,46 s`) |
| `CA_672867_4_29_24.txt` | `(4, 29, 24)` | `672.867` | `49.259.988` (`46,9780 MiB`, **ja**) | `ba70713f10b7539fe44cba550a1e3426c124bc14eaa38c74c1136982e81f5a92` | Exit `0` (`94,37 s`) / Exit `1` (`1260/23751` Lücken, `93,93 s`) | **nicht gelaufen (Shell-Cap, Ziel GitHub Actions)** |
| `CA_691092_4_29_25.txt` | `(4, 29, 25)` | `691.092` | `51.307.020` (`48,9302 MiB`, **ja**) | `ea88c870f9ba1764aea2862587f64cb5e377edb7de3110fa86f7cbe4f8bbaf07` | Exit `0` (`101,50 s`) / Exit `1` (`13624/23751` Lücken, `99,92 s`) | **nicht gelaufen (Shell-Cap, Ziel GitHub Actions)** |

- **`t = 3`:** Vollständig dual-verifiziert (POS `PASS` & NEG `FAIL` auf beiden Verifiern).
- **`t = 4`:** Beide Dateien liegen strikt unter `52.428.800 Bytes` (`50,00 MiB`); `verifiers/ca_verify` POS `Exit 0` / NEG `Exit 1` bestanden; `verify_independent.py` ausdrücklich nicht gestartet (Shell-Cap, Ziel GitHub Actions) — daher nach `RULES.md` §3 noch kein dual-verifizierter Kandidat.

### N.2 Gezielte 180-s-Läufe (`scripts/phase9_coset_search.c` mit `SOLVE1_RAY`-Fokus, `--selftest` `5000/5000 PASS`)

| Lauf | Ziel `CA(N; t, k, v)` | Modus & Seed | Laufzeit | Evals (`evals/s`) | Moves (`moves/s`) | Ergebnis | Belegart |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 2.1 | `CA(469; 3, 9, 7)` (`< 472`) | `all1_7 m=67 --scale-inv`, `seed=101`, `2T` | `178,043 s` | `922,0M` (`5,18M/s`) | `105,6M` (`593k/s`) | **`TIMEOUT (best_unc=6)`** | Heuristische Suche erfolglos (180 s Cap; Plateau identisch zu 58 s) |
| 2.2 | `CA(825; 4, 7, 5)` (`33` Cosets) | `c1 m=33 --scale-inv`, `seed=101`, `2T` | `178,016 s` | `1,194B` (`6,71M/s`) | `128,4M` (`722k/s`) | **`TIMEOUT (best_unc=2)`** | Heuristische Suche erfolglos (180 s Cap; Plateau identisch zu 58 s) |

### N.3 Verallgemeinerung auf $q = p^3$ (Gegenprobe $q = 8 = 2^3$)

- Für jede Primzahlpotenz $q = s^3$ liefert $B_{\mathrm{tr}}$ (Größe $q + s^2 + 1$, Profil B: $m = s^2 + 1$, Punktverteilung $(s^2, s^{s^2})$) je Seite $(s - 1) s^2 = q - s^2$ auf $d \ne 0$ disjunkte Klassen mit `100 %` exakter 1-Punkt-Paarabdeckung auf $d \ne 0$, sowie $(s - 1) s$ leere Waagerechte für Vollgeraden-Symbole.
- Direkte Gegenprobe in `GeneralGF(8)` ($q = 8 = 2^3$, $s = 2$): `4` `a`-Klassen $\times$ `4` `b`-Klassen (Größe `12`, $m = 5$), `16/16` eindeutige Paar-Treffer auf $d \ne 0$, `max |S_a0 cap S_b0| = 3/4` $\implies$ bei $v = 6$ ergibt die Gitterformel `|R| = 79` (schlechter als Bauart §14 mit `70`, ebenso `v = 8` schlechter als Phase 7 `91`). Asymptotisch gilt $|R| = q^2 + O(q^{5/3})$, sodass das Gitter ab $q = 27$ gewinnt.
