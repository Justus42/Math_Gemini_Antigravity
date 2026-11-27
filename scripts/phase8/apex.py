"""Common-apex version: all Redei-type classes are pairs of lines through ONE point O on a pure-b line.
Lines through O never meet again, so the only clash is at O itself (n-1 extra representatives).
m = q^2 + q*(|Delta|+j) - sum_p min(adel_p, 2+2j) + (n-1).
Usage: apex.py q j [lim] [out]   (out: build and check the list; only sensible for q <= ~41)"""
import itertools, sys, json, time
from ortools.sat.python import cp_model


def base(q):
    chi = lambda x: 0 if x == 0 else (1 if pow(x, (q - 1) // 2, q) == 1 else q - 1)
    U = [(x, x * chi(x) % q) for x in range(q)]
    D = {(y1 - y2) * pow(x1 - x2, -1, q) % q for (x1, y1), (x2, y2) in itertools.combinations(U, 2)}
    m = min(D - {1, q - 1})
    BU = {(y - m * x) % q for x, y in U}
    binf = min(b for b in range(q) if b not in BU)
    X0 = []
    for x, y in U:
        w = pow((y - m * x - binf) % q, -1, q)
        X0.append((x * w % q, w))
    D0 = [pow((mu - m) % q, -1, q) for mu in D - {m}]
    cnt = {}
    for c, d in X0:
        cnt[d] = cnt.get(d, 0) + 1
    d0 = [d for d, n in cnt.items() if n == 1]
    assert len(d0) == 1
    d0 = d0[0]
    cO = [c for c, d in X0 if d == d0][0]
    return X0, D0, sorted(cnt), d0, cO


def apex_candidates(q):
    X0, D0, Delta, d0, cO = base(q)
    inv = lambda a: pow(a % q, -1, q)
    out = {}
    for k in range(1, q):
        for r in range(q):
            t = (-(k * cO + r * d0)) % q          # apex goes to (0, d0)
            X = frozenset(((k * c + r * d + t) % q, d) for c, d in X0)
            K = frozenset((k * c + t) % q for c in D0)
            slopes = frozenset(c * inv(d - d0) % q for c, d in X if d != d0)
            assert len(slopes) == 2
            out[slopes] = (X, K)
    return Delta, d0, out


def pack(q, j, cands, lim):
    xb = (q + 1) // 2 + j
    xa = q - 1 - xb
    cap = 2 + 2 * j
    items = list(cands.items())
    mdl = cp_model.CpModel()
    y = [mdl.NewBoolVar("") for _ in items]
    by = {}
    for i, (sl, _) in enumerate(items):
        for s in sl:
            by.setdefault(s, []).append(i)
    for lst in by.values():
        mdl.AddAtMostOne([y[i] for i in lst])
    mdl.Add(sum(y) <= xa)
    z = []
    for p in range(q):
        zp = mdl.NewIntVar(0, cap, "")
        mdl.Add(zp <= sum(y[i] for i, (sl, (X, K)) in enumerate(items) if p not in K))
        z.append(zp)
    mdl.Maximize(sum(z) - sum(y))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = lim
    s.parameters.num_workers = 2
    st = s.Solve(mdl)
    chosen = [items[i][1] for i in range(len(items)) if s.Value(y[i])]
    gain = sum(s.Value(v) for v in z)
    return s.StatusName(st), gain, chosen, xa, xb


def run(q, j, lim=20, out=None, cache={}):
    t0 = time.time()
    if q not in cache:
        cache[q] = apex_candidates(q)
    Delta, d0, cands = cache[q]
    st, gain, chosen, xa, xb = pack(q, j, cands, lim)
    n = len(chosen)
    formula = q * q + q * (q - 1) // 2
    pred = q * q + q * xb - gain + max(n - 1, 0)
    res = dict(q=q, j=j, n=n, n_max=xa, gain=gain, gain_cap=min((2 + 2 * j) * q, xa * (q - 1) // 2), pack=st,
               formula=formula, predicted=pred, saved=formula - pred, saved_over_q2=round((formula - pred) / q / q, 4),
               ratio=round(pred / q / q, 4))
    if out:
        from gfmod import GF
        from skeleton import check
        from ls_pack import verify_class
        from ls_pack2 import build
        assert all(verify_class(q, X, K) for X, K in chosen)
        rest = [d for d in range(1, q) if d not in Delta]
        DB, DA = sorted(Delta + rest[:j]), rest[j:]
        st2, sol = build(q, DB, DA, chosen, len(DB) + 1, q - len(DB))
        res.update(m=len(sol), missing=check(GF(q), sol), heavy=st2)
        with open(out, "w") as f:
            for r in sol:
                f.write(" ".join(map(str, r)) + "\n")
    res["secs"] = round(time.time() - t0)
    print(json.dumps(res), flush=True)
    return res


if __name__ == "__main__":
    q, j = int(sys.argv[1]), int(sys.argv[2])
    run(q, j, float(sys.argv[3]) if len(sys.argv) > 3 else 20, sys.argv[4] if len(sys.argv) > 4 else None)
