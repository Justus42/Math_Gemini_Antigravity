#!/usr/bin/env python3
"""Phase 7, reduced alphabets (v < q): exact model for the smallest representative set R.

Same construction as scripts/phase7_solve_cpsat.py, but the two extra columns a, b only take the
v symbols 0..v-1 and the evaluation columns are mapped by pi (pi(z) = z for z < v, else 0) after
the lift. See docs/PHASE7_T2_REDUCTION.md section 10 for the argument.

NOT std-only: needs Google OR-Tools. Time-limited runs with two workers are NOT byte-reproducible;
the result is the representative list, which is checked separately (lift + counting).

Variables: one 0/1 variable per (c, d, a, b) with c, d in GF(q) and a, b in {0..v-1}.
Conditions (mixed-level strength 2 on M(R), columns c + al*d over q symbols, a and b over v symbols):
  every point (c, d) is chosen at least once;
  on every line c + al*d = u every symbol of a occurs, and every symbol of b occurs;
  every pair (a, b) occurs.
For v = q this is exactly the model of scripts/phase7_solve_cpsat.py.

Usage:
  phase7_solve_cpsat_vq.py Q V SECONDS fixknown        # positive control: q^2 + C(v,2) (Phase 6A)
  phase7_solve_cpsat_vq.py Q V SECONDS hint            # minimise m, start from the Phase 6A list
  phase7_solve_cpsat_vq.py Q V SECONDS hintfile FILE   # minimise m, start from a list
  phase7_solve_cpsat_vq.py Q V SECONDS atmost M        # decide: solution with <= M rows?
"""
import itertools
import os
import sys
import time

from ortools.sat.python import cp_model

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_general_tqv import GeneralGF  # noqa: E402

q, v = int(sys.argv[1]), int(sys.argv[2])
limit = float(sys.argv[3])
mode = sys.argv[4]
assert 2 <= v <= q
T = [(c, d, a, b) for c in range(q) for d in range(q) for a in range(v) for b in range(v)]
_F = GeneralGF(q)
rows = {t: [_F.add[t[0]][_F.mul[al][t[1]]] for al in range(q)] + [t[2], t[3]] for t in T}
k = q + 2
size = [q] * q + [v, v]
model = cp_model.CpModel()
x = {t: model.NewBoolVar("x%d_%d_%d_%d" % t) for t in T}
cons = set()
for i, j in itertools.combinations(range(k), 2):
    buckets = {}
    for t in T:
        buckets.setdefault((rows[t][i], rows[t][j]), []).append(t)
    assert len(buckets) == size[i] * size[j]
    cons.update(frozenset(ts) for ts in buckets.values())
for ts in cons:
    model.AddBoolOr([x[t] for t in ts])
print(f"q={q} v={v} vars={len(T)} distinct-conditions={len(cons)}", flush=True)
pi = [z if z < v else 0 for z in range(q)]
known = {(c, d, pi[d], pi[min(c, d)]) for c in range(q) for d in range(q)} | \
        {(c, d, c, d) for d in range(v) for c in range(d)}
assert len(known) == q * q + v * (v - 1) // 2
total = sum(x.values())
if mode == "fixknown":
    for t in T:
        model.Add(x[t] == (1 if t in known else 0))
elif mode == "atmost":
    model.Add(total <= int(sys.argv[5]))
    model.Add(x[(0, 0, 0, 0)] == 1)
else:
    model.Minimize(total)
    model.Add(x[(0, 0, 0, 0)] == 1)
    start = known
    if mode == "hintfile":
        with open(sys.argv[5]) as fh:
            start = {tuple(int(z) for z in ln.split("#")[0].split()) for ln in fh if ln.split("#")[0].strip()}
    for t in T:
        model.AddHint(x[t], 1 if t in start else 0)
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = limit
solver.parameters.num_search_workers = 2
solver.parameters.random_seed = 1
t0 = time.time()
status = solver.Solve(model)
print(f"status={solver.StatusName(status)} time={time.time() - t0:.1f}s", end=" ")
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    R = sorted(t for t in T if solver.Value(x[t]))
    out = f"R_q{q}_v{v}_m{len(R)}.txt"
    with open(out, "w") as fh:
        fh.write("".join("%d %d %d %d\n" % t for t in R))
    print(f"m={len(R)} bound={solver.BestObjectiveBound() if mode not in ('fixknown', 'atmost') else '-'} -> {out}")
else:
    print()
