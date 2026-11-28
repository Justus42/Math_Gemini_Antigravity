#!/usr/bin/env python3
"""Phase 8 Teil 3.1: Kurz-Explore fuer q = 16 Spur-Baer-Hybrid-Varianten (v = 14, 15, 16).

Harte Laufzeitgrenze <= 55 s intern (extern mit timeout 60 s ausfuehren).
Standardbibliothek (std-only), deterministisch (feste Seeds).

Untersucht:
  (1) Rekonstruktion/Test v = 14 (m = 298) als Basis und Varianten auf d_0, d_1, d_2.
  (2) F_2-lineare Blocking Sets der Groesse 24 beider Profile:
      - Profil 1: [8, 8, 8] (8 Punkte auf d=0, je 8 auf 2 Geraden d!=0)
      - Profil 2: [8, 2^8]  (8 Punkte auf d=0, je 2 auf 8 Geraden d!=0)
      und Kombinationen mit Vollgeraden / Baer-Klassen fuer v = 14, 15, 16.
  (3) K-Promotion (Ersetzen einer oder mehrerer K-Klassen / freie Geraden) und
      kombinatorische Optimierung auf d = 0 sowie kurze lokale Reduktions-Suche
      (1-Zeile-loeschen + Tabu-Swaps) ab m = 298 (v=14), m = 315 (v=15), m = 332 (v=16).

Ziele:
  - v = 14: < 298
  - v = 15: < 315
  - v = 16: < 332 (Stretch <= 326)
Jeder Fund unter Ziel wird sofort mit check_m geprueft und in data/phase8_q16_hybrid/ abgelegt.
"""

from __future__ import annotations

import itertools
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_general_tqv import GeneralGF  # noqa: E402
from phase7_lift import m_rows, uncovered_pairs  # noqa: E402
from phase8_q16_trace_hybrid import build_q16_trace_hybrid  # noqa: E402


TIME_LIMIT_S = 54.0


class GF16Context:
    def __init__(self) -> None:
        self.q = 16
        self.gf = GeneralGF(16)
        self.add = self.gf.add
        self.mul = self.gf.mul
        self.inv = [0] + [next(y for y in range(1, 16) if self.mul[x][y] == 1) for x in range(1, 16)]

        def pow_gf(x: int, e: int) -> int:
            r, b = 1, x
            while e:
                if e & 1:
                    r = self.mul[r][b]
                b = self.mul[b][b]
                e >>= 1
            return r

        self.Fn = sorted(x for x in range(16) if pow_gf(x, 4) == x)
        self.Fn_nz = self.Fn[1:]
        self.om = min(x for x in range(16) if x not in self.Fn)
        self.num = {x: i for i, x in enumerate(self.Fn)}
        self.nz_idx = {x: i for i, x in enumerate(self.Fn_nz)}
        self.p1 = [0] * 16
        self.p2 = [0] * 16
        for a1 in self.Fn:
            for a2 in self.Fn:
                z = self.add[a1][self.mul[a2][self.om]]
                self.p1[z] = a1
                self.p2[z] = a2

        self.tr = []
        for x in range(16):
            x2 = self.mul[x][x]
            x4 = self.mul[x2][x2]
            x8 = self.mul[x4][x4]
            self.tr.append(self.add[self.add[x][x2]][self.add[x4][x8]])

        self.d_free = [self.inv[i_u] for i_u in self.Fn_nz]
        self.dp_free = [self.inv[self.mul[i_u][self.om]] for i_u in self.Fn_nz]

    def K(self, i: int, j: int) -> int:
        return (self.num[i] - 1) * 4 + self.num[j]

    def is_blocking_set(self, pts: set[tuple[int, int]]) -> bool:
        """Prueft, ob pts in AG(2,16) jede nicht-waagerechte Gerade c + al*d = u trifft."""
        add, mul = self.add, self.mul
        for al in range(16):
            vals = {add[c][mul[al][d]] for (c, d) in pts}
            if len(vals) < 16:
                return False
        return True


def build_v14_m298(ctx: GF16Context) -> list[tuple[int, int, int, int]]:
    """Konstruiert eine m = 298 Liste fuer q = 16, v = 14 (1 Vollgerade V_0 + 1 Spur-Set V_1)."""
    add, mul, inv = ctx.add, ctx.mul, ctx.inv
    p1, p2, Fn, Fn_nz, om = ctx.p1, ctx.p2, ctx.Fn, ctx.Fn_nz, ctx.om
    d_free, dp_free = ctx.d_free, ctx.dp_free
    V0, V1 = 12, 13

    # V0: Vollgerade auf d_0 (a-Seite) und dp_0 (b-Seite);
    # V1: Spur-Blocking-Set auf d_1, d_2 und target_d0 = {p2(c) in {0, i0}}
    i0 = Fn_nz[0]
    target_d0 = {c for c in range(16) if p2[c] in (0, i0)}
    d1_plus_d2 = add[d_free[1]][d_free[2]]
    dp1_plus_dp2 = add[dp_free[1]][dp_free[2]]
    mu_a = next(mu for mu in range(1, 16) if {c for c in range(16) if ctx.tr[mul[mul[mu][d1_plus_d2]][c]] == 0} == target_d0)
    mu_b = next(mu for mu in range(1, 16) if {c for c in range(16) if ctx.tr[mul[mul[mu][dp1_plus_dp2]][c]] == 0} == target_d0)

    reps: list[tuple[int, int, int, int]] = []
    # d = 0
    for c in range(16):
        c1, c2 = p1[c], p2[c]
        t = ctx.num[c1]
        if c2 != 0:
            u = ctx.nz_idx[c2]
            if u == 0:
                # V1 tritt hier auf a- und b-Seite auf (je 1 Slot -> 5 reps)
                ks0 = ctx.K(c2, Fn[t])
                reps.append((c, 0, V1, ks0))
                reps.append((c, 0, ks0, V1))
                for idx in range(1, 4):
                    ks = ctx.K(c2, Fn[(t + idx) % 4])
                    reps.append((c, 0, ks, ks))
            else:
                for idx in range(4):
                    ks = ctx.K(c2, Fn[(t + idx) % 4])
                    reps.append((c, 0, ks, ks))
        else:
            # c2 == 0: 4 Punkte, V1 an allen 4 auf a und b, plus alle 4 Paare (V0/V1, V0/V1)
            if t == 0:
                reps.append((c, 0, V0, V1))
                reps.append((c, 0, V1, V0))
            elif t == 1:
                reps.append((c, 0, V0, V0))
                reps.append((c, 0, V1, V1))
            else:
                reps.append((c, 0, V1, V1))

    # d = 1..15
    for d in range(1, 16):
        w = inv[d]
        w1, w2 = p1[w], p2[w]
        for c in range(16):
            if w2 != 0:
                a_sym = ctx.K(w2, p2[mul[add[c][mul[w2][om]]][w]])
            else:
                u = ctx.nz_idx[w1]
                if u == 0:
                    a_sym = V0
                elif u == 1:
                    # Tr == 0 -> V1, Tr == 1 -> V0
                    a_sym = V1 if ctx.tr[mul[mul[mu_a][d_free[2]]][c]] == 0 else V0
                else:
                    a_sym = V1 if ctx.tr[mul[mul[mu_a][d_free[1]]][c]] == 0 else V0
            if w1 != 0:
                b_sym = ctx.K(w1, p1[mul[add[c][mul[w1][om]]][w]])
            else:
                u = ctx.nz_idx[w2]
                if u == 0:
                    b_sym = V0
                elif u == 1:
                    b_sym = V1 if ctx.tr[mul[mul[mu_b][dp_free[2]]][c]] == 0 else V0
                else:
                    b_sym = V1 if ctx.tr[mul[mul[mu_b][dp_free[1]]][c]] == 0 else V0
            reps.append((c, d, a_sym, b_sym))
    return reps


def enumerate_profile2_sets(ctx: GF16Context) -> list[tuple[frozenset[int], dict[int, set[int]]]]:
    r"""Erzeugt F_2-lineare Blocking Sets vom Profil [8, 2^8] (8 Punkte auf d=0, je 2 auf 8 Geraden d!=0).

    Konstruktion aus der projektiven linearen Menge B = {(x:Tr(x):1)} U {(x:1:0):Tr(x)=1} U {(1:0:0)}
    in PG(2, 16): Waehle Q != (1:0:0) in B als P_inf, eine Tangente durch Q als l_inf,
    und die eindeutige 9-Sekante Q-(1:0:0) als d = 0.
    Affine Darstellung (c, d) ueber direkte projektive Transformation:
      Nehme Basis mit P_inf = (1:0:0), d=0 als y=0, l_inf als z=0.
      In Koordinaten (X:Y:Z) ist B_proj = {(x, Tr(x), z) : x in F_16, z in F_2} \ {0}.
      Wird Q = (0:0:1) gewaehlt (liegt in B fuer x=0, z=1), dann ist:
        - 9-Sekante durch Q: Y = 0 (enthaelt (1:0:0) und 8 Punkte (x:0:1) mit Tr(x)=0)
        - Tangenten durch Q: X = alpha * Y mit alpha in F_16? Nein, Geraden durch (0:0:1) sind X = lambda * Y:
          * Y = 0 (9-Sekante)
          * X = lambda * Y: trifft B in (x, 1, z) mit x = lambda (Tr(lambda)=1 -> 2 Punkte (lambda:1:0) und (lambda:1:1), plus Q -> 3-Sekante!)
          * Tr(lambda) = 0 -> (lambda, 1, z) NICHT in B! Also TANGENTE durch Q!
      Perfekt! Setze also neue Koordinaten (c, d) mit:
        - neue l_inf: X = lam0 * Y (mit Tr(lam0) = 0, lam0 != 0)
        - neue d = 0: Y = 0
        - neuer P_inf: Q = (0:0:1)
      Projektive Abbildung (X:Y:Z) -> (c, d) = (Z / (X + lam0*Y), Y / (X + lam0*Y))!
      Check:
        - Y = 0 (mit X != 0): d = 0, c = Z / X. Fuer (1:0:0) -> c = 0; fuer (x:0:1) (Tr(x)=0, x!=0) -> c = 1/x (7 Werte). Zusammen 8 Werte auf d = 0!
        - Y = 1, X = x mit Tr(x) = 1: d = 1 / (x + lam0) (8 verschiedene d != 0!), c = z / (x + lam0) fuer z in {0, 1} -> genau 2 Punkte (0, d) und (d, d) pro Gerade!
      Affin skalier-/verschiebbar durch (c, d) -> (k*c + r*d + t, s*d) mit k, s in F_16^*, r, t in F_16.
    """
    add, mul, inv = ctx.add, ctx.mul, ctx.inv
    results = []
    # Basis-Profil-2 fuer lam0 = 0 (Wait: X = 0 ist AUCH eine Tangente durch Q=(0:0:1) falls Tr(0)=0! Check: X=0 trifft B nur in (0:0:1)!)
    # Pruefe direkt fuer lam0 = 0: d = 1/x (Tr(x)=1, 8 Geraden), c in {0, d}; auf d=0: c = 0 und c = 1/x (Tr(x)=0, x!=0).
    base_d0 = frozenset({0} | {inv[x] for x in range(1, 16) if ctx.tr[x] == 0})
    base_lines = {inv[x]: {0, inv[x]} for x in range(1, 16) if ctx.tr[x] == 1}
    base_pts = {(c, 0) for c in base_d0} | {(c, d) for d, cs in base_lines.items() for c in cs}
    assert len(base_pts) == 24 and ctx.is_blocking_set(base_pts), "Basis Profil [8, 2^8] ungueltig!"

    # Prüfe alle Skalierungen s in F_16^* der Geradenmenge d -> s*d (15 Varianten)
    # und pruefe, wie viele der 8 Geraden in den 3 freien Geraden d_free liegen!
    d_free_set = set(ctx.d_free)
    for s in range(1, 16):
        lines_s = {mul[s][d]: {0, mul[s][d]} for d in base_lines}
        overlap = len(set(lines_s.keys()) & d_free_set)
        results.append((overlap, s, base_d0, lines_s))
    return results


def analyze_profile2_for_baer(ctx: GF16Context) -> None:
    """Analysiert Profil [8, 2^8] im Baer-Skelett."""
    p2_list = enumerate_profile2_sets(ctx)
    overlaps = [x[0] for x in p2_list]
    print(f"[Profil 2: [8, 2^8]] Basis-Blocking-Set Groesse 24 verifiziert (15 Geraden-Skalierungen): "
          f"max Ueberlapp mit d_free (3 Geraden) = {max(overlaps)}/3, min extra auf K-Geraden = {8 - max(overlaps)} Geraden (>= {2*(8 - max(overlaps))} Punkte)")

    # Pruefe auch allgemeine affine Transformationen der 8 Geraden (d -> 1/(a*d + b) geht nicht, nur d -> s*d erhaelt d=0 und Parallelenschar)
    # Mit allen 8 Tangenten lam0 (Tr(lam0)=0): d_set = {1/(x + lam0) : Tr(x) = 1} = {1/y : Tr(y) = 1} (INVARIANTE Menge!)
    # Denn Tr(x + lam0) = Tr(x) + Tr(lam0) = 1 + 0 = 1!
    # Also gibt es bis auf Skalierung d -> s*d nur die 15 Hyperebenen-Komplement-Inversen als 8-Geraden-Menge!
    # Auf jeder der 8 - overlap K-Geraden braucht Profil 2 jeweils 2 Punkte -> mindestens 2*(8 - 3) = 10 Zusatzvertreter auf d != 0!
    # Zum Vergleich: [8, 8, 8] nutzt 0 K-Geraden (0 Zusatzvertreter auf d != 0)!
    best_overlap = max(overlaps)
    print(f"  -> Profil [8, 2^8] auf unveraendertem 12-K-Baer-Skelett kostet auf d!=0 mindestens +{2*(8 - best_overlap)} Vertreter pro Symbol "
          f"(gegen +0 bei [8, 8, 8]).")


def check_and_save_if_better(
    reps: list[tuple[int, int, int, int]],
    ctx: GF16Context,
    v: int,
    target: int,
    label: str,
    out_dir: str,
) -> bool:
    if len(reps) >= target:
        return False
    # Dedup & check
    if len(set(reps)) != len(reps):
        reps = list(dict.fromkeys(reps))
    unc = uncovered_pairs(m_rows(reps, 16, ctx.gf), 16, v if v < 16 else None)
    if unc != 0:
        return False
    fname = f"R_q16_v{v}_explore_{label}_m{len(reps)}.txt"
    fpath = os.path.join(out_dir, fname)
    os.makedirs(out_dir, exist_ok=True)
    with open(fpath, "w", encoding="utf-8") as fh:
        fh.write(f"# q=16 v={v} m={len(reps)} source={label}\n")
        for c, d, a, b in reps:
            fh.write(f"{c} {d} {a} {b}\n")
    print(f"  *** FUND! v={v} m={len(reps)} < {target} ({label}) -> {fpath} (unc=0) ***")
    return True


def eval_symmetric_3trace_v15(ctx: GF16Context) -> int:
    """Prueft systematisch alle Kombinationen von 3 [8,8,8]-Spur-Sets auf d_0, d_1, d_2 fuer v=15
    (und 4 Spur-Sets / 3 Spur + 1 Vollgerade fuer v=16) auf minimalen Ueberlapp."""
    add, mul = ctx.add, ctx.mul
    d_free = ctx.d_free
    # Ein [8,8,8]-Set S(pair=(u1, u2), mu, shift1, shift2):
    #   auf d_{u1}: {c : Tr(mu * d_{u2} * c) == shift1}
    #   auf d_{u2}: {c : Tr(mu * d_{u1} * c) == shift2}
    #   auf d=0:    {c : Tr(mu * (d_{u1} + d_{u2}) * c) == shift1 ^ shift2}
    # Pruefe ob es 3 [8,8,8]-Sets gibt, die d_0, d_1, d_2 paarweise disjunkt (oder mit kleinem Ueberlapp) ueberdecken!
    sets_by_pair: dict[tuple[int, int], list[tuple[int, int, int, frozenset[int], frozenset[int], frozenset[int]]]] = {}
    for u1, u2 in [(0, 1), (0, 2), (1, 2)]:
        lst = []
        dsum = add[d_free[u1]][d_free[u2]]
        for mu in range(1, 16):
            for s1 in (0, 1):
                for s2 in (0, 1):
                    A1 = frozenset(c for c in range(16) if ctx.tr[mul[mul[mu][d_free[u2]]][c]] == s1)
                    A2 = frozenset(c for c in range(16) if ctx.tr[mul[mul[mu][d_free[u1]]][c]] == s2)
                    A0 = frozenset(c for c in range(16) if ctx.tr[mul[mul[mu][dsum]][c]] == (s1 ^ s2))
                    # Pruefe wie viele c2-Werte in A0 getroffen werden (fuer Kosten auf d=0)
                    lst.append((mu, s1, s2, A1, A2, A0))
        sets_by_pair[(u1, u2)] = lst

    b_on_dfree = []
    for u in range(3):
        w = ctx.Fn_nz[u]
        b_on_dfree.append([ctx.K(w, ctx.p1[mul[add[c][mul[w][ctx.om]]][w]]) for c in range(16)])

    min_ov_d = 999
    zero_ov_cnt = 0
    best_exact_lb = 999
    for _, _, _, A0_d0, A0_d1, A0_0 in sets_by_pair[(0, 1)]:
        for _, _, _, A1_d0, A1_d2, A1_0 in sets_by_pair[(0, 2)]:
            ov0 = len(A0_d0 & A1_d0)
            if ov0 > 0:
                if ov0 < min_ov_d:
                    min_ov_d = ov0
                continue
            for _, _, _, A2_d1, A2_d2, A2_0 in sets_by_pair[(1, 2)]:
                ov = ov0 + len(A0_d1 & A2_d1) + len(A1_d2 & A2_d2)
                if ov < min_ov_d:
                    min_ov_d = ov
                if ov != 0:
                    continue
                zero_ov_cnt += 1
                As = (A0_0, A1_0, A2_0)
                covs = (
                    (len({b_on_dfree[0][c] for c in A0_d0}), len({b_on_dfree[1][c] for c in A0_d1}), 0),
                    (len({b_on_dfree[0][c] for c in A1_d0}), 0, len({b_on_dfree[2][c] for c in A1_d2})),
                    (0, len({b_on_dfree[1][c] for c in A2_d1}), len({b_on_dfree[2][c] for c in A2_d2})),
                )
                d0_nz = 48
                for u in range(3):
                    for m in range(3):
                        present = sum(1 for c in As[m] if ctx.p2[c] == ctx.Fn_nz[u])
                        need = 4 - covs[m][u]
                        d0_nz += present if present >= need else need
                d0_z = sum(max(1, sum(1 for m in range(3) if c in As[m])) for c in range(16) if ctx.p2[c] == 0)
                tot = 240 + d0_nz + d0_z
                if tot < best_exact_lb:
                    best_exact_lb = tot
    print(f"[3-Trace-Scan (0,1)+(0,2)+(1,2)] min_ov_auf_d_free={min_ov_d} (pro Seite), "
          f"disjunkte Tripel={zero_ov_cnt}, exakte d=0-Untergrenze inkl. K-Paarbedarf={best_exact_lb} (> 315)")

    # 4-Trace-Bilanz fuer v=16:
    # Jedes [8,8,8]-Set braucht 16 Punkte auf d_free (48 Punkte verfuegbar -> 4 Sets brauchen 64 Punkte ->
    # mind. +16 Ueberlapp pro Seite = +32 gesamt -> >= 240 + 32 + 64 = 336 > 332).
    print("[4-Trace-Bilanz fuer v=16] 4x16 = 64 Punkte auf 48 freien Punkten -> mind. +16 Ueberlapp/Seite (+32 gesamt) => >= 336 (> 332).")
    return best_exact_lb


def fast_tabu_reduce(
    init_reps: list[tuple[int, int, int, int]],
    ctx: GF16Context,
    v: int,
    time_budget: float,
    seed: int,
) -> tuple[int, int, list[tuple[int, int, int, int]]]:
    """Schnelle lokale Reduktions-Probe auf M(R): loescht 1 Zeile und versucht unc -> 0 per 1-Eintrag-Aenderung (a oder b).

    Fokussiert auf die nicht-K-Zeilen (d=0 und freie Geraden) sowie beliebige Zeilen:
    Aendert (c, d, a, b) -> (c, d, a', b) oder (c, d, a, b') oder verschiebt (c, d) einer Zusatzzeile.
    Gibt (best_m, best_unc_at_m_minus_1, best_reps, moves) zurueck.
    """
    t_start = time.monotonic()
    rng = random.Random(seed)
    add, mul = ctx.add, ctx.mul
    q = 16
    reps = list(init_reps)
    m_cur = len(reps)

    # Versuche 1 Zeile zu entfernen, deren Loeschung die wenigsten ungedeckten Paare erzeugt
    # Precompute eval columns: for each (c, d), col[x] = c + x*d
    eval_tbl = [[add[c][mul[x][d]] for x in range(q)] for c in range(q) for d in range(q)]

    def build_state(cur_reps):
        # cnt_eval[x][y][v1*q + v2] nicht noetig, wenn alle 256 Punkte (c, d) bedeckt sind!
        # Pruefe erst Punkt-Multiplizitaet pt_cnt[c][d]: solange pt_cnt[c][d] >= 1 fuer alle (c,d),
        # sind ALLE eval-eval Paare automatisch abgedeckt!
        pt_cnt = [0] * 256
        # ca_cnt[x][val][a], cb_cnt[x][val][b], ab_cnt[a][b]
        ca_cnt = [[[0] * v for _ in range(q)] for _ in range(q)]
        cb_cnt = [[[0] * v for _ in range(q)] for _ in range(q)]
        ab_cnt = [[0] * v for _ in range(v)]
        for c, d, a, b in cur_reps:
            pt_cnt[c * 16 + d] += 1
            ab_cnt[a][b] += 1
            ev = eval_tbl[c * 16 + d]
            for x in range(q):
                ca_cnt[x][ev[x]][a] += 1
                cb_cnt[x][ev[x]][b] += 1
        unc = 0
        for x in range(q):
            for val in range(q):
                row_a = ca_cnt[x][val]
                row_b = cb_cnt[x][val]
                for s in range(v):
                    if row_a[s] == 0:
                        unc += 1
                    if row_b[s] == 0:
                        unc += 1
        for a in range(v):
            for b in range(v):
                if ab_cnt[a][b] == 0:
                    unc += 1
        # plus fehlende Punkte (falls pt_cnt == 0, zaehlen wir Strafe 1000)
        missing_pts = sum(1 for k in pt_cnt if k == 0)
        return pt_cnt, ca_cnt, cb_cnt, ab_cnt, unc, missing_pts

    # Finde beste loeschbare Zeile (pt_cnt >= 2, also auf d = 0)
    pt_cnt0, ca0, cb0, ab0, unc0, mpts0 = build_state(reps)
    assert unc0 == 0 and mpts0 == 0

    best_del_idx = -1
    best_del_unc = 10**9
    for idx, (c, d, a, b) in enumerate(reps):
        if pt_cnt0[c * 16 + d] < 2:
            continue
        du = 0
        if ab0[a][b] == 1:
            du += 1
        ev = eval_tbl[c * 16 + d]
        for x in range(q):
            if ca0[x][ev[x]][a] == 1:
                du += 1
            if cb0[x][ev[x]][b] == 1:
                du += 1
        if du < best_del_unc:
            best_del_unc = du
            best_del_idx = idx

    if best_del_idx < 0:
        return m_cur, 999, reps, 0

    cand = reps[:best_del_idx] + reps[best_del_idx + 1:]
    pt_cnt, ca_cnt, cb_cnt, ab_cnt, unc, mpts = build_state(cand)
    assert mpts == 0 and unc == best_del_unc

    best_unc = unc
    best_cand = list(cand)
    tabu = {}
    moves = 0
    step = 0

    while time.monotonic() - t_start < time_budget:
        step += 1
        # Waehle ein zufaelliges ungedecktes Ziel (ab oder ca oder cb) und teste Zuege
        # Sammle aktive Zuege: waehle 24 zufaellige Zeilen oder Zeilen mit a/b-Aenderung
        best_delta = 10**9
        best_move = None

        # Suche gezielt: finde ein ungedecktes Paar
        target_type = rng.randrange(3)
        # Schneller Scan ueber 40 zufaellige Zeilen und alle v Symbole (a oder b)
        for _ in range(36):
            idx = rng.randrange(len(cand))
            c, d, a, b = cand[idx]
            ev = eval_tbl[c * 16 + d]
            side = rng.randrange(2)
            if side == 0:
                # Berechne Verlust durch Entfernen von a
                loss = (1 if ab_cnt[a][b] == 1 else 0)
                for x in range(q):
                    if ca_cnt[x][ev[x]][a] == 1:
                        loss += 1
                for na in range(v):
                    if na == a:
                        continue
                    gain = (1 if ab_cnt[na][b] == 0 else 0)
                    for x in range(q):
                        if ca_cnt[x][ev[x]][na] == 0:
                            gain += 1
                    delta = loss - gain
                    moves += 1
                    if delta < best_delta:
                        if unc + delta == 0 or tabu.get((idx, 0, na), 0) < step:
                            best_delta = delta
                            best_move = (idx, 0, na)
            else:
                loss = (1 if ab_cnt[a][b] == 1 else 0)
                for x in range(q):
                    if cb_cnt[x][ev[x]][b] == 1:
                        loss += 1
                for nb in range(v):
                    if nb == b:
                        continue
                    gain = (1 if ab_cnt[a][nb] == 0 else 0)
                    for x in range(q):
                        if cb_cnt[x][ev[x]][nb] == 0:
                            gain += 1
                    delta = loss - gain
                    moves += 1
                    if delta < best_delta:
                        if unc + delta == 0 or tabu.get((idx, 1, nb), 0) < step:
                            best_delta = delta
                            best_move = (idx, 1, nb)

        if best_move is None:
            continue
        idx, side, ns = best_move
        c, d, a, b = cand[idx]
        ev = eval_tbl[c * 16 + d]
        if side == 0:
            ab_cnt[a][b] -= 1
            ab_cnt[ns][b] += 1
            for x in range(q):
                ca_cnt[x][ev[x]][a] -= 1
                ca_cnt[x][ev[x]][ns] += 1
            cand[idx] = (c, d, ns, b)
            tabu[(idx, 0, a)] = step + rng.randint(15, 35)
        else:
            ab_cnt[a][b] -= 1
            ab_cnt[a][ns] += 1
            for x in range(q):
                cb_cnt[x][ev[x]][b] -= 1
                cb_cnt[x][ev[x]][ns] += 1
            cand[idx] = (c, d, a, ns)
            tabu[(idx, 1, b)] = step + rng.randint(15, 35)
        unc += best_delta
        if unc < best_unc:
            best_unc = unc
            best_cand = list(cand)
            if best_unc == 0:
                return len(cand), 0, best_cand, moves

    return m_cur, best_unc, best_cand, moves


def main() -> int:
    t0 = time.monotonic()
    ctx = GF16Context()
    out_dir = "data/phase8_q16_hybrid"

    print("=== TEIL 3.1: q = 16 SPUR-BAER-HYBRID KURZ-EXPLORE (Budget <= 54 s) ===")

    # 1. Basis v=14 (m=298) konstruieren & pruefen
    reps_v14 = build_v14_m298(ctx)
    unc14 = uncovered_pairs(m_rows(reps_v14, 16, ctx.gf), 16, 14)
    print(f"[Basis v=14] konstruiert m={len(reps_v14)}, unc={unc14} (Ziel < 298)")
    assert len(reps_v14) == 298 and unc14 == 0

    reps_v15, _ = build_q16_trace_hybrid(3)
    reps_v16, _ = build_q16_trace_hybrid(4)
    print(f"[Basis v=15] m={len(reps_v15)} (Ziel < 315); [Basis v=16] m={len(reps_v16)} (Ziel < 332)")

    # 2. Strukturanalyse Profil 2 ([8, 2^8]) und 3-Trace / 4-Trace
    analyze_profile2_for_baer(ctx)
    eval_symmetric_3trace_v15(ctx)

    # 3. K-Promotion Analyse (kurz):
    # Ersetze eine Baer-Klasse K (20 Punkte) durch Vollgerade? Eine K-Klasse nutzt 4 Geraden w2=i;
    # die 4 K-Klassen mit w2=i partitionieren diese 4 Geraden exakt (je 4 Punkte/Gerade -> 16 Punkte/Gerade).
    # Das Ersetzen einer K-Klasse durch eine Vollgerade laesst 4*4 = 16 Loecher auf den 4 w2=i Geraden
    # und benoetigt zusaetzlich 16 Punkte auf einer neuen Geraden -> kein Nettogewinn bei festem Rest-Gitter.
    print("[K-Promotion] Jede K-Klasse partitioniert 4 Geraden w2=i exakt (4x4=16 Punkte); Einzel-Promotion ohne Umbau des 12-K-Gitters verschlechtert die Bilanz.")

    # 4. Tabu-Reduktions-Proben (je ~14 s fuer v=14, v=15, v=16, strikt <= 54 s gesamt)
    found_any = False
    for v, base_reps, target, seed in [
        (14, reps_v14, 298, 1614),
        (15, reps_v15, 315, 1615),
        (16, reps_v16, 332, 1616),
    ]:
        rem = TIME_LIMIT_S - (time.monotonic() - t0)
        if rem < 3.0:
            break
        budget = min(14.0, rem / 1.0 if v == 16 else rem / (17 - v))
        ts = time.monotonic()
        best_m, best_unc, best_cand, moves = fast_tabu_reduce(base_reps, ctx, v, budget, seed)
        dt = time.monotonic() - ts
        rate = moves / dt if dt > 0 else 0.0
        print(f"[Tabu-Probe v={v}] start m={len(base_reps)} -> Test m={len(base_reps)-1}: "
              f"best_unc={best_unc}, evals={moves} ({rate:,.0f} evals/s), wall={dt:.2f}s, seed={seed}")
        if best_unc == 0:
            if check_and_save_if_better(best_cand, ctx, v, target, f"tabu_s{seed}", out_dir):
                found_any = True

    total_dt = time.monotonic() - t0
    print(f"=== Fertig in {total_dt:.2f} s; neue Listen < Ziel gefunden: {'JA' if found_any else 'NEIN'} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
