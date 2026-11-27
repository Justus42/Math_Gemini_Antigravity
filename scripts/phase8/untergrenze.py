#!/usr/bin/env python3
"""Phase 8: Untergrenze im Modell M(R) (docs/phase8/NOTIZ_3_UNTERGRENZE_BAER.md), std-only, keine Suche.

Aufruf:
  untergrenze.py schranke Q [Q ...]      L(q) = ceil(q^2 + q*sqrt(q)*(sqrt(q)-1)/(sqrt(q)+1))  (nur v = q)
  untergrenze.py listen DATEI [...]      je Liste R_q<Q>[_v<V>]...txt:
       Lemma J je Symbolklasse  |A_s| >= q + m_s - 1  (m_s = Zahl der Waagerechten, die die Klasse trifft),
       Klassen ohne volle Waagerechte, und fuer v = q der Vergleich |R| >= L(q).
  Exit 1, sobald eine Liste das Lemma oder die Schranke verletzt.
"""
import math
import re
import sys
from fractions import Fraction


def schranke(q):
    """Kleinste ganze Zahl >= q^2 + q*sqrt(q)*(sqrt(q)-1)/(sqrt(q)+1); exakt ueber ganzzahlige Vergleiche."""
    # x = q*sqrt(q)*(sqrt(q)-1)/(sqrt(q)+1) = q*(q - sqrt(q))/(sqrt(q)+1) = q*(sqrt(q)-1)^2*sqrt(q)/(q-1) ... direkt numerisch
    # mit Sicherheitsabstand und exakter Nachpruefung:  L - q^2 >= x  <=>  (L - q^2)*(sqrt(q)+1) >= q*(q - sqrt(q))
    #   <=>  sqrt(q)*(E + q) >= q^2 - E   mit E = L - q^2
    def ok(E):
        lhs, rhs = E + q, q * q - E
        return rhs <= 0 or q * lhs * lhs >= rhs * rhs
    E = max(0, int(q * math.sqrt(q) * (math.sqrt(q) - 1) / (math.sqrt(q) + 1)) - 2)
    while not ok(E):
        E += 1
    return q * q + E


def lese(path):
    m = re.search(r"R_q(\d+)(?:_v(\d+))?", path)
    q = int(m.group(1))
    v = int(m.group(2)) if m.group(2) else q
    reps = []
    for ln in open(path):
        ln = ln.split("#")[0].strip()
        if ln:
            reps.append(tuple(int(z) for z in ln.split()))
    return q, v, reps


def listen(paths):
    bad = 0
    print("| Liste | q | v | `|R|` | Klassen ohne volle Waagerechte (a / b) | kleinster Wert von `|A_s| - (q + m_s - 1)` | L(q) | `|R| - L(q)` |")
    print("| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |")
    for path in paths:
        q, v, reps = lese(path)
        slack, nofull = None, []
        for side in (2, 3):
            cnt = 0
            for s in range(v):
                pts = {(r[0], r[1]) for r in reps if r[side] == s}
                per_line = {}
                for c, d in pts:
                    per_line[d] = per_line.get(d, 0) + 1
                sl = len(pts) - (q + len(per_line) - 1)
                slack = sl if slack is None else min(slack, sl)
                if max(per_line.values(), default=0) < q:
                    cnt += 1
            nofull.append(cnt)
        L = schranke(q) if v == q else None
        if slack < 0 or (L is not None and len(reps) < L):
            bad += 1
        name = path.split("/")[-1]
        print(f"| `{name}` | {q} | {v} | {len(reps)} | {nofull[0]} / {nofull[1]} | {slack} | {L if L else '–'} | {len(reps) - L if L else '–'} |")
    print(f"\nVerletzungen: {bad} von {len(paths)}")
    return bad


if __name__ == "__main__":
    if sys.argv[1] == "schranke":
        for q in map(int, sys.argv[2:]):
            L = schranke(q)
            print(f"q={q}: L(q)={L}  ({L / q / q:.4f} q^2;  q^2 + q*sqrt(q) - 2q = {q * q + q * math.sqrt(q) - 2 * q:.1f})")
    else:
        sys.exit(1 if listen(sys.argv[2:]) else 0)
