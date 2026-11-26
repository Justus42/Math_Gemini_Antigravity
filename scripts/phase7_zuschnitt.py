#!/usr/bin/env python3
"""Phase 7: package cut. Lists every cell (t, q+2, v) where the best own size is below the table.

Pure Python (std-only), deterministic, read-only. Best own size per cell:
  v < q            : closed list, q^2 + C(max(0, 2v - q), 2) cosets   (scripts/phase7_reps_vq.py)
  v = q, q in SOLV : solver list from data/phase7/                    (scripts/phase7_lift.py)
  v = q otherwise  : Phase 6A, q^2 + C(q, 2) cosets                   (scripts/gen_general_tqv.py)
File size is an ESTIMATE (uniform symbols): N * (k + k * mean digits per symbol) bytes.

Usage: phase7_zuschnitt.py PATH/TO/ca-tools/table REPO_ROOT
"""
import os
import sys
from math import comb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scan_phase7_vq as scan  # noqa: E402

SOLV = {5: 34, 7: 68, 8: 91, 9: 116, 11: 175}
COUNTED = {  # counted by the checker (docs/PHASE7_T2_REDUCTION.md sections 10 and 14.4), not in results/
    (3, 13, 10), (4, 13, 10), (5, 13, 10), (6, 13, 10), (3, 15, 12), (4, 15, 12), (5, 15, 12),
    (4, 18, 14), (4, 19, 14), (4, 19, 15), (4, 19, 16), (3, 21, 17), (3, 21, 18), (4, 21, 18),
    (4, 25, 20), (4, 25, 21), (4, 27, 20), (3, 27, 21), (4, 27, 21), (4, 27, 22), (4, 27, 23),
    (3, 13, 11), (4, 13, 11), (5, 13, 11), (6, 13, 11)}
MIB = 1024 * 1024


def size_bytes(n, k, v):
    digits = (min(v, 10) + 2 * max(0, v - 10)) / v
    return n * (k + k * digits)


def main():
    best = scan.load(sys.argv[1])
    root = sys.argv[2]
    have = {}
    for sub in ("results/phase7", "results/general_tqv", "results/t4_nearbush"):
        for f in os.listdir(os.path.join(root, sub)):
            if f.startswith("CA_") and f.endswith(".txt"):
                n, t, k, v = (int(z) for z in f[3:-4].split("_"))
                have.setdefault((t, k, v), []).append((n, sub))
    rows = []
    for t in range(2, 7):
        for v in range(2, 26):
            for q in [q for q in range(2, 60) if scan.is_prime_power(q)]:
                if q < v or q + 2 < t:
                    continue
                e = scan.n_eff(best, t, q + 2, v)
                if e is None:
                    continue
                if v < q:
                    m, src = q * q + comb(max(0, 2 * v - q), 2), "Bauart §14"
                elif q in SOLV:
                    m, src = SOLV[q], "Löserliste"
                else:
                    m, src = q * q + comb(q, 2), "Phase 6A"
                n = m * q ** (t - 2)
                if n >= e[0]:
                    continue
                k = q + 2
                mib = size_bytes(n, k, v) / MIB
                h = sorted(have.get((t, k, v), []))
                if any(hn == n for hn, _ in h):
                    status = "in `" + [s for hn, s in h if hn == n][0] + "/`"
                elif (t, k, v) in COUNTED:
                    status = "gezählt (Prüfer), nicht in `results/`"
                else:
                    status = "nur Vorhersage"
                old = ", ".join(f"`{hn}`" for hn, _ in h if hn != n)
                rows.append((mib, t, k, v, q, src, m, n, e[0], status, old))
    # dominance among own arrays: same t, v; more columns and not more rows
    dom = set()
    for a in rows:
        for b in rows:
            if a is not b and a[1] == b[1] and a[3] == b[3] and b[2] > a[2] and b[7] <= a[7]:
                dom.add((a[1], a[2], a[3]))
    small = [r for r in rows if r[0] <= 50]
    print(f"Zellen unter der Tabelle: {len(rows)}; geschätzt <= 50 MiB: {len(small)} "
          f"(zusammen {sum(r[0] for r in small):.0f} MiB); > 50 MiB: {len(rows) - len(small)}; "
          f"von eigener Datei dominiert: {len(dom)}")
    for label, part in (("Geschätzt <= 50 MiB (Datei im Pull Request möglich)", small),
                        ("Geschätzt > 50 MiB (nur über externe Ablage)", [r for r in rows if r[0] > 50])):
        print(f"\n## {label}\n")
        print("| Zelle `(t, k, v)` | `q` | Herkunft | Blöcke | `N` | Tabelle | Differenz | Größe (MiB, geschätzt) | Stand | überholte eigene Dateien |")
        print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for mib, t, k, v, q, src, m, n, tab, status, old in sorted(part):
            print(f"| `({t}, {k}, {v})` | `{q}` | {src} | `{m}` | `{n}` | `{tab}` | `{n - tab}` | `{mib:.1f}` | {status} | {old} |")


if __name__ == "__main__":
    main()
