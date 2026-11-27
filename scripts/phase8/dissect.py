"""Dissect representative lists: per symbol class of a and b, size, full horizontal lines contained,
and check that class + P_inf blocks (i.e. class meets every line c+al*d=u)."""
import sys, collections
from gfmod import GF
def dissect(q, fn, v=None):
    F = GF(q); v = v or q
    R = [tuple(map(int, l.split())) for l in open(fn) if l.strip() and not l.startswith("#")]
    pts = collections.Counter((c, d) for c, d, a, b in R)
    out = {}
    for name, idx in (("a", 2), ("b", 3)):
        info = []
        for s in range(v):
            cls = {(r[0], r[1]) for r in R if r[idx] == s}
            lines = [d for d in range(q) if all((c, d) in cls for c in range(q))]
            blocks = (q in (8, 9)) or all(any(F.add[c][F.mul[al][d]] == u for c, d in cls) for al in range(q) for u in range(q))
            info.append((len(cls), len(lines), blocks))
        out[name] = info
    mult = collections.Counter(pts.values())
    perline = [sum(pts[(c, d)] for c in range(q)) for d in range(q)]
    return len(R), dict(mult), perline, out
for q, fn, v in [(5,"R_q5_m34.txt",5),(7,"R_q7_m68.txt",7),(8,"R_q8_m91.txt",8),(9,"R_q9_m116.txt",9),(11,"R_q11_m175.txt",11),(5,"R_q5_v4_m27.txt",4),(7,"R_q7_v6_m58.txt",6)]:
    m, mult, perline, out = dissect(q, __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "..", "data", "phase7", fn), v)
    print(f"q={q} v={v} m={m} reps-per-point={mult} reps-per-line(d)={perline}")
    for name in "ab":
        print("   ", name, "classes (size, full lines, blocks):", out[name])
