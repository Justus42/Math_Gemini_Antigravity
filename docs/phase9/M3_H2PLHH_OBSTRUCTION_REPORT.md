# Phase 9 / PR #54 (Option C): Realisierbarkeits- & Obstruktionsbericht zu `H_2P_L_HH` (`LP_2P_no3PLL = 143/81`)

- **Datum:** 2026-11-28
- **Branch:** `exp/phase9-biaffine-3d` (Basis `0686d85`)
- **Zielprüfung:** Diskrete Realisierbarkeit der aggregierten LP-Lösung `LP_2P_no3PLL = 143/81 q^3 (~1.7654 q^3)` mittels `H_2P_L_HH`-Blöcken auf `z*` im 3D-biaffinen Modell `M_3(R_3)` (`full-bg3`, `k = q + 3`, `3 <= t <= q`).
- **Ergebnis (Abbruchkriterium AP 2.3 sauber ausgelöst):** **Negativbefund mit drei unabhängigen, exakt bewiesenen `Omega(q^3)`-Obstruktionen** (rechnerisch verifiziert in [`scripts/phase9_m3_h2plhh.py`](../../scripts/phase9_m3_h2plhh.py), Gesamtlaufzeit `50.03 s` für `q = 7..25`). Keine neuen Bestwerte gefunden; AP 3 (Dual-Verify) entfällt planmäßig; bestehende 5/5 Dual-Verify-Bestwerte (`607, 914, 1319, 2417, 4026`) bleiben unverändert.
- **Governance:** `verifiers/`, `submission/`, `staging/`, `results/`, `data/phase8_baer/` strikt unverändert; keine Schreibvorgänge auf `ca-tools`.
- **Belegstatus:** Exakte Rational-LP-Zertifikate (`LP-Vorhersage` / `Argument`), exaktes `check_m3` (`q = 7..13`), diskrete Zählung (`q = 16..25`); `Regel-2d offen`.

---

## 1. AP 1.1: Ausgangspunkt (`LP_2P_no3PLL = 143/81`) und Korrektur der Aggregat-LP

Die aggregierte LP `LP_2P_no3PLL` aus [`M3_46_27_IMPROVEMENT_REPORT.md`](M3_46_27_IMPROVEMENT_REPORT.md) §1.1 lieferte das Primaloptimum `143/81 ≈ 1.765432` mit:
- **Light-Ebenen (`Summe = 27/27`):** `L_3LHH = 10/27`, `L_1LL = 1/3`, `L_1LH = 8/27`.
- **Heavy-Ebene `z*` (`Summe = 62/81`):** `H_3HHH = 14/81`, `H_1HH = 4/9 (36/81)`, `H_2P_L_HH = 4/27 (12/81)`.

Die explizite diskrete Übersetzung eines `H_2P_a(a_0; B_sub, C_sub)`-Blocks der Breite `h_sub = s * q` (`0 < s <= 2/3`) für ein fixes leichtes Symbol `a_0 in A_L` auf einer Zeile `(y, z*)` lautet:
$$H_{2P,a}(a_0; B_{\mathrm{sub}}, C_{\mathrm{sub}}) = \big\{(x, y, z^*, a_0, b_{u \bmod |B_{\mathrm{sub}}|}, c_{(u + x) \bmod |C_{\mathrm{sub}}|}) : x \in \mathbb{F}_q,\; 0 \le u < \max(|B_{\mathrm{sub}}|, |C_{\mathrm{sub}}|)\big\}.$$
Für `|B_sub| = |C_sub| = s * q` hat dieser Block exakte Kosten `s * q^2`, deckt `2 s q` volle `x`-Geraden (`ab` und `ac`), deckt `s^2 q^2` `LHH`-Tripel (`Tripel-Quote = s` pro Punkt) und erzeugt auf jeder Zelle `(x, y, z*)` `0` Kopien aus `A_H`, `s q` distinkte aus `B_H` und `s q` distinkte aus `C_H`. Um `s = 2/3` (`143/81`) zu erreichen, muss `B_sub = B_H, C_sub = C_H` auf `r_2p = round(2q/27)` Symbolen je Oktant gewählt werden.

---

## 2. Drei unabhängige `Omega(q^3)`-Obstruktionen (`Argument` + exakter `Fraction`-Simplex)

### Obstruktion 1 — Zeilenweise Heavy-Multiplizität auf `z*` (Widerlegung von `1885/1107` und `143/81`)
Auf **jeder einzelnen Zeile `y`** der Heavy-Ebene `z*` tragen `u_a` Punkte/Spalte aus `H_2P_a` nichts zu `A_H` bei (`0` für `A_H`, `<= u_a` für `B_H, C_H`), analog `u_b` nichts zu `B_H` und `u_c` nichts zu `C_H`. Mit `w` übrigen Punkten/Spalte auf Zeile `y` erfordert `Typ 1` auf `z*` (`|A_H| = |B_H| = |C_H| = h = 2q/3`):
$$u_b + u_c + w \ge h, \qquad u_a + u_c + w \ge h, \qquad u_a + u_b + w \ge h.$$
- **Gleichheit (`2` distinkte Heavy-Inzidenzen pro `H_2P`-Punkt ohne Überlappung)** erfordert `u_a + u_b <= h` usw., im symmetrischen Fall also **`s <= h/2 = 1/3`** (disjunkte Hälften `B_{H1}, B_{H2}` auf derselben Zeile `y`). Bei `s = 1/3` sinkt aber die `LHH`-Tripel-Quote von `2/3` auf `1/3`, womit das LP-Optimum **exakt auf `49/27` (`H_2P` nutzlos) bzw. `46/27` (`H_2P = 0`) zurückfällt**.
- **Bei vollem `s = 2/3` (`143/81`-Regime)** verletzt jede Zeile `y` mit `H_2P`-Block zwangsläufig `u_a = 2/3 > 1/3`:
  * 1 Block/Zeile (`f_1`) lässt `A_H` komplett offen und erzwingt `2/3 q^2` Filler-Punkte auf derselben Zeile, die dort nur noch `<= 1` statt `3` neue Heavy-Symbole liefern;
  * 2 Blöcke/Zeile (`f_2`, Paarung `a+b`) überdecken `C_H` doppelt (`1.5` Heavy/Punkt);
  * 3 Blöcke/Zeile (`f_3`) überdecken alle drei Mengen doppelt (`1.0` Heavy/Punkt).
- **Exakte Folge (Zeilen-gekoppeltes Rational-LP in `scripts/phase9_m3_h2plhh.py`):**
  * **Freies LP (`allow_3p_ll = True`):** Die aggregierte Schranke `1885/1107 = 1.7028` war ein Aggregat-Artefakt; zeilen-exakt gilt wieder **`OPT = 46/27 = 1.703704` mit `H_2P_vol = 0`**.
  * **Ohne `3P` in `LLL/LLH` (`allow_3p_ll = False`):** **`143/81 = 1.765432` ist zeilen-exakt unzulässig**; das Optimum steigt sofort auf **`1879/1053 = 1.784425`** (`f_2 = 8/117`, `f_half = 8/117`, `+0.0190 q^3`).

### Obstruktion 2 — `HHH`-3-Zylinder-Überlappung (`|U_HHH| + |U_LHH| = Omega(q^3)`)
Sowohl `143/81` als auch `1879/1053` setzen `H_1HH = 4/9` und `H_0HHH = 0` voraus — also eine **überlappungsfreie** Partition von `H^3` (`|H| = 2q/3`) durch drei `1P`-Zylinder `E_ab^1P x H`, `E_ac^1P x H`, `E_bc^1P x H` mit Gesamtgröße `|E_ab^1P| + |E_ac^1P| + |E_bc^1P| = |H|^2`. Wie in [`M3_46_27_IMPROVEMENT_REPORT.md`](M3_46_27_IMPROVEMENT_REPORT.md) §1.1 bewiesen, ist dies nur an der degenerierten Ecke `E_ab^1P = H^2, E_ac^1P = E_bc^1P = empty` möglich (die `4/9` `HH`-Paare ohne `3P`-Zulässigkeit offen lässt). Bereits eine konservative Deckelung der `H_1HH`-Quote auf `1/2` (reale symmetrische 3-Zylinder-Überlappung liegt noch darunter bei `<= 38/81 ≈ 0.469`) hebt das zeilen-exakte LP sofort zurück auf **`49/27 = 1.814815`**.

### Obstruktion 3 — Light-Plane-Starvation von `z(a_0)` (`pad(a_0) >= (1/3) q^2`)
Für jedes leichte Symbol `a_0 in A_{L1}`, das einen vollen Block `H_2P_a(a_0; B_H, C_H)` auf `z*` trägt:
- Auf der Light-Ebene `z(a_0)` werden `q` volle Zeilen (`q^2` Punkte) mit `a = a_0` benötigt.
- `H_2P_a(a_0; B_H, C_H)` entfernt jedoch **100%** aller `a_0 x B_H`-Paare, `a_0 x C_H`-Paare und `a_0 x B_H x C_H`-Tripel von `z(a_0)`.
- Übrig bleiben für `z(a_0)` höchstens die `1P_LL`-Geraden `a_0 x B_L` (`q/3`) und `a_0 x C_L` (`q/3`) — zusammen maximal `(2/3) q` Zeilen (wobei zudem die Hälfte auf `z(b_0), z(c_0)` benötigt wird).
- **Konsequenz:** Jedes `a_0 in A_{L1}` erzwingt mindestens **`pad(a_0) >= (1/3) q^2`** reine Dummy-Punkte auf `z(a_0)` (`+50%` Aufschlag auf `H_2P_a`). Nimmt man diese exakte Erhaltungsbedingung ins zeilen-exakte LP auf, kollabiert das Optimum **identisch auf `49/27 = 1.814815` mit `H_2P_vol = 0`**!
- **Kein Ausweg durch Platzierung von `H_2P_a` auf `z(a_0)`:** Auf einer einzelnen Zeile `y` von `z(a_0)` bleiben `q - 1` Zeilen leer; verteilt man `b_u` hingegen auf verschiedene Zeilen `y = u` von `z(a_0)`, bricht `Typ 2` für `(a_0, c_v)` an **`q - 1` von `q` Normalen `al`** (rechnerisch bestätigt in Teil 3 von `scripts/phase9_m3_h2plhh.py`: `6/7, 7/8, 8/9, 10/11, 12/13` Normalen fehlerhaft, `68..408` Lücken).

### Zusammenfassung der exakten Rational-LP-Reihe (`scripts/phase9_m3_h2plhh.py` Teil 1)

| LP-Variante | Exaktes Optimum | Dezimalwert | `H_2P_vol` | Diagnose |
|---|---:|---:|---:|---|
| Aggregat `LP_2P` (bisher, ohne Zeilen-Kopplung) | `1885/1107` | `1.702800` | `4/369` | Aggregat-Artefakt |
| **Zeilen-exakt frei (`allow_3p_ll = True`)** | **`46/27`** | `1.703704` | **`0`** | Widerlegt `1885/1107` |
| Aggregat `LP_2P_no3PLL` (bisher) | `143/81` | `1.765432` | `4/27` | Aggregat-Artefakt |
| **Zeilen-exakt `no-3P-LL` (Obstruktion 1)** | **`1879/1053`** | `1.784425` | `56/351` | `+0.0190 q^3` (`f_2 + f_half`) |
| **Zeilen-exakt `no-3P-LL`, nur `s = 1/3` (`f_half`)** | **`49/27`** | `1.814815` | `16/81` | Kein Gewinn `< 49/27` |
| **Zeilen-exakt `no-3P-LL` + `HHH`-Cap `1/2` (Obstr. 2)** | **`49/27`** | `1.814815` | `4/27` | Kein Gewinn `< 49/27` |
| **Zeilen-exakt `no-3P-LL` + Light-Pad (Obstr. 3)** | **`49/27`** | `1.814815` | **`0`** | **`H_2P_L_HH` komplett dominiert** |

---

## 3. AP 1.2 & AP 2: Empirische Verifikation (`q = 7..25`, `scripts/phase9_m3_h2plhh.py`)

Exakte Messwerte des deterministischen `H_2P_L_HH`-Prototyps vor Schließung (`skel`, `skel_miss = (Typ0, Typ1, Typ2, Typ3)`) und nach deterministischer Schließung auf `check_m3 = 0` (`q <= 13`) bzw. `suff = 0` (`q <= 25`), im direkten Vergleich zu `143/81 q^3`, `49/27 q^3`, deterministischem `k`-Block (`scripts/phase9_m3_cyclic_opt.py`) und bisherigem PAWS-Bestwert:

| `q` | Variante (`r_LP = max(1, round(2q/27))`) | `skel` (`skel/q^3`) | `skel_miss` (`T0,T1,T2,T3`) | **Closed `m`** (`m/q^3`) | `2P` | `pad` (Obstr. 3) | `uLHH+uHHH` (Obstr. 2) | `exh` (Obstr. 1) | `143/81 q^3` | Det `k`-Block | PAWS Best |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `7` | `r2p=0` (Kontrolle) | `553` (`1.6122`) | `(0, 3204, 0, 81)` | `654` (`1.9067`) | `0` | `0` | `54+27` | `20` | `605.5` | `613` | **`607`** |
| `7` | `r2p=1 full s=2/3 (pair2)` | `693` (`2.0204`) | `(0, 802, 0, 39)` | `734` (`2.1399`) | `105` | **`96`** | `27+21` | `2` | `605.5` | `613` | **`607`** |
| `7` | `r2p=1 half s=1/3 (disj)` | `609` (`1.7755`) | `(0, 1813, 0, 65)` | `677` (`1.9738`) | `56` | `16` | `52+32` | `3` | `605.5` | `613` | **`607`** |
| `8` | `r2p=0` (Kontrolle) | `848` (`1.6562`) | `(0, 5826, 0, 112)` | `997` (`1.9473`) | `0` | `0` | `83+29` | `37` | `903.9` | `932` | **`914`** |
| `8` | `r2p=1 full s=2/3 (pair2)` | `1024` (`2.0000`) | `(0, 1605, 0, 66)` | `1090` (`2.1289`) | `144` | **`122`** | `47+25` | `0` | `903.9` | `932` | **`914`** |
| `8` | `r2p=1 half s=1/3 (disj)` | `920` (`1.7969`) | `(0, 2545, 0, 85)` | `1011` (`1.9746`) | `72` | `18` | `77+30` | `6` | `903.9` | `932` | **`914`** |
| `9` | `r2p=0` (Kontrolle) | `1179` (`1.6173`) | `(0, 11730, 0, 194)` | `1406` (`1.9287`) | `0` | `0` | `128+66` | `33` | `1287.0` | `1326` | **`1319`** |
| `9` | `r2p=1 full s=2/3 (pair2)` | `1404` (`1.9259`) | `(0, 5420, 0, 110)` | `1519` (`2.0837`) | `180` | **`140`** | `73+50` | `5` | `1287.0` | `1326` | **`1319`** |
| `9` | `r2p=1 half s=1/3 (disj)` | `1260` (`1.7284`) | `(0, 7287, 0, 147)` | `1413` (`1.9383`) | `90` | `11` | `112+60` | `6` | `1287.0` | `1326` | **`1319`** |
| `11` | `r2p=1 full s=2/3 (pair2)` | `2398` (`1.8017`) | `(0, 20089, 0, 254)` | `2691` (`2.0218`) | `264` | **`186`** | `198+101` | `39` | `2349.8` | `2425` | **`2417`** |
| `11` | `r2p=1 half s=1/3 (disj)` | `2288` (`1.7190`) | `(0, 19879, 0, 266)` | `2599` (`1.9527`) | `132` | `12` | `231+89` | `45` | `2349.8` | `2425` | **`2417`** |
| `13` | `r2p=1 full s=2/3 (pair2)` | `3861` (`1.7574`) | `(0, 48178, 0, 458)` | `4364` (`1.9863`) | `351` | **`254`** | `378+177` | `45` | `3878.7` | `4035` | **`4026`** |
| `13` | `r2p=1 full s=2/3 (single)` | `3861` (`1.7574`) | `(0, 56227, 0, 458)` | `4461` (`2.0305`) | `351` | **`254`** | `378+177` | **`142`** | `3878.7` | `4035` | **`4026`** |
| `13` | `r2p=1 half s=1/3 (disj)` | `3731` (`1.6982`) | `(0, 49451, 0, 473)` | `4286` (`1.9508`) | `182` | `12` | `416+162` | `82` | `3878.7` | `4035` | **`4026`** |
| `16` | `r2p=1 full s=2/3 (pair2)` | `7072` (`1.7266`) | — (`suff`-Check) | `8155` (`1.9910`) | `528` | **`368`** | `768+316` | `159` | `7231.2` | **`7595`** | — |
| `17` | `r2p=1 full s=2/3 (pair2)` | `8432` (`1.7163`) | — (`suff`-Check) | `9759` (`1.9864`) | `612` | **`400`** | `922+385` | `147` | `8673.6` | **`9114`** | — |
| `19` | `r2p=1 full s=2/3 (pair2)` | `11685` (`1.7036`) | — (`suff`-Check) | `13515` (`1.9704`) | `741` | **`502`** | `1365+526` | `178` | `12109.1` | **`12848`** | — |
| `23` | `r2p=2 full s=2/3 (pair2)` | `21666` (`1.7807`) | — (`suff`-Check) | `24373` (`2.0032`) | `2208` | **`1543`** | `2190+968` | `53` | `21480.0` | **`22849`** | — |
| `25` | `r2p=2 full s=2/3 (pair2)` | `27525` (`1.7616`) | — (`suff`-Check) | `31373` (`2.0079`) | `2550` | **`1786`** | `2988+1226` | `398` | `27584.9` | **`29108`** | — |
| `25` | `r2p=2 half s=1/3 (disj)` | `26600` (`1.7024`) | — (`suff`-Check) | `30965` (`1.9818`) | `1300` | `126` | `3229+1075` | `760` | `27584.9` | **`29108`** | — |

**Eindeutige Bestätigung des Abbruchkriteriums (AP 2.3):**
1. Bei `q = 25` liegt das ungeschlossene Skelett exakt auf dem LP-Wert (`27525 = 1.7616 q^3` vs. `143/81 = 27584.9`), aber alle drei Obstruktionen addieren **reine `Omega(q^3)`-Zusatzkosten** (`pad = 1786 = 0.114 q^3`, `uLHH+uHHH = 4214 = 0.270 q^3`, `exh = 398` bei `pair2` bzw. `1232` bei `single`), sodass die geschlossene `check_m3 = 0`-Lösung bei `~1.95–2.01 q^3` landet.
2. Für alle `q in {7, 8, 9, 11, 13, 16, 17, 19, 23, 25}` bleibt `H_2P_L_HH` **deutlich oberhalb** des deterministischen `k`-Block-Konstruktors (`15/8 = 1.875 q^3`) und der bestehenden PAWS-Bestwerte (`607, 914, 1319, 2417, 4026`).
3. Gemäß AP 2.3 wurde daher sauber abgebrochen (kein PAWS-Warmstart auf schlechteren `H_2P_L_HH`-Seeds, keine unnötigen Dual-Verify-Läufe in AP 3).

---

## 4. Reproduzierbarkeit

```bash
python3 scripts/phase9_m3_h2plhh.py --qs 7,8,9,11,13,16,17,19,23,25 --check-m3-max 13
```
