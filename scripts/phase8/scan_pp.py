"""Rule count |R| = q(v+x_b) - G + (n-1) for odd prime powers, all v, j, n; S = n largest pair representatives
(as scripts/phase8_spec_repro.py) and, for comparison, S chosen by CP-SAT.  Usage: scan_pp.py q [vmax]"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfmod import GF
from math import comb
from ortools.sat.python import cp_model
q = int(sys.argv[1]); vmax = min(q, int(sys.argv[2])) if len(sys.argv) > 2 else q
F = GF(q)
sq = {F.mul[x][x] for x in range(q)}          # squares incl. 0
neg = F.neg
pairs = sorted({min(e, neg[e]) for e in range(1, q)})
nonsq = {(p, e): F.sub(F.mul[p][p], F.mul[e][e]) not in sq for p in range(q) for e in pairs}
def G_of(S, cap):
    return sum(min(sum(nonsq[p, e] for e in S), cap) for p in range(q))
def best_S(n, cap, lim=5):
    m = cp_model.CpModel(); y = {e: m.NewBoolVar("") for e in pairs}; m.Add(sum(y.values()) == n); z = []
    for p in range(q):
        zp = m.NewIntVar(0, cap, ""); m.Add(zp <= sum(y[e] for e in pairs if nonsq[p, e])); z.append(zp)
    m.Maximize(sum(z)); s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = lim; s.parameters.num_workers = 2
    s.Solve(m); return int(s.ObjectiveValue())
for v in range((q + 3) // 2, vmax + 1):
    p7 = q * q + comb(max(0, 2 * v - q), 2); best = None; bestopt = None
    for j in range(0, (q - 3) // 2 + 1):
        xb = (q + 1) // 2 + j; xa = q - 1 - xb; ha, hb = v - xa, v - xb
        if hb < 1 or xa < 0: continue
        cap = ha - hb
        for n in range(1, min(q - ha, ha, (q - 1) // 2) + 1):
            R = q * (v + xb) - G_of(pairs[-n:], cap) + n - 1
            if best is None or R < best[0]: best = (R, j, n)
            if n in (min(q - ha, ha, (q - 1) // 2), min(q - ha, ha, (q - 1) // 2) - 1):
                Ro = q * (v + xb) - best_S(n, cap) + n - 1
                if bestopt is None or Ro < bestopt[0]: bestopt = (Ro, j, n)
    print(q, v, "Phase7", p7, "Regel", best, "Regel mit gewaehltem S", bestopt, "KLEINER" if min(best[0], bestopt[0]) < p7 else "-")
