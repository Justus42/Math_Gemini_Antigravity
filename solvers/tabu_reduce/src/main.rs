use std::env;
use std::fs::{self, File};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::{Path, PathBuf};
use std::process;
use std::time::{Duration, Instant};

#[derive(Clone)]
struct Rng {
    state: u64,
}

impl Rng {
    fn new(seed: u64) -> Self {
        let mut s = seed.wrapping_add(0x9E37_79B9_7F4A_7C15);
        s = (s ^ (s >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        s = (s ^ (s >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        s ^= s >> 31;
        if s == 0 {
            s = 0x1234_5678_9ABC_DEF0;
        }
        Self { state: s }
    }

    #[inline]
    fn next_u64(&mut self) -> u64 {
        let mut x = self.state;
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        self.state = x;
        x
    }

    #[inline]
    fn next_usize(&mut self, bound: usize) -> usize {
        (self.next_u64() as usize) % bound
    }
}

/// Entry describing a triple touching column `c`:
/// `tid` = triple index, `other1`, `other2` = the other two columns,
/// `w_c`, `w1`, `w2` = place weights in {v*v, v, 1} so tup_idx = val[c]*w_c + val[other1]*w1 + val[other2]*w2.
#[derive(Clone, Copy)]
struct ColTriple {
    tid: u32,
    other1: u16,
    other2: u16,
    w_c: u16,
    w1: u16,
    w2: u16,
}

struct CaState {
    n: usize,
    k: usize,
    v: usize,
    v2: usize,
    v3: usize,
    /// Row-major: rows[r * k + c]
    rows: Vec<u8>,
    /// Column-major mirror: cols[c * n + r]
    cols: Vec<u8>,
    triples: Vec<(u16, u16, u16)>,
    col_triples: Vec<Vec<ColTriple>>,
    /// Exact coverage counts: cov[tid * v3 + tup_idx]
    cov: Vec<u16>,
    /// Uncovered global tuple indices: tid * v3 + tup_idx
    unc_list: Vec<u32>,
    unc_pos: Vec<u32>,
}

impl CaState {
    fn from_rows(row_vecs: &[Vec<u8>], v: usize) -> Self {
        let n = row_vecs.len();
        let k = row_vecs[0].len();
        let v2 = v * v;
        let v3 = v2 * v;

        let mut rows = vec![0u8; n * k];
        let mut cols = vec![0u8; k * n];
        for r in 0..n {
            for c in 0..k {
                let sym = row_vecs[r][c];
                rows[r * k + c] = sym;
                cols[c * n + r] = sym;
            }
        }

        let mut triples = Vec::new();
        let mut col_triples = vec![Vec::new(); k];
        for c1 in 0..k {
            for c2 in (c1 + 1)..k {
                for c3 in (c2 + 1)..k {
                    let tid = triples.len() as u32;
                    triples.push((c1 as u16, c2 as u16, c3 as u16));
                    col_triples[c1].push(ColTriple {
                        tid,
                        other1: c2 as u16,
                        other2: c3 as u16,
                        w_c: v2 as u16,
                        w1: v as u16,
                        w2: 1,
                    });
                    col_triples[c2].push(ColTriple {
                        tid,
                        other1: c1 as u16,
                        other2: c3 as u16,
                        w_c: v as u16,
                        w1: v2 as u16,
                        w2: 1,
                    });
                    col_triples[c3].push(ColTriple {
                        tid,
                        other1: c1 as u16,
                        other2: c2 as u16,
                        w_c: 1,
                        w1: v2 as u16,
                        w2: v as u16,
                    });
                }
            }
        }

        let total_slots = triples.len() * v3;
        let mut st = Self {
            n,
            k,
            v,
            v2,
            v3,
            rows,
            cols,
            triples,
            col_triples,
            cov: vec![0u16; total_slots],
            unc_list: Vec::new(),
            unc_pos: vec![u32::MAX; total_slots],
        };
        st.rebuild_cov();
        st
    }

    fn to_row_vecs(&self) -> Vec<Vec<u8>> {
        let mut out = Vec::with_capacity(self.n);
        for r in 0..self.n {
            out.push(self.rows[r * self.k..(r + 1) * self.k].to_vec());
        }
        out
    }

    fn rebuild_cov(&mut self) {
        self.cov.fill(0);
        self.unc_list.clear();
        self.unc_pos.fill(u32::MAX);
        let k = self.k;
        let v = self.v;
        let v2 = self.v2;
        let v3 = self.v3;

        for r in 0..self.n {
            let row = &self.rows[r * k..(r + 1) * k];
            for (tid, &(c1, c2, c3)) in self.triples.iter().enumerate() {
                let idx = tid * v3
                    + (row[c1 as usize] as usize) * v2
                    + (row[c2 as usize] as usize) * v
                    + (row[c3 as usize] as usize);
                self.cov[idx] += 1;
            }
        }

        for (idx, &c) in self.cov.iter().enumerate() {
            if c == 0 {
                let pos = self.unc_list.len() as u32;
                self.unc_list.push(idx as u32);
                self.unc_pos[idx] = pos;
            }
        }
    }

    /// Independent full recompute of uncovered tuple count from `self.rows` only.
    fn full_recompute_unc(&self) -> (usize, Vec<u16>) {
        let mut fresh = vec![0u16; self.triples.len() * self.v3];
        for r in 0..self.n {
            let row = &self.rows[r * self.k..(r + 1) * self.k];
            for (tid, &(c1, c2, c3)) in self.triples.iter().enumerate() {
                let idx = tid * self.v3
                    + (row[c1 as usize] as usize) * self.v2
                    + (row[c2 as usize] as usize) * self.v
                    + (row[c3 as usize] as usize);
                fresh[idx] += 1;
            }
        }
        let mut unc = 0usize;
        for &c in &fresh {
            if c == 0 {
                unc += 1;
            }
        }
        (unc, fresh)
    }

    #[inline]
    fn unc(&self) -> usize {
        self.unc_list.len()
    }

    #[inline]
    fn add_unc(&mut self, idx: usize) {
        debug_assert_eq!(self.unc_pos[idx], u32::MAX);
        let pos = self.unc_list.len() as u32;
        self.unc_list.push(idx as u32);
        self.unc_pos[idx] = pos;
    }

    #[inline]
    fn rem_unc(&mut self, idx: usize) {
        let pos = self.unc_pos[idx] as usize;
        debug_assert!(pos < self.unc_list.len());
        let last = *self.unc_list.last().unwrap();
        self.unc_list[pos] = last;
        self.unc_pos[last as usize] = pos as u32;
        self.unc_list.pop();
        self.unc_pos[idx] = u32::MAX;
    }

    /// Exact O(C(k-1,2)) delta in uncovered tuples for changing (r, c) -> new_val.
    #[inline]
    fn eval_change(&self, r: usize, c: usize, new_val: u8) -> i32 {
        let row = &self.rows[r * self.k..(r + 1) * self.k];
        let old_val = row[c];
        if old_val == new_val {
            return 0;
        }
        let v3 = self.v3;
        let ov = old_val as usize;
        let nv = new_val as usize;
        let cov = &self.cov;
        let mut delta = 0i32;

        for ct in &self.col_triples[c] {
            let base = (ct.tid as usize) * v3
                + (row[ct.other1 as usize] as usize) * (ct.w1 as usize)
                + (row[ct.other2 as usize] as usize) * (ct.w2 as usize);
            let wc = ct.w_c as usize;
            let old_idx = base + ov * wc;
            let new_idx = base + nv * wc;
            if cov[old_idx] == 1 {
                delta += 1;
            }
            if cov[new_idx] == 0 {
                delta -= 1;
            }
        }
        delta
    }

    /// Apply cell change (r, c) -> new_val incrementally.
    #[inline]
    fn apply_change(&mut self, r: usize, c: usize, new_val: u8) {
        let k = self.k;
        let old_val = self.rows[r * k + c];
        if old_val == new_val {
            return;
        }
        let v3 = self.v3;
        let ov = old_val as usize;
        let nv = new_val as usize;
        let row_off = r * k;

        for idx_ct in 0..self.col_triples[c].len() {
            let ct = self.col_triples[c][idx_ct];
            let s1 = self.rows[row_off + ct.other1 as usize] as usize;
            let s2 = self.rows[row_off + ct.other2 as usize] as usize;
            let base = (ct.tid as usize) * v3 + s1 * (ct.w1 as usize) + s2 * (ct.w2 as usize);
            let wc = ct.w_c as usize;
            let old_idx = base + ov * wc;
            let new_idx = base + nv * wc;

            let c_old = self.cov[old_idx] - 1;
            self.cov[old_idx] = c_old;
            if c_old == 0 {
                self.add_unc(old_idx);
            }

            let c_new = self.cov[new_idx];
            self.cov[new_idx] = c_new + 1;
            if c_new == 0 {
                self.rem_unc(new_idx);
            }
        }

        self.rows[row_off + c] = new_val;
        self.cols[c * self.n + r] = new_val;
    }

    /// Compute unique coverage count (number of triples with cov == 1) for every row.
    fn unique_coverage_per_row(&self) -> Vec<usize> {
        let mut uniq = vec![0usize; self.n];
        for r in 0..self.n {
            let row = &self.rows[r * self.k..(r + 1) * self.k];
            let mut u = 0usize;
            for (tid, &(c1, c2, c3)) in self.triples.iter().enumerate() {
                let idx = tid * self.v3
                    + (row[c1 as usize] as usize) * self.v2
                    + (row[c2 as usize] as usize) * self.v
                    + (row[c3 as usize] as usize);
                if self.cov[idx] == 1 {
                    u += 1;
                }
            }
            uniq[r] = u;
        }
        uniq
    }
}

fn load_ca(path: &Path, v: usize) -> std::io::Result<Vec<Vec<u8>>> {
    let f = File::open(path)?;
    let reader = BufReader::new(f);
    let mut rows: Vec<Vec<u8>> = Vec::new();
    for line in reader.lines() {
        let line = line?;
        let t = line.trim();
        if t.is_empty() {
            continue;
        }
        let row: Vec<u8> = t
            .split_whitespace()
            .map(|tok| {
                let x: usize = tok.parse().expect("Invalid integer in CA");
                assert!(x < v, "Symbol {} >= v={}", x, v);
                x as u8
            })
            .collect();
        if let Some(first) = rows.first() {
            assert_eq!(row.len(), first.len(), "Ragged CA");
        }
        rows.push(row);
    }
    assert!(!rows.is_empty());
    Ok(rows)
}

fn write_ca_atomic(path: &Path, rows: &[Vec<u8>]) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        if !parent.as_os_str().is_empty() {
            fs::create_dir_all(parent)?;
        }
    }
    let tmp = path.with_extension("tmp");
    {
        let file = File::create(&tmp)?;
        let mut out = BufWriter::with_capacity(1 << 20, file);
        for row in rows {
            for (c, &sym) in row.iter().enumerate() {
                if c > 0 {
                    out.write_all(b" ")?;
                }
                write!(out, "{}", sym)?;
            }
            out.write_all(b"\n")?;
        }
        out.flush()?;
    }
    fs::rename(&tmp, path)?;
    Ok(())
}

/// Mandatory 10,000-move incremental vs full-recompute sanity check (0 deviations required).
fn run_sanity_check(in_ca: &Path, v: usize, seed: u64) {
    let rows = load_ca(in_ca, v).expect("Failed to load CA for sanity check");
    let mut st = CaState::from_rows(&rows, v);
    let (init_unc, init_cov) = st.full_recompute_unc();
    assert_eq!(st.unc(), init_unc);
    assert_eq!(st.cov, init_cov);

    let mut rng = Rng::new(seed);
    let t0 = Instant::now();
    for step in 1..=10_000usize {
        let r = rng.next_usize(st.n);
        let c = rng.next_usize(st.k);
        let nv = rng.next_usize(st.v) as u8;
        let before = st.unc() as i32;
        let d = st.eval_change(r, c, nv);
        st.apply_change(r, c, nv);
        let after = st.unc() as i32;
        assert_eq!(
            before + d,
            after,
            "Delta mismatch at step {}: before={} d={} after={}",
            step,
            before,
            d,
            after
        );
        // Full recompute every 500 steps and on final step (plus fast spot checks)
        if step <= 200 || (step % 500) == 0 || step == 10_000 {
            let (full_unc, full_cov) = st.full_recompute_unc();
            assert_eq!(
                st.unc(),
                full_unc,
                "Full unc mismatch at step {}: inc={} full={}",
                step,
                st.unc(),
                full_unc
            );
            assert_eq!(st.cov, full_cov, "Full cov mismatch at step {}", step);
        }
    }
    println!(
        "SANITY_PASS 10000 incremental moves on {} (N={}, k={}, v={}): 0 deviations in {:.3}s",
        in_ca.display(),
        st.n,
        st.k,
        st.v,
        t0.elapsed().as_secs_f64()
    );
}

/// Attempt to repair `st` (after deleting 1 row) back to unc == 0 using conflict-directed Nurmela Tabu.
fn tabu_repair(
    st: &mut CaState,
    rng: &mut Rng,
    deadline: Instant,
    max_steps: u64,
    total_moves: &mut u64,
) -> (bool, usize) {
    let n = st.n;
    let k = st.k;
    let v = st.v;
    let v2 = st.v2;
    let v3 = st.v3;
    let mut tabu_until = vec![0u64; n * k];
    let mut best_unc = st.unc();
    let mut cands: Vec<(usize, usize, u8)> = Vec::with_capacity(256);

    for step in 1..=max_steps {
        if (step & 255) == 0 && Instant::now() >= deadline {
            break;
        }
        let cur_unc = st.unc();
        if cur_unc == 0 {
            return (true, 0);
        }
        *total_moves += 1;

        // Pick a random uncovered tuple (tid, a, b, c)
        let global_idx = st.unc_list[rng.next_usize(cur_unc)] as usize;
        let tid = global_idx / v3;
        let rem = global_idx % v3;
        let a = (rem / v2) as u8;
        let b = ((rem % v2) / v) as u8;
        let c_val = (rem % v) as u8;
        let (c1, c2, c3) = st.triples[tid];
        let (c1, c2, c3) = (c1 as usize, c2 as usize, c3 as usize);

        // Find all rows matching 2 of the 3 values (column-major scan)
        cands.clear();
        let col1 = &st.cols[c1 * n..(c1 + 1) * n];
        let col2 = &st.cols[c2 * n..(c2 + 1) * n];
        let col3 = &st.cols[c3 * n..(c3 + 1) * n];
        for r in 0..n {
            let m1 = col1[r] == a;
            let m2 = col2[r] == b;
            let m3 = col3[r] == c_val;
            if m1 && m2 {
                cands.push((r, c3, c_val));
            } else if m1 && m3 {
                cands.push((r, c2, b));
            } else if m2 && m3 {
                cands.push((r, c1, a));
            }
        }

        // Rare fallback if no row matches 2 of 3 -> pick any row matching 1 of 3
        if cands.is_empty() {
            for r in 0..n {
                if col1[r] == a {
                    cands.push((r, c2, b));
                    if cands.len() >= 32 {
                        break;
                    }
                }
            }
            if cands.is_empty() {
                let r = rng.next_usize(n);
                cands.push((r, c1, a));
            }
        }

        // Small random walk noise (1%) to escape deep cycles
        let chosen = if rng.next_usize(100) == 0 {
            cands[rng.next_usize(cands.len())]
        } else {
            let mut best_mv: Option<(usize, usize, u8)> = None;
            let mut best_d = i32::MAX;
            let mut ties = 0usize;

            for &(r, col, nv) in &cands {
                let d = st.eval_change(r, col, nv);
                let new_unc = (cur_unc as i32 + d) as usize;
                let is_tabu = tabu_until[r * k + col] > step;
                if is_tabu && new_unc >= best_unc && new_unc > 0 {
                    continue;
                }
                if d < best_d {
                    best_d = d;
                    best_mv = Some((r, col, nv));
                    ties = 1;
                } else if d == best_d {
                    ties += 1;
                    if rng.next_usize(ties) == 0 {
                        best_mv = Some((r, col, nv));
                    }
                }
            }

            if let Some(mv) = best_mv {
                mv
            } else {
                // All candidates tabu -> pick best ignoring tabu
                let mut fb_mv = cands[0];
                let mut fb_d = i32::MAX;
                for &(r, col, nv) in &cands {
                    let d = st.eval_change(r, col, nv);
                    if d < fb_d {
                        fb_d = d;
                        fb_mv = (r, col, nv);
                    }
                }
                fb_mv
            }
        };

        let (mr, mc, mval) = chosen;
        st.apply_change(mr, mc, mval);
        let tenure = 6 + rng.next_usize(10) as u64;
        tabu_until[mr * k + mc] = step + tenure;

        let new_unc = st.unc();
        if new_unc < best_unc {
            best_unc = new_unc;
            if new_unc == 0 {
                return (true, 0);
            }
        }
    }

    (st.unc() == 0, best_unc)
}

fn usage() -> ! {
    eprintln!("Usage:");
    eprintln!("  tabu_reduce sanity --v <v> --in-ca <path> [--seed <u64>]");
    eprintln!("  tabu_reduce reduce --v <v> --in-ca <path> --out-ca <path> --time-limit-secs <f64> [--seed <u64>] [--max-saved <N>]");
    process::exit(2);
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        usage();
    }

    match args[1].as_str() {
        "sanity" => {
            let mut v: Option<usize> = None;
            let mut in_ca: Option<PathBuf> = None;
            let mut seed: u64 = 42;
            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--v" => {
                        i += 1;
                        v = Some(args[i].parse().expect("Invalid --v"));
                    }
                    "--in-ca" => {
                        i += 1;
                        in_ca = Some(PathBuf::from(&args[i]));
                    }
                    "--seed" => {
                        i += 1;
                        seed = args[i].parse().expect("Invalid --seed");
                    }
                    other => {
                        eprintln!("Unknown option {}", other);
                        usage();
                    }
                }
                i += 1;
            }
            run_sanity_check(&in_ca.expect("--in-ca required"), v.expect("--v required"), seed);
        }
        "reduce" => {
            let mut v: Option<usize> = None;
            let mut in_ca: Option<PathBuf> = None;
            let mut out_ca: Option<PathBuf> = None;
            let mut time_limit_secs: Option<f64> = None;
            let mut seed: u64 = 13001;
            let mut max_saved: usize = usize::MAX;
            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--v" => {
                        i += 1;
                        v = Some(args[i].parse().expect("Invalid --v"));
                    }
                    "--in-ca" => {
                        i += 1;
                        in_ca = Some(PathBuf::from(&args[i]));
                    }
                    "--out-ca" => {
                        i += 1;
                        out_ca = Some(PathBuf::from(&args[i]));
                    }
                    "--time-limit-secs" => {
                        i += 1;
                        time_limit_secs = Some(args[i].parse().expect("Invalid --time-limit-secs"));
                    }
                    "--seed" => {
                        i += 1;
                        seed = args[i].parse().expect("Invalid --seed");
                    }
                    "--max-saved" => {
                        i += 1;
                        max_saved = args[i].parse().expect("Invalid --max-saved");
                    }
                    other => {
                        eprintln!("Unknown option {}", other);
                        usage();
                    }
                }
                i += 1;
            }

            let v = v.expect("--v required");
            let in_ca = in_ca.expect("--in-ca required");
            let out_ca = out_ca.expect("--out-ca required");
            let time_limit_secs = time_limit_secs.expect("--time-limit-secs required");

            let start = Instant::now();
            let deadline = start + Duration::from_secs_f64(time_limit_secs);
            let mut best_rows = load_ca(&in_ca, v).expect("Failed to load --in-ca");
            let orig_n = best_rows.len();
            let k = best_rows[0].len();
            let init_st = CaState::from_rows(&best_rows, v);
            assert_eq!(init_st.unc(), 0, "Input CA is not valid!");

            let mut rng = Rng::new(seed);
            let mut total_moves = 0u64;
            let mut attempts = 0usize;
            let mut saved = 0usize;
            let mut min_unc_on_next = usize::MAX;

            while Instant::now() < deadline && saved < max_saved {
                let cur_st = CaState::from_rows(&best_rows, v);
                let uniq = cur_st.unique_coverage_per_row();
                let mut order: Vec<usize> = (0..cur_st.n).collect();
                order.sort_by_key(|&r| uniq[r]);
                let min_u = uniq[order[0]];

                // Cycle through lowest unique-coverage rows across attempts at the same N
                let pool = order.len().min(40);
                let pick_idx = if attempts == 0 {
                    0
                } else {
                    attempts % pool
                };
                let del_row = order[pick_idx];
                let del_u = uniq[del_row];

                let mut reduced_rows = Vec::with_capacity(best_rows.len() - 1);
                for (r, row) in best_rows.iter().enumerate() {
                    if r != del_row {
                        reduced_rows.push(row.clone());
                    }
                }

                let mut work_st = CaState::from_rows(&reduced_rows, v);
                // Progressive step budget per attempt: start fast (200k), escalate if stuck
                let step_budget = match attempts {
                    0..=3 => 250_000,
                    4..=10 => 500_000,
                    _ => 1_000_000,
                };
                let (ok, b_unc) = tabu_repair(&mut work_st, &mut rng, deadline, step_budget, &mut total_moves);
                if b_unc < min_unc_on_next {
                    min_unc_on_next = b_unc;
                }

                if ok {
                    let (check_unc, _) = work_st.full_recompute_unc();
                    assert_eq!(check_unc, 0, "Scratch check failed after repair!");
                    best_rows = work_st.to_row_vecs();
                    saved += 1;
                    attempts = 0;
                    min_unc_on_next = usize::MAX;
                    write_ca_atomic(&out_ca, &best_rows).expect("Failed to write --out-ca");
                    println!(
                        "REDUCED N={} (saved={}, del_row={} uniq={} min_u={}, elapsed={:.2}s, total_moves={})",
                        best_rows.len(),
                        saved,
                        del_row,
                        del_u,
                        min_u,
                        start.elapsed().as_secs_f64(),
                        total_moves
                    );
                } else {
                    attempts += 1;
                    if attempts <= 5 || (attempts % 5) == 0 {
                        println!(
                            "ATTEMPT N->{} #{} del_row={} (uniq={}, min_u={}) best_unc={} elapsed={:.2}s moves={}",
                            best_rows.len() - 1,
                            attempts,
                            del_row,
                            del_u,
                            min_u,
                            b_unc,
                            start.elapsed().as_secs_f64(),
                            total_moves
                        );
                    }
                }
            }

            let elapsed = start.elapsed().as_secs_f64();
            let mv_s = if elapsed > 0.0 {
                (total_moves as f64) / elapsed
            } else {
                0.0
            };
            println!(
                "SUMMARY in={} k={} v={} orig_N={} final_N={} saved={} next_best_unc={} elapsed={:.3}s moves={} mv_s={:.0}",
                in_ca.display(),
                k,
                v,
                orig_n,
                best_rows.len(),
                saved,
                if min_unc_on_next == usize::MAX { 0 } else { min_unc_on_next },
                elapsed,
                total_moves,
                mv_s
            );
        }
        _ => usage(),
    }
}
