use std::fs::{self, File};
use std::io::{BufRead, BufReader, Write};
use std::path::Path;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

const BASE_W: u16 = 16;
const MAX_W: u16 = 64;
const UNREQ_OFFSET: u8 = 100;

/// Map 3-bit pattern (0..8) to slot index (0..7).
/// Patterns 0 (000) and 7 (111) share slot 0 (the const-coverage slot).
const SLOT: [usize; 8] = [0, 1, 2, 3, 4, 5, 6, 0];

/// For a non-const pattern p in 1..=6, returns the single-bit flip mask (4=c1, 2=c2, 1=c3)
/// that turns p into 000 or 111.
const CONST_FIX_MASK: [u8; 8] = [0, 1, 2, 4, 4, 2, 1, 0];

#[derive(Clone, Copy, Debug)]
pub enum SearchAlgo {
    Hybrid,
    TabuCw,
    Paws,
}

#[derive(Clone)]
pub struct Rng {
    state: u64,
}

impl Rng {
    pub fn new(seed: u64) -> Self {
        let mut s = seed.wrapping_add(0x9E37_79B9_7F4A_7C15);
        s = (s ^ (s >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        s = (s ^ (s >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        s ^= s >> 31;
        if s == 0 {
            s = 0xCAFE_BABE_DEAD_BEEF;
        }
        Self { state: s }
    }

    #[inline]
    pub fn next_u64(&mut self) -> u64 {
        let mut x = self.state;
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        self.state = x;
        x
    }

    #[inline]
    pub fn next_usize(&mut self, bound: usize) -> usize {
        (self.next_u64() as usize) % bound
    }
}

pub struct CclProblem {
    pub k: usize,
    pub m: usize,
    pub cover_const: bool,
    pub triples: Vec<(u8, u8, u8)>,
    pub req_mask: Vec<u8>,
    /// For each column c, list of (triple_id, flip_mask in {4, 2, 1})
    pub col_triples: Vec<Vec<(u16, u8)>>,
    pub total_req_slots: usize,
}

impl CclProblem {
    pub fn new(k: usize, m: usize, cover_const: bool) -> Self {
        assert!(k >= 3 && m >= 1 && m <= 60);
        let l_size = k / 2;
        let mut triples = Vec::new();
        let mut req_mask = Vec::new();
        let mut col_triples = vec![Vec::new(); k];
        let mut total_req_slots = 0usize;

        for c1 in 0..k {
            for c2 in (c1 + 1)..k {
                for c3 in (c2 + 1)..k {
                    let tid = triples.len() as u16;
                    triples.push((c1 as u8, c2 as u8, c3 as u8));

                    let in_l = (c1 < l_size) as u8 + (c2 < l_size) as u8 + (c3 < l_size) as u8;
                    let mask: u8 = match in_l {
                        3 | 0 => 0x7E, // pure L^3 or R^3: all 6 non-const patterns (1..6)
                        2 => 0x3C | (cover_const as u8), // L^2 R: {010,011,100,101} (+ const)
                        1 => 0x66 | (cover_const as u8), // L R^2: {001,010,101,110} (+ const)
                        _ => unreachable!(),
                    };
                    req_mask.push(mask);
                    total_req_slots += mask.count_ones() as usize;

                    col_triples[c1].push((tid, 4));
                    col_triples[c2].push((tid, 2));
                    col_triples[c3].push((tid, 1));
                }
            }
        }

        Self {
            k,
            m,
            cover_const,
            triples,
            req_mask,
            col_triples,
            total_req_slots,
        }
    }

    /// Independent from-scratch verifier of a binary M x k matrix against the CCL requirements.
    /// Returns the number of uncovered required slots (0 = valid).
    pub fn verify_from_scratch(&self, mat: &[u8]) -> usize {
        assert_eq!(mat.len(), self.m * self.k);
        let mut unc = 0usize;
        for (tid, &(c1, c2, c3)) in self.triples.iter().enumerate() {
            let mut present = 0u8;
            for r in 0..self.m {
                let row = &mat[r * self.k..(r + 1) * self.k];
                let b1 = row[c1 as usize];
                let b2 = row[c2 as usize];
                let b3 = row[c3 as usize];
                debug_assert!(b1 <= 1 && b2 <= 1 && b3 <= 1);
                let pat = (b1 << 2) | (b2 << 1) | b3;
                let s = SLOT[pat as usize];
                present |= 1u8 << s;
            }
            let missing = self.req_mask[tid] & !present;
            unc += missing.count_ones() as usize;
        }
        unc
    }
}

pub struct CclState<'a> {
    pub prob: &'a CclProblem,
    pub mat: Vec<u8>,
    pub row_pat: Vec<u8>,
    pub cnt: Vec<u8>,
    pub weight: Vec<u16>,
    pub unc_list: Vec<u32>,
    pub unc_pos: Vec<u32>,
    pub max_w: u16,
}

impl<'a> CclState<'a> {
    pub fn new(prob: &'a CclProblem, init_mat: Vec<u8>) -> Self {
        let num_t = prob.triples.len();
        let mut st = Self {
            prob,
            mat: init_mat,
            row_pat: vec![0u8; prob.m * num_t],
            cnt: vec![0u8; num_t * 8],
            weight: vec![BASE_W; num_t * 8],
            unc_list: Vec::with_capacity(prob.total_req_slots),
            unc_pos: vec![u32::MAX; num_t * 8],
            max_w: BASE_W,
        };
        st.rebuild();
        st
    }

    pub fn rebuild(&mut self) {
        let prob = self.prob;
        let num_t = prob.triples.len();
        self.unc_list.clear();
        self.unc_pos.fill(u32::MAX);
        self.weight.fill(BASE_W);
        self.max_w = BASE_W;

        for tid in 0..num_t {
            let base = tid << 3;
            let mask = prob.req_mask[tid];
            for s in 0..7 {
                if ((mask >> s) & 1) == 0 {
                    self.cnt[base + s] = UNREQ_OFFSET;
                } else {
                    self.cnt[base + s] = 0;
                }
            }
            self.cnt[base + 7] = UNREQ_OFFSET;
        }

        for r in 0..prob.m {
            let row = &self.mat[r * prob.k..(r + 1) * prob.k];
            let rp_off = r * num_t;
            for (tid, &(c1, c2, c3)) in prob.triples.iter().enumerate() {
                let pat = (row[c1 as usize] << 2) | (row[c2 as usize] << 1) | row[c3 as usize];
                self.row_pat[rp_off + tid] = pat;
                let s = SLOT[pat as usize];
                self.cnt[(tid << 3) + s] += 1;
            }
        }

        for tid in 0..num_t {
            let base = tid << 3;
            let mask = prob.req_mask[tid];
            for s in 0..7 {
                if ((mask >> s) & 1) != 0 && self.cnt[base + s] == 0 {
                    let slot_id = (base + s) as u32;
                    let pos = self.unc_list.len() as u32;
                    self.unc_list.push(slot_id);
                    self.unc_pos[slot_id as usize] = pos;
                }
            }
        }
    }

    #[inline]
    pub fn unc(&self) -> usize {
        self.unc_list.len()
    }

    #[inline]
    fn add_unc(&mut self, slot_id: usize) {
        debug_assert_eq!(self.unc_pos[slot_id], u32::MAX);
        let pos = self.unc_list.len() as u32;
        self.unc_list.push(slot_id as u32);
        self.unc_pos[slot_id] = pos;
    }

    #[inline]
    fn rem_unc(&mut self, slot_id: usize) {
        let pos = self.unc_pos[slot_id] as usize;
        debug_assert!(pos < self.unc_list.len());
        let last = *self.unc_list.last().unwrap();
        self.unc_list[pos] = last;
        self.unc_pos[last as usize] = pos as u32;
        self.unc_list.pop();
        self.unc_pos[slot_id] = u32::MAX;
    }

    #[inline]
    pub fn eval_flip(&self, r: usize, c: usize) -> (i32, i32) {
        let num_t = self.prob.triples.len();
        let rp = &self.row_pat[r * num_t..(r + 1) * num_t];
        let cnt = &self.cnt;
        let weight = &self.weight;
        let mut dw = 0i32;
        let mut du = 0i32;

        for &(tid_u16, fmask) in &self.prob.col_triples[c] {
            let tid = tid_u16 as usize;
            let old_p = rp[tid];
            let new_p = old_p ^ fmask;
            let base = tid << 3;
            let old_s = base + SLOT[old_p as usize];
            let new_s = base + SLOT[new_p as usize];

            if cnt[old_s] == 1 {
                dw += weight[old_s] as i32;
                du += 1;
            }
            if cnt[new_s] == 0 {
                dw -= weight[new_s] as i32;
                du -= 1;
            }
        }
        (dw, du)
    }

    #[inline]
    pub fn apply_flip(&mut self, r: usize, c: usize) {
        let k = self.prob.k;
        let num_t = self.prob.triples.len();
        self.mat[r * k + c] ^= 1;
        let rp_off = r * num_t;

        for &(tid_u16, fmask) in &self.prob.col_triples[c] {
            let tid = tid_u16 as usize;
            let old_p = self.row_pat[rp_off + tid];
            let new_p = old_p ^ fmask;
            self.row_pat[rp_off + tid] = new_p;

            let base = tid << 3;
            let old_s = base + SLOT[old_p as usize];
            let new_s = base + SLOT[new_p as usize];

            let c_old = self.cnt[old_s] - 1;
            self.cnt[old_s] = c_old;
            if c_old == 0 {
                self.add_unc(old_s);
            }

            let c_new = self.cnt[new_s];
            self.cnt[new_s] = c_new + 1;
            if c_new == 0 {
                self.rem_unc(new_s);
            }
        }
    }

    pub fn bump_weights(&mut self) {
        for &slot_id in &self.unc_list {
            let w = &mut self.weight[slot_id as usize];
            if *w < MAX_W {
                *w += 1;
                if *w > self.max_w {
                    self.max_w = *w;
                }
            }
        }
    }

    pub fn smooth_weights_frac(&mut self) {
        let mut new_max = BASE_W;
        for w in &mut self.weight {
            if *w > BASE_W {
                let excess = *w - BASE_W;
                *w = BASE_W + (excess * 3) / 4;
                if *w > new_max {
                    new_max = *w;
                }
            }
        }
        self.max_w = new_max;
    }

    pub fn smooth_weights_dec(&mut self) {
        let mut new_max = BASE_W;
        for w in &mut self.weight {
            if *w > BASE_W {
                *w -= 1;
                if *w > new_max {
                    new_max = *w;
                }
            }
        }
        self.max_w = new_max;
    }
}

pub fn random_init_mat(prob: &CclProblem, rng: &mut Rng, balanced: bool) -> Vec<u8> {
    let mut mat = vec![0u8; prob.m * prob.k];
    if balanced {
        let ones = prob.m / 2;
        for c in 0..prob.k {
            let mut col = vec![0u8; prob.m];
            for r in 0..ones {
                col[r] = 1;
            }
            // Fisher-Yates shuffle
            for i in (1..prob.m).rev() {
                let j = rng.next_usize(i + 1);
                col.swap(i, j);
            }
            // Ensure C[0][0] == 0
            if c == 0 && col[0] == 1 {
                if let Some(pos) = col.iter().position(|&x| x == 0) {
                    col.swap(0, pos);
                } else {
                    col[0] = 0;
                }
            }
            for r in 0..prob.m {
                mat[r * prob.k + c] = col[r];
            }
        }
    } else {
        for v in &mut mat {
            *v = (rng.next_u64() & 1) as u8;
        }
        mat[0] = 0; // Symmetry breaking: fix ONLY C[0][0] = 0
    }
    mat
}

pub fn save_bin_matrix(
    path: &Path,
    k: usize,
    m: usize,
    cover_const: bool,
    unc: usize,
    mat: &[u8],
) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        if !parent.as_os_str().is_empty() {
            fs::create_dir_all(parent)?;
        }
    }
    let tmp = path.with_extension("tmp");
    {
        let mut f = File::create(&tmp)?;
        writeln!(f, "# pgl_ccl_bin k={} m={} cover_const={} unc={}", k, m, cover_const as u8, unc)?;
        for r in 0..m {
            for c in 0..k {
                if c > 0 {
                    f.write_all(b" ")?;
                }
                write!(f, "{}", mat[r * k + c])?;
            }
            f.write_all(b"\n")?;
        }
        f.flush()?;
    }
    fs::rename(&tmp, path)?;
    Ok(())
}

pub fn load_bin_matrix(path: &Path) -> std::io::Result<(usize, usize, Option<bool>, Vec<u8>)> {
    let f = File::open(path)?;
    let reader = BufReader::new(f);
    let mut header_cc = None;
    let mut rows: Vec<Vec<u8>> = Vec::new();
    for line in reader.lines() {
        let line = line?;
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        if trimmed.starts_with('#') {
            for tok in trimmed.split_whitespace() {
                if let Some(val) = tok.strip_prefix("cover_const=") {
                    header_cc = Some(val == "1" || val == "true");
                }
            }
            continue;
        }
        let row: Vec<u8> = trimmed
            .split_whitespace()
            .map(|s| s.parse::<u8>().expect("Invalid binary entry"))
            .collect();
        rows.push(row);
    }
    assert!(!rows.is_empty(), "Empty binary matrix file");
    let m = rows.len();
    let k = rows[0].len();
    let mut mat = Vec::with_capacity(m * k);
    for row in rows {
        assert_eq!(row.len(), k, "Ragged binary matrix");
        for b in row {
            assert!(b <= 1, "Non-binary entry {}", b);
            mat.push(b);
        }
    }
    Ok((k, m, header_cc, mat))
}

pub struct SearchResult {
    pub best_unc: usize,
    pub best_mat: Vec<u8>,
    pub elapsed_secs: f64,
    pub total_moves: u64,
    pub total_restarts: u64,
}

struct SharedBest {
    best_unc: usize,
    best_mat: Vec<u8>,
    last_ckpt: Instant,
}

#[inline]
fn collect_fixing_flips_for_slot(
    st: &CclState,
    slot_id: u32,
    out: &mut Vec<(usize, usize)>,
) {
    let prob = st.prob;
    let tid = (slot_id >> 3) as usize;
    let s = (slot_id & 7) as u8;
    let (c1, c2, c3) = prob.triples[tid];
    let num_t = prob.triples.len();

    if s == 0 {
        for r in 0..prob.m {
            let p = st.row_pat[r * num_t + tid];
            let fmask = CONST_FIX_MASK[p as usize];
            let col = match fmask {
                4 => c1 as usize,
                2 => c2 as usize,
                1 => c3 as usize,
                _ => continue,
            };
            if r == 0 && col == 0 {
                continue;
            }
            out.push((r, col));
        }
    } else {
        for r in 0..prob.m {
            let p = st.row_pat[r * num_t + tid];
            let diff = p ^ s;
            let col = match diff {
                4 => c1 as usize,
                2 => c2 as usize,
                1 => c3 as usize,
                _ => continue,
            };
            if r == 0 && col == 0 {
                continue;
            }
            out.push((r, col));
        }
    }
}

pub fn run_search(
    prob: Arc<CclProblem>,
    algo: SearchAlgo,
    threads: usize,
    seed: u64,
    time_limit_secs: f64,
    init_resume: Option<Vec<u8>>,
    checkpoint_path: Option<std::path::PathBuf>,
) -> SearchResult {
    let start = Instant::now();
    let deadline = start + Duration::from_secs_f64(time_limit_secs);
    let stop = Arc::new(AtomicBool::new(false));
    let total_moves = Arc::new(AtomicU64::new(0));
    let total_restarts = Arc::new(AtomicU64::new(0));

    let init_best_mat = if let Some(ref m0) = init_resume {
        m0.clone()
    } else {
        let mut r0 = Rng::new(seed);
        random_init_mat(&prob, &mut r0, false)
    };
    let init_best_unc = prob.verify_from_scratch(&init_best_mat);

    let shared = Arc::new(Mutex::new(SharedBest {
        best_unc: init_best_unc,
        best_mat: init_best_mat,
        last_ckpt: start,
    }));

    if init_best_unc == 0 {
        stop.store(true, Ordering::Relaxed);
    }

    let mut handles = Vec::new();
    for tid_idx in 0..threads.max(1) {
        let prob = Arc::clone(&prob);
        let stop = Arc::clone(&stop);
        let total_moves = Arc::clone(&total_moves);
        let total_restarts = Arc::clone(&total_restarts);
        let shared = Arc::clone(&shared);
        let resume_mat = if tid_idx == 0 { init_resume.clone() } else { None };
        let ckpt_path = checkpoint_path.clone();

        let worker_mode = match algo {
            SearchAlgo::Hybrid => {
                if tid_idx % 2 == 0 {
                    SearchAlgo::TabuCw
                } else {
                    SearchAlgo::Paws
                }
            }
            other => other,
        };

        let h = thread::spawn(move || {
            let mut rng = Rng::new(seed.wrapping_add((tid_idx as u64 + 1).wrapping_mul(0x9E37_79B9_7F4A_7C15)));
            let nvars = prob.m * prob.k;
            let mut tabu_until = vec![0u64; nvars];
            let mut seen_stamp = vec![0u32; nvars];
            let mut stamp = 1u32;
            let mut cands: Vec<(usize, usize)> = Vec::with_capacity(nvars);

            let first_mat = resume_mat.unwrap_or_else(|| random_init_mat(&prob, &mut rng, tid_idx % 2 == 1));
            let mut st = CclState::new(&prob, first_mat);
            let mut basin_best = st.unc();
            let mut steps_since_imp = 0u64;
            let mut local_moves = 0u64;
            let mut local_restarts = 0u64;
            let mut bump_cnt = 0u64;
            let mut step = 0u64;

            // Update global best on init
            {
                let mut g = shared.lock().unwrap();
                if basin_best < g.best_unc {
                    g.best_unc = basin_best;
                    g.best_mat = st.mat.clone();
                    if basin_best == 0 {
                        stop.store(true, Ordering::Relaxed);
                    }
                }
            }

            let restart_limit: u64 = match worker_mode {
                SearchAlgo::TabuCw => 60_000,
                SearchAlgo::Paws => 400_000,
                SearchAlgo::Hybrid => unreachable!(),
            };

            while !stop.load(Ordering::Relaxed) {
                if (step & 255) == 0 && Instant::now() >= deadline {
                    stop.store(true, Ordering::Relaxed);
                    break;
                }
                let cur_unc = st.unc();
                if cur_unc == 0 {
                    stop.store(true, Ordering::Relaxed);
                    let mut g = shared.lock().unwrap();
                    g.best_unc = 0;
                    g.best_mat = st.mat.clone();
                    break;
                }

                // Restart check
                if steps_since_imp >= restart_limit {
                    local_restarts += 1;
                    let balanced = (local_restarts & 1) == 1;
                    st.mat = random_init_mat(&prob, &mut rng, balanced);
                    st.rebuild();
                    tabu_until.fill(0);
                    basin_best = st.unc();
                    steps_since_imp = 0;
                    bump_cnt = 0;
                    continue;
                }

                step += 1;
                local_moves += 1;
                steps_since_imp += 1;

                cands.clear();
                let mut best_move: Option<(usize, usize)> = None;
                let mut best_dw = i32::MAX;
                let mut best_du = i32::MAX;
                let mut ties = 0usize;

                match worker_mode {
                    SearchAlgo::TabuCw => {
                        if cur_unc <= 10 {
                            // Full neighborhood scan (excluding C[0][0])
                            for r in 0..prob.m {
                                for c in 0..prob.k {
                                    if r == 0 && c == 0 {
                                        continue;
                                    }
                                    let vid = r * prob.k + c;
                                    let (dw, du) = st.eval_flip(r, c);
                                    let new_unc = (cur_unc as i32 + du) as usize;
                                    let is_tabu = tabu_until[vid] > step;
                                    if is_tabu && new_unc >= basin_best && new_unc > 0 {
                                        continue;
                                    }
                                    if dw < best_dw || (dw == best_dw && du < best_du) {
                                        best_dw = dw;
                                        best_du = du;
                                        best_move = Some((r, c));
                                        ties = 1;
                                    } else if dw == best_dw && du == best_du {
                                        ties += 1;
                                        if rng.next_usize(ties) == 0 {
                                            best_move = Some((r, c));
                                        }
                                    }
                                }
                            }
                        } else {
                            // Union of all fixing flips for currently uncovered slots
                            stamp = stamp.wrapping_add(1);
                            if stamp == 0 {
                                seen_stamp.fill(0);
                                stamp = 1;
                            }
                            let mut tmp = Vec::with_capacity(prob.m);
                            for i in 0..st.unc_list.len() {
                                let slot_id = st.unc_list[i];
                                tmp.clear();
                                collect_fixing_flips_for_slot(&st, slot_id, &mut tmp);
                                for &(r, c) in &tmp {
                                    let vid = r * prob.k + c;
                                    if seen_stamp[vid] != stamp {
                                        seen_stamp[vid] = stamp;
                                        cands.push((r, c));
                                    }
                                }
                            }
                            // Fallback if no direct fixing flips exist
                            if cands.is_empty() {
                                let slot_id = st.unc_list[rng.next_usize(st.unc_list.len())];
                                let (c1, c2, c3) = prob.triples[(slot_id >> 3) as usize];
                                for &col in &[c1 as usize, c2 as usize, c3 as usize] {
                                    for r in 0..prob.m {
                                        if r == 0 && col == 0 {
                                            continue;
                                        }
                                        cands.push((r, col));
                                    }
                                }
                            }

                            for &(r, c) in &cands {
                                let vid = r * prob.k + c;
                                let (dw, du) = st.eval_flip(r, c);
                                let new_unc = (cur_unc as i32 + du) as usize;
                                let is_tabu = tabu_until[vid] > step;
                                if is_tabu && new_unc >= basin_best && new_unc > 0 {
                                    continue;
                                }
                                if dw < best_dw || (dw == best_dw && du < best_du) {
                                    best_dw = dw;
                                    best_du = du;
                                    best_move = Some((r, c));
                                    ties = 1;
                                } else if dw == best_dw && du == best_du {
                                    ties += 1;
                                    if rng.next_usize(ties) == 0 {
                                        best_move = Some((r, c));
                                    }
                                }
                            }
                        }

                        // Fallback if all candidates were tabu
                        if best_move.is_none() {
                            let r = rng.next_usize(prob.m);
                            let c = rng.next_usize(prob.k);
                            let (r, c) = if r == 0 && c == 0 { (0, 1) } else { (r, c) };
                            let (dw, _) = st.eval_flip(r, c);
                            best_dw = dw;
                            best_move = Some((r, c));
                        }

                        if best_dw >= 0 {
                            st.bump_weights();
                            bump_cnt += 1;
                            if st.max_w >= 48 || (bump_cnt & 31) == 0 {
                                st.smooth_weights_frac();
                            }
                        }

                        let (mr, mc) = best_move.unwrap();
                        st.apply_flip(mr, mc);
                        let tenure = 4 + rng.next_usize(7) as u64;
                        tabu_until[mr * prob.k + mc] = step + tenure;
                    }
                    SearchAlgo::Paws => {
                        // Pick 1 random uncovered slot and evaluate its fixing flips
                        let slot_id = st.unc_list[rng.next_usize(st.unc_list.len())];
                        collect_fixing_flips_for_slot(&st, slot_id, &mut cands);
                        if cands.is_empty() {
                            let (c1, c2, c3) = prob.triples[(slot_id >> 3) as usize];
                            for &col in &[c1 as usize, c2 as usize, c3 as usize] {
                                for r in 0..prob.m {
                                    if r == 0 && col == 0 {
                                        continue;
                                    }
                                    cands.push((r, col));
                                }
                            }
                        }

                        // Small WalkSAT noise (2%)
                        if !cands.is_empty() && rng.next_usize(50) == 0 {
                            let (mr, mc) = cands[rng.next_usize(cands.len())];
                            st.apply_flip(mr, mc);
                            let tenure = 2 + rng.next_usize(5) as u64;
                            tabu_until[mr * prob.k + mc] = step + tenure;
                        } else {
                            for &(r, c) in &cands {
                                let vid = r * prob.k + c;
                                let (dw, du) = st.eval_flip(r, c);
                                let new_unc = (cur_unc as i32 + du) as usize;
                                let is_tabu = tabu_until[vid] > step;
                                if is_tabu && new_unc >= basin_best && new_unc > 0 {
                                    continue;
                                }
                                if dw < best_dw || (dw == best_dw && du < best_du) {
                                    best_dw = dw;
                                    best_du = du;
                                    best_move = Some((r, c));
                                    ties = 1;
                                } else if dw == best_dw && du == best_du {
                                    ties += 1;
                                    if rng.next_usize(ties) == 0 {
                                        best_move = Some((r, c));
                                    }
                                }
                            }

                            if best_move.is_none() {
                                // All fixing flips tabu -> pick best ignoring tabu
                                for &(r, c) in &cands {
                                    let (dw, du) = st.eval_flip(r, c);
                                    if dw < best_dw || (dw == best_dw && du < best_du) {
                                        best_dw = dw;
                                        best_du = du;
                                        best_move = Some((r, c));
                                        ties = 1;
                                    } else if dw == best_dw && du == best_du {
                                        ties += 1;
                                        if rng.next_usize(ties) == 0 {
                                            best_move = Some((r, c));
                                        }
                                    }
                                }
                            }

                            if best_dw >= 0 {
                                // PAWS weight update: occasionally smooth, otherwise bump
                                bump_cnt += 1;
                                if (bump_cnt % 12) == 0 || st.max_w >= 48 {
                                    st.smooth_weights_dec();
                                } else {
                                    st.bump_weights();
                                }
                            }

                            let (mr, mc) = best_move.unwrap();
                            st.apply_flip(mr, mc);
                            let tenure = 2 + rng.next_usize(5) as u64;
                            tabu_until[mr * prob.k + mc] = step + tenure;
                        }
                    }
                    SearchAlgo::Hybrid => unreachable!(),
                }

                let new_unc = st.unc();
                if new_unc < basin_best {
                    basin_best = new_unc;
                    steps_since_imp = 0;

                    let mut g = shared.lock().unwrap();
                    if new_unc < g.best_unc {
                        g.best_unc = new_unc;
                        g.best_mat = st.mat.clone();
                        if let Some(ref cp) = ckpt_path {
                            if new_unc == 0 || g.last_ckpt.elapsed() >= Duration::from_secs(30) {
                                let _ = save_bin_matrix(cp, prob.k, prob.m, prob.cover_const, new_unc, &g.best_mat);
                                g.last_ckpt = Instant::now();
                            }
                        }
                        if new_unc == 0 {
                            stop.store(true, Ordering::Relaxed);
                            break;
                        }
                    }
                }
            }

            total_moves.fetch_add(local_moves, Ordering::Relaxed);
            total_restarts.fetch_add(local_restarts, Ordering::Relaxed);
        });
        handles.push(h);
    }

    for h in handles {
        h.join().unwrap();
    }

    let elapsed_secs = start.elapsed().as_secs_f64();
    let g = shared.lock().unwrap();
    // Final independent verification of best_mat
    let verified_unc = prob.verify_from_scratch(&g.best_mat);
    assert_eq!(
        verified_unc, g.best_unc,
        "Incremental unc mismatch: state={} vs scratch={}",
        g.best_unc, verified_unc
    );

    if let Some(ref cp) = checkpoint_path {
        let _ = save_bin_matrix(cp, prob.k, prob.m, prob.cover_const, g.best_unc, &g.best_mat);
    }

    SearchResult {
        best_unc: g.best_unc,
        best_mat: g.best_mat.clone(),
        elapsed_secs,
        total_moves: total_moves.load(Ordering::Relaxed),
        total_restarts: total_restarts.load(Ordering::Relaxed),
    }
}

/// Self-test incremental eval_flip / apply_flip against from-scratch verification.
pub fn self_test_ccl() {
    for &cover_const in &[false, true] {
        let prob = CclProblem::new(10, 8, cover_const);
        let mut rng = Rng::new(12345 + cover_const as u64);
        let init = random_init_mat(&prob, &mut rng, false);
        let mut st = CclState::new(&prob, init);
        assert_eq!(st.unc(), prob.verify_from_scratch(&st.mat));

        for _ in 0..200 {
            let r = rng.next_usize(prob.m);
            let c = rng.next_usize(prob.k);
            let before_unc = st.unc() as i32;
            let (_, du) = st.eval_flip(r, c);
            st.apply_flip(r, c);
            let after_unc = st.unc() as i32;
            assert_eq!(before_unc + du, after_unc, "Delta unc mismatch");
            assert_eq!(after_unc as usize, prob.verify_from_scratch(&st.mat), "Scratch unc mismatch");
        }
    }
}
