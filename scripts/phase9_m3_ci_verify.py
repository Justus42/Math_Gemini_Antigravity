#!/usr/bin/env python3
"""Self-contained CI & local runner for Phase 9 M_3(R_3) Dual-Verification.

Performs:
1. Integrity checks: verifiers/SHA256SUMS + data/phase9_m3/SHA256SUMS + seed line count.
2. Two independent lifts via scripts/phase9_m3_lift.py into a private /tmp directory,
   asserting exact line count N, byte-for-byte SHA-256 identity, optional expected SHA-256
   match, and canonical file size <= --max-mib (default 50.0 MiB).
3. Independent dual verification (verifiers/ca_verify + verifiers/verify_independent.py)
   on both the lifted array (POS -> expect rc=0) and a negative control with the last row
   removed (NEG -> expect rc=1).
4. Emits compact JSON + Markdown summaries (no raw CA files) and cleans up /tmp arrays.

Pure Python stdlib only. Does not modify verifiers/ or repository state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cmd(cmd: list[str], cwd: Path | None = None) -> tuple[int, float, str, str]:
    t0 = time.perf_counter()
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    dt = time.perf_counter() - t0
    return p.returncode, dt, p.stdout.strip(), p.stderr.strip()


def last_line(stdout: str, stderr: str) -> str:
    text = "\n".join(x for x in (stdout, stderr) if x).strip()
    return text.splitlines()[-1] if text else ""


def run_pair_parallel(
    cmd_a: list[str], cmd_b: list[str], parallel: bool
) -> tuple[tuple[int, float, str, str], tuple[int, float, str, str]]:
    if not parallel:
        return run_cmd(cmd_a), run_cmd(cmd_b)

    t0_a = time.perf_counter()
    pa = subprocess.Popen(cmd_a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    t0_b = time.perf_counter()
    pb = subprocess.Popen(cmd_b, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Poll/wait both processes to record accurate individual wall-clock durations
    res: dict[str, tuple[int, float, str, str]] = {}
    while len(res) < 2:
        if "a" not in res and pa.poll() is not None:
            out_a, err_a = pa.communicate()
            res["a"] = (pa.returncode, time.perf_counter() - t0_a, out_a.strip(), err_a.strip())
        if "b" not in res and pb.poll() is not None:
            out_b, err_b = pb.communicate()
            res["b"] = (pb.returncode, time.perf_counter() - t0_b, out_b.strip(), err_b.strip())
        if len(res) < 2:
            time.sleep(0.05)
    return res["a"], res["b"]


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 9 M_3(R_3) CI Dual-Verify runner")
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--t", type=int, required=True)
    ap.add_argument("--m", type=int, required=True)
    ap.add_argument("--seed", type=Path, required=True, help="Path to R_3 seed file")
    ap.add_argument("--table-n", type=int, default=None, help="ca-tools@b689967 N for comparison")
    ap.add_argument("--table-k", type=int, default=None, help="ca-tools@b689967 k' for comparison")
    ap.add_argument("--expected-sha256", type=str, default="", help="Optional expected CA SHA-256")
    ap.add_argument("--max-mib", type=float, default=50.0, help="Hard file size cap in MiB")
    ap.add_argument("--threads", type=int, default=min(4, os.cpu_count() or 2))
    ap.add_argument("--ca-verify", type=Path, default=Path("./verifiers/ca_verify"))
    ap.add_argument("--out-dir", type=Path, default=Path("/tmp/phase9_m3_summary"))
    ap.add_argument("--sequential", action="store_true", help="Run py_verify POS/NEG sequentially")
    args = ap.parse_args()

    q, t, m = args.q, args.t, args.m
    k = q + 3
    n_rows = m * (q ** (t - 3))
    seed_path = args.seed
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    git_sha = run_cmd(["git", "rev-parse", "--short", "HEAD"])[2]
    started_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Integrity checks: verifiers/SHA256SUMS & data/phase9_m3/SHA256SUMS
    rc_v, _, out_v, err_v = run_cmd(["sha256sum", "-c", "verifiers/SHA256SUMS"])
    if rc_v != 0:
        print(f"FAIL: verifiers/SHA256SUMS check failed:\n{out_v}\n{err_v}", file=sys.stderr)
        return 2

    rc_d, _, out_d, err_d = run_cmd(["sha256sum", "-c", "SHA256SUMS"], cwd=Path("data/phase9_m3"))
    if rc_d != 0:
        print(f"FAIL: data/phase9_m3/SHA256SUMS check failed:\n{out_d}\n{err_d}", file=sys.stderr)
        return 2

    if not seed_path.is_file():
        print(f"FAIL: seed file not found: {seed_path}", file=sys.stderr)
        return 2
    seed_lines = sum(1 for _ in seed_path.open("rb"))
    if seed_lines != m:
        print(f"FAIL: seed line count {seed_lines} != expected m={m}", file=sys.stderr)
        return 2
    seed_sha = sha256_file(seed_path)

    if not args.ca_verify.is_file():
        print(f"FAIL: ca_verify binary not found: {args.ca_verify}", file=sys.stderr)
        return 2

    workdir = Path(tempfile.mkdtemp(prefix=f"phase9_m3_q{q}_t{t}_"))
    try:
        out1 = workdir / f"CA_{n_rows}_{t}_{k}_{q}_run1.txt"
        out2 = workdir / f"CA_{n_rows}_{t}_{k}_{q}_run2.txt"
        neg_file = workdir / f"CA_{n_rows}_{t}_{k}_{q}_neg.txt"

        # 2. Two independent lifts -> byte equality + SHA-256 + size check
        rc_l1, dt_l1, o_l1, e_l1 = run_cmd([
            sys.executable, "scripts/phase9_m3_lift.py",
            "--q", str(q), "--t", str(t), "--mode", "full-bg3",
            "--reps", str(seed_path), "--check-m3", "--lift", "--out", str(out1),
        ])
        if rc_l1 != 0:
            print(f"FAIL: lift1 rc={rc_l1}\n{o_l1}\n{e_l1}", file=sys.stderr)
            return 2

        rc_l2, dt_l2, o_l2, e_l2 = run_cmd([
            sys.executable, "scripts/phase9_m3_lift.py",
            "--q", str(q), "--t", str(t), "--mode", "full-bg3",
            "--reps", str(seed_path), "--lift", "--out", str(out2),
        ])
        if rc_l2 != 0:
            print(f"FAIL: lift2 rc={rc_l2}\n{o_l2}\n{e_l2}", file=sys.stderr)
            return 2

        sha1 = sha256_file(out1)
        sha2 = sha256_file(out2)
        byte_equal = (sha1 == sha2)
        out2.unlink(missing_ok=True)
        if not byte_equal:
            print(f"FAIL: 2x lift mismatch: {sha1} != {sha2}", file=sys.stderr)
            return 2

        expected_sha = args.expected_sha256.strip().lower()
        expected_sha_ok = (not expected_sha) or (sha1 == expected_sha)
        if not expected_sha_ok:
            print(f"FAIL: SHA-256 mismatch vs expected: got {sha1}, expected {expected_sha}", file=sys.stderr)
            return 2

        size_bytes = out1.stat().st_size
        size_mib = size_bytes / (1024.0 * 1024.0)
        size_ok = size_mib <= args.max_mib

        lines = out1.read_bytes().splitlines(keepends=True)
        if len(lines) != n_rows:
            print(f"FAIL: lifted row count {len(lines)} != expected N={n_rows}", file=sys.stderr)
            return 2

        # Create negative control (delete last row -> N - 1 rows)
        neg_file.write_bytes(b"".join(lines[:-1]))
        neg_sha = sha256_file(neg_file)
        del lines

        # 3. Dual Verification: ca_verify (POS & NEG) + verify_independent.py (POS & NEG)
        rc_cp, dt_cp, o_cp, e_cp = run_cmd([str(args.ca_verify), str(out1), str(t), str(q), str(args.threads)])
        rc_cn, dt_cn, o_cn, e_cn = run_cmd([str(args.ca_verify), str(neg_file), str(t), str(q), str(args.threads)])

        use_parallel = (not args.sequential) and ((os.cpu_count() or 1) >= 2)
        cmd_pp = [
            sys.executable, "verifiers/verify_independent.py",
            str(out1), str(t), str(q), "-n", str(n_rows), "-k", str(k),
        ]
        cmd_pn = [
            sys.executable, "verifiers/verify_independent.py",
            str(neg_file), str(t), str(q), "-n", str(n_rows - 1), "-k", str(k),
        ]
        (rc_pp, dt_pp, o_pp, e_pp), (rc_pn, dt_pn, o_pn, e_pn) = run_pair_parallel(
            cmd_pp, cmd_pn, parallel=use_parallel
        )

        passed = all([
            byte_equal,
            expected_sha_ok,
            size_ok,
            rc_cp == 0,
            rc_cn == 1,
            rc_pp == 0,
            rc_pn == 1,
        ])

        delta = (n_rows - args.table_n) if args.table_n is not None else None
        summary = {
            "timestamp_utc": started_utc,
            "git_commit": git_sha,
            "q": q,
            "t": t,
            "k": k,
            "m": m,
            "N": n_rows,
            "seed_file": str(seed_path),
            "seed_sha256": seed_sha,
            "ca_sha256": sha1,
            "neg_sha256": neg_sha,
            "expected_sha256": expected_sha or None,
            "expected_sha256_ok": expected_sha_ok,
            "lift_byte_equal": byte_equal,
            "lift1_sec": round(dt_l1, 3),
            "lift2_sec": round(dt_l2, 3),
            "size_bytes": size_bytes,
            "size_mib": round(size_mib, 4),
            "max_mib": args.max_mib,
            "size_ok": size_ok,
            "table_b689967_N": args.table_n,
            "table_b689967_k": args.table_k,
            "delta_vs_table": delta,
            "ca_verify_threads": args.threads,
            "ca_verify_pos": {"rc": rc_cp, "sec": round(dt_cp, 3), "msg": last_line(o_cp, e_cp)},
            "ca_verify_neg": {"rc": rc_cn, "sec": round(dt_cn, 3), "msg": last_line(o_cn, e_cn)},
            "py_verify_parallel": use_parallel,
            "py_verify_pos": {"rc": rc_pp, "sec": round(dt_pp, 3), "msg": last_line(o_pp, e_pp)},
            "py_verify_neg": {"rc": rc_pn, "sec": round(dt_pn, 3), "msg": last_line(o_pn, e_pn)},
            "status": "PASS" if passed else "FAIL",
        }

        stem = f"summary_q{q}_t{t}_m{m}"
        json_path = out_dir / f"{stem}.json"
        md_path = out_dir / f"{stem}.md"
        json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

        table_str = (
            f"`{args.table_n}` (`k'={args.table_k}`, `{delta:+d}`)"
            if args.table_n is not None
            else "n/a"
        )
        md_lines = [
            f"### `CA({n_rows}; {t}, {k}, {q})` (`m = {m}`) — **{summary['status']}**",
            "",
            "| Check | Result |",
            "|---|---|",
            f"| Seed | `{seed_path}` (`{seed_sha[:16]}…`) |",
            f"| 2× Lift Byte-Equal | `{'YES' if byte_equal else 'NO'}` (`{dt_l1:.2f}s` / `{dt_l2:.2f}s`) |",
            f"| File Size | `{size_bytes}` B (**`{size_mib:.4f} MiB`** <= `{args.max_mib:.1f} MiB`: `{'OK' if size_ok else 'FAIL'}`) |",
            f"| CA SHA-256 | `{sha1}` |",
            f"| NEG SHA-256 (`N-1`) | `{neg_sha}` |",
            f"| `ca_verify` POS / NEG | `rc={rc_cp}` (`{dt_cp:.3f}s`) / `rc={rc_cn}` (`{dt_cn:.3f}s`) |",
            f"| `verify_independent.py` POS / NEG | `rc={rc_pp}` (`{dt_pp:.3f}s`) / `rc={rc_pn}` (`{dt_pn:.3f}s`) |",
            f"| `ca-tools@b689967` | {table_str} |",
            "",
        ]
        md_text = "\n".join(md_lines)
        md_path.write_text(md_text, encoding="utf-8")

        gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if gh_summary:
            with open(gh_summary, "a", encoding="utf-8") as sf:
                sf.write(md_text + "\n")

        print(md_text)
        print(f"Summary written to: {json_path} and {md_path}")
        return 0 if passed else 1
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
