use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;

/// Exact finite field arithmetic tables for GF(q), q in {5, 9, 11}.
pub struct FiniteField {
    pub q: usize,
    pub add: Vec<Vec<usize>>,
    pub sub: Vec<Vec<usize>>,
    pub mul: Vec<Vec<usize>>,
    pub inv: Vec<usize>,
}

impl FiniteField {
    pub fn new(q: usize) -> Self {
        let mut add = vec![vec![0; q]; q];
        let mut sub = vec![vec![0; q]; q];
        let mut mul = vec![vec![0; q]; q];

        match q {
            5 | 11 | 13 => {
                for a in 0..q {
                    for b in 0..q {
                        add[a][b] = (a + b) % q;
                        sub[a][b] = (a + q - b) % q;
                        mul[a][b] = (a * b) % q;
                    }
                }
            }
            9 => {
                // GF(9) = GF(3)[x] / (x^2 + 1)
                // Element a = a0 + a1*x encoded as a0 + 3*a1, a0,a1 in {0,1,2}
                for a in 0..9 {
                    let a0 = a % 3;
                    let a1 = a / 3;
                    for b in 0..9 {
                        let b0 = b % 3;
                        let b1 = b / 3;
                        let s0 = (a0 + b0) % 3;
                        let s1 = (a1 + b1) % 3;
                        add[a][b] = s0 + 3 * s1;

                        let d0 = (a0 + 3 - b0) % 3;
                        let d1 = (a1 + 3 - b1) % 3;
                        sub[a][b] = d0 + 3 * d1;

                        // (a0 + a1*x)(b0 + b1*x) = (a0*b0 - a1*b1) + (a0*b1 + a1*b0)*x (mod 3, x^2 = -1 = 2)
                        let m0 = (a0 * b0 + 2 * a1 * b1) % 3;
                        let m1 = (a0 * b1 + a1 * b0) % 3;
                        mul[a][b] = m0 + 3 * m1;
                    }
                }
            }
            _ => panic!("Unsupported prime power q={} (supported: 5, 9, 11, 13)", q),
        }

        let mut inv = vec![0; q];
        for a in 1..q {
            let mut found = None;
            for b in 1..q {
                if mul[a][b] == 1 {
                    assert!(found.is_none(), "Non-unique inverse for {} in GF({})", a, q);
                    found = Some(b);
                }
            }
            inv[a] = found.unwrap_or_else(|| panic!("No inverse for {} in GF({})", a, q));
        }

        let ff = Self { q, add, sub, mul, inv };
        ff.verify_axioms();
        ff
    }

    fn verify_axioms(&self) {
        let q = self.q;
        for a in 0..q {
            assert_eq!(self.add[a][0], a);
            assert_eq!(self.mul[a][1], a);
            assert_eq!(self.mul[a][0], 0);
            assert_eq!(self.sub[a][a], 0);
            if a > 0 {
                assert_eq!(self.mul[a][self.inv[a]], 1);
            }
            for b in 0..q {
                assert_eq!(self.add[a][b], self.add[b][a]);
                assert_eq!(self.mul[a][b], self.mul[b][a]);
                assert_eq!(self.add[self.sub[a][b]][b], a);
                for c in 0..q {
                    assert_eq!(self.add[self.add[a][b]][c], self.add[a][self.add[b][c]]);
                    assert_eq!(self.mul[self.mul[a][b]][c], self.mul[a][self.mul[b][c]]);
                    assert_eq!(
                        self.mul[a][self.add[b][c]],
                        self.add[self.mul[a][b]][self.mul[a][c]]
                    );
                }
            }
        }
    }
}

/// Generate all q*(q^2 - 1) permutations of PGL(2, q) acting on P^1(GF(q)) = {0..q-1, q=inf}.
pub fn generate_pgl2(q: usize) -> Vec<Vec<u8>> {
    let ff = FiniteField::new(q);
    let v = q + 1;
    let inf = q;
    let expected = q * (q * q - 1);
    let mut perms = Vec::with_capacity(expected);

    // Case 1: c = 0, d = 1, a in GF(q)*, b in GF(q): z -> a*z + b, inf -> inf
    for a in 1..q {
        for b in 0..q {
            let mut p = vec![0u8; v];
            for z in 0..q {
                p[z] = ff.add[ff.mul[a][z]][b] as u8;
            }
            p[inf] = inf as u8;
            perms.push(p);
        }
    }

    // Case 2: c = 1, a, d, b in GF(q) with a*d - b != 0: z -> (a*z + b) / (z + d), inf -> a, -d -> inf
    for a in 0..q {
        for d in 0..q {
            let ad = ff.mul[a][d];
            for b in 0..q {
                if b == ad {
                    continue;
                }
                let mut p = vec![0u8; v];
                for z in 0..q {
                    let denom = ff.add[z][d];
                    if denom == 0 {
                        p[z] = inf as u8;
                    } else {
                        let num = ff.add[ff.mul[a][z]][b];
                        p[z] = ff.mul[num][ff.inv[denom]] as u8;
                    }
                }
                p[inf] = a as u8;
                perms.push(p);
            }
        }
    }

    assert_eq!(perms.len(), expected);
    perms
}

/// Verify cardinality, bijectivity, pairwise distinctness, and sharp 3-transitivity of PGL(2, q).
pub fn self_test_pgl2(q: usize) -> Vec<Vec<u8>> {
    let perms = generate_pgl2(q);
    let v = q + 1;
    let expected = q * (q * q - 1);
    assert_eq!(
        perms.len(),
        expected,
        "PGL(2,{}) size mismatch: {} != {}",
        q,
        perms.len(),
        expected
    );

    // Check bijectivity
    for (idx, p) in perms.iter().enumerate() {
        assert_eq!(p.len(), v);
        let mut seen = vec![false; v];
        for &val in p {
            let u = val as usize;
            assert!(u < v, "Out-of-range symbol {} in perm {}", u, idx);
            assert!(!seen[u], "Duplicate symbol {} in perm {}", u, idx);
            seen[u] = true;
        }
    }

    // Check sharp 3-transitivity on (0, 1, 2) -> all v*(v-1)*(v-2) ordered distinct triples
    // Since every perm is uniquely determined by image of (0,1,2) in a sharply 3-transitive group,
    // hitting all v*(v-1)*(v-2) distinct triples also proves all perms are pairwise distinct!
    let mut triple_hit = vec![0u32; v * v * v];
    for p in &perms {
        let a = p[0] as usize;
        let b = p[1] as usize;
        let c = p[2] as usize;
        assert!(a != b && a != c && b != c);
        let idx = (a * v + b) * v + c;
        triple_hit[idx] += 1;
    }

    let mut distinct_triples = 0usize;
    for a in 0..v {
        for b in 0..v {
            if b == a {
                continue;
            }
            for c in 0..v {
                if c == a || c == b {
                    continue;
                }
                let idx = (a * v + b) * v + c;
                assert_eq!(
                    triple_hit[idx], 1,
                    "PGL(2,{}) not sharply 3-transitive at ({},{},{}): hit {} times",
                    q, a, b, c, triple_hit[idx]
                );
                distinct_triples += 1;
            }
        }
    }
    assert_eq!(distinct_triples, expected);

    // Extra sanity: sort copy and check no duplicate permutations
    let mut sorted = perms.clone();
    sorted.sort();
    sorted.dedup();
    assert_eq!(sorted.len(), expected, "Duplicate permutations in PGL(2,{})", q);

    perms
}

/// Generate oriented pairs for all v*(v-1)/2 unordered pairs such that every symbol 0..v-1
/// appears at least once as the first element (0) and at least once as the second element (1).
pub fn oriented_pairs(v: usize) -> Vec<(u8, u8)> {
    assert!(v >= 3, "v must be >= 3");
    let expected = v * (v - 1) / 2;
    let mut pairs = Vec::with_capacity(expected);

    // Directed cycle: (0,1), (1,2), ..., (v-2,v-1), (v-1,0)
    for u in 0..v {
        let w = (u + 1) % v;
        pairs.push((u as u8, w as u8));
    }

    // Remaining unordered pairs with u < w
    for u in 0..v {
        for w in (u + 1)..v {
            if w == u + 1 || (u == 0 && w == v - 1) {
                continue;
            }
            pairs.push((u as u8, w as u8));
        }
    }

    assert_eq!(pairs.len(), expected);

    // Self-check: every unordered pair occurs once, every symbol occurs left & right
    let mut seen_pair = vec![vec![false; v]; v];
    let mut has_left = vec![false; v];
    let mut has_right = vec![false; v];
    for &(u, w) in &pairs {
        let ui = u as usize;
        let wi = w as usize;
        assert_ne!(ui, wi);
        let (a, b) = if ui < wi { (ui, wi) } else { (wi, ui) };
        assert!(!seen_pair[a][b], "Duplicate unordered pair ({},{})", a, b);
        seen_pair[a][b] = true;
        has_left[ui] = true;
        has_right[wi] = true;
    }
    for s in 0..v {
        assert!(has_left[s], "Symbol {} never appears as 0-slot", s);
        assert!(has_right[s], "Symbol {} never appears as 1-slot", s);
    }

    pairs
}

/// Expand the 2 deterministic PGL(2, q) orbits + binary CCL matrix C (M x k)
/// (+ v constant rows if !cover_const) into an in-memory Vec<Vec<u8>>.
pub fn expand_ca_rows(
    q: usize,
    k: usize,
    m: usize,
    mat: &[u8],
    cover_const: bool,
) -> Vec<Vec<u8>> {
    let v = q + 1;
    let l_size = k / 2;
    let r_size = k - l_size;
    assert!(k >= 3, "k must be >= 3");
    assert!(
        l_size <= q && r_size <= q,
        "k={} exceeds 2*q={} for PGL(2,{})",
        k,
        2 * q,
        q
    );
    assert_eq!(mat.len(), m * k);

    let perms = self_test_pgl2(q);
    let pairs = oriented_pairs(v);

    let mut r1 = vec![0usize; k];
    for c in 0..l_size {
        r1[c] = 0;
    }
    for c in l_size..k {
        r1[c] = 1 + (c - l_size);
    }

    let mut r2 = vec![0usize; k];
    for c in 0..l_size {
        r2[c] = c;
    }
    for c in l_size..k {
        r2[c] = q;
    }

    let expected_n = 2 * perms.len() + m * pairs.len() + if cover_const { 0 } else { v };
    let mut rows = Vec::with_capacity(expected_n);

    for p in &perms {
        let mut row = Vec::with_capacity(k);
        for c in 0..k {
            row.push(p[r1[c]]);
        }
        rows.push(row);
    }
    for p in &perms {
        let mut row = Vec::with_capacity(k);
        for c in 0..k {
            row.push(p[r2[c]]);
        }
        rows.push(row);
    }
    for &(u, w) in &pairs {
        for r in 0..m {
            let crow = &mat[r * k..(r + 1) * k];
            let mut row = Vec::with_capacity(k);
            for c in 0..k {
                row.push(if crow[c] == 0 { u } else { w });
            }
            rows.push(row);
        }
    }
    if !cover_const {
        for a in 0..v {
            rows.push(vec![a as u8; k]);
        }
    }
    assert_eq!(rows.len(), expected_n);
    rows
}

/// Write canonical CA text file from rows.
pub fn write_ca_rows(rows: &[Vec<u8>], out_path: &Path) -> std::io::Result<usize> {
    if let Some(parent) = out_path.parent() {
        if !parent.as_os_str().is_empty() {
            std::fs::create_dir_all(parent)?;
        }
    }
    let file = File::create(out_path)?;
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
    Ok(rows.len())
}

/// Expand the 2 deterministic PGL(2, q) orbits + binary CCL matrix C (M x k)
/// (+ v constant rows if !cover_const) and write canonical CA text file.
/// Returns total number of rows N.
pub fn expand_and_write_ca(
    q: usize,
    k: usize,
    m: usize,
    mat: &[u8],
    cover_const: bool,
    out_path: &Path,
) -> std::io::Result<usize> {
    let rows = expand_ca_rows(q, k, m, mat, cover_const);
    write_ca_rows(&rows, out_path)
}
