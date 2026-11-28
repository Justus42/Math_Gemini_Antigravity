/*
 * Phase 9B Pilot: Fast C Checker & Multi-Stage Scanner for
 * Hyperplane-Pencil CPHF(2; 2q+2, q, 6) over F_q (q in {5, 7, 8, 9}).
 *
 * Build:
 *   gcc -O3 -march=native -pthread scripts/phase9_cphf_t6_pencil.c -o /tmp/phase9_cphf_t6_pencil
 *
 * Modes:
 *   check  <q> <g1_0> <g1_1> <g2_0> <g2_1> <a0> <a1> <b0> <b1> <m1> <d1> <frob1> <m2> <d2>
 *   stage1 <q> [--out-dir <dir>] [--timeout <sec>] [--threads <n>]
 *   stage2 <q> [--out-dir <dir>] [--timeout <sec>] [--seed <seed>]
 *   stage3 <q> <kA> <kB> [--out-dir <dir>] [--timeout <sec>] [--seed <seed>]
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <pthread.h>

#define MAX_Q 9
#define MAX_ORB 10
#define MAX_K 20
#define MAX_CRIT 34000
#define MAX_WORDS ((MAX_CRIT + 63) / 64)

/* ---------- Timing ---------- */
static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

/* ---------- Fast PRNG (xoshiro256**) ---------- */
typedef struct { uint64_t s[4]; } Rng;

static uint64_t splitmix64(uint64_t *x) {
    uint64_t z = (*x += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

static void rng_seed(Rng *r, uint64_t seed) {
    for (int i = 0; i < 4; i++) r->s[i] = splitmix64(&seed);
}

static inline uint64_t rotl64(uint64_t x, int k) {
    return (x << k) | (x >> (64 - k));
}

static inline uint64_t rng_u64(Rng *r) {
    uint64_t res = rotl64(r->s[1] * 5, 7) * 9;
    uint64_t t = r->s[1] << 17;
    r->s[2] ^= r->s[0];
    r->s[3] ^= r->s[1];
    r->s[1] ^= r->s[2];
    r->s[0] ^= r->s[3];
    r->s[2] ^= t;
    r->s[3] = rotl64(r->s[3], 45);
    return res;
}

static inline uint32_t rng_int(Rng *r, uint32_t bound) {
    return (uint32_t)(rng_u64(r) % bound);
}

static inline double rng_double(Rng *r) {
    return (double)(rng_u64(r) >> 11) * (1.0 / 9007199254740992.0);
}

/* ---------- Finite Field F_q and K = F_{q^2} ---------- */
typedef struct {
    uint8_t a, b;
} KElem;

typedef struct {
    int q;
    int n_orb;      /* q + 1 */
    int k_full;     /* 2q + 2 */
    int k_order;    /* q^2 - 1 */
    uint8_t add[MAX_Q][MAX_Q];
    uint8_t sub[MAX_Q][MAX_Q];
    uint8_t mul[MAX_Q][MAX_Q];
    uint8_t inv[MAX_Q];
    uint8_t p0, p1; /* i^2 = p0 + p1*i */
    KElem zeta;
    KElem eta;
    KElem zeta_pow[81]; /* zeta^e for e = 0..q^2-1 */
    KElem eta_pow[MAX_ORB];
    KElem k_nonzero[80]; /* all q^2-1 nonzero elements of K */
} FF;

static uint8_t mul8_raw(uint8_t a, uint8_t b) {
    uint16_t r = 0;
    for (int i = 0; i < 3; i++) {
        if ((b >> i) & 1) r ^= (uint16_t)a << i;
    }
    for (int i = 4; i >= 3; i--) {
        if ((r >> i) & 1) r ^= (uint16_t)(0x0B << (i - 3));
    }
    return (uint8_t)r;
}

static inline KElem k_mul(const FF *ff, KElem u, KElem v) {
    uint8_t bd = ff->mul[u.b][v.b];
    KElem r;
    r.a = ff->add[ff->mul[u.a][v.a]][ff->mul[bd][ff->p0]];
    r.b = ff->add[ff->add[ff->mul[u.a][v.b]][ff->mul[u.b][v.a]]][ff->mul[bd][ff->p1]];
    return r;
}

static KElem k_pow(const FF *ff, KElem u, int e) {
    KElem r = {1, 0};
    KElem b = u;
    while (e > 0) {
        if (e & 1) r = k_mul(ff, r, b);
        b = k_mul(ff, b, b);
        e >>= 1;
    }
    return r;
}

static void ff_init(FF *ff, int q) {
    memset(ff, 0, sizeof(*ff));
    ff->q = q;
    ff->n_orb = q + 1;
    ff->k_full = 2 * q + 2;
    ff->k_order = q * q - 1;

    if (q == 5 || q == 7) {
        for (int a = 0; a < q; a++) {
            for (int b = 0; b < q; b++) {
                ff->add[a][b] = (uint8_t)((a + b) % q);
                ff->sub[a][b] = (uint8_t)((a - b + q) % q);
                ff->mul[a][b] = (uint8_t)((a * b) % q);
            }
        }
    } else if (q == 8) {
        for (int a = 0; a < 8; a++) {
            for (int b = 0; b < 8; b++) {
                ff->add[a][b] = (uint8_t)(a ^ b);
                ff->sub[a][b] = (uint8_t)(a ^ b);
                ff->mul[a][b] = mul8_raw((uint8_t)a, (uint8_t)b);
            }
        }
    } else if (q == 9) {
        for (int a = 0; a < 9; a++) {
            int a0 = a % 3, a1 = a / 3;
            for (int b = 0; b < 9; b++) {
                int b0 = b % 3, b1 = b / 3;
                ff->add[a][b] = (uint8_t)(((a0 + b0) % 3) + 3 * ((a1 + b1) % 3));
                ff->sub[a][b] = (uint8_t)(((a0 - b0 + 3) % 3) + 3 * ((a1 - b1 + 3) % 3));
                int r0 = (a0 * b0 - a1 * b1 + 9) % 3;
                int r1 = (a0 * b1 + a1 * b0) % 3;
                ff->mul[a][b] = (uint8_t)(r0 + 3 * r1);
            }
        }
    } else {
        fprintf(stderr, "Unsupported q=%d\n", q);
        exit(1);
    }

    for (int a = 1; a < q; a++) {
        for (int b = 1; b < q; b++) {
            if (ff->mul[a][b] == 1) {
                ff->inv[a] = (uint8_t)b;
                break;
            }
        }
    }

    if (q == 5)      { ff->p0 = 2; ff->p1 = 0; ff->zeta = (KElem){2, 1}; }
    else if (q == 7) { ff->p0 = 3; ff->p1 = 0; ff->zeta = (KElem){1, 1}; }
    else if (q == 8) { ff->p0 = 1; ff->p1 = 1; ff->zeta = (KElem){2, 1}; }
    else if (q == 9) { ff->p0 = 4; ff->p1 = 0; ff->zeta = (KElem){3, 1}; }

    ff->eta = k_pow(ff, ff->zeta, q - 1);
    for (int e = 0; e <= ff->k_order; e++) {
        ff->zeta_pow[e] = k_pow(ff, ff->zeta, e);
    }
    for (int e = 0; e < ff->n_orb; e++) {
        ff->eta_pow[e] = k_pow(ff, ff->eta, e);
    }
    int idx = 0;
    for (int a = 0; a < q; a++) {
        for (int b = 0; b < q; b++) {
            if (a == 0 && b == 0) continue;
            ff->k_nonzero[idx++] = (KElem){(uint8_t)a, (uint8_t)b};
        }
    }
}

static int gcd_int(int a, int b) {
    while (b) { int t = a % b; a = b; b = t; }
    return a;
}

/* ---------- Exact 6x6 Full-Rank Check over F_q ---------- */
static inline int rank6_full(const FF *ff, uint8_t m[6][6]) {
    for (int col = 0; col < 6; col++) {
        int piv = -1;
        for (int r = col; r < 6; r++) {
            if (m[r][col] != 0) { piv = r; break; }
        }
        if (piv < 0) return 0;
        if (piv != col) {
            for (int j = col; j < 6; j++) {
                uint8_t tmp = m[col][j];
                m[col][j] = m[piv][j];
                m[piv][j] = tmp;
            }
        }
        uint8_t inv_p = ff->inv[m[col][col]];
        for (int r = col + 1; r < 6; r++) {
            uint8_t v = m[r][col];
            if (v != 0) {
                uint8_t f = ff->mul[v][inv_p];
                for (int j = col + 1; j < 6; j++) {
                    m[r][j] = ff->sub[m[r][j]][ff->mul[f][m[col][j]]];
                }
            }
        }
    }
    return 1;
}

static inline int rank4_full(const FF *ff, uint8_t m[4][4]) {
    for (int col = 0; col < 4; col++) {
        int piv = -1;
        for (int r = col; r < 4; r++) {
            if (m[r][col] != 0) { piv = r; break; }
        }
        if (piv < 0) return 0;
        if (piv != col) {
            for (int j = col; j < 4; j++) {
                uint8_t tmp = m[col][j];
                m[col][j] = m[piv][j];
                m[piv][j] = tmp;
            }
        }
        uint8_t inv_p = ff->inv[m[col][col]];
        for (int r = col + 1; r < 4; r++) {
            uint8_t v = m[r][col];
            if (v != 0) {
                uint8_t f = ff->mul[v][inv_p];
                for (int j = col + 1; j < 4; j++) {
                    m[r][j] = ff->sub[m[r][j]][ff->mul[f][m[col][j]]];
                }
            }
        }
    }
    return 1;
}

static inline int det3_nonzero(const FF *ff, const uint8_t m[3][3]) {
    uint8_t t0 = ff->sub[ff->mul[m[1][1]][m[2][2]]][ff->mul[m[1][2]][m[2][1]]];
    uint8_t t1 = ff->sub[ff->mul[m[1][0]][m[2][2]]][ff->mul[m[1][2]][m[2][0]]];
    uint8_t t2 = ff->sub[ff->mul[m[1][0]][m[2][1]]][ff->mul[m[1][1]][m[2][0]]];
    uint8_t res = ff->add[ff->sub[ff->mul[m[0][0]][t0]][ff->mul[m[0][1]][t1]]][ff->mul[m[0][2]][t2]];
    return res != 0;
}

static inline int det2_nonzero(const FF *ff, const uint8_t m[2][2]) {
    return ff->sub[ff->mul[m[0][0]][m[1][1]]][ff->mul[m[0][1]][m[1][0]]] != 0;
}

/* Compute nullspace basis N (size (6-a) x 6) of an a x 6 full-rank matrix A */
static void compute_nullspace(const FF *ff, int a, const uint8_t A_in[4][6], uint8_t N_out[4][6]) {
    uint8_t M[4][6];
    memcpy(M, A_in, (size_t)a * 6);
    int piv_col[4];
    int is_piv[6] = {0, 0, 0, 0, 0, 0};

    int r = 0;
    for (int col = 0; col < 6 && r < a; col++) {
        int p = -1;
        for (int i = r; i < a; i++) {
            if (M[i][col] != 0) { p = i; break; }
        }
        if (p < 0) continue;
        if (p != r) {
            for (int j = 0; j < 6; j++) {
                uint8_t tmp = M[r][j]; M[r][j] = M[p][j]; M[p][j] = tmp;
            }
        }
        uint8_t inv_p = ff->inv[M[r][col]];
        for (int j = col; j < 6; j++) M[r][j] = ff->mul[M[r][j]][inv_p];
        for (int i = 0; i < a; i++) {
            if (i != r && M[i][col] != 0) {
                uint8_t f = M[i][col];
                for (int j = col; j < 6; j++) {
                    M[i][j] = ff->sub[M[i][j]][ff->mul[f][M[r][j]]];
                }
            }
        }
        piv_col[r] = col;
        is_piv[col] = 1;
        r++;
    }
    if (r != a) {
        fprintf(stderr, "FATAL: expected full rank %d, got %d\n", a, r);
        exit(1);
    }

    int free_idx = 0;
    for (int col = 0; col < 6; col++) {
        if (!is_piv[col]) {
            memset(N_out[free_idx], 0, 6);
            N_out[free_idx][col] = 1;
            for (int i = 0; i < a; i++) {
                N_out[free_idx][piv_col[i]] = ff->sub[0][M[i][col]];
            }
            free_idx++;
        }
    }
}

/* ---------- Builders for Row 1 and Row 2 ---------- */
static void build_R1_base(const FF *ff, uint8_t R1_A[MAX_ORB][6]) {
    int q = ff->q;
    for (int k = 0; k < ff->n_orb; k++) {
        KElem w = ff->zeta_pow[k];
        KElem c1 = k_pow(ff, w, 5);
        KElem c2 = k_pow(ff, w, 4 + q);
        KElem c3 = k_pow(ff, w, 3 + 2 * q);
        R1_A[k][0] = c1.a; R1_A[k][1] = c1.b;
        R1_A[k][2] = c2.a; R1_A[k][3] = c2.b;
        R1_A[k][4] = c3.a; R1_A[k][5] = c3.b;
    }
}

static void build_R1_B_param(const FF *ff, KElem g1, KElem g2, KElem g3,
                             int m1, int d1, int frob1, uint8_t R1_B[MAX_ORB][6]) {
    int q = ff->q;
    int n = ff->n_orb;
    for (int k = 0; k < n; k++) {
        int j = (m1 * k + d1) % n;
        KElem w = ff->zeta_pow[j];
        if (frob1) w = k_pow(ff, w, q);
        KElem c1 = k_mul(ff, g1, k_pow(ff, w, 5));
        KElem c2 = k_mul(ff, g2, k_pow(ff, w, 4 + q));
        KElem c3 = k_mul(ff, g3, k_pow(ff, w, 3 + 2 * q));
        R1_B[k][0] = c1.a; R1_B[k][1] = c1.b;
        R1_B[k][2] = c2.a; R1_B[k][3] = c2.b;
        R1_B[k][4] = c3.a; R1_B[k][5] = c3.b;
    }
}

static void build_R2_base(const FF *ff, uint8_t R2_A[MAX_ORB][6]) {
    for (int k = 0; k < ff->n_orb; k++) {
        KElem u = ff->eta_pow[k];
        KElem u2 = k_mul(ff, u, u);
        R2_A[k][0] = u2.a; R2_A[k][1] = u2.b;
        R2_A[k][2] = u.a;  R2_A[k][3] = u.b;
        R2_A[k][4] = 1;    R2_A[k][5] = 0;
    }
}

static void build_R2_B_param(const FF *ff, KElem alpha, KElem beta,
                             int m2, int d2, uint8_t R2_B[MAX_ORB][6]) {
    int n = ff->n_orb;
    for (int k = 0; k < n; k++) {
        int j = (m2 * k + d2) % n;
        KElem u = ff->eta_pow[j];
        KElem u2 = k_mul(ff, u, u);
        KElem a2 = k_mul(ff, alpha, u2);
        KElem b1 = k_mul(ff, beta, u);
        R2_B[k][0] = a2.a; R2_B[k][1] = a2.b;
        R2_B[k][2] = b1.a; R2_B[k][3] = b1.b;
        R2_B[k][4] = 0;    R2_B[k][5] = 1;
    }
}

/* ---------- Full Exact Check over all C(k, 6) 6-tuples ---------- */
static void full_check_matrices(const FF *ff, int kA, int kB,
                                const uint8_t R1[][6], const uint8_t R2[][6],
                                int dep1[7], int dep2[7], int both[7]) {
    int k = kA + kB;
    memset(dep1, 0, 7 * sizeof(int));
    memset(dep2, 0, 7 * sizeof(int));
    memset(both, 0, 7 * sizeof(int));
    uint8_t m1[6][6], m2[6][6];

    for (int c0 = 0; c0 < k; c0++)
    for (int c1 = c0 + 1; c1 < k; c1++)
    for (int c2 = c1 + 1; c2 < k; c2++)
    for (int c3 = c2 + 1; c3 < k; c3++)
    for (int c4 = c3 + 1; c4 < k; c4++)
    for (int c5 = c4 + 1; c5 < k; c5++) {
        int cols[6] = {c0, c1, c2, c3, c4, c5};
        int a = 0;
        for (int i = 0; i < 6; i++) {
            if (cols[i] < kA) a++;
            memcpy(m1[i], R1[cols[i]], 6);
            memcpy(m2[i], R2[cols[i]], 6);
        }
        int ok1 = rank6_full(ff, m1);
        int ok2 = rank6_full(ff, m2);
        if (!ok1) dep1[a]++;
        if (!ok2) dep2[a]++;
        if (!ok1 && !ok2) both[a]++;
    }
}

/* ---------- Critical Tuple Indexing for (4,2), (3,3), (2,4) ---------- */
typedef struct {
    uint8_t a_cnt;       /* 4, 3, or 2 */
    uint8_t a_idx[4];    /* indices in 0..n_orb-1 */
    uint8_t b_idx[4];    /* indices in 0..n_orb-1 */
    uint16_t a_comb_id;  /* index into comb_A list for that a_cnt */
    uint16_t b_comb_id;  /* index into comb_B list for that b_cnt */
    uint32_t col_mask;   /* 6-bit mask over 0..2q+1 */
} CritTuple;

typedef struct {
    int n_orb;
    int n_42, n_33, n_24, n_total;
    int w_42_end, w_33_end, w_total; /* word boundaries (separate word-aligned blocks for fast split popcount!) */
    int off_42, off_33, off_24;      /* bit offsets (multiples of 64!) */
    CritTuple *tuples;               /* indexed by logical bit position 0..w_total*64-1? No, packed array + bit_pos */
    int *bit_pos;                    /* bit position for tuple t in 0..n_total-1 */

    /* Combinations of Orbit A (and B) of size 2, 3, 4 */
    int nA2, nA3, nA4;
    uint8_t comb2[45][2];
    uint8_t comb3[120][3];
    uint8_t comb4[210][4];

    /* Precomputed nullspaces for Orbit A of Row 1 and Row 2 */
    uint8_t N1_4[210][2][6];
    uint8_t N1_3[120][3][6];
    uint8_t N1_2[45][4][6];
    uint8_t N2_4[210][2][6];
    uint8_t N2_3[120][3][6];
    uint8_t N2_2[45][4][6];

    /* Lookup from sorted subset bitmask (in 0..2^n_orb-1) to comb id */
    int16_t mask2id[1024];

    /* Z_{q+1} orbit representatives for simultaneous shift (I+1, J+1) */
    int n_orbits;
    int *orb_rep;        /* tuple index of each orbit rep */
    int *orb_len;        /* length of orbit (divides q+1) */
    int *orb_members;    /* flattened member tuple indices */
    int *orb_start;      /* start offset in orb_members */
} CritTable;

static void init_crit_table(CritTable *ct, const FF *ff,
                            const uint8_t R1_A[MAX_ORB][6], const uint8_t R2_A[MAX_ORB][6]) {
    memset(ct, 0, sizeof(*ct));
    int n = ff->n_orb;
    ct->n_orb = n;
    for (int i = 0; i < 1024; i++) ct->mask2id[i] = -1;

    /* Enumerate combinations of sizes 2, 3, 4 */
    ct->nA2 = 0;
    for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++) {
        ct->comb2[ct->nA2][0] = (uint8_t)i;
        ct->comb2[ct->nA2][1] = (uint8_t)j;
        ct->mask2id[(1 << i) | (1 << j)] = (int16_t)ct->nA2;
        ct->nA2++;
    }
    ct->nA3 = 0;
    for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
    for (int k = j + 1; k < n; k++) {
        ct->comb3[ct->nA3][0] = (uint8_t)i;
        ct->comb3[ct->nA3][1] = (uint8_t)j;
        ct->comb3[ct->nA3][2] = (uint8_t)k;
        ct->mask2id[(1 << i) | (1 << j) | (1 << k)] = (int16_t)ct->nA3;
        ct->nA3++;
    }
    ct->nA4 = 0;
    for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
    for (int k = j + 1; k < n; k++)
    for (int l = k + 1; l < n; l++) {
        ct->comb4[ct->nA4][0] = (uint8_t)i;
        ct->comb4[ct->nA4][1] = (uint8_t)j;
        ct->comb4[ct->nA4][2] = (uint8_t)k;
        ct->comb4[ct->nA4][3] = (uint8_t)l;
        ct->mask2id[(1 << i) | (1 << j) | (1 << k) | (1 << l)] = (int16_t)ct->nA4;
        ct->nA4++;
    }

    /* Precompute nullspaces for Row 1 A and Row 2 A */
    uint8_t mat[4][6], Ntmp[4][6];
    for (int id = 0; id < ct->nA4; id++) {
        for (int r = 0; r < 4; r++) memcpy(mat[r], R1_A[ct->comb4[id][r]], 6);
        compute_nullspace(ff, 4, mat, Ntmp);
        memcpy(ct->N1_4[id], Ntmp, 2 * 6);
        for (int r = 0; r < 4; r++) memcpy(mat[r], R2_A[ct->comb4[id][r]], 6);
        compute_nullspace(ff, 4, mat, Ntmp);
        memcpy(ct->N2_4[id], Ntmp, 2 * 6);
    }
    for (int id = 0; id < ct->nA3; id++) {
        for (int r = 0; r < 3; r++) memcpy(mat[r], R1_A[ct->comb3[id][r]], 6);
        compute_nullspace(ff, 3, mat, Ntmp);
        memcpy(ct->N1_3[id], Ntmp, 3 * 6);
        for (int r = 0; r < 3; r++) memcpy(mat[r], R2_A[ct->comb3[id][r]], 6);
        compute_nullspace(ff, 3, mat, Ntmp);
        memcpy(ct->N2_3[id], Ntmp, 3 * 6);
    }
    for (int id = 0; id < ct->nA2; id++) {
        for (int r = 0; r < 2; r++) memcpy(mat[r], R1_A[ct->comb2[id][r]], 6);
        compute_nullspace(ff, 2, mat, Ntmp);
        memcpy(ct->N1_2[id], Ntmp, 4 * 6);
        for (int r = 0; r < 2; r++) memcpy(mat[r], R2_A[ct->comb2[id][r]], 6);
        compute_nullspace(ff, 2, mat, Ntmp);
        memcpy(ct->N2_2[id], Ntmp, 4 * 6);
    }

    ct->n_42 = ct->nA4 * ct->nA2;
    ct->n_33 = ct->nA3 * ct->nA3;
    ct->n_24 = ct->nA2 * ct->nA4;
    ct->n_total = ct->n_42 + ct->n_33 + ct->n_24;

    /* Word-aligned bit layout: [42 words][33 words][24 words] */
    int w42 = (ct->n_42 + 63) / 64;
    int w33 = (ct->n_33 + 63) / 64;
    int w24 = (ct->n_24 + 63) / 64;
    ct->off_42 = 0;
    ct->w_42_end = w42;
    ct->off_33 = w42 * 64;
    ct->w_33_end = w42 + w33;
    ct->off_24 = (w42 + w33) * 64;
    ct->w_total = w42 + w33 + w24;

    ct->tuples = (CritTuple *)malloc((size_t)ct->n_total * sizeof(CritTuple));
    ct->bit_pos = (int *)malloc((size_t)ct->n_total * sizeof(int));

    int t = 0;
    /* (4,2) */
    for (int ia = 0; ia < ct->nA4; ia++) {
        for (int ib = 0; ib < ct->nA2; ib++) {
            CritTuple *x = &ct->tuples[t];
            x->a_cnt = 4;
            x->a_comb_id = (uint16_t)ia;
            x->b_comb_id = (uint16_t)ib;
            uint32_t cm = 0;
            for (int r = 0; r < 4; r++) { x->a_idx[r] = ct->comb4[ia][r]; cm |= 1U << x->a_idx[r]; }
            for (int r = 0; r < 2; r++) { x->b_idx[r] = ct->comb2[ib][r]; cm |= 1U << (n + x->b_idx[r]); }
            x->col_mask = cm;
            ct->bit_pos[t] = ct->off_42 + (ia * ct->nA2 + ib);
            t++;
        }
    }
    /* (3,3) */
    for (int ia = 0; ia < ct->nA3; ia++) {
        for (int ib = 0; ib < ct->nA3; ib++) {
            CritTuple *x = &ct->tuples[t];
            x->a_cnt = 3;
            x->a_comb_id = (uint16_t)ia;
            x->b_comb_id = (uint16_t)ib;
            uint32_t cm = 0;
            for (int r = 0; r < 3; r++) { x->a_idx[r] = ct->comb3[ia][r]; cm |= 1U << x->a_idx[r]; }
            for (int r = 0; r < 3; r++) { x->b_idx[r] = ct->comb3[ib][r]; cm |= 1U << (n + x->b_idx[r]); }
            x->col_mask = cm;
            ct->bit_pos[t] = ct->off_33 + (ia * ct->nA3 + ib);
            t++;
        }
    }
    /* (2,4) */
    for (int ia = 0; ia < ct->nA2; ia++) {
        for (int ib = 0; ib < ct->nA4; ib++) {
            CritTuple *x = &ct->tuples[t];
            x->a_cnt = 2;
            x->a_comb_id = (uint16_t)ia;
            x->b_comb_id = (uint16_t)ib;
            uint32_t cm = 0;
            for (int r = 0; r < 2; r++) { x->a_idx[r] = ct->comb2[ia][r]; cm |= 1U << x->a_idx[r]; }
            for (int r = 0; r < 4; r++) { x->b_idx[r] = ct->comb4[ib][r]; cm |= 1U << (n + x->b_idx[r]); }
            x->col_mask = cm;
            ct->bit_pos[t] = ct->off_24 + (ia * ct->nA4 + ib);
            t++;
        }
    }

    /* Build Z_{q+1} shift orbits under (I, J) -> (I+1 mod n, J+1 mod n) */
    uint8_t *vis = (uint8_t *)calloc((size_t)ct->n_total, 1);
    ct->orb_rep = (int *)malloc((size_t)ct->n_total * sizeof(int));
    ct->orb_len = (int *)malloc((size_t)ct->n_total * sizeof(int));
    ct->orb_start = (int *)malloc((size_t)ct->n_total * sizeof(int));
    ct->orb_members = (int *)malloc((size_t)ct->n_total * sizeof(int));
    int mem_pos = 0;
    ct->n_orbits = 0;

    for (int i = 0; i < ct->n_total; i++) {
        if (vis[i]) continue;
        int oid = ct->n_orbits++;
        ct->orb_rep[oid] = i;
        ct->orb_start[oid] = mem_pos;
        int len = 0;
        const CritTuple *base = &ct->tuples[i];
        int a_cnt = base->a_cnt;
        int b_cnt = 6 - a_cnt;
        for (int sh = 0; sh < n; sh++) {
            int ma = 0, mb = 0;
            for (int r = 0; r < a_cnt; r++) ma |= 1 << ((base->a_idx[r] + sh) % n);
            for (int r = 0; r < b_cnt; r++) mb |= 1 << ((base->b_idx[r] + sh) % n);
            int ia = ct->mask2id[ma];
            int ib = ct->mask2id[mb];
            int tid;
            if (a_cnt == 4) tid = ia * ct->nA2 + ib;
            else if (a_cnt == 3) tid = ct->n_42 + ia * ct->nA3 + ib;
            else tid = ct->n_42 + ct->n_33 + ia * ct->nA4 + ib;
            if (!vis[tid]) {
                vis[tid] = 1;
                ct->orb_members[mem_pos++] = tid;
                len++;
            }
        }
        ct->orb_len[oid] = len;
    }
    free(vis);
}

/* Fast check of a single critical tuple using precomputed nullspace N_A */
static inline int check_tuple_nullspace(const FF *ff, const CritTable *ct, int tid,
                                        int is_row2, const uint8_t B[MAX_ORB][6]) {
    const CritTuple *x = &ct->tuples[tid];
    int ia = x->a_comb_id;
    if (x->a_cnt == 4) {
        const uint8_t (*N)[6] = is_row2 ? ct->N2_4[ia] : ct->N1_4[ia];
        uint8_t m[2][2];
        for (int r = 0; r < 2; r++) {
            const uint8_t *bv = B[x->b_idx[r]];
            for (int c = 0; c < 2; c++) {
                uint8_t acc = 0;
                for (int j = 0; j < 6; j++) acc = ff->add[acc][ff->mul[N[c][j]][bv[j]]];
                m[r][c] = acc;
            }
        }
        return det2_nonzero(ff, m);
    } else if (x->a_cnt == 3) {
        const uint8_t (*N)[6] = is_row2 ? ct->N2_3[ia] : ct->N1_3[ia];
        uint8_t m[3][3];
        for (int r = 0; r < 3; r++) {
            const uint8_t *bv = B[x->b_idx[r]];
            for (int c = 0; c < 3; c++) {
                uint8_t acc = 0;
                for (int j = 0; j < 6; j++) acc = ff->add[acc][ff->mul[N[c][j]][bv[j]]];
                m[r][c] = acc;
            }
        }
        return det3_nonzero(ff, m);
    } else {
        const uint8_t (*N)[6] = is_row2 ? ct->N2_2[ia] : ct->N1_2[ia];
        uint8_t m[4][4];
        for (int r = 0; r < 4; r++) {
            const uint8_t *bv = B[x->b_idx[r]];
            for (int c = 0; c < 4; c++) {
                uint8_t acc = 0;
                for (int j = 0; j < 6; j++) acc = ff->add[acc][ff->mul[N[c][j]][bv[j]]];
                m[r][c] = acc;
            }
        }
        return rank4_full(ff, m);
    }
}

/* Build dependent bitmask for a Z_{q+1}-invariant Row 1 (or Row 2 with m2=1) */
static int build_mask_cyclic(const FF *ff, const CritTable *ct, int is_row2,
                             const uint8_t B[MAX_ORB][6], uint64_t *mask) {
    memset(mask, 0, (size_t)ct->w_total * sizeof(uint64_t));
    int dep = 0;
    for (int oid = 0; oid < ct->n_orbits; oid++) {
        int rep = ct->orb_rep[oid];
        if (!check_tuple_nullspace(ff, ct, rep, is_row2, B)) {
            int st = ct->orb_start[oid];
            int len = ct->orb_len[oid];
            dep += len;
            for (int j = 0; j < len; j++) {
                int bp = ct->bit_pos[ct->orb_members[st + j]];
                mask[bp >> 6] |= 1ULL << (bp & 63);
            }
        }
    }
    return dep;
}

/* Permute Orbit-B indices of a bitmask: new_B[k] = old_B[perm[k]] */
static void permute_mask_B(const CritTable *ct, const uint64_t *src,
                           const uint8_t perm[MAX_ORB], uint64_t *dst) {
    memset(dst, 0, (size_t)ct->w_total * sizeof(uint64_t));
    /* Map each B combination under perm */
    int map2[45], map3[120], map4[210];
    for (int ib = 0; ib < ct->nA2; ib++) {
        int m = (1 << perm[ct->comb2[ib][0]]) | (1 << perm[ct->comb2[ib][1]]);
        map2[ib] = ct->mask2id[m];
    }
    for (int ib = 0; ib < ct->nA3; ib++) {
        int m = (1 << perm[ct->comb3[ib][0]]) | (1 << perm[ct->comb3[ib][1]]) | (1 << perm[ct->comb3[ib][2]]);
        map3[ib] = ct->mask2id[m];
    }
    for (int ib = 0; ib < ct->nA4; ib++) {
        int m = (1 << perm[ct->comb4[ib][0]]) | (1 << perm[ct->comb4[ib][1]]) |
                (1 << perm[ct->comb4[ib][2]]) | (1 << perm[ct->comb4[ib][3]]);
        map4[ib] = ct->mask2id[m];
    }
    /* For each tuple t in dst, check src at (ia, map(ib)) */
    int nA2 = ct->nA2, nA3 = ct->nA3, nA4 = ct->nA4;
    for (int ia = 0; ia < nA4; ia++) {
        int base = ct->off_42 + ia * nA2;
        for (int ib = 0; ib < nA2; ib++) {
            int sbp = base + map2[ib];
            if ((src[sbp >> 6] >> (sbp & 63)) & 1ULL) {
                int dbp = base + ib;
                dst[dbp >> 6] |= 1ULL << (dbp & 63);
            }
        }
    }
    for (int ia = 0; ia < nA3; ia++) {
        int base = ct->off_33 + ia * nA3;
        for (int ib = 0; ib < nA3; ib++) {
            int sbp = base + map3[ib];
            if ((src[sbp >> 6] >> (sbp & 63)) & 1ULL) {
                int dbp = base + ib;
                dst[dbp >> 6] |= 1ULL << (dbp & 63);
            }
        }
    }
    for (int ia = 0; ia < nA2; ia++) {
        int base = ct->off_24 + ia * nA4;
        for (int ib = 0; ib < nA4; ib++) {
            int sbp = base + map4[ib];
            if ((src[sbp >> 6] >> (sbp & 63)) & 1ULL) {
                int dbp = base + ib;
                dst[dbp >> 6] |= 1ULL << (dbp & 63);
            }
        }
    }
}

/* ---------- Exact Minimum Hitting Set (k_punc) ---------- */
typedef struct {
    int n_edges;
    int k_cols;
    uint32_t edges[MAX_CRIT];
    int best_del;
    uint32_t best_del_mask;
} HitState;

static void hit_dfs(HitState *hs, uint32_t chosen, int depth, int first_unc) {
    if (depth >= hs->best_del) return;
    /* Find first uncovered edge */
    int u = -1;
    for (int i = first_unc; i < hs->n_edges; i++) {
        if ((hs->edges[i] & chosen) == 0) { u = i; break; }
    }
    if (u < 0) {
        hs->best_del = depth;
        hs->best_del_mask = chosen;
        return;
    }
    if (depth + 1 >= hs->best_del) return;

    /* Order the 6 vertices in edge u by their degree in remaining uncovered edges */
    uint32_t e = hs->edges[u];
    int verts[6], deg[6], nv = 0;
    for (int v = 0; v < hs->k_cols; v++) {
        if ((e >> v) & 1U) {
            verts[nv] = v;
            deg[nv] = 0;
            nv++;
        }
    }
    for (int i = u; i < hs->n_edges; i++) {
        if ((hs->edges[i] & chosen) == 0) {
            uint32_t ei = hs->edges[i];
            for (int j = 0; j < nv; j++) {
                if ((ei >> verts[j]) & 1U) deg[j]++;
            }
        }
    }
    /* Sort verts by descending deg */
    for (int i = 0; i < nv; i++) {
        for (int j = i + 1; j < nv; j++) {
            if (deg[j] > deg[i]) {
                int tv = verts[i]; verts[i] = verts[j]; verts[j] = tv;
                int td = deg[i]; deg[i] = deg[j]; deg[j] = td;
            }
        }
    }
    /* Also check lower bound: max degree * remaining_slots >= num_uncovered */
    int rem_unc = 0;
    for (int i = u; i < hs->n_edges; i++) {
        if ((hs->edges[i] & chosen) == 0) rem_unc++;
    }
    int max_deg = 0;
    for (int v = 0; v < hs->k_cols; v++) {
        if ((chosen >> v) & 1U) continue;
        int d = 0;
        for (int i = u; i < hs->n_edges; i++) {
            if ((hs->edges[i] & chosen) == 0 && ((hs->edges[i] >> v) & 1U)) d++;
        }
        if (d > max_deg) max_deg = d;
    }
    if (max_deg > 0 && depth + (rem_unc + max_deg - 1) / max_deg >= hs->best_del) return;

    for (int j = 0; j < nv; j++) {
        hit_dfs(hs, chosen | (1U << verts[j]), depth + 1, u + 1);
    }
}

static int compute_exact_kpunc(const CritTable *ct, const uint64_t *m1, const uint64_t *m2,
                               uint32_t *out_del_mask) {
    HitState hs;
    hs.n_edges = 0;
    hs.k_cols = 2 * ct->n_orb;
    for (int t = 0; t < ct->n_total; t++) {
        int bp = ct->bit_pos[t];
        if (((m1[bp >> 6] & m2[bp >> 6]) >> (bp & 63)) & 1ULL) {
            hs.edges[hs.n_edges++] = ct->tuples[t].col_mask;
        }
    }
    if (hs.n_edges == 0) {
        if (out_del_mask) *out_del_mask = 0;
        return hs.k_cols;
    }
    /* Greedy upper bound first */
    uint32_t gmask = 0;
    int gdel = 0;
    while (1) {
        int best_v = -1, best_d = 0;
        for (int v = 0; v < hs.k_cols; v++) {
            if ((gmask >> v) & 1U) continue;
            int d = 0;
            for (int i = 0; i < hs.n_edges; i++) {
                if ((hs.edges[i] & gmask) == 0 && ((hs.edges[i] >> v) & 1U)) d++;
            }
            if (d > best_d) { best_d = d; best_v = v; }
        }
        if (best_d == 0) break;
        gmask |= 1U << best_v;
        gdel++;
    }
    hs.best_del = gdel;
    hs.best_del_mask = gmask;
    hit_dfs(&hs, 0, 0, 0);
    if (out_del_mask) *out_del_mask = hs.best_del_mask;
    return hs.k_cols - hs.best_del;
}

/* ---------- Save CPHF JSON ---------- */
static void save_cphf_json(const char *path, int q, int kA, int kB,
                           const uint8_t R1[][6], const uint8_t R2[][6],
                           const char *meta_json) {
    FILE *fp = fopen(path, "w");
    if (!fp) {
        perror("fopen save_cphf_json");
        return;
    }
    int k = kA + kB;
    fprintf(fp, "{\n  \"q\": %d,\n  \"k\": %d,\n  \"n_orbit_a\": %d,\n  \"meta\": %s,\n  \"R1\": [\n",
            q, k, kA, meta_json ? meta_json : "{}");
    for (int i = 0; i < k; i++) {
        fprintf(fp, "    [%d, %d, %d, %d, %d, %d]%s\n",
                R1[i][0], R1[i][1], R1[i][2], R1[i][3], R1[i][4], R1[i][5],
                (i + 1 < k) ? "," : "");
    }
    fprintf(fp, "  ],\n  \"R2\": [\n");
    for (int i = 0; i < k; i++) {
        fprintf(fp, "    [%d, %d, %d, %d, %d, %d]%s\n",
                R2[i][0], R2[i][1], R2[i][2], R2[i][3], R2[i][4], R2[i][5],
                (i + 1 < k) ? "," : "");
    }
    fprintf(fp, "  ]\n}\n");
    fclose(fp);
}

/* ---------- STAGE 1: Exhaustive Parametric Scan ---------- */
typedef struct {
    int i1, i2;
    int both_tot, b42, b33, b24;
} TopEntry;

typedef struct {
    int tid;
    int n_threads;
    int n1, n2;
    int w_42_end, w_33_end, w_total;
    const uint64_t *masks1;
    const uint64_t *masks2;
    int min_tot, min_42, min_33, min_24;
    int best_i1, best_i2, best_b42, best_b33, best_b24;
    int best42_i1, best42_i2;
    int best33_i1, best33_i2;
    int best24_i1, best24_i2;
    TopEntry top[256];
    int n_top;
    double deadline;
    int timed_out;
    uint64_t pairs_checked;
    uint64_t zero_count;
} Stage1Worker;

static void top_insert(Stage1Worker *w, int i1, int i2, int tot, int b42, int b33, int b24) {
    const int CAP = 200;
    if (w->n_top < CAP) {
        w->top[w->n_top++] = (TopEntry){i1, i2, tot, b42, b33, b24};
        if (w->n_top == CAP) {
            /* Sort ascending */
            for (int a = 0; a < CAP; a++)
                for (int b = a + 1; b < CAP; b++)
                    if (w->top[b].both_tot < w->top[a].both_tot) {
                        TopEntry tmp = w->top[a]; w->top[a] = w->top[b]; w->top[b] = tmp;
                    }
        }
    } else if (tot < w->top[CAP - 1].both_tot) {
        int pos = CAP - 1;
        while (pos > 0 && tot < w->top[pos - 1].both_tot) {
            w->top[pos] = w->top[pos - 1];
            pos--;
        }
        w->top[pos] = (TopEntry){i1, i2, tot, b42, b33, b24};
    }
}

static void *stage1_thread(void *arg) {
    Stage1Worker *w = (Stage1Worker *)arg;
    int w42 = w->w_42_end;
    int w33 = w->w_33_end;
    int wtot = w->w_total;
    w->min_tot = w->min_42 = w->min_33 = w->min_24 = 1000000000;
    w->n_top = 0;
    w->pairs_checked = 0;
    w->zero_count = 0;
    w->timed_out = 0;

    for (int i1 = w->tid; i1 < w->n1; i1 += w->n_threads) {
        if ((i1 & 31) == 0 && now_sec() > w->deadline) {
            w->timed_out = 1;
            break;
        }
        const uint64_t *m1 = w->masks1 + (size_t)i1 * wtot;
        for (int i2 = 0; i2 < w->n2; i2++) {
            const uint64_t *m2 = w->masks2 + (size_t)i2 * wtot;
            int b42 = 0, b33 = 0, b24 = 0;
            for (int k = 0; k < w42; k++) b42 += __builtin_popcountll(m1[k] & m2[k]);
            for (int k = w42; k < w33; k++) b33 += __builtin_popcountll(m1[k] & m2[k]);
            for (int k = w33; k < wtot; k++) b24 += __builtin_popcountll(m1[k] & m2[k]);
            int tot = b42 + b33 + b24;
            w->pairs_checked++;
            if (tot == 0) w->zero_count++;
            if (b42 < w->min_42) { w->min_42 = b42; w->best42_i1 = i1; w->best42_i2 = i2; }
            if (b33 < w->min_33) { w->min_33 = b33; w->best33_i1 = i1; w->best33_i2 = i2; }
            if (b24 < w->min_24) { w->min_24 = b24; w->best24_i1 = i1; w->best24_i2 = i2; }
            if (tot < w->min_tot) {
                w->min_tot = tot;
                w->best_i1 = i1; w->best_i2 = i2;
                w->best_b42 = b42; w->best_b33 = b33; w->best_b24 = b24;
            }
            if (w->n_top < 200 || tot < w->top[199].both_tot) {
                top_insert(w, i1, i2, tot, b42, b33, b24);
            }
        }
    }
    return NULL;
}

typedef struct {
    KElem g1, g2;
    int dep;
} R1Config;

typedef struct {
    KElem alpha, beta;
    int m2;
    int dep;
} R2Config;

static void run_stage1(int q, const char *out_dir, double timeout_sec, int n_threads) {
    double t0 = now_sec();
    double deadline = t0 + timeout_sec;
    FF ff;
    ff_init(&ff, q);

    uint8_t R1_A[MAX_ORB][6], R2_A[MAX_ORB][6];
    build_R1_base(&ff, R1_A);
    build_R2_base(&ff, R2_A);

    CritTable ct;
    init_crit_table(&ct, &ff, R1_A, R2_A);

    /* Build all Row 1 configs: (g1, g2) in (K*)^2 with g3 = 1 */
    int n_k = ff.k_order;
    int n1 = n_k * n_k;
    R1Config *r1_cfgs = (R1Config *)malloc((size_t)n1 * sizeof(R1Config));
    uint64_t *masks1 = (uint64_t *)malloc((size_t)n1 * ct.w_total * sizeof(uint64_t));

    int min_dep1 = 1000000000;
    int idx1 = 0;
    for (int i = 0; i < n_k; i++) {
        for (int j = 0; j < n_k; j++) {
            uint8_t R1_B[MAX_ORB][6];
            build_R1_B_param(&ff, ff.k_nonzero[i], ff.k_nonzero[j], (KElem){1, 0}, 1, 0, 0, R1_B);
            int dep = build_mask_cyclic(&ff, &ct, 0, R1_B, masks1 + (size_t)idx1 * ct.w_total);
            r1_cfgs[idx1] = (R1Config){ff.k_nonzero[i], ff.k_nonzero[j], dep};
            if (dep < min_dep1) min_dep1 = dep;
            idx1++;
        }
    }
    double t_r1 = now_sec() - t0;

    /* Build all Row 2 configs: (alpha, beta) mod F_q^* x all coprime m2 */
    /* Canonical representative mod F_q^*: alpha in {zeta^0 .. zeta^q} (q+1 cosets of F_q^* in K*), beta in K* */
    int coprimes[MAX_ORB], n_cop = 0;
    for (int m = 1; m < ff.n_orb; m++) {
        if (gcd_int(m, ff.n_orb) == 1) coprimes[n_cop++] = m;
    }
    int n2_base = ff.n_orb * n_k;
    int n2 = n2_base * n_cop;
    R2Config *r2_cfgs = (R2Config *)malloc((size_t)n2 * sizeof(R2Config));
    uint64_t *masks2 = (uint64_t *)malloc((size_t)n2 * ct.w_total * sizeof(uint64_t));

    int min_dep2 = 1000000000;
    int idx2 = 0;
    for (int ia = 0; ia < ff.n_orb; ia++) {
        KElem alpha = ff.zeta_pow[ia];
        for (int ib = 0; ib < n_k; ib++) {
            KElem beta = ff.k_nonzero[ib];
            uint8_t R2_B[MAX_ORB][6];
            build_R2_B_param(&ff, alpha, beta, 1, 0, R2_B);
            uint64_t base_mask[MAX_WORDS];
            int dep = build_mask_cyclic(&ff, &ct, 1, R2_B, base_mask);
            if (dep < min_dep2) min_dep2 = dep;
            for (int cm = 0; cm < n_cop; cm++) {
                int m2 = coprimes[cm];
                uint64_t *dst = masks2 + (size_t)idx2 * ct.w_total;
                if (m2 == 1) {
                    memcpy(dst, base_mask, (size_t)ct.w_total * sizeof(uint64_t));
                } else {
                    uint8_t perm[MAX_ORB];
                    for (int k = 0; k < ff.n_orb; k++) perm[k] = (uint8_t)((m2 * k) % ff.n_orb);
                    permute_mask_B(&ct, base_mask, perm, dst);
                }
                r2_cfgs[idx2] = (R2Config){alpha, beta, m2, dep};
                idx2++;
            }
        }
    }
    double t_r2 = now_sec() - t0 - t_r1;

    /* Parallel scan */
    if (n_threads < 1) n_threads = 1;
    if (n_threads > 8) n_threads = 8;
    Stage1Worker workers[8];
    pthread_t th[8];
    for (int t = 0; t < n_threads; t++) {
        workers[t].tid = t;
        workers[t].n_threads = n_threads;
        workers[t].n1 = n1;
        workers[t].n2 = n2;
        workers[t].w_42_end = ct.w_42_end;
        workers[t].w_33_end = ct.w_33_end;
        workers[t].w_total = ct.w_total;
        workers[t].masks1 = masks1;
        workers[t].masks2 = masks2;
        workers[t].deadline = deadline;
        pthread_create(&th[t], NULL, stage1_thread, &workers[t]);
    }
    for (int t = 0; t < n_threads; t++) pthread_join(th[t], NULL);

    int min_tot = 1000000000, min_42 = 1000000000, min_33 = 1000000000, min_24 = 1000000000;
    int bi1 = 0, bi2 = 0, bb42 = 0, bb33 = 0, bb24 = 0;
    uint64_t total_pairs = 0, total_zeros = 0;
    int timed_out = 0;

    TopEntry merged[2000];
    int n_merged = 0;
    for (int t = 0; t < n_threads; t++) {
        total_pairs += workers[t].pairs_checked;
        total_zeros += workers[t].zero_count;
        timed_out |= workers[t].timed_out;
        if (workers[t].min_42 < min_42) min_42 = workers[t].min_42;
        if (workers[t].min_33 < min_33) min_33 = workers[t].min_33;
        if (workers[t].min_24 < min_24) min_24 = workers[t].min_24;
        if (workers[t].min_tot < min_tot) {
            min_tot = workers[t].min_tot;
            bi1 = workers[t].best_i1; bi2 = workers[t].best_i2;
            bb42 = workers[t].best_b42; bb33 = workers[t].best_b33; bb24 = workers[t].best_b24;
        }
        for (int j = 0; j < workers[t].n_top; j++) merged[n_merged++] = workers[t].top[j];
    }
    /* Sort merged ascending by both_tot */
    for (int a = 0; a < n_merged; a++) {
        for (int b = a + 1; b < n_merged; b++) {
            if (merged[b].both_tot < merged[a].both_tot) {
                TopEntry tmp = merged[a]; merged[a] = merged[b]; merged[b] = tmp;
            }
        }
    }

    /* Compute exact k_punc on top 150 merged candidates */
    int best_kpunc = 0;
    uint32_t best_del_mask = 0;
    int kp_i1 = bi1, kp_i2 = bi2, kp_both = min_tot;
    int eval_limit = n_merged < 150 ? n_merged : 150;
    for (int i = 0; i < eval_limit; i++) {
        if (now_sec() > deadline) break;
        uint32_t dmask = 0;
        int kp = compute_exact_kpunc(&ct,
            masks1 + (size_t)merged[i].i1 * ct.w_total,
            masks2 + (size_t)merged[i].i2 * ct.w_total, &dmask);
        if (kp > best_kpunc) {
            best_kpunc = kp;
            best_del_mask = dmask;
            kp_i1 = merged[i].i1;
            kp_i2 = merged[i].i2;
            kp_both = merged[i].both_tot;
        }
    }

    double t_tot = now_sec() - t0;
    printf("STAGE1 q=%d (k=%d, crit=%d, orbits=%d): status=%s\n",
           q, ff.k_full, ct.n_total, ct.n_orbits, timed_out ? "TIMEOUT" : "EXHAUSTIVE");
    printf("  n1=%d (build %.3fs, min_dep1=%d), n2=%d (build %.3fs, min_dep2=%d)\n",
           n1, t_r1, min_dep1, n2, t_r2, min_dep2);
    printf("  pairs_checked=%llu / %llu in %.3fs (%.2fM pairs/s), zero_hits=%llu\n",
           (unsigned long long)total_pairs, (unsigned long long)n1 * n2,
           t_tot, (double)total_pairs / (t_tot * 1e6), (unsigned long long)total_zeros);
    printf("  global min_both=%d (splits 42=%d, 33=%d, 24=%d) at g1=(%d,%d) g2=(%d,%d) alpha=(%d,%d) beta=(%d,%d) m2=%d\n",
           min_tot, bb42, bb33, bb24,
           r1_cfgs[bi1].g1.a, r1_cfgs[bi1].g1.b, r1_cfgs[bi1].g2.a, r1_cfgs[bi1].g2.b,
           r2_cfgs[bi2].alpha.a, r2_cfgs[bi2].alpha.b, r2_cfgs[bi2].beta.a, r2_cfgs[bi2].beta.b,
           r2_cfgs[bi2].m2);
    printf("  independent split minima: min_42=%d, min_33=%d, min_24=%d\n", min_42, min_33, min_24);
    printf("  best k_punc=%d / %d (from both=%d, del_mask=0x%x) at g1=(%d,%d) g2=(%d,%d) alpha=(%d,%d) beta=(%d,%d) m2=%d\n",
           best_kpunc, ff.k_full, kp_both, best_del_mask,
           r1_cfgs[kp_i1].g1.a, r1_cfgs[kp_i1].g1.b, r1_cfgs[kp_i1].g2.a, r1_cfgs[kp_i1].g2.b,
           r2_cfgs[kp_i2].alpha.a, r2_cfgs[kp_i2].alpha.b, r2_cfgs[kp_i2].beta.a, r2_cfgs[kp_i2].beta.b,
           r2_cfgs[kp_i2].m2);

    /* Full verification and save if min_tot == 0 or best_kpunc > N_q(1) */
    int nq1 = (q == 5) ? 10 : (q == 7) ? 13 : (q == 8) ? 14 : 16;
    if (out_dir && (min_tot == 0 || best_kpunc > nq1)) {
        int si1 = (min_tot == 0) ? bi1 : kp_i1;
        int si2 = (min_tot == 0) ? bi2 : kp_i2;
        uint32_t dmask = (min_tot == 0) ? 0 : best_del_mask;
        uint8_t R1_B[MAX_ORB][6], R2_B[MAX_ORB][6];
        build_R1_B_param(&ff, r1_cfgs[si1].g1, r1_cfgs[si1].g2, (KElem){1, 0}, 1, 0, 0, R1_B);
        build_R2_B_param(&ff, r2_cfgs[si2].alpha, r2_cfgs[si2].beta, r2_cfgs[si2].m2, 0, R2_B);
        uint8_t R1_out[MAX_K][6], R2_out[MAX_K][6];
        int kA = 0, kB = 0;
        for (int c = 0; c < ff.n_orb; c++) {
            if (!((dmask >> c) & 1U)) {
                memcpy(R1_out[kA], R1_A[c], 6);
                memcpy(R2_out[kA], R2_A[c], 6);
                kA++;
            }
        }
        for (int c = 0; c < ff.n_orb; c++) {
            if (!((dmask >> (ff.n_orb + c)) & 1U)) {
                memcpy(R1_out[kA + kB], R1_B[c], 6);
                memcpy(R2_out[kA + kB], R2_B[c], 6);
                kB++;
            }
        }
        int d1[7], d2[7], bt[7];
        full_check_matrices(&ff, kA, kB, R1_out, R2_out, d1, d2, bt);
        int unc = 0;
        for (int a = 0; a <= 6; a++) unc += bt[a];
        printf("  FULL C VERIFY (k=%d, kA=%d, kB=%d): unc=%d\n", kA + kB, kA, kB, unc);
        if (unc == 0) {
            char fname[512], meta[512];
            snprintf(fname, sizeof(fname), "%s/cphf_q%d_k%d_stage1.json", out_dir, q, kA + kB);
            snprintf(meta, sizeof(meta),
                     "{\"stage\":\"stage1\",\"g1\":[%d,%d],\"g2\":[%d,%d],\"alpha\":[%d,%d],\"beta\":[%d,%d],\"m2\":%d,\"del_mask\":%u}",
                     r1_cfgs[si1].g1.a, r1_cfgs[si1].g1.b, r1_cfgs[si1].g2.a, r1_cfgs[si1].g2.b,
                     r2_cfgs[si2].alpha.a, r2_cfgs[si2].alpha.b, r2_cfgs[si2].beta.a, r2_cfgs[si2].beta.b,
                     r2_cfgs[si2].m2, dmask);
            save_cphf_json(fname, q, kA, kB, R1_out, R2_out, meta);
            printf("  SAVED HIT -> %s\n", fname);
        }
    }

    free(r1_cfgs); free(masks1); free(r2_cfgs); free(masks2);
    free(ct.tuples); free(ct.bit_pos); free(ct.orb_rep); free(ct.orb_len); free(ct.orb_start); free(ct.orb_members);
}

/* ---------- STAGE 2 & STAGE 3: Symmetry Breaking (pi, G in GL(6,q), M in GL(4,q)) ---------- */

static void apply_G_to_B(const FF *ff, int n, const uint8_t G[6][6],
                         const uint8_t B0[MAX_ORB][6], uint8_t B[MAX_ORB][6]) {
    for (int k = 0; k < n; k++) {
        for (int r = 0; r < 6; r++) {
            uint8_t acc = 0;
            for (int c = 0; c < 6; c++) acc = ff->add[acc][ff->mul[G[r][c]][B0[k][c]]];
            B[k][r] = acc;
        }
    }
}

static void apply_M_pi_to_B2(const FF *ff, int n, const uint8_t M[4][4], const uint8_t pi[MAX_ORB],
                             const uint8_t B0[MAX_ORB][6], uint8_t B[MAX_ORB][6]) {
    for (int k = 0; k < n; k++) {
        int idx = pi[k];
        for (int r = 0; r < 4; r++) {
            uint8_t acc = 0;
            for (int c = 0; c < 4; c++) acc = ff->add[acc][ff->mul[M[r][c]][B0[idx][c]]];
            B[k][r] = acc;
        }
        B[k][4] = 0;
        B[k][5] = 1;
    }
}

static void random_GL(const FF *ff, Rng *rng, int dim, uint8_t *G) {
    /* Start from identity and apply 4*dim random elementary operations + row scales */
    memset(G, 0, (size_t)dim * dim);
    for (int i = 0; i < dim; i++) G[i * dim + i] = (uint8_t)(1 + rng_int(rng, (uint32_t)(ff->q - 1)));
    for (int step = 0; step < 5 * dim; step++) {
        int r1 = (int)rng_int(rng, (uint32_t)dim);
        int r2 = (int)rng_int(rng, (uint32_t)(dim - 1));
        if (r2 >= r1) r2++;
        uint8_t c = (uint8_t)(1 + rng_int(rng, (uint32_t)(ff->q - 1)));
        for (int j = 0; j < dim; j++) {
            G[r1 * dim + j] = ff->add[G[r1 * dim + j]][ff->mul[c][G[r2 * dim + j]]];
        }
    }
}

static void perturb_GL(const FF *ff, Rng *rng, int dim, const uint8_t *src, uint8_t *dst) {
    memcpy(dst, src, (size_t)dim * dim);
    uint32_t move = rng_int(rng, 10);
    if (move < 5) {
        /* Left elementary row op: row[r1] += c * row[r2] */
        int r1 = (int)rng_int(rng, (uint32_t)dim);
        int r2 = (int)rng_int(rng, (uint32_t)(dim - 1));
        if (r2 >= r1) r2++;
        uint8_t c = (uint8_t)(1 + rng_int(rng, (uint32_t)(ff->q - 1)));
        for (int j = 0; j < dim; j++) {
            dst[r1 * dim + j] = ff->add[dst[r1 * dim + j]][ff->mul[c][dst[r2 * dim + j]]];
        }
    } else if (move < 9) {
        /* Right elementary col op: col[c1] += c * col[c2] */
        int c1 = (int)rng_int(rng, (uint32_t)dim);
        int c2 = (int)rng_int(rng, (uint32_t)(dim - 1));
        if (c2 >= c1) c2++;
        uint8_t c = (uint8_t)(1 + rng_int(rng, (uint32_t)(ff->q - 1)));
        for (int i = 0; i < dim; i++) {
            dst[i * dim + c1] = ff->add[dst[i * dim + c1]][ff->mul[c][dst[i * dim + c2]]];
        }
    } else {
        /* Scale a row */
        int r1 = (int)rng_int(rng, (uint32_t)dim);
        uint8_t c = (uint8_t)(1 + rng_int(rng, (uint32_t)(ff->q - 1)));
        for (int j = 0; j < dim; j++) dst[r1 * dim + j] = ff->mul[c][dst[r1 * dim + j]];
    }
}

/* Evaluate how many tuples in target_list are dependent in Row 1 (is_row2=0) or Row 2 (is_row2=1) */
static int eval_on_list(const FF *ff, const CritTable *ct, int is_row2,
                        const uint8_t B[MAX_ORB][6], const int *tlist, int n_list,
                        int *o42, int *o33, int *o24) {
    int c42 = 0, c33 = 0, c24 = 0;
    for (int i = 0; i < n_list; i++) {
        int tid = tlist[i];
        if (!check_tuple_nullspace(ff, ct, tid, is_row2, B)) {
            int ac = ct->tuples[tid].a_cnt;
            if (ac == 4) c42++;
            else if (ac == 3) c33++;
            else c24++;
        }
    }
    if (o42) *o42 = c42;
    if (o33) *o33 = c33;
    if (o24) *o24 = c24;
    return c42 + c33 + c24;
}

/* Build full dependent list (and mask) for arbitrary (non-cyclic) B */
static int build_list_general(const FF *ff, const CritTable *ct, int is_row2,
                              const uint8_t B[MAX_ORB][6], uint32_t active_col_mask,
                              int *out_list, uint64_t *out_mask) {
    if (out_mask) memset(out_mask, 0, (size_t)ct->w_total * sizeof(uint64_t));
    int cnt = 0;
    for (int tid = 0; tid < ct->n_total; tid++) {
        if ((ct->tuples[tid].col_mask & active_col_mask) != ct->tuples[tid].col_mask) continue;
        if (!check_tuple_nullspace(ff, ct, tid, is_row2, B)) {
            if (out_list) out_list[cnt] = tid;
            if (out_mask) {
                int bp = ct->bit_pos[tid];
                out_mask[bp >> 6] |= 1ULL << (bp & 63);
            }
            cnt++;
        }
    }
    return cnt;
}

/* Exhaustive permutation test on S_{n} / Z_{n} (fixing pi[0] = 0 for cyclic R1/R2) */
static int next_perm(uint8_t *a, int n) {
    int i = n - 2;
    while (i >= 0 && a[i] >= a[i + 1]) i--;
    if (i < 0) return 0;
    int j = n - 1;
    while (a[j] <= a[i]) j--;
    uint8_t t = a[i]; a[i] = a[j]; a[j] = t;
    for (int l = i + 1, r = n - 1; l < r; l++, r--) {
        t = a[l]; a[l] = a[r]; a[r] = t;
    }
    return 1;
}

/* Fast count of D1 & perm(D2) using pre-extracted list of D1 tuples */
static int count_perm_intersection(const CritTable *ct, const int *d1_list, int n_d1,
                                   const uint64_t *m2, const uint8_t pi[MAX_ORB],
                                   int *o42, int *o33, int *o24) {
    int c42 = 0, c33 = 0, c24 = 0;
    int nA2 = ct->nA2, nA3 = ct->nA3, nA4 = ct->nA4;
    for (int i = 0; i < n_d1; i++) {
        const CritTuple *x = &ct->tuples[d1_list[i]];
        int mb = 0;
        int b_cnt = 6 - x->a_cnt;
        for (int r = 0; r < b_cnt; r++) mb |= 1 << pi[x->b_idx[r]];
        int ib = ct->mask2id[mb];
        int bp;
        if (x->a_cnt == 4) bp = ct->off_42 + x->a_comb_id * nA2 + ib;
        else if (x->a_cnt == 3) bp = ct->off_33 + x->a_comb_id * nA3 + ib;
        else bp = ct->off_24 + x->a_comb_id * nA4 + ib;
        if ((m2[bp >> 6] >> (bp & 63)) & 1ULL) {
            if (x->a_cnt == 4) c42++;
            else if (x->a_cnt == 3) c33++;
            else c24++;
        }
    }
    if (o42) *o42 = c42;
    if (o33) *o33 = c33;
    if (o24) *o24 = c24;
    return c42 + c33 + c24;
}

static void set_k_block2(const FF *ff, KElem g, uint8_t *mat, int dim, int offset) {
    mat[(offset + 0) * dim + (offset + 0)] = g.a;
    mat[(offset + 0) * dim + (offset + 1)] = ff->mul[ff->p0][g.b];
    mat[(offset + 1) * dim + (offset + 0)] = g.b;
    mat[(offset + 1) * dim + (offset + 1)] = ff->add[g.a][ff->mul[ff->p1][g.b]];
}

static void run_stage2(int q, const char *out_dir, double timeout_sec, uint64_t seed,
                       int has_warm, KElem wg1, KElem wg2, KElem walpha, KElem wbeta, int wm2) {
    double t0 = now_sec();
    double deadline = t0 + timeout_sec;
    FF ff;
    ff_init(&ff, q);
    Rng rng;
    rng_seed(&rng, seed);

    uint8_t R1_A[MAX_ORB][6], R2_A[MAX_ORB][6];
    build_R1_base(&ff, R1_A);
    build_R2_base(&ff, R2_A);

    CritTable ct;
    init_crit_table(&ct, &ff, R1_A, R2_A);

    uint8_t R1_B0[MAX_ORB][6], R2_B0[MAX_ORB][6];
    build_R1_B_param(&ff, (KElem){1, 0}, (KElem){1, 0}, (KElem){1, 0}, 1, 0, 0, R1_B0);
    build_R2_B_param(&ff, (KElem){1, 0}, (KElem){1, 0}, 1, 0, R2_B0);

    /* Find the strongest Row 2 (minimal |D2|) and top-16 diverse Row 2s + top Row 1s */
    int n_k = ff.k_order;
    int best_dep2 = 1000000000;
    uint64_t best_m2[MAX_WORDS];

    typedef struct { KElem a, b; int dep; uint64_t mask[MAX_WORDS]; } StrongR2;
    StrongR2 top_r2[16];
    int n_top_r2 = 0;
    for (int ia = 0; ia < ff.n_orb; ia++) {
        KElem alpha = ff.zeta_pow[ia];
        for (int ib = 0; ib < n_k; ib++) {
            KElem beta = ff.k_nonzero[ib];
            uint8_t B2[MAX_ORB][6];
            build_R2_B_param(&ff, alpha, beta, 1, 0, B2);
            uint64_t m[MAX_WORDS];
            int dep = build_mask_cyclic(&ff, &ct, 1, B2, m);
            if (dep < best_dep2) {
                best_dep2 = dep;
                memcpy(best_m2, m, (size_t)ct.w_total * sizeof(uint64_t));
            }
            if (n_top_r2 < 16 || dep < top_r2[15].dep) {
                int pos = (n_top_r2 < 16) ? n_top_r2++ : 15;
                top_r2[pos].a = alpha; top_r2[pos].b = beta; top_r2[pos].dep = dep;
                memcpy(top_r2[pos].mask, m, (size_t)ct.w_total * sizeof(uint64_t));
                while (pos > 0 && top_r2[pos].dep < top_r2[pos - 1].dep) {
                    StrongR2 tmp = top_r2[pos]; top_r2[pos] = top_r2[pos - 1]; top_r2[pos - 1] = tmp;
                    pos--;
                }
            }
        }
    }

    typedef struct { KElem g1, g2; int dep; uint64_t mask[MAX_WORDS]; } StrongR1;
    StrongR1 top_r1[16];
    int n_top_r1 = 0;
    for (int i = 0; i < n_k; i++) {
        for (int j = 0; j < n_k; j++) {
            uint8_t B1[MAX_ORB][6];
            build_R1_B_param(&ff, ff.k_nonzero[i], ff.k_nonzero[j], (KElem){1, 0}, 1, 0, 0, B1);
            uint64_t m[MAX_WORDS];
            int dep = build_mask_cyclic(&ff, &ct, 0, B1, m);
            if (n_top_r1 < 16 || dep < top_r1[15].dep) {
                int pos = (n_top_r1 < 16) ? n_top_r1++ : 15;
                top_r1[pos].g1 = ff.k_nonzero[i]; top_r1[pos].g2 = ff.k_nonzero[j]; top_r1[pos].dep = dep;
                memcpy(top_r1[pos].mask, m, (size_t)ct.w_total * sizeof(uint64_t));
                while (pos > 0 && top_r1[pos].dep < top_r1[pos - 1].dep) {
                    StrongR1 tmp = top_r1[pos]; top_r1[pos] = top_r1[pos - 1]; top_r1[pos - 1] = tmp;
                    pos--;
                }
            }
        }
    }

    /* Warm-start matrices if provided */
    uint8_t warm_G[6][6], warm_M[4][4], warm_pi[MAX_ORB];
    uint64_t warm_m1[MAX_WORDS], warm_m2[MAX_WORDS];
    int warm_both = 1000000000, wb42 = 0, wb33 = 0, wb24 = 0;
    uint32_t all_cols = (1U << ff.k_full) - 1U;
    if (has_warm) {
        memset(warm_G, 0, sizeof(warm_G));
        set_k_block2(&ff, wg1, &warm_G[0][0], 6, 0);
        set_k_block2(&ff, wg2, &warm_G[0][0], 6, 2);
        set_k_block2(&ff, (KElem){1, 0}, &warm_G[0][0], 6, 4);

        memset(warm_M, 0, sizeof(warm_M));
        set_k_block2(&ff, walpha, &warm_M[0][0], 4, 0);
        set_k_block2(&ff, wbeta, &warm_M[0][0], 4, 2);
        for (int k = 0; k < ff.n_orb; k++) warm_pi[k] = (uint8_t)((wm2 * k) % ff.n_orb);

        uint8_t wB1[MAX_ORB][6], wB2[MAX_ORB][6];
        apply_G_to_B(&ff, ff.n_orb, warm_G, R1_B0, wB1);
        apply_M_pi_to_B2(&ff, ff.n_orb, warm_M, warm_pi, R2_B0, wB2);
        build_list_general(&ff, &ct, 0, wB1, all_cols, NULL, warm_m1);
        build_list_general(&ff, &ct, 1, wB2, all_cols, NULL, warm_m2);
        for (int k = 0; k < ct.w_42_end; k++) wb42 += __builtin_popcountll(warm_m1[k] & warm_m2[k]);
        for (int k = ct.w_42_end; k < ct.w_33_end; k++) wb33 += __builtin_popcountll(warm_m1[k] & warm_m2[k]);
        for (int k = ct.w_33_end; k < ct.w_total; k++) wb24 += __builtin_popcountll(warm_m1[k] & warm_m2[k]);
        warm_both = wb42 + wb33 + wb24;
    }

    printf("STAGE2 q=%d (k=%d, timeout=%.0fs, seed=%llu, warm=%d): min_dep1=%d, min_dep2=%d (warm_both=%d)\n",
           q, ff.k_full, timeout_sec, (unsigned long long)seed, has_warm,
           top_r1[0].dep, best_dep2, has_warm ? warm_both : -1);

    /* ---------- Part 2A: Non-cyclic permutation pi in S_{q+1} on Bahn B of Row 2 ---------- */
    double t2a_start = now_sec();
    double t2a_end = t0 + timeout_sec * 0.15;
    int best_pi_both = has_warm ? warm_both : 1000000000;
    int bp42 = wb42, bp33 = wb33, bp24 = wb24;
    int best_pi_is_warm = has_warm ? 1 : 0;
    int best_pi_r1 = 0, best_pi_r2 = 0;
    uint8_t best_pi[MAX_ORB];
    for (int k = 0; k < ff.n_orb; k++) best_pi[k] = has_warm ? warm_pi[k] : (uint8_t)k;
    uint64_t pi_evals = 0;
    int *d1_list = (int *)malloc((size_t)ct.n_total * sizeof(int));

    if (has_warm) {
        /* Test SA / local swaps on pi starting from warm_m1 & warm_m2 */
        int n_d1 = 0;
        for (int t = 0; t < ct.n_total; t++) {
            int bp = ct.bit_pos[t];
            if ((warm_m1[bp >> 6] >> (bp & 63)) & 1ULL) d1_list[n_d1++] = t;
        }
        uint64_t w_m2_base[MAX_WORDS];
        uint8_t wB2_id[MAX_ORB][6];
        build_R2_B_param(&ff, walpha, wbeta, 1, 0, wB2_id);
        build_mask_cyclic(&ff, &ct, 1, wB2_id, w_m2_base);
        for (int rep = 0; rep < 60 && now_sec() < t2a_end; rep++) {
            uint8_t perm[MAX_ORB];
            for (int k = 0; k < ff.n_orb; k++) perm[k] = (rep == 0) ? warm_pi[k] : (uint8_t)k;
            if (rep > 0) {
                for (int k = ff.n_orb - 1; k > 1; k--) {
                    int j = 1 + (int)rng_int(&rng, (uint32_t)k);
                    uint8_t tmp = perm[k]; perm[k] = perm[j]; perm[j] = tmp;
                }
            }
            int c42, c33, c24;
            int cur = count_perm_intersection(&ct, d1_list, n_d1, w_m2_base, perm, &c42, &c33, &c24);
            pi_evals++;
            for (int step = 0; step < 500; step++) {
                int u = 1 + (int)rng_int(&rng, (uint32_t)(ff.n_orb - 1));
                int v = 1 + (int)rng_int(&rng, (uint32_t)(ff.n_orb - 1));
                if (u == v) continue;
                uint8_t tmp = perm[u]; perm[u] = perm[v]; perm[v] = tmp;
                int nc42, nc33, nc24;
                int nxt = count_perm_intersection(&ct, d1_list, n_d1, w_m2_base, perm, &nc42, &nc33, &nc24);
                pi_evals++;
                if (nxt <= cur) {
                    cur = nxt; c42 = nc42; c33 = nc33; c24 = nc24;
                    if (cur < best_pi_both) {
                        best_pi_both = cur; bp42 = c42; bp33 = c33; bp24 = c24;
                        best_pi_is_warm = 1;
                        memcpy(best_pi, perm, (size_t)ff.n_orb);
                    }
                } else {
                    tmp = perm[u]; perm[u] = perm[v]; perm[v] = tmp;
                }
            }
        }
    }

    for (int i1 = 0; i1 < n_top_r1 && now_sec() < t2a_end && best_pi_both > 0; i1++) {
        int n_d1 = 0;
        for (int t = 0; t < ct.n_total; t++) {
            int bp = ct.bit_pos[t];
            if ((top_r1[i1].mask[bp >> 6] >> (bp & 63)) & 1ULL) d1_list[n_d1++] = t;
        }
        for (int i2 = 0; i2 < (q <= 7 ? 8 : 4) && now_sec() < t2a_end && best_pi_both > 0; i2++) {
            if (q <= 7) {
                uint8_t perm[MAX_ORB];
                for (int k = 0; k < ff.n_orb; k++) perm[k] = (uint8_t)k;
                do {
                    int c42, c33, c24;
                    int tot = count_perm_intersection(&ct, d1_list, n_d1, top_r2[i2].mask, perm, &c42, &c33, &c24);
                    pi_evals++;
                    if (tot < best_pi_both) {
                        best_pi_both = tot; bp42 = c42; bp33 = c33; bp24 = c24;
                        best_pi_is_warm = 0; best_pi_r1 = i1; best_pi_r2 = i2;
                        memcpy(best_pi, perm, (size_t)ff.n_orb);
                    }
                    if (tot == 0) break;
                } while (next_perm(perm + 1, ff.n_orb - 1));
            } else {
                for (int rep = 0; rep < 20 && now_sec() < t2a_end; rep++) {
                    uint8_t perm[MAX_ORB];
                    for (int k = 0; k < ff.n_orb; k++) perm[k] = (uint8_t)k;
                    for (int k = ff.n_orb - 1; k > 1; k--) {
                        int j = 1 + (int)rng_int(&rng, (uint32_t)k);
                        uint8_t tmp = perm[k]; perm[k] = perm[j]; perm[j] = tmp;
                    }
                    int c42, c33, c24;
                    int cur = count_perm_intersection(&ct, d1_list, n_d1, top_r2[i2].mask, perm, &c42, &c33, &c24);
                    pi_evals++;
                    for (int step = 0; step < 300; step++) {
                        int u = 1 + (int)rng_int(&rng, (uint32_t)(ff.n_orb - 1));
                        int v = 1 + (int)rng_int(&rng, (uint32_t)(ff.n_orb - 1));
                        if (u == v) continue;
                        uint8_t tmp = perm[u]; perm[u] = perm[v]; perm[v] = tmp;
                        int nc42, nc33, nc24;
                        int nxt = count_perm_intersection(&ct, d1_list, n_d1, top_r2[i2].mask, perm, &nc42, &nc33, &nc24);
                        pi_evals++;
                        if (nxt <= cur) {
                            cur = nxt; c42 = nc42; c33 = nc33; c24 = nc24;
                            if (cur < best_pi_both) {
                                best_pi_both = cur; bp42 = c42; bp33 = c33; bp24 = c24;
                                best_pi_is_warm = 0; best_pi_r1 = i1; best_pi_r2 = i2;
                                memcpy(best_pi, perm, (size_t)ff.n_orb);
                            }
                        } else {
                            tmp = perm[u]; perm[u] = perm[v]; perm[v] = tmp;
                        }
                    }
                }
            }
        }
    }
    printf("  [2A pi in S_%d] best_both=%d (42=%d, 33=%d, 24=%d), evals=%llu, time=%.3fs\n",
           ff.n_orb, best_pi_both, bp42, bp33, bp24,
           (unsigned long long)pi_evals, now_sec() - t2a_start);

    /* ---------- Part 2B: SA over G in GL(6, F_q) (Row 1) + warm-start ---------- */
    double t2b_start = now_sec();
    int *d2_list = (int *)malloc((size_t)ct.n_total * sizeof(int));
    int n_d2 = 0;

    int global_best = best_pi_both;
    int gb42 = bp42, gb33 = bp33, gb24 = bp24;
    uint8_t best_R1_B[MAX_ORB][6], best_R2_B[MAX_ORB][6];
    uint8_t best_G[6][6], best_M[4][4], best_pi2[MAX_ORB];
    memset(best_G, 0, sizeof(best_G));
    memset(best_M, 0, sizeof(best_M));
    for (int i = 0; i < 6; i++) best_G[i][i] = 1;
    for (int i = 0; i < 4; i++) best_M[i][i] = 1;
    memcpy(best_pi2, best_pi, sizeof(best_pi2));

    if (best_pi_is_warm && has_warm) {
        memcpy(best_G, warm_G, sizeof(warm_G));
        memcpy(best_M, warm_M, sizeof(warm_M));
        apply_G_to_B(&ff, ff.n_orb, best_G, R1_B0, best_R1_B);
        apply_M_pi_to_B2(&ff, ff.n_orb, best_M, best_pi2, R2_B0, best_R2_B);
    } else {
        set_k_block2(&ff, top_r1[best_pi_r1].g1, &best_G[0][0], 6, 0);
        set_k_block2(&ff, top_r1[best_pi_r1].g2, &best_G[0][0], 6, 2);
        set_k_block2(&ff, (KElem){1, 0}, &best_G[0][0], 6, 4);
        set_k_block2(&ff, top_r2[best_pi_r2].a, &best_M[0][0], 4, 0);
        set_k_block2(&ff, top_r2[best_pi_r2].b, &best_M[0][0], 4, 2);
        apply_G_to_B(&ff, ff.n_orb, best_G, R1_B0, best_R1_B);
        apply_M_pi_to_B2(&ff, ff.n_orb, best_M, best_pi2, R2_B0, best_R2_B);
    }

    uint64_t g_evals = 0, m_evals = 0;
    int restarts = 0;

    double t2b_mid = t0 + timeout_sec * 0.55;
    while (now_sec() < t2b_mid && global_best > 0) {
        restarts++;
        uint8_t cur_R2_B[MAX_ORB][6];
        uint8_t G[6][6], G_try[6][6], B1[MAX_ORB][6];
        double T_start, T_end;
        if (has_warm && (restarts % 2 == 1)) {
            /* Warm-start from best known (or original Stage-1 warm) Row 2 and G! */
            if (restarts == 1) {
                memcpy(cur_R2_B, best_R2_B, sizeof(cur_R2_B));
                memcpy(G, best_G, sizeof(G));
            } else {
                apply_M_pi_to_B2(&ff, ff.n_orb, warm_M, warm_pi, R2_B0, cur_R2_B);
                memcpy(G, warm_G, sizeof(G));
                /* Small random kick (1-3 elementary moves) */
                int kicks = 1 + (int)rng_int(&rng, 3);
                for (int k = 0; k < kicks; k++) {
                    perturb_GL(&ff, &rng, 6, &G[0][0], &G_try[0][0]);
                    memcpy(G, G_try, sizeof(G));
                }
            }
            n_d2 = build_list_general(&ff, &ct, 1, cur_R2_B, all_cols, d2_list, NULL);
            T_start = 2.5;
            T_end = 0.08;
        } else {
            int r2_idx = (restarts - 1) % 4;
            n_d2 = 0;
            for (int t = 0; t < ct.n_total; t++) {
                int bp = ct.bit_pos[t];
                if ((top_r2[r2_idx].mask[bp >> 6] >> (bp & 63)) & 1ULL) d2_list[n_d2++] = t;
            }
            build_R2_B_param(&ff, top_r2[r2_idx].a, top_r2[r2_idx].b, 1, 0, cur_R2_B);
            random_GL(&ff, &rng, 6, &G[0][0]);
            T_start = (q == 5) ? 4.0 : 12.0;
            T_end = 0.2;
        }
        apply_G_to_B(&ff, ff.n_orb, G, R1_B0, B1);
        int c42, c33, c24;
        int cur = eval_on_list(&ff, &ct, 0, B1, d2_list, n_d2, &c42, &c33, &c24);
        g_evals++;
        if (cur < global_best) {
            global_best = cur; gb42 = c42; gb33 = c33; gb24 = c24;
            memcpy(best_G, G, sizeof(G));
            memcpy(best_R1_B, B1, sizeof(B1));
            memcpy(best_R2_B, cur_R2_B, sizeof(cur_R2_B));
            if (global_best == 0) break;
        }

        int steps = (q == 5) ? 25000 : (q == 7) ? 8000 : (q == 8) ? 3500 : 1800;
        for (int s = 0; s < steps; s++) {
            if ((s & 127) == 0 && now_sec() >= t2b_mid) break;
            double frac = (double)s / (double)steps;
            double T = T_start * pow(T_end / T_start, frac);
            perturb_GL(&ff, &rng, 6, &G[0][0], &G_try[0][0]);
            apply_G_to_B(&ff, ff.n_orb, G_try, R1_B0, B1);
            int n42, n33, n24;
            int nxt = eval_on_list(&ff, &ct, 0, B1, d2_list, n_d2, &n42, &n33, &n24);
            g_evals++;
            int delta = nxt - cur;
            if (delta <= 0 || rng_double(&rng) < exp(-(double)delta / T)) {
                memcpy(G, G_try, sizeof(G));
                cur = nxt; c42 = n42; c33 = n33; c24 = n24;
                if (cur < global_best) {
                    global_best = cur; gb42 = c42; gb33 = c33; gb24 = c24;
                    memcpy(best_G, G, sizeof(G));
                    memcpy(best_R1_B, B1, sizeof(B1));
                    memcpy(best_R2_B, cur_R2_B, sizeof(cur_R2_B));
                    if (global_best == 0) break;
                }
            }
        }
    }
    double t2b_dur = now_sec() - t2b_start;
    printf("  [2B G in GL(6,F_%d) vs strong R2] best_both=%d (42=%d, 33=%d, 24=%d), restarts=%d, evals=%llu (%.1fk/s), time=%.3fs\n",
           q, global_best, gb42, gb33, gb24, restarts,
           (unsigned long long)g_evals, (double)g_evals / (t2b_dur * 1e3 + 1e-9), t2b_dur);

    /* ---------- Part 2C: Alternating (M in GL(4,F_q) + pi in S_{q+1}) and (G in GL(6,F_q)) ---------- */
    double t2c_start = now_sec();
    int alt_rounds = 0;
    uint8_t cur_B1[MAX_ORB][6], cur_B2[MAX_ORB][6];
    memcpy(cur_B1, best_R1_B, sizeof(cur_B1));
    memcpy(cur_B2, best_R2_B, sizeof(cur_B2));
    uint8_t M[4][4], M_try[4][4], pi[MAX_ORB], pi_try[MAX_ORB];
    uint8_t G[6][6], G_try[6][6];
    memcpy(G, best_G, sizeof(G));
    memcpy(M, best_M, sizeof(M));
    memcpy(pi, best_pi2, sizeof(pi));

    while (now_sec() < deadline && global_best > 0) {
        alt_rounds++;
        /* Optimize (M, pi) in Row 2 against fixed cur_B1 */
        int n_d1 = build_list_general(&ff, &ct, 0, cur_B1, all_cols, d1_list, NULL);
        if (alt_rounds > 1 && (alt_rounds % 3 == 0)) {
            if (has_warm) {
                memcpy(M, best_M, sizeof(M));
                memcpy(pi, best_pi2, sizeof(pi));
                memcpy(G, best_G, sizeof(G));
                perturb_GL(&ff, &rng, 4, &M[0][0], &M_try[0][0]);
                memcpy(M, M_try, sizeof(M));
            } else {
                random_GL(&ff, &rng, 4, &M[0][0]);
                for (int i = 0; i < ff.n_orb; i++) pi[i] = (uint8_t)i;
                for (int k = ff.n_orb - 1; k > 0; k--) {
                    int j = (int)rng_int(&rng, (uint32_t)(k + 1));
                    uint8_t tmp = pi[k]; pi[k] = pi[j]; pi[j] = tmp;
                }
            }
        }
        uint8_t B2_tmp[MAX_ORB][6];
        apply_M_pi_to_B2(&ff, ff.n_orb, M, pi, R2_B0, B2_tmp);
        int c42, c33, c24;
        int cur = eval_on_list(&ff, &ct, 1, B2_tmp, d1_list, n_d1, &c42, &c33, &c24);
        m_evals++;
        if (cur < global_best) {
            global_best = cur; gb42 = c42; gb33 = c33; gb24 = c24;
            memcpy(best_R1_B, cur_B1, sizeof(cur_B1));
            memcpy(best_R2_B, B2_tmp, sizeof(B2_tmp));
            memcpy(best_M, M, sizeof(M));
            memcpy(best_pi2, pi, sizeof(pi));
        }

        int m_steps = (q == 5) ? 10000 : (q == 7) ? 3500 : (q == 8) ? 2000 : 1200;
        double T_start = has_warm ? 2.5 : ((q == 5) ? 3.5 : 10.0);
        double T_end = 0.08;
        for (int s = 0; s < m_steps; s++) {
            if ((s & 255) == 0 && now_sec() >= deadline) break;
            double T = T_start * pow(T_end / T_start, (double)s / (double)m_steps);
            memcpy(M_try, M, sizeof(M));
            memcpy(pi_try, pi, sizeof(pi));
            if (rng_int(&rng, 3) == 0) {
                int u = (int)rng_int(&rng, (uint32_t)ff.n_orb);
                int v = (int)rng_int(&rng, (uint32_t)ff.n_orb);
                uint8_t t = pi_try[u]; pi_try[u] = pi_try[v]; pi_try[v] = t;
            } else {
                perturb_GL(&ff, &rng, 4, &M[0][0], &M_try[0][0]);
            }
            apply_M_pi_to_B2(&ff, ff.n_orb, M_try, pi_try, R2_B0, B2_tmp);
            int n42, n33, n24;
            int nxt = eval_on_list(&ff, &ct, 1, B2_tmp, d1_list, n_d1, &n42, &n33, &n24);
            m_evals++;
            int delta = nxt - cur;
            if (delta <= 0 || rng_double(&rng) < exp(-(double)delta / T)) {
                memcpy(M, M_try, sizeof(M));
                memcpy(pi, pi_try, sizeof(pi));
                cur = nxt; c42 = n42; c33 = n33; c24 = n24;
                if (cur < global_best) {
                    global_best = cur; gb42 = c42; gb33 = c33; gb24 = c24;
                    memcpy(best_R1_B, cur_B1, sizeof(cur_B1));
                    memcpy(best_R2_B, B2_tmp, sizeof(B2_tmp));
                    memcpy(best_M, M, sizeof(M));
                    memcpy(best_pi2, pi, sizeof(pi));
                    if (global_best == 0) break;
                }
            }
        }
        if (global_best == 0 || now_sec() >= deadline) break;

        /* Now optimize G in GL(6, q) against this new Row 2 */
        apply_M_pi_to_B2(&ff, ff.n_orb, M, pi, R2_B0, cur_B2);
        n_d2 = build_list_general(&ff, &ct, 1, cur_B2, all_cols, d2_list, NULL);
        uint8_t B1_tmp[MAX_ORB][6];
        apply_G_to_B(&ff, ff.n_orb, G, R1_B0, B1_tmp);
        cur = eval_on_list(&ff, &ct, 0, B1_tmp, d2_list, n_d2, &c42, &c33, &c24);
        g_evals++;
        int g_steps = (q == 5) ? 10000 : (q == 7) ? 3500 : 1200;
        for (int s = 0; s < g_steps; s++) {
            if ((s & 255) == 0 && now_sec() >= deadline) break;
            double T = T_start * pow(T_end / T_start, (double)s / (double)g_steps);
            perturb_GL(&ff, &rng, 6, &G[0][0], &G_try[0][0]);
            apply_G_to_B(&ff, ff.n_orb, G_try, R1_B0, B1_tmp);
            int n42, n33, n24;
            int nxt = eval_on_list(&ff, &ct, 0, B1_tmp, d2_list, n_d2, &n42, &n33, &n24);
            g_evals++;
            int delta = nxt - cur;
            if (delta <= 0 || rng_double(&rng) < exp(-(double)delta / T)) {
                memcpy(G, G_try, sizeof(G));
                cur = nxt; c42 = n42; c33 = n33; c24 = n24;
                if (cur < global_best) {
                    global_best = cur; gb42 = c42; gb33 = c33; gb24 = c24;
                    memcpy(best_R1_B, B1_tmp, sizeof(B1_tmp));
                    memcpy(best_R2_B, cur_B2, sizeof(cur_B2));
                    memcpy(best_G, G, sizeof(G));
                    if (global_best == 0) break;
                }
            }
        }
        apply_G_to_B(&ff, ff.n_orb, G, R1_B0, cur_B1);
    }

    /* Compute exact k_punc on global best */
    uint64_t bm1[MAX_WORDS], bm2[MAX_WORDS];
    build_list_general(&ff, &ct, 0, best_R1_B, all_cols, NULL, bm1);
    build_list_general(&ff, &ct, 1, best_R2_B, all_cols, NULL, bm2);
    uint32_t dmask = 0;
    int kpunc = compute_exact_kpunc(&ct, bm1, bm2, &dmask);

    double t2c_dur = now_sec() - t2c_start;
    printf("  [2C Alt (M,pi)+G] global_best=%d (42=%d, 33=%d, 24=%d), k_punc=%d/%d (del_mask=0x%x), alt_rounds=%d, m_evals=%llu, total_time=%.3fs\n",
           global_best, gb42, gb33, gb24, kpunc, ff.k_full, dmask, alt_rounds,
           (unsigned long long)m_evals, now_sec() - t0);
    (void)t2c_dur;

    /* Full verification & save if global_best == 0 or kpunc > N_q(1) */
    int nq1 = (q == 5) ? 10 : (q == 7) ? 13 : (q == 8) ? 14 : 16;
    if (out_dir && (global_best == 0 || kpunc > nq1)) {
        uint8_t R1_out[MAX_K][6], R2_out[MAX_K][6];
        int kA = 0, kB = 0;
        for (int c = 0; c < ff.n_orb; c++) {
            if (!((dmask >> c) & 1U)) {
                memcpy(R1_out[kA], R1_A[c], 6);
                memcpy(R2_out[kA], R2_A[c], 6);
                kA++;
            }
        }
        for (int c = 0; c < ff.n_orb; c++) {
            if (!((dmask >> (ff.n_orb + c)) & 1U)) {
                memcpy(R1_out[kA + kB], best_R1_B[c], 6);
                memcpy(R2_out[kA + kB], best_R2_B[c], 6);
                kB++;
            }
        }
        int d1[7], d2[7], bt[7];
        full_check_matrices(&ff, kA, kB, R1_out, R2_out, d1, d2, bt);
        int unc = 0;
        for (int a = 0; a <= 6; a++) unc += bt[a];
        printf("  FULL C VERIFY (k=%d, kA=%d, kB=%d): unc=%d\n", kA + kB, kA, kB, unc);
        if (unc == 0) {
            char fname[512], meta[256];
            snprintf(fname, sizeof(fname), "%s/cphf_q%d_k%d_stage2_s%llu.json",
                     out_dir, q, kA + kB, (unsigned long long)seed);
            snprintf(meta, sizeof(meta),
                     "{\"stage\":\"stage2\",\"seed\":%llu,\"full_both\":%d,\"del_mask\":%u}",
                     (unsigned long long)seed, global_best, dmask);
            save_cphf_json(fname, q, kA, kB, R1_out, R2_out, meta);
            printf("  SAVED HIT -> %s\n", fname);
        }
    }

    free(d1_list); free(d2_list);
    free(ct.tuples); free(ct.bit_pos); free(ct.orb_rep); free(ct.orb_len); free(ct.orb_start); free(ct.orb_members);
}

/* ---------- STAGE 3: Direct Punctured Target Search (kA <= q+1, kB <= q+1) ---------- */
static void run_stage3(int q, int kA, int kB, const char *out_dir, double timeout_sec, uint64_t seed) {
    double t0 = now_sec();
    double deadline = t0 + timeout_sec;
    FF ff;
    ff_init(&ff, q);
    Rng rng;
    rng_seed(&rng, seed);

    uint8_t R1_A[MAX_ORB][6], R2_A[MAX_ORB][6];
    build_R1_base(&ff, R1_A);
    build_R2_base(&ff, R2_A);

    CritTable ct;
    init_crit_table(&ct, &ff, R1_A, R2_A);

    uint8_t R1_B0[MAX_ORB][6], R2_B0[MAX_ORB][6];
    build_R1_B_param(&ff, (KElem){1, 0}, (KElem){1, 0}, (KElem){1, 0}, 1, 0, 0, R1_B0);
    build_R2_B_param(&ff, (KElem){1, 0}, (KElem){1, 0}, 1, 0, R2_B0);

    /* Active columns: first kA of Orbit A and first kB of Orbit B */
    uint32_t active_mask = 0;
    for (int i = 0; i < kA; i++) active_mask |= 1U << i;
    for (int i = 0; i < kB; i++) active_mask |= 1U << (ff.n_orb + i);

    int *d1_list = (int *)malloc((size_t)ct.n_total * sizeof(int));
    int *d2_list = (int *)malloc((size_t)ct.n_total * sizeof(int));

    /* Pick best parametric Row 2 on this active subset */
    int best_dep2 = 1000000000;
    KElem best_alpha = {1, 0}, best_beta = {1, 0};
    for (int ia = 0; ia < ff.n_orb; ia++) {
        KElem alpha = ff.zeta_pow[ia];
        for (int ib = 0; ib < ff.k_order; ib++) {
            KElem beta = ff.k_nonzero[ib];
            uint8_t B2[MAX_ORB][6];
            build_R2_B_param(&ff, alpha, beta, 1, 0, B2);
            int dep = build_list_general(&ff, &ct, 1, B2, active_mask, NULL, NULL);
            if (dep < best_dep2) {
                best_dep2 = dep; best_alpha = alpha; best_beta = beta;
            }
        }
    }

    uint8_t base_R2_B[MAX_ORB][6];
    build_R2_B_param(&ff, best_alpha, best_beta, 1, 0, base_R2_B);
    int n_d2_base = build_list_general(&ff, &ct, 1, base_R2_B, active_mask, d2_list, NULL);

    int global_best = 1000000000, gb42 = 0, gb33 = 0, gb24 = 0;
    uint8_t best_R1_B[MAX_ORB][6], best_R2_B[MAX_ORB][6];
    memcpy(best_R2_B, base_R2_B, sizeof(best_R2_B));
    uint64_t evals = 0;
    int restarts = 0;

    while (now_sec() < deadline && global_best > 0) {
        restarts++;
        uint8_t cur_B2[MAX_ORB][6];
        uint8_t M[4][4], pi[MAX_ORB];
        int n_d2;
        if (restarts == 1 || (restarts % 2 == 1)) {
            memcpy(cur_B2, base_R2_B, sizeof(cur_B2));
            n_d2 = n_d2_base;
            build_list_general(&ff, &ct, 1, cur_B2, active_mask, d2_list, NULL);
        } else {
            random_GL(&ff, &rng, 4, &M[0][0]);
            for (int i = 0; i < ff.n_orb; i++) pi[i] = (uint8_t)i;
            for (int k = ff.n_orb - 1; k > 0; k--) {
                int j = (int)rng_int(&rng, (uint32_t)(k + 1));
                uint8_t t = pi[k]; pi[k] = pi[j]; pi[j] = t;
            }
            apply_M_pi_to_B2(&ff, ff.n_orb, M, pi, R2_B0, cur_B2);
            n_d2 = build_list_general(&ff, &ct, 1, cur_B2, active_mask, d2_list, NULL);
        }

        uint8_t G[6][6], G_try[6][6], B1[MAX_ORB][6];
        random_GL(&ff, &rng, 6, &G[0][0]);
        apply_G_to_B(&ff, ff.n_orb, G, R1_B0, B1);
        int c42, c33, c24;
        int cur = eval_on_list(&ff, &ct, 0, B1, d2_list, n_d2, &c42, &c33, &c24);
        evals++;
        if (cur < global_best) {
            global_best = cur; gb42 = c42; gb33 = c33; gb24 = c24;
            memcpy(best_R1_B, B1, sizeof(B1));
            memcpy(best_R2_B, cur_B2, sizeof(cur_B2));
            if (global_best == 0) break;
        }

        /* Alternating SA: G steps then (M,pi) steps */
        double T_start = (q == 5) ? 3.0 : 8.0;
        double T_end = 0.12;
        int steps = (q == 5) ? 15000 : (q == 7) ? 6000 : 2500;
        for (int s = 0; s < steps; s++) {
            if ((s & 255) == 0 && now_sec() >= deadline) break;
            double T = T_start * pow(T_end / T_start, (double)s / (double)steps);
            perturb_GL(&ff, &rng, 6, &G[0][0], &G_try[0][0]);
            apply_G_to_B(&ff, ff.n_orb, G_try, R1_B0, B1);
            int n42, n33, n24;
            int nxt = eval_on_list(&ff, &ct, 0, B1, d2_list, n_d2, &n42, &n33, &n24);
            evals++;
            int delta = nxt - cur;
            if (delta <= 0 || rng_double(&rng) < exp(-(double)delta / T)) {
                memcpy(G, G_try, sizeof(G));
                cur = nxt; c42 = n42; c33 = n33; c24 = n24;
                if (cur < global_best) {
                    global_best = cur; gb42 = c42; gb33 = c33; gb24 = c24;
                    memcpy(best_R1_B, B1, sizeof(B1));
                    memcpy(best_R2_B, cur_B2, sizeof(cur_B2));
                    if (global_best == 0) break;
                }
            }
        }
        if (global_best == 0 || now_sec() >= deadline) break;

        /* Polish Row 2 (M, pi) against this G */
        apply_G_to_B(&ff, ff.n_orb, G, R1_B0, B1);
        int n_d1 = build_list_general(&ff, &ct, 0, B1, active_mask, d1_list, NULL);
        random_GL(&ff, &rng, 4, &M[0][0]);
        for (int i = 0; i < ff.n_orb; i++) pi[i] = (uint8_t)i;
        uint8_t M_try[4][4], pi_try[MAX_ORB], B2_tmp[MAX_ORB][6];
        apply_M_pi_to_B2(&ff, ff.n_orb, M, pi, R2_B0, B2_tmp);
        cur = eval_on_list(&ff, &ct, 1, B2_tmp, d1_list, n_d1, &c42, &c33, &c24);
        evals++;
        int msteps = steps / 2;
        for (int s = 0; s < msteps; s++) {
            if ((s & 255) == 0 && now_sec() >= deadline) break;
            double T = T_start * pow(T_end / T_start, (double)s / (double)msteps);
            memcpy(M_try, M, sizeof(M));
            memcpy(pi_try, pi, sizeof(pi));
            if (rng_int(&rng, 3) == 0) {
                int u = (int)rng_int(&rng, (uint32_t)ff.n_orb);
                int v = (int)rng_int(&rng, (uint32_t)ff.n_orb);
                uint8_t t = pi_try[u]; pi_try[u] = pi_try[v]; pi_try[v] = t;
            } else {
                perturb_GL(&ff, &rng, 4, &M[0][0], &M_try[0][0]);
            }
            apply_M_pi_to_B2(&ff, ff.n_orb, M_try, pi_try, R2_B0, B2_tmp);
            int n42, n33, n24;
            int nxt = eval_on_list(&ff, &ct, 1, B2_tmp, d1_list, n_d1, &n42, &n33, &n24);
            evals++;
            int delta = nxt - cur;
            if (delta <= 0 || rng_double(&rng) < exp(-(double)delta / T)) {
                memcpy(M, M_try, sizeof(M));
                memcpy(pi, pi_try, sizeof(pi));
                cur = nxt; c42 = n42; c33 = n33; c24 = n24;
                if (cur < global_best) {
                    global_best = cur; gb42 = c42; gb33 = c33; gb24 = c24;
                    memcpy(best_R1_B, B1, sizeof(B1));
                    memcpy(best_R2_B, B2_tmp, sizeof(B2_tmp));
                    if (global_best == 0) break;
                }
            }
        }
    }

    double dt = now_sec() - t0;
    printf("STAGE3 q=%d k=%d (%d+%d): best_both=%d (42=%d, 33=%d, 24=%d), min_dep2=%d, restarts=%d, evals=%llu (%.1fk/s), time=%.3fs\n",
           q, kA + kB, kA, kB, global_best, gb42, gb33, gb24, best_dep2,
           restarts, (unsigned long long)evals, (double)evals / (dt * 1e3 + 1e-9), dt);

    if (global_best == 0) {
        uint8_t R1_out[MAX_K][6], R2_out[MAX_K][6];
        for (int c = 0; c < kA; c++) {
            memcpy(R1_out[c], R1_A[c], 6);
            memcpy(R2_out[c], R2_A[c], 6);
        }
        for (int c = 0; c < kB; c++) {
            memcpy(R1_out[kA + c], best_R1_B[c], 6);
            memcpy(R2_out[kA + c], best_R2_B[c], 6);
        }
        int d1[7], d2[7], bt[7];
        full_check_matrices(&ff, kA, kB, R1_out, R2_out, d1, d2, bt);
        int unc = 0;
        for (int a = 0; a <= 6; a++) unc += bt[a];
        printf("  FULL C VERIFY (k=%d, kA=%d, kB=%d): unc=%d\n", kA + kB, kA, kB, unc);
        if (unc == 0 && out_dir) {
            char fname[512], meta[256];
            snprintf(fname, sizeof(fname), "%s/cphf_q%d_k%d_%dplus%d_stage3_s%llu.json",
                     out_dir, q, kA + kB, kA, kB, (unsigned long long)seed);
            snprintf(meta, sizeof(meta),
                     "{\"stage\":\"stage3\",\"kA\":%d,\"kB\":%d,\"seed\":%llu}",
                     kA, kB, (unsigned long long)seed);
            save_cphf_json(fname, q, kA, kB, R1_out, R2_out, meta);
            printf("  SAVED HIT -> %s\n", fname);
        }
    }

    free(d1_list); free(d2_list);
    free(ct.tuples); free(ct.bit_pos); free(ct.orb_rep); free(ct.orb_len); free(ct.orb_start); free(ct.orb_members);
}

/* ---------- Main CLI ---------- */
int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <check|stage1|stage2|stage3> ...\n", argv[0]);
        return 1;
    }
    if (strcmp(argv[1], "check") == 0) {
        if (argc < 16) {
            fprintf(stderr, "Usage: %s check q g1_0 g1_1 g2_0 g2_1 a0 a1 b0 b1 m1 d1 frob1 m2 d2\n", argv[0]);
            return 1;
        }
        int q = atoi(argv[2]);
        KElem g1 = {(uint8_t)atoi(argv[3]), (uint8_t)atoi(argv[4])};
        KElem g2 = {(uint8_t)atoi(argv[5]), (uint8_t)atoi(argv[6])};
        KElem alpha = {(uint8_t)atoi(argv[7]), (uint8_t)atoi(argv[8])};
        KElem beta = {(uint8_t)atoi(argv[9]), (uint8_t)atoi(argv[10])};
        int m1 = atoi(argv[11]), d1 = atoi(argv[12]), frob1 = atoi(argv[13]);
        int m2 = atoi(argv[14]), d2 = atoi(argv[15]);

        FF ff;
        ff_init(&ff, q);
        uint8_t R1_A[MAX_ORB][6], R1_B[MAX_ORB][6], R2_A[MAX_ORB][6], R2_B[MAX_ORB][6];
        build_R1_base(&ff, R1_A);
        build_R1_B_param(&ff, g1, g2, (KElem){1, 0}, m1, d1, frob1, R1_B);
        build_R2_base(&ff, R2_A);
        build_R2_B_param(&ff, alpha, beta, m2, d2, R2_B);

        uint8_t R1[MAX_K][6], R2[MAX_K][6];
        for (int i = 0; i < ff.n_orb; i++) {
            memcpy(R1[i], R1_A[i], 6);
            memcpy(R1[ff.n_orb + i], R1_B[i], 6);
            memcpy(R2[i], R2_A[i], 6);
            memcpy(R2[ff.n_orb + i], R2_B[i], 6);
        }
        int dep1[7], dep2[7], both[7];
        full_check_matrices(&ff, ff.n_orb, ff.n_orb, R1, R2, dep1, dep2, both);
        printf("{\"dep1\":[%d,%d,%d,%d,%d,%d,%d],\"dep2\":[%d,%d,%d,%d,%d,%d,%d],\"both\":[%d,%d,%d,%d,%d,%d,%d]}\n",
               dep1[0], dep1[1], dep1[2], dep1[3], dep1[4], dep1[5], dep1[6],
               dep2[0], dep2[1], dep2[2], dep2[3], dep2[4], dep2[5], dep2[6],
               both[0], both[1], both[2], both[3], both[4], both[5], both[6]);
        return 0;
    } else if (strcmp(argv[1], "stage1") == 0) {
        int q = atoi(argv[2]);
        const char *out_dir = NULL;
        double timeout = 85.0;
        int threads = 2;
        for (int i = 3; i < argc; i++) {
            if (strcmp(argv[i], "--out-dir") == 0 && i + 1 < argc) out_dir = argv[++i];
            else if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) timeout = atof(argv[++i]);
            else if (strcmp(argv[i], "--threads") == 0 && i + 1 < argc) threads = atoi(argv[++i]);
        }
        run_stage1(q, out_dir, timeout, threads);
        return 0;
    } else if (strcmp(argv[1], "stage2") == 0) {
        int q = atoi(argv[2]);
        const char *out_dir = NULL;
        double timeout = 85.0;
        uint64_t seed = 20261128;
        int has_warm = 0, wm2 = 1;
        KElem wg1 = {1, 0}, wg2 = {1, 0}, wa = {1, 0}, wb = {1, 0};
        for (int i = 3; i < argc; i++) {
            if (strcmp(argv[i], "--out-dir") == 0 && i + 1 < argc) out_dir = argv[++i];
            else if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) timeout = atof(argv[++i]);
            else if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) seed = strtoull(argv[++i], NULL, 10);
            else if (strcmp(argv[i], "--warm") == 0 && i + 9 < argc) {
                has_warm = 1;
                wg1 = (KElem){(uint8_t)atoi(argv[i + 1]), (uint8_t)atoi(argv[i + 2])};
                wg2 = (KElem){(uint8_t)atoi(argv[i + 3]), (uint8_t)atoi(argv[i + 4])};
                wa  = (KElem){(uint8_t)atoi(argv[i + 5]), (uint8_t)atoi(argv[i + 6])};
                wb  = (KElem){(uint8_t)atoi(argv[i + 7]), (uint8_t)atoi(argv[i + 8])};
                wm2 = atoi(argv[i + 9]);
                i += 9;
            }
        }
        run_stage2(q, out_dir, timeout, seed, has_warm, wg1, wg2, wa, wb, wm2);
        return 0;
    } else if (strcmp(argv[1], "stage3") == 0) {
        int q = atoi(argv[2]);
        int kA = atoi(argv[3]);
        int kB = atoi(argv[4]);
        const char *out_dir = NULL;
        double timeout = 30.0;
        uint64_t seed = 20261128;
        for (int i = 5; i < argc; i++) {
            if (strcmp(argv[i], "--out-dir") == 0 && i + 1 < argc) out_dir = argv[++i];
            else if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) timeout = atof(argv[++i]);
            else if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) seed = strtoull(argv[++i], NULL, 10);
        }
        run_stage3(q, kA, kB, out_dir, timeout, seed);
        return 0;
    } else {
        fprintf(stderr, "Unknown mode: %s\n", argv[1]);
        return 1;
    }
}
