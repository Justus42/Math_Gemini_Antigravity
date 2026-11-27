#!/usr/bin/env python3
"""Phase 8: alle Zellen (t, q+2, v), t = 3..6, an denen eine Phase-8-Liste kleiner ist als die ca-tools-Tabelle.

Aufruf (aus dem Wurzelverzeichnis):  python3 scripts/phase8/zellen.py PFAD/ca-tools/table/
Liest ca_frame.csv, ca_table.csv.gz, derived.csv (kleinster Wert ueber k' >= k, wie scripts/pruefer/tabelle.py),
dazu die Listen in data/phase8/, data/phase8_repro/, data/phase8_baer/; je (q, v) zaehlt die kleinste Liste.
Ausgabe: Markdown-Tabelle und Zaehlung je Gruppe. std-only, keine Suche.
"""
import collections
import csv
import glob
import gzip
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = sys.argv[1]
best = collections.defaultdict(dict)


def put(t, v, k, n):
    d = best[(t, v)]
    if k not in d or n < d[k]:
        d[k] = n


for r in csv.DictReader(open(T + "ca_frame.csv")):
    put(int(r["t"]), int(r["v"]), int(r["k"]), int(r["N"]))
for r in csv.DictReader(gzip.open(T + "ca_table.csv.gz", "rt")):
    if r["tier"] not in ("DISPUTED", "FAILED_PENDING_RECHECK"):
        put(int(r["t"]), int(r["v"]), int(r["k"]), int(r["N"]))
for r in csv.DictReader(open(T + "derived.csv")):
    put(int(r["t"]), int(r["v"]), int(r["k"]), int(r["N"]))


def neff(t, k, v):
    c = [n for kk, n in best[(t, v)].items() if kk >= k]
    return min(c) if c else None


lists = {}
for grp in ("data/phase8", "data/phase8_repro", "data/phase8_baer"):
    for p in glob.glob(os.path.join(ROOT, grp, "R_*.txt")):
        m = re.search(r"R_q(\d+)(?:_v(\d+))?", os.path.basename(p))
        q = int(m.group(1))
        v = int(m.group(2)) if m.group(2) else q
        n = sum(1 for ln in open(p) if ln.split("#")[0].strip())
        lists.setdefault((q, v), []).append((n, grp, os.path.basename(p)))
stored = {os.path.basename(p) for d in ("results/phase8", "results/phase8_baer")
          for p in glob.glob(os.path.join(ROOT, d, "CA_*.txt"))}
cnt, total = collections.Counter(), 0
print("| Zelle | Tabelle | Phase 8 | Liste | Stand |")
print("| --- | ---: | ---: | --- | --- |")
for (q, v), cand in sorted(lists.items()):
    m, grp, name = min(cand)
    for t in (3, 4, 5, 6):
        tab = neff(t, q + 2, v)
        if tab is None:
            continue
        total += 1
        n = m * q ** (t - 2)
        if n < tab:
            cnt[grp] += 1
            st = "dual-verifiziert, abgelegt" if f"CA_{n}_{t}_{q + 2}_{v}.txt" in stored else "Vorhersage"
            print(f"| `({t}, {q + 2}, {v})` | {tab} | {n} | `{grp}/{name}` | {st} |")
print()
print("kleiner:", dict(cnt), "zusammen", sum(cnt.values()), "von", total, "Zellen mit Tabellenwert")
