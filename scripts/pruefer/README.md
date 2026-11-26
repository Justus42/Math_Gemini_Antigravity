# Hilfsprogramme des Prüfers (Claude, 2026-11-26)

Unabhängig von `verifiers/` und von `scripts/phase7_lift.py` geschrieben, damit sie nach einem Chatwechsel nicht neu gebaut werden müssen.

- `zaehler.c`: zählt fehlende `t`-Tupel. `gcc -O2 -o zaehler zaehler.c`, dann `./zaehler DATEI t v [N k]` (Exit 0 = gedeckt, 1 = Lücken, 2 = Format).
- `nachbau.py`: Lift einer Vertreterliste mit eigener Körperarithmetik und Horner-Schema. `python3 nachbau.py q t LISTE AUSGABE [v]`. Ergebnis soll byte-gleich zu `scripts/phase7_lift.py` sein.
- `tabelle.py`: Tabellenwert `min` über `k' >= k` aus `ca_frame.csv`, `ca_table.csv.gz`, `derived.csv`. `python3 tabelle.py PFAD/ca-tools/table/ N,t,k,v ...`.

Kein Ersatz für die Dual-Verifikation nach `RULES.md` §3.
