# Literaturprüfung: Zweibahn-`PGL(2,q)` + partitionsabhängige binäre CCL-Matrix (`docs/LITERATURE_CHECK_PGL_CCL.md`)

Stand: **2026-11-25** | Prüfvermerk gemäß [`RULES.md`](../RULES.md) Abschnitt *Meldung nach außen*, Punkt 2c.
Referenzstand Ziel-Tabelle: `chrispbsmolen/ca-tools` @ Commit `7b08aef06cbedaf1b376dbfa68f6aa171a54df4a` (`2026-11-25T03:31:22Z`, 0 offene PRs).

---

## 1. Prüfgegenstand & Vorarbeit

Geprüft wurden Konstruktionsherkunft, Benennung der binären Komponente `C` und mögliche kleinere veröffentlichte Größen für die 13 Pareto-Front-Arrays (`t = 3`, $v \in \{10, 12, 14, 20\}$, 23 Zellen) aus der Bauart:
- Zwei deterministische Bahnen der scharf 3-transitiven Gruppe $\mathrm{PGL}(2, q)$ auf $\mathbb{F}_q \cup \{\infty\}$ ($v = q + 1$, balancierte Spaltenhalbierung $k = |L| + |R|$ mit $|L| = \lfloor k/2 \rfloor, |R| = \lceil k/2 \rceil \le q$, also $k \le 2q$; Blockgröße $2q(q^2 - 1)$ Zeilen),
- kombiniert mit einer allgemeinen (nicht-selbstkomplementären) binären $M \times k$-Matrix $C$ über eine vollständige Orientierung der $\binom{v}{2}$ Kanten von $K_v$ (gerichteter $v$-Zyklus plus Restkanten $u < w$), wahlweise als $C_{\text{const}}$ (`cc=1`, 0 zusätzliche Konstantzeilen) oder $C_{\text{plain}}$ (`cc=0`, $+v$ Konstantzeilen).

## 2. Frage 1 — Einordnung der Zweibahn-`PGL(2,q)` + `C`-Bauart

- **Befund im volltextgeprüften Bestand:** Die exakte Zweibahn-$\mathrm{PGL}(2,q)$-Spaltenhalbierung ($k \le 2q$) mit abgeschwächter, partitionsabhängiger Binärmatrix $C$ wurde im volltextgeprüften Bestand nicht gefunden.
- **Engste fremde Vorarbeit (in dieser Reihenfolge zu nennen):**
  1. **Chateauneuf, Colbourn & Kreher (1999, `ck-cck1999`):** Gruppenaktionen für Covering Arrays der Stärke 3 (inkl. scharf 3-transitiver Gruppenwirkung).
  2. **Chateauneuf & Kreher (2002, `ck-ck2002`):** Stärke-3-Konstruktionen und Verdopplungs-Benchmarks, gegen die ein Großteil unserer Zellen verglichen wird.
  3. **Cohen, Colbourn & Ling (2008, `sa-ccl2008`, Constructions 1–3):** Engster unmittelbarer Vorläufer — kombiniert eine $\mathrm{PGL}(2,q)$-Einbahn-Struktur (Einbahn-Fall $k \le q + 1$) mit einer binären Paar-Expansion über $\binom{v}{2}$ Symbolpaare. Unsere Bauart erweitert dieses Prinzip auf zwei $\mathrm{PGL}(2,q)$-Bahnen ($k \le 2q$) mit balancierter Spaltenhalbierung und reduzierten Musteranforderungen auf gemischten Tripeln.
  4. **Meagher & Stevens (2005, `group-ms2005`):** Gruppenkonstruktionen für Covering Arrays.
  5. **Nurmela (2004, `tabu-n2004`):** Tabu-Suche für Covering Arrays.
- **Abgrenzung:** Maity, Akhtar, Chandrasekharan & Colbourn (2018, `pgl-macc2018`) verwenden $\mathrm{PGL}(2,q)$ für **Stärke $t = 4$** (insbesondere $v = 3$) und werden für unsere $t = 3$-Arrays nicht als `builds_on`-Vorarbeit geführt, sondern lediglich zur Abgrenzung genannt.

## 3. Volltextgeprüfte neuere Einzelquellen (Stand 2026-11-25)

1. **Peter Seelman / IRSI (`ca-strength3-note.pdf`, Draft 2026-10-13):**
   - *Methode:* Fügt einem Bush-Orthogonal-Array eine gefärbte Spalte über $\mathrm{AG}(2,q)$ hinzu (kein $\mathrm{PGL}(2,q)$-Zweistarter).
   - *Betroffene Zellen für unsere Alphabete:* ausschließlich $(3, 13, 10) \in \{1854, 1698\}$, $(3, 15, 12) \in \{3100, 2987, 2891\}$ und $(3, 19, 14) = 5804$.
   - *Überschneidung mit unseren 23 Zellen:* **keine** (unsere Zellen beginnen erst bei $k=15$ für $v=10$, $k=19$ für $v=12$ und $k=20$ für $v=14$).
2. **Théo Nicolas Sitjar (`2611.covering-arrays-strength-bounds`, v1.4 vom 2026-11-13, S. 1–3 inkl. vollständiger Table 1):**
   - *Methode:* $\mathrm{PGL}(2,q)$-Orbitsuche für $t = 4$; für $t = 3$ listet Table 1 insgesamt 20 Einträge.
   - *Überschneidung für $v \in \{10, 12, 14, 20\}$:* Alle Einträge in Table 1 liegen unterhalb unserer Spaltenzahlen (maximal $k = 13$ bei $v=10$, $k = 15$ bei $v=12$, $k = 19$ bei $v=14$, $k = 8$ bei $v=20$).
   - *Hinweis zu S. 4 (Tabelle überholter Einträge):* Dort ist $(3, 16, 10)$ mit Sitjars Wert `2205` als überholt gelistet; die Spalten `smaller`/`source` waren im lokalen Snapshot abgeschnitten. In `ca-tools` führt `table/derived.csv` @ `7b08aef` für $(3, 16, 10)$ den Wert `2178`, der weiterhin deutlich oberhalb unseres verifizierten $N = 2115$ liegt.

## 4. Frage 2 — Einordnung der binären Matrix $C$

- **Benennung / Tabellen:** Für die partitionsabhängige binäre $M \times k$-Matrix $C$ (volle 6 nicht-konstante Muster auf $L^3, R^3$; nur 4 nicht-konstante Muster auf $L^2 R, L R^2$; bei $C_{\text{const}}$ zusätzlich `000` oder `111` auf gemischten Tripeln) wurde kein etablierter eigener Fachbegriff und keine eigene Referenztabelle gefunden. Engster Verwandter ist `TOCA` aus Cohen, Colbourn & Ling (2008).
- **Nachweis der Nicht-Trivialität ($M < \mathrm{CAN}(3, k, 2)$):** $C$ entsteht nicht trivial durch Streichen konstanter Zeilen aus regulären binären Covering Arrays $\mathrm{CA}(N_2; 3, k, 2)$, wie konkrete Werte belegen:
  - $k = 15$: $M = 14 < 17 = \mathrm{CAN}(3, 15, 2)$ (bewiesener exakter Wert; `ccl_k15_m14_cc1.bin`),
  - $k = 18, 19$: $M = 16 < 18$ (best known upper bound für $\mathrm{CAN}(3, k, 2)$; `ccl_k18_m16_cc1.bin`, `ccl_k19_m16_cc1.bin`).

## 5. Frage 3 — Abgleich auf kleinere veröffentlichte Werte

In den folgenden geprüften Quellen wurden **keine** kleineren oder gleichen Werte für unsere 13 Pareto-Zellen (bzw. 23 abgedeckten Zellen) gefunden:
- `chrispbsmolen/ca-tools` @ `7b08aef06cbedaf1b376dbfa68f6aa171a54df4a` (`table/ca_table.csv.gz`, `table/ca_frame.csv`, `table/derived.csv`, 0 offene PRs): **23/23 strikt kleiner**.
- Colbourn-Tabellenstand (Nov. 2024), R-Paket `CAs` v0.25, NIST-Covering-Array-Tabellen, Seelman / IRSI (Draft 2026-10-13), Sitjar v1.4 (Table 1), Dzoba, Bergeron.
- **Arhan Canli (`arhancanli/quantavane-covering-arrays` @ Commit `0b179b520c9eb8b6c2ce8ea6273403a8d861c608`, 2026-11-21, lesend geprüft via `gh api`):**
  - `cells.csv` (`448.049` Zeilen gesamt, $t \in \{3,4,5,6\}$, $v \in \{4..25\}$) enthält für unsere Alphabete ausschließlich große Spaltenzahlen aus CPHF-Familien:
    - $v = 10$: `1.770` Zeilen, $k \in [551, 6935]$, $\min N = 5291$ (unser Bereich: $N \in [2070, 2160]$),
    - $v = 12$: `1.381` Zeilen, $k \in [774, 10000]$, $\min N = 8749$ (unser Bereich: $N \in [3696, 3762]$),
    - $v = 14$: `1.225` Zeilen, $k \in [325, 5880]$, $\min N = 12256$ (unser Bereich: $N \in [5915, 6188]$),
    - $v = 20$: `645` Zeilen, $k \in [2493, 3137]$, $\min N = 48599$ (unser Bereich: $N \in [17670, 18240]$).
  - `families.csv`, `families_91.csv`, `three-row/`: `0` Überschneidungen mit unseren 13 Pareto-Zellen (`CANLI_CONFLICTS = 0`).

## 6. Transparente Restliste nicht im Volltext geprüfter Quellen & formeller Status

Folgende Quellen wurden in dieser Prüfung **nicht im Volltext** bzw. nicht vollständig ausgewertet:
- Bai XunDi (Deposit mit 237 Arrays / `zenodo.23787051`),
- Théo Nicolas Sitjar v1.4 S. 4–9 Resttext & zugehöriges Zenodo-Archiv,
- Chateauneuf & Kreher (2002) Volltext,
- Cohen, Colbourn & Ling (2003, ISSRE),
- Colbourn, Martirosyan, Tran Van Trung & Walker (2006, Roux-type),
- Colbourn & Zhou (2012, Power CZ).

**Formeller Neuheitsstatus:** **offen** (da die Restliste nicht im Volltext geprüft ist). Entsprechend beschränkt sich jede Außenformulierung gemäß `RULES.md` Regel 4 strikt auf: **„kleiner als `chrispbsmolen/ca-tools` am Commit `7b08aef06cbedaf1b376dbfa68f6aa171a54df4a`“**.
