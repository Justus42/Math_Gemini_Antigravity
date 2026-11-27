"""Generic model: union of cosets of a linear code C (dim t-2, k columns) over GF(q).
A union of cosets r + C is a CA(m q^(t-2); t, k, q) iff for each t-set T of columns the
representatives hit every coset of C|_T in GF(q)^T  (needs rank(C|_T) = t-2).
Variables: one 0/1 per candidate representative. Minimise the number chosen (OR-Tools CP-SAT).
"""
import itertools, sys, time
from gfmod import GF
from ortools.sat.python import cp_model


def rref_reduce(F, rows, T):
    """Return (pivcols, reduced rows restricted to T) for generator rows restricted to T."""
    M = [[r[c] for c in T] for r in rows]
    piv = []
    rk = 0
    for col in range(len(T)):
        p = next((i for i in range(rk, len(M)) if M[i][col]), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        iv = F.inv[M[rk][col]]
        M[rk] = [F.mul[iv][x] for x in M[rk]]
        for i in range(len(M)):
            if i != rk and M[i][col]:
                f = M[i][col]
                M[i] = [F.sub(x, F.mul[f][y]) for x, y in zip(M[i], M[rk])]
        piv.append(col)
        rk += 1
    return piv, M[:rk]


def class_id(F, piv, M, u):
    u = list(u)
    for pc, row in zip(piv, M):
        f = u[pc]
        if f:
            u = [F.sub(x, F.mul[f][y]) for x, y in zip(u, row)]
    return tuple(x for i, x in enumerate(u) if i not in piv)


def kernel(F, t, kind):
    """Generator rows (length q+2). Columns: q evaluation points, then two extra columns.
    Z2: extras (0,0)                [repo kernel K_t]
    Z1: extras ([i==t-3], 0)        [extended RS + one zero column]
    Z0: extras ([i==t-3], [i==t-3 if t==3 else i==t-4])"""
    q = F.q
    rows = []
    for i in range(t - 2):
        ev = [F.pw(x, i) for x in range(q)]
        if kind == "Z2":
            ex = [0, 0]
        elif kind == "Z1":
            ex = [1 if i == t - 3 else 0, 0]
        elif kind == "Z0":
            ex = [1 if i == t - 3 else 0, 1 if i == (t - 3 if t == 3 else t - 4) else 0]
        rows.append(ev + ex)
    return rows


def reps_rs(F, t):
    """Representatives (c x^(t-2) + d x^(t-1) on the q points, a, b)."""
    q = F.q
    out = []
    for c, d, a, b in itertools.product(range(q), repeat=4):
        ev = [F.add[F.mul[c][F.pw(x, t - 2)]][F.mul[d][F.pw(x, t - 1)]] for x in range(q)]
        out.append(((c, d, a, b), ev + [a, b]))
    return out


def build(F, t, kind):
    q = F.q
    k = q + 2
    G = kernel(F, t, kind)
    reps = reps_rs(F, t)
    cons = set()
    lowrank = 0
    for T in itertools.combinations(range(k), t):
        piv, M = rref_reduce(F, G, T)
        if len(piv) < t - 2:
            lowrank += 1
        buckets = {}
        for idx, (_, vec) in enumerate(reps):
            cid = class_id(F, piv, M, [vec[c] for c in T])
            buckets.setdefault(cid, []).append(idx)
        need = q ** (t - len(piv))
        assert len(buckets) == need, (T, len(buckets), need)
        for lst in buckets.values():
            cons.add(tuple(lst))
    return reps, sorted(cons), lowrank


def solve(F, t, kind, limit, hint=None, atmost=None, workers=2, seed=1, log=False):
    reps, cons, lowrank = build(F, t, kind)
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f"x{i}") for i in range(len(reps))]
    for lst in cons:
        m.AddBoolOr([x[i] for i in lst])
    if atmost is not None:
        m.Add(sum(x) <= atmost)
    m.Minimize(sum(x))
    if hint:
        hs = set(hint)
        for i, (lab, _) in enumerate(reps):
            m.AddHint(x[i], 1 if lab in hs else 0)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = limit
    s.parameters.num_workers = workers
    s.parameters.random_seed = seed
    s.parameters.log_search_progress = log
    t0 = time.time()
    st = s.Solve(m)
    sol = [reps[i][0] for i in range(len(reps)) if st in (cp_model.OPTIMAL, cp_model.FEASIBLE) and s.Value(x[i])]
    return dict(status=s.StatusName(st), m=len(sol) if sol else None, bound=s.BestObjectiveBound(),
                secs=round(time.time() - t0, 1), ncons=len(cons), lowrank=lowrank, sol=sol)


if __name__ == "__main__":
    q, t, kind, limit = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], float(sys.argv[4])
    F = GF(q)
    r = solve(F, t, kind, limit)
    sol = r.pop("sol")
    print(q, t, kind, r, flush=True)
    if sol and len(sys.argv) > 5:
        with open(sys.argv[5], "w") as f:
            for lab in sol:
                f.write(" ".join(map(str, lab)) + "\n")
