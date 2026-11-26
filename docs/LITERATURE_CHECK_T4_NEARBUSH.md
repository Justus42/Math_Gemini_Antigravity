# Literaturprüfung `t = 4 NEAR_BUSH` — Phase 1 (`ca-tools`), Phase 2 (extern) & Struktur-Analyse

- **Stand:** `2026-11-25`, Branch `chore/t4-nearbush-audit` (Basis `origin/main` @ `ca637a6`, nach Merge von PR `#17`).
- **Umfang:** Phase 1 prüft alle relevanten Quellen in `chrispbsmolen/ca-tools` @ `d739412` (rein lesend via `gh api` in ein Scratch-Verzeichnis außerhalb des Repos); Phase 2 dokumentiert den externen Literaturabgleich (Stand `2026-11-25`) sowie den Abgleich durch den Drittprüfer (Claude/Fable); Abschnitt 7 liefert die suchfreie Struktur-Analyse ([`scripts/analyze_bai_deltas.py`](../scripts/analyze_bai_deltas.py)) zu Bais Prop. 5.4, Satz 6.2 und Satz 3.7.
- **Status:** interner Prüfvermerk mit expliziter offener Restliste (Abschnitt 6.3). Eine Meldung nach außen ist weiterhin gesperrt (PR `#88` offen, Regel 7).

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
| `(4, 9, 7)` | `3556` | `VERIFIED` (S7, `2026-11-01`) | T. N. Sitjar (`tns-research`), Release v1.5, `doi:10.5281/zenodo.23864483`; Einreichung `sitjar-t3t4-2026-11` | „Union of 508 cosets of the all-ones code of length 9 over Z_7“ | `new https://github.com/tns-research/covering-array-records` | `3430` | `−126` |
| `(4, 10, 8)` | `6101` | `VERIFIED` (S7, `2026-11-02`) | Bai XunDi, `doi:10.5281/zenodo.23787055`; Einreichung `bai-xundi-2026-11-part11`; Credit „Nayeri, Colbourn and Konjevod (the ingredient CA(6125; 4, 10, 8)), Bai XunDi (the derivation)“ | „row deletion + Nurmela-style tabu repair post-optimisation of CA(6125;4,10,8)“ | `fuse-ckrs2010; postop-nck2013; tabu-n2004; deposit-bai2026` | `5888` | `−213` |
| `(4, 11, 8)` | `7680` (Zeile `k = 15`) | `CITED` (S1) | Colbourn-Tabelle 2024-11 | „3-Restricted SCPHF RE (CL)“ | `cphf-smc2006; cphf-cl2018` | `7056` | `−624` |
| `(4, 11, 9)` | `9801` | `VERIFIED` (S7, `2026-11-01`) | Bai XunDi, `doi:10.5281/zenodo.23787055`; Einreichung `bai-xundi-2026-10-part3` | „degree-2 polynomial construction + block cover / SA post-processing“ | `deposit-bai2026` | `9558` | `−243` |
| `(4, 13, 11)` | `21901` | `VERIFIED` (S7, `2026-11-01`) | Bai XunDi, `doi:10.5281/zenodo.23787055`; Einreichung `bai-xundi-2026-10-part4` | „degree-2 polynomial construction (poly2) with a pencil cover of AG(2,q)“ | `deposit-bai2026` | `21900` | `−1` |
| `(4, 15, 13)` | `42757` | `VERIFIED` (S7, `2026-11-01`) | Bai XunDi, `doi:10.5281/zenodo.23787055`; Einreichung `bai-xundi-2026-10-part3` | „degree-2 polynomial construction (poly2) with a pencil cover of AG(2,q)“ | `deposit-bai2026` | `42722` | `−35` |

**Widerspruch-Hinweis zu `(4, 9, 7)`:** Der Startwert `3577` stammt aus Bais Formel in Kor. 5.3 (`7^4 + ((7^2 - 1)/2) * 7^2 = 3577`), **nicht** aus einem abgelegten Bai-Eintrag in `ca-tools`. Der Tabellenwert `3556` stammt aus `tns-research` v1.5 (Coset-Union über `Z_7`, Sitjar), der vorherige Wert `3569` aus `OA fuse postop NCK` (Dwyer / Colbourn-Tabelle). Ebenso steht auf `(4, 10, 8)` kein `poly2`-Eintrag von Bai XunDi, sondern eine Post-Op-Ableitung aus `CA(6125)` (NCK), und auf `(4, 11, 8)` nur ein `CITED`-Wert aus der Colbourn-Tabelle.

### 2.2 Nachbarzellen (Plateau-Kontext)

| `v` | Zeilen `ca_table` (`k`: `N`, Tier) |
| :---: | --- |
| `7` | `k = 8`: `2401` (`CITED`/`VERIFIED`, Bush-OA); `k = 9`: `3569` (`CITED` S1 & `VERIFIED` S5 Dwyer, „orthogonal array fuse postop NCK“), `3556` (`VERIFIED` S7 Sitjar) |
| `8` | `k = 9`: `4096` (Bush-OA); `k = 10`: `6125` (`CITED` S1 & `VERIFIED` S5 Dwyer), `6101` (S7 Bai); `k = 11..15`: keine eigene Zeile, Bestwert `7680` aus `k = 15` (`CITED`) |
| `9` | `k = 10`: `6561` (Bush-OA); `k = 11`: `12312` (`CITED`, „extended OA (Colbourn)“), `9801` (S7 Bai) |
| `11` | `k = 12`: `14641` (Bush-OA, `CITED` & `VERIFIED` S7 Smolen); `k = 13`: `27482` (`CITED`), `21901` (S7 Bai); `k = 14`: `27544` (`CITED`) |
| `13` | `k = 14`: `28561` (Bush-OA, `CITED` & `VERIFIED` S7 Smolen); `k = 15`: `54756` (`CITED`, „extended OA (Colbourn)“), `42757` (S7 Bai) |

- `table/derived.csv`: **`0`** Zeilen für `t = 4` in den Zielzellen oder Nachbarzellen.
- `table/withdrawn_files.csv`: **`0`** Zeilen für `t = 4` in den Zielzellen oder Nachbarzellen. Alle Startarrays werden von eigenen Generatoren erzeugt; zurückgezogene Arrays sind nicht berührt.

## 3. Vollständige Zitation von Bai XunDi & Baustein-Zuordnung

**Primärquelle der Grundbauart:**
- **X. Bai, „Covering arrays from line-polychromatic colourings of affine planes“, Preprint vom 30.10.2026, `doi:10.5281/zenodo.23787051`** (in `ca-tools/table/references.csv` unter Kennung `polychrome-bai2026`; zugehöriges Datendepot `deposit-bai2026`: `doi:10.5281/zenodo.23787055`).

Jeder tragende theoretische Baustein unserer `t = 4`-Konstruktionen ist diesem Preprint explizit zuzuordnen:

| Baustein in Bai (30.10.2026) | Inhalt im Preprint | Zuordnung zu unseren `t = 4`-Konstruktionen |
| --- | --- | --- |
| **Satz 3.5** | Zusatzspalte als linien-polychromatische Färbung von `AG(2, q)` über Bush/RS-OA + `OA(q^3; 3, q + 1, q)`-Blöcke für die Restsymbole (`N = q^4 + (q - c) q^3`) | Direkter Konstruktionsrahmen aller `6` Zielzellen (`q = 7, 8, 9, 11, 13`) |
| **Prop. 4.1** | Obergrenze `c <= floor(q/2)` **innerhalb von Bais Ebenenfärbungsmodell** über Jamison (1977) / Brouwer–Schrijver (1978) (`>= 2q - 1` Punkte pro affinem Blocking-Set; keine allgemeine CA-Untergrenze) | Identisch mit der in `docs/T4_ODD_Q_NEAR_BUSH.md` §3.2 genutzten Paritätsschranke (`q = 8: c <= 4`, ungerades `q: c <= (q - 1)/2`) |
| **Satz 5.1 / Prop. 5.2 / Kor. 5.3** | Pencil-Cover-Überdeckung von `AG(2, q)`, Zeilenformel `N = q^4 + ((q^2 - 1)/2) * q^2` | Identisch mit den Startgrößen `3577` (`q = 7`), `9801` (`q = 9`), `21901` (`q = 11`), `42757` (`q = 13`) |
| **Prop. 5.4** | Optimalität **ausschließlich innerhalb von Bais Ebenenfärbungs-/Kostenmodell** (keine allgemeine Covering-Array-Untergrenze, da `q^4 + C(q, 2) q^2` diese Modellgrenze bereits für alle `q >= 7` — algebraisch für alle Primzahlpotenzen `q >= 2` — unterbietet); für gerades `q` gilt im Modell `g >= q^2 / 2`, also bei `q = 8, t = 4` mindestens **`6144`** (`4096 + 32 * 64`) | Vergleichsmarke für `CA(5888; 4, 10, 8)` (`−256` Zeilen unter `6144`; Mechanismus in Abschnitt 7.1) |
| **Satz 6.2** | Zwei Zusatzspalten (`k = q + 3`); für `q = 8` mit Hyperoval-Block `E` ergibt Satz 6.2 **`8192`** (`4096 + 4 * 512 + 4 * 512`) | Vergleichsmarke für das Roh-Array `CA(7203; 4, 11, 8)` (`−989` Zeilen unter `8192`; Mechanismus in Abschnitt 7.2) |
| **Satz 3.7 & Offenes Problem 2** | Allgemeinere Spaltenfunktionen jenseits reiner Ebenenfärbungen (`> floor(q/2)` Farbklassen für `t >= 4`) | Suchfrei geprüft an `CA(3430; 4, 9, 7)` und `CA(5888; 4, 10, 8)` in Abschnitt 7.3 (Ergebnis: **nein**, keines der beiden Arrays überschreitet `floor(q/2)`) |

- **Einreichungen & `HOW.md` in `ca-tools`:** `bai-xundi-2026-10-part3`, `bai-xundi-2026-10-part4`, `bai-xundi-2026-11-part11` und `sitjar-t3t4-2026-11` enthalten nur `claims.csv` (ohne `HOW.md`). `bai-xundi-2026-11-external2/HOW.md` ordnet `poly2` + Pencil-Cover ausdrücklich `doi:10.5281/zenodo.23787051` („paper A“) zu.
- **`docs/llms.txt` („Rules for agents“):** benannte verantwortliche Person; `HOW.md` mit `AI tools used: yes/no`; nur selbst gebaute Arrays einreichen und tatsächliche Urheber nennen; Tabellen-DOI `10.5281/zenodo.24168008` und Zeilen-Autoren zitieren.

## 4. Gegenüberstellung unserer Arrays mit Bai (30.10.2026) & Tabellen-Einträgen

| `q` / Zelle | Bauart (Startarray → Ergebnis) | Bezug zu Bai (30.10.2026) & Tabelle | Eigener Anteil | Pflicht-Credit (bei späterer Meldung) |
| --- | --- | --- | --- | --- |
| `q = 8`, `(4, 10, 8)` | **Verfeinerung von Bai XunDis Satz 3.5 / 5.1** (keine eigene Grundbauart): `4` disjunkte `15`-Punkte-Blocking-Sets in `AG(2, 8)` (Prop. 4.1) mit Projektion `Q_g` entlang `x^2 + x + 1` (Char. `2`), sodass die `4` freien Punkte direkt fertige `OA(64)`-Slices im Bush-OA liefern (`−4 * 64 = −256` Zeilen → `5888` ohne Post-Op) | Verfeinerung von Bai (`polychrome-bai2026`, Satz 3.5 / 5.1), keine eigene Grundbauart; unterbietet Bais Modellgrenze `6144` (Prop. 5.4) um `4 * 64 = 256` Zeilen durch Nutzung der `4` freien Punkte als fertige Scheiben (Abschnitt 7.1). Tabelleneintrag `6101` ist Bais Post-Op aus `CA(6125)` (NCK). | Konkrete Wahl der `Q_g`-Projektion (Hyperoval-Nukleus in Char. `2`) und Blocking-Set-Zerlegung mit `4` freien Ankerpunkten | Bai XunDi (`polychrome-bai2026`, `deposit-bai2026`) zuerst; Bush 1952; Jamison 1977 / Brouwer–Schrijver 1978 |
| `q = 8`, `(4, 11, 8)` | Rahmen Bai Satz 3.5 / Satz 6.2 mit zwei balancierten `4`-polychromatischen Färbungen, `16` geteilten Hyperoval-Slices + `35` Reparaturzeilen (`7203`), danach `t4_postop` (`7203 → 7056`) | Grundrahmen bei Bai (`polychrome-bai2026`); Roh-Array `7203` unterbietet Satz 6.2 (`8192`) um `989` Zeilen (Abschnitt 7.2). Post-Op nach NCK 2013 / Nurmela 2004. Tabellenwert `7680` ist `CITED` (Colbourn–Lanus). | Geteilte Hyperoval-Slices zwischen `col9` und `col10`, eigene Färbungen, eigener Reduzierer `solvers/t4_postop` | Bai XunDi (`polychrome-bai2026`) zuerst; Bush 1952; Nayeri–Colbourn–Konjevod 2013; Nurmela 2004 |
| `q = 7`, `(4, 9, 7)` | Startgröße `3577` aus Bai Kor. 5.3 unter Projektion `Q_cd` mit Parabel-Packung `q^2 = q + ((q - 1)/2)(2q - 1) + (q - 1)/2`, danach `t4_postop` (`3577 → 3430`) | Rahmen und Startgröße vollständig bei Bai (`polychrome-bai2026`, Kor. 5.3); Tabellenwert `3556` stammt von Sitjar (`tns-research` v1.5). Post-Op wie oben. | Parabel-Packung zur Halbierung von `min_row_unique` (`30 → 15`) und eigener Reduzierer (`−147 = −3 · 7^2`) | Bai XunDi (`polychrome-bai2026`, `deposit-bai2026`) zuerst; Bush 1952; Nayeri–Colbourn–Konjevod 2013; Nurmela 2004; Sitjar (Vergleichswert) |
| `q = 9`, `(4, 11, 9)` | wie `q = 7` (`9801` aus Bai Kor. 5.3), danach `t4_postop` (`9801 → 9558`) | Rahmen und Startgröße identisch mit Bai (`polychrome-bai2026`, Kor. 5.3; Tabellenwert `9801`). | Parabel-Packung (`72 → 36`) und eigener Reduzierer (`−243 = −3 · 9^2`) | wie `q = 7`, Bai XunDi zusätzlich als Inhaber des Vergleichswerts |
| `q = 11`, `(4, 13, 11)` | `poly2-disjoint` ohne Parabel (`21901` aus Bai Kor. 5.3), danach `t4_postop` (`21901 → 21900`) | **Reine Nachoptimierung (`−1` Zeile) auf Bais Bauart (`polychrome-bai2026`, Kor. 5.3; Tabellenwert `21901`).** | Eigene Implementierung und `1` Zeile Post-Op | Bai XunDi (`polychrome-bai2026`, `deposit-bai2026`) zuerst; Bush 1952; Nayeri–Colbourn–Konjevod 2013; Nurmela 2004 |
| `q = 13`, `(4, 15, 13)` | wie `q = 11` (`42757` aus Bai Kor. 5.3), danach `t4_postop` (`42757 → 42722`) | **Reine Nachoptimierung (`−35` Zeilen) auf Bais Bauart (`polychrome-bai2026`, Kor. 5.3; Tabellenwert `42757`).** | Eigene Implementierung und `35` Zeilen Post-Op | wie `q = 11` |

### 4.1 Vorläufige `builds_on`-Kette (intern)
`oa-bush1952; polychrome-bai2026; deposit-bai2026; postop-nck2013; tabu-n2004` für `q = 7, 9, 11, 13` und `(4, 11, 8)`; `oa-bush1952; polychrome-bai2026` für das rein deterministische `CA(5888; 4, 10, 8)`.

## 5. Trennung: große Abstände und dünne Nachschliffe

| Gruppe | Zellen | Abstand zur Tabelle @ `d739412` | Herkunft des Abstands | Einordnung |
| --- | --- | :---: | --- | --- |
| **Große Abstände** | `(4, 9, 7)` | `−126` | Startarray `3577` (Bai Kor. 5.3, `+21` über Sitjar), Post-Op `−147 = −3 · 7^2` | Abstand entsteht erst durch Post-Op |
| | `(4, 10, 8)` | `−213` | rein deterministisch, `−256` unter Bai Prop. 5.4 (`6144`), keine Post-Op | einziger Fall ohne Suchanteil |
| | `(4, 11, 8)` | `−624` | Roh-Array `7203` (`−989` unter Bai Satz 6.2, `−477` unter `CITED`), Post-Op `−147` | Vergleichswert nur `CITED` (kein Array in Tabelle) |
| | `(4, 11, 9)` | `−243` | Startarray `9801` (Bai Kor. 5.3), Post-Op `−243 = −3 · 9^2` | Abstand entsteht erst durch Post-Op |
| **Dünne Nachschliffe** | `(4, 13, 11)` | `−1` | Startarray `21901` (Bai Kor. 5.3), Post-Op `−1` Zeile | reine Nachoptimierung auf Bais Bauart |
| | `(4, 15, 13)` | `−35` | Startarray `42757` (Bai Kor. 5.3), Post-Op `−35` Zeilen | reine Nachoptimierung (`< q^2 = 169`) auf Bais Bauart |

---

## 6. Phase 2: Externe Literaturprüfung (Stand 2026-11-25) & Abgleich durch Drittprüfer

### 6.1 Extern gelesene Quellen & Gesamtbefund
In keiner der extern gelesenen Quellen wurde für eine der `6` Zielzellen ein `N <=` unserer Werte gefunden:
- Bai XunDi, Preprint vom `30.10.2026` (`doi:10.5281/zenodo.23787051`, Volltext via alphaXiv),
- `tns-research` README (Sitjar),
- Colbourn–Kéri–Rivas Soriano–Schlage-Puchta (2010), Lemma 3.3,
- Colbourn–Lanus (2018),
- Torres-Jimenez & Izquierdo-Marquez (2024),
- Barát–Marcugini–Pambianco–Szőnyi (2006),
- `arXiv:2507.05037`,
- `ca-tools` PR-Auszüge.

**Einordnung:** Die Grundbauart (linien-polychromatische Färbung von `AG(2, q)` über Bush/RS-OA, Jamison-Obergrenze, Pencil-Cover-Formel `q^4 + ((q^2 - 1)/2) q^2`) ist durch Bai (`30.10.2026`) vollständig vorweggenommen. Insbesondere sind `q = 11` (`−1`) und `q = 13` (`−35`) reine Nachoptimierungen mit Pflicht-Credit auf Bai.

### 6.2 Ergänzender Abgleich durch den Drittprüfer (Angabe von Claude/Fable, `ca-tools @ d739412`)
- `ca-tools` PR `#36` enthält für `v = 8` nur `CA(6101; 4, 10, 8)`, **kein** Array für `(4, 11, 8)`.
- Alle **`1.008` Claims** in `submissions/*/claims.csv` und `external.csv` wurden durchsucht; keiner liegt `<=` unseren Größen auf den `6` Zielzellen.

### 6.3 Offene Restliste
1. **Neuere Zenodo-Versionen & nicht eingereichte Ergebnisse:** Zenodo `23787055` (Folgeversionen), `tns-research` v1.7–v1.9 (`23959429`, `24060956`, `24141927`) sowie noch nicht in `ca-tools` eingereichte Ergebnisse.
2. **Systematische arXiv-Volltextsuche (2023–2026) & Primärliteratur-Volltexte:** Colbourn–Lanus (2018), Raaphorst–Moura–Stevens (2014), Nurmela (2004), Chateauneuf–Kreher (2002).
3. **Existenz der Parabel-Packung für `q = 11` und `q = 13`:** weiterhin offen (`60 s`-Suche in Phase 5B-2C erfolglos).
4. **Methodischer Hinweis:** Bai arbeitete ebenfalls mit Claude; dies berührt Neuheitsurteile (offen zu dokumentieren), nicht die deterministische Verifikation durch `ca_verify` und den `ca-tools`-Verifier.

Bis zum Abschluss dieser Restliste gilt nach Regel 4 weiterhin die Wortwahl „kleiner als die Tabelle `ca-tools` am Commit `d739412`“; keine Aussage über Neuheit.

---

## 7. Suchfreie Struktur-Analyse (`scripts/analyze_bai_deltas.py`)

Deterministische Prüfung ohne Suche (`timeout --kill-after=10s 60 python3 scripts/analyze_bai_deltas.py`, Laufzeit `0,86 s`):

### 7.1 Warum liegt `CA(5888; 4, 10, 8)` unter Bais Modellgrenze `6144` (Prop. 5.4)?
- **Bais Prop. 5.4 (`q = 8, t = 4`, ausschließlich innerhalb von Bais Ebenenfärbungs-/Kostenmodell, keine allgemeine CA-Untergrenze):** `c <= floor(8/2) = 4` Blocking-Set-Farben `{0, 1, 2, 3}`, `4` Restsymbole `{4, 5, 6, 7}` mit je einem vollen `OA(512; 3, 9, 8)` (`8 * 64` Zeilen) → `g >= q^2 / 2 = 32` Blöcke à `64` Zeilen (`2048` Zusatzzeilen) → **`4096 + 2048 = 6144`**. *(Die allgemeine geschlossene Bauart `q^4 + C(q, 2) q^2` unterbietet Bais Modellgrenze bereits für alle `q >= 7`, algebraisch für alle Primzahlpotenzen `q >= 2`.)*
- **Gemessener Befund an `results/t4_nearbush/CA_5888_4_10_8.txt`:**
  - `4096/4096` Zeilen bilden das vollständige Bush-`OA(4096; 4, 9, 8)` auf Spalten `0..8`; die `4` disjunkten minimalen `15`-Punkte-Blocking-Sets belegen `4 * 15 = 60` Punkte von `AG(2, 8)` (`960` Zeilen je Symbol `{0..3}`).
  - Die `4` verbleibenden freien Punkte `(9, 39, 42, 59)` werden im Bush-OA direkt den `4` Restsymbolen `{4, 5, 6, 7}` zugewiesen (`64` Zeilen je Symbol im Bush-OA).
  - Unter der Projektion `Q(a, b, c, d) = (a ^ c ^ d, a ^ b ^ d)` (Kern `{(u + v x)(x^2 + x + 1)}`, Charakteristik `2`, Hyperoval-Nukleus `(0, 1, 0)`) bildet jede dieser `4` 64-Zeilen-Fasern im Bush-OA bereits ein **exaktes `OA(64; 2, 9, 8)`** (`OA(64;2,9,8) = True` für alle `m in {4..7}`).
  - Daher benötigt jedes Restsymbol `m in {4..7}` nur noch `7` statt `8` externe `OA(64)`-Slices (`7 * 64 = 448` statt `512` Zeilen) → `28 * 64 = 1792` statt `32 * 64 = 2048` Zusatzzeilen (`−4` Blöcke à `64` = **`−256` Zeilen**, `4096 + 1792 = 5888`). Die Einsparung entsteht nicht durch `c > 4`, sondern durch die Wiederverwendung der `4` freien Punkte als vollwertige `OA(64)`-Slices.

### 7.2 Warum liegt das Roh-Array `CA(7203; 4, 11, 8)` unter Bais Satz 6.2 (`8192`)?
- **Bais Satz 6.2 (`q = 8, k = 11`):** `4096` (Bush-OA) `+ 4 * 512` (`col9 in {4..7}`) `+ 4 * 512` (`col10 in {4..7}`) `= 8192`.
- **Gemessene Zerlegung von `build_k11_polychrom()` (`7203` Zeilen, `−989` vs. `8192`):**
  - `4096` Zeilen Basis-Bush-OA (`col9, col10 in {0..3}` aus zwei balancierten `[16, 16, 16, 16]`-4-polychromatischen Färbungen),
  - `2048` Zeilen Hyperoval-Blöcke für `col9 in {4..7}` (`4 * 512`), in denen `col10 = b ^ (m9 - 4)` alle `8` Symbole durchläuft: genau `1024` Zeilen haben `(col9 >= 4, col10 < 4)` und **`1024` Zeilen (`16` `OA(64)`-Slices, je `256` Zeilen pro `m10 in {4..7}`) haben `(col9 >= 4, col10 >= 4)`**,
  - `1024` Zeilen dezidierte Hyperoval-Slices für `col10 in {4..7}` mit `col9 in {0..3}` (`256` Zeilen pro `m10 in {4..7}`; zusammen mit den `256` geteilten Zeilen aus den `col9`-Blöcken ein exaktes `OA(512; 3, 9, 8)` für jedes `m10 in {4..7}`),
  - `35` deterministische Greedy-Reparaturzeilen für die `68` fehlenden `(c0, c1, col9, col10)`-Tupel in `{0..3}^2`.
  - Netto-Bilanz: `8192 − 1024` (geteilte Hyperoval-Slices) `+ 35` (Paar-Reparatur) `= 7203` (`−989`).

### 7.3 Suchfreier Check auf Bai Satz 3.7 / Offenes Problem 2 (`CA_5888` & `CA_3430`)

| Kenngröße (gemessen direkt an der Datei) | `CA(5888; 4, 10, 8)` (`q = 8`) | `CA(3430; 4, 9, 7)` (`q = 7`) |
| --- | :---: | :---: |
| Bush-`OA(q^4; 4, q + 1, q)` auf Spalten `0..q` | **`4096/4096`** (`0` fehlend, `0` mehrdeutig) | **`2401/2401`** (`0` fehlend, `0` mehrdeutig) |
| Zeilen außerhalb Bush-OA-Präfix (`col_∞ != d`) | `1792` (`28 × 64`) | `1029` (`21 × 49`), `0` Nicht-Polynomzeilen auf `0..6` |
| Modifizierte `col_{q+1}`-Zeilen im Bush-OA vs. Startarray | `0/4096` (deterministisch) | **`392/2401`** (`8` Slices à `49` gegenüber `CA(3577)`) |
| Reine Funktion `f: OA(q^4) -> GF(q)` auf `0..q` | **ja** | **ja** |
| Geprüfte `(t - 1)`-Tupel-Fasern auf `0..q` (`C(q+1, 3) * q^3`) | `43.008` | `19.208` |
| Farben pro Faser (nur Bush-OA-Zeilen): `min / max` | `4 / 7` | `3 / 6` |
| Universelle Farben (treffen jede Faser im Bush-OA) | `{0, 1, 2, 3}` (**`4 = floor(8/2)`**) | `{0, 1}` (**`2 < floor(7/2) = 3`**) |
| Min. getroffene Fasern pro Symbol (von `q^3`) im Bush-OA | `{0..3: 512, 4..7: 64}` | `{0: 343, 1: 343, 2: 294, 3: 196, 4: 49, 5: 49, 6: 98}` |
| Satz 3.7 / Offenes Problem 2 (`> floor(q/2)` universelle Farben)? | **nein** (`4 <= 4`) | **nein** (`2 < 3`) |

**Befund:** In beiden Arrays bleibt das gesamte Bush-`OA(q^4; 4, q + 1, q)` auf Spalten `0..q` vollständig intakt (die lokale Suche bricht die `OA(7^4)`-Basis in `CA_3430` **nicht** auf, sondern färbt genau `392/2401 = 8` `q^2`-Slices in `col_8` um). Keines der beiden Arrays erreicht `> floor(q/2)` universelle Farbklassen im Sinne von Bais Satz 3.7 / Offenes Problem 2; bei `CA_3430` sinkt die universelle Farbzahl sogar von `3` auf `2`, während die verbleibenden Lücken von `m = 2` (`294/343`) durch `1` Zusatz-Slice (`49` Zeilen) statt `2` Bush-Slices geschlossen werden.

---

## 8. Phase 3: Ergänzender Literatur- und Datenabgleich (Angabe von Claude, `ca-tools @ d739412`, Zenodo gelesen `2026-11-26`)

### 8.1 Geschlossen (Angabe von Claude)
- **`PR #78` (`bai-xundi-2026-11-external2`):** `29` Einträge vollständig gelesen; `t = 4` nur `v = 20..25`, `t = 5` nur `v >= 12`, `t = 6` nur `v >= 10` — keine unserer Zellen.
- **`PR #36`:** `11` Claims, für `v = 8` ausschließlich `CA(6101; 4, 10, 8)`.
- **Bai-Ablage `doi:10.5281/zenodo.23787055` (Version `1.0` vom `30.10.2026`, `records.csv` gelesen):** `(4, 9, 7) = 3557`, `(4, 10, 8) = 6101`, `(4, 11, 9) = 9801`, `(4, 13, 11) = 21901`, `(4, 15, 13) = 42757`, kein Eintrag für `(4, 11, 8)`; `(5, 10, 8) = 49136`, `(6, 10, 8) = 393088`.
- **`1.008` Claims + `237` `EXTERNAL`-Einträge:** kein Wert `<=` unseren `6` `t = 4`-Größen bzw. den Track-2-Vorhersagen `47.104` / `376.832`.
- **Colbourn & Lanus (2018), ADAM 1 `#P2.03`, `doi:10.26493/2590-9770.1220.3a1` (Volltext gelesen, PDF vom Nutzer, Angabe von Claude, `2026-11-26`) — erledigt:**
  - Keine Konstruktion für `k = q + 2`, kein OA-plus-Spalte, keine Schranke `q^t + C(v, 2) * q^(t - 2)`; das Paper behandelt ausschließlich CPHF/SCPHF per Computersuche (`>= 2` Hash-Zeilen).
  - Lemma 1.2: ein `SCPHF(n; k, q, t)` ergibt `CA(n(q^t - q) + q; t, k, q)`; mit Einschränkung `<t - 1>` auf `2` Zeilen ergibt sich `2 q^t - q^(t - 1)` (Rechnung des Prüfers), was stets größer ist als `q^t + C(q, 2) * q^(t - 2)`.
  - Herkunft von `7680` auf `(4, 11, 8)` (Tabellenzeile `k = 15`): Tabelle 7, `q = 8, n = 2, <3>`, `15` Spalten (`2 * 8^4 - 8^3 = 7680`); analog `12393` (`q = 9`, `17` Spalten) und `54925` (`q = 13`, `21` Spalten).

### 8.2 Weiter offen
1. Systematische arXiv-Suche (2023–2026).
2. `tns-research`-Zenodo-Ablagen direkt (`v1.7`–`v1.9`).
3. Existenz der Parabel-Packung für `q = 11, 13` (Empfehlung Drittprüfer: vollständiger SAT/CP-Löser statt Heuristik, damit auch ein Negativbefund als Beleg gilt).
4. **Offene Literatur-Restliste zur allgemeinen Konstruktion `q^t + C(v, 2) * q^(t - 2)` (`k = q + 2`, beliebige Stärke `t` und `2 <= v <= q`, aktualisiert `2026-11-26`):**
   - Colbourn–Lanus–Sarkar (2018)
   - Hartman (2005)
   - Ji & Yin (2010)
   - Colbourn (2004 / 2015)
   - Hedayat–Sloane–Stufken (Bush-Arrays mit `q + 2` Spalten)
   - Chateauneuf–Kreher (2002)

Diese Punkte bleiben transparent als offen dokumentiert (für lokales Staging ohne Neuheitsanspruch kein Blockade-Gate mehr, vorbehaltlich ausdrücklicher Nutzerfreigabe vor jeder externen Einreichung). Es gilt nach Regel 4 weiterhin durchgehend die Wortwahl „kleiner als `ca-tools` am Commit `<SHA>`“ ohne Neuheitsanspruch.



