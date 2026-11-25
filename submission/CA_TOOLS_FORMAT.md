# `chrispbsmolen/ca-tools` Einreichungsformat & Regeln (`submission/CA_TOOLS_FORMAT.md`)

Stand: **2026-11-25** | Lesend ermittelt via `gh api` aus `chrispbsmolen/ca-tools` @ `main` Commit **`7b08aef06cbedaf1b376dbfa68f6aa171a54df4a`** (`2026-11-25T03:31:22Z`).
Offene Pull Requests in `ca-tools` zum Prüfzeitpunkt: **0** (`[]`). Zuletzt gemergte PRs: `#87` (`laverdi-2026-11`), `#84` (`baig-ai-2026-11`), `#83`, `#82`, `#81`.

---

## 1. Verzeichnis- & PR-Struktur (Regel 7)

- Jede Einreichung ist **genau ein neues Verzeichnis** `submissions/<slug>/` (`[A-Za-z0-9._-]+`, z. B. `<name>-pgl-ccl-2026-11`).
- **Strikt keine Änderungen außerhalb von `submissions/<slug>/`** (keine Code-, Test-, Workflow- oder Dokumentationsänderungen; PRs mit Änderungen außerhalb von `submissions/` werden ungemerged geschlossen).
- Inhalt von `submissions/<slug>/`:
  1. `claims.csv` (exakt 10 Spalten, 1 Zeile pro Array-Datei)
  2. `HOW.md` (3 Pflichtabschnitte + KI-Angabe)
  3. Alle in `claims.csv` referenzierten Array-Dateien `CA_<N>_<t>_<k>_<v>.txt`
- Größenlimits (`tools/check_submission.py`): max. **50 MiB pro Array-Datei**, max. **200 MiB pro Submission** (unsere 13 Pareto-Dateien: max. `1,65 MiB`/Datei, gesamt `8,8 MiB`).

## 2. Stair-Step- / Pareto-Front-Semantik

Aus `submissions/README.md` (*"What a claim means"*):
> *"If you have one array that serves a whole range of k, submit it once at its largest k; it then also improves every smaller k for which it beats the table."*

- **Nur die strenge Pareto-Front einreichen** (maximales `k` pro erreichtem `N` je `(t, v)`). Dominierte kleinere `k` werden automatisch mit verbessert und müssen **nicht** als separate Projektionsdateien eingereicht werden (für unsere 23 verbesserten Zellen genügen daher exakt **13 Array-Dateien**).

## 3. Schema von `claims.csv`

Exakter Header (10 Spalten, keine Zeilenumbrüche innerhalb von Feldern, Felder mit Kommas in `"` einschließen):

```text
t,v,k,N,file,source_detail,construction,builds_on,credit,notes
```

- `t, v, k, N`: ganze Zahlen (`t in 2..6`, `v <= 25`, `k <= 100000`).
- `file`: Dateiname im selben Verzeichnis (z. B. `CA_2070_3_15_10.txt`).
- `source_detail`: Reproduzierbarkeitsquelle (Repo-URL + Commit, DOI oder exakter Erzeugungsbefehl).
- `construction`: benannte Konstruktion/Suchmethode (`unknown` wird seit `2026-11-04` abgelehnt).
- `builds_on`: Semikolon-getrennte IDs aus `table/references.csv` (z. B. `sa-ccl2008`, `ck-ck2002`, `ck-cck1999`, `group-ms2005`, `tabu-n2004`) und/oder eigene Methode als `new https://...` (bzw. `new doi:...` / `new arXiv:...`). Unbekannte IDs oder leeres Feld führen zum Abbruch.
- `credit`: reale Person(en) (Regel 5).
- `notes`: Freitext (darf leer sein; Vorwert muss nicht wiederholt werden).

## 4. Pflichtformat von `HOW.md` & KI-Offenlegung (`ai_tools`)

Geprüft durch `tools/provenance.py` (Regel 1) sowie angekündigt in `CHANGES.md` (ab `2026-11-24` erbeten, neue Tabellenspalte `ai_tools` in `table/ca_table.csv` ab frühestens `2026-12-25`):

1. Drei nicht-leere Pflichtabschnitte mit Label:
   - `Construction:` Name der Konstruktion / Suchmethode
   - `Built from:` Basis-Arrays / Zutaten (`nothing` bei Konstruktion von Grund auf; **keine** Torres-Jimenez-Arrays erlaubt, Regel 6)
   - `Program:` Link zum Code bzw. exakte Befehle/Seeds zur Reproduktion
2. **KI-Offenlegungszeile** (exakte Formulierung laut `submissions/README.md` und `CHANGES.md`):
   ```text
   AI tools used: yes
   ```
   *(Die Tabellenspalte `ai_tools` speichert nur `yes` oder leer; konkrete Tool-Namen sind in `table/ca_table.csv` nicht vorgesehen, können aber im PR-Text / `HOW.md` transparent benannt werden.)*

## 5. Kanonisches Array-Format, Lizenz & Realnamen-Regel

- **Array-Format:** Klartext, genau `N` nicht-leere Zeilen × `k` Einträge (`0..v-1` Einzel-Leerzeichen-getrennt, kein Header, keine Kommentare, LF-Zeilenende). Duplikate anhand SHA-256 des kanonischen Textes werden abgelehnt.
- **Lizenz (Regel 4):** Mit Öffnen des PR werden die Arrays unter **CC BY 4.0** freigegeben.
- **Reale Namen (Regel 5):** Jeder PR nennt die verantwortliche(n) reale(n) Person(en) mit E-Mail-Adresse und Affiliation (`Independent researcher` zulässig; optional ORCID) im PR-Text oder per E-Mail an `chrispbsmolen@gmail.com`. KI-Systeme dürfen nur **neben**, niemals **statt** einer Person genannt werden.
- **Keine Torres-Jimenez-Arrays (Regel 6):** Keine Arrays aus `TJ2level_CAs`, `CAEX_CAs`, `TJcat` oder `web-tj` als Basis/Zutat (unsere Konstruktion ist 100 % from scratch, `Built from: nothing`).

## 6. Live-Prüfung aller 23 Zellen gegen `ca-tools` @ `7b08aef`

Stand `2026-11-25` (`7b08aef`, 0 offene PRs): **Alle 23/23 Zellen sind weiterhin frei** und werden durch unsere 13 Pareto-Arrays strikt unterboten (`Delta` zwischen `−44` und `−607`). Lokale Vorabprüfung im `ca-tools`-Klon vor PR-Eröffnung:

```bash
cc -O3 -pthread -o ca_verify ca_verify.c
python3 tools/check_submission.py submissions/<slug>
```
