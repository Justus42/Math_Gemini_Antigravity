#!/usr/bin/env python3
"""
Phase 9B Option B — AP 1 Structural Analysis & Invariant Extractor.

Analyzes Stage-1 exhaustive dumps for q in {5, 7, 8, 9} (and optionally 11, 13):
  1. Algebraic invariants (minpoly, trace, norm, order, x^(q+1), x^(q-1)) and
     exact symmetry-orbit decomposition of all unc=0 hits at q=5 (916) and q=7 (4).
  2. Uncovered 6-tuple split breakdown, column-support / subfield / difference-pattern
     diagnostics, and independent exact hitting-set verification at q=8 and q=9.
"""

import argparse
import itertools
import json
import math
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "scripts")
from phase9_cphf_t6_check import (
    FiniteField,
    build_parametric_rows,
    check_all_6tuples,
    find_sherwood_hyperplane,
)


def k_add(ff: FiniteField, u, v):
    return (ff.add[u[0]][v[0]], ff.add[u[1]][v[1]])


def k_conj(ff: FiniteField, u):
    return ff.kpow(u, ff.q)


def k_inv(ff: FiniteField, u):
    return ff.kpow(u, ff.q * ff.q - 2)


def k_order(ff: FiniteField, u):
    order = ff.q * ff.q - 1
    divs = sorted(d for d in range(1, order + 1) if order % d == 0)
    for d in divs:
        if ff.kpow(u, d) == (1, 0):
            return d
    return order


def k_invariants(ff: FiniteField, u):
    uq = k_conj(ff, u)
    tr = k_add(ff, u, uq)
    nm = ff.kmul(u, uq)
    assert tr[1] == 0 and nm[1] == 0
    tr_v = tr[0]
    nm_v = nm[0]
    in_fq = (u[1] == 0)
    minpoly = f"X - {u[0]}" if in_fq else f"X^2 - {tr_v}*X + {nm_v}"
    ord_u = k_order(ff, u)
    u_qp1 = ff.kpow(u, ff.q + 1)  # norm in F_q*
    u_qm1 = ff.kpow(u, ff.q - 1)  # phase in U
    return {
        "val": list(u),
        "in_Fq": in_fq,
        "minpoly": minpoly,
        "trace": tr_v,
        "norm": nm_v,
        "order": ord_u,
        "pow_qp1": list(u_qp1),
        "ord_qp1": k_order(ff, u_qp1),
        "pow_qm1": list(u_qm1),
        "ord_qm1": k_order(ff, u_qm1),
    }


def build_k_log(ff: FiniteField):
    log = {}
    cur = (1, 0)
    for e in range(ff.q * ff.q - 1):
        log[cur] = e
        cur = ff.kmul(cur, ff.zeta)
    return log


def norm_ab(ff: FiniteField, log, alpha, beta):
    """Canonical (alpha', beta') mod F_q^* with alpha' = zeta^{ac}, ac in 0..q."""
    n = ff.q + 1
    order = ff.q * ff.q - 1
    la = log[alpha]
    ac = la % n
    lam_exp = (la - ac) % order
    inv_lam = ff.kpow(ff.zeta, (-lam_exp) % order)
    alpha_p = ff.kpow(ff.zeta, ac)
    beta_p = ff.kmul(beta, inv_lam)
    return alpha_p, beta_p


def sym_orbit_rep(ff: FiniteField, log, g1, g2, alpha, beta, m2):
    """Compute full symmetry orbit under Swap(A<->B), Gal(K/F_p), and simultaneous shift."""
    q = ff.q
    n = q + 1
    p = {5: 5, 7: 7, 8: 2, 9: 3, 11: 11, 13: 13}[q]
    e_gal = {5: 2, 7: 2, 8: 6, 9: 4, 11: 2, 13: 2}[q]
    alpha, beta = norm_ab(ff, log, alpha, beta)
    start = (g1, g2, alpha, beta, m2)
    seen = {start}
    queue = [start]
    while queue:
        cg1, cg2, ca, cb, cm2 = queue.pop()
        # 1. Gal(K/F_p): z -> z^p (preserves m2)
        nxt = (
            ff.kpow(cg1, p),
            ff.kpow(cg2, p),
            *norm_ab(ff, log, ff.kpow(ca, p), ff.kpow(cb, p)),
            cm2,
        )
        if nxt not in seen:
            seen.add(nxt)
            queue.append(nxt)
        # 2. Swap A <-> B: (g1^-1, g2^-1, alpha^-1, beta^-1, m2^-1)
        m2_inv = pow(cm2, -1, n)
        nxt2 = (
            k_inv(ff, cg1),
            k_inv(ff, cg2),
            *norm_ab(ff, log, k_inv(ff, ca), k_inv(ff, cb)),
            m2_inv,
        )
        if nxt2 not in seen:
            seen.add(nxt2)
            queue.append(nxt2)
        # 3. Simultaneous column shift r on A and B (fixes R1, shifts R2 when m2 != 1)
        if cm2 != 1:
            sh = (cm2 - 1) % n
            a2 = ff.kmul(ca, ff.kpow(ff.eta, (2 * sh) % n))
            b2 = ff.kmul(cb, ff.kpow(ff.eta, sh))
            nxt3 = (cg1, cg2, *norm_ab(ff, log, a2, b2), cm2)
            if nxt3 not in seen:
                seen.add(nxt3)
                queue.append(nxt3)
    return min(seen), len(seen), seen


def analyze_zeros(q: int, dump_path: str):
    with open(dump_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    ff = FiniteField(q)
    log = build_k_log(ff)
    zeros = data["zeros"]
    print(f"\n================ AP 1.1: q = {q} (k = {2*q+2}), zero_hits = {len(zeros)} ================")
    print(f"Field generator zeta = {ff.zeta}: {k_invariants(ff, ff.zeta)}")
    print(f"Norm-1 generator eta = {ff.eta}: {k_invariants(ff, ff.eta)}")

    orbits = {}
    m2_counts = Counter()
    norm_g1_g2 = Counter()
    ratio_in_fq = 0
    for z in zeros:
        g1 = tuple(z["g1"])
        g2 = tuple(z["g2"])
        al = tuple(z["alpha"])
        be = tuple(z["beta"])
        m2 = z["m2"]
        m2_counts[m2] += 1
        rep, osz, _ = sym_orbit_rep(ff, log, g1, g2, al, be, m2)
        orbits.setdefault(rep, []).append((g1, g2, al, be, m2))
        ng1 = ff.kpow(g1, q + 1)[0]
        ng2 = ff.kpow(g2, q + 1)[0]
        norm_g1_g2[(ng1, ng2)] += 1
        # Check alpha / beta^2
        ab2 = ff.kmul(al, k_inv(ff, ff.kmul(be, be)))
        if ab2[1] == 0:
            ratio_in_fq += 1

    print(f"By m2: {dict(m2_counts)}")
    print(f"Distinct symmetry orbits (under Swap A<->B, Gal(K/F_p), shift): {len(orbits)}")
    orbit_sizes = Counter(len(v) for v in orbits.values())
    print(f"Orbit size distribution in raw Stage-1 space: {dict(orbit_sizes)}")
    print(f"Solutions with alpha/beta^2 in F_q*: {ratio_in_fq} / {len(zeros)}")

    # Print detailed info for all orbits if <= 10, else top 5
    sorted_orbs = sorted(orbits.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    show_n = len(sorted_orbs) if len(sorted_orbs) <= 10 else 5
    for idx, (rep, members) in enumerate(sorted_orbs[:show_n]):
        g1, g2, al, be, m2 = rep
        ab2 = ff.kmul(al, k_inv(ff, ff.kmul(be, be)))
        # Check Sherwood hyperplanes for this rep
        R1, R2 = build_parametric_rows(ff, g1, g2, al, be, m2=m2)
        v1 = find_sherwood_hyperplane(ff, R1)
        v2 = find_sherwood_hyperplane(ff, R2)
        print(f"\n  Orbit #{idx+1} (size={len(members)}, m2={m2}, Sherwood={v1 is not None and v2 is not None}):")
        print(f"    rep: g1={g1} (log={log[g1]}), g2={g2} (log={log[g2]}), alpha={al} (log={log[al]}), beta={be} (log={log[be]})")
        print(f"    g1 inv:    {k_invariants(ff, g1)}")
        print(f"    g2 inv:    {k_invariants(ff, g2)}")
        print(f"    alpha inv: {k_invariants(ff, al)}")
        print(f"    beta inv:  {k_invariants(ff, be)}")
        print(f"    alpha/beta^2 inv: {k_invariants(ff, ab2)}")
        if len(members) <= 8:
            print(f"    all members ({len(members)}):")
            for m in members:
                mg1, mg2, mal, mbe, mm2 = m
                print(f"      g1={mg1}(log={log[mg1]}), g2={mg2}(log={log[mg2]}), a={mal}(log={log[mal]}), b={mbe}(log={log[mbe]}), m2={mm2}")

    # Summary statistics over all zeros for q=5
    if len(zeros) > 10:
        g1_in_fq = sum(1 for z in zeros if z["g1"][1] == 0)
        g2_in_fq = sum(1 for z in zeros if z["g2"][1] == 0)
        g1_ords = Counter(k_order(ff, tuple(z["g1"])) for z in zeros)
        g2_ords = Counter(k_order(ff, tuple(z["g2"])) for z in zeros)
        al_ords = Counter(k_order(ff, tuple(z["alpha"])) for z in zeros)
        be_ords = Counter(k_order(ff, tuple(z["beta"])) for z in zeros)
        ab2_ords = Counter(
            k_order(ff, ff.kmul(tuple(z["alpha"]), k_inv(ff, ff.kmul(tuple(z["beta"]), tuple(z["beta"])))))
            for z in zeros
        )
        print(f"\n  Aggregate invariants across all {len(zeros)} hits at q={q}:")
        print(f"    g1 in F_q*: {g1_in_fq}, g2 in F_q*: {g2_in_fq}")
        print(f"    ord(g1): {dict(sorted(g1_ords.items()))}")
        print(f"    ord(g2): {dict(sorted(g2_ords.items()))}")
        print(f"    ord(alpha): {dict(sorted(al_ords.items()))}")
        print(f"    ord(beta):  {dict(sorted(be_ords.items()))}")
        print(f"    ord(alpha/beta^2): {dict(sorted(ab2_ords.items()))}")

    return {
        "q": q,
        "zero_hits": len(zeros),
        "n_orbits": len(orbits),
        "orbit_sizes": dict(orbit_sizes),
        "by_m2": dict(m2_counts),
    }


def analyze_errors(q: int, dump_path: str):
    with open(dump_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    ff = FiniteField(q)
    n = q + 1
    ev = data["evaluated"]
    print(f"\n================ AP 1.2: q = {q} (k = {2*n}), evaluated = {len(ev)} ================")
    min_unc = min(c["unc"] for c in ev)
    min_tau = min(c["tau"] for c in ev if c["tau"] >= 0)
    print(f"Global min_unc = {min_unc}, global min_tau = {min_tau}, best k_punc = {2*n - min_tau} / {2*n}")

    # Distribution by m2
    by_m2 = defaultdict(list)
    for c in ev:
        by_m2[c["m2"]].append(c)
    for m2, lst in sorted(by_m2.items()):
        mu = min(x["unc"] for x in lst)
        mt = min(x["tau"] for x in lst if x["tau"] >= 0)
        ex = all(x["exact_tau"] == 1 for x in lst if x["tau"] == mt)
        print(f"  m2={m2}: n_eval={len(lst)}, min_unc={mu}, min_tau={mt} (exact={ex}, k_punc={2*n-mt})")

    # Inspect the min_unc winner and the best_tau winner in detail
    c_min_unc = min(ev, key=lambda x: (x["unc"], x["tau"]))
    c_min_tau = min(ev, key=lambda x: (x["tau"], x["unc"]))
    targets = [("min_unc_winner", c_min_unc)]
    if c_min_tau != c_min_unc:
        targets.append(("min_tau_winner", c_min_tau))

    # Also find any non-m2=1 candidate with best tau
    ne1 = [x for x in ev if x["m2"] != 1]
    if ne1:
        c_ne1 = min(ne1, key=lambda x: (x["tau"], x["unc"]))
        targets.append(("best_m2_ne_1", c_ne1))

    details = {}
    for label, c in targets:
        g1, g2 = tuple(c["g1"]), tuple(c["g2"])
        al, be, m2 = tuple(c["alpha"]), tuple(c["beta"]), c["m2"]
        R1, R2 = build_parametric_rows(ff, g1, g2, al, be, m2=m2)
        bad_tuples = []
        dep1_s = [0] * 7
        dep2_s = [0] * 7
        both_s = [0] * 7
        col_freq = [0] * (2 * n)
        for tup in itertools.combinations(range(2 * n), 6):
            a = sum(1 for x in tup if x < n)
            ok1 = ff.has_full_rank_6([R1[x] for x in tup])
            ok2 = ff.has_full_rank_6([R2[x] for x in tup])
            if not ok1:
                dep1_s[a] += 1
            if not ok2:
                dep2_s[a] += 1
            if not ok1 and not ok2:
                both_s[a] += 1
                bad_tuples.append(tup)
                for x in tup:
                    col_freq[x] += 1

        del_cols = [i for i in range(2 * n) if (c["del_mask"] >> i) & 1]
        # Verify del_cols is a valid hitting set
        del_set = set(del_cols)
        uncovered_after = sum(1 for tup in bad_tuples if not (set(tup) & del_set))
        assert uncovered_after == 0, f"Invalid hitting set for {label}!"

        # Check column-frequency distribution (subfield columns vs non-subfield)
        freq_A = col_freq[:n]
        freq_B = col_freq[n:]
        # Identify cyclic difference patterns of uncovered tuples
        diff_pats = Counter()
        for tup in bad_tuples:
            A = sorted(x for x in tup if x < n)
            B = sorted(x - n for x in tup if x >= n)
            # Canonical shift-normalized pattern (shift A[0] to 0)
            if A:
                s = A[0]
                A_norm = tuple(sorted((x - s) % n for x in A))
                B_norm = tuple(sorted((x - s) % n for x in B))
                diff_pats[(A_norm, B_norm)] += 1

        # Compute expected random overlap from dep1 and dep2 densities
        n42 = math.comb(n, 4) * math.comb(n, 2)
        n33 = math.comb(n, 3) * math.comb(n, 3)
        n24 = math.comb(n, 2) * math.comb(n, 4)
        exp42 = dep1_s[4] * dep2_s[4] / n42
        exp33 = dep1_s[3] * dep2_s[3] / n33
        exp24 = dep1_s[2] * dep2_s[2] / n24

        print(f"\n  [{label}] g1={g1}, g2={g2}, alpha={al}, beta={be}, m2={m2}")
        print(f"    dep1(a=0..6) = {dep1_s} (crit={dep1_s[4]+dep1_s[3]+dep1_s[2]})")
        print(f"    dep2(a=0..6) = {dep2_s} (crit={dep2_s[4]+dep2_s[3]+dep2_s[2]})")
        print(f"    both(a=0..6) = {both_s} (unc={len(bad_tuples)})")
        print(f"    random-indep expectation: 42={exp42:.1f}, 33={exp33:.1f}, 24={exp24:.1f}, sum={exp42+exp33+exp24:.1f}")
        print(f"    tau={c['tau']} (exact={c['exact_tau']}, greedy={c['greedy_tau']}), k_punc={2*n - c['tau']}, del_cols={del_cols} (verified 0 remaining)")
        print(f"    col_freq Orbit A (0..{n-1}): {freq_A}")
        print(f"    col_freq Orbit B ({n}..{2*n-1}): {freq_B}")
        print(f"    top difference patterns (shift-norm): {diff_pats.most_common(5)}")

        # Subfield column check: for q=8, u in F_4^* <=> k % 3 == 0; for q=9, u^2=1 <=> k%5==0, u^5=1 <=> k%2==0
        if q == 8:
            subA = [freq_A[k] for k in range(n) if k % 3 == 0]
            nonA = [freq_A[k] for k in range(n) if k % 3 != 0]
            subB = [freq_B[k] for k in range(n) if k % 3 == 0]
            nonB = [freq_B[k] for k in range(n) if k % 3 != 0]
            print(f"    subfield check (q=8, F_4 coset k%3==0): A avg={sum(subA)/len(subA):.2f} vs non={sum(nonA)/len(nonA):.2f}; B avg={sum(subB)/len(subB):.2f} vs non={sum(nonB)/len(nonB):.2f}")
        elif q == 9:
            evA = [freq_A[k] for k in range(n) if k % 2 == 0]
            odA = [freq_A[k] for k in range(n) if k % 2 == 1]
            f5A = [freq_A[k] for k in range(n) if k % 5 == 0]
            print(f"    subfield check (q=9, k%2==0 vs 1): A avg={sum(evA)/len(evA):.2f} vs {sum(odA)/len(odA):.2f}; k%5==0 (u in {{+-1}}): {f5A}")

        details[label] = {
            "params": {"g1": list(g1), "g2": list(g2), "alpha": list(al), "beta": list(be), "m2": m2},
            "dep1": dep1_s, "dep2": dep2_s, "both": both_s,
            "tau": c["tau"], "exact_tau": c["exact_tau"], "k_punc": 2 * n - c["tau"],
            "del_cols": del_cols, "freq_A": freq_A, "freq_B": freq_B,
        }
    return details


def main():
    parser = argparse.ArgumentParser(description="AP 1 structural analysis for q=5,7,8,9")
    parser.add_argument("--dir", type=str, default="/tmp/phase9_ap1")
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args()

    summary = {}
    summary["q5"] = analyze_zeros(5, f"{args.dir}/ap1_q5.json")
    summary["q7"] = analyze_zeros(7, f"{args.dir}/ap1_q7.json")
    summary["q8"] = analyze_errors(8, f"{args.dir}/ap1_q8.json")
    summary["q9"] = analyze_errors(9, f"{args.dir}/ap1_q9.json")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"\nSaved AP 1 summary JSON -> {args.out}")


if __name__ == "__main__":
    main()
