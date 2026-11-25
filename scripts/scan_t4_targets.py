#!/usr/bin/env python3
"""Systematic Covering Array Target Scanner for t=4 (v=3..14) and Phase-5 Bonus Tracks.

Pure Python stdlib-only scanner reading official `chrispbsmolen/ca-tools` tables:
  - table/ca_table.csv.gz
  - table/ca_frame.csv
  - table/derived.csv
  - (optional) table/priority.csv, table/lower_bounds.csv, table/references.csv

Computes:
  1. Effective best upper bound N_eff = min(ca_table, ca_frame, derived) with exact
     monotonic stair-step envelope (N_eff(k) = min_{k' >= k} N(k')).
  2. t=4, v=3..14 analysis: N_eff / v^4, Bush-OA distance, NON_PP (v in {6,10,12,14})
     and NEAR_BUSH (k = v+2..2v for prime powers) tags, 2026 contributor coverage
     (Sitjar/Bai/Canli/Smolen/LaVerdi), and calibrated 2-vCPU verifier cost/runtime.
  3. Bonus A: t=3, v in {15, 21, 22} (strictly outside q+1 / PGL(2,q)+CCL).
  4. Bonus B: t=5, v=12, k=6..16 (Mathieu group M_12 orbit-capacity audit).
  5. Transparent Top-15 candidate ranking based on hard metrics only.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PRIME_POWERS_T4 = {3, 4, 5, 7, 8, 9, 11, 13}
NON_PP_T4 = {6, 10, 12, 14}
VALID_TIERS = {"VERIFIED", "CITED", "SCREENED"}

# Calibrated from measured STATUS.md dual-verification timings on this VM
# (Intel Xeon @ 2.30 GHz, 2 vCPUs, 7.8 GiB RAM):
# - verify_independent.py (1T Python set(zip(...))): ~4.6e6 row_ops/s at t=3
#   -> conservative scaling by strength t: t=3: 4.5e6, t=4: 3.5e6, t=5: 2.8e6
# - ca_verify (2T C AVX2 bit-planes): ~5.0e8 plane-row-ops/s
PY_OPS_PER_SEC = {2: 5.5e6, 3: 4.5e6, 4: 3.5e6, 5: 2.8e6, 6: 2.2e6}
CA_VERIFY_OPS_PER_SEC = 5.0e8


def bush_oa_width_t4(v: int) -> int | None:
    """Return known OA(v^4; 4, k, v) max column count k for t=4."""
    if v == 3:
        return 5  # OA(81; 4, 5, 3), linear parity-check MDS code
    if v in PRIME_POWERS_T4:
        return v + 1  # Bush / Reed-Solomon OA(q^4; 4, q+1, q) for q >= 4
    return None  # Non-prime-power (trivial parity OA at k=5 only)


def estimate_verify_times(t: int, k: int, v: int, n_rows: int) -> dict[str, Any]:
    """Estimate ca_verify (2T C/AVX2) and verify_independent.py (1T Python) runtimes."""
    ckt = math.comb(k, t)
    ck_tm1 = math.comb(k, t - 1)
    tuple_cost = ckt * (v ** t)
    row_ops = ckt * n_rows

    py_rate = PY_OPS_PER_SEC.get(t, 2.5e6)
    est_py_s = row_ops / py_rate

    # ca_verify processes C(k, t-1) (t-1)-sets; per (t-1)-set ~ N * v * ceil(k/64) word ops
    words_k = max(1, (k + 63) // 64)
    plane_ops = ck_tm1 * n_rows * v * words_k
    est_ca_s = max(0.005, plane_ops / CA_VERIFY_OPS_PER_SEC)

    est_dual_s = est_ca_s + est_py_s
    # Rough plain-text file size in MB: N * k * (digits(v-1) + 1)
    bytes_per_entry = len(str(v - 1)) + 1
    est_file_mb = (n_rows * k * bytes_per_entry) / (1024 * 1024)

    return {
        "ckt": ckt,
        "tuple_cost": tuple_cost,
        "row_ops": row_ops,
        "est_ca_s": round(est_ca_s, 3),
        "est_py_s": round(est_py_s, 3),
        "est_dual_s": round(est_dual_s, 3),
        "dual_60s": est_dual_s <= 60.0,
        "ca_60s": est_ca_s <= 60.0,
        "est_file_mb": round(est_file_mb, 2),
    }


def load_priority_map(data_dir: Path) -> dict[str, str]:
    """Map 'pr-<num>' -> contributor slug from table/priority.csv if available."""
    pr_map: dict[str, str] = {}
    p = data_dir / "priority.csv"
    if not p.exists():
        return pr_map
    with open(p, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ev = r.get("evidence", "")
            m = re.search(r"/pull/(\d+)", ev)
            if m:
                pr_map[f"pr-{m.group(1)}"] = r["slug"]
    return pr_map


def classify_contributor(row: dict[str, str], pr_map: dict[str, str]) -> str:
    """Return a clean contributor/origin label for a ca_table row."""
    snap = row.get("snapshot_id", "")
    notes = row.get("notes", "")
    src_det = row.get("source_detail", "")
    entered = row.get("entered", "")

    if snap in pr_map:
        slug = pr_map[snap]
        if slug.startswith("sitjar"):
            return "Sitjar-2026"
        if slug.startswith("bai-xundi"):
            return "Bai-2026"
        if slug.startswith("canli"):
            return "Canli-2026"
        if slug.startswith("laverdi"):
            return "LaVerdi-2026"
        if slug.startswith("baig"):
            return "Baig-2026"
        return slug

    low = (snap + " " + notes + " " + src_det).lower()
    if "sitjar" in low:
        return "Sitjar-2026"
    if "bai" in low and entered >= "2026-10-01":
        return "Bai-2026"
    if "canli" in low or "quantavane" in low:
        return "Canli-2026"
    if "smolen" in low:
        return "Smolen-2026"
    if "laverdi" in low:
        return "LaVerdi-2026"
    if "baig" in low:
        return "Baig-2026"
    if snap == "colbourn-2024-11-ug" or row.get("source_id") == "S1":
        return "Colbourn-2024(S1)"
    if entered >= "2026-10-01":
        return f"Other-2026({snap or row.get('source_id', '?')})"
    return row.get("source_id", "unknown")


def load_tables(data_dir: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    with gzip.open(data_dir / "ca_table.csv.gz", "rt", encoding="utf-8") as f:
        ca_table = list(csv.DictReader(f))
    with open(data_dir / "ca_frame.csv", "rt", encoding="utf-8") as f:
        ca_frame = list(csv.DictReader(f))
    with open(data_dir / "derived.csv", "rt", encoding="utf-8") as f:
        derived = list(csv.DictReader(f))
    return ca_table, ca_frame, derived


def build_envelope(
    t: int,
    v: int,
    k_range: range,
    ca_table: list[dict[str, str]],
    ca_frame: list[dict[str, str]],
    derived: list[dict[str, str]],
    pr_map: dict[str, str],
) -> list[dict[str, Any]]:
    """Build exact monotonic stair-step effective best table for (t, v) over k_range."""
    # Gather per-source raw entries for (t, v)
    tier_prio = {"VERIFIED": 0, "SCREENED": 1, "CITED": 2}

    ct_rows = [
        r for r in ca_table
        if int(r["t"]) == t and int(r["v"]) == v and r["tier"] in VALID_TIERS
    ]
    cf_rows = [r for r in ca_frame if int(r["t"]) == t and int(r["v"]) == v]
    dv_rows = [r for r in derived if int(r["t"]) == t and int(r["v"]) == v]

    # Map k -> best entry in each source (at exact k)
    ct_by_k: dict[int, dict[str, str]] = {}
    for r in ct_rows:
        k = int(r["k"])
        N = int(r["N"])
        cur = ct_by_k.get(k)
        key_new = (N, tier_prio.get(r["tier"], 9))
        if cur is None or key_new < (int(cur["N"]), tier_prio.get(cur["tier"], 9)):
            ct_by_k[k] = r

    cf_by_k: dict[int, dict[str, str]] = {}
    for r in cf_rows:
        k = int(r["k"])
        N = int(r["N"])
        cur = cf_by_k.get(k)
        if cur is None or N < int(cur["N"]):
            cf_by_k[k] = r

    dv_by_k: dict[int, dict[str, str]] = {}
    for r in dv_rows:
        k = int(r["k"])
        N = int(r["N"])
        cur = dv_by_k.get(k)
        if cur is None or N < int(cur["N"]):
            dv_by_k[k] = r

    all_ks = sorted(set(ct_by_k) | set(cf_by_k) | set(dv_by_k))
    if not all_ks:
        return []

    # Helper: stair-step min for k' >= k
    def stair_min(mapping: dict[int, dict[str, str]], k_query: int, is_ct: bool = False) -> tuple[int, int, dict[str, str]] | None:
        best = None
        for kp, r in mapping.items():
            if kp < k_query:
                continue
            N = int(r["N"])
            tp = tier_prio.get(r.get("tier", "CITED"), 9) if is_ct else (0 if r.get("tier") == "VERIFIED" else 2)
            cand = (N, tp, kp)
            if best is None or cand < best[0]:
                best = (cand, N, kp, r)
        if best is None:
            return None
        return best[1], best[2], best[3]

    results: list[dict[str, Any]] = []
    for k in k_range:
        st_ct = stair_min(ct_by_k, k, is_ct=True)
        st_cf = stair_min(cf_by_k, k, is_ct=False)
        st_dv = stair_min(dv_by_k, k, is_ct=False)

        cands: list[tuple[int, int, str, int, dict[str, str]]] = []
        if st_ct is not None:
            cands.append((st_ct[0], 0 if st_ct[2]["tier"] == "VERIFIED" else 2, "ca_table", st_ct[1], st_ct[2]))
        if st_cf is not None:
            cands.append((st_cf[0], 1 if st_cf[2]["tier"] == "VERIFIED" else 3, "ca_frame", st_cf[1], st_cf[2]))
        if st_dv is not None:
            cands.append((st_dv[0], 4, "derived", st_dv[1], st_dv[2]))

        if not cands:
            continue
        cands.sort(key=lambda x: (x[0], x[1], x[3]))
        n_eff, _, win_src, win_k, win_row = cands[0]

        # Resolve tier, get, source_id, contributor, construction
        cf_hit = st_cf[2] if (st_cf is not None and st_cf[0] == n_eff) else None
        ct_hit = st_ct[2] if (st_ct is not None and st_ct[0] == n_eff) else None
        dv_hit = st_dv[2] if (st_dv is not None and st_dv[0] == n_eff) else None

        if win_src == "derived":
            tier = "DERIVED"
            get_flag = "derived"
            source_id = f"derived:{win_row['law']}"
            contributor = f"derived({win_row['law']})"
            construction = win_row.get("arithmetic", "")
            entered = ""
        else:
            # Prefer verified status if either ca_table or ca_frame verifies N_eff
            tier = "CITED"
            if (ct_hit and ct_hit["tier"] == "VERIFIED") or (cf_hit and cf_hit["tier"] == "VERIFIED"):
                tier = "VERIFIED"
            elif ct_hit and ct_hit["tier"] == "SCREENED":
                tier = "SCREENED"
            get_flag = cf_hit["get"] if cf_hit else ("file" if tier == "VERIFIED" else "none")
            source_id = ct_hit["source_id"] if ct_hit else (cf_hit["id"] if cf_hit else "?")
            contributor = classify_contributor(ct_hit, pr_map) if ct_hit else (cf_hit["family"] if cf_hit else "?")
            construction = (cf_hit["construction"] if cf_hit else "") or (ct_hit["construction"] if ct_hit else "")
            entered = (ct_hit["entered"] if ct_hit else "") or (cf_hit["entered"] if cf_hit else "")

        ver = estimate_verify_times(t, k, v, n_eff)
        results.append({
            "t": t,
            "v": v,
            "k": k,
            "N_eff": n_eff,
            "N_table": st_ct[0] if st_ct else None,
            "N_frame": st_cf[0] if st_cf else None,
            "N_derived": st_dv[0] if st_dv else None,
            "win_src": win_src,
            "k_witness": win_k,
            "tier": tier,
            "get": get_flag,
            "source_id": source_id,
            "contributor": contributor,
            "family": cf_hit["family"] if cf_hit else "",
            "construction": construction,
            "entered": entered,
            "ratio_vt": round(n_eff / (v ** t), 4),
            "derived_strictly_better": (dv_hit is not None and (st_ct is None or st_dv[0] < st_ct[0])),
            **ver,
        })

    # Compute jump ΔN from k-1 and plateau width (count of contiguous k with same N_eff)
    for i, row in enumerate(results):
        if i == 0:
            row["delta_N"] = 0
        else:
            row["delta_N"] = row["N_eff"] - results[i - 1]["N_eff"]
        # Plateau width across scanned range
        n_cur = row["N_eff"]
        lo = i
        while lo > 0 and results[lo - 1]["N_eff"] == n_cur:
            lo -= 1
        hi = i
        while hi + 1 < len(results) and results[hi + 1]["N_eff"] == n_cur:
            hi += 1
        row["plateau_width"] = hi - lo + 1
        row["plateau_k_max"] = results[hi]["k"]
        row["is_plateau_right_edge"] = (i == hi)
        row["is_plateau_left_edge"] = (i == lo)

    return results


def audit_2026_coverage_t4(
    ca_table: list[dict[str, str]],
    ca_frame: list[dict[str, str]],
    pr_map: dict[str, str],
) -> dict[int, dict[str, Any]]:
    """Quantify 2026 contributor dominance vs. untouched CITED niches for t=4, v=3..14."""
    out: dict[int, dict[str, Any]] = {}
    for v in range(3, 15):
        cf_v = [r for r in ca_frame if int(r["t"]) == 4 and int(r["v"]) == v]
        ct_2026 = [
            r for r in ca_table
            if int(r["t"]) == 4 and int(r["v"]) == v and r["entered"] >= "2026-10-01" and r["tier"] in VALID_TIERS
        ]
        by_contrib = Counter(classify_contributor(r, pr_map) for r in ct_2026)

        # Scope to k <= 25 (practical low-k search regime)
        cf_low = [r for r in cf_v if int(r["k"]) <= 25]
        ver_low = sum(1 for r in cf_low if r["tier"] == "VERIFIED")
        cit_none_low = [int(r["k"]) for r in cf_low if r["tier"] == "CITED" and r["get"] == "none"]
        recent_low_ks = sorted({int(r["k"]) for r in ct_2026 if int(r["k"]) <= 25})
        out[v] = {
            "total_frame": len(cf_v),
            "low_k_frame": len(cf_low),
            "low_k_verified": ver_low,
            "low_k_cited_none_ks": sorted(cit_none_low),
            "recent_2026_total": len(ct_2026),
            "recent_2026_low_ks": recent_low_ks,
            "contributors_2026": dict(by_contrib.most_common(6)),
        }
    return out


def score_t4_candidates(all_t4_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank t=4 target cells transparently by hard metrics (no hype).

    Criteria (additive, 0..100 scale):
      - Openness (CITED + get=none): +25; VERIFIED: +5 (still improvable if huge jump)
      - Headroom (N_eff / v^4): up to +25 (scales with ratio above 1.25x)
      - Structural gap (jump ΔN / v^4 and plateau width >= 2): up to +20
      - Target class bonus: NON_PP (v in {6,10,12,14}) or NEAR_BUSH (k=v+2..2v): +15
      - 2-vCPU Dual-Verification speed (<=10s: +15, <=30s: +11, <=60s: +7)
      - Penalty if dominated by recent 2026 Sitjar/Bai/LaVerdi/Smolen VERIFIED row: -12
    Filters:
      - Exclude exact OAs (N_eff == v^4)
      - Require dual_60s == True (both ca_verify and verify_independent.py <= 60s)
      - Prefer plateau left-edge (where jump happens, maximal headroom per k) or right-edge
        (strongest single array covering the whole plateau), deduplicating same (v, N_eff)
        plateau to keep Top-15 diverse (reporting the best representative k for each plateau).
    """
    scored: list[dict[str, Any]] = []
    for r in all_t4_rows:
        if r["N_eff"] <= r["v"] ** 4:
            continue
        if not r["dual_60s"]:
            continue

        score = 0.0
        # 1. Openness
        if r["tier"] == "CITED" and r["get"] == "none":
            score += 25.0
        elif r["tier"] == "CITED":
            score += 14.0
        else:
            score += 5.0

        # 2. Ratio headroom above v^4
        ratio = r["ratio_vt"]
        score += min(25.0, max(0.0, (ratio - 1.20) * 16.0))

        # 3. Jump & plateau signal
        jump_ratio = r["delta_N"] / (r["v"] ** 4)
        score += min(12.0, jump_ratio * 22.0)
        if r["plateau_width"] >= 2:
            score += min(8.0, (r["plateau_width"] - 1) * 2.0)

        # 4. Target class (NON_PP or NEAR_BUSH)
        tags = r["tags"]
        if "NON_PP" in tags or "NEAR_BUSH" in tags:
            score += 15.0

        # 5. Dual-verification speed on 2 vCPUs
        ds = r["est_dual_s"]
        if ds <= 5.0:
            score += 15.0
        elif ds <= 15.0:
            score += 12.0
        elif ds <= 35.0:
            score += 9.0
        else:
            score += 6.0

        # 6. Saturation penalty for fresh 2026 verified rows
        if r["tier"] == "VERIFIED" and r["entered"] >= "2026-10-01":
            score -= 12.0

        item = dict(r)
        item["score"] = round(score, 1)
        scored.append(item)

    # Deduplicate by (v, N_eff) plateau: keep the highest-scoring k on each plateau
    # (note: left edge captures the big jump; we also record full plateau k-span!)
    by_plateau: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for item in scored:
        by_plateau[(item["v"], item["N_eff"])].append(item)

    reps: list[dict[str, Any]] = []
    for (v, n_eff), grp in by_plateau.items():
        ks = sorted(x["k"] for x in grp)
        best = max(grp, key=lambda x: (x["score"], -x["est_dual_s"], x["k"]))
        best = dict(best)
        best["plateau_span"] = f"{ks[0]}..{ks[-1]}" if len(ks) > 1 else str(ks[0])
        reps.append(best)

    reps.sort(key=lambda x: (-x["score"], x["est_dual_s"], x["v"], x["k"]))
    return reps


def analyze_m12_t5_v12(
    ca_table: list[dict[str, str]],
    ca_frame: list[dict[str, str]],
    derived: list[dict[str, str]],
    pr_map: dict[str, str],
) -> list[dict[str, Any]]:
    """Audit t=5, v=12, k=6..16 against Mathieu group M_12 orbit structure.

    M_12 is sharply 5-transitive on 12 symbols: |M_12| = 12*11*10*9*8 = 95,040.
    Orbit sizes on {0..11}^5 by number of distinct symbols m in a 5-tuple:
      - m=5 (1 pattern, S(5,5)=1):     size 95,040  (95,040 tuples)
      - m=4 (10 patterns, S(5,4)=10):  size 11,880  (118,800 tuples)
      - m=3 (25 patterns, S(5,3)=25):  size 1,320   (33,000 tuples)
      - m=2 (15 patterns, S(5,2)=15):  size 132     (1,980 tuples)
      - m=1 (1 pattern, S(5,1)=1):     size 12      (12 tuples)
    Sum: 95040 + 118800 + 33000 + 1980 + 12 = 248,832 = 12^5.
    """
    env = build_envelope(5, 12, range(6, 17), ca_table, ca_frame, derived, pr_map)

    for row in env:
        k = row["k"]
        ck5 = math.comb(k, 5)
        # Minimum 5-symbol starter rows (orbit size 95,040):
        # 1 starter with all distinct symbols covers 100% of 5-sym for k <= 12.
        # For k=13..16, a single starter repeats some symbols, so at least 2 starters
        # are needed to cover all C(k,5) 5-sets (e.g. two complementary repeat blocks).
        a5_min = 1 if k <= 12 else 2

        # Exact max 4-sym pattern-slots covered by a single pure 4-symbol starter row
        # (orbit size 11,880) with balanced partition of k into 4 parts (n0,n1,n2,n3):
        # A 5-set hits a 4-sym pattern iff it picks 2 from one part and 1 from each of the other 3.
        q, rem = divmod(k, 4)
        parts = [q + (1 if i < rem else 0) for i in range(4)]
        max_4sym_hits_per_starter = sum(
            math.comb(parts[i], 2) * math.prod(parts[j] for j in range(4) if j != i)
            for i in range(4)
        )
        total_4sym_slots = ck5 * 10  # S(5,4) = 10 patterns per 5-set
        # Note: if k <= 12, the A5=1 distinct-symbol starter covers ZERO 4-sym slots!
        # If k > 12, A5=2 starters with repeats also cover some 4-sym slots; we compute
        # the pure 4-sym starter count B4_pure_lb assuming 0 overlap from A5 (exact for k<=12).
        if k <= 12:
            b4_min = math.ceil(total_4sym_slots / max_4sym_hits_per_starter) if max_4sym_hits_per_starter > 0 else 0
            # Lower bound on rows from 5-sym + 4-sym + minimal 3/2/1-sym (at least 33000+1980+12 = 34992 tuples,
            # though 3-sym starters cover multiple 5-sets at once; conservative floor for 3/2/1-sym is >= 25*1320 + 15*132 + 12
            # ONLY if each 3-sym starter hits 1 pattern per 5-set; actually a single 3-sym starter covers at most 1 pattern per 5-set
            # out of 25 patterns, so >= 25 starters of size 1320 are ALWAYS needed even for k=5, i.e., >= 33,000 rows!).
            # Specifically, for a fixed 5-set, each 3-sym starter row has a single partition pattern -> covers <= 1 of 25 patterns!
            # Wait: a 3-sym starter row on k columns covers at most 1 of the 25 3-sym patterns on ANY single 5-set!
            # So ANY 5-set requires >= 25 distinct 3-sym orbits (25*1320 = 33,000), >= 15 2-sym (1,980), >= 1 1-sym (12)!
            # (Unless covered by 4-sym starters, which can cover 3-sym patterns too!)
            m12_54_only_lb = a5_min * 95040 + b4_min * 11880
        else:
            # For k > 12, a 5-sym starter with k-12 repeats covers some 4-sym slots:
            # Specifically, with (k-11) copies of symbol 0 and 11 singletons, a 5-set hits 4-sym iff
            # it picks 2 copies of symbol 0 and 3 of the 11 singletons: C(k-11, 2) * C(11, 3) slots.
            # With 2 such starters (disjoint repeat blocks), <= 2 * C(k-11, 2) * C(11, 3) slots covered.
            bonus_4sym = 2 * math.comb(k - 11, 2) * math.comb(11, 3)
            rem_4sym = max(0, total_4sym_slots - bonus_4sym)
            b4_min = math.ceil(rem_4sym / max_4sym_hits_per_starter) if max_4sym_hits_per_starter > 0 else 0
            m12_54_only_lb = a5_min * 95040 + b4_min * 11880

        row["m12_a5_min"] = a5_min
        row["m12_b4_min"] = b4_min
        row["m12_54_only_lb"] = m12_54_only_lb
        row["m12_margin_vs_table"] = row["N_eff"] - m12_54_only_lb

    return env


def main() -> int:
    parser = argparse.ArgumentParser(description="Systematic t=4 (and bonus t=3/t=5) target scanner.")
    parser.add_argument("--data-dir", type=Path, required=True, help="Directory with ca-tools CSVs")
    parser.add_argument("--commit", type=str, default="083a0933e3561625b2aad9bd19035ad76d783f03")
    parser.add_argument("--k-max-t4", type=int, default=28, help="Max k to scan for t=4")
    parser.add_argument("--out-json", type=Path, default=None, help="Optional JSON output path")
    args = parser.parse_args()

    ca_table, ca_frame, derived = load_tables(args.data_dir)
    pr_map = load_priority_map(args.data_dir)

    # 1. t=4, v=3..14 scan
    t4_by_v: dict[int, list[dict[str, Any]]] = {}
    all_t4_rows: list[dict[str, Any]] = []
    for v in range(3, 15):
        k_oa = bush_oa_width_t4(v)
        k_hi = max(args.k_max_t4, 2 * v + 2)
        env = build_envelope(4, v, range(5, k_hi + 1), ca_table, ca_frame, derived, pr_map)
        for r in env:
            tags: list[str] = []
            if v in NON_PP_T4:
                tags.append("NON_PP")
            if k_oa is not None:
                r["k_oa"] = k_oa
                r["dist_oa"] = r["k"] - k_oa
                if (v == 3 and r["k"] == 6) or (v >= 4 and v + 2 <= r["k"] <= 2 * v):
                    tags.append("NEAR_BUSH")
            else:
                r["k_oa"] = None
                r["dist_oa"] = None
            r["tags"] = tags
        t4_by_v[v] = env
        all_t4_rows.extend(env)

    cov_2026 = audit_2026_coverage_t4(ca_table, ca_frame, pr_map)
    ranked_t4 = score_t4_candidates(all_t4_rows)

    # 2. Bonus A: t=3, v in {15, 21, 22}
    bonus_t3: dict[int, list[dict[str, Any]]] = {}
    for v in (15, 21, 22):
        bonus_t3[v] = build_envelope(3, v, range(5, 41), ca_table, ca_frame, derived, pr_map)

    # 3. Bonus B: t=5, v=12, k=6..16 (M_12)
    bonus_m12 = analyze_m12_t5_v12(ca_table, ca_frame, derived, pr_map)

    # Print concise summary to stdout
    print(f"=== Phase 5 Recon Target Scan (ca-tools @ {args.commit[:7]}) ===")
    print(f"Scanned t=4 v=3..14 cells: {len(all_t4_rows)} (dual_60s=True: {sum(1 for r in all_t4_rows if r['dual_60s'])})")
    print("\n--- 2026 Coverage Audit for t=4 (v=3..14) ---")
    for v in range(3, 15):
        c = cov_2026[v]
        tag = "NON_PP" if v in NON_PP_T4 else "PP"
        print(
            f"v={v:2d} [{tag:6s}]: low_k_VER={c['low_k_verified']:2d}/{c['low_k_frame']:2d} | "
            f"2026_rows={c['recent_2026_total']:2d} | open_CITED(k<=25)={c['low_k_cited_none_ks'][:10]} | "
            f"2026_by={c['contributors_2026']}"
        )

    print("\n--- TOP 20 CANDIDATES (t=4, v=3..14, dual_verify <= 60s, deduplicated by plateau) ---")
    hdr = f"{'#':>2} {'Score':>5} {'Cell':<11} {'Span':<7} {'N_eff':>6} {'x v^4':>6} {'dN':>6} {'Tier/Get':<11} {'Tags':<10} {'C(k,4)*v^4':>12} {'CA/PY s':>11} {'Origin'}"
    print(hdr)
    for idx, r in enumerate(ranked_t4[:20], 1):
        cell = f"(4,{r['k']},{r['v']})"
        tg = f"{r['tier'][:3]}/{r['get'][:4]}"
        tags = ",".join(r["tags"]) or "-"
        times = f"{r['est_ca_s']:.2f}/{r['est_py_s']:.1f}"
        print(
            f"{idx:2d} {r['score']:5.1f} {cell:<11} {r['plateau_span']:<7} {r['N_eff']:6d} "
            f"{r['ratio_vt']:6.2f} {r['delta_N']:+6d} {tg:<11} {tags:<10} {r['tuple_cost']:12,d} "
            f"{times:>11} {r['source_id']}:{r['family'] or r['construction'][:22]}"
        )

    print("\n--- BONUS A: t=3, v in {15, 21, 22} largest CITED gaps (dual_60s=True) ---")
    for v in (15, 21, 22):
        cited_gaps = [
            r for r in bonus_t3[v]
            if r["tier"] == "CITED" and r["get"] == "none" and r["N_eff"] > v ** 3
        ]
        # Group by plateau
        seen_n = set()
        print(f"  v={v} (v^3={v**3}):")
        for r in cited_gaps:
            if r["N_eff"] in seen_n:
                continue
            seen_n.add(r["N_eff"])
            if r["ratio_vt"] >= 1.45 or r["delta_N"] >= 500:
                print(
                    f"    k={r['k']:2d}..{r['plateau_k_max']:2d} (w={r['plateau_width']:2d}) "
                    f"N={r['N_eff']:6d} ({r['ratio_vt']:.2f}x) dN={r['delta_N']:+5d} "
                    f"dual={r['est_dual_s']:5.1f}s ({'OK' if r['dual_60s'] else 'SLOW'}) "
                    f"fam={r['family']} cons={r['construction'][:35]}"
                )

    print("\n--- BONUS B: t=5, v=12, k=6..16 (M_12 audit) ---")
    for r in bonus_m12:
        print(
            f"  k={r['k']:2d} N={r['N_eff']:7d} ({r['ratio_vt']:.2f}x) {r['tier'][:3]}/{r['get'][:4]} "
            f"C*v^5={r['tuple_cost']:>13,d} ca={r['est_ca_s']:5.1f}s py={r['est_py_s']:7.1f}s | "
            f"M12_lb(5+4sym)={r['m12_54_only_lb']:>7d} (A5={r['m12_a5_min']},B4>={r['m12_b4_min']:2d}, "
            f"margin={r['m12_margin_vs_table']:+7d}) | {r['family']}:{r['construction'][:28]}"
        )

    if args.out_json is not None:
        payload = {
            "commit": args.commit,
            "t4_by_v": {str(v): rows for v, rows in t4_by_v.items()},
            "cov_2026": {str(v): c for v, c in cov_2026.items()},
            "ranked_t4_top25": ranked_t4[:25],
            "bonus_t3": {str(v): rows for v, rows in bonus_t3.items()},
            "bonus_m12": bonus_m12,
        }
        args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote structured JSON to {args.out_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
