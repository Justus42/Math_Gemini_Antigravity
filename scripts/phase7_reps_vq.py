#!/usr/bin/env python3
"""Phase 7, reduced alphabets: deterministic representative list without a solver.

Pure Python (std-only). No search, no randomness. Writes a list R of representatives (c, d, a, b)
with |R| = q^2 + C(w, 2), w = max(0, 2v - q), for any 2 <= v <= q. The list satisfies the
mixed-level strength-2 conditions of docs/PHASE7_T2_REDUCTION.md section 11; lift it with
scripts/phase7_lift.py --q Q --v V. For v = q this is the Phase 6A list (q^2 + C(q, 2)).

Lines d = const of the plane of points (c, d); f = q - v, w = max(0, q - 2f), n = v - w:
  d < w            base label (a, b) = (d, d); at the points c < d two representatives
                   (a, b) = (d, c) and (c, d) instead of one          -> C(w, 2) extra rows
  w <= d < w + n   a = w + (d - w) on the whole line, b = c for c < v, else 0
  w + n <= d < w + 2n   b = w + (d - w - n) on the whole line, a = c for c < v, else 0
  d >= w + 2n      (a, b) = (0, 0)   (only for v < q/2)
See docs/PHASE7_T2_REDUCTION.md section 14 for the argument.

Usage: phase7_reps_vq.py Q V OUT
"""
import sys


def reps_vq(q, v):
    assert 2 <= v <= q
    f = q - v
    w = max(0, q - 2 * f)
    n = v - w
    reps = []
    for d in range(q):
        for c in range(q):
            cc = c if c < v else 0
            if d < w:
                if c < d:
                    reps += [(c, d, d, c), (c, d, c, d)]
                else:
                    reps.append((c, d, d, d))
            elif d < w + n:
                reps.append((c, d, w + (d - w), cc))
            elif d < w + 2 * n:
                reps.append((c, d, cc, w + (d - w - n)))
            else:
                reps.append((c, d, 0, 0))
    assert len(reps) == q * q + w * (w - 1) // 2
    return sorted(reps)


def main():
    q, v, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    reps = reps_vq(q, v)
    with open(out, "w") as fh:
        fh.write("".join("%d %d %d %d\n" % r for r in reps))
    print(f"q={q} v={v} w={max(0, 2 * v - q)} m={len(reps)} -> {out}")


if __name__ == "__main__":
    main()
