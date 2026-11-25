# Systematischer `t=3` Target-Scan (`docs/TARGET_SCAN_t3.md`)

Stand: **2026-11-24** | Branch: `exp/t3-target-scan` | Reproduzierbares Analysescript: [`scripts/scan_t3_targets.py`](../scripts/scan_t3_targets.py) (Pure Python `std`-only).
Datenbasis: `chrispbsmolen/ca-tools` @ Commit `4f3c95d` (`2026-11-25T00:10:02Z`, inkl. Submission `laverdi-2026-11`), abgerufen via `gh api` nach `/tmp/` (nicht ins Repo committet).

---

## 1. Schema-Übersicht (`table/ca_table.csv.gz` & Metadaten)

- **Dateiumfang:** `16.052` Zeilen gesamt, davon `2.220` für `t = 3` und `1.225` für `t = 3, v = 4..14` (`218` Einträge direkt bei `k = 6..35`: `111 VERIFIED`, `107 CITED`; Eintragsdatum `entered`: `2026-08-23` bis `2026-11-24`).
- **Exakter CSV-Header (17 Spalten):**
  `t, v, k, N, tier, source_id, source_detail, snapshot_id, array_sha256, verify_stamp, entered, notes, lb, lb_evidence, construction, builds_on, family_sha256`
  *(Hinweis: `lb`/`lb_evidence` sind in `ca_table.csv.gz` leer; bewiesene Untergrenzen liegen separat in `table/lower_bounds.csv`, Konstantzeilenzahlen verifizierter Binär-Arrays in `table/MANIFEST.csv`, Zitationen/Familien in `table/references.csv`, `table/families.csv`, `table/lexicon.csv`.)*
- **Monotone Hüllkurve:** Für Primzahlpotenzen fehlen kleine `k` wegen orthogonaler Arrays `OA(v^3; 3, v+1, v)` (bzw. `k=10` bei `v=8`). Alle `N_rec(3, k, v)` werden exakt als $N_{\text{rec}}(k) = \min_{k' \ge k} N(k')$ über alle Einträge der Tabelle berechnet.
- **Aktuelle Live-Änderung seit Phase 2:** `(3, 9, 6)` wurde am `2026-11-24` (`laverdi-2026-11`) von `361` auf **`341`** verbessert; `(3, 13, 10)` am `2026-11-24` auf **`1760`**; `(3, 12, 14)` auf **`3372`**; `(3, 16, 8)` am `2026-11-23` (`baig-ai-2026-11`) auf **`848`**.

---

## 2. Verifizierte Symbolgruppen & kombinatorisches Machbarkeitsmodell

Alle Orbitzahlen pro Spaltentripel (`o3` für 3-symbolige, `o2 = 3` für 2-symbolige Tupel) wurden direkt über die Permutationsgruppenaktion auf $\{0, \dots, v-1\}^3$ verifiziert:

| `v` | Gruppe | `\|G\|` | `bin`-Größen | `o3` | `o2` | Orbits/Tripel | Strukturhinweis |
| :---: | --- | :---: | :---: | :---: | :---: | :---: | --- |
| 5 | `AGL(1,5)` *(Ref)* | 20 | 10 | 3 | 3 | 6 | Referenz (`exp/ca-3-9-5`) |
| 6 | `PSL(2,5)` / `PGL(2,5)` *(Ref)* | 60 / 120 | 30 | 2 / 1 | 3 | 5 / 4 | Referenz (`exp/ca-3-k-6`) |
| 7 | `PSL(3,2)` / `AGL(1,7)` | 168 / 42 | 42, 21 / 21 | 2 / 5 | 3 | 5 / 8 | `PSL(3,2)`: 3-sym Orbits `42` (Fano) + `168` |
| 8 | `PSL(2,7)` / `PGL(2,7)` / `A\Gamma L(1,8)` | 168 / 336 / 168 | 56, 28 / 56 / 56 | 2 / 1 / 2 | 3 | 5 / 4 / 5 | `OA(512)` bis `k=10`; `k=12..16` durch `848` besetzt |
| 9 | `PSL(2,8)` / `ASL(2,3)` / `A\Gamma L(1,9)` | 504 / 216 / 144 | 72, 36 / 72 / 72 | 1 / 3 / 4 | 3 | 4 / 6 / 7 | `PSL(2,8)` scharf 3-transitiv (`k <= 16` für `A=2`) |
| 10 | `PSL(2,9)` / `PGL(2,9)` | 360 / 720 | 90, 45 / 90 | 2 / 1 | 3 | 5 / 4 | `PGL(2,9)` scharf 3-transitiv (`k <= 18` für `A=2`) |
| 11 | `PSL(2,11)_11` / `AGL(1,11)` | 660 / 110 | 110 / 55 | 2 / 9 | 3 | 5 / 12 | `PSL(2,11)_11`: 3-sym Orbits `330` + `660` |
| 12 | `PSL(2,11)` / `PGL(2,11)` | 660 / 1320 | 132, 66 / 132 | 2 / 1 | 3 | 5 / 4 | `PGL(2,11)` scharf 3-transitiv (`k <= 22` für `A=2`) |
| 13 | `AGL(1,13)` | 156 | 78 | 11 | 3 | 14 | `OA(2197)` bis `k=14`; hohe Orbit-/Variablenzahl |
| 14 | `PSL(2,13)` | 1092 | 182, 91 | 2 | 3 | 5 | `4*1092 = 2*\|PGL(2,13)\|` (`k <= 26` für `A=4`) |

### Zentrale Strukturerkenntnis des Scans (`PGL(2,q)` / `PSL(2,8)` mit `A = 2`)
1. **Exakte Pareto-Kalibrierung (`cap3`, `bal_cap2`):** Über die exakte obere Konkavhülle aller Partitionen von $k$ in $\le v$ Teile werden 3-sym-Kapazität (`cap3`) und 2-sym-Kapazität bei balancierten Starterzeilen (`bal_cap2`) gegen die empirischen `exp/ca-3-k-6`-Grenzen (`CA(396;3,10,6)` PASS bei `1.47/1.74`; `B=4` bei `k=13` FAIL trotz `1.67`) geprüft.
2. **Deterministisches `A = 2`-Theorem für scharf 3-transitive Gruppen (`o3 = 1`):** Für $k \le 2v - 2$ decken **zwei** explizite Starterzeilen mit disjunkten Wiederholungsblöcken der Länge $k - v + 1$ (z. B. `[0..0, 1..q]` und `[1..q, 0..0]`) **100 % aller 3-sym-Tripel ohne jede Suche** ab (`det_3sym = True`) und decken nebenbei bereits ~20–26 % der 2-sym-Orbits ab.
   - Das verbleibende Problem reduziert sich auf eine **rein binäre (`v=2`) Suche** über $B$ Zeilen ($V_{\text{eff}} = k \cdot B$, Alphabetgröße 2 statt $v$).
   - **Wichtige Unterscheidung `bin = v(v-1)` vs. `v(v-1)/2`:** Ein voller `PGL`-Binärorbit (`bin = v(v-1)`) entspricht einem komplementären Binärpaar $\{r, \bar r\}$ (`2` Zeilen). Verwendet man stattdessen ungeordnete Paar-Patches (`bin = v(v-1)/2`, wie in CCL 2008), liefert jedes bekannte binäre `CA(N_2; 3, k, 2)` mit 1 Konstantzeile (laut `MANIFEST.csv`: `16` nicht-konstante Zeilen für `k=16`, `17` für `k=20`, `19` für `k=28`) eine **konstruktiv garantierte** obere Schranke **ohne Suche**, die bei `v=10 (k=15..18)`, `v=12 (k=19..20)` und `v=14 (k=20..26)` bereits strikt unter dem Live-Rekord liegt! Mit binärer Optimierung auf die durch `A=2` ungedeckten 2-sym-Orbits sind noch deutlich tiefere `N_cand` (`B = 6..7` volle Orbits) erreichbar.

---

## 3. Top 15 Kandidaten (`v = 7..14`, eindeutige `(3, k, v)`-Zellen)

Sortiert nach transparentem Gesamtscore (`scripts/scan_t3_targets.py`: Sweet-Spot `V` bzw. entkoppeltes binäres `V_eff`, kombinatorische Machbarkeit `cap3/bal_cap2`, Rekordluft `N_rec/v^3` + Sprung/Plateau, Orbit-Overhead `<= 15.000`, Gate-0-Anker, Red-Team-Fingerprint-Abzug).

- **Mode:** `SW` = strikt `35 <= V <= 95`; `DEC` = entkoppeltes `PGL(2,q)` (`A=2` deterministisch, aktive binäre Suchdimension `V_eff = k*B` in Klammern).
- **FP (Red-Team-Fingerprint auf `N_rec - v`):** `NO` = kein Gruppenraster; `CK?` = rein arithmetische Identität von CK-Doubling ($N_{\text{CK}}(q) - q = q(q-1)(2q+1)$ ist stets Vielfaches von $v(v-1)$, Konstruktion ist aber **nicht** gruppengeneriert).
- **Gate-0:** `k=...` = direkter Anker bei `k-1` oder `k-2` mit `V <= 85`; `~k=...` = nächstgelegener kleinerer `V <= 85`-Anker (z. B. `A=1` Ordered Design bei `k <= v`).

| # | Mode | Score | Zelle `(3,k,v)` | Gruppe (`bin`) | `N_rec` (`x v³`) | `ΔN` / Pl. | `N_cand` (`save`) | `(A, B)` | `V (V_eff)` | Orbits | `c3 / bc2` | `bin` vs `CAN2` | FP | Gate-0 (`V<=85`) | Aktueller Rekord (`ca_table`) |
| :-: | :-: | :-: | :---: | --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :-: | --- | --- |
| **1** | `DEC` | **93.3** | **`(3, 15, 10)`** | `PGL(2,9)` (`90`) | **2205** (`2.21×`) | `+320` / 2 | **2170** (`-35`) | `(2, 8)` | `150 (120)` | 1.820 | `1.71 / 2.23` | `16/16` | `NO` | `k=13:SOF (V=78)` | `VER` Post-op SA/Tabu (`2026-11-01`) |
| **2** | `DEC` | **84.3** | **`(3, 16, 10)`** | `PGL(2,9)` (`90`) | **2205** (`2.21×`) | `0` / 2 | **2170** (`-35`) | `(2, 8)` | `160 (128)` | 2.240 | `1.70 / 2.23` | `16/16` | `NO` | `k=14:SUB (V=84)` | `VER` Post-op SA/Tabu (`2026-11-01`) |
| **3** | `DEC` | **83.7** | **`(3, 17, 10)`** | `PGL(2,9)` (`90`) | **2232** (`2.23×`) | `+27` / 2 | **2170** (`-62`) | `(2, 8)` | `170 (136)` | 2.720 | `1.69 / 2.22` | `16/17` | `NO` | `~k=10:SOF (V=70)` | `CIT` CK-Doubling (`2026-08-23`) |
| **4** | `DEC` | **83.7** | **`(3, 18, 10)`** | `PGL(2,9)` (`90`) | **2232** (`2.23×`) | `0` / 2 | **2170** (`-62`) | `(2, 8)` | `180 (144)` | 3.264 | `1.69 / 2.22` | `16/17` | `NO` | `~k=10:SOF (V=70)` | `CIT` CK-Doubling (`2026-08-23`) |
| **5** | `DEC` | **80.0** | **`(3, 16, 12)`** | `PGL(2,11)` (`132`) | **3564** (`2.06×`) | `+609` / 1 | **3444** (`-120`) | `(2, 6)` | `128 (96)` | 2.240 | `1.80 / 1.67` | `12/16` | `NO` | `~k=12:SUB (V=84)` | `CIT` OA-Fuse⁴ Post-op (`2026-08-23`) |
| **6** | `DEC` | **77.8** | **`(3, 18, 12)`** | `PGL(2,11)` (`132`) | **3647** (`2.11×`) | `+32` / 1 | **3576** (`-71`) | `(2, 7)` | `162 (126)` | 3.264 | `1.76 / 1.93` | `14/17` | `NO` | `~k=12:SUB (V=84)` | `CIT` OA-Fuse⁴ Post-op (`2026-08-23`) |
| **7** | `DEC` | **77.5** | **`(3, 17, 12)`** | `PGL(2,11)` (`132`) | **3615** (`2.09×`) | `+51` / 1 | **3576** (`-39`) | `(2, 7)` | `153 (119)` | 2.720 | `1.78 / 1.93` | `14/17` | `NO` | `~k=12:SUB (V=84)` | `CIT` OA-Fuse⁴ Post-op (`2026-08-23`) |
| **8** | `DEC` | **67.2** | **`(3, 19, 12)`** | `PGL(2,11)` (`132`) | **3806** (`2.20×`) | `+159` / 2 | **3708** (`-98`) | `(2, 8)` | `190 (152)` | 3.876 | `1.75 / 2.19` | `16/17` | `NO` | `~k=12:SUB (V=84)` | `CIT` CK-Doubling (`2026-08-23`) |
| **9** | `SW` | **66.2** | **`(3, 14, 10)`** | `PGL(2,9)` (`90`) | **1885** (`1.89×`) | `+125` / 1 | **1810** (`-75`) | `(2, 4)` | `84 (56)` | 1.456 | `1.74 / 1.16` | `8/15` | `NO` | `k=13:SOF (V=78)` | `VER` Dwyer `OA+` (`2026-08-23`) |
| **10** | `SW` | **64.2** | **`(3, 13, 9)`** | `PSL(2,8)` (`72`) | **1377** (`1.89×`) | `+182` / 8 | **1305** (`-72`) | `(2, 4)` | `78 (52)` | 1.144 | `1.69 / 1.18` | `8/15` | `CK?` | `k=12:SOF (V=72)` | `VER` CK-Doubling (`2026-11-13`) |
| **11** | `DEC` | **64.2** | **`(3, 20, 12)`** | `PGL(2,11)` (`132`) | **3806** (`2.20×`) | `0` / 2 | **3708** (`-98`) | `(2, 8)` | `200 (160)` | 4.560 | `1.75 / 2.19` | `16/17` | `NO` | `~k=12:SUB (V=84)` | `CIT` CK-Doubling (`2026-08-23`) |
| **12** | `DEC` | **62.4** | **`(3, 21, 12)`** | `PGL(2,11)` (`132`) | **3828** (`2.22×`) | `+22` / 2 | **3576** (`-252`) | `(2, 7)` | `189 (147)` | 5.320 | `1.74 / 1.92` | `14/18` | `NO` | `~k=12:SUB (V=84)` | `CIT` CK-Doubling (`2026-08-23`) |
| **13** | `DEC` | **62.4** | **`(3, 22, 12)`** | `PGL(2,11)` (`132`) | **3828** (`2.22×`) | `0` / 2 | **3576** (`-252`) | `(2, 7)` | `198 (154)` | 6.160 | `1.74 / 1.92` | `14/18` | `NO` | `~k=12:SUB (V=84)` | `CIT` CK-Doubling (`2026-08-23`) |
| **14** | `SW` | **61.2** | **`(3, 14, 9)`** | `PSL(2,8)` (`72`) | **1377** (`1.89×`) | `0` / 8 | **1305** (`-72`) | `(2, 4)` | `84 (56)` | 1.456 | `1.67 / 1.19` | `8/15` | `CK?` | `k=12:SOF (V=72)` | `VER` CK-Doubling (`2026-11-13`) |
| **15** | `SW` | **59.2** | **`(3, 13, 10)`** | `PSL(2,9)` (`90`) | **1760** (`1.76×`) | `+461` / 1 | **1450** (`-310`) | `(3, 4)` | `91` | 1.430 | `1.33 / 1.19` | `8/15` | `NO` | `k=12:SOF (V=84)` | `VER` LaVerdi SA/Tabu (`2026-11-24`) |

### Zusatzbefunde (Striktes `35 <= V <= 95` & `v=14` Erweiterter Horizont)
- **Weitere strikte `SW`-Kandidaten (`35 <= V <= 95`, nicht in Top 15 wegen engerer Kapazität):**
  - `(3, 11, 8)` `PSL(2,7)` / `A\Gamma L(1,8)` (`bin=56`): `N_rec = 812 (1.59×, ΔN=+300, poly2)` → `792 (-20)`, `A=3, B=5, V=88, Orbs=825, FP=NO`, aber `cap3 = 1.25` (so eng wie `A=3` auf `(3,7,6)`, Risiko für `3-sym`-Wand!).
  - `(3, 11, 7)` `PSL(3,2)` (`bin=42`): `N_rec = 637 (1.86×, Pl.=6, CK-Doubling)` → `595 (-42)`, `A=2, B=6, V=88, Orbs=825, bc2=1.78`, aber `cap3 = 1.25` (`A=2` auf `o3=2` extrem eng!).
  - `(3, 12, 9)` `ASL(2,3)` (`bin=72`): `N_rec = 1195 (1.64×, OA+)` → `1089 (-106)`, `A=4, B=3, V=84, Orbs=1320, G0=k=11:EXACT(V=77)`, aber `bc2 = 1.00` (sehr eng auf `2-sym`).
- **Tiefere `N_cand`-Ziele auf Top-1–4 (`v=10`, `PGL(2,9)`):** Neben `B=8 -> 2170` liegen auch `B=7 -> 2080 (-125/-152)` (`V_eff = 105..126`, `bc2 = 1.96`) und `B=6 -> 1990 (-215/-242)` (`V_eff = 90..108`, `bc2 = 1.70`) sauber im Suchbereich; mit `bin=45` (`PSL(2,9)` `A=4`, ungeordnete Binär-Patches) sind `k=16` (`2160/2170`) und `k=18` (`2205/2215`) konstruktiv garantiert unter `2205` bzw. `2232`.
- **Erweiterter Horizont `v=14` (`V > 200`, daher nicht in Top 15):** `(3, 20..22, 14)` `PSL(2,13)` (`N_rec = 6006, 2.19×, CIT CK-Doubling`) mit `A=4` (`= 2*|PGL(2,13)|`), `B=8 (bin=182)` → **`5838 (-168)`** (`Orbs = 5.700..7.700`, `V=240..264`); `(3, 23..26, 14)` (`N_rec = 6279..6383`) mit `A=4, B=9 (bin=182)` → **`6020 (-259 bis -363)`** (mit `19` ungeordneten `91`-Patches sogar `6097/6111` konstruktiv garantiert!).

---

## 4. Sanity-Check: Referenzzellen `v = 5` und `v = 6` (nicht in Top 15)

| Zelle `(3,k,v)` | Gruppe | `N_rec` (`x v³`) | Scanner-Kandidat `N_cand` | `(A, B)`, `V` | `c3 / bc2` | FP | Abgleich mit Phasen 2A–3C |
| :---: | --- | :---: | :---: | :---: | :---: | :-: | --- |
| `(3, 7, 5)` | `AGL(1,5)` | **165** (`1.32×`) | `155 (-10)` | `(6,3)`, `V=63` | `1.43 / 1.00` | `GRP!` | Bestätigt: Live-Rekord ist selbst `AGL(1,5)` (`8*20+5`) |
| `(3, 9, 5)` | `AGL(1,5)` | **185** (`1.48×`) | `165 (-20)` | `(6,4)`, `V=90` | `1.33 / 1.22` | `GRP!` | Bestätigt Gate 1 ABORT: starrer `CK_NRB`/`AGL(1,5)`-Kristall |
| `(3, 9, 6)` | `PSL(2,5)` | **341** (`1.58×`) | `336 (-5)` | `(4,3)`, `V=63` | `1.50 / 1.17` | `NO` | Neu am `2026-11-24` auf `341` gedrückt; `B=3` (wie `G0v6-2`) zu eng |
| `(3, 10, 6)` | `PSL(2,5)` | **366** (`1.69×`) | `336 (-30)` | `(4,3)`, `V=70` | `1.47 / 1.19` | `GRP!` | Bestätigt: Post-op aus `396`-`PSL(2,5)` (`G0v6-3` PASS 0,41s) |
| `(3, 12, 6)` | `PSL(2,5)` | **456** (`2.11×`) | `336 (-120)` | `(4,3)`, `V=84` | `1.45 / 1.18` | `GRP!` | Bestätigt: Live-Rekord ist reines `PSL(2,5)` (`A=5, B=5`) |
| `(3, 13, 6)` | `PSL(2,5)` | **490** (`2.27×`) | `336 (-154)` | `(4,3)`, `V=91` | `1.40 / 1.20` | `NO` | Bestätigt Gate 2 ABORT: `V<=95` zu eng, `A=5/6` ausgereizt (`3C-1/2`) |

---

## 5. Explicit Watch-Out / Vermeidungsliste

Zellen, die nach `N_rec / v^3`, Sprung oder niedrigem `V` zunächst verlockend wirken, aber aufgrund von Gruppen-Belegung, Orbit-Explosion oder kombinatorischer Enge **vermieden** werden sollten:

| Zelle(n) | Gruppe(n) | `N_rec` (`x v³`) | Warnsignal / Ursache | Empfehlung |
| --- | --- | :---: | --- | --- |
| **`(3, 12..16, 8)`** | `PSL(2,7)` / `A\Gamma L(1,8)` | **848** (`1.66×`) | **TRUE_GROUP_RECORD:** `848 = 840 + 8` ist seit `2026-11-23` bereits durch Baigs `C15 × AGL(1,8)`-Gruppenkonstruktion (`baig-ai-2026-11`) besetzt! | **Strikt meiden** (Gruppenraster bereits abgeschöpft) |
| **`(3, 10, 10)`, `(3, 11, 12)`, `(3, 14, 14)`** | `PGL(2,9/11/13)` | `1215` / `2046` / `3549` | **TRUE_GROUP_RECORD:** Bereits exakte CCL-Ordered-Designs (`A=1` `PGL(2,q)` + `11`/`15` Binär-Patches). | Nur als **Gate-0-Anker** nutzen, nicht als Suchziel |
| **`(3, 9..10, 7)`** | `AGL(1,7)` | `472` / `479` (`1.38–1.40×`) | **TIGHT_2SYM (`bc2 = 0.60–0.72`):** Trotz `V = 90` (`A=8/9`) reicht die 2-sym-Kapazität nicht annähernd für `k=9..10`. | **Meiden** (`AGL(1,7)`-Raster zu klein für `V<=95`) |
| **`(3, 13..15, 9)`** (`A=2, B=4`), **`(3, 14, 10)`** (`A=2, B=4`) | `PSL(2,8)` / `PGL(2,9)` | `1377` / `1885` (`1.89×`) | **TIGHT_2SYM (`bc2 = 1.16–1.19`, `bin = 8/15`):** `B=4` (8 Binärzeilen) gegen `CAN(3,14,2)-1 = 15` ist analog zu unserem `3C-2`-Scheitern (`B=4` bei `k=13, v=6` ließ 29 `2-sym`-Orbits offen). | Nur sekundär testen, falls `A=2` extrem viele 2-sym übernimmt; Primärfokus auf `B >= 6..8` (`#1–#8`) |
| **`(3, 11, 7)`** (`A=2, B=6`), **`(3, 11, 8)`** (`A=3, B=5`) | `PSL(3,2)` / `PSL(2,7)` | `637` / `812` | **TIGHT_3SYM (`cap3 = 1.25`):** Analog zu `G0v6-4` (`A=3` auf `(3,7,6)`, `cap3=1.29` → 3 D-Orbits offen); hohes Risiko einer harten 3-sym-Wand. | **Vorsicht** — vorab nur extrem kurzes Gate-1-Screening, falls überhaupt |
| **`(3, 15..24, 11)`**, **`(3, 15..28, 13)`** | `AGL(1,11)`, `AGL(1,13)`, `PSL(2,11)_11` | `1991–2541`, `3289–4225` | **HIGH_V & HUGE_ORBS:** `AGL(1,11/13)` benötigen `V >= 273–360` (`o3 = 9..11`); bei `PSL(2,11)_11` hat `A=3, B=3` nur `bc2 = 0.91`. | **Meiden** (ungeeignet für 2-vCPU-Suche) |
| **`(3, 28..35, 10/12/14)`** | `PSL(2,9/11/13)` | `2.56–2.63×` | **HUGE_ORBS (`16.380–32.725`):** Deutlich über dem `15.000`-Cache-Limit; `V = 250..455` zudem gegen starke `SCPHF+`-/`CK`-Baselines. | **Meiden** (Cache-Thrashing auf 2 vCPUs) |

---

## 6. Fazit & Empfehlung für Zielzelle + Gate 0

Der Scan identifiziert eine klare **Nr.-1-Zielklasse**: **scharf 3-transitives `PGL(2,9)` auf `v = 10` (`k = 15..18`, Plätze #1–#4)** — dicht gefolgt von **`PGL(2,11)` auf `v = 12` (`k = 16..20`, Plätze #5–#8, #11)**.
- **Warum `(3, 15..18, 10)` mit `PGL(2,9)` herausragt:**
  1. `A = 2` (`1440` Zeilen) löst **100 % der 3-sym-Orbits deterministisch** bis $k = 2v - 2 = 18$ (kein 3-sym-Engpass wie in `exp/ca-3-k-6`).
  2. Das Restproblem ist **rein binär (`v = 2`)** auf nur `1.820–3.264` Gesamt-Orbits (voll L1/L2-Cache-resident auf 2 vCPUs) und ohne Gruppen-Fingerprint auf den Live-Rekorden (`2205` / `2232`).
  3. **Gestaffeltes Gewinnpotenzial:** `B = 8` (`2170`, `-35` bei `k=15..16`, `-62` bei `k=17..18`) bzw. `16–17` `bin=45`-Patches (`2160..2215`) sind **kombinatorisch hochwahrscheinlich / konstruktiv gesichert**; anschließend lässt sich `B = 7` (`2080`, `-125/-152`) und `B = 6` (`1990`, `-215/-242`) mit rein binärem Tabu/SAT-Solver systematisch ausloten.
  4. **Schneller Gate-0-Anker:** `PGL(2,9)` bei `k = 10` (`A=1, B=5..6`, `V = 60..70 <= 85`, `N = 1180..1270` nahe Live-Rekord `1215`) oder `k = 8` (`CA(1180; 3, 8, 10)`, `V = 48`) validiert die `PGL(2,9)`-Orbit-Engine und Dual-Verifikation in Sekunden.
