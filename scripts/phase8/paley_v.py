"""Same construction for v <= q symbols.  x_b = (q+1)/2 + j pure-b lines, x_a = (q-3)/2 - j pure-a lines,
heavy line with h_a = v - x_a and h_b = v - x_b symbols; up to n <= q - h_a classes (two points per pure-b line each).
m = q^2 - q + q*h_a - sum_p min(adel_p, 2+2j) + (n-1).   Usage: paley_v.py q v [build j]"""
import sys, json
from apex import base
from paley import chi, cls
from ortools.sat.python import cp_model


def choose(q, v, j, lim=8):
    xb = (q + 1) // 2 + j
    xa = q - 1 - xb
    ha, hb = v - xa, v - xb
    if hb < 1 or xa < 0:
        return None
    cap, nmax = ha - hb, min((q - 1) // 2, q - ha)
    es = list(range(1, (q + 1) // 2))
    mdl = cp_model.CpModel()
    y = [mdl.NewBoolVar("") for _ in es]
    mdl.Add(sum(y) <= nmax)
    z = []
    for p in range(q):
        zp = mdl.NewIntVar(0, cap, "")
        mdl.Add(zp <= sum(y[i] for i, e in enumerate(es) if chi(p * p - e * e, q) == -1))
        z.append(zp)
    mdl.Maximize(sum(z) - sum(y))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = lim
    s.parameters.num_workers = 2
    s.Solve(mdl)
    E = [e for i, e in enumerate(es) if s.Value(y[i])]
    G = sum(s.Value(t) for t in z)
    return q * q - q + q * ha - G + max(len(E) - 1, 0), E, (xa, xb, ha, hb)


def build(q, v, j, E, lim=180):
    from gfmod import GF
    from skeleton import constraints, check
    from ls_pack import verify_class
    F = GF(q)
    X0, D0, Delta, d0, cO = base(q)
    rest = [d for d in range(1, q) if d not in Delta]
    DB, DA = sorted(Delta + rest[:j]), rest[j:]
    ha, hb = v - len(DA), v - len(DB)
    chosen = [cls(q, Delta, d0, e) for e in E]
    assert all(verify_class(q, X, K) for X, K in chosen)
    n = len(chosen)
    symA = {d: ha + i for i, d in enumerate(DA)}
    symB = {d: hb + i for i, d in enumerate(DB)}
    fixed = []
    for d in DA:                                   # pure-a line: b takes every symbol (v <= q of them)
        fixed += [(c, d, symA[d], c % v) for c in range(q)]
    owner = {}
    for i, (X, K) in enumerate(chosen):
        for p in X:
            owner.setdefault(p, []).append(i)
    for d in DB:
        here = {a for c in range(q) for a in owner.get((c, d), [])}
        need = [a for a in range(ha) if a not in here]
        free = [c for c in range(q) if (c, d) not in owner]
        assert len(free) >= len(need), (d, len(free), len(need))
        for c, a in zip(free, need + [0] * (len(free) - len(need))):
            owner[(c, d)] = [a]
        fixed += [(c, d, a, symB[d]) for c in range(q) for a in owner[(c, d)]]
    present = {p: list(range(n, ha)) + [i for i, (X, K) in enumerate(chosen) if p in K] for p in range(q)}
    cand = [(p, 0, a, b) for p in range(q) for a in present[p] for b in range(hb)]
    reps = fixed + cand
    cons, need = constraints(F, reps, v)
    assert len(cons) == need, need - len(cons)
    return F, fixed, reps, cons


def solve_build(q, v, j, E, target, lim=180):
    from skeleton import check
    F, fixed, reps, cons = build(q, v, j, E)
    mdl = cp_model.CpModel()
    x = [mdl.NewBoolVar("") for _ in reps]
    for i in range(len(fixed)):
        mdl.Add(x[i] == 1)
    for lst in cons.values():
        mdl.AddBoolOr([x[i] for i in lst])
    mdl.Add(sum(x) <= target)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = lim
    s.parameters.num_workers = 2
    st = s.Solve(mdl)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return s.StatusName(st), None, None
    sol = [reps[i] for i in range(len(reps)) if s.Value(x[i])]
    return s.StatusName(st), sol, check(F, sol, v)


if __name__ == "__main__":
    q, v = int(sys.argv[1]), int(sys.argv[2])
    if len(sys.argv) > 4:
        j = int(sys.argv[4])
        m, E, info = choose(q, v, j)
        st, sol, miss = solve_build(q, v, j, E, m)
        print(json.dumps(dict(q=q, v=v, j=j, n=len(E), predicted=m, status=st, m=len(sol) if sol else None, missing=miss)))
        if sol:
            with open(f"V_q{q}_v{v}.txt", "w") as f:
                for r in sol:
                    f.write(" ".join(map(str, r)) + "\n")
    else:
        w = max(0, 2 * v - q)
        s14 = q * q + w * (w - 1) // 2
        best = None
        for j in range(0, q // 4):
            r = choose(q, v, j, 4)
            if r and (best is None or r[0] < best[0]):
                best = (r[0], j, len(r[1]))
        print(f"q={q} v={v}: repo (Sec.14 / 6A) {s14} | new {best[0] if best else None} (j={best[1]}, n={best[2]}) | diff {best[0]-s14 if best else None}", flush=True)
