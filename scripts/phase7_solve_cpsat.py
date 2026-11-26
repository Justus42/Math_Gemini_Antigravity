#!/usr/bin/env python3
"""Phase 7: exact model for the smallest representative set R (see docs/PHASE7_T2_REDUCTION.md).

NOT std-only: needs Google OR-Tools (pip install ortools). Runs with a wall-clock limit and two
workers, so a run that stops at the limit is NOT byte-reproducible; only the representative list
it writes is the result, and that list is checked by scripts/phase7_lift.py and the verifiers.

Variables: one 0/1 variable per (c, d, a, b) in GF(q)^4 (prime q).
Conditions: for every pair of columns of M(R) and every pair of symbols, at least one chosen row.
WLOG (0, 0, 0, 0) is chosen (rename the symbols in columns a and b).

Usage:
  phase7_solve_cpsat.py Q SECONDS fixknown        # positive control: Phase 6A solution is feasible
  phase7_solve_cpsat.py Q SECONDS min             # minimise m
  phase7_solve_cpsat.py Q SECONDS atmost M        # decide: is there a solution with <= M rows?
"""
import itertools
import sys
import time

from ortools.sat.python import cp_model

q = int(sys.argv[1])
limit = float(sys.argv[2])
mode = sys.argv[3] if len(sys.argv) > 3 else "min"
arg = int(sys.argv[4]) if len(sys.argv) > 4 else None
T = list(itertools.product(range(q), repeat=4))
rows = {t: [(t[0] + al * t[1]) % q for al in range(q)] + [t[2], t[3]] for t in T}
k = q + 2
model = cp_model.CpModel()
x = {t: model.NewBoolVar("x%d_%d_%d_%d" % t) for t in T}
cons = set()
for i, j in itertools.combinations(range(k), 2):
    buckets = {}
    for t in T:
        buckets.setdefault((rows[t][i], rows[t][j]), []).append(t)
    assert len(buckets) == q * q
    cons.update(frozenset(ts) for ts in buckets.values())
for ts in cons:
    model.AddBoolOr([x[t] for t in ts])
print(f"q={q} vars={len(T)} pair-conditions={(k * (k - 1) // 2) * q * q} distinct={len(cons)}", flush=True)
known = {(c, d, d, min(c, d)) for c in range(q) for d in range(q)} | \
        {(c, d, c, d) for d in range(q) for c in range(d)}
total = sum(x.values())
if mode == "fixknown":
    for t in T:
        model.Add(x[t] == (1 if t in known else 0))
elif mode == "atmost":
    model.Add(total <= arg)
    model.Add(x[(0, 0, 0, 0)] == 1)
else:
    model.Minimize(total)
    model.Add(x[(0, 0, 0, 0)] == 1)
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = limit
solver.parameters.num_search_workers = 2
solver.parameters.random_seed = 1
t0 = time.time()
status = solver.Solve(model)
print(f"status={solver.StatusName(status)} time={time.time() - t0:.1f}s", end=" ")
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    R = sorted(t for t in T if solver.Value(x[t]))
    out = f"R_q{q}_m{len(R)}.txt"
    with open(out, "w") as fh:
        fh.write("".join("%d %d %d %d\n" % t for t in R))
    print(f"m={len(R)} -> {out}")
else:
    print()
