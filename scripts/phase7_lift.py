#!/usr/bin/env python3
"""Phase 7: strength-2 reduction for arrays built from cosets of the kernel code K_t.

Pure Python (std-only). No solver, no search, no randomness. Any prime power q; the field is
GeneralGF from scripts/gen_general_tqv.py (same element labels 0..q-1 as the Phase 6A generator).

Setting (see docs/PHASE7_T2_REDUCTION.md):
  A representative is a tuple (c, d, a, b) in GF(q)^4.
  M(R)   : one row per representative, columns (c + al*d for al = 0..q-1), a, b.
  L_t(R) : for every representative and every (a_0, ..., a_{t-3}) in GF(q)^(t-2) the row
             (P(0), ..., P(q-1), a, b),  P(x) = a_0 + ... + a_{t-3} x^(t-3) + c x^(t-2) + d x^(t-1).
  Claim checked here by direct counting: if M(R) is a CA(m; 2, q+2, q), then L_t(R) is a
  CA(m * q^(t-2); t, q+2, q) for 2 <= t <= q + 2.

Usage:
  phase7_lift.py --q 5 --reps data/phase7/R_q5_m34.txt --check-m
  phase7_lift.py --q 5 --reps data/phase7/R_q5_m34.txt --t 5 --out CA_4250_5_7_5.txt
  phase7_lift.py --q 5 --known --check-m          # the m = q^2 + C(q,2) solution of Phase 6A
"""
import argparse
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_general_tqv import GeneralGF  # noqa: E402


def read_reps(path, q):
    reps = []
    with open(path) as fh:
        for line in fh:
            line = line.split("#")[0].strip()
            if not line:
                continue
            c, d, a, b = (int(z) for z in line.split())
            assert all(0 <= z < q for z in (c, d, a, b)), line
            reps.append((c, d, a, b))
    assert len(set(reps)) == len(reps), "duplicate representative"
    return reps


def known_reps(q):
    """Phase 6A solution: (c, d, d, min(c, d)) for all c, d; (c, d, c, d) for c < d."""
    return [(c, d, d, min(c, d)) for c in range(q) for d in range(q)] + \
           [(c, d, c, d) for d in range(q) for c in range(d)]


def m_rows(reps, q, field):
    add, mul = field.add, field.mul
    return [[add[c][mul[al][d]] for al in range(q)] + [a, b] for (c, d, a, b) in reps]


def uncovered_pairs(rows, q):
    k = len(rows[0])
    miss = 0
    for i, j in itertools.combinations(range(k), 2):
        miss += q * q - len({(r[i], r[j]) for r in rows})
    return miss


def lift(reps, q, t, field):
    add, mul = field.add, field.mul
    pw = [[1] * q]
    for _ in range(1, t):
        pw.append([mul[pw[-1][x]][x] for x in range(q)])
    for (c, d, a, b) in reps:
        for low in itertools.product(range(q), repeat=t - 2):
            co = list(low) + [c, d]
            row = []
            for x in range(q):
                s = 0
                for e in range(t):
                    s = add[s][mul[co[e]][pw[e][x]]]
                row.append(s)
            yield row + [a, b]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--reps")
    ap.add_argument("--known", action="store_true")
    ap.add_argument("--check-m", action="store_true")
    ap.add_argument("--t", type=int)
    ap.add_argument("--out")
    args = ap.parse_args()
    q = args.q
    field = GeneralGF(q)
    reps = known_reps(q) if args.known else read_reps(args.reps, q)
    print(f"q={q} m={len(reps)}")
    if args.check_m:
        unc = uncovered_pairs(m_rows(reps, q, field), q)
        print(f"M(R): {len(reps)} rows, {q + 2} columns, uncovered pairs = {unc}")
        if unc:
            sys.exit(1)
    if args.t is not None:
        if not 2 <= args.t <= q + 2:
            sys.exit("need 2 <= t <= q + 2")
        n = 0
        with open(args.out, "w") as fh:
            for row in lift(reps, q, args.t, field):
                fh.write(" ".join(map(str, row)) + "\n")
                n += 1
        print(f"wrote CA candidate N={n} t={args.t} k={q + 2} v={q} -> {args.out} (verify separately)")


if __name__ == "__main__":
    main()
