#!/usr/bin/env python3
"""Tabellenwert N_eff(t,k,v) = min ueber k'>=k aus ca_frame.csv, ca_table.csv.gz, derived.csv (ca-tools)."""
import csv, gzip, sys, collections
T = (sys.argv.pop(1) if len(sys.argv) > 1 and sys.argv[1].endswith('/') else 'ca-tools/table/')  # Pfad zu ca-tools/table/ als erstes Argument (mit / am Ende)
best = collections.defaultdict(dict)   # (t,v) -> k -> (N, quelle)
def put(t, v, k, N, src):
    d = best[(t, v)]
    if k not in d or N < d[k][0]: d[k] = (N, src)
for r in csv.DictReader(open(T + 'ca_frame.csv')):
    put(int(r['t']), int(r['v']), int(r['k']), int(r['N']), 'frame:' + r['tier'])
for r in csv.DictReader(gzip.open(T + 'ca_table.csv.gz', 'rt')):
    if r['tier'] in ('DISPUTED', 'FAILED_PENDING_RECHECK'): continue
    put(int(r['t']), int(r['v']), int(r['k']), int(r['N']), 'table:' + r['tier'])
for r in csv.DictReader(open(T + 'derived.csv')):
    put(int(r['t']), int(r['v']), int(r['k']), int(r['N']), 'derived:' + r['law'])
def neff(t, k, v):
    c = [(N, kk, s) for kk, (N, s) in best[(t, v)].items() if kk >= k]
    return min(c) if c else None
if __name__ == '__main__':
    for a in sys.argv[1:]:
        N, t, k, v = map(int, a.split(','))
        e = neff(t, k, v)
        print(f"({t},{k},{v}) eigen={N} Tabelle={e[0]} (bei k'={e[1]}, {e[2]}) Differenz={N - e[0]} {'KLEINER' if N < e[0] else 'NICHT kleiner'}")
