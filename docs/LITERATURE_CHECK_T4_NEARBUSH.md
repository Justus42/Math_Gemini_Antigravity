# Literaturprüfung `t = 4 NEAR_BUSH` — Phase 1: `ca-tools`-Quellen & `builds_on`-Abgrenzung

- **Stand:** `2026-11-25`, Branch `chore/t4-nearbush-audit` (Basis `origin/main` @ `ca637a6`, nach Merge von PR `#17`).
- **Umfang dieser Phase:** ausschließlich Quellen, die im Tabellen-Repository `chrispbsmolen/ca-tools` selbst liegen (Tabellen-Dateien, `references.csv`, `submissions/*/claims.csv` und `HOW.md`, `docs/llms.txt`). Alle Abrufe rein lesend via `gh api` in ein Scratch-Verzeichnis außerhalb des Repos; nichts davon ist committet.
- **Nicht Teil dieser Phase:** externe Literatur (arXiv, Colbourn-Tabellen, Zenodo-Preprints). Siehe Abschnitt 6 (*offen*).
- **Status:** interner Prüfvermerk. Er ersetzt **nicht** Punkt 2c der Checkliste `RULES.md` („Meldung nach außen“); eine Meldung nach außen ist weiterhin gesperrt (PR `#88` offen, Regel 7).

---

## 1. Live-Abgleich (rein lesend)

| Prüfpunkt | Ergebnis (`2026-11-25T22:00Z`) |
| --- | --- |
| `chrispbsmolen/ca-tools` `main` | `d7394120eb9703fbd92e5a28cbbda970c298f115` (`2026-11-25T20:25:41Z`), unverändert gegenüber dem Stand von Phase 5B-2C (`compare d739412...main`: `ahead_by = 0`) |
| PR `#88` | `open`, `merged: false`, `draft: false`, Head `8d3365c`, `mergeable_state: clean`, `2` Issue-Kommentare (`Justus42` `17:12:50Z`, `github-actions[bot]` `20:47:49Z`), `0` Reviews, `0` Review-Kommentare, letzte Änderung `2026-11-25T20:47:49Z` |
| Offene PRs gesamt | `1` (nur `#88`, `t = 3`); **`0` offene PRs mit Bezug zu `t = 4`** |
| Gelesene Dateien @ `d739412` | `table/ca_table.csv.gz`, `table/ca_frame.csv`, `table/derived.csv`, `table/references.csv`, `table/withdrawn_files.csv`, `docs/llms.txt`, `submissions/{bai-xundi-2026-10-part3, bai-xundi-2026-10-part4, bai-xundi-2026-11-part11, sitjar-t3t4-2026-11, sitjar-t4-2026-10, sitjar-postop-2026-11, bai-xundi-2026-11-external2, bai-xundi-2026-11-external3, bai-xundi-2026-11-genus2}/` |

## 2. Tabellenstand der 6 Zielzellen und der Nachbarzellen (`ca-tools` @ `d739412`)

### 2.1 Zielzellen

| Zelle `(t, k, v)` | Bestwert `ca_frame` | Tier | Quelle / Credit (`ca_table`) | `construction` (`ca_table`) | `builds_on` | Unser Array | Abstand |
| --- | :---: | :---: | --- | --- | --- | :---: | :---: |
| `(4, 9, 7)` | `3556` | `VERIFIED` (S7, `2026-11-01`) | T. N. Sitjar (tns-research), Release v1.5, `doi:10.5281/zenodo.23864483`; Einreichung `sitjar-t3t4-2026-11` | „Union of 508 cosets of the all-ones code of length 9 over Z_7“ | `new https://github.com/tns-research/covering-array-records` | `3430` | `−126` |
| `(4, 10, 8)` | `6101` | `VERIFIED` (S7, `2026-11-02`) | Bai XunDi, `doi:10.5281/zenodo.23787055`; Einreichung `bai-xundi-2026-11-part11`; Credit „Nayeri, Colbourn and Konjevod (the ingredient CA(6125; 4, 10, 8)), Bai XunDi (the derivation)“ | „row deletion + Nurmela-style tabu repair post-optimisation of CA(6125;4,10,8)“ | `fuse-ckrs2010; postop-nck2013; tabu-n2004; deposit-bai2026` | `5888` | `−213` |
| `(4, 11, 8)` | `7680` (Zeile `k = 15`) | `CITED` (S1) | Colbourn-Tabelle 2024-11 | „3-Restricted SCPHF RE (CL)“ | `cphf-smc2006; cphf-cl2018` | `7056` | `−624` |
| `(4, 11, 9)` | `9801` | `VERIFIED` (S7, `2026-11-01`) | Bai XunDi, `doi:10.5281/zenodo.23787055`; Einreichung `bai-xundi-2026-10-part3` | „degree-2 polynomial construction + block cover / SA post-processing“ | `deposit-bai2026` | `9558` | `−243` |
| `(4, 13, 11)` | `21901` | `VERIFIED` (S7, `2026-11-01`) | Bai XunDi, `doi:10.5281/zenodo.23787055`; Einreichung `bai-xundi-2026-10-part4` | „degree-2 polynomial construction (poly2) with a pencil cover of AG(2,q)“ | `deposit-bai2026` | `21900` | `−1` |
| `(4, 15, 13)` | `42757` | `VERIFIED` (S7, `2026-11-01`) | Bai XunDi, `doi:10.5281/zenodo.23787055`; Einreichung `bai-xundi-2026-10-part3` | „degree-2 polynomial construction (poly2) with a pencil cover of AG(2,q)“ | `deposit-bai2026` | `42722` | `−35` |

**Korrektur gegenüber der Arbeitsannahme:** Nicht alle sechs Zellen tragen einen Eintrag von Bai XunDi. Die `poly2`-Bauart von Bai XunDi steht auf `(4, 11, 9)`, `(4, 13, 11)` und `(4, 15, 13)`. Auf `(4, 10, 8)` steht ein Post-Op-Eintrag von Bai XunDi (Zutat `CA(6125)` von Nayeri–Colbourn–Konjevod), **keine** `poly2`-Bauart. Auf `(4, 9, 7)` steht Sitjar (`Z_7`-Nebenklassen), auf `(4, 11, 8)` nur ein `CITED`-Wert aus der Colbourn-Tabelle.

### 2.2 Nachbarzellen (Plateau-Kontext)

| `v` | Zeilen `ca_table` (`k`: `N`, Tier) |
| :---: | --- |
| `7` | `k = 8`: `2401` (`CITED`/`VERIFIED`, Bush-OA); `k = 9`: `3569` (`CITED` S1 & `VERIFIED` S5 Dwyer, „orthogonal array fuse postop NCK“), `3556` (`VERIFIED` S7 Sitjar) |
| `8` | `k = 9`: `4096` (Bush-OA); `k = 10`: `6125` (`CITED` S1 & `VERIFIED` S5 Dwyer), `6101` (S7 Bai); `k = 11..15`: keine eigene Zeile, Bestwert `7680` aus `k = 15` (`CITED`) |
| `9` | `k = 10`: `6561` (Bush-OA); `k = 11`: `12312` (`CITED`, „extended OA (Colbourn)“), `9801` (S7 Bai) |
| `11` | `k = 12`: `14641` (Bush-OA, `CITED` & `VERIFIED` S7 Smolen); `k = 13`: `27482` (`CITED`), `21901` (S7 Bai); `k = 14`: `27544` (`CITED`) |
| `13` | `k = 14`: `28561` (Bush-OA, `CITED` & `VERIFIED` S7 Smolen); `k = 15`: `54756` (`CITED`, „extended OA (Colbourn)“), `42757` (S7 Bai) |

- `table/derived.csv`: **`0`** Zeilen für `t = 4` in den Zielzellen oder Nachbarzellen.
- `table/withdrawn_files.csv`: **`0`** Zeilen für `t = 4` in den Zielzellen oder Nachbarzellen. Keines unserer Startarrays stammt aus der Tabelle; alle Startarrays werden von eigenen Generatoren erzeugt (Abschnitt 3). Die Regel „withdrawn arrays are never used as a start or an ingredient“ (`docs/llms.txt`) ist damit nicht berührt.

## 3. Einreichungen, Referenzen und `HOW.md`

- **`HOW.md`:** Die Einreichungsordner `bai-xundi-2026-10-part3`, `bai-xundi-2026-10-part4`, `bai-xundi-2026-11-part11` und `sitjar-t3t4-2026-11` enthalten **nur `claims.csv`** und die Arrays, **kein `HOW.md`** (älteres Format ohne `builds_on`-Spalte; Kopf `t,v,k,N,file,source_detail,construction,credit,notes`). Ein `HOW.md` mit Bai-Bezug liegt nur in `bai-xundi-2026-11-external2/3` und `bai-xundi-2026-11-genus2` vor; diese betreffen keine der sechs Zielzellen.
- **Herkunft von `poly2` + Pencil-Cover:** `bai-xundi-2026-11-external2/HOW.md` ordnet „the poly2 construction with a pencil cover of AG(2, q)“ dem Preprint **„paper A“, `doi:10.5281/zenodo.23787051`** zu. In `table/references.csv` ist das die Referenz `polychrome-bai2026`: *X. Bai, Covering arrays from line-polychromatic colourings of affine planes, preprint, Zenodo (2026)*.
- **`polychrome-bai2026` in der Tabelle:** `15` Zeilen nennen diese Referenz in `builds_on` (`t = 3`: `v = 8, 10, 12, 14, 15, 16, 17, 18`; `t = 5`: `v = 14, 15, 17, 18, 19`; `t = 6`: `v = 10, 11`). Für `t = 4` nennen die Zeilen nur `deposit-bai2026` (Zenodo-Datendepot `23787055`); die Bauart ist in der Spalte `construction` aber wörtlich dieselbe („poly2 with a pencil cover of AG(2,q)“).
- **Weitere relevante Referenzen (`references.csv`):** `deposit-bai2026` (`10.5281/zenodo.23787055`), `oa-bush1952` (Bush 1952), `tabu-n2004` (Nurmela 2004), `postop-nck2013` (Nayeri–Colbourn–Konjevod 2013), `fuse-ckrs2010` (Colbourn–Keri–Rivas Soriano–Schlage-Puchta 2010), `pgl-s2026` (Sitjar 2026).
- **`docs/llms.txt`, „Rules for agents“ (gelesen):** benannte verantwortliche Person; `HOW.md` mit Zeile `AI tools used: yes/no`; nur selbst gebaute Arrays einreichen und jeden tatsächlichen Urheber nennen; Größen und Arrays der Tabelle gehören den Autoren ihrer Zeilen und dürfen nicht als neue Ergebnisse dargestellt werden; Tiers wörtlich lesen (`CITED` ohne Array); zurückgezogene Arrays nie als Start oder Zutat; jede Nutzung der Daten zitiert die Tabellen-DOI `10.5281/zenodo.24168008` und die Autoren der benutzten Zeilen.

## 4. Gegenüberstellung unserer Bauarten mit den Tabellen-Einträgen

| `q` / Zelle | Unsere Bauart (Startarray → Ergebnis) | Bezug zu fremder Vorarbeit | Eigener Anteil | Pflicht-Credit (bei späterer Meldung) |
| --- | --- | --- | --- | --- |
| `q = 8`, `(4, 10, 8)` | Projektion `Q_g` entlang `x^2 + x + 1` über `GF(8)`; Bush-`OA(8^4; 4, 9, 8)` + Spalte `k = 10` aus einer Zerlegung von `AG(2, 8)` in `4` disjunkte `15`-Punkte-Blocking-Sets + `4` Einzelpunkte; Komplettierung durch Hyperoval-Slices; rein deterministisch, `5888` ohne Post-Op | Das Prinzip „Bush-OA + Zusatzspalte über eine Färbung von `AG(2, q)`, deren Farbklassen jede Gerade treffen“ ist nach Titel und Tabelleneinträgen der Gegenstand von `polychrome-bai2026` (Bai XunDi, paper A). Bai XunDis Tabelleneintrag auf dieser Zelle (`6101`) ist dagegen eine Post-Op-Ableitung aus `CA(6125)` (NCK) und nicht `poly2`. | Konkrete Wahl der Projektion `Q_g` (Hyperoval-Nukleus in Charakteristik `2`), die gefundene Blocking-Set-Zerlegung von `AG(2, 8)` und die Zeilenbilanz `4096 + 4 · 448 = 5888`. Ob paper A diese oder eine gleich große Zerlegung für `t = 4, q = 8` bereits enthält: **offen** (Abschnitt 6). | Bush 1952; Bai XunDi (`polychrome-bai2026`, `deposit-bai2026`); Jamison 1977 / Brouwer–Schrijver 1978 (Mindestgröße affiner Blocking-Sets) |
| `q = 8`, `(4, 11, 8)` | Zwei balancierte 4-polychromatische Färbungen von `AG(2, 8)` + Hyperoval-Slices + `35` Reparaturzeilen (`7203`), danach `t4_postop` (`7203 → 7056`) | Gleicher Färbungsrahmen wie oben (`polychrome-bai2026`); Post-Op nach Nayeri–Colbourn–Konjevod 2013 und Nurmela 2004, in derselben Art wie Bai XunDis `6101`-Ableitung. Tabellenwert `7680` ist ein `CITED`-SCPHF-Wert (Colbourn–Lanus), keine Bai-Zeile. | Eigene Färbungen, eigener Generator und eigener Zero-Dep-Reduzierer `solvers/t4_postop`. | Bush 1952; Bai XunDi (`polychrome-bai2026`); Nayeri–Colbourn–Konjevod 2013; Nurmela 2004 |
| `q = 7`, `(4, 9, 7)` | Projektion `Q_cd`, `3` disjunkte Blocking-Sets + Parabel `{(d^2, d)}` + Einzelpunkte (`poly2-disjoint`, `3577 = N_poly2(7)`), danach `t4_postop` (`3577 → 3430`) | Startgröße `3577` ist exakt Bai XunDis `poly2`-Formel `q^4 + ((q^2 - 1)/2) q^2`; Färbungsrahmen `polychrome-bai2026`. Tabellenwert `3556` stammt von Sitjar (`Z_7`-Nebenklassen), nicht von Bai XunDi. Post-Op wie oben. | Parabel-Packung (Symbol `(q - 1)/2` auf `q` Punkten statt Einzelpunkt bzw. Pencil), die `min_row_unique` halbiert (`30 → 15`); eigener Reduzierer. Der Abstand `−126` zu Sitjar entsteht erst durch die Post-Op-Phase. | Bush 1952; Bai XunDi (`polychrome-bai2026`, `deposit-bai2026`); Nayeri–Colbourn–Konjevod 2013; Nurmela 2004; Sitjar als Inhaber des Vergleichswerts |
| `q = 9`, `(4, 11, 9)` | wie `q = 7` (`poly2-disjoint`, `9801 = N_poly2(9)`), danach `t4_postop` (`9801 → 9558`) | Startgröße identisch mit Bai XunDis Tabelleneintrag `9801` (gleiche Formel); Bai XunDis Eintrag nennt ebenfalls eine Nachbearbeitung („block cover / SA post-processing“). | Parabel-Packung (`72 → 36`) und eigener Reduzierer; `−243 = −3 · 9^2`. | wie `q = 7`, Bai XunDi zusätzlich als Inhaber des Vergleichswerts |
| `q = 11`, `(4, 13, 11)` | `poly2-disjoint` **ohne** Parabel (`5` disjunkte `22`-Punkte-Blocking-Sets + `11` freie Punkte, `21901 = N_poly2(11)`), danach `t4_postop` (`21901 → 21900`) | **Setzt direkt auf Bai XunDis Bauart auf:** Startgröße gleich Bai XunDis `poly2`-Wert `21901`; die Färbung ersetzt den Pencil-Cover durch disjunkte Blocking-Sets, bleibt aber im selben Rahmen. Post-Op-Methode wie bei Bai XunDis `6101`-Ableitung. | Eigener Generator und eigene Färbung; Gewinn ausschließlich durch Post-Op (`1` Zeile). | Bai XunDi zuerst (`polychrome-bai2026`, `deposit-bai2026`); Bush 1952; Nayeri–Colbourn–Konjevod 2013; Nurmela 2004 |
| `q = 13`, `(4, 15, 13)` | wie `q = 11` (`6` disjunkte `27`-Punkte-Blocking-Sets + `7` freie Punkte, `42757 = N_poly2(13)`), danach `t4_postop` (`42757 → 42722`) | **Setzt direkt auf Bai XunDis Bauart auf** (Startgröße gleich Bai XunDis Tabelleneintrag `42757`). | Eigener Generator und eigene Färbung; Gewinn ausschließlich durch Post-Op (`35` Zeilen). | wie `q = 11` |

### 4.1 Vorschlag für `builds_on` (nur intern, keine Meldung)

Falls nach Abschluss von PR `#88` und vollständiger Checkliste je eine Meldung freigegeben würde, wäre nach dem heutigen Stand mindestens folgende `builds_on`-Kette zu nennen: `oa-bush1952; polychrome-bai2026; deposit-bai2026; postop-nck2013; tabu-n2004` (für `q = 7, 9, 11, 13` und `(4, 11, 8)`), sowie `oa-bush1952; polychrome-bai2026` für das rein deterministische `CA(5888; 4, 10, 8)`. Jamison 1977 und Brouwer–Schrijver 1978 haben keinen Eintrag in `references.csv` und wären im `HOW.md` zu zitieren. Diese Liste ist vorläufig, bis Abschnitt 6 abgeschlossen ist.

## 5. Trennung: große Abstände und dünne Nachschliffe

| Gruppe | Zellen | Abstand zur Tabelle @ `d739412` | Woher der Abstand kommt | Einordnung |
| --- | --- | :---: | --- | --- |
| **Große Abstände** | `(4, 9, 7)` | `−126` | Parabel-gepacktes Startarray `3577` (`+21` über Sitjar), Post-Op `−147 = −3 · 7^2` | Startarray liegt über dem Tabellenwert; der Abstand entsteht nur durch die Post-Op-Phase |
| | `(4, 10, 8)` | `−213` | rein deterministische Konstruktion, keine Post-Op | einziger Fall ohne Suchanteil; Nähe zu `polychrome-bai2026` extern zu prüfen |
| | `(4, 11, 8)` | `−624` | Startarray `7203` liegt schon `−477` unter dem `CITED`-Wert, Post-Op `−147` | Vergleichswert ist nur `CITED` (kein Array in der Tabelle) |
| | `(4, 11, 9)` | `−243` | Parabel-gepacktes Startarray `9801` (gleich Bai XunDi), Post-Op `−243 = −3 · 9^2` | Startgröße gleich Bai XunDi; Abstand nur durch Post-Op |
| **Dünne Nachschliffe** | `(4, 13, 11)` | `−1` | Startgröße gleich Bai XunDi `21901`; Post-Op entfernt `1` Zeile | Nachbearbeitung einer Bai-XunDi-gleichen Bauart; als eigenständige Bauart nicht tragfähig |
| | `(4, 15, 13)` | `−35` | Startgröße gleich Bai XunDi `42757`; Post-Op entfernt `35` Zeilen | wie `q = 11`; deutlich unter `q^2 = 169`, also keine ganze Faser |

## 6. Offen: externe Literaturprüfung außerhalb des Containers (arXiv/Colbourn/Zenodo)

Folgende Punkte sind in dieser Phase **nicht** geprüft und müssen außerhalb dieses Containers nachgeholt werden, bevor Punkt 2c der Checkliste (`RULES.md`) als erfüllt gelten kann:

1. **Bai XunDi, paper A (`doi:10.5281/zenodo.23787051`, `polychrome-bai2026`):** Volltext lesen; prüfen, ob dort für `t = 4` und `q = 7, 8, 9, 11, 13` Färbungen, Blocking-Set-Zerlegungen oder Größen genannt sind, die `5888`, `7203`, `3430`, `7056`, `9558`, `21900` oder `42722` erreichen oder unterbieten; insbesondere ob die `q = 8`-Zerlegung in `4` disjunkte `15`-Punkte-Blocking-Sets dort bereits steht.
2. **Bai XunDi, Datendepot (`doi:10.5281/zenodo.23787055`) und paper B (`doi:10.5281/zenodo.23787053`):** Arrays und Begleittexte für `t = 4` auf Größen unterhalb der Tabellenwerte prüfen.
3. **Sitjar (`doi:10.5281/zenodo.23842218`, `23864483` und Folgeversionen):** spätere Releases (v1.6 ff.) auf `(4, 9, 7)` und Nachbarzellen.
4. **Colbourn-Tabelle (aktueller Stand) und arXiv:** Suche nach `CAN(4, k, q)` für `k = q + 2` und nach Arbeiten zu affinen Blocking-Sets / polychromatischen Färbungen in Verbindung mit Covering Arrays (u. a. Shokri–Moura–Stevens, Torres-Jiménez, Colbourn–Lanus).
5. **Schranken-Argumente in `docs/T4_ODD_Q_NEAR_BUSH.md` §8.2:** Nachvollzug durch eine unabhängige Person oder ein unbeteiligtes Modell (vgl. `docs/THIRD_PARTY_VERIFICATION_T4_NEARBUSH.md`).

Bis dahin gilt die Wortwahl nach Regel 4: „kleiner als die Tabelle `ca-tools` am Commit `d739412`“; keine Aussage über Neuheit.
