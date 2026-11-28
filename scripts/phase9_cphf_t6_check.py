#!/usr/bin/env python3
"""
Independent Python reference verifier for Phase 9B:
Hyperplane-pencil CPHF(2; 2q+2, q, 6) over F_q (q in {5, 7, 8, 9}).

Pure Python std-only implementation. Performs exact F_q Gaussian elimination
over all C(k, 6) 6-tuples, checks Sherwood hyperplanes, supports negative
controls, cross-checks against the C implementation, and rolls out canonical
Covering Arrays CA(N; 6, k, q).
"""

import argparse
import itertools
import json
import random
import subprocess
import sys
import time


class FiniteField:
    """Exact arithmetic for F_q and K = F_{q^2} = F_q[i] / (i^2 - p1*i - p0)."""

    def __init__(self, q: int):
        if q not in (5, 7, 8, 9, 11, 13, 17, 19):
            raise ValueError(f"Unsupported q={q}; expected one of 5, 7, 8, 9, 11, 13, 17, 19")
        self.q = q
        if q in (5, 7, 11, 13, 17, 19):
            self.add = [[(a + b) % q for b in range(q)] for a in range(q)]
            self.sub = [[(a - b) % q for b in range(q)] for a in range(q)]
            self.mul = [[(a * b) % q for b in range(q)] for a in range(q)]
        elif q == 8:
            # F_8 = F_2[x] / (x^3 + x + 1)
            self.add = [[a ^ b for b in range(8)] for a in range(8)]
            self.sub = [[a ^ b for b in range(8)] for a in range(8)]
            self.mul = [[self._mul8(a, b) for b in range(8)] for a in range(8)]
        elif q == 9:
            # F_9 = F_3[x] / (x^2 + 1), encoded as a0 + 3*a1
            self.add = [[0] * 9 for _ in range(9)]
            self.sub = [[0] * 9 for _ in range(9)]
            self.mul = [[0] * 9 for _ in range(9)]
            for a in range(9):
                a0, a1 = a % 3, a // 3
                for b in range(9):
                    b0, b1 = b % 3, b // 3
                    self.add[a][b] = ((a0 + b0) % 3) + 3 * ((a1 + b1) % 3)
                    self.sub[a][b] = ((a0 - b0) % 3) + 3 * ((a1 - b1) % 3)
                    r0 = (a0 * b0 - a1 * b1) % 3
                    r1 = (a0 * b1 + a1 * b0) % 3
                    self.mul[a][b] = r0 + 3 * r1

        self.inv = [0] * q
        for a in range(1, q):
            for b in range(1, q):
                if self.mul[a][b] == 1:
                    self.inv[a] = b
                    break
            assert self.inv[a] != 0

        # Quadratic extension K = F_q[i] / (i^2 - p1*i - p0)
        ext_params = {
            5: (2, 0, (2, 1)),   # i^2 = 2, zeta = 2 + i
            7: (3, 0, (1, 1)),   # i^2 = 3, zeta = 1 + i
            8: (1, 1, (2, 1)),   # i^2 = i + 1, zeta = x + i
            9: (4, 0, (3, 1)),   # i^2 = 1 + x (4), zeta = x + i
            11: (2, 0, (2, 1)),  # i^2 = 2, zeta = 2 + i
            13: (2, 0, (2, 1)),  # i^2 = 2, zeta = 2 + i
            17: (3, 0, (3, 1)),  # i^2 = 3, zeta = 3 + i
            19: (2, 0, (2, 1)),  # i^2 = 2, zeta = 2 + i
        }
        self.p0, self.p1, self.zeta = ext_params[q]
        self.eta = self.kpow(self.zeta, q - 1)

    @staticmethod
    def _mul8(a: int, b: int) -> int:
        r = 0
        for bit in range(3):
            if (b >> bit) & 1:
                r ^= a << bit
        for bit in range(4, 2, -1):
            if (r >> bit) & 1:
                r ^= 0b1011 << (bit - 3)
        return r

    def kmul(self, u, v):
        a, b = u
        c, d = v
        bd = self.mul[b][d]
        r0 = self.add[self.mul[a][c]][self.mul[bd][self.p0]]
        r1 = self.add[
            self.add[self.mul[a][d]][self.mul[b][c]]
        ][self.mul[bd][self.p1]]
        return (r0, r1)

    def kpow(self, u, e: int):
        r = (1, 0)
        b = u
        while e > 0:
            if e & 1:
                r = self.kmul(r, b)
            b = self.kmul(b, b)
            e >>= 1
        return r

    def mat_vec(self, mat, vec):
        out = []
        for row in mat:
            acc = 0
            for a, b in zip(row, vec):
                acc = self.add[acc][self.mul[a][b]]
            out.append(acc)
        return out

    def has_full_rank_6(self, rows) -> bool:
        """Exact Gaussian elimination over F_q for a 6x6 matrix."""
        m = [list(r) for r in rows]
        add = self.add
        sub = self.sub
        mul = self.mul
        inv = self.inv
        for col in range(6):
            piv = -1
            for r in range(col, 6):
                if m[r][col] != 0:
                    piv = r
                    break
            if piv == -1:
                return False
            if piv != col:
                m[col], m[piv] = m[piv], m[col]
            inv_p = inv[m[col][col]]
            piv_row = m[col]
            for r in range(col + 1, 6):
                val = m[r][col]
                if val != 0:
                    f = mul[val][inv_p]
                    row_r = m[r]
                    for j in range(col + 1, 6):
                        row_r[j] = sub[row_r[j]][mul[f][piv_row[j]]]
        return True


def build_parametric_rows(
    ff: FiniteField,
    g1,
    g2,
    alpha,
    beta,
    g3=(1, 0),
    m1=1,
    d1=0,
    frob1=0,
    m2=1,
    d2=0,
    G=None,
    M=None,
    pi2=None,
):
    """Build R1 and R2 (each list of 2q+2 vectors in F_q^6) from parameters."""
    q = ff.q
    n_orb = q + 1
    zeta = ff.zeta
    eta = ff.eta

    R1 = []
    # Row 1 Orbit A: k = 0..q, w = zeta^k
    for k in range(n_orb):
        w = ff.kpow(zeta, k)
        c1 = ff.kpow(w, 5)
        c2 = ff.kpow(w, 4 + q)
        c3 = ff.kpow(w, 3 + 2 * q)
        R1.append([c1[0], c1[1], c2[0], c2[1], c3[0], c3[1]])

    # Row 1 Orbit B: k = 0..q
    for k in range(n_orb):
        j = (m1 * k + d1) % n_orb
        w = ff.kpow(zeta, j)
        if frob1:
            w = ff.kpow(w, q)
        c1 = ff.kmul(g1, ff.kpow(w, 5))
        c2 = ff.kmul(g2, ff.kpow(w, 4 + q))
        c3 = ff.kmul(g3, ff.kpow(w, 3 + 2 * q))
        v = [c1[0], c1[1], c2[0], c2[1], c3[0], c3[1]]
        if G is not None:
            v = ff.mat_vec(G, v)
        R1.append(v)

    R2 = []
    # Row 2 Orbit A: k = 0..q, u = eta^k
    for k in range(n_orb):
        u = ff.kpow(eta, k)
        u2 = ff.kmul(u, u)
        R2.append([u2[0], u2[1], u[0], u[1], 1, 0])

    # Row 2 Orbit B: k = 0..q
    for k in range(n_orb):
        idx = pi2[k] if pi2 is not None else k
        j = (m2 * idx + d2) % n_orb
        u = ff.kpow(eta, j)
        u2 = ff.kmul(u, u)
        if M is not None:
            w4 = ff.mat_vec(M, [u2[0], u2[1], u[0], u[1]])
            R2.append([w4[0], w4[1], w4[2], w4[3], 0, 1])
        else:
            a2 = ff.kmul(alpha, u2)
            b1 = ff.kmul(beta, u)
            R2.append([a2[0], a2[1], b1[0], b1[1], 0, 1])

    return R1, R2


def check_all_6tuples(ff: FiniteField, R1, R2, n_orbit_a=None):
    """Exact check over all C(k, 6) 6-tuples. Returns counts by split a in 0..6."""
    k = len(R1)
    assert len(R2) == k
    if n_orbit_a is None:
        n_orbit_a = ff.q + 1
    dep1 = [0] * 7
    dep2 = [0] * 7
    both = [0] * 7
    for tup in itertools.combinations(range(k), 6):
        a = 0
        for x in tup:
            if x < n_orbit_a:
                a += 1
        ok1 = ff.has_full_rank_6([R1[x] for x in tup])
        ok2 = ff.has_full_rank_6([R2[x] for x in tup])
        if not ok1:
            dep1[a] += 1
        if not ok2:
            dep2[a] += 1
        if (not ok1) and (not ok2):
            both[a] += 1
    return dep1, dep2, both


def find_sherwood_hyperplane(ff: FiniteField, R):
    """Find a vector v in F_q^6 (first nonzero entry = 1) with v . R[j] != 0 for all j."""
    q = ff.q
    add = ff.add
    mul = ff.mul
    for lead in range(6):
        tail_len = 5 - lead
        for tail in itertools.product(range(q), repeat=tail_len):
            v = [0] * lead + [1] + list(tail)
            ok = True
            for col in R:
                dot = 0
                for a, b in zip(v, col):
                    dot = add[dot][mul[a][b]]
                if dot == 0:
                    ok = False
                    break
            if ok:
                return v
    return None


def rollout_ca(ff: FiniteField, R1, R2, out_path: str):
    """Roll out CPHF(2; k, q, 6) into canonical CA(N; 6, k, q)."""
    q = ff.q
    k = len(R1)
    add = ff.add
    mul = ff.mul
    inv = ff.inv

    v1 = find_sherwood_hyperplane(ff, R1)
    v2 = find_sherwood_hyperplane(ff, R2)

    def normalize(R, v):
        out = []
        for col in R:
            dot = 0
            for a, b in zip(v, col):
                dot = add[dot][mul[a][b]]
            assert dot != 0
            s = inv[dot]
            out.append([mul[s][x] for x in col])
        return out

    use_sherwood = (v1 is not None) and (v2 is not None)
    if use_sherwood:
        H1 = normalize(R1, v1)
        H2 = normalize(R2, v2)
    else:
        H1 = [list(c) for c in R1]
        H2 = [list(c) for c in R2]

    rows = []
    # Row 1 generates all q^6 codewords
    for x in itertools.product(range(q), repeat=6):
        row = []
        for col in H1:
            acc = 0
            for a, b in zip(x, col):
                acc = add[acc][mul[a][b]]
            row.append(acc)
        rows.append(row)

    # Row 2 generates q^6 - q (Sherwood) or q^6 - 1 (all-zero dedup) codewords
    const_rows = set(tuple([c] * k) for c in range(q)) if use_sherwood else {tuple([0] * k)}
    for x in itertools.product(range(q), repeat=6):
        row = []
        for col in H2:
            acc = 0
            for a, b in zip(x, col):
                acc = add[acc][mul[a][b]]
            row.append(acc)
        if tuple(row) in const_rows:
            continue
        rows.append(row)

    expected_n = 2 * (q ** 6) - (q if use_sherwood else 1)
    assert len(rows) == expected_n, f"Expected {expected_n} rows, got {len(rows)}"

    with open(out_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(" ".join(str(x) for x in row) + "\n")
    return len(rows), use_sherwood, v1, v2


def run_gate0(c_bin: str):
    print("=== GATE 0: Python Independent Verification ===")
    ff5 = FiniteField(5)
    g1, g2 = (1, 2), (2, 1)
    alpha, beta = (1, 1), (2, 1)
    R1, R2 = build_parametric_rows(ff5, g1, g2, alpha, beta)
    dep1, dep2, both = check_all_6tuples(ff5, R1, R2)
    print(f"q=5 Gate-0 example: g1={g1}, g2={g2}, alpha={alpha}, beta={beta}")
    print(f"  dep1 (a=0..6): {dep1}")
    print(f"  dep2 (a=0..6): {dep2}")
    print(f"  both (a=0..6): {both} (total={sum(both)})")

    assert dep1[6] == 0 and dep1[0] == 0 and dep1[5] == 0 and dep1[1] == 0, "Gate-0 Row 1 check failed!"
    assert dep2[5] == 0 and dep2[1] == 0 and dep2[6] == 1 and dep2[0] == 1, "Gate-0 Row 2 check failed!"
    print("  [PASS] Gate-0 analytical properties verified for q=5!")

    if c_bin:
        print(f"\n=== GATE 0: Cross-Check Python vs C ({c_bin}) ===")
        rng = random.Random(20261128)
        for q in (5, 7):
            ff = FiniteField(q)
            n_orb = q + 1
            coprimes = [m for m in range(1, n_orb) if _gcd(m, n_orb) == 1]
            # First test Gate-0 example on q=5, plus 5 random configs each for q=5 and q=7
            cases = []
            if q == 5:
                cases.append((g1, g2, alpha, beta, 1, 0, 0, 1, 0))
            for _ in range(5):
                def rand_k():
                    while True:
                        u = (rng.randrange(q), rng.randrange(q))
                        if u != (0, 0):
                            return u
                cases.append((
                    rand_k(), rand_k(), rand_k(), rand_k(),
                    rng.choice(coprimes), rng.randrange(n_orb), rng.randrange(2),
                    rng.choice(coprimes), rng.randrange(n_orb),
                ))
            for idx, (cg1, cg2, calpha, cbeta, m1, d1, frob1, m2, d2) in enumerate(cases):
                R1, R2 = build_parametric_rows(
                    ff, cg1, cg2, calpha, cbeta,
                    m1=m1, d1=d1, frob1=frob1, m2=m2, d2=d2
                )
                p_dep1, p_dep2, p_both = check_all_6tuples(ff, R1, R2)
                cmd = [
                    c_bin, "check",
                    str(q),
                    str(cg1[0]), str(cg1[1]),
                    str(cg2[0]), str(cg2[1]),
                    str(calpha[0]), str(calpha[1]),
                    str(cbeta[0]), str(cbeta[1]),
                    str(m1), str(d1), str(frob1), str(m2), str(d2),
                ]
                out = subprocess.check_output(cmd, text=True).strip()
                data = json.loads(out)
                assert data["dep1"] == p_dep1, f"q={q} case {idx} dep1 mismatch: C={data['dep1']} Py={p_dep1}"
                assert data["dep2"] == p_dep2, f"q={q} case {idx} dep2 mismatch: C={data['dep2']} Py={p_dep2}"
                assert data["both"] == p_both, f"q={q} case {idx} both mismatch: C={data['both']} Py={p_both}"
                print(
                    f"  [PASS] q={q} case {idx}: m1={m1},d1={d1},frob1={frob1},m2={m2},d2={d2} "
                    f"dep1={sum(p_dep1)} dep2={sum(p_dep2)} both={p_both} (sum={sum(p_both)})"
                )
        print("  [PASS] 100% agreement between C checker and independent Python reference!")


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def verify_json_file(path: str, rollout_path: str = None):
    t0 = time.time()
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    q = obj["q"]
    R1 = obj["R1"]
    R2 = obj["R2"]
    n_orb_a = obj.get("n_orbit_a", len(R1) // 2)
    ff = FiniteField(q)
    dep1, dep2, both = check_all_6tuples(ff, R1, R2, n_orbit_a=n_orb_a)
    unc = sum(both)
    dt = time.time() - t0
    print(f"Verified {path}: q={q}, k={len(R1)}, unc={unc}, time={dt:.3f}s")
    print(f"  dep1={dep1}, dep2={dep2}, both={both}")

    # Negative control: duplicate column 0 into column 1 in both rows
    R1_bad = [list(c) for c in R1]
    R2_bad = [list(c) for c in R2]
    R1_bad[1] = list(R1_bad[0])
    R2_bad[1] = list(R2_bad[0])
    _, _, both_bad = check_all_6tuples(ff, R1_bad, R2_bad, n_orbit_a=n_orb_a)
    unc_bad = sum(both_bad)
    print(f"  Negative control (duplicate col 0->1): unc={unc_bad} ({'FAIL as expected' if unc_bad > 0 else 'UNEXPECTED PASS'})")
    assert unc_bad > 0

    # Sherwood hyperplane check
    v1 = find_sherwood_hyperplane(ff, R1)
    v2 = find_sherwood_hyperplane(ff, R2)
    print(f"  Sherwood hyperplanes: Row1={v1}, Row2={v2}")
    if v1 is not None and v2 is not None:
        print(f"  -> Sherwood form available: N = 2*q^6 - q = {2 * (q**6) - q}")
    else:
        print(f"  -> Standard form: N = 2*q^6 - 1 = {2 * (q**6) - 1}")

    if rollout_path and unc == 0:
        n_rows, sher, _, _ = rollout_ca(ff, R1, R2, rollout_path)
        print(f"  Rolled out CA({n_rows}; 6, {len(R1)}, {q}) (sherwood={sher}) to {rollout_path}")

    return unc == 0


def main():
    parser = argparse.ArgumentParser(description="Independent Phase 9B CPHF(2; k, q, 6) verifier")
    parser.add_argument("--gate0", action="store_true", help="Run Gate 0 checks")
    parser.add_argument("--c-bin", type=str, default="", help="Path to compiled C binary for Gate 0 cross-check")
    parser.add_argument("--verify-json", type=str, default="", help="Verify a saved CPHF JSON file")
    parser.add_argument("--rollout", type=str, default="", help="Roll out verified CPHF to CA text file")
    args = parser.parse_args()

    if args.gate0:
        run_gate0(args.c_bin)
    elif args.verify_json:
        ok = verify_json_file(args.verify_json, args.rollout or None)
        sys.exit(0 if ok else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
