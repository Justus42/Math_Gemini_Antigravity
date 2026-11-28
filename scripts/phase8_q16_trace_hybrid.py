#!/usr/bin/env python3
"""Phase 8: q = 16 Spur-Baer-Hybrid Konstruktion (m = 315 fuer v = 15, m = 332 fuer v = 16).

Pure Python (std-only), feldunabhaengig ueber GeneralGF(16) aus scripts/gen_general_tqv.py.
Keine Suche, keine Zufallszahlen, deterministisch.

Erzeugt die Vertreterlisten:
  - data/phase8_q16_hybrid/R_q16_v15_trace_m315.txt  (F = 3, v = 15, m = 315)
  - data/phase8_q16_hybrid/R_q16_v16_trace_m332.txt  (F = 4, v = 16, m = 332)
  - data/phase8_q16_hybrid/SHA256SUMS
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_general_tqv import GeneralGF  # noqa: E402


def build_q16_trace_hybrid(F: int) -> tuple[list[tuple[int, int, int, int]], dict]:
    """Konstruiert die q = 16 Spur-Baer-Hybrid Vertreterliste fuer F in {3, 4}."""
    if F not in (3, 4):
        raise ValueError(f"F={F} nicht unterstuetzt (erwartet 3 oder 4)")

    q = 16
    gf = GeneralGF(q)
    add, mul = gf.add, gf.mul

    # Additive und multiplikative Inverse (feldunabhaengig)
    neg = [next(y for y in range(q) if add[x][y] == 0) for x in range(q)]
    sub = [[add[x][neg[y]] for y in range(q)] for x in range(q)]
    inv = [0] + [next(y for y in range(1, q) if mul[x][y] == 1) for x in range(1, q)]

    def pow_gf(x: int, e: int) -> int:
        res = 1
        base = x
        while e > 0:
            if e & 1:
                res = mul[res][base]
            base = mul[base][base]
            e >>= 1
        return res

    # Spurabbildung Tr(x) = x + x^2 + x^4 + x^8 in GF(16) (Charakteristik 2)
    def trace(x: int) -> int:
        x2 = mul[x][x]
        x4 = mul[x2][x2]
        x8 = mul[x4][x4]
        val = add[add[x][x2]][add[x4][x8]]
        assert val in (0, 1), f"Tr({x}) = {val} nicht in GF(2)"
        return val

    # Unterkoerper F_4 = {x in F_16 : x^4 == x}
    Fn = sorted(x for x in range(q) if pow_gf(x, 4) == x)
    assert len(Fn) == 4 and Fn[0] == 0
    Fn_nz = Fn[1:]  # [i0, i1, i2]
    om = min(x for x in range(q) if x not in Fn)

    num = {x: idx for idx, x in enumerate(Fn)}
    nz_idx = {x: idx for idx, x in enumerate(Fn_nz)}

    # Eindeutige Zerlegung z = p1(z) + p2(z)*om mit p1(z), p2(z) in Fn
    p1 = [0] * q
    p2 = [0] * q
    seen = set()
    for a1 in Fn:
        for a2 in Fn:
            z = add[a1][mul[a2][om]]
            p1[z] = a1
            p2[z] = a2
            seen.add(z)
    assert len(seen) == q

    def K(i: int, j: int) -> int:
        assert i in nz_idx and j in num
        return (num[i] - 1) * 4 + num[j]

    V = [12 + m for m in range(F)]

    # Freie Geraden: d_u = 1/i_u (a-Seite, w2=0) und d'_u = 1/(i_u*om) (b-Seite, w1=0)
    d_free = [inv[i_u] for i_u in Fn_nz]
    dp_free = [inv[mul[i_u][om]] for i_u in Fn_nz]

    # Zielmenge auf d = 0: target_d0 = {c in F_16 : p2(c) in {0, i2}}
    i2 = Fn_nz[2]
    target_d0 = {c for c in range(q) if p2[c] in (0, i2)}
    assert len(target_d0) == 8

    # Eindeutige Skalare mu_a, mu_b in F_16^*
    d0_plus_d1 = add[d_free[0]][d_free[1]]
    dp0_plus_dp1 = add[dp_free[0]][dp_free[1]]
    mu_a_cands = [
        mu for mu in range(1, q)
        if {c for c in range(q) if trace(mul[mul[mu][d0_plus_d1]][c]) == 0} == target_d0
    ]
    mu_b_cands = [
        mu for mu in range(1, q)
        if {c for c in range(q) if trace(mul[mul[mu][dp0_plus_dp1]][c]) == 0} == target_d0
    ]
    assert len(mu_a_cands) == 1, f"mu_a nicht eindeutig: {mu_a_cands}"
    assert len(mu_b_cands) == 1, f"mu_b nicht eindeutig: {mu_b_cands}"
    mu_a = mu_a_cands[0]
    mu_b = mu_b_cands[0]

    reps: list[tuple[int, int, int, int]] = []

    # Reihenfolge: d = 0..15, darin c = 0..15
    # (B) d = 0
    for c in range(q):
        c1, c2 = p1[c], p2[c]
        t = num[c1]
        if c2 != 0:
            u = nz_idx[c2]
            if F == 3:
                v_list = [V[2]] if u in (0, 1) else [V[0], V[1]]
            else:  # F == 4
                v_list = [V[2], V[3]] if u in (0, 1) else [V[0], V[1], V[3]]
            for idx in range(len(v_list)):
                ksym = K(c2, Fn[(t + idx) % 4])
                reps.append((c, 0, v_list[idx], ksym))
                reps.append((c, 0, ksym, v_list[idx]))
            for idx in range(len(v_list), 4):
                ksym = K(c2, Fn[(t + idx) % 4])
                reps.append((c, 0, ksym, ksym))
        else:
            if F == 3:
                if t < 3:
                    for m in range(3):
                        reps.append((c, 0, V[m], V[(m + t) % 3]))
                else:
                    reps.append((c, 0, V[0], V[0]))
                    reps.append((c, 0, V[1], V[1]))
            else:  # F == 4
                for m in range(4):
                    reps.append((c, 0, V[m], V[(m + t) % 4]))

    # (A) d = 1..15
    for d in range(1, q):
        w = inv[d]
        w1, w2 = p1[w], p2[w]
        for c in range(q):
            # a-Spalte
            if w2 != 0:
                a_sym = K(w2, p2[mul[sub[c][mul[w2][om]]][w]])
            else:
                u = nz_idx[w1]
                if u == 0:
                    a_sym = V[trace(mul[mul[mu_a][d_free[1]]][c])]
                elif u == 1:
                    a_sym = V[trace(mul[mul[mu_a][d_free[0]]][c])]
                else:
                    a_sym = V[2]
            # b-Spalte
            if w1 != 0:
                b_sym = K(w1, p1[mul[sub[c][mul[w1][om]]][w]])
            else:
                u = nz_idx[w2]
                if u == 0:
                    b_sym = V[trace(mul[mul[mu_b][dp_free[1]]][c])]
                elif u == 1:
                    b_sym = V[trace(mul[mul[mu_b][dp_free[0]]][c])]
                else:
                    b_sym = V[2]
            reps.append((c, d, a_sym, b_sym))

    meta = {
        "q": q,
        "F": F,
        "v": 12 + F,
        "m": len(reps),
        "mod_poly": gf.mod_poly,
        "Fn": Fn,
        "om": om,
        "d_free": d_free,
        "dp_free": dp_free,
        "mu_a": mu_a,
        "mu_b": mu_b,
    }
    return reps, meta


def write_reps(path: str, reps: list[tuple[int, int, int, int]], meta: dict) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        f"# q={meta['q']} v={meta['v']} F={meta['F']} m={meta['m']} "
        f"mod_poly={meta['mod_poly']} Fn={meta['Fn']} om={meta['om']} "
        f"mu_a={meta['mu_a']} mu_b={meta['mu_b']}\n"
    ]
    for c, d, a, b in reps:
        lines.append(f"{c} {d} {a} {b}\n")
    data = "".join(lines).encode("utf-8")
    with open(path, "wb") as fh:
        fh.write(data)
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="q=16 Spur-Baer-Hybrid Vertreterlisten (m=315, m=332)")
    ap.add_argument("--out-dir", default="data/phase8_q16_hybrid")
    args = ap.parse_args()

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    specs = [
        (3, 15, 315, "R_q16_v15_trace_m315.txt"),
        (4, 16, 332, "R_q16_v16_trace_m332.txt"),
    ]
    sha_lines = []
    for F, v_exp, m_exp, fname in specs:
        reps, meta = build_q16_trace_hybrid(F)
        assert meta["v"] == v_exp and meta["m"] == m_exp, f"Mismatch: {meta}"
        assert len(set(reps)) == len(reps), "Duplikate in reps!"
        fpath = os.path.join(out_dir, fname)
        sha = write_reps(fpath, reps, meta)
        sha_lines.append(f"{sha}  {fname}\n")
        print(f"F={F} v={v_exp} m={m_exp} mu_a={meta['mu_a']} mu_b={meta['mu_b']} sha256={sha} -> {fpath}")

    sha_path = os.path.join(out_dir, "SHA256SUMS")
    with open(sha_path, "w", encoding="utf-8") as fh:
        fh.writelines(sha_lines)
    print(f"wrote {sha_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
