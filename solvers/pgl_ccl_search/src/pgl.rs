use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;

/// Exact finite field arithmetic for GF(5), GF(9) = GF(3)[x]/(x^2+1), and GF(11).
pub struct FiniteField {
    pub q: usize,
    add: Vec<Vec<usize>>,
    mul: Vec<Vec<usize>>,
    neg: Vec<usize>,
    inv: Vec<usize>, // inv[0] = 0 (unused)
}

impl FiniteField {
    pub fn new(q: usize) -> Self {
        match q {
            5 | 11 => Self::new_prime(q),
            9 => Self::new_gf9(),
            _ => panic!("Unsupported field order q={q}; supported: 5, 9, 11"),
        }
    }

    fn new_prime(q: usize) -> Self {
        let mut add = vec![vec![0; q]; q];
        let mut mul = vec![vec![0; q]; q];
        let mut neg = vec![0; q];
        let mut inv = vec![0; q];

        for a in 0..q {
            neg[a] = (q - a) % q;
            for b in 0..q {
                add[a][b] = (a + b) % q;
                mul[a][b] = (a * b) % q;
            }
        }
        for a in 1..q {
            let mut found = 0;
            for b in 1..q {
                if mul[a][b] == 1 {
                    assert_eq!(found, 0, "Duplicate inverse in GF({q}) for {a}");
                    found = b;
                }
            }
            assert_ne!(found, 0, "No inverse in GF({q}) for {a}");
            inv[a] = found;
        }
        let ff = Self { q, add, mul, neg, inv };
        ff.verify_axioms();
        ff
    }

    /// GF(9) = GF(3)[x] / (x^2 + 1), encoded as e = a + 3*b with a, b in {0, 1, 2}.
    fn new_gf9() -> Self {
        let q = 9;
        let mut add = vec![vec![0; q]; q];
        let mut mul = vec![vec![0; q]; q];
        let mut neg = vec![0; q];
        let mut inv = vec![0; q];

        for e1 in 0..q {
            let a1 = e1 % 3;
            let b1 = e1 / 3;
            neg[e1] = ((3 - a1) % 3) + 3 * ((3 - b1) % 3);
            for e2 in 0..q {
                let a2 = e2 % 3;
                let b2 = e2 / 3;
                let sa = (a1 + a2) % 3;
                let sb = (b1 + b2) % 3;
                add[e1][e2] = sa + 3 * sb;

                // (a1 + b1 x)(a2 + b2 x) = (a1*a2 - b1*b2) + (a1*b2 + b1*a2) x  (x^2 = -1)
                let ma = (a1 * a2 + 9 - b1 * b2) % 3;
                let mb = (a1 * b2 + b1 * a2) % 3;
                mul[e1][e2] = ma + 3 * mb;
            }
        }
        for a in 1..q {
            let mut found = 0;
            for b in 1..q {
                if mul[a][b] == 1 {
                    assert_eq!(found, 0, "Duplicate inverse in GF(9) for {a}");
                    found = b;
                }
            }
            assert_ne!(found, 0, "No inverse in GF(9) for {a}");
            inv[a] = found;
        }
        let ff = Self { q, add, mul, neg, inv };
        ff.verify_axioms();
        ff
    }

    fn verify_axioms(&self) {
        let q = self.q;
        for a in 0..q {
            assert_eq!(self.add[a][0], a);
            assert_eq!(self.add[a][self.neg[a]], 0);
            assert_eq!(self.mul[a][0], 0);
            assert_eq!(self.mul[a][1], a);
            if a > 0 {
                assert_eq!(self.mul[a][self.inv[a]], 1);
            }
            for b in 0..q {
                assert_eq!(self.add[a][b], self.add[b][a]);
                assert_eq!(self.mul[a][b], self.mul[b][a]);
                for c in 0..q {
                    assert_eq!(
                        self.mul[a][self.add[b][c]],
                        self.add[self.mul[a][b]][self.mul[a][c]]
                    );
                }
            }
        }
    }

    #[inline]
    pub fn add(&self, a: usize, b: usize) -> usize {
        self.add[a][b]
    }

    #[inline]
    pub fn mul(&self, a: usize, b: usize) -> usize {
        self.mul[a][b]
    }

    #[inline]
    pub fn neg(&self, a: usize) -> usize {
        self.neg[a]
    }

    #[inline]
    pub fn inv(&self, a: usize) -> usize {
        debug_assert!(a > 0 && a < self.q);
        self.inv[a]
    }
}

/// Generate all q*(q^2 - 1) permutations of PGL(2, q) acting on P^1(GF(q)) = {0..q} (with inf = q).
/// Runs a built-in exact self-test for order, bijection, distinctness, and sharp 3-transitivity.
pub fn generate_pgl2(q: usize) -> Vec<Vec<u8>> {
    let ff = FiniteField::new(q);
    let v = q + 1;
    let inf = q;
    let expected_order = q * (q * q - 1);
    let mut perms: Vec<Vec<u8>> = Vec::with_capacity(expected_order);

    // Case 1: c = 0, d = 1 => z -> a*z + b (a != 0), inf -> inf
    for a in 1..q {
        for b in 0..q {
            let mut p = vec![0u8; v];
            for z in 0..q {
                p[z] = ff.add(ff.mul(a, z), b) as u8;
            }
            p[inf] = inf as u8;
            perms.push(p);
        }
    }

    // Case 2: c = 1 => z -> (a*z + b) / (z + d), det = a*d - b != 0
    for a in 0..q {
        for d in 0..q {
            let ad = ff.mul(a, d);
            let neg_d = ff.neg(d);
            for b in 0..q {
                if b == ad {
                    continue;
                }
                let mut p = vec![0u8; v];
                for z in 0..q {
                    if z == neg_d {
                        p[z] = inf as u8;
                    } else {
                        let num = ff.add(ff.mul(a, z), b);
                        let den = ff.add(z, d);
                        p[z] = ff.mul(num, ff.inv(den)) as u8;
                    }
                }
                p[inf] = a as u8;
                perms.push(p);
            }
        }
    }

    assert_eq!(
        perms.len(),
        expected_order,
        "PGL(2,{q}) size mismatch: got {}, expected {expected_order}",
        perms.len()
    );

    // Self-test: every element is a bijection on {0..v-1}, and action on (0, 1, 2)
    // hits every ordered 3-distinct triple in {0..v-1}^3 exactly once (proving sharp 3-transitivity
    // AND pairwise distinctness simultaneously!).
    let mut seen_triple = vec![false; v * v * v];
    let mut distinct_triples = 0usize;
    for p in &perms {
        let mut used = vec![false; v];
        for &img in p {
            let x = img as usize;
            assert!(x < v, "Image out of range in PGL(2,{q})");
            assert!(!used[x], "Not a bijection in PGL(2,{q})");
            used[x] = true;
        }
        let a = p[0] as usize;
        let b = p[1] as usize;
        let c = p[2] as usize;
        assert!(a != b && b != c && a != c);
        let idx = (a * v + b) * v + c;
        assert!(
            !seen_triple[idx],
            "Duplicate image of (0,1,2) in PGL(2,{q}): ({a},{b},{c})"
        );
        seen_triple[idx] = true;
        distinct_triples += 1;
    }
    assert_eq!(
        distinct_triples,
        v * (v - 1) * (v - 2),
        "PGL(2,{q}) failed sharp 3-transitivity check"
    );

    perms
}

/// Generate oriented pairs for all v*(v-1)/2 unordered pairs {u, w} such that every symbol
/// appears at least once as left (0) and at least once as right (1).
/// Uses directed cycle (0,1), (1,2), ..., (v-2,v-1), (v-1,0) plus all remaining pairs (u, w) with u < w.
pub fn generate_oriented_pairs(v: usize) -> Vec<(u8, u8)> {
    assert!(v >= 3, "v must be >= 3 for cycle orientation");
    let expected = v * (v - 1) / 2;
    let mut pairs = Vec::with_capacity(expected);

    // Directed cycle
    for u in 0..v {
        let w = (u + 1) % v;
        pairs.push((u as u8, w as u8));
    }
    // Remaining unordered pairs with u < w
    for u in 0..v {
        for w in (u + 2)..v {
            if u == 0 && w == v - 1 {
                continue; // already in cycle as (v-1, 0)
            }
            pairs.push((u as u8, w as u8));
        }
    }

    assert_eq!(pairs.len(), expected, "Oriented pair count mismatch");

    // Self-test: every unordered pair appears exactly once, and every symbol appears >=1 left & >=1 right
    let mut seen_pair = vec![vec![false; v]; v];
    let mut left_cnt = vec![0usize; v];
    let mut right_cnt = vec![0usize; v];
    for &(u, w) in &pairs {
        let uu = u as usize;
        let ww = w as usize;
        assert!(uu < v && ww < v && uu != ww);
        let (lo, hi) = if uu < ww { (uu, ww) } else { (ww, uu) };
        assert!(!seen_pair[lo][hi], "Duplicate unordered pair ({lo}, {hi})");
        seen_pair[lo][hi] = true;
        left_cnt[uu] += 1;
        right_cnt[ww] += 1;
    }
    for s in 0..v {
        assert!(left_cnt[s] >= 1, "Symbol {s} never appears on left");
        assert!(right_cnt[s] >= 1, "Symbol {s} never appears on right");
    }

    pairs
}

/// Run startup self-tests for PGL(2,5), PGL(2,9), PGL(2,11) and oriented pairs.
pub fn run_pgl_selftests() {
    for &q in &[5usize, 9, 11] {
        let perms = generate_pgl2(q);
        assert_eq!(perms.len(), q * (q * q - 1));
        let pairs = generate_oriented_pairs(q + 1);
        assert_eq!(pairs.len(), (q + 1) * q / 2);
    }
}

/// Compute total row count N for the PGL(2,q) + binary CCL construction.
pub fn total_rows(v: usize, m: usize, cover_const: bool) -> usize {
    let q = v - 1;
    let pgl_rows = 2 * q * (q * q - 1);
    let ccl_rows = m * (v * (v - 1) / 2);
    let const_rows = if cover_const { 0 } else { v };
    pgl_rows + ccl_rows + const_rows
}

/// Expand the 2 deterministic PGL(2,q) orbits + M x k binary CCL matrix into a canonical CA file.
/// Returns the exact number of rows written.
pub fn expand_to_file(
    v: usize,
    k: usize,
    matrix_rows: &[u32],
    cover_const: bool,
    out_path: &Path,
) -> std::io::Result<usize> {
    let q = v - 1;
    let left_len = k / 2;
    let right_len = k - left_len;
    assert!(
        left_len <= q && right_len <= q,
        "k={k} exceeds 2*q={} for v={v}",
        2 * q
    );

    let perms = generate_pgl2(q);
    let pairs = generate_oriented_pairs(v);

    // Starter r1: 0 on L, 1..=|R| on R
    let mut r1 = vec![0usize; k];
    for i in 0..right_len {
        r1[left_len + i] = i + 1;
    }
    // Starter r2: 0..|L| on L, q on R
    let mut r2 = vec![0usize; k];
    for i in 0..left_len {
        r2[i] = i;
    }
    for i in 0..right_len {
        r2[left_len + i] = q;
    }

    let file = File::create(out_path)?;
    let mut writer = BufWriter::with_capacity(1 << 20, file);
    let mut row_count = 0usize;
    let mut line_buf = String::with_capacity(k * 3 + 2);

    let mut write_row = |vals: &[u8]| -> std::io::Result<()> {
        line_buf.clear();
        for (i, &val) in vals.iter().enumerate() {
            if i > 0 {
                line_buf.push(' ');
            }
            if val >= 10 {
                line_buf.push((b'0' + val / 10) as char);
                line_buf.push((b'0' + val % 10) as char);
            } else {
                line_buf.push((b'0' + val) as char);
            }
        }
        line_buf.push('\n');
        writer.write_all(line_buf.as_bytes())?;
        row_count += 1;
        Ok(())
    };

    let mut row_vals = vec![0u8; k];

    // Block 1a: PGL(2,q) orbit of r1
    for p in &perms {
        for c in 0..k {
            row_vals[c] = p[r1[c]];
        }
        write_row(&row_vals)?;
    }

    // Block 1b: PGL(2,q) orbit of r2
    for p in &perms {
        for c in 0..k {
            row_vals[c] = p[r2[c]];
        }
        write_row(&row_vals)?;
    }

    // Block 2: Oriented pair expansion of binary CCL matrix C
    for &(u, w) in &pairs {
        for &bits in matrix_rows {
            for c in 0..k {
                row_vals[c] = if ((bits >> c) & 1) == 0 { u } else { w };
            }
            write_row(&row_vals)?;
        }
    }

    // Optional Block 3: v constant rows when --cover-const is false
    if !cover_const {
        for s in 0..v {
            row_vals.fill(s as u8);
            write_row(&row_vals)?;
        }
    }

    writer.flush()?;
    let expected_n = total_rows(v, matrix_rows.len(), cover_const);
    assert_eq!(row_count, expected_n, "Written row count mismatch");
    Ok(row_count)
}
