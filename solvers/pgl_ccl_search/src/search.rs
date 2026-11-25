use std::fs::File;
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

const BASE_W: u16 = 16;
const MAX_W: u16 = 64;

#[derive(Clone, Copy)]
pub struct TripleInfo {
    pub c1: u8,
    pub c2: u8,
    pub c3: u8,
    pub req_mask: u8,
    pub need_const: bool,
}

#[derive(Clone, Copy)]
struct ColTripleEntry {
    triple_idx: u16,
    c1: u8,
    c2: u8,
    c3: u8,
    flip_xor: u8, // 4 if col==c1, 2 if col==c2, 1 if col==c3
}

pub struct Problem {
    pub k: usize,
    pub m: usize,
    pub cover_const: bool,
    pub triples: Vec<TripleInfo>,
    col_triples: Vec<Vec<ColTripleEntry>>,
    pub total_required_clauses: usize,
}

impl Problem {
    pub fn new(k: usize, m: usize, cover_const: bool) -> Self {
        assert!(k >= 3 && k <= 31, "k must be in 3..=31, got {k}");
        assert!(m >= 1 && m <= 200, "m must be in 1..=200, got {m}");
        let left_len = k / 2;
        let num_triples = k * (k - 1) * (k - 2) / 6;
        let mut triples = Vec::with_capacity(num_triples);
        let mut col_triples = vec![Vec::new(); k];
        let mut total_required_clauses = 0usize;

        for c1 in 0..k {
            for c2 in (c1 + 1)..k {
                for c3 in (c2 + 1)..k {
                    let in_l1 = c1 < left_len;
                    let in_l2 = c2 < left_len;
                    let in_l3 = c3 < left_len;

                    // Pattern encoding: (b1 << 2) | (b2 << 1) | b3
                    let (req_mask, need_const) = if in_l1 && in_l2 && in_l3 {
                        // Pure L^3: all 6 non-constant patterns {1,2,3,4,5,6}
                        (0b0111_1110u8, false)
                    } else if !in_l1 && !in_l2 && !in_l3 {
                        // Pure R^3: all 6 non-constant patterns {1,2,3,4,5,6}
                        (0b0111_1110u8, false)
                    } else if in_l1 && in_l2 && !in_l3 {
                        // Mixed (L, L, R): r1 covers aab = {001 (1), 110 (6)}
                        // Need {010 (2), 011 (3), 100 (4), 101 (5)}
                        (0b0011_1100u8, cover_const)
                    } else {
                        // Mixed (L, R, R): r2 covers baa = {100 (4), 011 (3)}
                        // Need {001 (1), 010 (2), 101 (5), 110 (6)}
                        debug_assert!(in_l1 && !in_l2 && !in_l3);
                        (0b0110_0110u8, cover_const)
                    };

                    total_required_clauses += req_mask.count_ones() as usize;
                    if need_const {
                        total_required_clauses += 1;
                    }

                    let t_idx = triples.len() as u16;
                    triples.push(TripleInfo {
                        c1: c1 as u8,
                        c2: c2 as u8,
                        c3: c3 as u8,
                        req_mask,
                        need_const,
                    });

                    col_triples[c1].push(ColTripleEntry {
                        triple_idx: t_idx,
                        c1: c1 as u8,
                        c2: c2 as u8,
                        c3: c3 as u8,
                        flip_xor: 4,
                    });
                    col_triples[c2].push(ColTripleEntry {
                        triple_idx: t_idx,
                        c1: c1 as u8,
                        c2: c2 as u8,
                        c3: c3 as u8,
                        flip_xor: 2,
                    });
                    col_triples[c3].push(ColTripleEntry {
                        triple_idx: t_idx,
                        c1: c1 as u8,
                        c2: c2 as u8,
                        c3: c3 as u8,
                        flip_xor: 1,
                    });
                }
            }
        }

        Self {
            k,
            m,
            cover_const,
            triples,
            col_triples,
            total_required_clauses,
        }
    }
}

/// Independent from-scratch verifier for a binary CCL matrix C (M x k).
/// Returns exact count of uncovered required clauses.
pub fn verify_binary_ccl(prob: &Problem, rows: &[u32]) -> usize {
    assert_eq!(rows.len(), prob.m);
    let mut unc = 0usize;
    for tr in &prob.triples {
        let mut seen = 0u8;
        for &r in rows {
            let b1 = (r >> tr.c1) & 1;
            let b2 = (r >> tr.c2) & 1;
            let b3 = (r >> tr.c3) & 1;
            let pat = (b1 << 2) | (b2 << 1) | b3;
            seen |= 1u8 << pat;
        }
        let missing_nonconst = tr.req_mask & !seen;
        unc += missing_nonconst.count_ones() as usize;
        if tr.need_const && (seen & 0b1000_0001u8) == 0 {
            unc += 1;
        }
    }
    unc
}

/// Fast deterministic SplitMix64 / Xoshiro256** PRNG (zero deps).
struct Rng {
    s: [u64; 4],
}

impl Rng {
    fn new(mut seed: u64) -> Self {
        let mut splitmix = || {
            seed = seed.wrapping_add(0x9E37_79B9_7F4A_7C15);
            let mut z = seed;
            z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
            z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
            z ^ (z >> 31)
        };
        Self {
            s: [splitmix(), splitmix(), splitmix(), splitmix()],
        }
    }

    #[inline]
    fn next_u64(&mut self) -> u64 {
        let res = (self.s[1].wrapping_mul(5)).rotate_left(7).wrapping_mul(9);
        let t = self.s[1] << 17;
        self.s[2] ^= self.s[0];
        self.s[3] ^= self.s[1];
        self.s[1] ^= self.s[2];
        self.s[0] ^= self.s[3];
        self.s[2] ^= t;
        self.s[3] = self.s[3].rotate_left(45);
        res
    }

    #[inline]
    fn next_usize(&mut self, bound: usize) -> usize {
        (self.next_u64() % (bound as u64)) as usize
    }

    #[inline]
    fn next_f64(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 * (1.0 / ((1u64 << 53) as f64))
    }
}

struct WorkerState<'a> {
    prob: &'a Problem,
    rows: Vec<u32>,
    counts: Vec<[u8; 8]>,
    weights: Vec<[u16; 8]>,
    unc_list: Vec<u32>,
    unc_pos: Vec<i32>,
    bumped: Vec<u32>,
    tabu_until: Vec<u64>,
    seen_stamp: Vec<u32>,
    stamp: u32,
    candidates: Vec<(usize, usize)>,
    bumps_since_smooth: u32,
    rng: Rng,
}

impl<'a> WorkerState<'a> {
    fn new(prob: &'a Problem, seed: u64) -> Self {
        let nt = prob.triples.len();
        let mk = prob.m * prob.k;
        Self {
            prob,
            rows: vec![0u32; prob.m],
            counts: vec![[0u8; 8]; nt],
            weights: vec![[0u16; 8]; nt],
            unc_list: Vec::with_capacity(prob.total_required_clauses),
            unc_pos: vec![-1i32; nt * 7],
            bumped: Vec::with_capacity(512),
            tabu_until: vec![0u64; mk],
            seen_stamp: vec![0u32; mk],
            stamp: 1,
            candidates: Vec::with_capacity(mk),
            bumps_since_smooth: 0,
            rng: Rng::new(seed),
        }
    }

    fn reset_weights(&mut self) {
        self.bumped.clear();
        self.bumps_since_smooth = 0;
        for (t, tr) in self.prob.triples.iter().enumerate() {
            let w = &mut self.weights[t];
            *w = [0u16; 8];
            if tr.need_const {
                w[0] = BASE_W;
                w[7] = BASE_W;
            }
            for p in 1..=6 {
                if (tr.req_mask & (1u8 << p)) != 0 {
                    w[p] = BASE_W;
                }
            }
        }
    }

    fn init_random(&mut self) {
        let mask = (1u32 << self.prob.k) - 1;
        for r in 0..self.prob.m {
            self.rows[r] = (self.rng.next_u64() as u32) & mask;
        }
        // Single-bit symmetry breaking only: C[0][0] = 0
        self.rows[0] &= !1u32;
        self.rebuild_state();
    }

    fn init_from_rows(&mut self, init_rows: &[u32]) {
        assert_eq!(init_rows.len(), self.prob.m);
        let mask = (1u32 << self.prob.k) - 1;
        for r in 0..self.prob.m {
            self.rows[r] = init_rows[r] & mask;
        }
        // Preserve exact matrix if C[0][0] == 1 by complementing all rows (lossless symmetry)
        if (self.rows[0] & 1) != 0 {
            for r in 0..self.prob.m {
                self.rows[r] = (!self.rows[r]) & mask;
            }
        }
        self.rebuild_state();
    }

    fn rebuild_state(&mut self) {
        self.reset_weights();
        self.unc_list.clear();
        self.unc_pos.fill(-1);
        self.tabu_until.fill(0);

        for (t, tr) in self.prob.triples.iter().enumerate() {
            let mut cnt = [0u8; 8];
            for &row in &self.rows {
                let b1 = (row >> tr.c1) & 1;
                let b2 = (row >> tr.c2) & 1;
                let b3 = (row >> tr.c3) & 1;
                let pat = ((b1 << 2) | (b2 << 1) | b3) as usize;
                cnt[pat] += 1;
            }
            self.counts[t] = cnt;

            if tr.need_const && (cnt[0] + cnt[7] == 0) {
                self.add_unc(t * 7);
            }
            for p in 1..=6 {
                if (tr.req_mask & (1u8 << p)) != 0 && cnt[p] == 0 {
                    self.add_unc(t * 7 + p);
                }
            }
        }
    }

    #[inline]
    fn add_unc(&mut self, cid: usize) {
        debug_assert_eq!(self.unc_pos[cid], -1);
        let pos = self.unc_list.len() as i32;
        self.unc_list.push(cid as u32);
        self.unc_pos[cid] = pos;
    }

    #[inline]
    fn remove_unc(&mut self, cid: usize) {
        let pos = self.unc_pos[cid];
        debug_assert!(pos >= 0);
        let pos_u = pos as usize;
        let last_cid = self.unc_list.pop().unwrap() as usize;
        if pos_u < self.unc_list.len() {
            self.unc_list[pos_u] = last_cid as u32;
            self.unc_pos[last_cid] = pos;
        }
        self.unc_pos[cid] = -1;
    }

    #[inline]
    fn eval_flip(&self, r: usize, c: usize) -> (i32, i32) {
        let row_bits = self.rows[r];
        let mut w_delta = 0i32;
        let mut unc_delta = 0i32;

        // SAFETY: all indices are pre-validated in Problem::new
        let entries = &self.prob.col_triples[c];
        for e in entries {
            let t = e.triple_idx as usize;
            let b1 = (row_bits >> e.c1) & 1;
            let b2 = (row_bits >> e.c2) & 1;
            let b3 = (row_bits >> e.c3) & 1;
            let old_p = ((b1 << 2) | (b2 << 1) | b3) as usize;
            let new_p = old_p ^ (e.flip_xor as usize);

            let w = &self.weights[t];
            let w_old = w[old_p];
            if w_old > 0 {
                let cnt = &self.counts[t];
                let eff_old = if old_p == 0 || old_p == 7 {
                    cnt[0] + cnt[7]
                } else {
                    cnt[old_p]
                };
                if eff_old == 1 {
                    w_delta += w_old as i32;
                    unc_delta += 1;
                }
            }
            let w_new = w[new_p];
            if w_new > 0 {
                let cnt = &self.counts[t];
                let eff_new = if new_p == 0 || new_p == 7 {
                    cnt[0] + cnt[7]
                } else {
                    cnt[new_p]
                };
                if eff_new == 0 {
                    w_delta -= w_new as i32;
                    unc_delta -= 1;
                }
            }
        }
        (w_delta, unc_delta)
    }

    #[inline]
    fn apply_flip(&mut self, r: usize, c: usize) {
        let old_row = self.rows[r];
        self.rows[r] = old_row ^ (1u32 << c);
        let entries = &self.prob.col_triples[c];

        for e in entries {
            let t = e.triple_idx as usize;
            let b1 = (old_row >> e.c1) & 1;
            let b2 = (old_row >> e.c2) & 1;
            let b3 = (old_row >> e.c3) & 1;
            let old_p = ((b1 << 2) | (b2 << 1) | b3) as usize;
            let new_p = old_p ^ (e.flip_xor as usize);

            let tr = &self.prob.triples[t];
            let cnt = &mut self.counts[t];
            cnt[old_p] -= 1;
            if old_p == 0 || old_p == 7 {
                if tr.need_const && cnt[0] + cnt[7] == 0 {
                    self.add_unc(t * 7);
                }
            } else if (tr.req_mask & (1u8 << old_p)) != 0 && cnt[old_p] == 0 {
                self.add_unc(t * 7 + old_p);
            }

            let cnt = &mut self.counts[t];
            cnt[new_p] += 1;
            if new_p == 0 || new_p == 7 {
                if tr.need_const && cnt[0] + cnt[7] == 1 {
                    self.remove_unc(t * 7);
                }
            } else if (tr.req_mask & (1u8 << new_p)) != 0 && cnt[new_p] == 1 {
                self.remove_unc(t * 7 + new_p);
            }
        }
    }

    #[inline]
    fn add_candidate(&mut self, r: usize, c: usize) {
        // Respect single-bit symmetry breaking C[0][0] = 0
        if r == 0 && c == 0 {
            return;
        }
        let idx = r * self.prob.k + c;
        if self.seen_stamp[idx] != self.stamp {
            self.seen_stamp[idx] = self.stamp;
            self.candidates.push((r, c));
        }
    }

    fn collect_fixing_moves_for_clause(&mut self, cid: u32) {
        let t = (cid / 7) as usize;
        let slot = (cid % 7) as usize;
        let tr = self.prob.triples[t];
        let c1 = tr.c1 as usize;
        let c2 = tr.c2 as usize;
        let c3 = tr.c3 as usize;

        let m = self.prob.m;
        if slot == 0 {
            // Const clause {000, 111}: every non-const pattern is at Hamming distance 1 from either 000 or 111
            for r in 0..m {
                let row = self.rows[r];
                let b1 = (row >> c1) & 1;
                let b2 = (row >> c2) & 1;
                let b3 = (row >> c3) & 1;
                let pat = (b1 << 2) | (b2 << 1) | b3;
                match pat {
                    4 | 3 => self.add_candidate(r, c1),
                    2 | 5 => self.add_candidate(r, c2),
                    1 | 6 => self.add_candidate(r, c3),
                    _ => {}
                }
            }
        } else {
            let slot_u32 = slot as u32;
            for r in 0..m {
                let row = self.rows[r];
                let b1 = (row >> c1) & 1;
                let b2 = (row >> c2) & 1;
                let b3 = (row >> c3) & 1;
                let pat = (b1 << 2) | (b2 << 1) | b3;
                match pat ^ slot_u32 {
                    4 => self.add_candidate(r, c1),
                    2 => self.add_candidate(r, c2),
                    1 => self.add_candidate(r, c3),
                    _ => {}
                }
            }
        }
    }

    fn bump_and_maybe_smooth(&mut self, smooth_period: u32) {
        let mut hit_cap = false;
        for &cid in &self.unc_list {
            let t = (cid / 7) as usize;
            let slot = (cid % 7) as usize;
            let old_w = self.weights[t][slot];
            let new_w = old_w + 1;
            if old_w == BASE_W {
                self.bumped.push(cid);
            }
            self.weights[t][slot] = new_w;
            if slot == 0 {
                self.weights[t][7] = new_w;
            }
            if new_w >= MAX_W {
                hit_cap = true;
            }
        }

        self.bumps_since_smooth += 1;
        if hit_cap {
            // Multiplicative smoothing back towards BASE_W to guarantee bounded weight ratio
            let mut i = 0;
            while i < self.bumped.len() {
                let cid = self.bumped[i];
                let t = (cid / 7) as usize;
                let slot = (cid % 7) as usize;
                let cur = self.weights[t][slot];
                let next = BASE_W + ((cur - BASE_W) * 3) / 4;
                self.weights[t][slot] = next;
                if slot == 0 {
                    self.weights[t][7] = next;
                }
                if next <= BASE_W {
                    self.bumped.swap_remove(i);
                } else {
                    i += 1;
                }
            }
            self.bumps_since_smooth = 0;
        } else if self.bumps_since_smooth >= smooth_period {
            // PAWS-style additive decrement of bumped weights
            let mut i = 0;
            while i < self.bumped.len() {
                let cid = self.bumped[i];
                let t = (cid / 7) as usize;
                let slot = (cid % 7) as usize;
                let next = self.weights[t][slot].saturating_sub(1).max(BASE_W);
                self.weights[t][slot] = next;
                if slot == 0 {
                    self.weights[t][7] = next;
                }
                if next <= BASE_W {
                    self.bumped.swap_remove(i);
                } else {
                    i += 1;
                }
            }
            self.bumps_since_smooth = 0;
        }
    }
}

pub struct SearchConfig {
    pub k: usize,
    pub m: usize,
    pub cover_const: bool,
    pub time_limit_secs: f64,
    pub threads: usize,
    pub seed: u64,
    pub restart_stale_steps: u64,
    pub checkpoint_path: Option<PathBuf>,
    pub resume_rows: Option<Vec<u32>>,
    pub verbose: bool,
}

pub struct SearchResult {
    pub solved: bool,
    pub best_unc: usize,
    pub best_rows: Vec<u32>,
    pub total_moves: u64,
    pub total_restarts: u64,
    pub elapsed_secs: f64,
}

pub fn save_matrix_file(
    path: &Path,
    k: usize,
    m: usize,
    cover_const: bool,
    unc: usize,
    rows: &[u32],
) -> std::io::Result<()> {
    let mut f = File::create(path)?;
    writeln!(
        f,
        "# pgl_ccl k={} m={} cover_const={} unc={}",
        k, m, cover_const, unc
    )?;
    for &row in rows {
        for c in 0..k {
            if c > 0 {
                write!(f, " ")?;
            }
            write!(f, "{}", (row >> c) & 1)?;
        }
        writeln!(f)?;
    }
    f.flush()?;
    Ok(())
}

pub fn load_matrix_file(path: &Path, expected_k: usize) -> std::io::Result<Vec<u32>> {
    let f = File::open(path)?;
    let reader = BufReader::new(f);
    let mut rows = Vec::new();
    for line_res in reader.lines() {
        let line = line_res?;
        let trimmed = line.trim();
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }
        let toks: Vec<&str> = trimmed.split_whitespace().collect();
        if toks.len() != expected_k {
            return Err(std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                format!(
                    "Expected {} columns in matrix file, got {}",
                    expected_k,
                    toks.len()
                ),
            ));
        }
        let mut bits = 0u32;
        for (c, tok) in toks.iter().enumerate() {
            match *tok {
                "0" => {}
                "1" => bits |= 1u32 << c,
                other => {
                    return Err(std::io::Error::new(
                        std::io::ErrorKind::InvalidData,
                        format!("Invalid binary token '{}' at col {}", other, c),
                    ))
                }
            }
        }
        rows.push(bits);
    }
    Ok(rows)
}

/// If warm-start matrix has more rows than target m, greedily drop rows with minimum damage.
pub fn trim_rows_for_m(prob: &Problem, mut rows: Vec<u32>) -> Vec<u32> {
    while rows.len() > prob.m {
        let mut best_drop = 0usize;
        let mut best_unc = usize::MAX;
        for drop_idx in 0..rows.len() {
            let mut cand = Vec::with_capacity(rows.len() - 1);
            for (i, &r) in rows.iter().enumerate() {
                if i != drop_idx {
                    cand.push(r);
                }
            }
            let tmp_prob = Problem::new(prob.k, cand.len(), prob.cover_const);
            let u = verify_binary_ccl(&tmp_prob, &cand);
            if u < best_unc {
                best_unc = u;
                best_drop = drop_idx;
            }
        }
        rows.remove(best_drop);
    }
    rows
}

pub fn run_search(cfg: &SearchConfig) -> SearchResult {
    let start = Instant::now();
    let deadline = start + Duration::from_secs_f64(cfg.time_limit_secs);
    let prob = Arc::new(Problem::new(cfg.k, cfg.m, cfg.cover_const));
    let threads = cfg.threads.max(1);

    let solved_flag = Arc::new(AtomicBool::new(false));
    let global_best_unc = Arc::new(AtomicUsize::new(usize::MAX));
    let global_best_rows = Arc::new(Mutex::new(vec![0u32; cfg.m]));
    let total_moves = Arc::new(AtomicU64::new(0));
    let total_restarts = Arc::new(AtomicU64::new(0));
    let last_ckpt_secs = Arc::new(AtomicU64::new(0));

    let resume_trimmed: Option<Vec<u32>> = cfg.resume_rows.as_ref().map(|r| {
        if r.len() > cfg.m {
            trim_rows_for_m(&prob, r.clone())
        } else {
            r.clone()
        }
    });

    let mut handles = Vec::with_capacity(threads);
    for tid in 0..threads {
        let prob = Arc::clone(&prob);
        let solved_flag = Arc::clone(&solved_flag);
        let global_best_unc = Arc::clone(&global_best_unc);
        let global_best_rows = Arc::clone(&global_best_rows);
        let total_moves = Arc::clone(&total_moves);
        let total_restarts = Arc::clone(&total_restarts);
        let last_ckpt_secs = Arc::clone(&last_ckpt_secs);
        let ckpt_path = cfg.checkpoint_path.clone();
        let init_rows = if tid == 0 {
            resume_trimmed.clone()
        } else {
            None
        };
        let verbose = cfg.verbose;
        let restart_stale_steps = cfg.restart_stale_steps;

        // Diversified search profiles across threads while strictly deterministic per seed
        let t_seed = cfg
            .seed
            .wrapping_add((tid as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15))
            ^ 0xD1B5_4A32_D192_ED03;
        let (base_tenure, tenure_span, p_rw, smooth_period, stale_mult): (u64, u64, f64, u32, u64) =
            match tid % 2 {
                0 => (4, 6, 0.025, 5, 1),
                _ => (7, 8, 0.055, 8, 2),
            };

        handles.push(thread::spawn(move || {
            let mut st = WorkerState::new(&prob, t_seed);
            let mut local_moves: u64 = 0;
            let mut local_restarts: u64 = 0;
            let mut step: u64 = 0;
            let stale_limit = (restart_stale_steps * stale_mult).max(20_000);

            loop {
                if solved_flag.load(Ordering::Relaxed) || Instant::now() >= deadline {
                    break;
                }

                if local_restarts == 0 {
                    if let Some(ref rows) = init_rows {
                        if rows.len() == prob.m {
                            st.init_from_rows(rows);
                        } else {
                            st.init_random();
                        }
                    } else {
                        st.init_random();
                    }
                } else {
                    st.init_random();
                }

                let mut restart_best_unc = st.unc_list.len();
                let mut steps_since_improve: u64 = 0;
                let mut local_min_streak: u32 = 0;

                // Record initial state if better than global best
                if restart_best_unc < global_best_unc.load(Ordering::Relaxed) {
                    let mut guard = global_best_rows.lock().unwrap();
                    if restart_best_unc < global_best_unc.load(Ordering::Relaxed) {
                        global_best_unc.store(restart_best_unc, Ordering::Relaxed);
                        *guard = st.rows.clone();
                        if let Some(ref p) = ckpt_path {
                            let _ = save_matrix_file(
                                p,
                                prob.k,
                                prob.m,
                                prob.cover_const,
                                restart_best_unc,
                                &guard,
                            );
                        }
                    }
                }

                if restart_best_unc == 0 {
                    assert_eq!(verify_binary_ccl(&prob, &st.rows), 0);
                    solved_flag.store(true, Ordering::Release);
                    break;
                }

                while steps_since_improve < stale_limit {
                    if (step & 255) == 0 {
                        if solved_flag.load(Ordering::Relaxed) || Instant::now() >= deadline {
                            break;
                        }
                        // Periodic 60s checkpoint
                        if let Some(ref p) = ckpt_path {
                            let elapsed_u = start.elapsed().as_secs();
                            let prev = last_ckpt_secs.load(Ordering::Relaxed);
                            if elapsed_u >= prev + 60
                                && last_ckpt_secs
                                    .compare_exchange(
                                        prev,
                                        elapsed_u,
                                        Ordering::Relaxed,
                                        Ordering::Relaxed,
                                    )
                                    .is_ok()
                            {
                                let guard = global_best_rows.lock().unwrap();
                                let bu = global_best_unc.load(Ordering::Relaxed);
                                let _ = save_matrix_file(
                                    p,
                                    prob.k,
                                    prob.m,
                                    prob.cover_const,
                                    bu,
                                    &guard,
                                );
                            }
                        }
                    }

                    step += 1;
                    local_moves += 1;
                    let cur_unc = st.unc_list.len();

                    // Bump candidate stamp (handle rare u32 wrap)
                    st.stamp = st.stamp.wrapping_add(1);
                    if st.stamp == 0 {
                        st.seen_stamp.fill(0);
                        st.stamp = 1;
                    }
                    st.candidates.clear();

                    let mut sampled_cid = 0u32;
                    if cur_unc <= 20 {
                        // Endgame: evaluate ALL 1-bit fixing moves across ALL uncovered clauses
                        for i in 0..cur_unc {
                            let cid = st.unc_list[i];
                            st.collect_fixing_moves_for_clause(cid);
                        }
                        sampled_cid = st.unc_list[st.rng.next_usize(cur_unc)];
                    } else {
                        // Focused: sample up to 3 random uncovered clauses
                        let n_samp = if cur_unc > 80 { 1 } else { 3 };
                        for s_i in 0..n_samp {
                            let cid = st.unc_list[st.rng.next_usize(cur_unc)];
                            if s_i == 0 {
                                sampled_cid = cid;
                            }
                            st.collect_fixing_moves_for_clause(cid);
                        }
                    }

                    // Fallback if no Hamming-distance-1 fixing move exists
                    if st.candidates.is_empty() {
                        let t = (sampled_cid / 7) as usize;
                        let tr = st.prob.triples[t];
                        for r in 0..prob.m {
                            st.add_candidate(r, tr.c1 as usize);
                            st.add_candidate(r, tr.c2 as usize);
                            st.add_candidate(r, tr.c3 as usize);
                        }
                    }

                    // Evaluate candidates
                    let mut best_nt: Option<(usize, usize, i32, i32)> = None;
                    let mut best_nt_ties: u32 = 0;
                    let mut best_tabu: Option<(usize, usize, i32, i32)> = None;
                    let mut best_tabu_ties: u32 = 0;
                    let mut asp_move: Option<(usize, usize, i32, i32)> = None;

                    for i in 0..st.candidates.len() {
                        let (r, c) = st.candidates[i];
                        let (wd, ud) = st.eval_flip(r, c);
                        let new_unc = (cur_unc as i32 + ud) as usize;

                        // Immediate solve or strict aspiration over restart_best_unc
                        if new_unc == 0 {
                            asp_move = Some((r, c, wd, ud));
                            break;
                        }
                        if new_unc < restart_best_unc {
                            match asp_move {
                                None => asp_move = Some((r, c, wd, ud)),
                                Some((_, _, awd, aud)) => {
                                    if ud < aud || (ud == aud && wd < awd) {
                                        asp_move = Some((r, c, wd, ud));
                                    }
                                }
                            }
                        }

                        let idx = r * prob.k + c;
                        let is_tabu = step < st.tabu_until[idx];
                        if !is_tabu {
                            match best_nt {
                                None => {
                                    best_nt = Some((r, c, wd, ud));
                                    best_nt_ties = 1;
                                }
                                Some((_, _, bwd, bud)) => {
                                    if wd < bwd || (wd == bwd && ud < bud) {
                                        best_nt = Some((r, c, wd, ud));
                                        best_nt_ties = 1;
                                    } else if wd == bwd && ud == bud {
                                        best_nt_ties += 1;
                                        if st.rng.next_usize(best_nt_ties as usize) == 0 {
                                            best_nt = Some((r, c, wd, ud));
                                        }
                                    }
                                }
                            }
                        } else {
                            match best_tabu {
                                None => {
                                    best_tabu = Some((r, c, wd, ud));
                                    best_tabu_ties = 1;
                                }
                                Some((_, _, bwd, bud)) => {
                                    if wd < bwd || (wd == bwd && ud < bud) {
                                        best_tabu = Some((r, c, wd, ud));
                                        best_tabu_ties = 1;
                                    } else if wd == bwd && ud == bud {
                                        best_tabu_ties += 1;
                                        if st.rng.next_usize(best_tabu_ties as usize) == 0 {
                                            best_tabu = Some((r, c, wd, ud));
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Bridge scan in tight endgame when stuck in a local minimum
                    if asp_move.is_none()
                        && cur_unc <= 8
                        && best_nt.map_or(true, |x| x.2 > 0)
                        && (local_min_streak & 3) == 3
                    {
                        for r in 0..prob.m {
                            for c in 0..prob.k {
                                if r == 0 && c == 0 {
                                    continue;
                                }
                                let idx = r * prob.k + c;
                                if st.seen_stamp[idx] == st.stamp {
                                    continue;
                                }
                                let is_tabu = step < st.tabu_until[idx];
                                if is_tabu {
                                    continue;
                                }
                                let (wd, ud) = st.eval_flip(r, c);
                                match best_nt {
                                    None => {
                                        best_nt = Some((r, c, wd, ud));
                                        best_nt_ties = 1;
                                    }
                                    Some((_, _, bwd, bud)) => {
                                        if wd < bwd || (wd == bwd && ud < bud) {
                                            best_nt = Some((r, c, wd, ud));
                                            best_nt_ties = 1;
                                        } else if wd == bwd && ud == bud {
                                            best_nt_ties += 1;
                                            if st.rng.next_usize(best_nt_ties as usize) == 0 {
                                                best_nt = Some((r, c, wd, ud));
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    let chosen = if let Some(m) = asp_move {
                        local_min_streak = 0;
                        m
                    } else if let Some(m) = best_nt {
                        if m.2 >= 0 {
                            local_min_streak = local_min_streak.saturating_add(1);
                            st.bump_and_maybe_smooth(smooth_period);
                            if st.rng.next_f64() < p_rw && !st.candidates.is_empty() {
                                let (rr, cc) =
                                    st.candidates[st.rng.next_usize(st.candidates.len())];
                                (rr, cc, 0, 0)
                            } else {
                                m
                            }
                        } else {
                            local_min_streak = 0;
                            m
                        }
                    } else if let Some(m) = best_tabu {
                        local_min_streak = local_min_streak.saturating_add(1);
                        st.bump_and_maybe_smooth(smooth_period);
                        m
                    } else {
                        break;
                    };

                    let (r, c, _, _) = chosen;
                    st.apply_flip(r, c);
                    let tenure = base_tenure + (st.rng.next_u64() % tenure_span);
                    st.tabu_until[r * prob.k + c] = step + tenure;

                    let new_unc = st.unc_list.len();
                    if new_unc < restart_best_unc {
                        restart_best_unc = new_unc;
                        steps_since_improve = 0;

                        if new_unc < global_best_unc.load(Ordering::Relaxed) {
                            let mut guard = global_best_rows.lock().unwrap();
                            if new_unc < global_best_unc.load(Ordering::Relaxed) {
                                global_best_unc.store(new_unc, Ordering::Relaxed);
                                *guard = st.rows.clone();
                                if verbose {
                                    eprintln!(
                                        "[t={:.2}s T{} rst={}] new best unc={} (moves={})",
                                        start.elapsed().as_secs_f64(),
                                        tid,
                                        local_restarts,
                                        new_unc,
                                        local_moves
                                    );
                                }
                                if let Some(ref p) = ckpt_path {
                                    let _ = save_matrix_file(
                                        p,
                                        prob.k,
                                        prob.m,
                                        prob.cover_const,
                                        new_unc,
                                        &guard,
                                    );
                                }
                            }
                        }

                        if new_unc == 0 {
                            let check = verify_binary_ccl(&prob, &st.rows);
                            assert_eq!(
                                check, 0,
                                "Incremental counter said unc=0 but independent verifier found {check}!"
                            );
                            solved_flag.store(true, Ordering::Release);
                            break;
                        }
                    } else {
                        steps_since_improve += 1;
                    }
                }

                local_restarts += 1;
            }

            total_moves.fetch_add(local_moves, Ordering::Relaxed);
            total_restarts.fetch_add(local_restarts, Ordering::Relaxed);
        }));
    }

    for h in handles {
        h.join().expect("Worker thread panicked");
    }

    let elapsed_secs = start.elapsed().as_secs_f64();
    let best_rows = global_best_rows.lock().unwrap().clone();
    let best_unc = global_best_unc.load(Ordering::Relaxed);
    let solved = solved_flag.load(Ordering::Acquire);

    if solved {
        assert_eq!(
            verify_binary_ccl(&prob, &best_rows),
            0,
            "Final solution failed independent binary CCL verification"
        );
    }

    SearchResult {
        solved,
        best_unc,
        best_rows,
        total_moves: total_moves.load(Ordering::Relaxed),
        total_restarts: total_restarts.load(Ordering::Relaxed),
        elapsed_secs,
    }
}
