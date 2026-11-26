# Literaturprüfung zur Bauart `v <= q` aus Phase 7 (`docs/LITERATURE_CHECK_PHASE7_VQ.md`)

- **Stand:** 2026-11-26, ca. 17:15 MEZ. **Autor:** Claude (Prüfer-Chat). Prüfvermerk nach `RULES.md` „Meldung nach außen“ 2c.
- **Gegenstand:** `CAN(t, q+2, v) <= (q^2 + C(max(0, 2v - q), 2)) * q^(t-2)` ([`docs/PHASE7_T2_REDUCTION.md`](PHASE7_T2_REDUCTION.md) §14) und die Nebenklassen-Listen für `v = q` (§5–§10).
- **Ergebnis in einem Satz:** In den gelesenen Quellen steht die Formel nicht; die nächste Vorarbeit (Bai 2026) hat für `v < q` eine schwächere Schranke derselben Familie, und der Rahmen „Vereinigung von Nebenklassen eines linearen Codes“ steht bereits bei Sitjar (2026). **Kein Neuheitsanspruch**; die Prüfung ist nicht vollständig (§5).

## 1. Was gelesen wurde

| Quelle | Wie | Gelesene Teile |
| --- | --- | --- |
| X. Bai, „Covering arrays from line-polychromatic colourings of affine planes“, Preprint 30.10.2026, `doi:10.5281/zenodo.23787051` (`polychrome-bai2026`) | Volltext über den alphaXiv-Index | Zusammenfassung, §1–§2, §5 (Prop. 5.2, Kor. 5.3, Prop. 5.4, Bem. 5.5), §8 (Lemma 8.1, Satz 8.2), §9–§12, Tabellen 2–4 |
| X. Bai, „Two-block covering arrays from elliptic curves and curves of genus two“, Preprint 08.11.2026 (`twoblock-bai2026`) | Volltext über den alphaXiv-Index | Zusammenfassung, §1–§2, §7–§10 |
| T. N. Sitjar, „New upper bounds for covering arrays of strengths 3 to 6“, Version 1.4, 13.11.2026 | Volltext über den alphaXiv-Index | vollständig (9 Seiten) |
| `chrispbsmolen/ca-tools @ e673ab4` | lokale Kopie | `table/references.csv`, `table/ca_table.csv`, `table/ca_frame.csv` (Bauart-Etiketten aller Trefferzellen) |
| Suche | alphaXiv (2 Anfragen), Websuche (3 Anfragen) | Trefferlisten gesichtet |

Nicht möglich in dieser Sitzung: direkter Abruf von Zenodo-Seiten (Freigabe blieb unbeantwortet) und die GitHub-Schnittstelle von `ca-tools` (kein Zugriff). Über `git` sichtbar: `main` unverändert `e673ab4`, kein Pull Request mit Nummer über 89.

## 2. Befunde

### 2.1 Bai (2026), linien-polychromatische Färbungen: nächste Vorarbeit

Bauart dort: Reed–Solomon-/Bush-Array `OA(q^t; t, q+1, q)` plus **eine** neue Spalte, nämlich eine Färbung von `AG(2, q)`, verknüpft mit der Auswertung des Polynoms an einem Element aus `F_(q^2) \ F_q`. Die neue Spalte muss auf **allen** `q + 1` Richtungen bunt sein; daraus folgt über die Jamison-/Brouwer–Schrijver-Schranke die Obergrenze `c <= floor(q/2)` Farben.

| Aussage bei Bai | Zeilenzahl | In Blöcken zu `q^(t-2)` über `q^t` |
| --- | --- | --- |
| Satz 3.5 (`v = q`, Färbung mit `c <= floor(q/2)` Farben) | `q^t + (q - c) q^(t-1)` | `(q - c) q` |
| Kor. 3.8 (Alphabet-Einschränkung, `c`-Färbung vorhanden) | `q^t + (v - c) q^(t-1)` | `(v - c) q`, also `0` für `v <= c` |
| Kor. 5.3 (Pencil-Überdeckung, `q` ungerade, `(q+1)/2 <= v <= q`) | `q^t + (v - (q+1)/2) q^(t-1) + ((q-1)/2) q^(t-2)` | `(v - (q+1)/2) q + (q-1)/2` |
| Satz 8.2 (Teilfusion der Basiszeilen, `v < q`) | spart zusätzlich mindestens `2(q - v)` Zeilen | — |
| Phase 6A (dieses Repo) | `q^t + C(v, 2) q^(t-2)` | `C(v, 2)` |
| Phase 7 §14 (dieses Repo) | `q^t + C(max(0, 2v - q), 2) q^(t-2)` | `C(max(0, 2v - q), 2)` |

Vergleich an einem Fall (`q = 19`, `v = 18`): Bai `161` Blöcke (Tabelleneintrag `(3, 21, 18) = 9884` nach Teilfusion und Nachoptimierung), Phase 6A `153`, Phase 7 §14 `136`. Für `v = q` ungerade: Bai `(q^2 - 1)/2`, Phase 6A und §14 `q(q - 1)/2`.

Der Unterschied in der Bauart: Bei Bai bleibt die Spalte `∞` des Bush-Arrays erhalten und nur die neue Spalte ist eine Färbung. In Phase 6A und Phase 7 werden **zwei** Spalten frei beschriftet (`a` und `b`, §2 und §11.1 des Phase-7-Dokuments), und jede muss nur auf `q` Richtungen jedes Symbol zeigen; dort ist eine einzelne Gerade bereits eine blockierende Menge. Deshalb greift Bais Obergrenze `floor(q/2)` hier nicht.

Zwei Stellen, die für die Wortwahl wichtig sind:
- Bais offene Frage 2 nennt als Beispiel, dass eine Färbung mit `c = 5` Farben für `q = 9`, `t >= 4` (über Projektionen in höhere Dimension) `CAN(6, 11, 9) <= 767637` ergäbe, gegen `793881` bei ihm. `767637` ist genau der Phase-6A-Wert für `(6, 11, 9)`: `(q - c) q = C(q, 2)` für `c = (q+1)/2`. Phase 6A erreicht diese Zahl auf anderem Weg; ob damit Bais Frage in seinem Modell beantwortet ist, ist **nicht geprüft** und wird nicht behauptet.
- Bai schreibt selbst, er habe in der Covering-Array-Literatur keine frühere Verwendung von blockierenden Mengen oder Ebenen-Zerlegungen gefunden, bei nicht vollständiger Suche. Das ist seine Angabe, hier nicht nachgeprüft.

### 2.2 Sitjar (2026), Vereinigung von Nebenklassen: Rahmen der Löserlisten

§2.3, Lemma 1 dort: Für einen linearen `[k, d]`-Code `C` über `GF(q)`, dessen Erzeugermatrix auf je `t` Spalten Rang `d` hat, ist die Vereinigung von `m` Nebenklassen genau dann ein `CA(m q^d; t, k, q)`, wenn die Vertreter auf jeder `t`-Spaltenmenge alle `q^(t-d)` Nebenklassen der Projektion treffen. Sitjar ordnet das der bekannten Familie gruppen- und hashbasierter Bauarten zu. Beispiele dort: `34` Nebenklassen eines `[7, 2]`-Codes über `GF(5)` (`850` Zeilen, nach Streichen überflüssiger Zeilen `CA(825; 4, 7, 5)`) und `508` Nebenklassen des Einsen-Codes der Länge 9 über `GF(7)` (`CA(3556; 4, 9, 7)`), beide per lokaler Suche.

Folge: Der Rahmen von Phase 7 (Vertreterliste `R`, Nebenklassen des Kerns `K_t`, Dimension `t - 2`) ist ein Fall dieses Lemmas. Eigener Anteil in Phase 7 ist die Wahl des Codes `K_t`, die Rückführung der Bedingung auf Stärke 2 unabhängig von `t` (Aussage A), das Modell für `v < q` und die geschlossene Liste aus §14. Die Zahl `34` bei `q = 5` tritt bei Sitjar (`t = 4`, anderer Code, eine Nullspalte laut §4 des Phase-7-Dokuments) und in Phase 7 (`m = 34`) auf; ein Zusammenhang ist **nicht untersucht**.

Eine allgemeine Formel für `k = q + 2` oder für `v < q` enthält Sitjars Arbeit nicht; ihre Einträge an den hier betroffenen Zellen sind Nachoptimierungen von Bais Arrays.

### 2.3 CKRS (2010), nach Bais Darstellung und `table/references.csv`

Colbourn, Kéri, Rivas Soriano, Schlage-Puchta: Satz 3.2 (eine Zusatzspalte, `q^t + (q - 1) q^(t-1)`), Lemma 3.3 (`q^(t-2)` Zeilen weniger), Lemma 3.1 (Fusion, zwei Zeilen je entferntem Symbol). **Volltext nicht gelesen**; die Angaben stammen aus Bais Abschnitten 1, 2 und 11 und aus [`docs/GENERAL_TQV_PROOF.md`](GENERAL_TQV_PROOF.md) §4.

### 2.4 Wer hält die Tabellenwerte an den 48 Zellen mit `v < q`?

Etiketten in `ca_frame.csv @ e673ab4` (Zeile mit dem kleinsten `N` bei `k' >= k`): 17-mal „orthogonal array fuse …“ (teils mit Nachoptimierung), 12-mal Nachoptimierung oder Simulated Annealing auf Tabellen-Arrays, 9-mal zweizeilige CPHF, 7-mal Bais `poly2` mit Pencil-Überdeckung (teils ausgedünnt), 2-mal „extended OA (Colbourn) special fuse“, 1-mal elliptisches Zwei-Block-Array. Keine dieser Zeilen nennt eine Bauart mit zwei freien Spalten oder die Zahl `C(2v - q, 2)`. Alle 76 Scan-Zellen haben in der Tabelle größere Werte ([`docs/PHASE7_VQ_SCAN.md`](PHASE7_VQ_SCAN.md)).

### 2.5 Weitere Treffer der Suche (anderer Parameterbereich)

- Bai, Zwei-Block-Arrays aus Kurven: `2q^t - q^(t-1)` bzw. `2q^t - q^(t-2)` Zeilen bei deutlich mehr als `q + 2` Spalten; `v < q` nur über Fusion.
- Shokri, Moura, Stevens (arXiv:2510.13122): Stärke 4, `(q^2 + 1)/2` Spalten.
- Colbourn, Ingalls, Jedwab, Saaltink, Smith, Stevens (arXiv:2210.11961): Stärke 3, `q^2 + 2` Spalten.

Keine davon betrifft `k = q + 2` mit Zeilenzahl nahe `q^t`.

## 3. Ergebnis und Wortwahl

- Die Formel aus §14 wurde in keiner gelesenen Quelle gefunden. Belegart: **Suche in den oben genannten Quellen, nicht vollständig**.
- Zulässig nach Regel 4: „kleiner als `ca-tools` am Commit `e673ab4`“. Nicht zulässig: „neu“, „Rekord“.
- Die Bauart gehört in die Familie von Bai (2026). Beim Melden fremde Vorarbeit zuerst nennen.

## 4. Herkunft, wie sie in `HOW.md` stehen sollte (Vorschlag, Entscheidung offen)

1. Bush (1952): Polynomauswertung, `OA(q^t; t, q+1, q)`.
2. CKRS (2010): Zusatzspalte mit Reparaturzeilen; Fusion.
3. Bai (2026, `polychrome-bai2026`): Zusatzspalte als Färbung von `AG(2, q)`, blockierende Mengen, Alphabet-Einschränkung für `v < q`, Pencil-Überdeckung.
4. Sitjar (2026): Vereinigung von Nebenklassen eines linearen Codes (Lemma 1), für die Löserlisten bei `v = q`.
5. Eigener Schritt: zwei frei beschriftete Spalten über den `q` Auswertungsspalten, Rückführung auf Stärke 2, Liste mit `q^2 + C(max(0, 2v - q), 2)` Vertretern.

## 5. Grenzen und Restliste

Nicht gelesen: CKRS (2010) im Volltext; Colbourn (2004, 2008, 2014, 2015); Hartman (2005); Ji–Yin (2010); Ji–Li–Yin (2012, Quelle des Tabellenwerts `4375` bei `(5, 7, 5)`); Hedayat–Sloane–Stufken; Chateauneuf–Kreher (2002); Colbourn–Lanus (2018); Nayeri–Colbourn–Konjevod (2013). Nicht geprüft: neuere Fassungen von Bais Preprint und Ablage auf Zenodo (die gelesene Fassung trägt das Datum 30.10.2026 und nennt §8 als neu in dieser Fassung), Sitjars Archiv ab Version 1.10, `aadwyer/CA_Database`, offene Issues von `ca-tools`. Der alphaXiv-Index liefert Top-Treffer, keine Vollliste.

Die ältere Restliste in [`docs/LITERATURE_CHECK_T4_NEARBUSH.md`](LITERATURE_CHECK_T4_NEARBUSH.md) §8.2 gilt weiter.
