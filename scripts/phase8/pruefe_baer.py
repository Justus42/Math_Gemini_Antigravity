#!/usr/bin/env python3
"""Phase 8, Baer-Gitter: Listen bauen, M(R) zaehlen, Arrays liften und pruefen. Schreibt eine Markdown-Tabelle.

Aufruf:  pruefe_baer.py ARBEITSVERZEICHNIS ZAEHLER  Q:F:T[:py] ...
  Q:F:T      Liste baer_gitter(Q, F), Lift auf Staerke T; ca_verify und der Zaehler des Pruefers (scripts/pruefer/zaehler.c)
  ...:py     zusaetzlich verifiers/verify_independent.py (Dual-Verifikation nach RULES.md §3)
Negativkontrolle je Array: letzte Zeile entfernt, ca_verify muss Exit 1 liefern.
"""
import hashlib
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import baer_gitter  # noqa: E402


def run(cmd):
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, time.time() - t0


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def main():
    work, zaehler = sys.argv[1], sys.argv[2]
    print("| q | v | F | `|R|` | Lücken eigener Zähler | `phase7_lift --check-m` | t | N | `ca_verify` | `zaehler` | `verify_independent.py` | Negativkontrolle | SHA-256 Liste | SHA-256 Array |")
    print("| ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |")
    for spec in sys.argv[3:]:
        parts = spec.split(":")
        q, f, t = int(parts[0]), int(parts[1]), int(parts[2])
        py = len(parts) > 3
        reps, v = baer_gitter.build(q, f)
        gaps = baer_gitter.check_model(q, v, reps)
        lst = os.path.join(work, f"R_q{q}_v{v}_baer_m{len(reps)}.txt")
        with open(lst, "w") as fh:
            for r in reps:
                fh.write(" ".join(map(str, r)) + "\n")
        n_rows = len(reps) * q ** (t - 2)
        arr = os.path.join(work, f"CA_{n_rows}_{t}_{q + 2}_{v}.txt")
        cmd = ["python3", os.path.join(ROOT, "scripts", "phase7_lift.py"), "--q", str(q), "--reps", lst, "--check-m",
               "--t", str(t), "--out", arr] + ([] if v == q else ["--v", str(v)])
        rc_m, _ = run(cmd)
        rc1, s1 = run([os.path.join(ROOT, "verifiers", "ca_verify"), arr, str(t), str(v)])
        rc2, s2 = run([zaehler, arr, str(t), str(v), str(n_rows), str(q + 2)])
        if py:
            rc3, s3 = run(["python3", os.path.join(ROOT, "verifiers", "verify_independent.py"), arr, str(t), str(v),
                           "-n", str(n_rows), "-k", str(q + 2)])
            col3 = f"Exit {rc3} ({s3:.0f} s)"
        else:
            col3 = "nicht gelaufen"
        neg = arr + ".neg"
        with open(arr) as fh, open(neg, "w") as out:
            lines = fh.readlines()
            out.writelines(lines[:-1])
        rcn, _ = run([os.path.join(ROOT, "verifiers", "ca_verify"), neg, str(t), str(v)])
        os.remove(neg)
        print(f"| {q} | {v} | {f} | {len(reps)} | {gaps[0]}/{gaps[1]}/{gaps[2]} | Exit {rc_m} | {t} | {n_rows} | Exit {rc1} ({s1:.1f} s) | "
              f"Exit {rc2} ({s2:.1f} s) | {col3} | Exit {rcn} | `{sha(lst)[:16]}…` | `{sha(arr)[:16]}…` |", flush=True)


if __name__ == "__main__":
    main()
