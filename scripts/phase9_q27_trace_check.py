#!/usr/bin/env python3
r"""Phase 9 Experiment 2: F_3-linear trace blocking set B_tr in PG(2, 27) / BG(2, 27).

Pure Python (std-only), uses GeneralGF(27) from scripts/gen_general_tqv.py.
Computes:
  1. Standard trace blocking set B_tr of size 37 in PG(2, 27) via Tr(x) = x + x^3 + x^9.
  2. Exact secant distribution across all 757 lines of PG(2, 27) and minimality check.
  3. All (P_infty, L_infty) tangent pairs with P_infty in B_tr, L_infty tangent to B_tr,
     and exact horizontal-line profiles (m, sorted point distribution summing to 36).
  4. Explicit affine realizations A in AG(2, 27) for each profile type, verified against
     all 729 non-horizontal lines c + al*d = u.
  5. Exact LP / combinatorial lower bounds and explicit Cubic Trace Grid construction
     in M(R) for v = 24, 25, 26, 27 (beating existing q=27 lists: v=24 m=930, v=25 m=968).

Usage:
  python3 scripts/phase9_q27_trace_check.py [--save-dir data/phase9_explore]
"""

from __future__ import annotations

import argparse
import collections
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_general_tqv import GeneralGF  # noqa: E402


def build_gf27():
    F = GeneralGF(27)
    q = 27
    add, mul = F.add, F.mul
    neg = [next(b for b in range(q) if add[a][b] == 0) for a in range(q)]
    inv = [0] + [next(b for b in range(q) if mul[a][b] == 1) for a in range(1, q)]

    def pw(x, e):
        r = 1
        for _ in range(e):
            r = mul[r][x]
        return r

    tr = [add[add[x][pw(x, 3)]][pw(x, 9)] for x in range(q)]
    sub = sorted(x for x in range(q) if pw(x, 3) == x)
    assert sub == [0, 1, 2]
    assert set(tr) == set(sub)
    assert all(tr.count(s) == 9 for s in sub)
    return F, neg, inv, pw, tr, sub


def norm_pt(F, inv, x, y, z):
    if z != 0:
        iz = inv[z]
        return (F.mul[x][iz], F.mul[y][iz], 1)
    if y != 0:
        iy = inv[y]
        return (F.mul[x][iy], 1, 0)
    assert x != 0
    return (1, 0, 0)


def build_pg2(F):
    q = F.q
    pts = [(x, y, 1) for x in range(q) for y in range(q)]
    pts += [(x, 1, 0) for x in range(q)]
    pts.append((1, 0, 0))
    return pts, list(pts)


def lp_lower_bound_profile(q, v, m_nonfull, size_nonfull):
    """Discrete lower bound over (k_a, k_b, E) for a fixed non-full class profile."""
    best_lb = 10**9
    best_cfg = None
    for k_a in range(v + 1):
        f_a = v - k_a
        sum_mu = k_a * m_nonfull + f_a
        r_a = q * v + (size_nonfull - q) * k_a
        for k_b in range(k_a, v + 1):
            f_b = v - k_b
            sum_nu = k_b * m_nonfull + f_b
            r_b = q * v + (size_nonfull - q) * k_b
            budget_sqrt = 0.5 * (sum_mu + sum_nu)
            min_r_pair = 10**9
            for E in range(0, v * v + 1):
                if q * q + E >= best_lb:
                    break
                p0 = min(v * v, q + E)
                rem = v * v - p0
                n_full = rem // q
                rem_last = rem % q
                if 1 + n_full + (1 if rem_last else 0) <= q:
                    min_sum_sqrt = math.sqrt(p0) + n_full * math.sqrt(q) + math.sqrt(rem_last)
                else:
                    continue
                if min_sum_sqrt <= budget_sqrt + 1e-9:
                    min_r_pair = q * q + E
                    break
            lb = max(r_a, r_b, min_r_pair)
            if lb < best_lb:
                best_lb = lb
                best_cfg = (k_a, f_a, k_b, f_b, r_a, r_b, min_r_pair)
    return best_lb, best_cfg


def check_model_m(F, reps, v):
    """Independent checker for M(R) (point cov, line incidence, symbol pairs, uniqueness)."""
    q = F.q
    add, mul = F.add, F.mul
    pts = {(c, d) for (c, d, a, b) in reps}
    pairs = {(a, b) for (c, d, a, b) in reps}
    mp = q * q - len(pts)
    mpair = v * v - len(pairs)
    ml = 0
    for side in (2, 3):
        seen = set()
        for r in reps:
            c, d, s = r[0], r[1], r[side]
            for al in range(q):
                seen.add((s, al, add[c][mul[al][d]]))
        ml += v * q * q - len(seen)
    dups = len(reps) - len(set(reps))
    return mp, ml, mpair, dups


def build_cubic_trace_grid(F, neg, inv, tr, sub, params, v):
    """Deterministic Cubic Trace Grid construction in M(R) for q=27, v in {24, 25, 26, 27}.

    Uses 18 m=10 F_3-linear trace classes (size 36, profile (9, 3^9)) on each side:
      - a-classes (0..17): 9 on W1={1/w: Tr(w)=1} with (sc_a1, c0_a1),
                           9 on W2={1/w: Tr(w)=2} with (sc_a2, c0_a2).
      - b-classes (0..17): 9 on W1'={1/w: Tr(3*w)=1} with (sc_b1, c0_b1),
                           9 on W2'={1/w: Tr(3*w)=2} with (sc_b2, c0_b2).
    All 18x18 = 324 (a_cls, b_cls) pairs meet in a unique point on d != 0.
    Full-horizontal symbols 18..23 sit on the 6 empty horizontals W0 \\ W0' (resp. W0' \\ W0).
    Additional full-horizontal symbols 24..v-1 sit on d = 0.
    """
    q = 27
    add, mul = F.add, F.mul
    ker_tr = [x for x in range(q) if tr[x] == 0]
    t_reps = [3 * i for i in range(9)]
    a_dir, b_dir = 1, 3
    w_k = [w for w in range(1, q) if tr[mul[a_dir][w]] == 0 and tr[mul[b_dir][w]] == 0][0]

    sc_a1, c0_a1, sc_a2, c0_a2, sc_b1, c0_b1, sc_b2, c0_b2 = params

    def valid_ab(sc_a, c0_a, sc_b, c0_b):
        if mul[sc_b][inv[sc_a]] in sub:
            return False
        sp = {add[mul[s1][sc_a]][mul[s2][sc_b]] for s1 in sub for s2 in sub}
        return mul[add[c0_b][neg[c0_a]]][w_k] not in sp

    assert valid_ab(sc_a1, c0_a1, sc_b1, c0_b1)
    assert valid_ab(sc_a1, c0_a1, sc_b2, c0_b2)
    assert valid_ab(sc_a2, c0_a2, sc_b1, c0_b1)
    assert valid_ab(sc_a2, c0_a2, sc_b2, c0_b2)

    def d0_set(dir_val, scale_c, shift_c0):
        s = {shift_c0}
        for h in ker_tr:
            if h != 0:
                s.add(add[mul[scale_c][mul[dir_val][inv[h]]]][shift_c0])
        return s

    def make_non0(dir_val, r_val, scale_c, shift_t, shift_c0):
        k0_loc = next(x for x in range(q) if neg[tr[x]] == r_val)
        pts = []
        for h in ker_tr:
            w_std = add[h][neg[k0_loc]]
            d_val = mul[dir_val][inv[w_std]]
            for s in sub:
                c_val = add[mul[scale_c][mul[add[s][shift_t]][d_val]]][shift_c0]
                pts.append((c_val, d_val))
        return pts

    assert 24 <= v <= 27
    n_d0 = v - 24

    a_map = {}
    for g, (ra, sca, c0a) in enumerate([(1, sc_a1, c0_a1), (2, sc_a2, c0_a2)]):
        for ti, t in enumerate(t_reps):
            sym = g * 9 + ti
            for pt in make_non0(a_dir, ra, sca, t, c0a):
                assert pt not in a_map
                a_map[pt] = sym

    b_map = {}
    for g, (rb, scb, c0b) in enumerate([(1, sc_b1, c0_b1), (2, sc_b2, c0_b2)]):
        for ti, t in enumerate(t_reps):
            sym = g * 9 + ti
            for pt in make_non0(b_dir, rb, scb, t, c0b):
                assert pt not in b_map
                b_map[pt] = sym

    w0_b1, w0_b2, a1_w0, a2_w0, both_w0 = [], [], [], [], []
    for d in range(1, q):
        w = inv[d]
        ta = tr[mul[a_dir][w]]
        tb = tr[mul[b_dir][w]]
        if ta == 0 and tb == 1:
            w0_b1.append(d)
        elif ta == 0 and tb == 2:
            w0_b2.append(d)
        elif ta == 1 and tb == 0:
            a1_w0.append(d)
        elif ta == 2 and tb == 0:
            a2_w0.append(d)
        elif ta == 0 and tb == 0:
            both_w0.append(d)

    full_a_on_d = {d: 18 + i for i, d in enumerate(w0_b1 + w0_b2)}
    full_b_on_d = {d: 18 + i for i, d in enumerate(a1_w0 + a2_w0)}

    reps = []
    covered_pairs = set()

    for d in range(1, q):
        if d in both_w0:
            continue
        for c in range(q):
            a_sym = a_map.get((c, d), full_a_on_d.get(d))
            b_sym = b_map.get((c, d), full_b_on_d.get(d))
            reps.append((c, d, a_sym, b_sym))
            covered_pairs.add((a_sym, b_sym))

    # Place up to 54 (full_a, full_b) pairs on the 2 empty horizontals both_w0,
    # prioritizing pairs involving 18..23 so any overflow on d=0 involves 24..v-1!
    ff_pairs = (
        [(fa, fb) for fa in range(18, 24) for fb in range(18, 24)]
        + [(fa, fb) for fa in range(18, 24) for fb in range(24, v)]
        + [(fa, fb) for fa in range(24, v) for fb in range(18, 24)]
        + [(fa, fb) for fa in range(24, v) for fb in range(24, v)]
    )
    both_pts = [(c, d) for d in both_w0 for c in range(q)]
    for idx, (c, d) in enumerate(both_pts):
        fa, fb = ff_pairs[idx % len(ff_pairs)]
        reps.append((c, d, fa, fb))
        covered_pairs.add((fa, fb))

    rem_ff = [p for p in ff_pairs if p not in covered_pairs]
    assert all((a, b) in covered_pairs for a in range(18) for b in range(18))

    miss_a_fb = [(a, fb) for a in range(18) for fb in range(18, v) if (a, fb) not in covered_pairs]
    miss_fa_b = [(fa, b) for fa in range(18, v) for b in range(18) if (fa, b) not in covered_pairs]

    Sa1 = d0_set(a_dir, sc_a1, c0_a1)
    Sa2 = d0_set(a_dir, sc_a2, c0_a2)
    Sb1 = d0_set(b_dir, sc_b1, c0_b1)
    Sb2 = d0_set(b_dir, sc_b2, c0_b2)

    need_a = [set() for _ in range(q)]
    need_b = [set() for _ in range(q)]
    for c in range(q):
        if c in Sa1:
            need_a[c].update(range(0, 9))
        if c in Sa2:
            need_a[c].update(range(9, 18))
        if c in Sb1:
            need_b[c].update(range(0, 9))
        if c in Sb2:
            need_b[c].update(range(9, 18))
        for sym in range(24, v):
            need_a[c].add(sym)
            need_b[c].add(sym)

    d0_reps = [[] for _ in range(q)]

    # Step A: At every point c where BOTH class sides are present, satisfy full_d0 symbols (24..v-1)
    # by placing one (a_cls, sym) and one (sym, b_cls) from miss_a_fb / miss_fa_b!
    rem_a_fb = list(miss_a_fb)
    rem_fa_b = list(miss_fa_b)
    rem_ff_mut = list(rem_ff)

    both_c = [c for c in range(q) if (c in Sa1 or c in Sa2) and (c in Sb1 or c in Sb2)]
    other_c = [c for c in range(q) if c not in both_c]

    for sym in range(24, v):
        # Satisfy sym on b-side at all both_c points using (a_cls, sym)
        for c in both_c:
            # Prefer a_cls from the smaller-overlap group at c (or any needed a_cls at c)
            cand_idx = None
            for idx, (a, fb) in enumerate(rem_a_fb):
                if fb == sym and a in need_a[c] and (a, fb) not in d0_reps[c]:
                    cand_idx = idx
                    break
            if cand_idx is not None:
                a, fb = rem_a_fb.pop(cand_idx)
                d0_reps[c].append((a, fb))
                need_a[c].discard(a)
                need_b[c].discard(fb)
        # Satisfy sym on a-side at all both_c points using (sym, b_cls)
        for c in both_c:
            cand_idx = None
            for idx, (fa, b) in enumerate(rem_fa_b):
                if fa == sym and b in need_b[c] and (fa, b) not in d0_reps[c]:
                    cand_idx = idx
                    break
            if cand_idx is not None:
                fa, b = rem_fa_b.pop(cand_idx)
                d0_reps[c].append((fa, b))
                need_a[c].discard(fa)
                need_b[c].discard(b)

    # Step B: At non-both points c (other_c), place any remaining rem_ff pairs involving 24..v-1,
    # then satisfy remaining full_d0 needs with (sym, sym) pairs!
    for c in other_c:
        # First try pairing remaining rem_ff_mut that hit both need_a[c] and need_b[c]
        progressed = True
        while progressed:
            progressed = False
            for idx, (fa, fb) in enumerate(rem_ff_mut):
                if fa in need_a[c] and fb in need_b[c] and (fa, fb) not in d0_reps[c]:
                    rem_ff_mut.pop(idx)
                    d0_reps[c].append((fa, fb))
                    need_a[c].discard(fa)
                    need_b[c].discard(fb)
                    progressed = True
                    break
        # If c has only a_cls (no b_cls), we can satisfy full_b_d0 with (a_cls, sym) and full_a_d0 with rem_ff (sym, 18..23)!
        if need_a[c] and not (c in Sb1 or c in Sb2):
            for sym in range(24, v):
                if sym in need_a[c]:
                    idx_ff = next((i for i, (fa, fb) in enumerate(rem_ff_mut) if fa == sym and (fa, fb) not in d0_reps[c]), None)
                    if idx_ff is not None:
                        fa, fb = rem_ff_mut.pop(idx_ff)
                        d0_reps[c].append((fa, fb))
                        need_a[c].discard(fa)
                        need_b[c].discard(fb)
        if need_b[c] and not (c in Sa1 or c in Sa2):
            for sym in range(24, v):
                if sym in need_b[c]:
                    idx_ff = next((i for i, (fa, fb) in enumerate(rem_ff_mut) if fb == sym and (fa, fb) not in d0_reps[c]), None)
                    if idx_ff is not None:
                        fa, fb = rem_ff_mut.pop(idx_ff)
                        d0_reps[c].append((fa, fb))
                        need_a[c].discard(fa)
                        need_b[c].discard(fb)
        # Pair any remaining full_d0 on both sides at c with (sym, sym)
        for sym in range(24, v):
            if sym in need_a[c] and sym in need_b[c] and (sym, sym) not in d0_reps[c]:
                d0_reps[c].append((sym, sym))
                need_a[c].discard(sym)
                need_b[c].discard(sym)

    # Step C: Greedily place all remaining missing pairs (rem_ff_mut, rem_a_fb, rem_fa_b)
    def cur_tot(c):
        return len(d0_reps[c]) + max(len(need_a[c]), len(need_b[c]), 1 if len(d0_reps[c]) == 0 else 0)

    def place_pair(a, b):
        best_c = None
        best_key = None
        for c in range(q):
            if (a, b) in d0_reps[c]:
                continue
            old_t = cur_tot(c)
            na_after = len(need_a[c]) - (1 if a in need_a[c] else 0)
            nb_after = len(need_b[c]) - (1 if b in need_b[c] else 0)
            new_t = len(d0_reps[c]) + 1 + max(na_after, nb_after)
            delta = new_t - old_t
            hits = (1 if a in need_a[c] else 0) + (1 if b in need_b[c] else 0)
            imb = 0
            if a in need_a[c] and b not in need_b[c]:
                imb = len(need_a[c]) - len(need_b[c])
            elif b in need_b[c] and a not in need_a[c]:
                imb = len(need_b[c]) - len(need_a[c])
            key = (delta, -hits, -imb, c)
            if best_key is None or key < best_key:
                best_key = key
                best_c = c
        d0_reps[best_c].append((a, b))
        need_a[best_c].discard(a)
        need_b[best_c].discard(b)

    for p in rem_ff_mut:
        place_pair(*p)
    for i in range(max(len(rem_a_fb), len(rem_fa_b))):
        if i < len(rem_a_fb):
            place_pair(*rem_a_fb[i])
        if i < len(rem_fa_b):
            place_pair(*rem_fa_b[i])

    # Step D: Pair up remaining need_a[c], need_b[c], and ensure every c has >= 1 rep
    for c in range(q):
        la = sorted(need_a[c])
        lb = sorted(need_b[c])
        existing = set(d0_reps[c])
        k = max(len(la), len(lb))
        if k == 0 and len(d0_reps[c]) == 0:
            d0_reps[c].append((0, 0))
            continue
        for i in range(k):
            a = la[i] if i < len(la) else 0
            b = lb[i] if i < len(lb) else 0
            if (a, b) in existing:
                if i >= len(la):
                    a = next(x for x in range(v) if (x, b) not in existing)
                elif i >= len(lb):
                    b = next(x for x in range(v) if (a, x) not in existing)
                else:
                    swapped = False
                    for j in range(i + 1, len(lb)):
                        if (a, lb[j]) not in existing:
                            lb[i], lb[j] = lb[j], lb[i]
                            b = lb[i]
                            swapped = True
                            break
                    assert swapped
            d0_reps[c].append((a, b))
            existing.add((a, b))

    for c in range(q):
        for (a, b) in d0_reps[c]:
            reps.append((c, 0, a, b))

    return reps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save-dir", help="Optional directory to save improved v=24 (<930) and v=25 (<968) lists")
    args = ap.parse_args()

    t0 = time.monotonic()
    F, neg, inv, pw, tr, sub = build_gf27()
    q = 27
    add, mul = F.add, F.mul

    B = {(x, tr[x], 1) for x in range(q)} | {norm_pt(F, inv, x, tr[x], 0) for x in range(1, q)}
    assert len(B) == 37
    pts, lines = build_pg2(F)

    secant_hist = collections.Counter()
    pt_lines_B = {p: [] for p in B}
    for L in lines:
        a, b, c = L
        hits = [p for p in B if add[add[mul[a][p[0]]][mul[b][p[1]]]][mul[c][p[2]]] == 0]
        secant_hist[len(hits)] += 1
        for p in hits:
            pt_lines_B[p].append((L, len(hits)))

    print(f"GF(27) mod_poly={F.mod_poly}, F_3={sub}")
    print(f"|B_tr| = {len(B)}, secant_hist = {dict(sorted(secant_hist.items()))}")
    assert secant_hist.get(0, 0) == 0
    min_tangents = min(sum(1 for _, k in lst if k == 1) for lst in pt_lines_B.values())
    print(f"Min tangents per point in B_tr = {min_tangents} -> minimal blocking set = {min_tangents >= 1}")

    profile_pts = collections.Counter()
    profile_pairs = collections.Counter()
    profile_examples = {}
    for p, lst in pt_lines_B.items():
        nt = sum(1 for _, k in lst if k == 1)
        if nt == 0:
            continue
        horiz_counts = tuple(sorted((k - 1 for _, k in lst if k > 1), reverse=True))
        prof = (len(horiz_counts), horiz_counts)
        profile_pts[prof] += 1
        profile_pairs[prof] += nt
        if prof not in profile_examples:
            profile_examples[prof] = (p, next(L for L, k in lst if k == 1), nt)

    print("\n=== Horizontal-line profiles (P_infty in B_tr, tangent L_infty) ===")
    for prof, n_p in sorted(profile_pts.items()):
        m, dist = prof
        p_ex, L_ex, nt = profile_examples[prof]
        print(f"  m={m:2d}, dist={dist}, Lemma-J slack={36 - (q + m - 1)}: "
              f"{n_p} pts ({nt} tangents each, {profile_pairs[prof]} pairs), ex P={p_ex}, L={L_ex}")

    print("\n=== Explicit affine verification in AG(2, 27) ===")
    for prof, (p_inf, L_inf, _) in sorted(profile_examples.items()):
        a, b, c = L_inf
        px, py, pz = p_inf
        row2 = next(r2 for r2 in lines if r2 != L_inf and add[add[mul[r2[0]][px]][mul[r2[1]][py]]][mul[r2[2]][pz]] == 0)
        row1 = next(cand for cand in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
                    if add[add[mul[cand[0]][px]][mul[cand[1]][py]]][mul[cand[2]][pz]] != 0)
        A = set()
        for pt in B:
            if pt == p_inf:
                continue
            xp = add[add[mul[row1[0]][pt[0]]][mul[row1[1]][pt[1]]]][mul[row1[2]][pt[2]]]
            yp = add[add[mul[row2[0]][pt[0]]][mul[row2[1]][pt[1]]]][mul[row2[2]][pt[2]]]
            zp = add[add[mul[a][pt[0]]][mul[b][pt[1]]]][mul[c][pt[2]]]
            iz = inv[zp]
            A.add((mul[xp][iz], mul[yp][iz]))
        hits = {(al, add[cc][mul[al][dd]]) for (cc, dd) in A for al in range(q)}
        dist_chk = tuple(sorted(collections.Counter(dd for (_, dd) in A).values(), reverse=True))
        assert len(A) == 36 and len(hits) == 729 and dist_chk == prof[1]
        print(f"  m={prof[0]:2d}: |A|=36, miss_non_horiz=0, dist={dist_chk} PASS")

    print("\n=== Universal LP Lower Bounds in M(R) (class size 36) ===")
    for prof in sorted(profile_pts.keys()):
        m, _ = prof
        for v in (24, 25, 27):
            lb, cfg = lp_lower_bound_profile(q, v, m, 36)
            print(f"  m={m:2d}, v={v}: |R| >= {lb} (k_a={cfg[0]}, k_b={cfg[2]}, size_b={cfg[5]}, pair_lb={cfg[6]})")

    print("\n=== Explicit Cubic Trace Grid Construction in M(R) (q = 27) ===")
    configs = [
        (24, (1, 0, 1, 3, 4, 12, 4, 18), 930),
        (25, (1, 0, 3, 5, 5, 9, 9, 3), 968),
        (26, (1, 0, 3, 5, 5, 9, 9, 3), None),
        (27, (1, 0, 3, 5, 5, 9, 9, 3), None),
    ]
    if args.save_dir:
        os.makedirs(args.save_dir, exist_ok=True)
    for v, prm, baseline in configs:
        reps = build_cubic_trace_grid(F, neg, inv, tr, sub, prm, v)
        mp, ml, mpair, dups = check_model_m(F, reps, v)
        assert mp == 0 and ml == 0 and mpair == 0 and dups == 0
        cmp_str = f" (vs baseline {baseline}: delta={len(reps) - baseline:+d})" if baseline else ""
        print(f"  q=27 v={v}: |R|={len(reps)}{cmp_str}, miss_pts={mp}, miss_lines={ml}, miss_pairs={mpair}, dups={dups} PASS")
        if args.save_dir and baseline is not None and len(reps) < baseline:
            out_path = os.path.join(args.save_dir, f"R_q27_v{v}_m{len(reps)}.txt")
            with open(out_path, "w") as fh:
                fh.write(f"# Phase 9 Cubic Trace Grid: q=27 v={v} m={len(reps)} params={prm}\n")
                for r in reps:
                    fh.write(" ".join(map(str, r)) + "\n")
            print(f"    -> saved {out_path}")

    print(f"\nElapsed: {time.monotonic() - t0:.3f}s")


if __name__ == "__main__":
    main()
