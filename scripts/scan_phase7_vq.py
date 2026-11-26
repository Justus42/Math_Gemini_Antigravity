#!/usr/bin/env python3
"""Phase 7: table scan for N(t, q, v) = (q^2 + C(max(0, 2v - q), 2)) * q^(t-2) at k = q + 2.

Pure Python (std-only), deterministic, read-only. Compares against the monotone hull
N_eff(t, k, v) = min over k' >= k of ca_frame.csv, ca_table.csv.gz (without DISPUTED and
FAILED_PENDING_RECHECK) and derived.csv of a local ca-tools checkout.

Usage: scan_phase7_vq.py PATH/TO/ca-tools/table  [> docs table as markdown]
"""
import collections
import csv
import gzip
import os
import sys
from math import comb


def load(table_dir):
    best = collections.defaultdict(dict)

    def put(t, v, k, n, src):
        d = best[(t, v)]
        if k not in d or n < d[k][0]:
            d[k] = (n, src)

    with open(os.path.join(table_dir, "ca_frame.csv")) as fh:
        for r in csv.DictReader(fh):
            put(int(r["t"]), int(r["v"]), int(r["k"]), int(r["N"]), r["tier"])
    with gzip.open(os.path.join(table_dir, "ca_table.csv.gz"), "rt") as fh:
        for r in csv.DictReader(fh):
            if r["tier"] in ("DISPUTED", "FAILED_PENDING_RECHECK"):
                continue
            put(int(r["t"]), int(r["v"]), int(r["k"]), int(r["N"]), r["tier"])
    with open(os.path.join(table_dir, "derived.csv")) as fh:
        for r in csv.DictReader(fh):
            put(int(r["t"]), int(r["v"]), int(r["k"]), int(r["N"]), "derived")
    return best


def n_eff(best, t, k, v):
    c = [(n, src) for kk, (n, src) in best[(t, v)].items() if kk >= k]
    return min(c) if c else None


def is_prime_power(n):
    for p in range(2, n + 1):
        if n % p == 0:
            while n % p == 0:
                n //= p
            return n == 1
    return False


def main():
    best = load(sys.argv[1])
    qs = [q for q in range(2, 60) if is_prime_power(q)]
    hits = []
    for t in range(2, 7):
        for v in range(2, 26):
            for q in qs:
                if q < v or q + 2 < t:
                    continue
                e = n_eff(best, t, q + 2, v)
                if e is None:
                    continue
                m6a = q * q + comb(v, 2)
                m = q * q + comb(max(0, 2 * v - q), 2)
                n6a, n = m6a * q ** (t - 2), m * q ** (t - 2)
                if n < e[0]:
                    hits.append((q, v, t, m6a, m, n6a, n, e[0], e[1]))
    hits.sort()
    lt = [h for h in hits if h[1] < h[0]]
    print(f"Treffer gesamt: {len(hits)}; davon v < q: {len(lt)}, v = q: {len(hits) - len(lt)}; "
          f"davon von Phase 6A nicht erreicht: {sum(1 for h in hits if h[5] >= h[7])}")
    print()
    print("| Zelle `(t, k, v)` | `q` | Blöcke 6A | Blöcke neu | `N` Phase 6A | `N` neu | Tabelle (Tier) | Differenz | 6A kleiner als Tabelle? |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for q, v, t, m6a, m, n6a, n, tab, tier in hits:
        print(f"| `({t}, {q + 2}, {v})` | `{q}` | `{m6a}` | `{m}` | `{n6a}` | `{n}` | `{tab}` (`{tier}`) | `{n - tab}` | "
              f"{'ja' if n6a < tab else 'nein'} |")


if __name__ == "__main__":
    main()
