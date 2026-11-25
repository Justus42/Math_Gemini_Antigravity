#!/usr/bin/env python3
"""
Systematic t=3 Covering Array Target Scan (v=4..14, k=6..35)
against chrispbsmolen/ca-tools (table/ca_table.csv.gz).

Pure Python (stdlib only). Read-only analysis script; does not touch verifiers/.
"""

import argparse
import csv
import gzip
import json
import math
import os
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class GroupSpec:
    v: int
    name: str
    order: int
    bin_sizes: Tuple[int, ...]
    orbs_3sym: int
    orbs_2sym: int
    is_reference: bool = False

    @property
    def orbs_per_triple(self) -> int:
        return self.orbs_3sym + self.orbs_2sym


# Exact permutation-group orbit counts on {0..v-1}^3 (verified directly by group action):
#   orbs_2sym = 3 for every 2-transitive group ((a,a,b), (a,b,a), (b,a,a)).
#   orbs_3sym = number of orbits on ordered triples of 3 distinct symbols.
GROUP_SPECS: List[GroupSpec] = [
    # Reference groups (sanity check only; excluded from Top 15)
    GroupSpec(5, "AGL(1,5)", 20, (10,), 3, 3, is_reference=True),
    GroupSpec(6, "PSL(2,5)", 60, (30,), 2, 3, is_reference=True),
    GroupSpec(6, "PGL(2,5)", 120, (30,), 1, 3, is_reference=True),
    # Target groups v=7..14
    GroupSpec(7, "PSL(3,2)", 168, (42, 21), 2, 3),
    GroupSpec(7, "AGL(1,7)", 42, (21,), 5, 3),
    GroupSpec(8, "PSL(2,7)", 168, (56, 28), 2, 3),
    GroupSpec(8, "PGL(2,7)", 336, (56,), 1, 3),
    GroupSpec(8, "AGammaL(1,8)", 168, (56,), 2, 3),
    GroupSpec(9, "PSL(2,8)", 504, (72, 36), 1, 3),
    GroupSpec(9, "ASL(2,3)", 216, (72,), 3, 3),
    GroupSpec(9, "AGammaL(1,9)", 144, (72,), 4, 3),
    GroupSpec(10, "PSL(2,9)", 360, (90, 45), 2, 3),
    GroupSpec(10, "PGL(2,9)", 720, (90,), 1, 3),
    GroupSpec(11, "PSL(2,11)_11", 660, (110,), 2, 3),
    GroupSpec(11, "AGL(1,11)", 110, (55,), 9, 3),
    GroupSpec(12, "PSL(2,11)", 660, (132, 66), 2, 3),
    GroupSpec(12, "PGL(2,11)", 1320, (132,), 1, 3),
    GroupSpec(13, "AGL(1,13)", 156, (78,), 11, 3),
    GroupSpec(14, "PSL(2,13)", 1092, (182, 91), 2, 3),
]

GROUP_CONSTR_KEYWORDS = (
    "psl(",
    "pgl(",
    "agl(",
    "group construction",
    "group-orbit",
    "ordered design",
    "ck_nrb",
    "starter",
)

CK_DOUBLING_KEYWORDS = (
    "chateauneuf-kreher doubling",
    "ck_doubling",
)


def pareto_f3_f2(k: int, v: int) -> List[Tuple[int, int]]:
    """
    Exact upper concave hull of (f3, f2) across all partitions of k into <= v parts,
    where f3 = # of 3-distinct column triples and f2 = # of 2-distinct column triples
    in a single row of length k over v symbols.
    """
    pts: Dict[int, int] = {}

    def gen(rem: int, max_p: int, parts_left: int, s2: int, s3: int) -> None:
        if rem == 0:
            f3 = (k * k * k - 3 * k * s2 + 2 * s3) // 6
            f2 = ((k + 1) * s2 - s3 - k * k) // 2
            prev = pts.get(f3)
            if prev is None or f2 > prev:
                pts[f3] = f2
            return
        if parts_left == 0 or rem > max_p * parts_left:
            return
        lo = (rem + parts_left - 1) // parts_left
        hi = min(rem, max_p)
        for p in range(hi, lo - 1, -1):
            gen(rem - p, p, parts_left - 1, s2 + p * p, s3 + p * p * p)

    gen(k, k, v, 0, 0)
    items = sorted(pts.items())
    hull: List[Tuple[int, int]] = []
    for pt in items:
        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            x3, y3 = pt
            if (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1) >= 0:
                hull.pop()
            else:
                break
        hull.append(pt)
    return hull


def max_f2_given_avg_f3(hull: List[Tuple[int, int]], avg_f3: float) -> Optional[float]:
    """Upper-hull interpolation for max average f2 given required average f3."""
    if avg_f3 > hull[-1][0] + 1e-9:
        return None
    if avg_f3 <= hull[0][0]:
        return float(max(y for _, y in hull))
    for i in range(len(hull) - 1):
        x1, y1 = hull[i]
        x2, y2 = hull[i + 1]
        if x1 <= avg_f3 <= x2:
            if x2 == x1:
                return float(max(y1, y2))
            t = (avg_f3 - x1) / (x2 - x1)
            return y1 + t * (y2 - y1)
    return float(hull[-1][1])


def max_2sym_bin(k: int) -> int:
    """Maximum 2-distinct column triples in a binary row of length k."""
    m = k // 2
    return m * (k - m) * (k - 2) // 2


def load_ca_table(path: str):
    """Load ca_table.csv.gz, returning schema stats and all t=3 rows for v in {2, 4..14}."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])
        total_rows = 0
        t3_rows_total = 0
        t3_by_v: Dict[int, List[dict]] = defaultdict(list)
        entered_dates = []
        tier_counts = Counter()
        for row in reader:
            total_rows += 1
            if row["t"] == "3":
                t3_rows_total += 1
                v = int(row["v"])
                if v == 2 or 4 <= v <= 14:
                    t3_by_v[v].append(row)
                    if 6 <= int(row["k"]) <= 35:
                        tier_counts[row["tier"]] += 1
                        if row["entered"]:
                            entered_dates.append(row["entered"])
    schema = {
        "header": header,
        "total_rows": total_rows,
        "t3_rows_total": t3_rows_total,
        "t3_v4_14_rows": sum(len(t3_by_v[v]) for v in range(4, 15)),
        "t3_v4_14_k6_35_tiers": dict(tier_counts),
        "entered_min": min(entered_dates) if entered_dates else "",
        "entered_max": max(entered_dates) if entered_dates else "",
    }
    return schema, t3_by_v


def load_lower_bounds(path: Optional[str]) -> Dict[Tuple[int, int], int]:
    """Load proven lower bounds for t=3, v=4..14, k=6..35 if available."""
    lb: Dict[Tuple[int, int], int] = defaultdict(int)
    if not path or not os.path.exists(path):
        return lb
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["t"] == "3":
                v = int(row["v"])
                if 4 <= v <= 14:
                    kmin = max(6, int(row["k_min"]))
                    kmax = min(35, int(row["k_max"]))
                    b = int(row["bound"])
                    for k in range(kmin, kmax + 1):
                        if b > lb[(v, k)]:
                            lb[(v, k)] = b
    return lb


def load_binary_const_rows(path: Optional[str]) -> Dict[int, int]:
    """Read constant_rows counts for verified binary t=3 arrays from MANIFEST.csv."""
    # Map (k, N) -> max constant_rows; fallback 1 (conservative vs 2)
    by_k: Dict[int, Tuple[int, int]] = {}
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["t"] == "3" and row["v"] == "2":
                k = int(row["k"])
                N = int(row["N"])
                cr = int(row["constant_rows"]) if row["constant_rows"].isdigit() else 1
                prev = by_k.get(k)
                if prev is None or N < prev[0] or (N == prev[0] and cr > prev[1]):
                    by_k[k] = (N, cr)
    return {k: cr for k, (_, cr) in by_k.items()}


def build_envelope(rows: List[dict], kmin: int = 5, kmax: int = 36):
    """
    Compute monotone best-known N_rec(k) = min_{k' >= k} N(k') and representative record row.
    """
    env = {}
    for k in range(kmin, kmax + 1):
        cands = [r for r in rows if int(r["k"]) >= k]
        best_N = min(int(r["N"]) for r in cands)
        achievers = [r for r in cands if int(r["N"]) == best_N]
        true_max_k = max(int(r["k"]) for r in achievers)
        # Prefer VERIFIED, then exact/smallest k >= current k, then newest entry
        best_row = sorted(
            achievers,
            key=lambda r: (
                0 if r["tier"] == "VERIFIED" else 1,
                int(r["k"]),
                r["entered"],
            ),
        )[0]
        env[k] = {
            "N_rec": best_N,
            "true_max_k": true_max_k,
            "source_k": int(best_row["k"]),
            "tier": best_row["tier"],
            "source_id": best_row["source_id"],
            "entered": best_row["entered"],
            "construction": best_row["construction"],
            "source_detail": best_row["source_detail"],
            "notes": best_row["notes"],
        }
    return env


def compute_plateaus(env: dict, kmin: int = 6, kmax: int = 35) -> Dict[int, int]:
    """Compute consecutive plateau length within [kmin, kmax] sharing the same N_rec."""
    plen: Dict[int, int] = {}
    k = kmin
    while k <= kmax:
        n0 = env[k]["N_rec"]
        k2 = k
        while k2 <= kmax and env[k2]["N_rec"] == n0:
            k2 += 1
        for kk in range(k, k2):
            plen[kk] = k2 - k
        k = k2
    return plen


def check_arith_fingerprint(N_rec: int, v: int, G: int, gbin: int) -> Optional[Tuple[int, int]]:
    """Check if N_rec - v == A'*G + B'*gbin for integers A' >= 1, B' >= 0."""
    rem = N_rec - v
    if rem < G:
        return None
    # Return witness with largest A' (smallest B')
    for a in range(rem // G, 0, -1):
        left = rem - a * G
        if left % gbin == 0:
            return (a, left // gbin)
    return None


def classify_construction(rec: dict) -> str:
    """Classify record construction provenance (ignoring notes about superseded records)."""
    txt = (rec["construction"] + " " + rec["source_detail"]).lower()
    if any(kw in txt for kw in GROUP_CONSTR_KEYWORDS):
        return "GROUP/CCL"
    if "row-deletion" in txt or "post-optimisation" in txt or "delete a run" in txt or "postop" in txt:
        if "fuse" in txt:
            return "OA_FUSE_POSTOP"
        return "POSTOP_SA_TABU"
    if any(kw in txt for kw in CK_DOUBLING_KEYWORDS):
        return "CK_DOUBLING"
    if "poly2" in txt or "pencil" in txt:
        return "POLY2"
    if "scphf" in txt or "lfsr" in txt or "raaphorst" in txt:
        return "SCPHF/LFSR"
    if "ckrs" in txt:
        return "CKRS_SA"
    if "oa" in txt or "orthogonal array" in txt:
        return "OA/OA+"
    if "torres jimenez" in txt:
        return "TORRES_JIMENEZ"
    return "OTHER"


def main() -> None:
    parser = argparse.ArgumentParser(description="Systematic t=3 covering array target scan (v=4..14, k=6..35)")
    parser.add_argument("--ca-table", default="/tmp/ca_table.csv.gz")
    parser.add_argument("--lower-bounds", default="/tmp/lower_bounds.csv")
    parser.add_argument("--manifest", default="/tmp/MANIFEST.csv")
    parser.add_argument("--json-out", default="")
    args = parser.parse_args()

    schema, t3_by_v = load_ca_table(args.ca_table)
    lb = load_lower_bounds(args.lower_bounds)
    bin_const = load_binary_const_rows(args.manifest)

    envs = {v: build_envelope(t3_by_v[v], 5, 36) for v in range(4, 15)}
    plateaus = {v: compute_plateaus(envs[v], 6, 35) for v in range(4, 15)}
    can2_env = build_envelope(t3_by_v[2], 6, 35)
    can2 = {k: can2_env[k]["N_rec"] for k in range(6, 36)}
    # Conservative non-constant binary row count needed for a pure binary CA(N2; 3, k, 2)
    bin_nonconst_need = {}
    for k in range(6, 36):
        # Find smallest k' >= k in bin_const, fallback 1 constant row
        cr = 1
        for kk in range(k, 36):
            if kk in bin_const:
                cr = bin_const[kk]
                break
        bin_nonconst_need[k] = can2[k] - cr

    hull_cache: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}

    def get_hull(k: int, v: int) -> List[Tuple[int, int]]:
        key = (k, v)
        if key not in hull_cache:
            hull_cache[key] = pareto_f3_f2(k, v)
        return hull_cache[key]

    def find_gate0_anchor(spec: GroupSpec, gbin: int, k: int) -> Optional[dict]:
        """
        Check k-1 and k-2 for a known record solvable as a fast Gate-0 positive control
        with the same group and V <= 85 (either EXACT/SUB <= N_rec or SOFT <= 1.15*N_rec).
        """
        v, G, o3 = spec.v, spec.order, spec.orbs_3sym
        best = None
        for k0 in (k - 1, k - 2):
            if k0 < 5:
                continue
            nr0 = envs[v][k0]["N_rec"]
            ck3 = math.comb(k0, 3)
            hull = get_hull(k0, v)
            max_f3, f2_bal = hull[-1]
            m2b = max_2sym_bin(k0)
            max_ab = 85 // k0
            for a in range(o3, max_ab + 1):
                c3 = (a * G * max_f3) / (ck3 * v * (v - 1) * (v - 2))
                det_od = (o3 == 1 and a == 1 and k0 <= v)
                if c3 < 1.35 and not det_od:
                    continue
                req_f3 = (ck3 * v * (v - 1) * (v - 2)) / (a * G)
                mf2 = max_f2_given_avg_f3(hull, req_f3)
                if mf2 is None:
                    continue
                for b in range(0, max_ab - a + 1):
                    v0 = k0 * (a + b)
                    if v0 > 85:
                        continue
                    n0 = a * G + b * gbin + v
                    if n0 < v ** 3 or n0 > int(1.15 * nr0):
                        continue
                    mc2 = (a * mf2 * v * (v - 1) + b * m2b * gbin) / (3 * ck3 * v * (v - 1))
                    bc2 = (a * f2_bal * v * (v - 1) + b * m2b * gbin) / (3 * ck3 * v * (v - 1))
                    if mc2 < 1.35:
                        continue
                    kind = "EXACT" if n0 == nr0 else ("SUB" if n0 < nr0 else "SOFT")
                    prio = (
                        0 if kind == "EXACT" else (1 if kind == "SOFT" else 2),
                        k - k0,
                        abs(n0 - nr0),
                        -(bc2 if det_od else min(c3, bc2)),
                    )
                    if best is None or prio < best[0]:
                        best = (
                            prio,
                            {
                                "k0": k0,
                                "kind": kind,
                                "N0": n0,
                                "N_rec_k0": nr0,
                                "A": a,
                                "B": b,
                                "V": v0,
                                "cap3": round(c3, 2),
                                "bal_cap2": round(bc2, 2),
                            },
                        )
        return best[1] if best else None

    def find_nearby_gate0(spec: GroupSpec, gbin: int, k: int) -> Optional[dict]:
        """Fallback: nearest smaller k0 < k-2 with V <= 85 (e.g. k=8..11 CCL/OA anchor)."""
        v, G, o3 = spec.v, spec.order, spec.orbs_3sym
        for k0 in range(k - 3, 5, -1):
            nr0 = envs[v][k0]["N_rec"]
            ck3 = math.comb(k0, 3)
            hull = get_hull(k0, v)
            max_f3, f2_bal = hull[-1]
            m2b = max_2sym_bin(k0)
            max_ab = 85 // k0
            best = None
            for a in range(o3, max_ab + 1):
                c3 = (a * G * max_f3) / (ck3 * v * (v - 1) * (v - 2))
                det_od = (o3 == 1 and a == 1 and k0 <= v)
                if c3 < 1.35 and not det_od:
                    continue
                for b in range(0, max_ab - a + 1):
                    v0 = k0 * (a + b)
                    if v0 > 85:
                        continue
                    n0 = a * G + b * gbin + v
                    if n0 < v ** 3 or n0 > int(1.15 * nr0):
                        continue
                    bc2 = (a * f2_bal * v * (v - 1) + b * m2b * gbin) / (3 * ck3 * v * (v - 1))
                    if bc2 < 1.35:
                        continue
                    kind = "EXACT" if n0 == nr0 else ("SUB" if n0 < nr0 else "SOFT")
                    prio = (0 if kind in ("EXACT", "SOFT") else 1, abs(n0 - nr0), -(bc2 if det_od else min(c3, bc2)))
                    if best is None or prio < best[0]:
                        best = (
                            prio,
                            {
                                "k0": k0,
                                "kind": kind,
                                "N0": n0,
                                "N_rec_k0": nr0,
                                "A": a,
                                "B": b,
                                "V": v0,
                                "cap3": round(c3, 2),
                                "bal_cap2": round(bc2, 2),
                            },
                        )
            if best:
                return best[1]
        return None

    all_candidates = []
    ref_candidates = []
    watchouts = []

    for spec in GROUP_SPECS:
        v, G, o3 = spec.v, spec.order, spec.orbs_3sym
        for k in range(6, 36):
            rec = envs[v][k]
            N_rec = rec["N_rec"]
            N_prev = envs[v][k - 1]["N_rec"]
            delta_N = N_rec - N_prev
            plen = plateaus[v][k]
            ratio = N_rec / (v ** 3)
            ck3 = math.comb(k, 3)
            tot_orbs = ck3 * spec.orbs_per_triple
            hull = get_hull(k, v)
            max_f3, f2_bal = hull[-1]
            m2b = max_2sym_bin(k)
            min_N = max(v ** 3, lb[(v, k)])
            constr_class = classify_construction(rec)

            for gbin in spec.bin_sizes:
                fp_witness = check_arith_fingerprint(N_rec, v, G, gbin)
                fp_arith = fp_witness is not None
                fp_true_group = constr_class == "GROUP/CCL"

                # Enumerate all Pareto-feasible (A, B) with N_cand < N_rec
                feasible_sw = []
                feasible_decoup = []
                feasible_all = []
                max_A = (N_rec - 1 - v) // G
                for a in range(o3, max_A + 1):
                    c3 = (a * G * max_f3) / (ck3 * v * (v - 1) * (v - 2))
                    if c3 < 1.25:
                        continue
                    req_f3 = (ck3 * v * (v - 1) * (v - 2)) / (a * G)
                    mf2 = max_f2_given_avg_f3(hull, req_f3)
                    if mf2 is None:
                        continue
                    max_B = (N_rec - 1 - v - a * G) // gbin
                    for b in range(0, max_B + 1):
                        N_cand = a * G + b * gbin + v
                        if N_cand < min_N or N_cand >= N_rec:
                            continue
                        mc2 = (a * mf2 * v * (v - 1) + b * m2b * gbin) / (3 * ck3 * v * (v - 1))
                        bc2 = (a * f2_bal * v * (v - 1) + b * m2b * gbin) / (3 * ck3 * v * (v - 1))
                        if mc2 < 1.25:
                            continue
                        V = k * (a + b)
                        det_3sym = (o3 == 1 and a >= 2 and k <= 2 * v - 2)
                        bin_eq = b * (2 if gbin == v * (v - 1) else 1)
                        # Effective active variables if A=2 is fixed deterministically:
                        V_eff = k * b if det_3sym else V
                        entry = {
                            "A": a,
                            "B": b,
                            "N_cand": N_cand,
                            "save": N_rec - N_cand,
                            "V": V,
                            "V_eff": V_eff,
                            "cap3": round(c3, 2),
                            "max_cap2": round(mc2, 2),
                            "bal_cap2": round(bc2, 2),
                            "det_3sym": det_3sym,
                            "bin_eq": bin_eq,
                            "bin_need": bin_nonconst_need[k],
                            "guaranteed_bin": det_3sym and (bin_eq >= bin_nonconst_need[k]),
                        }
                        feasible_all.append(entry)
                        if 35 <= V <= 95:
                            feasible_sw.append(entry)
                        elif 96 <= V <= 200 and c3 >= 1.45 and bc2 >= 1.45:
                            feasible_decoup.append(entry)

                if not feasible_all:
                    continue

                # Select best candidate config:
                # 1) Strict sweet spot (35<=V<=95) with strong balance (bal_cap2>=1.15)
                # 2) Or decoupled PGL/PSL (bal_cap2>=1.50, V<=200) if strict sweet spot is missing or too thin
                sw_best = (
                    max(feasible_sw, key=lambda e: (min(e["cap3"], e["bal_cap2"]), e["N_cand"]))
                    if feasible_sw
                    else None
                )
                dec_best = (
                    max(
                        feasible_decoup,
                        key=lambda e: (
                            1 if e["guaranteed_bin"] else 0,
                            1 if e["det_3sym"] else 0,
                            e["bal_cap2"] if e["det_3sym"] else min(e["cap3"], e["bal_cap2"]),
                            e["N_cand"],
                            -e["V_eff"],
                        ),
                    )
                    if feasible_decoup
                    else None
                )

                # Track watch-out items (high ratio or big jump, but fp_true_group / fp_arith / tot_orbs > 15000 / thin bc2)
                if not spec.is_reference:
                    best_any = sw_best or dec_best or max(feasible_all, key=lambda e: (min(e["cap3"], e["bal_cap2"]), -e["V"]))
                    reasons = []
                    if fp_true_group:
                        reasons.append("TRUE_GROUP_RECORD")
                    if fp_arith and not fp_true_group:
                        reasons.append(f"ARITH_FP({fp_witness[0]}*{G}+{fp_witness[1]}*{gbin})")
                    if tot_orbs > 15000:
                        reasons.append(f"HUGE_ORBS({tot_orbs})")
                    if best_any["V"] > 180 and not best_any["det_3sym"]:
                        reasons.append(f"HIGH_V({best_any['V']})")
                    if sw_best and sw_best["bal_cap2"] < 1.15 and not dec_best:
                        reasons.append(f"TIGHT_2SYM(bc2={sw_best['bal_cap2']})")
                    if reasons and (ratio >= 1.45 or delta_N >= 150):
                        watchouts.append(
                            {
                                "v": v,
                                "k": k,
                                "group": spec.name,
                                "G": G,
                                "gbin": gbin,
                                "N_rec": N_rec,
                                "ratio": round(ratio, 2),
                                "delta_N": delta_N,
                                "plateau": plen,
                                "tot_orbs": tot_orbs,
                                "best_N_cand": best_any["N_cand"],
                                "V": best_any["V"],
                                "constr_class": constr_class,
                                "construction": rec["construction"][:60],
                                "reasons": reasons,
                            }
                        )

                if tot_orbs > 15000 and not spec.is_reference:
                    continue

                g0 = find_gate0_anchor(spec, gbin, k)
                g0_near = None if g0 else find_nearby_gate0(spec, gbin, k)

                def build_record(mode: str, cfg: dict) -> dict:
                    # Transparent attractiveness score (higher is better)
                    score = 0.0
                    # 1) Variable sweet spot
                    if 35 <= cfg["V"] <= 95:
                        score += 28.0
                    elif cfg["det_3sym"] and cfg["V_eff"] <= 145:
                        score += 24.0  # A=2 deterministic, only binary B searched
                    elif cfg["V"] <= 145:
                        score += 14.0
                    elif cfg["V"] <= 200:
                        score += 8.0
                    # 2) Combinatorial solvability / headroom (calibrated to exp/ca-3-k-6)
                    eff_cap = cfg["bal_cap2"] if cfg["det_3sym"] else min(cfg["cap3"], cfg["bal_cap2"])
                    if cfg["guaranteed_bin"]:
                        score += 26.0  # existence mathematically guaranteed via known CA(N2;3,k,2)
                    elif cfg["det_3sym"] and cfg["bin_eq"] >= cfg["bin_need"] - 1:
                        score += 23.0  # within 1 binary row of pure CA(N2;3,k,2), +26% 2-sym from A=2
                    elif eff_cap >= 1.85:
                        score += 21.0
                    elif eff_cap >= 1.60:
                        score += 18.0
                    elif eff_cap >= 1.40:
                        score += 14.0
                    elif eff_cap >= 1.20:
                        score += 8.0
                    elif eff_cap >= 1.00:
                        score += 2.0
                    else:
                        score -= 10.0
                    if cfg["det_3sym"]:
                        score += 8.0
                    # 3) Record headroom (N_rec / v^3), jump, plateau, savings
                    score += min(18.0, max(0.0, (ratio - 1.25) * 16.0))
                    if delta_N >= 300:
                        score += 6.0
                    elif delta_N >= 100:
                        score += 3.0
                    if plen >= 3:
                        score += 4.0
                    elif plen == 2:
                        score += 2.0
                    if rec["tier"] == "CITED":
                        score += 3.0  # unverified older record often softer than fresh SA/tabu
                    # 4) Cache / orbit speed bonus
                    if tot_orbs <= 1500:
                        score += 8.0
                    elif tot_orbs <= 3500:
                        score += 5.0
                    elif tot_orbs <= 8000:
                        score += 2.0
                    # 5) Gate-0 anchor bonus
                    if g0 is not None:
                        score += 7.0 if g0["kind"] in ("EXACT", "SOFT") else 4.0
                    elif g0_near is not None:
                        score += 3.0
                    # 6) Red-Team fingerprint penalties
                    if fp_true_group:
                        score -= 35.0
                    elif fp_arith:
                        # Arithmetical hit from CK-doubling is much milder than true group hit
                        score -= 6.0 if constr_class == "CK_DOUBLING" else 14.0

                    return {
                        "mode": mode,
                        "score": round(score, 1),
                        "v": v,
                        "k": k,
                        "group": spec.name,
                        "G": G,
                        "gbin": gbin,
                        "orbs_per_triple": spec.orbs_per_triple,
                        "tot_orbs": tot_orbs,
                        "N_rec": N_rec,
                        "ratio": round(ratio, 2),
                        "delta_N": delta_N,
                        "plateau": plen,
                        "true_max_k": rec["true_max_k"],
                        "tier": rec["tier"],
                        "entered": rec["entered"],
                        "constr_class": constr_class,
                        "construction": rec["construction"],
                        "fp_arith": fp_arith,
                        "fp_witness": fp_witness,
                        "fp_true_group": fp_true_group,
                        "gate0": g0,
                        "gate0_near": g0_near,
                        **cfg,
                    }

                if spec.is_reference:
                    if sw_best:
                        ref_candidates.append(build_record("SW", sw_best))
                    elif dec_best:
                        ref_candidates.append(build_record("DEC", dec_best))
                else:
                    if sw_best:
                        all_candidates.append(build_record("SW", sw_best))
                    if dec_best and (sw_best is None or dec_best["bal_cap2"] >= sw_best["bal_cap2"] + 0.30):
                        all_candidates.append(build_record("DEC", dec_best))

    # Deduplicate Top 15: keep best config per (v, k) cell so Top 15 spans distinct target cells
    best_by_cell: Dict[Tuple[int, int], dict] = {}
    for c in sorted(all_candidates, key=lambda x: (-x["score"], x["tot_orbs"], x["V"])):
        key = (c["v"], c["k"])
        if key not in best_by_cell:
            best_by_cell[key] = c
    top15 = sorted(best_by_cell.values(), key=lambda x: (-x["score"], x["tot_orbs"], x["V"]))[:15]

    # Also build strict-SW Top list (35 <= V <= 95 only) for full transparency
    best_sw_by_cell: Dict[Tuple[int, int], dict] = {}
    for c in sorted(
        [x for x in all_candidates if x["mode"] == "SW"],
        key=lambda x: (-x["score"], x["tot_orbs"], x["V"]),
    ):
        key = (c["v"], c["k"])
        if key not in best_sw_by_cell:
            best_sw_by_cell[key] = c
    strict_sw_list = sorted(best_sw_by_cell.values(), key=lambda x: (-x["score"], x["tot_orbs"]))

    # Print structured summary
    print("=== CA_TABLE SCHEMA ===")
    print(json.dumps(schema, indent=2))

    print("\n=== TOP 15 CANDIDATES (v=7..14, distinct (v,k) cells) ===")
    print(
        f"{'#':>2} {'Mode':4} {'Scr':>5} {'(3,k,v)':>9} {'Group':12} {'bin':>3} "
        f"{'N_rec':>5} {'xV3':>5} {'dN':>4} {'pl':>2} {'N_cand':>6} {'save':>5} "
        f"{'A,B':>5} {'V(eff)':>8} {'Orbs':>5} {'c3/bc2':>9} {'FP':>4} {'Gate0':>18} {'Record'}"
    )
    for idx, c in enumerate(top15, 1):
        g0 = c["gate0"]
        if g0:
            g0_s = f"k={g0['k0']}:{g0['kind'][:3]}(V{g0['V']})"
        elif c["gate0_near"]:
            gn = c["gate0_near"]
            g0_s = f"~k={gn['k0']}:{gn['kind'][:3]}(V{gn['V']})"
        else:
            g0_s = "-"
        fp_s = "GRP!" if c["fp_true_group"] else ("CK?" if (c["fp_arith"] and c["constr_class"] == "CK_DOUBLING") else ("AR!" if c["fp_arith"] else "NO"))
        veff = f"{c['V']}({c['V_eff']})" if c["det_3sym"] else f"{c['V']}"
        print(
            f"{idx:2d} {c['mode']:4} {c['score']:5.1f} "
            f"({c['k']:2d},{c['v']:2d})   {c['group']:12} {c['gbin']:3d} "
            f"{c['N_rec']:5d} {c['ratio']:5.2f} {c['delta_N']:4d} {c['plateau']:2d} "
            f"{c['N_cand']:6d} {-c['save']:5d} {c['A']},{c['B']:<3d} {veff:>8} "
            f"{c['tot_orbs']:5d} {c['cap3']:.2f}/{c['bal_cap2']:.2f} {fp_s:>4} {g0_s:>18} "
            f"{c['tier'][:3]}:{c['constr_class']}"
        )

    print("\n=== ALL STRICT SWEET-SPOT CANDIDATES (35 <= V <= 95, v=7..14) ===")
    for idx, c in enumerate(strict_sw_list, 1):
        g0 = c["gate0"]
        g0_s = f"k={g0['k0']}:{g0['kind'][:3]}(V{g0['V']})" if g0 else "-"
        fp_s = "GRP!" if c["fp_true_group"] else ("CK?" if (c["fp_arith"] and c["constr_class"] == "CK_DOUBLING") else ("AR!" if c["fp_arith"] else "NO"))
        print(
            f"{idx:2d} {c['score']:5.1f} (3,{c['k']:2d},{c['v']:2d}) {c['group']:12} b={c['gbin']:3d} | "
            f"Nrec={c['N_rec']:4d}({c['ratio']:.2f}x dN={c['delta_N']:4d} pl={c['plateau']:2d}) -> {c['N_cand']:4d}(-{c['save']:3d}) "
            f"A={c['A']} B={c['B']} V={c['V']:2d} orb={c['tot_orbs']:4d} c3={c['cap3']:.2f} bc2={c['bal_cap2']:.2f} FP={fp_s:3} G0={g0_s:16} {c['tier'][:3]}:{c['constr_class']}"
        )

    print("\n=== REFERENCE / SANITY CHECK (v=5, 6) ===")
    for c in sorted(ref_candidates, key=lambda x: (x["v"], x["k"], x["group"])):
        if c["k"] <= 15:
            fp_s = "GRP!" if c["fp_true_group"] else ("AR!" if c["fp_arith"] else "NO")
            print(
                f"v={c['v']} k={c['k']:2d} {c['group']:8} b={c['gbin']:2d} | Nrec={c['N_rec']:3d}({c['ratio']:.2f}x) -> "
                f"{c['N_cand']:3d}(-{c['save']:3d}) A={c['A']} B={c['B']} V={c['V']:3d} orb={c['tot_orbs']:4d} "
                f"c3={c['cap3']:.2f} bc2={c['bal_cap2']:.2f} FP={fp_s:4} {c['tier'][:3]}:{c['constr_class']}"
            )

    if args.json_out:
        out = {
            "schema": schema,
            "top15": top15,
            "strict_sw": strict_sw_list,
            "reference": ref_candidates,
            "watchouts": watchouts,
            "all_candidates_count": len(all_candidates),
            "envelopes_summary": {
                str(v): [
                    {
                        "k": k,
                        "N_rec": envs[v][k]["N_rec"],
                        "ratio": round(envs[v][k]["N_rec"] / (v ** 3), 2),
                        "delta_N": envs[v][k]["N_rec"] - envs[v][k - 1]["N_rec"],
                        "plateau": plateaus[v][k],
                        "tier": envs[v][k]["tier"],
                        "entered": envs[v][k]["entered"],
                        "constr_class": classify_construction(envs[v][k]),
                        "construction": envs[v][k]["construction"],
                    }
                    for k in range(6, 36)
                ]
                for v in range(4, 15)
            },
        }
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"\nWrote JSON output to {args.json_out}")


if __name__ == "__main__":
    main()
