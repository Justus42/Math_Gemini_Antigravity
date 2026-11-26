# Systematischer Vorab-Scan: `N_pred(t, q, v) = q^t + C(v, 2) * q^(t - 2)` gegen `ca-tools`

- **Datum (UTC):** `2026-11-26`
- **Branch:** `exp/phase6a-general-tqv` (Basis `origin/main` @ `68c8402`)
- **Geprüfter Tabellenstand (`chrispbsmolen/ca-tools`):** Commit **`e673ab45758a3959710c662a34837f79f6add689`** (`table/ca_frame.csv`, `table/ca_table.csv.gz`, `table/derived.csv`, rein lesend via `gh api`)
- **Scan-Skript:** [`scripts/scan_general_tqv.py`](../scripts/scan_general_tqv.py) (Pure Python `std`-only, deterministisch, Laufzeit `0,743 s`)
- **Neuheitsvorbehalt & Wortwahl (Regel 4):** Alle Vergleiche gelten streng als **„kleiner als `ca-tools` am Commit `e673ab4`“**. Die externe Literaturprüfung für die allgemeine Formel `q^t + C(v, 2) * q^(t - 2)` ist noch nicht abgeschlossen; externe Einreichungs-Sperre aktiv.

---

## 1. Methodik & Zusammenfassung

1. **Exakte monotone Hülle:** Für jede Zelle `(t, k, v)` wurde
   $$N_{\text{eff}}(t, k, v) = \min_{k' \ge k} \min\big(\texttt{ca\_table}(t, k', v),\; \texttt{ca\_frame}(t, k', v),\; \texttt{derived}(t, k', v)\big)$$
   berechnet (`DISPUTED` und `FAILED_PENDING_RECHECK` in `ca_table.csv.gz` ausgeschlossen).
2. **Vollständiger Suchraum (`t in 2..7`):** Für jede Stärke `t in 2..7` wurden alle Tabellen-Obergrenzen aus `ca_frame.csv` bestimmt (`q_max = floor(max_N^(1/t)) + 3`; für jedes größere `q` gilt bereits `q^t > max_N`) und für jedes `(t, k, v)` sämtliche zulässigen Primzahlpotenzen `q >= max(v, k - 2, t - 2)` geprüft (das Minimum wird stets von der kleinsten zulässigen Primzahlpotenz `q` angenommen).
   - `t = 2`: `max_v = 25`, `max_N = 2.425` (`q <= 51`) → **`0` Treffer** (strikte Unterbietung; `(2, 4, 2)` mit `N = 5` erreicht Gleichstand mit einem bereits als `VERIFIED` geführten Eintrag in `ca_table.csv.gz`).
   - `t = 3`: `max_v = 25`, `max_N = 109.225` (`q <= 49`) → **`5` Treffer**.
   - `t = 4`: `max_v = 25`, `max_N = 7.031.233` (`q <= 53`) → **`12` Treffer** (`5` bereits in `results/t4_nearbush/`, `7` neu).
   - `t = 5`: `max_v = 25`, `max_N = 166.015.225` (`q <= 46`) → **`19` Treffer**, `1` `CITED`-Gleichstand `(5, 7, 5)` (`N = 4.375`).
   - `t = 6`: `max_v = 25`, `max_N = 18.232.119.844` (`q <= 53`) → **`20` Treffer**.
   - `t = 7`: `ca_frame.csv` enthält ausschließlich `v = 2` (`max_N = 9.920`, `q <= 5`) → **`0` Treffer**.
3. **Gesamtbilanz:** Exakt **`56` Treffer** mit `N_pred < N_eff` (alle `56` bei exakt `k = q + 2`; `0` zusätzliche projizierte Zellen mit `k < q + 2` unterbieten `N_eff`), davon:
   - **`already_in_t4_nearbush`:** `5` Zellen (`q = 7, 8, 9, 11, 13` bei `t = 4, v = q`),
   - **`phase6a_small`** (`est_py_s <= 30 s` und unkomprimierte Dateigröße `<= 10 MB`, neu): **`12` Zellen**,
   - **`phase6b_large`** (`est_py_s > 30 s` oder Dateigröße `> 10 MB`): **`39` Zellen**.
4. **Abgleich gegen Claudes Stichproben-Zahl (`56` Zellen bei `0b79e3f`):**
   - **Exakte Übereinstimmung (`56 == 56`):** Sowohl gegen `ca_frame.csv` allein (`56` Zellen) als auch gegen die vollständige monotone Hülle aus `ca_frame.csv + ca_table.csv.gz + derived.csv` (`56` Zellen am Commit `e673ab4` sowie `56` Zellen am Commit `0b79e3f`) ergibt sich exakt dieselbe Menge von **`56` Zellen**.
   - **Begründung für die `0`-Abweichung:** (a) Der Übergang `0b79e3f → e673ab4` übernahm PR `#88` (`t = 3`, `v in {10, 12, 14, 20}`, Spalten `k in 15..38`) in die Tabelle; keine dieser Zellen kollidiert mit den `5` `t = 3`-Treffern (`v in {9, 11, 13, 18, 19}`). (b) `table/derived.csv` unterbietet keine der `56` Zellen. (c) Für `t = 7` enthält `ca_frame.csv` nur `v = 2`, wo `q^7 + q^5` weit über den binären Tabelleneinträgen liegt. (d) Jede der `56` Zellen liegt exakt an der Stufe `k = q + 2` unmittelbar nach Bushs `OA(q^t; t, q + 1, q)`; keine projizierte Spaltenzahl `k < q + 2` erzeugt zusätzliche Treffer.

*(Zeitmodell zur Vorklassifikation auf `Intel(R) Xeon(R) CPU @ 2.30GHz`, kalibriert an Phase 5E: `est_ca_s = max(0,01; 0,005 + work / 5,5e8)`, `est_py_s = 0,05 + work / 3,2e6`, `work = C(k, t) * N_pred`.)*

---

## 2. Vollständige Trefferliste (`N_pred < N_eff` gegen `ca-tools @ e673ab4`, sortiert nach `C(k, t) * N_pred`)

| # | Zelle `(t, k, v)` | `q` | `N_pred` | `N_eff` (`tier`) | `Delta` | `C(k, t) * N_pred` | `est_ca_s` | `est_py_s` | Dateigröße (ca.) | Klassifikation |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| 1 | `(3, 11, 9)` | `9` | `1.053` | `1.089` (`VERIFIED`) | `−36` | `173.745` | `0,01 s` | `0,10 s` | `0,02 MB` | `phase6a_small` |
| 2 | `(4, 9, 7)` | `7` | `3.430` | `3.556` (`VERIFIED`) | `−126` | `432.180` | `0,01 s` | `0,19 s` | `0,06 MB` | `already_in_t4_nearbush` |
| 3 | `(3, 13, 11)` | `11` | `1.936` | `1.991` (`VERIFIED`) | `−55` | `553.696` | `0,01 s` | `0,22 s` | `0,05 MB` | `phase6a_small` |
| 4 | `(4, 10, 8)` | `8` | `5.888` | `6.101` (`VERIFIED`) | `−213` | `1.236.480` | `0,01 s` | `0,44 s` | `0,11 MB` | `already_in_t4_nearbush` |
| 5 | `(3, 15, 13)` | `13` | `3.211` | `3.289` (`VERIFIED`) | `−78` | `1.461.005` | `0,01 s` | `0,51 s` | `0,10 MB` | `phase6a_small` |
| 6 | `(5, 9, 7)` | `7` | `24.010` | `25.039` (`VERIFIED`) | `−1.029` | `3.025.260` | `0,01 s` | `1,00 s` | `0,41 MB` | `phase6a_small` |
| 7 | `(4, 11, 9)` | `9` | `9.477` | `9.801` (`VERIFIED`) | `−324` | `3.127.410` | `0,01 s` | `1,03 s` | `0,20 MB` | `already_in_t4_nearbush` |
| 8 | `(5, 10, 8)` | `8` | `47.104` | `49.128` (`VERIFIED`) | `−2.024` | `11.870.208` | `0,03 s` | `3,76 s` | `0,90 MB` | `phase6a_small` |
| 9 | `(3, 21, 18)` | `19` | `9.766` | `9.830` (`VERIFIED`) | `−64` | `12.988.780` | `0,03 s` | `4,11 s` | `0,48 MB` | `phase6a_small` |
| 10 | `(3, 21, 19)` | `19` | `10.108` | `10.279` (`VERIFIED`) | `−171` | `13.443.640` | `0,03 s` | `4,25 s` | `0,50 MB` | `phase6a_small` |
| 11 | `(6, 9, 7)` | `7` | `168.070` | `175.273` (`VERIFIED`) | `−7.203` | `14.117.880` | `0,03 s` | `4,46 s` | `2,89 MB` | `phase6a_small` |
| 12 | `(4, 13, 10)` | `11` | `20.086` | `20.383` (`VERIFIED`) | `−297` | `14.361.490` | `0,03 s` | `4,54 s` | `0,50 MB` | `phase6a_small` |
| 13 | `(4, 13, 11)` | `11` | `21.296` | `21.901` (`VERIFIED`) | `−605` | `15.226.640` | `0,03 s` | `4,81 s` | `0,55 MB` | `already_in_t4_nearbush` |
| 14 | `(5, 11, 9)` | `9` | `85.293` | `88.209` (`VERIFIED`) | `−2.916` | `39.405.366` | `0,08 s` | `12,36 s` | `1,79 MB` | `phase6a_small` |
| 15 | `(4, 15, 12)` | `13` | `39.715` | `40.476` (`VERIFIED`) | `−761` | `54.210.975` | `0,10 s` | `16,99 s` | `1,23 MB` | `phase6a_small` |
| 16 | `(4, 15, 13)` | `13` | `41.743` | `42.757` (`VERIFIED`) | `−1.014` | `56.979.195` | `0,11 s` | `17,86 s` | `1,33 MB` | `already_in_t4_nearbush` |
| 17 | `(6, 10, 8)` | `8` | `376.832` | `393.018` (`VERIFIED`) | `−16.186` | `79.134.720` | `0,15 s` | `24,78 s` | `7,19 MB` | `phase6a_small` |
| 18 | `(5, 13, 10)` | `11` | `220.946` | `224.844` (`VERIFIED`) | `−3.898` | `284.357.502` | `0,52 s` | `88,91 s` | `5,48 MB` | `phase6b_large` |
| 19 | `(5, 13, 11)` | `11` | `234.256` | `240.911` (`VERIFIED`) | `−6.655` | `301.487.472` | `0,55 s` | `94,26 s` | `6,07 MB` | `phase6b_large` |
| 20 | `(6, 11, 9)` | `9` | `767.637` | `793.881` (`VERIFIED`) | `−26.244` | `354.648.294` | `0,65 s` | `110,9 s` | `16,11 MB` | `phase6b_large` |
| 21 | `(4, 19, 17)` | `17` | `122.825` | `125.137` (`VERIFIED`) | `−2.312` | `476.069.700` | `0,87 s` | `148,8 s` | `5,37 MB` | `phase6b_large` |
| 22 | `(4, 21, 18)` | `19` | `185.554` | `188.412` (`VERIFIED`) | `−2.858` | `1.110.540.690` | `2,02 s` | `347,1 s` | `9,08 MB` | `phase6b_large` |
| 23 | `(4, 21, 19)` | `19` | `192.052` | `195.301` (`VERIFIED`) | `−3.249` | `1.149.431.220` | `2,09 s` | `359,2 s` | `9,51 MB` | `phase6b_large` |
| 24 | `(5, 15, 12)` | `13` | `516.295` | `527.205` (`VERIFIED`) | `−10.910` | `1.550.433.885` | `2,82 s` | `484,6 s` | `16,00 MB` | `phase6b_large` |
| 25 | `(5, 15, 13)` | `13` | `542.659` | `555.841` (`VERIFIED`) | `−13.182` | `1.629.604.977` | `2,97 s` | `509,3 s` | `17,32 MB` | `phase6b_large` |
| 26 | `(6, 13, 10)` | `11` | `2.430.406` | `2.483.623` (`VERIFIED`) | `−53.217` | `4.170.576.696` | `7,59 s` | `1303,4 s` | `60,26 MB` | `phase6b_large` |
| 27 | `(6, 13, 11)` | `11` | `2.576.816` | `2.650.021` (`VERIFIED`) | `−73.205` | `4.421.816.256` | `8,04 s` | `1381,9 s` | `66,80 MB` | `phase6b_large` |
| 28 | `(4, 25, 20)` | `23` | `380.351` | `382.933` (`VERIFIED`) | `−2.582` | `4.811.440.150` | `8,75 s` | `1503,6 s` | `22,67 MB` | `phase6b_large` |
| 29 | `(4, 27, 21)` | `25` | `521.875` | `523.044` (`VERIFIED`) | `−1.169` | `9.158.906.250` | `16,66 s` | `2862,2 s` | `33,91 MB` | `phase6b_large` |
| 30 | `(5, 19, 14)` | `17` | `1.866.940` | `1.876.724` (`VERIFIED`) | `−9.784` | `21.708.778.320` | `39,48 s` | `1,88 h` | `77,32 MB` | `phase6b_large` |
| 31 | `(5, 19, 15)` | `17` | `1.935.722` | `1.960.252` (`VERIFIED`) | `−24.530` | `22.508.575.416` | `40,93 s` | `1,95 h` | `81,84 MB` | `phase6b_large` |
| 32 | `(5, 19, 16)` | `17` | `2.009.417` | `2.031.616` (`VERIFIED`) | `−22.199` | `23.365.500.876` | `42,49 s` | `2,03 h` | `86,47 MB` | `phase6b_large` |
| 33 | `(5, 19, 17)` | `17` | `2.088.025` | `2.127.329` (`VERIFIED`) | `−39.304` | `24.279.554.700` | `44,15 s` | `2,11 h` | `91,25 MB` | `phase6b_large` |
| 34 | `(6, 15, 12)` | `13` | `6.711.835` | `8.225.568` (`CITED`) | `−1.513.733` | `33.592.734.175` | `61,08 s` | `2,92 h` | `208,0 MB` | `phase6b_large` |
| 35 | `(6, 15, 13)` | `13` | `7.054.567` | `9.253.764` (`CITED`) | `−2.199.197` | `35.308.107.835` | `64,20 s` | `3,06 h` | `225,1 MB` | `phase6b_large` |
| 36 | `(5, 21, 18)` | `19` | `3.525.526` | `3.580.380` (`VERIFIED`) | `−54.854` | `71.740.928.574` | `130,4 s` | `6,23 h` | `172,6 MB` | `phase6b_large` |
| 37 | `(5, 21, 19)` | `19` | `3.648.988` | `3.710.719` (`VERIFIED`) | `−61.731` | `74.253.256.812` | `135,0 s` | `6,45 h` | `180,8 MB` | `phase6b_large` |
| 38 | `(6, 18, 14)` | `16` | `22.740.992` | `24.137.563` (`VERIFIED`) | `−1.396.571` | `422.163.775.488` | `767,6 s` | `36,65 h` | `892,3 MB` | `phase6b_large` |
| 39 | `(6, 18, 15)` | `16` | `23.658.496` | `24.137.565` (`VERIFIED`) | `−479.069` | `439.196.319.744` | `798,5 s` | `38,12 h` | `947,6 MB` | `phase6b_large` |
| 40 | `(5, 25, 20)` | `23` | `8.748.073` | `9.765.615` (`VERIFIED`) | `−1.017.542` | `464.785.118.490` | `845,1 s` | `40,35 h` | `521,4 MB` | `phase6b_large` |
| 41 | `(5, 25, 21)` | `23` | `8.991.413` | `9.765.617` (`VERIFIED`) | `−774.204` | `477.713.772.690` | `868,6 s` | `41,47 h` | `541,0 MB` | `phase6b_large` |
| 42 | `(5, 25, 22)` | `23` | `9.246.920` | `9.765.619` (`VERIFIED`) | `−518.699` | `491.288.859.600` | `893,3 s` | `42,65 h` | `561,2 MB` | `phase6b_large` |
| 43 | `(5, 25, 23)` | `23` | `9.514.594` | `9.765.621` (`VERIFIED`) | `−251.027` | `505.510.379.220` | `919,1 s` | `43,88 h` | `581,9 MB` | `phase6b_large` |
| 44 | `(6, 19, 14)` | `17` | `31.737.980` | `33.554.412` (`VERIFIED`) | `−1.816.432` | `861.114.873.360` | `1565,7 s` | `74,75 h` | `1,28 GB` | `phase6b_large` |
| 45 | `(6, 19, 15)` | `17` | `32.907.274` | `33.554.414` (`VERIFIED`) | `−647.140` | `892.840.158.168` | `1623,4 s` | `77,50 h` | `1,36 GB` | `phase6b_large` |
| 46 | `(6, 19, 17)` | `17` | `35.496.425` | `46.771.760` (`CITED`) | `−11.275.335` | `963.089.003.100` | `1751,1 s` | `83,60 h` | `1,51 GB` | `phase6b_large` |
| 47 | `(5, 27, 20)` | `25` | `12.734.375` | `12.872.657` (`VERIFIED`) | `−138.282` | `1.028.046.093.750` | `1869,2 s` | `89,24 h` | `819,8 MB` | `phase6b_large` |
| 48 | `(5, 27, 24)` | `25` | `14.078.125` | `14.348.901` (`VERIFIED`) | `−270.776` | `1.136.527.031.250` | `2066,4 s` | `98,66 h` | `936,5 MB` | `phase6b_large` |
| 49 | `(6, 21, 18)` | `19` | `66.984.994` | `84.448.008` (`CITED`) | `−17.463.014` | `3.634.873.714.416` | `1,84 h` | `315,53 h` | `3,20 GB` | `phase6b_large` |
| 50 | `(6, 21, 19)` | `19` | `69.330.772` | `91.485.342` (`CITED`) | `−22.154.570` | `3.762.165.011.808` | `1,90 h` | `326,58 h` | `3,35 GB` | `phase6b_large` |
| 51 | `(6, 25, 20)` | `23` | `201.205.679` | `244.140.615` (`CITED`) | `−42.934.936` | `35.633.525.750.900` | `18,00 h` | `3093,19 h` | `11,71 GB` | `phase6b_large` |
| 52 | `(6, 25, 21)` | `23` | `206.802.499` | `244.140.617` (`CITED`) | `−37.338.118` | `36.624.722.572.900` | `18,50 h` | `3179,23 h` | `12,15 GB` | `phase6b_large` |
| 53 | `(6, 25, 22)` | `23` | `212.679.160` | `244.140.619` (`CITED`) | `−31.461.459` | `37.665.479.236.000` | `19,02 h` | `3269,57 h` | `12,60 GB` | `phase6b_large` |
| 54 | `(6, 25, 23)` | `23` | `218.835.662` | `244.140.621` (`CITED`) | `−25.304.959` | `38.755.795.740.200` | `19,57 h` | `3364,22 h` | `13,07 GB` | `phase6b_large` |
| 55 | `(6, 27, 24)` | `25` | `351.953.125` | `387.420.483` (`CITED`) | `−35.467.358` | `104.181.644.531.250` | `52,62 h` | `9043,55 h` | `22,86 GB` | `phase6b_large` |
| 56 | `(6, 27, 25)` | `25` | `361.328.125` | `387.420.485` (`CITED`) | `−26.092.360` | `106.956.738.281.250` | `54,02 h` | `9284,44 h` | `23,62 GB` | `phase6b_large` |

---

## 3. Gleichstände mit `CITED`-Zellen (`N_pred == N_eff` bei `tier == CITED`, `ca-tools @ e673ab4`)

| # | Zelle `(t, k, v)` | `q` | `N_pred == N_eff` (`tier`) | `C(k, t) * N_pred` | `est_ca_s` | `est_py_s` | Dateigröße (ca.) | Hinweis |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| 1 | `(5, 7, 5)` | `5` | `4.375` (`CITED`) | `91.875` | `0,01 s` | `0,08 s` | `0,06 MB` | reine `CITED`-Schranke ohne verifiziertes Array in `ca_frame.csv` (nicht strikt kleiner, daher nicht in Schritt 4) |
