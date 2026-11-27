"""Prueft die Listen in data/phase8/ : Lift mit scripts/phase7_lift.py, beide Verifier, Nachbau des Pruefers,
Zaehler des Pruefers, Negativkontrolle.  Schreibt Markdown-Zeilen.  Aufruf aus dem Repo-Wurzelverzeichnis:
  python3 scripts/phase8/pruefe_listen.py ZAEHLER_BINARY ARBEITSVERZEICHNIS
Abgelegt in results/phase8/ werden nur die Arrays mit keep=True."""
import hashlib, os, shutil, subprocess, sys, time

CASES = [  # q, v, m, t, keep, python-verifier
    (9, 9, 113, 3, True, True), (9, 9, 113, 4, True, True),
    (11, 11, 170, 3, True, True), (11, 11, 170, 4, True, True),
    (13, 13, 238, 3, True, True), (13, 13, 238, 4, True, True),
    (17, 17, 412, 3, False, True),
    (19, 19, 513, 3, True, True),
    (23, 23, 746, 3, False, True), (23, 22, 722, 3, False, True),
    (29, 29, 1190, 3, False, False), (31, 31, 1356, 3, False, False), (37, 37, 1942, 3, False, False),
]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def run(cmd):
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, round(time.time() - t0, 1), r.stdout


def main(zaehler, work):
    os.makedirs(work, exist_ok=True)
    print("| Liste | `t` | Array | SHA-256 (Array) | `M(R)` Lücken | `ca_verify` | `verify_independent` | Nachbau byte-gleich | `zaehler` | Negativkontrolle |")
    print("| --- | :---: | --- | --- | :---: | :---: | :---: | :---: | :---: | :---: |")
    for q, v, m, t, keep, pyv in CASES:
        name = f"R_q{q}_m{m}.txt" if v == q else f"R_q{q}_v{v}_m{m}.txt"
        lst = os.path.join("data", "phase8", name)
        N, k = m * q ** (t - 2), q + 2
        arr = os.path.join(work, f"CA_{N}_{t}_{k}_{v}.txt")
        cmd = ["python3", "scripts/phase7_lift.py", "--q", str(q), "--reps", lst, "--check-m", "--t", str(t), "--out", arr]
        if v != q:
            cmd += ["--v", str(v)]
        rc, _, out = run(cmd)
        mr = [l for l in out.splitlines() if l.startswith("M(R)")]
        gaps = mr[0].split("=")[-1].strip() if mr else "?"
        rc1, s1, _ = run(["./verifiers/ca_verify", arr, str(t), str(v)])
        if pyv:
            rc2, s2, _ = run(["python3", "verifiers/verify_independent.py", arr, str(t), str(v), "-n", str(N), "-k", str(k)])
            py = f"Exit {rc2} ({s2} s)"
        else:
            py = "nicht gelaufen"
        nb = os.path.join(work, "nachbau.txt")
        cmd = ["python3", "scripts/pruefer/nachbau.py", str(q), str(t), lst, nb] + ([str(v)] if v != q else [])
        rc3, _, _ = run(cmd)
        same = "ja" if rc3 == 0 and sha(nb) == sha(arr) else f"NEIN (Exit {rc3})"
        rc4, _, _ = run([zaehler, arr, str(t), str(v), str(N), str(k)])
        neg = os.path.join(work, "neg.txt")
        with open(arr) as f, open(neg, "w") as g:
            g.writelines(f.readlines()[:-1])
        n1, _, _ = run(["./verifiers/ca_verify", neg, str(t), str(v)])
        if pyv:
            n2, _, _ = run(["python3", "verifiers/verify_independent.py", neg, str(t), str(v), "-n", str(N - 1), "-k", str(k)])
            negs = f"Exit {n1} / {n2}"
        else:
            negs = f"Exit {n1} / –"
        if keep:
            shutil.copy(arr, os.path.join("results", "phase8", os.path.basename(arr)))
        print(f"| `{name}` | {t} | `CA({N}; {t}, {k}, {v})`{' (abgelegt)' if keep else ''} | `{sha(arr)}` | {gaps} | Exit {rc1} ({s1} s) | {py} | {same} | Exit {rc4} | {negs} |", flush=True)
        if not keep:
            os.remove(arr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
