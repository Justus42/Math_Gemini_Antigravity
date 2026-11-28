# Literaturprüfung zu Phase 8 und zur Pareto-Liste (`docs/LITERATURE_CHECK_PHASE8.md`)

- **Stand:** 2026-11-28, ca. 16:30 MEZ. **Autor:** Claude (Prüferchat). Prüfvermerk nach `RULES.md` „Meldung nach außen“ 2c.
- **Gegenstand:** die 30 Zellen der Pareto-Liste (`t = 3..6`, `k = q + 2`, je Datei `<= 50 MiB`, kleiner als `chrispbsmolen/ca-tools @ b689967`; Lauf `P8-FINAL-VERIFY`, `P8-FINAL-NACHPRUEFUNG`) und die Bauarten dahinter:
  - Klassen ohne volle Gerade mit Rédei-Klassen (`data/phase8/`, `q = 11, 13, 17, 19, 23`; [`docs/phase8/NOTIZ_1_KLASSEN_OHNE_GERADE.md`](phase8/NOTIZ_1_KLASSEN_OHNE_GERADE.md), [`docs/PHASE8_ARGUMENTE.md`](PHASE8_ARGUMENTE.md)),
  - Baer-Gitter, Fassung v3 (`data/phase8_baer_v3/`, `q = 9, 16, 25`; [`docs/phase8/NOTIZ_3_UNTERGRENZE_BAER.md`](phase8/NOTIZ_3_UNTERGRENZE_BAER.md) §3, [`docs/phase8/SPRINT_BAER3_PRIME_LOG.md`](phase8/SPRINT_BAER3_PRIME_LOG.md)),
  - Spur-Baer-Hybrid `q = 16` (`data/phase8_q16_hybrid/`) und Spur-Gitter `q = 27` (`data/phase9_explore/`; [`docs/phase9/EXPLORE_KERNEL_Q27_LOG.md`](phase9/EXPLORE_KERNEL_Q27_LOG.md)),
  - die in Notiz 1, 3 und 4 sowie in `PHASE8_ARGUMENTE.md` zitierten Geometrie-Sätze.
- **Ergebnis in einem Satz:** In den gelesenen Quellen steht keine dieser Listen und keine Bauart mit Baer-Unterebenen, Rédei- oder Spur-Mengen für Covering Arrays. Nächste Vorarbeit sind CKRS (2010, Lemma 3.3) für das Gerüst und Bai (2026, Satz 5.1 und Prop. 5.4) für Überdeckungen der Ebene durch blockierende Mengen. **Kein Neuheitsanspruch**; die Prüfung ist nicht vollständig (§6).

## 1. Was gelesen wurde

| Quelle | Wie | Gelesene Teile | Belegart |
| --- | --- | --- | --- |
| X. Bai, „Covering arrays from line-polychromatic colourings of affine planes“, Preprint 30.10.2026, `doi:10.5281/zenodo.23787051` | alphaXiv-Index, Fassung `v1` | S. 1–9, 17–19 (Einleitung, §2–§6, Tab. 4, §11–§12, Literatur) | Volltext, in Teilen |
| X. Bai, „Two-row covering perfect hash families from Singer cycles, and upper bounds for their length“, Fassung vom 08.11.2026 (`singer-cphf-bai2026`) | alphaXiv-Index, `v2` | S. 1–5, 12, 14, 17, 19, 21 | Volltext, in Teilen |
| T. N. Sitjar, „New upper bounds for covering arrays of strengths 3 to 6“, Version 1.4, 13.11.2026 | alphaXiv-Index, `v4` | vollständig (9 Seiten) | Volltext |
| CKRS (2010), Autoren-Preprint | im Phase-7-Vermerk gelesen ([`LITERATURE_CHECK_PHASE7_VQ.md`](LITERATURE_CHECK_PHASE7_VQ.md) §2.6) | Lemma 3.1, Satz 3.2, Lemma 3.3 | Volltext (Preprint), nicht neu gelesen |
| D. Bartoli, T. Héger, G. Kiss, M. Takáts, arXiv:1706.06583 (2017) | alphaXiv-Index, `v1` | S. 1–14, 17, 20–22 | Volltext |
| A. A. Bruen, „Baer subplanes and blocking sets“, Bull. AMS 76 (1970) | Auszug der Original-PDF über die Websuche | Satz „Baer subplanes form blocking sets“, Lemma 2, Satz 1 | Auszug Original |
| A. A. Bruen, „Blocking sets and skew subspaces of projective space“, Canad. J. Math. 32 (1980) | Auszug über die Websuche | Satz 1 (Zitat von Bruen 1970/1971) | Auszug, Sekundärquelle für die Schranke |
| A. E. Brouwer, A. Schrijver (1978), JCTA 24 | Auszug der Original-PDF (CWI-Archiv), Gate-1-Prüfung 27.11. | Einleitung, Satz | Auszug Original |
| A. Blokhuis (1994), Combinatorica 14 | Zusammenfassung und Literaturliste (Springer/Unpaywall) | Abstract | Abstract |
| `chrispbsmolen/ca-tools @ b689967` | lokale Kopie `table/` | `references.csv`, `ca_table.csv.gz`, `ca_frame.csv` | Tabellenstand |
| Suche | alphaXiv (3 Anfragen), Websuche (6 Anfragen) | Trefferlisten gesichtet | — |

Nicht abrufbar in dieser Sitzung: die Zenodo-Seite `10.5281/zenodo.24054350` (Abruf begrenzt), die Volltexte bei ScienceDirect (Jamison 1977) und der AMS (Bruen 1970, nur Suchauszug).

## 2. Befunde zur Vorarbeit bei Covering Arrays

### 2.1 Gerüst: CKRS (2010), Lemma 3.3

Unverändert aus dem Phase-7-Vermerk (§2.6 dort): Die Vertreterliste mit zwei Zusatzspalten `a`, `b` über den Nebenklassen des Bush-Codes ist der Sache nach die Bauart von CKRS, Lemma 3.3; Phase 7 und Phase 8 verfeinern sie. In `ca-tools @ b689967` tragen 16 der 30 Vergleichswerte das Etikett „Coset-lift refinement of CKRS Lemma 3.3“ (unsere Zeilen aus PR `#88`/`#91`), 12 „SCA_Busht“, je einer „groupOrbit“ und „polynomial“.

### 2.2 Blockierende Mengen: Bai (2026), Färbungen

- Bai fügt **eine** neue Spalte hinzu: eine Färbung von `AG(2, q)`, verknüpft mit der Auswertung bei `α ∈ F_(q^2) \ F_q`. Jede Farbklasse muss **alle** `q + 1` Richtungen blockieren; daher die Schranke `2q - 1` je Klasse (Jamison, Brouwer–Schrijver; dort Satz 2.2) und höchstens `floor(q/2)` Farben (Prop. 4.1).
- **Satz 5.1 (Überdeckungen)** erlaubt überlappende Klassen gegen Zusatzzeilen; **Prop. 5.4** bestimmt das Optimum dieses Kostenmodells; **Kor. 5.3** (Büschel-Überdeckung) ist das Optimum für ungerades `q`.
- **Satz 6.2** fügt zwei neue Spalten hinzu (`k = q + 3`), mit zwei Färbungen, die gemeinsam surjektiv sind.
- Bai schreibt (§11), er habe in der Covering-Array-Literatur keine Verwendung blockierender Mengen gefunden, bei nicht vollständiger Suche. Er nennt Färbungen projektiver Ebenen (Csima–Füredi 1986) und Zerlegungen von `PG(2, q)` in disjunkte blockierende Mengen (Barát–Marcugini–Pambianco–Szőnyi 2006; Asgarli–Ghioca–Yip 2026) und merkt an, dass projektive blockierende Mengen bei Quadratzahlen nur `q + sqrt(q) + 1` Punkte brauchen (Baer-Größe).

**Einordnung:** In Phase 8 sind beide Spalten `a`, `b` des CKRS-Gerüsts frei beschriftet, und eine Klasse muss nur die `q` nicht-waagerechten Richtungen blockieren. Damit greifen die Schranken für **projektive** blockierende Mengen (Bruen, Blokhuis) statt der affinen (Jamison), und Baer-Unterebenen, Rédei- und Spur-Mengen werden als Klassen möglich. Diese Verbindung steht in den gelesenen Teilen von Bai nicht; sie ist aber eng mit Bais Satz 5.1 verwandt und sollte beim Melden als Vorarbeit genannt werden.

### 2.3 Weitere Quellen ohne Treffer

- **Bai, Singer-CPHF (08.11.2026):** zwei Zeilen, `k = 2q + 2`, Singer-Bahnen und Kegelschnitte; keine blockierenden Mengen, keine Baer-Unterebenen. Andere Spaltenzahl. Bais Ablage `deposit-bai2026` enthält Zeilen „Singer CPHF + one free column via … line-blocking covers of AG(3,7)“ (`ca_table`, `pr-14`) bei `k >= 2q + 2`; nicht unsere Zellen.
- **Sitjar (Version 1.4):** Lemma 1 (Vereinigung von Nebenklassen eines linearen Codes) ist der Rahmen der Löserlisten; keine Geometrie der Ebene, keine Bauart für `k = q + 2`.
- **alphaXiv-Suche** „covering arrays“ mit „blocking sets / Baer subplane / Rédei“: Treffer sind Bais Arbeiten, Sitjar, Shokri–Moura–Stevens (Stärke 4, andere Spaltenzahl) und reine Geometrie-Arbeiten (Rédei-Mengen, lineare Mengen, starke blockierende Mengen); keine verbindet beides.
- **`ca-tools @ b689967`:** Kein Eintrag in `references.csv` und kein Bauart-Etikett in `ca_table.csv.gz` nennt Baer, Rédei, Unterebene oder Spur. „blocking“ kommt einmal vor (Bai, `(5, 17, 7)`, `AG(3, 7)`).

## 3. Geometrie-Sätze, die in Phase 8 zitiert werden

| Aussage | Verwendet in | Quelle | Stand der Prüfung |
| --- | --- | --- | --- |
| Baer-Unterebenen sind blockierende Mengen; eine blockierende Menge mit `q + sqrt(q) + 1` Punkten ist eine Baer-Unterebene | Notiz 3 §3, Notiz 4 Satz C.2 | Bruen (1970) | **Auszug Original gelesen** (Satz und Satz 1) |
| Nichttriviale blockierende Menge in `PG(2, q)`: `|B| >= q + sqrt(q) + 1` | `PHASE8_ARGUMENTE.md` 1.1, Notiz 4 | Bruen (1970, 1971) | **Sekundär bestätigt** (Bruen 1980, Satz 1, zitiert [1, 2]; Ebert 1978); Bruen 1971 ungeprüft |
| Nichttriviale blockierende Menge in `PG(2, p)`, `p` prim: `|B| >= 3(p + 1)/2` | `PHASE8_ARGUMENTE.md` 1.1, Notiz 4 Satz C.1 | Blokhuis (1994) | **Abstract gelesen**, Aussage stimmt; Volltext ungeprüft |
| Blockierende Menge in `AG(2, q)`: `>= 2q - 1` Punkte | Notiz 3 §2, Notiz 4 | Jamison (1977); Brouwer–Schrijver (1978) | Brouwer–Schrijver: **Auszug Original**; Jamison: ungeprüft (Aussage über BS78 und Bai, Satz 2.2) |
| Wesentlicher Punkt `P` einer blockierenden Menge `B` liegt auf `>= 2q + 1 - |B|` Tangenten | Notiz 3 Lemma J, Notiz 4 | Blokhuis–Brouwer (1986) | **Sekundär** (Bartoli u. a. 2017, Result 3.11, mit dem Hinweis, dass dies zu Jamison/Brouwer–Schrijver äquivalent ist); Original ungeprüft |
| Index-Schranke für `k`-Erweiterer | Notiz 4 (zitiert als Lemma 3.12) | Bartoli–Héger–Kiss–Takáts (2017) | **Volltext gelesen**; siehe §5, Punkt 2 |
| Bipartiter Multigraph: Kantenfärbungszahl `= Δ` | `PHASE8_ARGUMENTE.md` 1.3 | König (1916) | Sekundär (arXiv:2308.16808, Satz 2.7); Original ungeprüft |
| Funktionen mit weniger als `(q + 3)/2` Richtungen sind linear über einem Teilkörper; Rédei-Mengen | Notiz 1 §4, Notiz 2 §7 | Rédei (1970); Lovász–Schrijver (1981); Blokhuis–Ball–Brouwer–Storme–Szőnyi (1999); Ball (2003) | Ungeprüft; die Aussage wird im Abstract von arXiv:2610.28002 so zitiert |
| Projektives Dreieck: blockierende Menge der Größe `3(q + 1)/2` für ungerades `q` | Hintergrund der Rédei-Klassen `x -> x^((q+1)/2)` | di Paola (1969) | Ungeprüft; Blokhuis (1994) nennt im Abstract „Vermutung von di Paola“ |
| `PG(2, q)`, `q` Quadrat, zerfällt in `q - sqrt(q) + 1` disjunkte Baer-Unterebenen | Hintergrund des Baer-Gitters | Bruck (1960) | Sekundär (Kurz, arXiv:2112.11763; Brouwer, CWI-Bericht); Original ungeprüft |

## 4. Herkunft, wie sie in `HOW.md` stehen sollte (Vorschlag, Entscheidung offen)

1. Bush (1952): `OA(q^t; t, q+1, q)` aus Polynomauswertung.
2. **CKRS (2010), Lemma 3.3: direkte Vorarbeit** für das Gerüst mit zwei Zusatzspalten über Nebenklassen; Lemma 3.1 nur, falls Fusion benutzt wird.
3. **Bai (2026, `polychrome-bai2026`), Satz 5.1, Prop. 5.4, Kor. 5.3:** Überdeckung von `AG(2, q)` durch blockierende Mengen gegen Zusatzzeilen; Satz 6.2 für zwei neue Spalten.
4. Sitjar (2026), Lemma 1: Vereinigung von Nebenklassen, soweit Löserlisten (`q = 11`) beteiligt sind.
5. Geometrie: Bruen (1970) für Baer-Unterebenen als blockierende Mengen; Rédei-Mengen und Spur-Mengen als bekannte blockierende Mengen vom Rédei-Typ; Bruck (1960) für Zerlegungen in Baer-Unterebenen, falls darauf Bezug genommen wird.
6. Eigener Schritt: Klassen müssen nur `q` Richtungen blockieren (zwei freie Spalten), daher projektive statt affine Mindestgröße; Packung solcher Klassen im Modell `M(R)`; Baer-Gitter v3, Spur-Hybrid `q = 16`, Spur-Gitter `q = 27`.

Wortwahl nach Regel 4: „kleiner als die Tabelle am Commit `b689967`“. Nicht zulässig: „neu“, „Rekord“.

## 5. Gegenlesen von Notiz 4 (kurz)

Sol hat Notiz 4 gelesen (`P8-NOTIZ4-PRUEFUNG-SOL`); die beiden Asymptotik-Reparaturen hat dieser Prüferchat eingearbeitet (`P8-NOTIZ4-REPARATUR`). Ein Gegenlesen der eingearbeiteten Fassung durch einen anderen Chat oder ein unbeteiligtes Modell steht damit weiter aus. Beim erneuten Lesen hier:

1. §2.3: `F = U + V + t_{11} <= 3p` stimmt, weil `t_{11} <= min(u_A, u_B) <= p` (Parameterbereich in §2.1).
2. §1, Zitat „Bartoli–Héger–Kiss–Takáts (2017), Lemma 3.12“: Die dort benutzte Ungleichung ist wörtlich **Result 3.11** (Blokhuis–Brouwer: jeder wesentliche Punkt liegt auf mindestens `2q + 1 - |B|` Tangenten), angewandt auf `B = A ∪ {P_∞}`. Lemma 3.12 ist die Umformulierung mit `k`-Erweiterern (für `k = 1`). In Notiz 4 präzisiert.
3. §1, Bruen-Absatz: Die Fallunterscheidung (volle nicht-waagerechte Gerade in `A_s` oder nichttriviale blockierende Menge `A_s ∪ {P_∞}`) ist vollständig, weil `A_s` keine volle Waagerechte enthält und die Ferngerade nur `P_∞` aus `B` enthält.

Kein weiterer Befund. Belegart bleibt „informelles Argument“.

## 6. Grenzen und Restliste

- Nicht gelesen: Bruen (1971); Jamison (1977); Blokhuis (1994) und Blokhuis–Brouwer (1986) im Volltext; König (1916); Rédei (1970); Lovász–Schrijver (1981); Blokhuis–Ball–Brouwer–Storme–Szőnyi (1999); Ball (2003); di Paola (1969); Bruck (1960); Csima–Füredi (1986); Barát–Marcugini–Pambianco–Szőnyi (2006); die Zeitschriftenfassung von CKRS (2010); die übrigen Punkte der Restliste in [`LITERATURE_CHECK_PHASE7_VQ.md`](LITERATURE_CHECK_PHASE7_VQ.md) §5.
- Nicht durchgesehen: `aadwyer/CA_Database`, Zenodo-Suche nach neueren Fassungen von Bai und Sitjar nach dem 13.11.2026 (Abruf begrenzt), Bais Begleitpapier zu zwei Blöcken über den Phase-7-Stand hinaus.
- Offene Pull Requests und Issues bei `ca-tools` (Regel 2b): zuletzt am 28.11., 14:02 MEZ geprüft (höchste PR-Nummer 93, ohne Bezug; Issues `#85`, `#86` Inhalt ungelesen). Vor einer Einreichung erneut prüfen.
- Die Suche ist nicht erschöpfend. Eine frühere Verwendung von Baer-Unterebenen oder Rédei-Mengen in Covering Arrays bleibt möglich.
