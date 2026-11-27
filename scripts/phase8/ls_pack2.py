"""Redei-type classes with j additional pure-b lines.
Skeleton: heavy line d=0; DB = Delta + j more lines (pure-b), DA = rest (pure-a).
h_a = |DB|+1 heavy a-symbols, h_b = q-|DB| heavy b-symbols; start q^2 + q*|DB| representatives.
Usage: ls_pack2.py q j [packlim] [out]"""
import sys, time, json
from gfmod import GF
from ortools.sat.python import cp_model
from skeleton import constraints, check
from ls_pack import verify_class
from ls_fast import candidates_fast as candidates


def pack(q, DB, cands, ha, hb, lim, seed=1):
    items = list(cands.items())
    mdl = cp_model.CpModel()
    y = [mdl.NewBoolVar("") for _ in items]
    bypt, dbl = {}, {d: [] for d in DB}
    for i, (X, K) in enumerate(items):
        cnt = {}
        for p in X:
            bypt.setdefault(p, []).append(i)
            cnt[p[1]] = cnt.get(p[1], 0) + 1
        for d, c in cnt.items():
            if c > 1:
                dbl[d].append((i, c - 1))
    extra = {}
    for p, lst in bypt.items():
        e = mdl.NewIntVar(0, 6, "")
        mdl.Add(e >= sum(y[i] for i in lst) - 1)
        extra[p] = e
    for d in DB:   # every heavy a-symbol needs a point on every pure-b line; second points of a class need room
        mdl.Add(ha + sum(c * y[i] for i, c in dbl[d]) - sum(e for p, e in extra.items() if p[1] == d) <= q)
    mdl.Add(sum(y) <= ha)
    z = []
    notK = [[i for i, (X, K) in enumerate(items) if p not in K] for p in range(q)]
    for p in range(q):
        zp = mdl.NewIntVar(0, ha - hb, "")
        mdl.Add(zp <= sum(y[i] for i in notK[p]))
        z.append(zp)
    mdl.Maximize(sum(z) - sum(extra.values()))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = lim
    s.parameters.num_workers = 2
    s.parameters.random_seed = seed
    st = s.Solve(mdl)
    chosen = [items[i] for i in range(len(items)) if s.Value(y[i])]
    return s.StatusName(st), int(round(s.ObjectiveValue())), int(round(s.BestObjectiveBound())), chosen


def build(q, DB, DA, chosen, ha, hb, lim=90, target=None):
    F = GF(q)
    n = len(chosen)
    symA = {d: ha + i for i, d in enumerate(DA)}
    symB = {d: hb + i for i, d in enumerate(DB)}
    fixed = []
    for d in DA:
        fixed += [(c, d, symA[d], c) for c in range(q)]
    owner = {}
    for i, (X, K) in enumerate(chosen):
        for p in X:
            owner.setdefault(p, []).append(i)
    for d in DB:
        here = {a for c in range(q) for a in owner.get((c, d), [])}
        rest = [a for a in range(ha) if a not in here]          # heavy a-symbols still missing on this line
        free = [c for c in range(q) if (c, d) not in owner]
        assert len(free) >= len(rest), (d, len(free), len(rest))
        for c, a in zip(free, rest + [rest[0] if rest else 0] * (len(free) - len(rest))):
            owner[(c, d)] = [a]
        fixed += [(c, d, a, symB[d]) for c in range(q) for a in owner[(c, d)]]
    present = {p: list(range(n, ha)) + [i for i, (X, K) in enumerate(chosen) if p in K] for p in range(q)}
    cand = [(p, 0, a, b) for p in range(q) for a in present[p] for b in range(hb)]
    reps = fixed + cand
    cons, need = constraints(F, reps)
    assert len(cons) == need, need - len(cons)
    mdl = cp_model.CpModel()
    x = [mdl.NewBoolVar("") for _ in reps]
    for i in range(len(fixed)):
        mdl.Add(x[i] == 1)
    for lst in cons.values():
        mdl.AddBoolOr([x[i] for i in lst])
    if target is None:
        mdl.Minimize(sum(x))
    else:
        mdl.Add(sum(x) <= target)        # stop at the first list of the predicted size
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = lim
    s.parameters.num_workers = 2
    st = s.Solve(mdl)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return s.StatusName(st), []
    sol = [reps[i] for i in range(len(reps)) if s.Value(x[i])]
    return s.StatusName(st), sol


def run(q, j, lim, out=None, cache={}):
    t0 = time.time()
    if q not in cache:
        cache[q] = candidates(q)
    Delta, cands = cache[q]
    rest = [d for d in range(1, q) if d not in Delta]
    DB = sorted(Delta + rest[:j])
    DA = rest[j:]
    ha, hb = len(DB) + 1, q - len(DB)
    st, gain, bound, chosen = pack(q, DB, cands, ha, hb, lim)
    assert all(verify_class(q, X, K) for X, K in chosen)
    st2, sol = build(q, DB, DA, chosen, ha, hb)
    F = GF(q)
    formula = q * q + q * (q - 1) // 2
    res = dict(q=q, j=j, lines_b=len(DB), ha=ha, hb=hb, cand=len(cands), n=len(chosen), gain=gain, gain_bound=bound,
               pack=st, start=q * q + q * len(DB), formula=formula, predicted=q * q + q * len(DB) - gain,
               m=len(sol), missing=check(F, sol), saved=formula - len(sol),
               saved_over_q2=round((formula - len(sol)) / q / q, 4), secs=round(time.time() - t0))
    print(json.dumps(res), flush=True)
    if out:
        with open(out, "w") as f:
            for r in sol:
                f.write(" ".join(map(str, r)) + "\n")
    return res


if __name__ == "__main__":
    q, j = int(sys.argv[1]), int(sys.argv[2])
    lim = float(sys.argv[3]) if len(sys.argv) > 3 else 120
    run(q, j, lim, sys.argv[4] if len(sys.argv) > 4 else None)
