#!/usr/bin/env python3
"""Phase 8: Exakte ganzzahlige Untergrenzen Satz C.1 (ungerade Primzahlen) und
Satz C.2 (Quadrat-Primzahlpotenzen) fuer das Modell M(R) bei v = q.

Standardbibliothek (std-only), keine Suche, deterministisch, Laufzeit < 10 s.

Belegart:
  Satz C.1 und Satz C.2 sind informelle Argumente aus Vorwaerts-Recherche
  (siehe docs/phase8/NOTIZ_4_UNTERGRENZEN_C1_C2.md), hier exakt ausgewertet
  und gegen alle existierenden v = q Listen im Repository geprueft.
  Regel-2d-Pruefung steht aus.
"""

from __future__ import annotations

import glob
import math
import os
import re
import sys
import time
from fractions import Fraction


PRIMES = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
SQUARES = [4, 9, 16, 25, 49, 64, 81]

EXPECTED_C1 = {
    3: 12,
    5: 34,
    7: 66,
    11: 163,
    13: 228,
    17: 388,
    19: 485,
    23: 710,
    29: 1128,
}

EXPECTED_C2 = {
    4: 20,
    9: 99,
    16: 304,
    25: 725,
    49: 2694,
}

# Referenzwerte Baer-v3 (aus Auftragsbeschreibung, falls keine eigene Datei vorliegt)
BAER_V3_REF = {
    9: 108,
    16: 334,
    25: 791,
}


def c1_value(p: int, bl: int, ha: int, hb: int, U: int, V: int, t11: int) -> int:
    """Exakter Wert max(e1, e2, e3a, e3b, e4, e5a, e5b, e6) fuer ein 5-Tupel."""
    uA = ha - U
    uB = hb - V
    F = U + V + t11
    S = 0 if t11 == 0 else min(ha * hb, U * V + F)
    p2 = p * p
    e1 = p * ha + (p - ha) * bl
    e2 = p * hb + (p - hb) * bl
    e3a = (p2 + p * F + p * ha - S + (p - ha) * bl + 1) // 2
    e3b = (p2 + p * F + p * hb - S + (p - hb) * bl + 1) // 2
    e4 = (p * (ha + hb) + (2 * p - ha - hb) * bl + ha * hb - S + 1) // 2
    e5a = (p * (ha + hb) + (p - hb) * bl + ha * hb - S + (p - ha) * (p + uB - 1) + 1) // 2
    e5b = (p * (ha + hb) + (p - ha) * bl + ha * hb - S + (p - hb) * (p + uA - 1) + 1) // 2
    e6 = p2 + p * (U if U >= V else V)
    return max(e1, e2, e3a, e3b, e4, e5a, e5b, e6)


def bound_c1_bruteforce(p: int) -> tuple[int, tuple[int, int, int, int, int]]:
    """Vollstaendige 5-fach-Schleife (Referenz fuer kleine Primzahlen)."""
    bl = (3 * p + 1) // 2
    best = 10**18
    witness = (0, 0, 0, 0, 0)
    for ha in range(p + 1):
        u_max = 0 if ha == 0 else ha - 1
        for hb in range(ha, p + 1):
            v_max = 0 if hb == 0 else hb - 1
            for U in range(u_max + 1):
                uA = ha - U
                for V in range(v_max + 1):
                    uB = hb - V
                    lo = max(0, uA + uB - p)
                    hi = min(uA, uB)
                    for t11 in range(lo, hi + 1):
                        val = c1_value(p, bl, ha, hb, U, V, t11)
                        if val < best:
                            best = val
                            witness = (ha, hb, U, V, t11)
    return best, witness


def bound_c1_exact(p: int) -> tuple[int, tuple[int, int, int, int, int]]:
    """Exakte ganzzahlige Schranke Satz C.1 mit exakter Branch-and-Bound-Reduktion in t11.

    Begruendung der Exaktheit der t11-Reduktion fuer t11 >= 1:
      - e1 >= e2 und e3a >= e3b wegen ha <= hb und bl > p.
      - Fuer t11 >= 1 ist S(t11) = min(ha*hb, U*V + U + V + t11) monoton steigend in t11,
        waehrend p*t11 - S(t11) streng steigend (p >= 3) ist.
      - Damit ist inc(t11) = e3a(t11) streng steigend und dec(t11) = max(e4, e5a, e5b)
        monoton fallend fuer t11 >= 1.
      - Der Schnittpunkt der Zaehler vor Division durch 2 ist t* = (A_const - B_const) // p,
        unabhaengig von S(t11), weil -S(t11) auf beiden Seiten identisch eingeht.
      - Das Minimum ueber t11 in [max(1, lo), hi] wird daher exakt bei clamp(t*) oder
        clamp(t* + 1) angenommen; t11 == 0 wird bei lo == 0 separat geprueft.
    """
    bl = (3 * p + 1) // 2
    p2 = p * p
    best = p * bl  # gueltiger Startwert bei (0, 0, 0, 0, 0)
    witness = (0, 0, 0, 0, 0)

    # ha absteigend: e1 = p*ha + (p - ha)*bl waechst streng bei fallendem ha
    for ha in range(p, -1, -1):
        e1 = p * ha + (p - ha) * bl
        if e1 >= best:
            break
        u_max_ha = 0 if ha == 0 else ha - 1
        p_ha = p * ha
        pm_ha = p - ha
        pm_ha_bl = pm_ha * bl

        for hb in range(ha, p + 1):
            v_max_hb = 0 if hb == 0 else hb - 1
            hahb = ha * hb
            p_hab = p * (ha + hb)
            pm_hb = p - hb
            pm_hb_bl = pm_hb * bl
            e4_noS = p_hab + pm_ha_bl + pm_hb_bl + hahb
            e5a_base = p_hab + pm_hb_bl + hahb
            e5b_base = p_hab + pm_ha_bl + hahb
            e3a_base = p2 + p_ha + pm_ha_bl

            uv_cap = (best - 1 - p2) // p
            if uv_cap < 0:
                continue
            u_lim = u_max_ha if u_max_ha <= uv_cap else uv_cap
            v_lim_base = v_max_hb if v_max_hb <= uv_cap else uv_cap

            for U in range(u_lim + 1):
                # Nachfuehrung von uv_cap falls best geschrumpft ist
                if p2 + p * U >= best:
                    break
                uA = ha - U
                e5b_noS = e5b_base + pm_hb * (p + uA - 1)
                v_cap = (best - 1 - p2) // p
                v_lim = v_lim_base if v_lim_base <= v_cap else v_cap

                for V in range(v_lim + 1):
                    uB = hb - V
                    lo = uA + uB - p
                    if lo < 0:
                        lo = 0
                    hi = uA if uA < uB else uB
                    if lo > hi:
                        continue

                    e5a_noS = e5a_base + pm_ha * (p + uB - 1)
                    A_const = e4_noS
                    if e5a_noS > A_const:
                        A_const = e5a_noS
                    if e5b_noS > A_const:
                        A_const = e5b_noS

                    e6 = p2 + p * (U if U >= V else V)
                    base_floor = e1 if e1 >= e6 else e6
                    B_const = e3a_base + p * (U + V)

                    # Fall t11 == 0
                    if lo == 0:
                        # S = 0
                        inc0 = (B_const + 1) // 2
                        dec0 = (A_const + 1) // 2
                        val0 = base_floor
                        if inc0 > val0:
                            val0 = inc0
                        if dec0 > val0:
                            val0 = dec0
                        if val0 < best:
                            best = val0
                            witness = (ha, hb, U, V, 0)

                    # Fall t11 in [max(1, lo), hi]
                    lo1 = 1 if lo == 0 else lo
                    if lo1 <= hi:
                        t_star = (A_const - B_const) // p
                        cands = []
                        if t_star < lo1:
                            cands.append(lo1)
                        elif t_star >= hi:
                            cands.append(hi)
                        else:
                            cands.append(t_star)
                            cands.append(t_star + 1)
                        uv_prod = U * V + U + V
                        for t11 in cands:
                            S = uv_prod + t11
                            if S > hahb:
                                S = hahb
                            inc = (B_const + p * t11 - S + 1) // 2
                            dec = (A_const - S + 1) // 2
                            val = base_floor
                            if inc > val:
                                val = inc
                            if dec > val:
                                val = dec
                            if val < best:
                                best = val
                                witness = (ha, hb, U, V, t11)

    # Nachpruefung des Zeugen mit der vollen Definition
    assert c1_value(p, bl, *witness) == best
    return best, witness


def c2_value(q: int, n: int, kA: int, kB: int, hA: int, hB: int) -> int:
    """Exakter Wert LB = q^2 + E fuer ein 4-Tupel in Satz C.2."""
    c1X = (q - kA) * n
    c2X = max((q - kB) * n + (hA - 1) * kB, (hA - 1) * q)
    eX = max(c1X, (c1X + c2X + 1) // 2)
    c1Y = (q - kB) * n
    c2Y = max((q - kA) * n + (hB - 1) * kA, (hB - 1) * q)
    eY = max(c1Y, (c1Y + c2Y + 1) // 2)
    E = max(eX, eY, (kA - hA) * q, (kB - hB) * q)
    return q * q + E


def bound_c2_bruteforce(q: int) -> tuple[int, tuple[int, int, int, int]]:
    """Vollstaendige 4-fach-Schleife (Referenz fuer kleine Quadratzahlen)."""
    n = math.isqrt(q)
    assert n * n == q
    best = 10**18
    witness = (0, 0, 0, 0)
    for kA in range(q + 1):
        hA_range = [0] if kA == 0 else range(1, kA + 1)
        for kB in range(kA, q + 1):
            hB_range = [0] if kB == 0 else range(1, kB + 1)
            for hA in hA_range:
                for hB in hB_range:
                    val = c2_value(q, n, kA, kB, hA, hB)
                    if val < best:
                        best = val
                        witness = (kA, kB, hA, hB)
    return best, witness


def bound_c2_exact(q: int) -> tuple[int, tuple[int, int, int, int]]:
    """Exakte ganzzahlige Schranke Satz C.2 ueber exakte Separierung von hA und hB.

    Fuer feste (kA, kB) haengen eX und (kA - hA)*q nur von hA ab, waehrend eY und
    (kB - hB)*q nur von hB abhaengen. Daher gilt exakt:
      min_{hA, hB} E = max( min_{hA} max(eX, (kA - hA)*q), min_{hB} max(eY, (kB - hB)*q) ).
    """
    n = math.isqrt(q)
    assert n * n == q
    best_E = 10**18
    witness = (0, 0, 0, 0)

    for kA in range(q + 1):
        c1X = (q - kA) * n
        hA_iter = (0,) if kA == 0 else range(1, kA + 1)
        for kB in range(kA, q + 1):
            c1Y = (q - kB) * n
            hB_iter = (0,) if kB == 0 else range(1, kB + 1)

            best_X = 10**18
            best_hA = 0
            for hA in hA_iter:
                t1 = c1Y + (hA - 1) * kB
                t2 = (hA - 1) * q
                c2X = t1 if t1 >= t2 else t2
                eX = (c1X + c2X + 1) // 2
                if c1X > eX:
                    eX = c1X
                penA = (kA - hA) * q
                vX = eX if eX >= penA else penA
                if vX < best_X:
                    best_X = vX
                    best_hA = hA
            if best_X >= best_E:
                continue

            best_Y = 10**18
            best_hB = 0
            for hB in hB_iter:
                t1 = c1X + (hB - 1) * kA
                t2 = (hB - 1) * q
                c2Y = t1 if t1 >= t2 else t2
                eY = (c1Y + c2Y + 1) // 2
                if c1Y > eY:
                    eY = c1Y
                penB = (kB - hB) * q
                vY = eY if eY >= penB else penB
                if vY < best_Y:
                    best_Y = vY
                    best_hB = hB

            E = best_X if best_X >= best_Y else best_Y
            if E < best_E:
                best_E = E
                witness = (kA, kB, best_hA, best_hB)

    lb = q * q + best_E
    assert c2_value(q, n, *witness) == lb
    return lb, witness


def is_odd_prime(n: int) -> bool:
    if n < 3 or n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def is_square_prime_power(q: int) -> bool:
    n = math.isqrt(q)
    if n * n != q or n < 2:
        return False
    # pruefe ob n Primzahlpotenz ist
    tmp = n
    d = 2
    while d * d <= tmp:
        if tmp % d == 0:
            while tmp % d == 0:
                tmp //= d
            return tmp == 1
        d += 1
    return True


def collect_vq_lists(root: str) -> list[tuple[str, int, int]]:
    """Sammelt alle v = q Listen aus data/phase7, phase8, phase8_repro, phase8_baer,
    phase8_baer_repro und phase8_q16_hybrid (falls vorhanden)."""
    dirs = [
        "data/phase7",
        "data/phase8",
        "data/phase8_repro",
        "data/phase8_baer",
        "data/phase8_baer_repro",
        "data/phase8_q16_hybrid",
    ]
    out = []
    for rel in dirs:
        dpath = os.path.join(root, rel)
        if not os.path.isdir(dpath):
            continue
        for path in sorted(glob.glob(os.path.join(dpath, "R_*.txt"))):
            fname = os.path.basename(path)
            m = re.search(r"R_q(\d+)(?:_v(\d+))?", fname)
            if not m:
                continue
            q = int(m.group(1))
            v = int(m.group(2)) if m.group(2) else q
            if v != q:
                continue
            with open(path) as fh:
                cnt = sum(1 for ln in fh if ln.split("#")[0].strip())
            out.append((os.path.join(rel, fname), q, cnt))
    return out


def main() -> int:
    t0 = time.perf_counter()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 1. Selbsttest: schnelle exakte Auswertung == Brute-Force auf kleinen Instanzen
    for p in [3, 5, 7, 11, 13, 17]:
        fast_val, _ = bound_c1_exact(p)
        bf_val, _ = bound_c1_bruteforce(p)
        assert fast_val == bf_val, f"C.1 mismatch at p={p}: fast={fast_val} != bf={bf_val}"
    for q in [4, 9, 16, 25]:
        fast_val, _ = bound_c2_exact(q)
        bf_val, _ = bound_c2_bruteforce(q)
        assert fast_val == bf_val, f"C.2 mismatch at q={q}: fast={fast_val} != bf={bf_val}"

    # 2. Satz C.1 fuer alle geforderten Primzahlen
    c1_map: dict[int, int] = {}
    print("=== SATZ C.1 (ungerade Primzahlen p, v = p; Asymptotik 91/68 = 1.338235...) ===")
    print(f"{'p':>4} | {'LB_C1':>6} | {'LB/p^2':>8} | {'91/68*p^2':>9} | {'Zeuge (ha,hb,U,V,t11)':>24} | {'Soll':>6}")
    print("-" * 74)
    for p in PRIMES:
        lb, wit = bound_c1_exact(p)
        c1_map[p] = lb
        soll = EXPECTED_C1.get(p)
        if soll is not None:
            assert lb == soll, f"C.1 Soll-Abweichung bei p={p}: {lb} != {soll}"
        soll_str = f"{soll} OK" if soll is not None else "-"
        asym = 91 * p * p / 68
        print(f"{p:4d} | {lb:6d} | {lb/(p*p):8.5f} | {asym:9.2f} | {str(wit):>24} | {soll_str:>6}")

    # 3. Satz C.2 fuer alle geforderten Quadrat-Primzahlpotenzen
    c2_map: dict[int, int] = {}
    print("\n=== SATZ C.2 (Quadrat-Primzahlpotenzen q = n^2, v = q; Asymptotik q^2 + q^(3/2) - (9/8)q) ===")
    print(f"{'q':>4} | {'n':>2} | {'LB_C2':>6} | {'E=LB-q^2':>8} | {'(E-q*n)/q':>9} | {'Zeuge (kA,kB,hA,hB)':>22} | {'Soll':>6}")
    print("-" * 76)
    for q in SQUARES:
        n = math.isqrt(q)
        lb, wit = bound_c2_exact(q)
        c2_map[q] = lb
        soll = EXPECTED_C2.get(q)
        if soll is not None:
            assert lb == soll, f"C.2 Soll-Abweichung bei q={q}: {lb} != {soll}"
        soll_str = f"{soll} OK" if soll is not None else "-"
        E = lb - q * q
        coeff = (E - q * n) / q
        print(f"{q:4d} | {n:2d} | {lb:6d} | {E:8d} | {coeff:9.4f} | {str(wit):>22} | {soll_str:>6}")

    # 4. Pruefung aller existierenden v = q Listen im Repo + Baer-v3 Vergleichswerte
    print("\n=== PRUEFUNG GEGEN ALLE v = q LISTEN IM REPO + BAER-V3 REFERENZ ===")
    vq_lists = collect_vq_lists(root)
    violations = 0
    checked_c1 = 0
    checked_c2 = 0
    print(f"{'Quelle':<45} | {'q':>3} | {'|R|':>5} | {'Satz':>4} | {'LB':>5} | {'Diff':>5} | {'Status'}")
    print("-" * 86)
    for relpath, q, m_val in vq_lists:
        if is_odd_prime(q):
            lb = c1_map[q] if q in c1_map else bound_c1_exact(q)[0]
            satz = "C.1"
            checked_c1 += 1
        elif is_square_prime_power(q):
            lb = c2_map[q] if q in c2_map else bound_c2_exact(q)[0]
            satz = "C.2"
            checked_c2 += 1
        else:
            print(f"{relpath:<45} | {q:3d} | {m_val:5d} | {'n/a':>4} | {'-':>5} | {'-':>5} | nicht C.1/C.2")
            continue
        diff = m_val - lb
        ok = diff >= 0
        if not ok:
            violations += 1
        print(f"{relpath:<45} | {q:3d} | {m_val:5d} | {satz:>4} | {lb:5d} | {diff:+5d} | {'OK' if ok else 'VIOLATION'}")

    for q, m_val in sorted(BAER_V3_REF.items()):
        lb = c2_map[q]
        diff = m_val - lb
        ok = diff >= 0
        if not ok:
            violations += 1
        checked_c2 += 1
        print(f"{f'[Ref Baer-v3] q={q}, v={q}':<45} | {q:3d} | {m_val:5d} | {'C.2':>4} | {lb:5d} | {diff:+5d} | {'OK' if ok else 'VIOLATION'}")

    elapsed = time.perf_counter() - t0
    print(f"\nGepruefte v=q Eintraege: C.1={checked_c1}, C.2={checked_c2} (inkl. 3 Baer-v3 Ref), Verletzungen={violations}, Laufzeit={elapsed:.3f} s")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
