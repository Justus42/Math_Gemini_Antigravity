"""M(R) model (strength 2 of the small table, t-independent) restricted to a skeleton:
heavy line d=0 carrying h a-symbols and h b-symbols, pure-a lines DA, pure-b lines DB.
Usage: skeleton.py q limit [split] [out]
split: 'int' (DA = 1..x, DB = x+1..q-1) or 'sq' (DA = nonzero squares, DB = non-squares) or 'full' (no restriction)
"""
import itertools, sys, time
from gfmod import GF
from ortools.sat.python import cp_model


def allowed(F, split):
    q = F.q
    if split == "full":
        return [r for r in itertools.product(range(q), repeat=4)], None
    x = (q - 1) // 2
    h = q - x
    nz = list(range(1, q))
    if split == "int":
        DA, DB = nz[:x], nz[x:2 * x]
    else:
        sq = sorted({F.mul[a][a] for a in nz})
        DA, DB = sq, [a for a in nz if a not in sq]
    rest = [d for d in nz if d not in DA and d not in DB]
    assert not rest, "q even needs another skeleton"
    symA = {d: h + i for i, d in enumerate(DA)}
    symB = {d: h + i for i, d in enumerate(DB)}
    reps, hint = [], []
    for d in range(q):
        for c in range(q):
            if d == 0:
                for a in range(h):
                    for b in range(h):
                        reps.append((c, d, a, b))
                for i in range(h):
                    hint.append((c, d, i, (i + c) % h))
            elif d in symA:
                for b in range(q):
                    reps.append((c, d, symA[d], b))
                hint.append((c, d, symA[d], c))
            else:
                for a in range(q):
                    reps.append((c, d, a, symB[d]))
                hint.append((c, d, c, symB[d]))
    return reps, hint


def constraints(F, reps, v=None):
    q = F.q
    v = v or q
    cons = {}
    for i, (c, d, a, b) in enumerate(reps):
        cons.setdefault(("pt", c, d), []).append(i)
        cons.setdefault(("ab", a, b), []).append(i)
        for al in range(q):
            u = F.add[c][F.mul[al][d]]
            cons.setdefault(("a", al, u, a), []).append(i)
            cons.setdefault(("b", al, u, b), []).append(i)
    need = q * q + v * v + 2 * q * q * v
    return cons, need


def check(F, sol, v=None):
    cons, need = constraints(F, sol, v)
    return need - len(cons)


def solve(q, limit, split="int", hintfile=None, workers=2, seed=1):
    F = GF(q)
    reps, hint = allowed(F, split)
    cons, need = constraints(F, reps)
    assert len(cons) == need, (len(cons), need)
    m = cp_model.CpModel()
    x = [m.NewBoolVar("") for _ in reps]
    for lst in cons.values():
        m.AddBoolOr([x[i] for i in lst])
    m.Minimize(sum(x))
    if hintfile:
        hint = [tuple(map(int, l.split())) for l in open(hintfile) if l.strip()]
    if hint:
        assert check(F, hint) == 0, "hint is not a solution"
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
    return dict(q=q, split=split, vars=len(reps), base=len(hint) if hint else None, status=s.StatusName(st),
                m=len(sol), missing=check(F, sol), secs=round(time.time() - t0, 1)), sol


if __name__ == "__main__":
    q, limit = int(sys.argv[1]), float(sys.argv[2])
    split = sys.argv[3] if len(sys.argv) > 3 else "int"
    res, sol = solve(q, limit, split)
    print(res, flush=True)
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            for r in sol:
                f.write(" ".join(map(str, r)) + "\n")
