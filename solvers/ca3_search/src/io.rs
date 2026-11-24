use std::fs::{self, File};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::Path;
use std::time::{SystemTime, UNIX_EPOCH};

pub struct LoadedMatrix {
    pub n: usize,
    pub k: usize,
    #[allow(dead_code)]
    pub v_max: usize,
    pub mat: Vec<u8>,
}

/// Reads a canonical covering array text file (space-separated integers 0..v-1).
pub fn read_matrix<P: AsRef<Path>>(path: P) -> Result<LoadedMatrix, String> {
    let file = File::open(path.as_ref())
        .map_err(|e| format!("failed to open {}: {}", path.as_ref().display(), e))?;
    let reader = BufReader::new(file);
    let mut mat = Vec::new();
    let mut n = 0usize;
    let mut k: Option<usize> = None;
    let mut v_max = 0usize;

    for (line_idx, line_res) in reader.lines().enumerate() {
        let line = line_res.map_err(|e| format!("I/O error at line {}: {}", line_idx + 1, e))?;
        let trimmed = line.trim();
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }
        let mut row_len = 0usize;
        for tok in trimmed.split_whitespace() {
            let val: usize = tok.parse().map_err(|e| {
                format!(
                    "parse error at line {} token '{}': {}",
                    line_idx + 1,
                    tok,
                    e
                )
            })?;
            if val >= 255 {
                return Err(format!("symbol {} out of u8 range at line {}", val, line_idx + 1));
            }
            if val + 1 > v_max {
                v_max = val + 1;
            }
            mat.push(val as u8);
            row_len += 1;
        }
        match k {
            None => k = Some(row_len),
            Some(expected_k) if expected_k != row_len => {
                return Err(format!(
                    "ragged matrix at line {}: expected {} cols, got {}",
                    line_idx + 1,
                    expected_k,
                    row_len
                ));
            }
            _ => {}
        }
        n += 1;
    }

    let k = k.ok_or_else(|| "empty matrix file".to_string())?;
    Ok(LoadedMatrix { n, k, v_max, mat })
}

/// Writes matrix in canonical format (N lines, k space-separated ints, LF endings) atomically.
pub fn write_matrix_atomic<P: AsRef<Path>>(
    path: P,
    mat: &[u8],
    n: usize,
    k: usize,
) -> Result<(), String> {
    let path = path.as_ref();
    if let Some(parent) = path.parent() {
        if !parent.as_os_str().is_empty() {
            fs::create_dir_all(parent)
                .map_err(|e| format!("failed to create dir {}: {}", parent.display(), e))?;
        }
    }
    let tmp_path = path.with_extension("txt.tmp");
    {
        let file = File::create(&tmp_path)
            .map_err(|e| format!("failed to create {}: {}", tmp_path.display(), e))?;
        let mut w = BufWriter::new(file);
        for r in 0..n {
            let row = &mat[r * k..(r + 1) * k];
            for (c, &val) in row.iter().enumerate() {
                if c > 0 {
                    w.write_all(b" ").map_err(|e| e.to_string())?;
                }
                write!(w, "{}", val).map_err(|e| e.to_string())?;
            }
            w.write_all(b"\n").map_err(|e| e.to_string())?;
        }
        w.flush().map_err(|e| e.to_string())?;
    }
    fs::rename(&tmp_path, path).map_err(|e| {
        format!(
            "failed to rename {} -> {}: {}",
            tmp_path.display(),
            path.display(),
            e
        )
    })?;
    Ok(())
}

pub struct CheckpointMeta<'a> {
    pub mode: &'a str,
    pub n: usize,
    pub k: usize,
    pub v: usize,
    pub uncovered: usize,
    pub total_moves: u64,
    pub moves_per_sec: f64,
    pub elapsed_secs: f64,
    pub base_seed: u64,
    pub best_thread: usize,
    pub best_seed: u64,
    pub extra: &'a str,
}

pub fn write_meta_atomic<P: AsRef<Path>>(path: P, meta: &CheckpointMeta<'_>) -> Result<(), String> {
    let path = path.as_ref();
    if let Some(parent) = path.parent() {
        if !parent.as_os_str().is_empty() {
            fs::create_dir_all(parent)
                .map_err(|e| format!("failed to create dir {}: {}", parent.display(), e))?;
        }
    }
    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);
    let escaped_extra = meta.extra.replace('\\', "\\\\").replace('"', "\\\"");
    let json = format!(
        "{{\n  \"mode\": \"{}\",\n  \"n\": {},\n  \"k\": {},\n  \"v\": {},\n  \"uncovered\": {},\n  \"total_moves\": {},\n  \"moves_per_sec\": {:.1},\n  \"elapsed_secs\": {:.3},\n  \"base_seed\": {},\n  \"best_thread\": {},\n  \"best_seed\": {},\n  \"extra\": \"{}\",\n  \"timestamp_unix\": {}\n}}\n",
        meta.mode,
        meta.n,
        meta.k,
        meta.v,
        meta.uncovered,
        meta.total_moves,
        meta.moves_per_sec,
        meta.elapsed_secs,
        meta.base_seed,
        meta.best_thread,
        meta.best_seed,
        escaped_extra,
        ts
    );
    let tmp_path = path.with_extension("json.tmp");
    fs::write(&tmp_path, json).map_err(|e| format!("write {}: {}", tmp_path.display(), e))?;
    fs::rename(&tmp_path, path)
        .map_err(|e| format!("rename {} -> {}: {}", tmp_path.display(), path.display(), e))?;
    Ok(())
}

/// Drop column `drop_col` from an `(n, k)` matrix, returning `(n, k-1)` matrix.
pub fn project_drop_col(mat: &[u8], n: usize, k: usize, drop_col: usize) -> Vec<u8> {
    assert!(drop_col < k && k >= 4);
    let new_k = k - 1;
    let mut out = Vec::with_capacity(n * new_k);
    for r in 0..n {
        let row = &mat[r * k..(r + 1) * k];
        for (c, &val) in row.iter().enumerate() {
            if c != drop_col {
                out.push(val);
            }
        }
    }
    out
}

/// Delete row `del_row` from an `(n, k)` matrix, returning `(n-1, k)` matrix.
pub fn delete_row(mat: &[u8], n: usize, k: usize, del_row: usize) -> Vec<u8> {
    assert!(del_row < n && n >= 2);
    let mut out = Vec::with_capacity((n - 1) * k);
    for r in 0..n {
        if r != del_row {
            out.extend_from_slice(&mat[r * k..(r + 1) * k]);
        }
    }
    out
}
