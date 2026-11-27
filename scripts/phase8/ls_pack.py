"""Enumerate all Redei/LS-type classes on a fixed set DB of pure-b lines and pack them (CP-SAT).
A candidate = (X, K): X = q points on the DB lines, K = (q+1)/2 points of the heavy line that must be kept.
Usage: ls_pack.py q [lim] [out]"""
import itertools, sys
from gfmod import GF
from ortools.sat.python import cp_model
from skeleton import constraints, check


def candidates(q):
    chi = lambda x: 0 if x == 0 else (1 if pow(x, (q - 1) // 2, q) == 1 else q - 1)
    U = [(x, x * chi(x) % q) for x in range(q)]
    D = {(y1 - y2) * pow(x1 - x2, -1, q) % q for (x1, y1), (x2, y2) in itertools.combinations(U, 2)}
    out = {}
    target = None
    for m in sorted(D - {1, q - 1}):
        BU = {(y - m * x) % q for x, y in U}
        for binf in range(q):
            if binf in BU:
                continue
            for nu in range(1, q):
                X0 = []
                for x, y in U:
                    w = pow((y - m * x - binf) % q, -1, q)
                    X0.append((x * w % q, nu * w % q))
                DB = frozenset(d for c, d in X0)
                if target is None:
                    target = DB
                if DB != target:
                    continue
                D0 = [pow((mu - m) % q, -1, q) for mu in D - {m}]
                for k in range(1, q):
                    for r in range(q):
                        for t in range(q):
                            X = frozenset(((k * c + r * d + t) % q, d) for c, d in X0)
                            K = frozenset((k * c + t) % q for c in D0)
                            out[X] = K
    return sorted(target), out


def verify_class(q, X, K):
    A = set(X) | {(c, 0) for c in K}
    return all(any((c + al * d) % q == u for c, d in A) for al in range(q) for u in range(q))


def pack(q, DB, cands, n_max, lim):
    DA = [d for d in range(1, q) if d not in DB]
    ha, hb = q - len(DA), q - len(DB)
    items = list(cands.items())
    mdl = cp_model.CpModel()
    y = [mdl.NewBoolVar("") for _ in items]
    bypt = {}
    for i, (X, K) in enumerate(items):
        for p in X:
            bypt.setdefault(p, []).append(i)
    extra = {}
    for p, lst in bypt.items():
        e = mdl.NewIntVar(0, len(lst), "")
        mdl.Add(e >= sum(y[i] for i in lst) - 1)
        extra[p] = e
    n = sum(y)
    mdl.Add(n <= n_max)
    for d in DB:   # room for the other heavy a-symbols on every pure-b line
        mdl.Add(sum(y[i] * sum(1 for p in X if p[1] == d) for i, (X, K) in enumerate(items))
                - sum(e for p, e in extra.items() if p[1] == d) + ha - n <= q)
    z = []
    for p in range(q):
        zp = mdl.NewIntVar(0, ha - hb, "")
        mdl.Add(zp <= sum(y[i] for i, (X, K) in enumerate(items) if p not in K))
        z.append(zp)
    mdl.Maximize(sum(z) - sum(extra.values()))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = lim
    s.parameters.num_workers = 2
    st = s.Solve(mdl)
    chosen = [items[i] for i in range(len(items)) if s.Value(y[i])]
    return s.StatusName(st), int(s.ObjectiveValue()), chosen, (DA, ha, hb)


def build(q, DB, chosen, DA, ha, hb):
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
        free = [c for c in range(q) if (c, d) not in owner]
        rest = list(range(n, ha))
        assert len(free) >= len(rest)
        for c, a in zip(free, rest + [n] * (len(free) - len(rest))):
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
    mdl.Minimize(sum(x))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = 60
    s.parameters.num_workers = 2
    st = s.Solve(mdl)
    sol = [reps[i] for i in range(len(reps)) if s.Value(x[i])]
    return s.StatusName(st), sol


if __name__ == "__main__":
    q = int(sys.argv[1])
    lim = float(sys.argv[2]) if len(sys.argv) > 2 else 60
    DB, cands = candidates(q)
    some = list(cands.items())[:: max(1, len(cands) // 50)]
    assert all(verify_class(q, X, K) for X, K in some)
    DA = [d for d in range(1, q) if d not in DB]
    st, gain, chosen, (DA, ha, hb) = pack(q, DB, cands, len(DA), lim)
    assert all(verify_class(q, X, K) for X, K in chosen)
    st2, sol = build(q, DB, chosen, DA, ha, hb)
    F = GF(q)
    print(dict(q=q, DB=DB, DA=DA, ha=ha, hb=hb, candidates=len(cands), pack_status=st, n=len(chosen), gain=gain,
               formula=q * q + q * (q - 1) // 2, predicted=q * (q - 1) + q * ha - gain, heavy_status=st2,
               m=len(sol), missing=check(F, sol)), flush=True)
    if len(sys.argv) > 3:
        with open(sys.argv[3], "w") as f:
            for r in sol:
                f.write(" ".join(map(str, r)) + "\n")
