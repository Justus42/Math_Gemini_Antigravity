"""Independent checker: lift a representative list to the full array and count t-tuples.
Usage: count_ca.py q t kind repsfile [v]"""
import itertools, sys
from gfmod import GF
from coset_model import kernel


def lift(F, t, kind, labs):
    q = F.q
    G = kernel(F, t, kind)
    rows = []
    for (c, d, a, b) in labs:
        base = [F.add[F.mul[c][F.pw(x, t - 2)]][F.mul[d][F.pw(x, t - 1)]] for x in range(q)] + [a, b]
        for coef in itertools.product(range(q), repeat=t - 2):
            row = list(base)
            for cf, g in zip(coef, G):
                if cf:
                    row = [F.add[r][F.mul[cf][y]] for r, y in zip(row, g)]
            rows.append(row)
    return rows


def missing(rows, t, v):
    k = len(rows[0])
    miss = 0
    for T in itertools.combinations(range(k), t):
        seen = set(tuple(r[c] for c in T) for r in rows)
        seen = {s for s in seen if all(x < v for x in s)}
        miss += v ** t - len(seen)
    return miss


if __name__ == "__main__":
    q, t, kind, fn = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
    F = GF(q)
    labs = [tuple(map(int, l.split())) for l in open(fn) if l.strip()]
    rows = lift(F, t, kind, labs)
    print("reps", len(labs), "rows", len(rows), "missing", missing(rows, t, q),
          "missing_without_last_rep", missing(lift(F, t, kind, labs[:-1]), t, q))
