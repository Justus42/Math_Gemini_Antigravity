# Phase 7: Zuschnitt für Nachbau und Einreichung (`docs/PHASE7_ZUSCHNITT.md`)

- Stand: 2026-11-26, ca. 17:20 MEZ. Autor: Claude (Prüfer-Chat). Vergleichsstand: `chrispbsmolen/ca-tools @ e673ab4`.
- Erzeugt mit `python3 scripts/phase7_zuschnitt.py <ca-tools>/table .` (deterministisch, nur lesend).
- Je Zelle `(t, q+2, v)` die kleinste eigene Größe: `v < q` aus der Bauart §14, `v = q` aus der Löserliste (`q = 5, 7, 8, 9, 11`) oder aus Phase 6A (`q >= 13`).
- **Größen sind Schätzungen** (gleichverteilte Symbole). Die echte Datei ist bei `v < q` eher etwas kleiner. Grenzfälle: `(4, 29, 24)` mit `48,9` und `(5, 18, 14)` mit `51,8 MiB`; dort entscheidet erst die erzeugte Datei.
- Grenzen von `ca-tools` (`docs/GENERAL_TQV_SCAN.md`, „Einreichungsform“): Einzeldatei `<= 50 MiB`, **Summe je Einreichung `<= 200 MiB`**.
- Stand der Prüfung: „in `results/...`“ = dort abgelegt und dual verifiziert; „gezählt (Prüfer)“ = vom Prüfer erzeugt und gezählt, nicht fremdgeprüft; „nur Vorhersage“ = Zahl aus der Formel, kein Array erzeugt.
- Keine Entscheidung enthalten. Kein Neuheitsanspruch (`docs/LITERATURE_CHECK_PHASE7_VQ.md`).

## Überblick

- `77` Zellen kleiner als die Tabelle: `76` aus dem Scan (`docs/PHASE7_VQ_SCAN.md`) und `(5, 7, 5)` aus der Löserliste.
- Geschätzt `<= 50 MiB`: `41` Zellen, zusammen etwa `340 MiB`. Davon `14` in `results/`, `23` vom Prüfer gezählt, `4` nur Vorhersage (`(4, 19, 17)`, `(4, 21, 19)`, `(5, 15, 13)`, `(4, 29, 24)`).
- **Die Summengrenze greift:** Nach Größe sortiert passen die ersten `37` Dateien in `200 MiB` (etwa `193 MiB`). Die vier größten (`(4, 27, 21)`, `(4, 27, 22)`, `(4, 27, 23)`, `(4, 29, 24)`, zusammen etwa `147 MiB`) passen nicht mehr in dieselbe Einreichung.
- Geschätzt `> 50 MiB`: `36` Zellen (bis etwa `24 GiB`), davon `2` vom Prüfer gezählt (`(6, 13, 10)`, `(6, 13, 11)`), `34` nur Vorhersage.
- Keine eigene Datei wird von einer anderen dominiert (Regel 3: gleiches `t`, `v`, mehr Spalten, nicht mehr Zeilen).
- Für den Nachbau offen (geschätzt `<= 50 MiB`, nicht in `results/`): `27` Arrays.
- Überholte eigene Dateien in `results/` stehen in der letzten Spalte; sie bleiben liegen (geschützter Pfad), werden aber nicht eingereicht.


## Geschätzt <= 50 MiB (Datei im Pull Request möglich)

| Zelle `(t, k, v)` | `q` | Herkunft | Blöcke | `N` | Tabelle | Differenz | Größe (MiB, geschätzt) | Stand | überholte eigene Dateien |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `(3, 11, 9)` | `9` | Löserliste | `116` | `1044` | `1089` | `-45` | `0.0` | in `results/phase7/` | `1053` |
| `(3, 13, 10)` | `11` | Bauart §14 | `157` | `1727` | `1760` | `-33` | `0.0` | gezählt (Prüfer), nicht in `results/` |  |
| `(3, 13, 11)` | `11` | Löserliste | `175` | `1925` | `1991` | `-66` | `0.0` | gezählt (Prüfer), nicht in `results/` | `1936` |
| `(5, 7, 5)` | `5` | Löserliste | `34` | `4250` | `4375` | `-125` | `0.1` | in `results/phase7/` |  |
| `(4, 9, 7)` | `7` | Löserliste | `68` | `3332` | `3556` | `-224` | `0.1` | in `results/phase7/` | `3430`, `3479` |
| `(3, 15, 12)` | `13` | Bauart §14 | `224` | `2912` | `2955` | `-43` | `0.1` | gezählt (Prüfer), nicht in `results/` |  |
| `(3, 15, 13)` | `13` | Phase 6A | `247` | `3211` | `3289` | `-78` | `0.1` | in `results/general_tqv/` |  |
| `(4, 10, 8)` | `8` | Löserliste | `91` | `5824` | `6101` | `-277` | `0.1` | in `results/phase7/` | `5888` |
| `(4, 11, 9)` | `9` | Löserliste | `116` | `9396` | `9801` | `-405` | `0.2` | in `results/phase7/` | `9477`, `9558`, `9639` |
| `(5, 9, 7)` | `7` | Löserliste | `68` | `23324` | `25039` | `-1715` | `0.4` | in `results/phase7/` | `24010` |
| `(3, 21, 17)` | `19` | Bauart §14 | `466` | `8854` | `9376` | `-522` | `0.4` | gezählt (Prüfer), nicht in `results/` |  |
| `(3, 21, 18)` | `19` | Bauart §14 | `497` | `9443` | `9830` | `-387` | `0.5` | gezählt (Prüfer), nicht in `results/` | `9766` |
| `(4, 13, 10)` | `11` | Bauart §14 | `157` | `18997` | `20383` | `-1386` | `0.5` | gezählt (Prüfer), nicht in `results/` | `20086` |
| `(3, 21, 19)` | `19` | Phase 6A | `532` | `10108` | `10279` | `-171` | `0.5` | in `results/general_tqv/` |  |
| `(4, 13, 11)` | `11` | Löserliste | `175` | `21175` | `21901` | `-726` | `0.5` | gezählt (Prüfer), nicht in `results/` | `21296`, `21900` |
| `(5, 10, 8)` | `8` | Löserliste | `91` | `46592` | `49128` | `-2536` | `0.9` | in `results/phase7/` | `47104` |
| `(4, 15, 12)` | `13` | Bauart §14 | `224` | `37856` | `40476` | `-2620` | `1.2` | gezählt (Prüfer), nicht in `results/` | `39715` |
| `(3, 27, 21)` | `25` | Bauart §14 | `761` | `19025` | `19052` | `-27` | `1.2` | gezählt (Prüfer), nicht in `results/` |  |
| `(4, 15, 13)` | `13` | Phase 6A | `247` | `41743` | `42757` | `-1014` | `1.3` | in `results/t4_nearbush/` | `42722` |
| `(5, 11, 9)` | `9` | Löserliste | `116` | `84564` | `88209` | `-3645` | `1.8` | in `results/phase7/` | `85293` |
| `(6, 9, 7)` | `7` | Löserliste | `68` | `163268` | `175273` | `-12005` | `2.8` | in `results/phase7/` | `168070` |
| `(4, 18, 14)` | `16` | Bauart §14 | `322` | `82432` | `82993` | `-561` | `3.2` | gezählt (Prüfer), nicht in `results/` |  |
| `(4, 19, 14)` | `17` | Bauart §14 | `344` | `99416` | `106023` | `-6607` | `4.1` | gezählt (Prüfer), nicht in `results/` |  |
| `(4, 19, 15)` | `17` | Bauart §14 | `367` | `106063` | `110273` | `-4210` | `4.5` | gezählt (Prüfer), nicht in `results/` |  |
| `(4, 19, 16)` | `17` | Bauart §14 | `394` | `113866` | `114489` | `-623` | `4.9` | gezählt (Prüfer), nicht in `results/` |  |
| `(5, 13, 10)` | `11` | Bauart §14 | `157` | `208967` | `224844` | `-15877` | `5.2` | gezählt (Prüfer), nicht in `results/` | `220946` |
| `(4, 19, 17)` | `17` | Phase 6A | `425` | `122825` | `125137` | `-2312` | `5.4` | nur Vorhersage |  |
| `(5, 13, 11)` | `11` | Löserliste | `175` | `232925` | `240911` | `-7986` | `6.0` | gezählt (Prüfer), nicht in `results/` | `234256` |
| `(6, 10, 8)` | `8` | Löserliste | `91` | `372736` | `393018` | `-20282` | `7.1` | in `results/phase7/` | `376832` |
| `(4, 21, 18)` | `19` | Bauart §14 | `497` | `179417` | `188412` | `-8995` | `8.8` | gezählt (Prüfer), nicht in `results/` |  |
| `(4, 21, 19)` | `19` | Phase 6A | `532` | `192052` | `195301` | `-3249` | `9.5` | nur Vorhersage |  |
| `(5, 15, 12)` | `13` | Bauart §14 | `224` | `492128` | `527205` | `-35077` | `15.3` | gezählt (Prüfer), nicht in `results/` |  |
| `(6, 11, 9)` | `9` | Löserliste | `116` | `761076` | `793881` | `-32805` | `16.0` | in `results/phase7/` |  |
| `(5, 15, 13)` | `13` | Phase 6A | `247` | `542659` | `555841` | `-13182` | `17.3` | nur Vorhersage |  |
| `(4, 25, 20)` | `23` | Bauart §14 | `665` | `351785` | `382933` | `-31148` | `21.0` | gezählt (Prüfer), nicht in `results/` |  |
| `(4, 25, 21)` | `23` | Bauart §14 | `700` | `370300` | `390612` | `-20312` | `22.3` | gezählt (Prüfer), nicht in `results/` |  |
| `(4, 27, 20)` | `25` | Bauart §14 | `730` | `456250` | `507412` | `-51162` | `29.4` | gezählt (Prüfer), nicht in `results/` |  |
| `(4, 27, 21)` | `25` | Bauart §14 | `761` | `475625` | `523044` | `-47419` | `30.9` | gezählt (Prüfer), nicht in `results/` |  |
| `(4, 27, 22)` | `25` | Bauart §14 | `796` | `497500` | `531431` | `-33931` | `32.6` | gezählt (Prüfer), nicht in `results/` |  |
| `(4, 27, 23)` | `25` | Bauart §14 | `835` | `521875` | `531433` | `-9558` | `34.5` | gezählt (Prüfer), nicht in `results/` |  |
| `(4, 29, 24)` | `27` | Bauart §14 | `939` | `684531` | `707271` | `-22740` | `48.9` | nur Vorhersage |  |

## Geschätzt > 50 MiB (nur über externe Ablage)

| Zelle `(t, k, v)` | `q` | Herkunft | Blöcke | `N` | Tabelle | Differenz | Größe (MiB, geschätzt) | Stand | überholte eigene Dateien |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `(5, 18, 14)` | `16` | Bauart §14 | `322` | `1318912` | `1419851` | `-100939` | `51.8` | nur Vorhersage |  |
| `(6, 13, 10)` | `11` | Bauart §14 | `157` | `2298637` | `2483623` | `-184986` | `57.0` | gezählt (Prüfer), nicht in `results/` |  |
| `(6, 13, 11)` | `11` | Löserliste | `175` | `2562175` | `2650021` | `-87846` | `66.4` | gezählt (Prüfer), nicht in `results/` |  |
| `(5, 19, 14)` | `17` | Bauart §14 | `344` | `1690072` | `1876724` | `-186652` | `70.0` | nur Vorhersage |  |
| `(5, 19, 15)` | `17` | Bauart §14 | `367` | `1803071` | `1960252` | `-157181` | `76.2` | nur Vorhersage |  |
| `(5, 19, 16)` | `17` | Bauart §14 | `394` | `1935722` | `2031616` | `-95894` | `83.3` | nur Vorhersage |  |
| `(5, 19, 17)` | `17` | Phase 6A | `425` | `2088025` | `2127329` | `-39304` | `91.2` | nur Vorhersage |  |
| `(5, 21, 18)` | `19` | Bauart §14 | `497` | `3408923` | `3580380` | `-171457` | `166.9` | nur Vorhersage |  |
| `(5, 21, 19)` | `19` | Phase 6A | `532` | `3648988` | `3710719` | `-61731` | `180.8` | nur Vorhersage |  |
| `(6, 15, 12)` | `13` | Bauart §14 | `224` | `6397664` | `8225568` | `-1827904` | `198.3` | nur Vorhersage |  |
| `(6, 15, 13)` | `13` | Phase 6A | `247` | `7054567` | `9253764` | `-2199197` | `225.1` | nur Vorhersage |  |
| `(5, 25, 20)` | `23` | Bauart §14 | `665` | `8091055` | `9765615` | `-1674560` | `482.3` | nur Vorhersage |  |
| `(5, 25, 21)` | `23` | Bauart §14 | `700` | `8516900` | `9765617` | `-1248717` | `512.5` | nur Vorhersage |  |
| `(5, 25, 22)` | `23` | Bauart §14 | `739` | `8991413` | `9765619` | `-774206` | `545.7` | nur Vorhersage |  |
| `(5, 25, 23)` | `23` | Phase 6A | `782` | `9514594` | `9765621` | `-251027` | `581.9` | nur Vorhersage |  |
| `(5, 27, 20)` | `25` | Bauart §14 | `730` | `11406250` | `12872657` | `-1466407` | `734.3` | nur Vorhersage |  |
| `(5, 27, 21)` | `25` | Bauart §14 | `761` | `11890625` | `12872659` | `-982034` | `772.7` | nur Vorhersage |  |
| `(5, 27, 22)` | `25` | Bauart §14 | `796` | `12437500` | `12872661` | `-435161` | `815.2` | nur Vorhersage |  |
| `(6, 18, 14)` | `16` | Bauart §14 | `322` | `21102592` | `24137563` | `-3034971` | `828.0` | nur Vorhersage |  |
| `(6, 18, 15)` | `16` | Bauart §14 | `347` | `22740992` | `24137565` | `-1396573` | `910.9` | nur Vorhersage |  |
| `(5, 27, 24)` | `25` | Bauart §14 | `878` | `13718750` | `14348901` | `-630151` | `912.6` | nur Vorhersage |  |
| `(6, 19, 14)` | `17` | Bauart §14 | `344` | `28731224` | `33554412` | `-4823188` | `1190.0` | nur Vorhersage |  |
| `(6, 19, 15)` | `17` | Bauart §14 | `367` | `30652207` | `33554414` | `-2902207` | `1296.0` | nur Vorhersage |  |
| `(5, 29, 24)` | `27` | Bauart §14 | `939` | `18482337` | `19531223` | `-1048886` | `1320.5` | nur Vorhersage |  |
| `(5, 29, 25)` | `27` | Bauart §14 | `982` | `19328706` | `19531225` | `-202519` | `1389.9` | nur Vorhersage |  |
| `(6, 19, 16)` | `17` | Bauart §14 | `394` | `32907274` | `33554416` | `-647142` | `1416.1` | nur Vorhersage |  |
| `(6, 19, 17)` | `17` | Phase 6A | `425` | `35496425` | `46771760` | `-11275335` | `1551.2` | nur Vorhersage |  |
| `(6, 21, 18)` | `19` | Bauart §14 | `497` | `64769537` | `84448008` | `-19678471` | `3170.8` | nur Vorhersage |  |
| `(6, 21, 19)` | `19` | Phase 6A | `532` | `69330772` | `91485342` | `-22154570` | `3434.7` | nur Vorhersage |  |
| `(6, 25, 20)` | `23` | Bauart §14 | `665` | `186094265` | `244140615` | `-58046350` | `11092.1` | nur Vorhersage |  |
| `(6, 25, 21)` | `23` | Bauart §14 | `700` | `195888700` | `244140617` | `-48251917` | `11787.1` | nur Vorhersage |  |
| `(6, 25, 22)` | `23` | Bauart §14 | `739` | `206802499` | `244140619` | `-37338120` | `12550.5` | nur Vorhersage |  |
| `(6, 25, 23)` | `23` | Phase 6A | `782` | `218835662` | `244140621` | `-25304959` | `13383.9` | nur Vorhersage |  |
| `(6, 27, 20)` | `25` | Bauart §14 | `730` | `285156250` | `296071749` | `-10915499` | `18356.4` | nur Vorhersage |  |
| `(6, 27, 24)` | `25` | Bauart §14 | `878` | `342968750` | `387420483` | `-44451733` | `22813.9` | nur Vorhersage |  |
| `(6, 27, 25)` | `25` | Phase 6A | `925` | `361328125` | `387420485` | `-26092360` | `24190.2` | nur Vorhersage |  |
