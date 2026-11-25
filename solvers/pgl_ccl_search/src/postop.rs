use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;
use std::time::{Duration, Instant};

pub fn load_ca_rows(path: &Path, v: usize) -> std::io::Result<Vec<Vec<u8>>> {
    let f = File::open(path)?;
    let reader = BufReader::new(f);
    let mut rows: Vec<Vec<u8>> = Vec::new();
    for line in reader.lines() {
        let line = line?;
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        let row: Vec<u8> = trimmed
            .split_whitespace()
            .map(|tok| {
                let x: usize = tok.parse().expect("Invalid symbol in CA file");
                assert!(x < v, "Symbol {} >= v={}", x, v);
                x as u8
            })
            .collect();
        if let Some(first) = rows.first() {
            assert_eq!(row.len(), first.len(), "Ragged CA file");
        }
        rows.push(row);
    }
    assert!(!rows.is_empty(), "Empty CA file");
    Ok(rows)
}

fn build_triples(k: usize) -> (Vec<(usize, usize, usize)>, Vec<Vec<usize>>) {
    let mut triples = Vec::new();
    let mut col_triples = vec![Vec::new(); k];
    for c1 in 0..k {
        for c2 in (c1 + 1)..k {
            for c3 in (c2 + 1)..k {
                let tid = triples.len();
                triples.push((c1, c2, c3));
                col_triples[c1].push(tid);
                col_triples[c2].push(tid);
                col_triples[c3].push(tid);
            }
        }
    }
    (triples, col_triples)
}

pub fn count_uncovered_ca(rows: &[Vec<u8>], v: usize) -> usize {
    let k = rows[0].len();
    let (triples, _) = build_triples(k);
    let v2 = v * v;
    let v3 = v2 * v;
    let mut seen = vec![0u32; v3];
    let mut stamp = 0u32;
    let mut unc = 0usize;
    for &(c1, c2, c3) in &triples {
        stamp += 1;
        let mut cov = 0usize;
        for row in rows {
            let idx = (row[c1] as usize) * v2 + (row[c2] as usize) * v + (row[c3] as usize);
            if seen[idx] != stamp {
                seen[idx] = stamp;
                cov += 1;
            }
        }
        unc += v3 - cov;
    }
    unc
}

fn greedy_delete_order(rows: &[Vec<u8>], v: usize, order: &[usize]) -> Vec<Vec<u8>> {
    let k = rows[0].len();
    let (triples, _) = build_triples(k);
    let num_t = triples.len();
    let v2 = v * v;
    let v3 = v2 * v;

    let mut cnt = vec![0u16; num_t * v3];
    for row in rows {
        for (tid, &(c1, c2, c3)) in triples.iter().enumerate() {
            let idx = tid * v3 + (row[c1] as usize) * v2 + (row[c2] as usize) * v + (row[c3] as usize);
            cnt[idx] = cnt[idx].saturating_add(1);
        }
    }

    // Ensure valid CA before deleting
    let mut init_unc = 0usize;
    for &c in &cnt {
        if c == 0 {
            init_unc += 1;
        }
    }
    assert_eq!(init_unc, 0, "Input CA has {} uncovered tuples", init_unc);

    let mut alive = vec![true; rows.len()];
    for &r in order {
        let row = &rows[r];
        let mut can_del = true;
        for (tid, &(c1, c2, c3)) in triples.iter().enumerate() {
            let idx = tid * v3 + (row[c1] as usize) * v2 + (row[c2] as usize) * v + (row[c3] as usize);
            if cnt[idx] <= 1 {
                can_del = false;
                break;
            }
        }
        if can_del {
            alive[r] = false;
            for (tid, &(c1, c2, c3)) in triples.iter().enumerate() {
                let idx = tid * v3 + (row[c1] as usize) * v2 + (row[c2] as usize) * v + (row[c3] as usize);
                cnt[idx] -= 1;
            }
        }
    }

    let mut out = Vec::with_capacity(rows.len());
    for (r, row) in rows.iter().enumerate() {
        if alive[r] {
            out.push(row.clone());
        }
    }
    out
}

/// Deterministic greedy row deletion: tests reverse (N-1..0) and forward (0..N) passes
/// and returns the strictly smaller valid CA (tie-break: reverse).
pub fn greedy_row_delete(rows: &[Vec<u8>], v: usize) -> Vec<Vec<u8>> {
    let n = rows.len();
    let rev_order: Vec<usize> = (0..n).rev().collect();
    let fwd_order: Vec<usize> = (0..n).collect();

    let res_rev = greedy_delete_order(rows, v, &rev_order);
    let res_fwd = greedy_delete_order(rows, v, &fwd_order);

    let best = if res_fwd.len() < res_rev.len() {
        res_fwd
    } else {
        res_rev
    };
    assert_eq!(count_uncovered_ca(&best, v), 0, "Post-deletion CA verification failed");
    best
}

/// Repair uncovered tuples via zero-break single-cell changes followed by greedy single-row completion
/// (up to max_n rows), plus final greedy row deletion.
pub fn repair_and_complete(
    mut rows: Vec<Vec<u8>>,
    v: usize,
    max_n: usize,
    time_limit_secs: f64,
) -> (Vec<Vec<u8>>, usize, usize, usize) {
    let start = Instant::now();
    let deadline = start + Duration::from_secs_f64(time_limit_secs);
    let k = rows[0].len();
    let (triples, col_triples) = build_triples(k);
    let num_t = triples.len();
    let v2 = v * v;
    let v3 = v2 * v;

    let mut cnt = vec![0u16; num_t * v3];
    for row in &rows {
        for (tid, &(c1, c2, c3)) in triples.iter().enumerate() {
            let idx = tid * v3 + (row[c1] as usize) * v2 + (row[c2] as usize) * v + (row[c3] as usize);
            cnt[idx] = cnt[idx].saturating_add(1);
        }
    }

    let mut unc_tuples: Vec<(usize, u8, u8, u8)> = Vec::new();
    for tid in 0..num_t {
        let base = tid * v3;
        for a in 0..v {
            for b in 0..v {
                for c in 0..v {
                    if cnt[base + a * v2 + b * v + c] == 0 {
                        unc_tuples.push((tid, a as u8, b as u8, c as u8));
                    }
                }
            }
        }
    }
    let initial_unc = unc_tuples.len();

    // Stage 1: Zero-break single-cell repair (multi-pass until convergence or time limit)
    let mut repairs = 0usize;
    loop {
        if unc_tuples.is_empty() || Instant::now() >= deadline {
            break;
        }
        let mut progress = false;
        let mut idx_u = 0usize;
        while idx_u < unc_tuples.len() {
            if Instant::now() >= deadline {
                break;
            }
            let (tid, a, b, c) = unc_tuples[idx_u];
            let tup_idx = tid * v3 + (a as usize) * v2 + (b as usize) * v + (c as usize);
            if cnt[tup_idx] > 0 {
                unc_tuples.swap_remove(idx_u);
                continue;
            }
            let (c1, c2, c3) = triples[tid];
            let mut fixed = false;

            // Search rows matching 2 of the 3 columns, try changing the 3rd if 0 breaks
            // Prefer modifying binary-CCL rows (from end backwards) first
            for r in (0..rows.len()).rev() {
                let row = &rows[r];
                let m1 = row[c1] == a;
                let m2 = row[c2] == b;
                let m3 = row[c3] == c;
                let matches = (m1 as u8) + (m2 as u8) + (m3 as u8);
                if matches != 2 {
                    continue;
                }
                let (change_col, new_val) = if !m1 {
                    (c1, a)
                } else if !m2 {
                    (c2, b)
                } else {
                    (c3, c)
                };

                // Check if changing (r, change_col) breaks any covered triple
                let mut breaks = false;
                for &t2 in &col_triples[change_col] {
                    let (x1, x2, x3) = triples[t2];
                    let old_idx = t2 * v3
                        + (row[x1] as usize) * v2
                        + (row[x2] as usize) * v
                        + (row[x3] as usize);
                    if cnt[old_idx] <= 1 {
                        breaks = true;
                        break;
                    }
                }
                if !breaks {
                    // Apply zero-break cell change
                    for &t2 in &col_triples[change_col] {
                        let (x1, x2, x3) = triples[t2];
                        let old_idx = t2 * v3
                            + (rows[r][x1] as usize) * v2
                            + (rows[r][x2] as usize) * v
                            + (rows[r][x3] as usize);
                        cnt[old_idx] -= 1;
                    }
                    rows[r][change_col] = new_val;
                    for &t2 in &col_triples[change_col] {
                        let (x1, x2, x3) = triples[t2];
                        let new_idx = t2 * v3
                            + (rows[r][x1] as usize) * v2
                            + (rows[r][x2] as usize) * v
                            + (rows[r][x3] as usize);
                        cnt[new_idx] = cnt[new_idx].saturating_add(1);
                    }
                    repairs += 1;
                    progress = true;
                    fixed = true;
                    break;
                }
            }

            if fixed {
                unc_tuples.swap_remove(idx_u);
            } else {
                idx_u += 1;
            }
        }
        if !progress {
            break;
        }
    }

    // Re-filter uncovered tuples
    unc_tuples.retain(|&(tid, a, b, c)| cnt[tid * v3 + (a as usize) * v2 + (b as usize) * v + (c as usize)] == 0);

    // Stage 2: Greedy single-row addition while unc > 0 and rows.len() < max_n
    while !unc_tuples.is_empty() && rows.len() < max_n && Instant::now() < deadline {
        // Count uncovered tuples per triple so we always attack bottleneck triples first
        let mut t_unc = vec![0u32; num_t];
        for &(tid, _, _, _) in &unc_tuples {
            t_unc[tid] += 1;
        }
        unc_tuples.sort_unstable_by(|x, y| t_unc[y.0].cmp(&t_unc[x.0]).then_with(|| x.0.cmp(&y.0)));

        let mut new_row = vec![u8::MAX; k];
        for &(tid, a, b, c) in &unc_tuples {
            let (c1, c2, c3) = triples[tid];
            if (new_row[c1] == u8::MAX || new_row[c1] == a)
                && (new_row[c2] == u8::MAX || new_row[c2] == b)
                && (new_row[c3] == u8::MAX || new_row[c3] == c)
            {
                new_row[c1] = a;
                new_row[c2] = b;
                new_row[c3] = c;
            }
        }
        for val in &mut new_row {
            if *val == u8::MAX {
                *val = 0;
            }
        }

        for (tid, &(c1, c2, c3)) in triples.iter().enumerate() {
            let idx = tid * v3
                + (new_row[c1] as usize) * v2
                + (new_row[c2] as usize) * v
                + (new_row[c3] as usize);
            cnt[idx] = cnt[idx].saturating_add(1);
        }
        rows.push(new_row);

        unc_tuples.retain(|&(tid, a, b, c)| cnt[tid * v3 + (a as usize) * v2 + (b as usize) * v + (c as usize)] == 0);
    }

    let final_unc = count_uncovered_ca(&rows, v);
    if final_unc == 0 {
        let reduced = greedy_row_delete(&rows, v);
        (reduced, initial_unc, repairs, 0)
    } else {
        (rows, initial_unc, repairs, final_unc)
    }
}
