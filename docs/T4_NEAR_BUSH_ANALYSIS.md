# Phase 5B-1: Struktur-Inspektion, `PG(3, 7)`-Geometrie & Machbarkeitsanalyse für `t = 4 NEAR_BUSH` (`k = q + 2 → q + 3`)

- **Datum:** 2026-11-25
- **Branch:** `exp/phase5b-t4-nearbush-recon` (Basis: `origin/main` @ `8f33f7d`)
- **Live-Abgleich `chrispbsmolen/ca-tools`:** Commit `c5f447da7f3efcc1b39cdea6340463ec7e90e006` (`2026-11-25T17:49:34Z`, rein lesend via `gh api`)
- **Reproduktionsskript:** [`scripts/analyze_t4_nearbush.py`](../scripts/analyze_t4_nearbush.py) (Pure Python `std`-only, Laufzeit `5,06 s` auf 2 vCPUs)
- **Governance-Status:** `verifiers/`, `submission/` und `results/` in diesem Branch vollständig unverändert; Regel-7-Sperre (`t = 3 PGL(2,q)+CCL` / PR #88) eingehalten; alle erzeugten Test-Arrays ausschließlich im Scratch-Verzeichnis abgelegt.

---

## 1. Frischer Live-Abgleich (`chrispbsmolen/ca-tools @ c5f447d`)

Gegenüber dem Phase-5-Recon-Stand (`083a093`, `2026-11-25T13:32:06Z`) liegt `chrispbsmolen/ca-tools/main` **9 Commits voraus** (`c5f447da7f3efcc1b39cdea6340463ec7e90e006`).

- **Geänderte Zellen in `table/ca_frame.csv` seit `083a093`:** exakt **3 Zellen** (Commit `5d4fdd0`, `smolen-2026-11-formula-arrays-2`): `(3, 704, 2) = 53`, `(5, 68, 2) = 136`, `(5, 110, 2) = 218` (jeweils `CITED/none → CITED/file`). **Keine einzige `t = 4`-Zelle hat sich geändert.**
- **Offene Pull Requests (`chrispbsmolen/ca-tools`):** exakt **1** offener PR (`#88`, `Justus42`, `t = 3`), **0 Überschneidungen** mit `t = 4 NEAR_BUSH`.

### Relevante `t = 4 NEAR_BUSH`-Zellen am Commit `c5f447d`

| `q` | Bush-OA `k = q + 1` | `k = q + 2` (Tier / Quelle / Bauart) | `k = q + 3`..Plateau (Tier / Quelle / Bauart) | Sprung `q + 2 → q + 3` |
| :---: | :---: | --- | --- | :---: |
| `7` | `(4, 8, 7) = 2401` (`VER`) | `(4, 9, 7) = 3556` (`VER`, Sitjar v1.5, PR #20: `508` Cosets des All-Ones-Codes über `Z_7`) | `k = 10..15: 4459` (`CIT`, `k = 14` Colbourn–Lanús `3-Restricted SCPHF`, `k = 15` Torres-Jimenez–Izquierdo-Marquez 2024 `CPHF(2; 15, 7, 4)`) | `+903` (`+25,4 %`) |
| `8` | `(4, 9, 8) = 4096` (`VER`) | `(4, 10, 8) = 6101` (`VER`, Bai XunDi 2026, PR #36: Row-Deletion + Nurmela-Tabu-Postop von NCK `6125`) | `k = 11..15: 7680` (`CIT`, Colbourn–Lanús `3-Restricted SCPHF RE`) | `+1579` (`+25,9 %`) |
| `9` | `(4, 10, 9) = 6561` (`VER`) | `(4, 11, 9) = 9801` (`VER`, Bai XunDi 2026, PR #10: `poly2` + Pencil-Cover auf `AG(2, 9)`) | `k = 12..17: 12393` (`CIT`, Colbourn–Lanús `3-Restricted SCPHF RE`) | `+2592` (`+26,4 %`) |
| `11` | `(4, 12, 11) = 14641` (`VER`) | `(4, 13, 11) = 21901` (`VER`, Bai XunDi 2026, PR #11: `poly2` + Pencil-Cover auf `AG(2, 11)`) | `k = 14: 27544` (`CIT`, NCK `OA fuse fuse postop`); `k = 15..20: 27951` (`CIT`, `3-Restricted SCPHF RE`) | `+5643` / `+6050` |
| `13` | `(4, 14, 13) = 28561` (`VER`) | `(4, 15, 13) = 42757` (`VER`, Bai XunDi 2026, PR #10: `poly2` + Pencil-Cover auf `AG(2, 13)`) | `k = 16..21: 54925` (`CIT`, Colbourn–Lanús `3-Restricted SCPHF RE`) | `+12168` (`+28,5 %`) |
| `16` *(Ref.)* | `(4, 17, 16) = 65536` (`VER`) | `(4, 18, 16) = 83519` (`VER`, CKRS 2010 Lemma 3.1 Symbol-Fusion aus `OA(17^4; 4, 18, 17)`) | `k = 19: 114489` (`VER`, Sitjar v1.8 Postop von `114495`) | `+30970` |

*Hinweis zu `submissions/*/HOW.md`:* In `ca-tools` werden gemergte Einreichungsordner nach Übernahme in `table/` entfernt (HTTP 404). Die genaue Herkunft wurde über `table/ca_table.csv.gz` (`construction`, `source_detail`) und rein lesenden Abruf der PR-Beschreibungen `#10`, `#11`, `#20`, `#36` bestätigt.

---

## 2. Struktur-Inspektion der verifizierten `k = q + 2`-Arrays (`q = 7, 8, 9`)

Die drei Arrays wurden temporär ins Scratch-Verzeichnis geladen (nicht committet) und mit [`scripts/analyze_t4_nearbush.py`](../scripts/analyze_t4_nearbush.py) vollständig vermessen:

| Datei (Scratch, @ `c5f447d`) | SHA-256 (Prefix) | Konst. Zeilen | Symmetrie-Check | Präfix-`OA(q^4; 4, q+1, q)` | Befund |
| --- | --- | :---: | --- | :---: | --- |
| `CA_3556_4_9_7.txt` | `28224181…` | `0` | `Z_7`-Shift: **`3556/3556`**; `AGL(1,7) ×3`: `28/3556` | `0/70` | Exakt **`508` vollständige Cosets** des All-Ones-Codes über `Z_7` (`508 · 7 = 3556`), alle 9 Spalten perfekt balanciert (`508`/Symbol). Spart `-21` Zeilen gegenüber `poly2` (`3577`), weil die OA-Struktur vollständig zugunsten von `Z_7`-Coset-Suche aufgegeben wurde (Sitjar 2026). |
| `CA_6101_4_10_8.txt` | `1d23048f…` | `1` (Idx `372`) | `Z_8`-Shift: `0/6101`; `GF(8)`-XOR: `0/6101` | `0/126` | Unbalancierte Spalten (`728..823`), keine algebraische Gruppeninvarianz. Konsistent mit Bai XunDis Dokumentation: Row-Deletion + Nurmela-Tabu-Reparatur von `CA(6125; 4, 10, 8)` (Dwyer/NCK; `-43` unter `1,5 · 8^4 = 6144`). |
| `CA_9801_4_11_9.txt` | `827ee427…` | `0` | `Z_9`-Shift: `0/9801` | **`210/210`** | **Exakte `poly2`-Pencil-Cover-Zerlegung** (s. u.). |

### Mechanismus von `poly2` mit Pencil-Cover auf `AG(2, q)` (Bai XunDi 2026; Vorarbeit: Bush 1952)

Die Inspektion von `CA(9801; 4, 11, 9)` legt den exakten Aufbau offen:
1. **Hauptblock (`rows[0:6561]`, `q^4 = 6561`):** Auf den Spalten `0..9` sind **`210/210` 4-Mengen ein exaktes Bush-`OA(6561; 4, 10, 9)`** (`f(x) = a + b x + c x^2 + d x^3` für `x ∈ GF(9)`, `col 9 = d`).
2. **Spalte `10` im Hauptblock:** Nimmt ausschließlich **`(q + 1)/2 = 5` Symbole** `{0, 1, 2, 3, 4}` an, mit Gesamtanzahlen `{0: 1377, 1: 1296, 2: 1377, 3: 1215, 4: 1296}` (= `{17, 16, 17, 15, 16} · 81`). Geometrisch wird die affine Ebene `AG(2, q)` der Parameter `(c, d)` durch ein Geradenbüschel durch `(0, 0)` in `(q + 1)/2` Blocking-Sets von Geraden (jeweils 2 sich im Ursprung schneidende Geraden der Größe `2q - 1`) zerlegt. Da jede Gerade in `AG(2, q)` mindestens `q - 1` andere Richtungen trifft, schneidet jede Gerade, die einen 3-Tupel-Fixpunkt auf `cols 0..9` bestimmt, jedes der `(q + 1)/2` Blocking-Sets — außer für die `(q - 1)/2` Symbole, denen der gemeinsame Scheitel `(0, 0)` weggenommen wurde.
3. **Restblock (`rows[6561:9801]`, `3240 = ((q^2 - 1)/2) · q^2` Zeilen):** Zerfällt exakt in:
   - **`(q - 1)/2 = 4` exakte `OA(729; 3, 9, 9)`-Blöcke** für `col 10 ∈ {5, 6, 7, 8}` (`84/84` Tripel auf `cols 0..8`), jeder in `9/9` `OA(81; 2, 9, 9)`-Slices nach `col 9` zerlegt (`4 · 729 = 2916` Zeilen), plus
   - **`(q - 1)/2 = 4` Scheitel-Reparaturblöcke à `q^2 = 81` Zeilen** (`col 10 = 1: 81`, `col 10 = 3: 162`, `col 10 = 4: 81`, zusammen `324` Zeilen).

Damit ist die universelle Formel für ungerade Primzahlpotenzen `q` erklärt:
$$N_{\text{poly2}}(q) = q^4 + \frac{q - 1}{2} q^3 + \frac{q - 1}{2} q^2 = q^4 + \frac{q^2 - 1}{2} q^2$$
Sie liefert exakt `q = 7: 3577`, `q = 9: 9801`, `q = 11: 21901`, `q = 13: 42757` — in voller Übereinstimmung mit `ca-tools` für `q = 9, 11, 13` (und `+21` über Sitjars `Z_7`-Coset-Lösung `3556` bei `q = 7`).

---

## 3. `PG(3, 7)`-Geometrie, lineare untere Schranke & Positivkontrollen

### 3.1 Exakte Zählung der koplanaren 4-Mengen außerhalb der Twisted Cubic in `PG(3, 7)`

Die Twisted Cubic `TC = {(1, x, x^2, x^3) : x ∈ GF(7)} ∪ {(0, 0, 0, 1)}` hat `8` Punkte; außerhalb liegen `400 - 8 = 392` projektive Punkte (`scripts/analyze_t4_nearbush.py`, `0,51 s`):

- **`k = 9` (1 Zusatzpunkt):** Verteilung der linear abhängigen 4-Mengen über alle `392` Punkte: `{5: 56, 7: 168, 9: 112, 10: 56}`. Minimum: **`5/126` abhängige 4-Mengen** (Zeuge `p_1 = (0, 0, 1, 0)`), ergibt `5 · 6 · 7^3 = 10.290` fehlende 4-Tupel nach dem linearen `7^4 = 2401`-Block.
- **`k = 10` (2 Zusatzpunkte):** Globales Minimum über alle `C(392, 2)` Punktpaare bewiesen: **`12/210` abhängige 4-Mengen** (Zeuge `p_1 = (0, 0, 1, 0)` mit `d_1 = 5`, `p_2 = (0, 1, 1, 6)` mit `d_2 = 5`, gemeinsame `d_{12} = 2`), ergibt `12 · 6 · 7^3 = 24.696` fehlende 4-Tupel.

### 3.2 Beweis einer harten unteren Schranke für unveränderte lineare `[k, 4]_q`-Grundblöcke

> **Beobachtung (Lineare Augmentations-Schranke):** Sei `G` der Code eines linearen `[k, 4]_q`-Blocks (`q^4` Zeilen) mit mindestens einer linear abhängigen 4-Menge `S` (für `k >= q + 2` bei ungeradem `q` unvermeidbar nach dem Satz von Segre/Bush). Auf `S` hat die Projektion von `G` Rang `<= 3`, überdeckt also höchstens `q^3` der `q^4` möglichen 4-Tupel. Daher fehlen auf `S` **allein** mindestens `(q - 1) q^3` Tupel. Jede Erweiterung von `G` um zusätzliche Zeilen (ohne Zeilen von `G` zu ändern) erfüllt zwingend:
> $$N \ge q^4 + (q - 1) q^3 = (2q - 1) q^3.$$

Diese Schranke ergibt für `q = 7, 8, 9, 11, 13` exakt **`4459`, `7680`, `12393`, `27951`, `54925`** — punktgenau die Werte der `3-Restricted SCPHF`-Stufe (Sherwood–Martirosyan–Colbourn / Colbourn–Lanús) in `ca-tools`! Sie wird scharf angenommen durch `G` plus `(q - 1)` geeignete Verschiebungen eines 3-dimensionalen Unterraums `H ⊂ G`, der alle 1D-Kerne der abhängigen 4-Mengen meidet (`PC-2` unten).

**Strategische Konsequenz:** Um bei `k = q + 3` **strikt unter** `q^4 + (q - 1) q^3` zu kommen, genügt keine reine Augmentation eines unveränderten linearen `[k, 4]_q`-Grundblocks. Erforderlich ist entweder:
1. eine **nichtlineare** Erweiterung des `OA(q^4; 4, q + 1, q)`-Kerns (z. B. `Double-poly2`), oder
2. das **Aufbrechen** der linearen OA-Struktur (z. B. `Z_q`-Cosets wie bei Sitjar oder lokale Zell-Reparatur / Post-Optimierung wie bei Bai XunDi).

### 3.3 Dual-verifizierte Positivkontrollen (ausschließlich im Scratch)

Beide strukturellen Anker wurden mit [`scripts/analyze_t4_nearbush.py`](../scripts/analyze_t4_nearbush.py) deterministisch erzeugt und gegen beide unveränderte Verifier geprüft:

| ID | Array (Scratch) | Bauart | `ca_verify` | `verify_independent.py` | SHA-256 (Prefix) | Urteil |
| :---: | --- | --- | :---: | :---: | --- | :---: |
| **PC-1** | `pc1_poly2_CA_3577_4_9_7.txt` | `poly2` Pencil-Cover (`q = 7, k = 9`) | `0,01 s` PASS | `0,1152 s` PASS | `3cb260cc…` | **DUAL_PASS** |
| **PC-2** | `pc2_pg3_CA_4459_4_10_7.txt` | `PG(3, 7) + 6H` (`q = 7, k = 10`, erreicht untere Schranke exakt) | `0,01 s` PASS | `0,1930 s` PASS | `e732beec…` | **DUAL_PASS** |

---

## 4. Billig-Tests auf `k = q + 3`: Ungerade Obstruktion (`q = 7`) vs. Hyperoval-Double-`poly2` (`q = 8`)

### 4.1 Billig-Test `q = 7, k = 10` (`Double-poly2`, `N = 4321`) — Exakte Lokalisierung der ungeraden Obstruktion

Koppelt man zwei orthogonale Pencil-Cover-Spalten `col 8 = pencil(c, d)` und `col 9 = pencil(a, b)` an das Bush-`OA(2401; 4, 8, 7)`, fügt je `3 · 49 = 147` Scheitel-Reparaturen (`294` Zeilen), `3 · 343 = 1029` `OA(343; 3, 8, 7)`-Blöcke für `col 8 ∈ {4, 5, 6}` (geschnitten nach dem internen Punkt `(1, 0, 1)` von `PG(2, 7)` via `s = (a + c) mod 7`), `3 · 4 · 49 = 588` Rest-Slices für `col 9 ∈ {4, 5, 6}` sowie `9` Kollisionszeilen `(0^8, v_8, v_9)` (`v_8, v_9 ∈ {1, 2, 3}`) hinzu, erhält man `N = 4321` Zeilen (`-138` unter `4459`). Die exakte Diagnose in [`scripts/analyze_t4_nearbush.py`](../scripts/analyze_t4_nearbush.py) ergibt:

- `miss_0_7 = 0`, `miss_only_8 = 0`, `miss_only_9 = 0`,
- **`miss_both_8_9 = 5544` auf exakt `4` von `28` 4-Mengen** des Typs `(c_0, c_1, 8, 9)`.

**Geometrische Ursache:** Nach dem Satz von Bush/Segre existiert für ungerades `q` kein `OA(q^3; 3, q + 2, q)`. In `PG(2, 7)` liegt jeder interne Punkt (wie `(1, 0, 1)`) auf genau `(q + 1)/2 = 4` Sekanten des `(q + 1)`-Kegelschnitts; genau diese `4` Paare von Spalten aus `{0..7}` werden durch die Schnitt-Koordinate `s = a + c` linear abhängig. Naives Ersetzen der `3` `OA(343)`-Blöcke durch `CA(472; 3, 9, 7)` erhöht die Zeilenanzahl auf über `4459`. Für ungerades `q = 7, 9, 11, 13` ist naives `Double-poly2` damit strukturell blockiert; echte Verbesserungen erfordern hier eine andere Bauart (z. B. `Z_7`-Coset-Suche `< 637` Cosets bei `q = 7, k = 10`, oder Post-Optimierung / nichtlineare Reparatur).

### 4.2 Billig-Test `q = 8, k = 11` (`Hyperoval Double-poly2`, `N = 7561`) — Dual-verifizierter Scratch-Prototyp

In Charakteristik `2` (`q = 2^m`) verschwindet die obige Obstruktion vollständig: Jeder Kegelschnitt in `PG(2, 2^m)` besitzt einen **Nukleus** `(0, 1, 0)`, der ihn zu einem `(q + 2)`-**Hyperoval** erweitert (Bush 1952). Damit existiert ein exaktes `OA(q^3; 3, q + 2, q)` — für `q = 8` ein `OA(512; 3, 10, 8)` (`120/120` Tripel in `analyze_t4_nearbush.py` geprüft), das durch den Nukleus `b ∈ GF(8)` in **8 exakte, paarweise disjunkte `OA(64; 2, 9, 8)`-Slices** zerfällt.

Kombiniert man zwei `AG(2, 8)`-Pencil-Cover-Spalten `col 9 = pencil8(c, d)` und `col 10 = pencil8(a, b)` (je `4` Symbole `{0..3}` im Hauptblock, wobei Symbol `0` die 3 Geraden `{u=0, v=0, v=7u}` trägt und `1, 2, 3` je 2 Geradenpaare) mit der Hyperoval-Slice-Teilung (`c_{10} = b ⊕ (m_9 - 4)` in Schritt 4 und komplementäre Slices `b ∈ {0..3}` in Schritt 5), erhält man für gerades `q = 2^m >= 8` ohne Suche die geschlossene Bauart:

| Baustein (`q = 8, k = 11`) | Allgemeine Anzahl (`q = 2^m`) | Zeilen (`q = 8`) | Funktion |
| --- | :---: | :---: | --- |
| 1. Bush-`OA(q^4; 4, q + 1, q)` + 2 Pencils | `q^4` | `4096` | Deckt `cols 0..8` sowie `{0..3}` auf `col 9`, `col 10` (außer Scheitel) |
| 2. Scheitel-Reparatur `col 9 ∈ {1..q/2 - 1}` | `(q/2 - 1) · q^2` | `192` | Repariert `(c, d) = (0, 0)` für `col 9` |
| 3. Scheitel-Reparatur `col 10 ∈ {1..q/2 - 1}` | `(q/2 - 1) · q^2` | `192` | Repariert `(a, b) = (0, 0)` für `col 10` |
| 4. `q/2` Hyperoval-`OA(q^3; 3, q + 2, q)`-Blöcke | `(q/2) · q^3` | `2048` | Deckt `col 9 ∈ {4..7}` komplett & liefert je 4 Slices für `col 10 ∈ {4..7}` |
| 5. Rest-Slices `b ∈ {0..q/2 - 1}` für `col 10 ∈ {4..7}` | `(q/2)^2 · q^2` | `1024` | Vervollständigt `col 10 ∈ {4..7}` zum vollen `OA(512)` |
| 6. Scheitel-Kollisionszeilen `(0^{q+1}, v_9, v_{10})` | `(q/2 - 1)^2` | `9` | Deckt den eindeutigen 4D-Schnitt `(a, b, c, d) = (0, 0, 0, 0)` |
| **Summe** | `q^4 + (q/2)q^3 + (q^2/4 + q - 2)q^2 + (q/2 - 1)^2` | **`7561`** | **0 fehlende 4-Tupel, 0 Duplikate** |

**Ergebnis der Dual-Verifikation (Scratch-Datei `test_hyperoval_CA_7561_4_11_8.txt`, SHA-256 `821c23ea…`):**
- `./verifiers/ca_verify`: **`0,01 s` PASS** (`330/330` 4-Mengen, `4096` Tupel).
- `python3 verifiers/verify_independent.py`: **`0,6270 s` PASS** (`1.351.680` Interaktionen).
- **Tabellenvergleich (`chrispbsmolen/ca-tools @ c5f447d`):** `7561` ist **119 Zeilen kleiner als die Tabelle am Commit `c5f447d`** (`7680`, `CITED`, `3-Restricted SCPHF RE`).
- **Einordnung anderer gerader `q = 2^m`:**
  - `q = 4, k = 7`: Formel liefert `401 > 384` (Tabellenwert `384`, `CPHF 3-stage`).
  - `q = 16, k = 19`: Formel liefert `118.321 > 114.489` (bereits geschlagen durch Sitjar v1.8 Postop `114.489`).
  - `q = 8, k = 11`: **`7561 < 7680` (`-119`)** — eindeutiger struktureller Treffer im Bereich `v <= 16`.

*Hinweis (Regel 4 & Phase-5B-1-Sperre):* Die Datei `test_hyperoval_CA_7561_4_11_8.txt` verbleibt in Phase 5B-1 ausschließlich im Scratch-Verzeichnis (`results/` bleibt unberührt). Vor einer späteren Meldung nach außen sind in jedem Fall der Prüfbericht zu PR #88 sowie sämtliche Schritte aus `RULES.md` Punkt 2 (insbesondere Literaturprüfung und Drittprüfung) einzuhalten.

---

## 5. Nüchterne Bewertung der nächsten Optionen für Phase 5B-2

1. **Option 5B-2A (primär, deterministisch + lokale Post-Optimierung auf `q = 8, k = 11`):**
   - Startet mit einem bereits dual-verifizierten deterministischen Anker **`CA(7561; 4, 11, 8)`** (`-119` unter `c5f447d`, `0,64 s` Dual-Verify).
   - Konkrete Forschungsfragen: (a) Lassen sich die `9` Scheitel-Kollisionszeilen oder weitere Zeilen via Row-Deletion + lokaler Nurmela/Tabu-Reparatur (analog Bai XunDis `6125 → 6101` auf `k = 10`) unter `7561` drücken? (b) Lässt sich das Hyperoval-Double-`poly2`-Prinzip auf `k = 12` (z. B. `7680`-Plateau `k = 11..15` auf `q = 8`) verallgemeinern?
   - Positivkontrolle in derselben Struktur: `CA(7561; 4, 11, 8)` selbst (bzw. `CA(6125; 4, 10, 8) → < 6125` für den Post-Op-Reduzierer).
2. **Option 5B-2B (sekundär, explorativ auf ungeradem `q = 7, k = 10`):**
   - `Z_7`-Coset-Suche (Bauart Sitjar 2026) mit Ziel `M < 637` Cosets (`N = 7M < 4459`).
   - Positivkontrolle in derselben Struktur: Sitjars `k = 9`-Zelle (`M = 508..511` Cosets, `N = 3556..3577`).
   - Höheres Risiko als 5B-2A, da bei `k = 10` (`C(10, 4) = 210` 4-Mengen, `210 · 343 = 72.030` Coset-Tupel) erst durch ein hartes Gate-0-Experiment geprüft werden muss, ob ein Zero-Dep-Solver auf 2 vCPUs überhaupt `M = 511` auf `k = 9` in `<= 30 s` reproduziert.

Der verbindliche Bau- und Gate-Vertrag für Phase 5B-2 ist in [`STATUS.md`](../STATUS.md) hinterlegt.
