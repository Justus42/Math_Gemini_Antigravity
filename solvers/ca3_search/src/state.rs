use crate::rng::Rng;

/// Precomputed descriptor of a column triple containing a specific column `c`.
#[derive(Clone, Copy, Debug)]
pub struct ColTriple {
    /// triple_idx * v^3
    pub base: u32,
    pub c_o1: u16,
    pub c_o2: u16,
    pub stride_self: u32,
    pub stride_o1: u32,
    pub stride_o2: u32,
}

/// Incremental L1-cache-friendly state for t=3 Covering Array CA(N; 3, k, v).
#[derive(Clone)]
pub struct CaState {
    pub n: usize,
    pub k: usize,
    pub v: usize,
    pub v2: usize,
    pub v3: usize,
    pub num_triples: usize,
    /// Number of triples containing any given column: (k-1)*(k-2)/2
    pub tpc: usize,
    /// Row-major matrix of size n * k, values in 0..v
    pub mat: Vec<u8>,
    /// Flat interaction counts of size num_triples * v^3
    pub counts: Vec<u16>,
    /// Dynamic list of currently uncovered flat interaction indices
    pub uncovered_list: Vec<u32>,
    /// Position of each flat interaction index in uncovered_list, or -1 if covered
    pub uncovered_pos: Vec<i32>,
    /// Dynamic weights for clause weighting (size num_triples * v^3)
    pub weights: Vec<u32>,
    /// Column indices [c0, c1, c2] for each triple_idx
    pub triple_cols: Vec<[u16; 3]>,
    /// Flat array of size k * tpc: col_triples[c * tpc .. (c+1) * tpc]
    pub col_triples: Vec<ColTriple>,
}

impl CaState {
    pub fn from_matrix(mat: Vec<u8>, n: usize, k: usize, v: usize) -> Self {
        assert!(k >= 3, "k must be >= 3 for t=3");
        assert!(v >= 2 && v <= 64, "v must be in 2..=64");
        assert!(n < 65000, "n must be < 65000 for u16 counts");
        assert_eq!(mat.len(), n * k, "matrix size mismatch");
        for &val in &mat {
            assert!((val as usize) < v, "symbol {} >= v={}", val, v);
        }

        let v2 = v * v;
        let v3 = v2 * v;
        let num_triples = k * (k - 1) * (k - 2) / 6;
        let tpc = (k - 1) * (k - 2) / 2;

        let mut triple_cols = Vec::with_capacity(num_triples);
        let mut per_col: Vec<Vec<ColTriple>> = vec![Vec::with_capacity(tpc); k];

        let mut t_idx = 0u32;
        for c0 in 0..k {
            for c1 in (c0 + 1)..k {
                for c2 in (c1 + 1)..k {
                    triple_cols.push([c0 as u16, c1 as u16, c2 as u16]);
                    let base = t_idx * (v3 as u32);
                    per_col[c0].push(ColTriple {
                        base,
                        c_o1: c1 as u16,
                        c_o2: c2 as u16,
                        stride_self: v2 as u32,
                        stride_o1: v as u32,
                        stride_o2: 1,
                    });
                    per_col[c1].push(ColTriple {
                        base,
                        c_o1: c0 as u16,
                        c_o2: c2 as u16,
                        stride_self: v as u32,
                        stride_o1: v2 as u32,
                        stride_o2: 1,
                    });
                    per_col[c2].push(ColTriple {
                        base,
                        c_o1: c0 as u16,
                        c_o2: c1 as u16,
                        stride_self: 1,
                        stride_o1: v2 as u32,
                        stride_o2: v as u32,
                    });
                    t_idx += 1;
                }
            }
        }
        debug_assert_eq!(t_idx as usize, num_triples);

        let mut col_triples = Vec::with_capacity(k * tpc);
        for c in 0..k {
            debug_assert_eq!(per_col[c].len(), tpc);
            col_triples.extend_from_slice(&per_col[c]);
        }

        let total_inter = num_triples * v3;
        let counts = vec![0u16; total_inter];
        let uncovered_pos = vec![-1i32; total_inter];
        let weights = vec![1u32; total_inter];

        let mut st = Self {
            n,
            k,
            v,
            v2,
            v3,
            num_triples,
            tpc,
            mat,
            counts,
            uncovered_list: Vec::new(),
            uncovered_pos,
            weights,
            triple_cols,
            col_triples,
        };
        st.recompute_counts();
        st
    }

    pub fn recompute_counts(&mut self) {
        self.counts.fill(0);
        self.uncovered_list.clear();
        self.uncovered_pos.fill(-1);

        let v = self.v;
        let v3 = self.v3;
        for r in 0..self.n {
            let row = &self.mat[r * self.k..(r + 1) * self.k];
            for (t_idx, &[c0, c1, c2]) in self.triple_cols.iter().enumerate() {
                let a = row[c0 as usize] as usize;
                let b = row[c1 as usize] as usize;
                let c = row[c2 as usize] as usize;
                let idx = t_idx * v3 + (a * v + b) * v + c;
                self.counts[idx] += 1;
            }
        }
        for (idx, &cnt) in self.counts.iter().enumerate() {
            if cnt == 0 {
                let pos = self.uncovered_list.len() as i32;
                self.uncovered_list.push(idx as u32);
                self.uncovered_pos[idx] = pos;
            }
        }
    }

    #[inline(always)]
    pub fn uncovered(&self) -> usize {
        self.uncovered_list.len()
    }

    #[inline(always)]
    pub fn reset_weights(&mut self) {
        self.weights.fill(1);
    }

    /// Evaluates changing cell (r, c) to new_val.
    /// Returns (delta_uncovered, delta_weighted).
    #[inline(always)]
    pub fn eval_move(&self, r: usize, c: usize, new_val: u8, use_weights: bool) -> (i32, i64) {
        let row_off = r * self.k;
        let old_val = unsafe { *self.mat.get_unchecked(row_off + c) as u32 };
        let new_val = new_val as u32;
        if old_val == new_val {
            return (0, 0);
        }
        let row = &self.mat[row_off..row_off + self.k];
        let cts = &self.col_triples[c * self.tpc..(c + 1) * self.tpc];
        let counts = &self.counts;
        let weights = &self.weights;

        let mut delta_unc: i32 = 0;

        if use_weights {
            let mut dw32: i32 = 0;
            for ct in cts {
                let a = unsafe { *row.get_unchecked(ct.c_o1 as usize) as u32 };
                let b = unsafe { *row.get_unchecked(ct.c_o2 as usize) as u32 };
                let base_other = ct.base + a * ct.stride_o1 + b * ct.stride_o2;
                let idx_old = (base_other + old_val * ct.stride_self) as usize;
                let idx_new = (base_other + new_val * ct.stride_self) as usize;
                let c_old = unsafe { *counts.get_unchecked(idx_old) };
                let c_new = unsafe { *counts.get_unchecked(idx_new) };
                let lose = (c_old == 1) as i32;
                let gain = (c_new == 0) as i32;
                delta_unc += lose - gain;
                let w_old = unsafe { *weights.get_unchecked(idx_old) as i32 };
                let w_new = unsafe { *weights.get_unchecked(idx_new) as i32 };
                dw32 += lose * w_old - gain * w_new;
            }
            (delta_unc, dw32 as i64)
        } else {
            for ct in cts {
                let a = unsafe { *row.get_unchecked(ct.c_o1 as usize) as u32 };
                let b = unsafe { *row.get_unchecked(ct.c_o2 as usize) as u32 };
                let base_other = ct.base + a * ct.stride_o1 + b * ct.stride_o2;
                let idx_old = (base_other + old_val * ct.stride_self) as usize;
                let idx_new = (base_other + new_val * ct.stride_self) as usize;
                let c_old = unsafe { *counts.get_unchecked(idx_old) };
                let c_new = unsafe { *counts.get_unchecked(idx_new) };
                delta_unc += (c_old == 1) as i32 - (c_new == 0) as i32;
            }
            (delta_unc, delta_unc as i64)
        }
    }

    /// Applies changing cell (r, c) to new_val, updating counts and uncovered_list in O(tpc).
    #[inline]
    pub fn apply_move(&mut self, r: usize, c: usize, new_val: u8) -> u8 {
        let row_off = r * self.k;
        let old_val = self.mat[row_off + c];
        if old_val == new_val {
            return old_val;
        }
        let old_u32 = old_val as u32;
        let new_u32 = new_val as u32;
        let t_start = c * self.tpc;
        let t_end = t_start + self.tpc;

        for ti in t_start..t_end {
            let ct = unsafe { *self.col_triples.get_unchecked(ti) };
            let a = unsafe { *self.mat.get_unchecked(row_off + ct.c_o1 as usize) as u32 };
            let b = unsafe { *self.mat.get_unchecked(row_off + ct.c_o2 as usize) as u32 };
            let base_other = ct.base + a * ct.stride_o1 + b * ct.stride_o2;
            let idx_old = (base_other + old_u32 * ct.stride_self) as usize;
            let idx_new = (base_other + new_u32 * ct.stride_self) as usize;

            let c_old = unsafe { self.counts.get_unchecked_mut(idx_old) };
            debug_assert!(*c_old >= 1);
            *c_old -= 1;
            if *c_old == 0 {
                let pos = self.uncovered_list.len() as i32;
                self.uncovered_list.push(idx_old as u32);
                unsafe {
                    *self.uncovered_pos.get_unchecked_mut(idx_old) = pos;
                }
            }

            let c_new = unsafe { self.counts.get_unchecked_mut(idx_new) };
            let was_zero = *c_new == 0;
            *c_new += 1;
            if was_zero {
                let pos = unsafe { *self.uncovered_pos.get_unchecked(idx_new) } as usize;
                debug_assert!(pos < self.uncovered_list.len());
                let last_idx = self.uncovered_list.pop().unwrap();
                if pos < self.uncovered_list.len() {
                    self.uncovered_list[pos] = last_idx;
                    unsafe {
                        *self.uncovered_pos.get_unchecked_mut(last_idx as usize) = pos as i32;
                    }
                }
                unsafe {
                    *self.uncovered_pos.get_unchecked_mut(idx_new) = -1;
                }
            }
        }
        self.mat[row_off + c] = new_val;
        old_val
    }

    /// Computes for each row the number of interactions exclusively covered (count == 1) by that row.
    pub fn row_exclusivities(&self) -> Vec<usize> {
        let mut excl = vec![0usize; self.n];
        let v = self.v;
        let v3 = self.v3;
        for r in 0..self.n {
            let row = &self.mat[r * self.k..(r + 1) * self.k];
            let mut cnt = 0usize;
            for (t_idx, &[c0, c1, c2]) in self.triple_cols.iter().enumerate() {
                let a = row[c0 as usize] as usize;
                let b = row[c1 as usize] as usize;
                let c = row[c2 as usize] as usize;
                let idx = t_idx * v3 + (a * v + b) * v + c;
                if self.counts[idx] == 1 {
                    cnt += 1;
                }
            }
            excl[r] = cnt;
        }
        excl
    }

    /// Full recompute check against incremental counts & uncovered_list.
    /// Returns Ok(()) if zero discrepancies, else Err with details.
    pub fn verify_incremental(&self) -> Result<(), String> {
        let mut fresh = vec![0u16; self.num_triples * self.v3];
        let v = self.v;
        let v3 = self.v3;
        for r in 0..self.n {
            let row = &self.mat[r * self.k..(r + 1) * self.k];
            for (t_idx, &[c0, c1, c2]) in self.triple_cols.iter().enumerate() {
                let a = row[c0 as usize] as usize;
                let b = row[c1 as usize] as usize;
                let c = row[c2 as usize] as usize;
                let idx = t_idx * v3 + (a * v + b) * v + c;
                fresh[idx] += 1;
            }
        }
        let mut diffs = 0usize;
        let mut fresh_unc = 0usize;
        for idx in 0..fresh.len() {
            if fresh[idx] != self.counts[idx] {
                diffs += 1;
            }
            if fresh[idx] == 0 {
                fresh_unc += 1;
                let pos = self.uncovered_pos[idx];
                if pos < 0
                    || (pos as usize) >= self.uncovered_list.len()
                    || self.uncovered_list[pos as usize] != idx as u32
                {
                    return Err(format!("uncovered_pos inconsistency at idx {}", idx));
                }
            } else if self.uncovered_pos[idx] != -1 {
                return Err(format!(
                    "covered idx {} has uncovered_pos={}",
                    idx, self.uncovered_pos[idx]
                ));
            }
        }
        if diffs > 0 {
            return Err(format!("{} count discrepancies found", diffs));
        }
        if fresh_unc != self.uncovered_list.len() {
            return Err(format!(
                "uncovered_list len {} != fresh {}",
                self.uncovered_list.len(),
                fresh_unc
            ));
        }
        Ok(())
    }

    /// Builds an extended (target_n x (k_base + 1)) matrix from a base (n_base x k_base) CA:
    /// 1. Greedily fills new column k_base on the n_base rows (in random row order).
    /// 2. Greedily constructs (target_n - n_base) repair rows covering maximum uncovered triples.
    pub fn build_extended_greedy(
        base_mat: &[u8],
        n_base: usize,
        k_base: usize,
        target_n: usize,
        v: usize,
        rng: &mut Rng,
    ) -> Self {
        assert!(target_n >= n_base);
        let k = k_base + 1;
        let v2 = v * v;
        let v3 = v2 * v;
        let num_triples = k * (k - 1) * (k - 2) / 6;

        // Build triple lookup for fast greedy initialization
        let mut triple_cols = Vec::with_capacity(num_triples);
        let mut new_col_triples = Vec::new(); // (triple_idx, c0, c1) where c2 == k - 1
        let mut t_idx = 0usize;
        for c0 in 0..k {
            for c1 in (c0 + 1)..k {
                for c2 in (c1 + 1)..k {
                    triple_cols.push([c0, c1, c2]);
                    if c2 == k - 1 {
                        new_col_triples.push((t_idx, c0, c1));
                    }
                    t_idx += 1;
                }
            }
        }

        let mut counts = vec![0u16; num_triples * v3];
        let mut mat = vec![0u8; target_n * k];

        // Copy base rows into first k_base columns and count base triples
        for r in 0..n_base {
            mat[r * k..r * k + k_base].copy_from_slice(&base_mat[r * k_base..(r + 1) * k_base]);
        }
        for (ti, &[c0, c1, c2]) in triple_cols.iter().enumerate() {
            if c2 < k - 1 {
                for r in 0..n_base {
                    let row = &mat[r * k..(r + 1) * k];
                    let idx = ti * v3 + (row[c0] as usize * v + row[c1] as usize) * v + row[c2] as usize;
                    counts[idx] += 1;
                }
            }
        }

        // Step 1: Greedily assign column k-1 for base rows in random order
        let mut row_order: Vec<usize> = (0..n_base).collect();
        for i in (1..row_order.len()).rev() {
            let j = rng.gen_usize(i + 1);
            row_order.swap(i, j);
        }

        for &r in &row_order {
            let row_off = r * k;
            let mut best_gain = 0usize;
            let mut best_val = 0u8;
            let mut ties = 0u64;
            for val in 0..v {
                let mut gain = 0usize;
                for &(ti, c0, c1) in &new_col_triples {
                    let a = mat[row_off + c0] as usize;
                    let b = mat[row_off + c1] as usize;
                    let idx = ti * v3 + (a * v + b) * v + val;
                    if counts[idx] == 0 {
                        gain += 1;
                    }
                }
                if gain > best_gain || ties == 0 {
                    best_gain = gain;
                    best_val = val as u8;
                    ties = 1;
                } else if gain == best_gain {
                    ties += 1;
                    if rng.gen_usize(ties as usize) == 0 {
                        best_val = val as u8;
                    }
                }
            }
            mat[row_off + (k - 1)] = best_val;
            for &(ti, c0, c1) in &new_col_triples {
                let a = mat[row_off + c0] as usize;
                let b = mat[row_off + c1] as usize;
                let idx = ti * v3 + (a * v + b) * v + best_val as usize;
                counts[idx] += 1;
            }
        }

        // Step 2: Greedily build (target_n - n_base) repair rows
        let mut uncov: Vec<usize> = Vec::new();
        for (idx, &c) in counts.iter().enumerate() {
            if c == 0 {
                uncov.push(idx);
            }
        }

        // Precompute triples indexed by each column
        let mut triples_by_col: Vec<Vec<(usize, usize, usize, usize)>> = vec![Vec::new(); k];
        for (ti, &[c0, c1, c2]) in triple_cols.iter().enumerate() {
            triples_by_col[c0].push((ti, c0, c1, c2));
            triples_by_col[c1].push((ti, c0, c1, c2));
            triples_by_col[c2].push((ti, c0, c1, c2));
        }

        for r in n_base..target_n {
            // Refresh uncovered list
            uncov.retain(|&idx| counts[idx] == 0);
            let mut assigned = vec![false; k];
            let mut row_vals = vec![0u8; k];

            if !uncov.is_empty() {
                let pick = uncov[rng.gen_usize(uncov.len())];
                let ti = pick / v3;
                let tup = pick % v3;
                let v0 = (tup / v2) as u8;
                let v1 = ((tup / v) % v) as u8;
                let v2 = (tup % v) as u8;
                let [c0, c1, c2] = triple_cols[ti];
                row_vals[c0] = v0;
                row_vals[c1] = v1;
                row_vals[c2] = v2;
                assigned[c0] = true;
                assigned[c1] = true;
                assigned[c2] = true;
            }

            let mut rem_cols: Vec<usize> = (0..k).filter(|&c| !assigned[c]).collect();
            for i in (1..rem_cols.len()).rev() {
                let j = rng.gen_usize(i + 1);
                rem_cols.swap(i, j);
            }

            for col in rem_cols {
                let mut best_gain = 0usize;
                let mut best_val = 0u8;
                let mut ties = 0u64;
                for val in 0..v {
                    row_vals[col] = val as u8;
                    let mut gain = 0usize;
                    for &(ti, c0, c1, c2) in &triples_by_col[col] {
                        if (c0 == col || assigned[c0])
                            && (c1 == col || assigned[c1])
                            && (c2 == col || assigned[c2])
                        {
                            let idx = ti * v3
                                + (row_vals[c0] as usize * v + row_vals[c1] as usize) * v
                                + row_vals[c2] as usize;
                            if counts[idx] == 0 {
                                gain += 1;
                            }
                        }
                    }
                    if gain > best_gain || ties == 0 {
                        best_gain = gain;
                        best_val = val as u8;
                        ties = 1;
                    } else if gain == best_gain {
                        ties += 1;
                        if rng.gen_usize(ties as usize) == 0 {
                            best_val = val as u8;
                        }
                    }
                }
                row_vals[col] = best_val;
                assigned[col] = true;
            }

            let row_off = r * k;
            mat[row_off..row_off + k].copy_from_slice(&row_vals);
            for (ti, &[c0, c1, c2]) in triple_cols.iter().enumerate() {
                let idx = ti * v3
                    + (row_vals[c0] as usize * v + row_vals[c1] as usize) * v
                    + row_vals[c2] as usize;
                counts[idx] += 1;
            }
        }

        Self::from_matrix(mat, target_n, k, v)
    }
}
