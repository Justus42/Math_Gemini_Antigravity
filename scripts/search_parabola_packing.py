#!/usr/bin/env python3
"""Phase 5B-2C Step B: Explicit reproducible search for AG(2, q) parabola packings.

Pure Python (std-only). Searches from scratch (no hardcoded colorings) for a partition of
AG(2, q) for odd prime power q in {7, 9, 11, 13} into:
  - c_b = (q - 1) / 2 pairwise disjoint minimal affine blocking sets of size 2q - 1
    (colors 0 .. c_b - 1),
  - the q-point parabola P = {(d^2, d) : d in GF(q)} (tag c_b + 1),
  - c_b = (q - 1) / 2 remaining singleton points (tag c_b).

Exact point identity: ((q - 1)/2) * (2q - 1) + q + (q - 1)/2 = q^2.

Algorithm:
  Focused min-conflicts Tabu Search + dynamic (line, color) weighting (PAWS/SWT)
  with deterministic PRNG and periodic restarts over exact-size color swaps on
  R = AG(2, q) \\ P.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys
import time

# Allow importing GF / verify_blocking_sets from sibling script
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gen_t4_odd_q_nearbush import GF, verify_blocking_sets  # noqa: E402


def build_geometry(q: int):
    gf = GF(q)
    q2 = q * q
    c_b = (q - 1) // 2
    lines = gf.ag2_lines()
    n_lines = len(lines)
    parab_set = {gf.x2[d] * q + d for d in range(q)}
    assert len(parab_set) == q
    r_pts = [p for p in range(q2) if p not in parab_set]
    assert len(r_pts) == q2 - q

    pt_lines_mut: list[list[int]] = [[] for _ in range(q2)]
    line_r_pts: list[tuple[int, ...]] = []
    shared_line = [-1] * (q2 * q2)

    for li, line in enumerate(lines):
        r_on_line = []
        for p in line:
            pt_lines_mut[p].append(li)
            if p not in parab_set:
                r_on_line.append(p)
        line_r_pts.append(tuple(r_on_line))
        for i in range(q):
            pi = line[i]
            base = pi * q2
            for j in range(i + 1, q):
                pj = line[j]
                shared_line[base + pj] = li
                shared_line[pj * q2 + pi] = li

    pt_lines = tuple(tuple(ls) for ls in pt_lines_mut)
    return gf, c_b, lines, n_lines, parab_set, r_pts, pt_lines, tuple(line_r_pts), shared_line


def verify_parabola_packing(gf: GF, raw: list[int] | tuple[int, ...]) -> None:
    q = gf.q
    c_b = (q - 1) // 2
    assert len(raw) == q * q
    parab_expected = {gf.x2[d] * q + d for d in range(q)}
    for p in range(q * q):
        if p in parab_expected:
            assert raw[p] == c_b + 1, f"Parabola pt {p} has tag {raw[p]}"
        else:
            assert 0 <= raw[p] <= c_b, f"Non-parabola pt {p} has tag {raw[p]}"
    for c in range(c_b):
        cnt = sum(1 for x in raw if x == c)
        assert cnt == 2 * q - 1, f"BS color {c} has size {cnt} != {2 * q - 1}"
    assert sum(1 for x in raw if x == c_b) == c_b
    verify_blocking_sets(gf, raw, c_b)


def search_parabola_packing(
    q: int,
    seed: int,
    time_limit_secs: float,
    tabu_tenure: int = 9,
    rand_walk_pct: int = 4,
    restart_patience: int = 25000,
) -> dict[str, object]:
    t0 = time.perf_counter()
    rng = random.Random(seed)
    gf, c_b, lines, n_lines, parab_set, r_pts, pt_lines, line_r_pts, shared_line = build_geometry(q)
    q2 = q * q
    bs_size = 2 * q - 1

    # Exact multiset of colors for R = AG(2, q) \ P
    template_colors = []
    for c in range(c_b):
        template_colors.extend([c] * bs_size)
    template_colors.extend([c_b] * c_b)
    assert len(template_colors) == len(r_pts)

    n_slots = n_lines * c_b
    global_best_unc = n_slots
    total_steps = 0
    total_evals = 0
    restarts = 0

    while True:
        if time.perf_counter() - t0 >= time_limit_secs:
            break

        restarts += 1
        # Fresh random partition of R
        perm = list(template_colors)
        rng.shuffle(perm)
        col = [c_b + 1] * q2
        color_pts: list[list[int]] = [[] for _ in range(c_b + 1)]
        pt_pos = [-1] * q2
        for p, c in zip(r_pts, perm):
            col[p] = c
            pt_pos[p] = len(color_pts[c])
            color_pts[c].append(p)

        cnt = [0] * n_slots
        for p in r_pts:
            c = col[p]
            if c < c_b:
                for li in pt_lines[p]:
                    cnt[li * c_b + c] += 1

        unc_list: list[int] = []
        unc_pos = [-1] * n_slots
        for slot, v in enumerate(cnt):
            if v == 0:
                unc_pos[slot] = len(unc_list)
                unc_list.append(slot)

        weights = [1] * n_slots
        tabu = [0] * (q2 * (c_b + 1))

        best_unc_run = len(unc_list)
        if best_unc_run < global_best_unc:
            global_best_unc = best_unc_run
        steps_since_best = 0
        step = 0

        def add_unc(slot: int) -> None:
            unc_pos[slot] = len(unc_list)
            unc_list.append(slot)

        def rem_unc(slot: int) -> None:
            pos = unc_pos[slot]
            last = unc_list.pop()
            if pos < len(unc_list):
                unc_list[pos] = last
                unc_pos[last] = pos
            unc_pos[slot] = -1

        while unc_list:
            if (step & 255) == 0:
                if time.perf_counter() - t0 >= time_limit_secs:
                    break
            if steps_since_best >= restart_patience:
                break

            step += 1
            total_steps += 1
            steps_since_best += 1

            # Pick a random uncovered (line, color) pair
            slot = unc_list[rng.randrange(len(unc_list))]
            li = slot // c_b
            c = slot % c_b

            cand_p1s = line_r_pts[li]
            cand_p2s = color_pts[c]

            best_p1 = -1
            best_p2 = -1
            best_score = 10**9
            best_ties = 0
            fb_p1 = -1
            fb_p2 = -1
            fb_score = 10**9
            found_zero = False
            cur_unc = len(unc_list)

            if rng.randrange(100) < rand_walk_pct:
                best_p1 = cand_p1s[rng.randrange(len(cand_p1s))]
                best_p2 = cand_p2s[rng.randrange(len(cand_p2s))]
            else:
                for p1 in cand_p1s:
                    a = col[p1]
                    # a != c is guaranteed because cnt[li, c] == 0
                    ls1 = pt_lines[p1]
                    base1 = p1 * q2
                    tabu_p1 = tabu[p1 * (c_b + 1) + c] > step

                    # Pre-accumulate p1's contribution ignoring shared line
                    a_lt_cb = a < c_b
                    for p2 in cand_p2s:
                        total_evals += 1
                        s_line = shared_line[base1 + p2]
                        du = 0
                        dw = 0

                        for l1 in ls1:
                            if l1 == s_line:
                                continue
                            b_idx = l1 * c_b
                            if a_lt_cb and cnt[b_idx + a] == 1:
                                du += 1
                                dw += weights[b_idx + a]
                            if cnt[b_idx + c] == 0:
                                du -= 1
                                dw -= weights[b_idx + c]

                        for l2 in pt_lines[p2]:
                            if l2 == s_line:
                                continue
                            b_idx = l2 * c_b
                            if cnt[b_idx + c] == 1:
                                du += 1
                                dw += weights[b_idx + c]
                            if a_lt_cb and cnt[b_idx + a] == 0:
                                du -= 1
                                dw -= weights[b_idx + a]

                        new_unc = cur_unc + du
                        if new_unc == 0:
                            best_p1 = p1
                            best_p2 = p2
                            found_zero = True
                            break

                        score = dw * 4 + du
                        if score < fb_score:
                            fb_score = score
                            fb_p1 = p1
                            fb_p2 = p2

                        is_tabu = tabu_p1 or (tabu[p2 * (c_b + 1) + a] > step)
                        aspire = new_unc < best_unc_run
                        if (not is_tabu) or aspire:
                            if score < best_score:
                                best_score = score
                                best_p1 = p1
                                best_p2 = p2
                                best_ties = 1
                            elif score == best_score:
                                best_ties += 1
                                if rng.randrange(best_ties) == 0:
                                    best_p1 = p1
                                    best_p2 = p2
                    if found_zero:
                        break

                if best_p1 < 0:
                    best_p1 = fb_p1
                    best_p2 = fb_p2

            # Apply swap (best_p1 <-> best_p2)
            p1, p2 = best_p1, best_p2
            a = col[p1]
            assert col[p2] == c and a != c
            s_line = shared_line[p1 * q2 + p2]
            a_lt_cb = a < c_b

            for l1 in pt_lines[p1]:
                if l1 == s_line:
                    continue
                b_idx = l1 * c_b
                if a_lt_cb:
                    idx_a = b_idx + a
                    cnt[idx_a] -= 1
                    if cnt[idx_a] == 0:
                        add_unc(idx_a)
                idx_c = b_idx + c
                if cnt[idx_c] == 0:
                    rem_unc(idx_c)
                cnt[idx_c] += 1

            for l2 in pt_lines[p2]:
                if l2 == s_line:
                    continue
                b_idx = l2 * c_b
                idx_c = b_idx + c
                cnt[idx_c] -= 1
                if cnt[idx_c] == 0:
                    add_unc(idx_c)
                if a_lt_cb:
                    idx_a = b_idx + a
                    if cnt[idx_a] == 0:
                        rem_unc(idx_a)
                    cnt[idx_a] += 1

            # Update color arrays and positions
            pos1 = pt_pos[p1]
            pos2 = pt_pos[p2]
            color_pts[a][pos1] = p2
            color_pts[c][pos2] = p1
            pt_pos[p2] = pos1
            pt_pos[p1] = pos2
            col[p1] = c
            col[p2] = a

            ten = tabu_tenure + rng.randrange(5)
            tabu[p1 * (c_b + 1) + a] = step + ten
            tabu[p2 * (c_b + 1) + c] = step + ten

            if len(unc_list) < best_unc_run:
                best_unc_run = len(unc_list)
                steps_since_best = 0
                if best_unc_run < global_best_unc:
                    global_best_unc = best_unc_run

            if (step & 127) == 0:
                for u_slot in unc_list:
                    if weights[u_slot] < 12:
                        weights[u_slot] += 1
            if (step & 1023) == 0:
                for idx_w in range(n_slots):
                    if weights[idx_w] > 1:
                        weights[idx_w] -= 1

        if not unc_list:
            verify_parabola_packing(gf, col)
            elapsed = time.perf_counter() - t0
            sha = hashlib.sha256(",".join(str(x) for x in col).encode("ascii")).hexdigest()
            return {
                "q": q,
                "found": True,
                "seed": seed,
                "elapsed_secs": round(elapsed, 4),
                "restarts": restarts,
                "steps": total_steps,
                "evals": total_evals,
                "best_unc": 0,
                "sha256": sha,
                "raw": col,
            }

    elapsed = time.perf_counter() - t0
    return {
        "q": q,
        "found": False,
        "seed": seed,
        "elapsed_secs": round(elapsed, 4),
        "restarts": restarts,
        "steps": total_steps,
        "evals": total_evals,
        "best_unc": global_best_unc,
        "sha256": None,
        "raw": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Explicit reproducible search for AG(2, q) parabola + minimal BS packings"
    )
    parser.add_argument("--q", type=int, choices=[7, 9, 11, 13], required=True)
    parser.add_argument("--seed", type=int, default=5401)
    parser.add_argument("--time-limit-secs", type=float, default=30.0)
    parser.add_argument("--tabu-tenure", type=int, default=9)
    parser.add_argument("--rand-walk-pct", type=int, default=4)
    parser.add_argument("--restart-patience", type=int, default=25000)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    res = search_parabola_packing(
        q=args.q,
        seed=args.seed,
        time_limit_secs=args.time_limit_secs,
        tabu_tenure=args.tabu_tenure,
        rand_walk_pct=args.rand_walk_pct,
        restart_patience=args.restart_patience,
    )
    rate = res["evals"] / max(res["elapsed_secs"], 1e-6)
    status = "FOUND" if res["found"] else "NOT_FOUND"
    print(
        f"[parabola_pack q={args.q} seed={args.seed}] {status} "
        f"best_unc={res['best_unc']} restarts={res['restarts']} "
        f"steps={res['steps']} evals={res['evals']} ({rate:.0f} evals/s) "
        f"elapsed={res['elapsed_secs']:.3f}s sha256={res['sha256']}"
    )
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
