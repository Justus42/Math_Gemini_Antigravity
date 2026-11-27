"""M(R) model restricted to an asymmetric skeleton.
heavy line d=0; DB = pure-b lines; DA = pure-a lines (the rest).  h_a = q-|DA| heavy a-symbols, h_b = q-|DB|.
Usage: skeleton2.py q limit DBspec [out] [hintfile]
DBspec: 'ls'  -> DB = {1/(s-n0): s square or 0}, n0 smallest non-square   (|DB| = (q+1)/2, q odd)
        'ls+J' -> the same plus J further lines
        'd1,d2,...' -> explicit list
"""
import sys, time
from gfmod import GF
from ortools.sat.python import cp_model
from skeleton import constraints, check


def db_spec(F, spec):
    q = F.q
    if spec.startswith("ls"):
        nz = range(1, q)
        sq = {F.mul[a][a] for a in nz}
        n0 = min(a for a in nz if a not in sq)
        DB = sorted({F.inv[F.sub(s, n0)] for s in sq | {0}})
        extra = int(spec[3:]) if len(spec) > 2 else 0
        rest = [d for d in nz if d not in DB]
        DB += rest[:extra]
        return sorted(DB)
    return sorted(int(x) for x in spec.split(","))


def allowed(F, DB):
    q = F.q
    DA = [d for d in range(1, q) if d not in DB]
    ha, hb = q - len(DA), q - len(DB)
    symA = {d: ha + i for i, d in enumerate(DA)}
    symB = {d: hb + i for i, d in enumerate(DB)}
    reps, hint = [], []
    for d in range(q):
        for c in range(q):
            if d == 0:
                reps += [(c, d, a, b) for a in range(ha) for b in range(hb)]
                for i in range(max(ha, hb)):
                    hint.append((c, d, i % ha, (i + c) % hb) if ha >= hb else (c, d, (i + c) % ha, i % hb))
            elif d in symA:
                reps += [(c, d, symA[d], b) for b in range(q)]
                hint.append((c, d, symA[d], c))
            else:
                reps += [(c, d, a, symB[d]) for a in range(q)]
                hint.append((c, d, c, symB[d]))
    return reps, hint, (DA, DB, ha, hb)


def solve(q, limit, spec, hintfile=None, workers=2, seed=1):
    F = GF(q)
    DB = db_spec(F, spec)
    reps, hint, info = allowed(F, DB)
    cons, need = constraints(F, reps)
    assert len(cons) == need
    if hintfile:
        hint = [tuple(map(int, l.split())) for l in open(hintfile) if l.strip() and not l.startswith("#")]
    assert check(F, hint) == 0, "hint is not a solution"
    m = cp_model.CpModel()
    x = [m.NewBoolVar("") for _ in reps]
    for lst in cons.values():
        m.AddBoolOr([x[i] for i in lst])
    m.Minimize(sum(x))
    hs = set(hint)
    for i, r in enumerate(reps):
        m.AddHint(x[i], 1 if r in hs else 0)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = limit
    s.parameters.num_workers = workers
    s.parameters.random_seed = seed
    t0 = time.time()
    st = s.Solve(m)
    sol = [reps[i] for i in range(len(reps)) if s.Value(x[i])]
    return dict(q=q, DA=info[0], DB=info[1], ha=info[2], hb=info[3], vars=len(reps), start=len(hint),
                formula=q * q + q * (q - 1) // 2, status=s.StatusName(st), m=len(sol), missing=check(F, sol),
                secs=round(time.time() - t0, 1)), sol


if __name__ == "__main__":
    q, limit, spec = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    res, sol = solve(q, limit, spec, sys.argv[5] if len(sys.argv) > 5 else None)
    print(res, flush=True)
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            for r in sol:
                f.write(" ".join(map(str, r)) + "\n")
