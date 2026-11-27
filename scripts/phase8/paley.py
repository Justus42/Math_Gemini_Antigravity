"""Explicit version. Classes = pairs of lines with slopes +-sigma through one apex O=(0,d0) on a pure-b line.
Feet on the heavy line: +-e.  Claim: the class may be dropped exactly at the points p of the heavy line with
chi(p^2 - e^2) = -1.  So everything depends on the set S of squares s = e^2 that are used.
m = q^2 + q*((q+1)/2 + j) - sum_p min(adel_p, 2+2j) + (n-1),  adel_p = #{s in S : chi(p^2 - s) = -1},  n = |S| <= (q-3)/2 - j.
Usage: paley.py q j [build]"""
import sys, json, time
from apex import base
from ortools.sat.python import cp_model


def chi(x, q):
    x %= q
    return 0 if x == 0 else (1 if pow(x, (q - 1) // 2, q) == 1 else -1)


def cls(q, Delta, d0, e):
    """class with feet +-e: points on the pure-b lines and kept points on the heavy line"""
    sig = (-e * pow(d0, -1, q)) % q
    X = frozenset(((s * (d - d0)) % q, d) for d in Delta for s in (sig, (-sig) % q))
    K = frozenset(p for p in range(q) if chi(p * p - e * e, q) != -1)
    return X, K


def choose(q, j, lim=20):
    """choose the set of squares s=e^2 (one class each): maximise useful deletions minus apex clashes"""
    cap, nmax = 2 + 2 * j, (q - 3) // 2 - j
    es = list(range(1, (q + 1) // 2))                      # one e from each pair +-e
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
    st = s.Solve(mdl)
    E = [e for i, e in enumerate(es) if s.Value(y[i])]
    return s.StatusName(st), E


def count(q, j, E):
    cap = 2 + 2 * j
    adel = [sum(1 for e in E if chi(p * p - e * e, q) == -1) for p in range(q)]
    return q * q + q * ((q + 1) // 2 + j) - sum(min(a, cap) for a in adel) + max(len(E) - 1, 0), adel


def simple(q, j):
    """no search: use all squares except the j+1 smallest e"""
    return list(range(j + 2, (q + 1) // 2))


def run(q, j, do_build=False, lim=20):
    t0 = time.time()
    formula = q * q + q * (q - 1) // 2
    st, E = choose(q, j, lim)
    m_opt, adel = count(q, j, E)
    m_simple, _ = count(q, j, simple(q, j))
    res = dict(q=q, j=j, n=len(E), st=st, formula=formula, m_simple=m_simple, m_opt=m_opt,
               saved=formula - m_opt, saved_q2=round((formula - m_opt) / q / q, 4), ratio=round(m_opt / q / q, 4))
    if do_build:
        from gfmod import GF
        from skeleton import check
        from ls_pack import verify_class
        from ls_pack2 import build
        X0, D0, Delta, d0, cO = base(q)
        chosen = [cls(q, Delta, d0, e) for e in E]
        assert all(verify_class(q, X, K) for X, K in chosen), "class is not blocking"
        rest = [d for d in range(1, q) if d not in Delta]
        DB, DA = sorted(Delta + rest[:j]), rest[j:]
        st2, sol = build(q, DB, DA, chosen, len(DB) + 1, q - len(DB), lim=120, target=m_opt)
        res.update(m_built=len(sol), missing=check(GF(q), sol) if sol else None, heavy=st2)
        if sol:
            with open(f"Y_q{q}_j{j}.txt", "w") as f:
                for r in sol:
                    f.write(" ".join(map(str, r)) + "\n")
    res["secs"] = round(time.time() - t0)
    print(json.dumps(res), flush=True)
    return res


if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]), len(sys.argv) > 3)
