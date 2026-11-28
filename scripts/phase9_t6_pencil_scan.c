/*
 * Phase 9B Option B (AP 1 / AP 2 / AP 3):
 * Ultra-fast OpenMP Stage-1 Scanner, Exact Hitting-Set Puncturer, and AP-1 Dumper
 * for Hyperplane-Pencil CPHF(2; 2q+2, q, 6) over F_q (q in {5, 7, 8, 9, 11, 13}).
 *
 * Build:
 *   gcc -O3 -march=native -fopenmp -Wall -Wextra scripts/phase9_t6_pencil_scan.c -o /tmp/phase9_t6_pencil_scan -lm
 *
 * Modes:
 *   check    <q> <g1_0> <g1_1> <g2_0> <g2_1> <a0> <a1> <b0> <b1> <m2>
 *   bench    <q> [--threads N]
 *   dump-ap1 <q> --out <json> [--threads N]
 *   scan     <q> [--m2-mode all|m2eq1|m2ne1] [--no-sym] [--chunk-start I] [--chunk-end J]
 *                [--out <json>] [--jsonl <ckpt>] [--save-hit-dir <dir>] [--threads N] [--timeout SEC]
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <omp.h>

#define MAX_Q 19
#define MAX_ORB 20
#define MAX_K 40
#define MAX_KORDER 360

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

static int gcd_int(int a, int b) {
    while (b) { int t = a % b; a = b; b = t; }
    return a;
}

/* ---------- Finite Field F_q and K = F_{q^2} ---------- */
typedef struct { uint8_t a, b; } KElem;

typedef struct {
    int q;
    int n_orb;      /* q + 1 */
    int k_full;     /* 2q + 2 */
    int k_order;    /* q^2 - 1 */
    uint8_t add[MAX_Q][MAX_Q];
    uint8_t sub[MAX_Q][MAX_Q];
    uint8_t mul[MAX_Q][MAX_Q];
    uint8_t inv[MAX_Q];
    uint8_t is_sq[MAX_Q];
    uint8_t p0, p1; /* i^2 = p0 + p1*i */
    KElem zeta;
    KElem eta;
    KElem zeta_pow[MAX_KORDER + 1];
    KElem eta_pow[MAX_ORB];
    KElem k_nonzero[MAX_KORDER];
    int16_t k_log[MAX_Q][MAX_Q]; /* discrete log base zeta, -1 for 0 */
    int16_t k_idx[MAX_Q][MAX_Q]; /* index in k_nonzero (0..k_order-1), -1 for 0 */
    int16_t k_conj[MAX_KORDER];  /* index of z^q */
    int16_t k_inv[MAX_KORDER];   /* index of z^{-1} */
    int16_t k_mul_idx[MAX_KORDER][MAX_KORDER]; /* index of u*v */
    uint8_t k_norm[MAX_KORDER];  /* norm z^{q+1} in F_q* */
} FF;

static uint8_t mul8_raw(uint8_t a, uint8_t b) {
    uint16_t r = 0;
    for (int i = 0; i < 3; i++) if ((b >> i) & 1) r ^= (uint16_t)a << i;
    for (int i = 4; i >= 3; i--) if ((r >> i) & 1) r ^= (uint16_t)(0x0B << (i - 3));
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

    if (q == 5 || q == 7 || q == 11 || q == 13 || q == 17 || q == 19) {
        for (int a = 0; a < q; a++)
            for (int b = 0; b < q; b++) {
                ff->add[a][b] = (uint8_t)((a + b) % q);
                ff->sub[a][b] = (uint8_t)((a - b + q) % q);
                ff->mul[a][b] = (uint8_t)((a * b) % q);
            }
    } else if (q == 8) {
        for (int a = 0; a < 8; a++)
            for (int b = 0; b < 8; b++) {
                ff->add[a][b] = (uint8_t)(a ^ b);
                ff->sub[a][b] = (uint8_t)(a ^ b);
                ff->mul[a][b] = mul8_raw((uint8_t)a, (uint8_t)b);
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
        ff->is_sq[ff->mul[a][a]] = 1;
        for (int b = 1; b < q; b++)
            if (ff->mul[a][b] == 1) { ff->inv[a] = (uint8_t)b; break; }
    }

    if (q == 5)       { ff->p0 = 2; ff->p1 = 0; ff->zeta = (KElem){2, 1}; }
    else if (q == 7)  { ff->p0 = 3; ff->p1 = 0; ff->zeta = (KElem){1, 1}; }
    else if (q == 8)  { ff->p0 = 1; ff->p1 = 1; ff->zeta = (KElem){2, 1}; }
    else if (q == 9)  { ff->p0 = 4; ff->p1 = 0; ff->zeta = (KElem){3, 1}; }
    else if (q == 11) { ff->p0 = 2; ff->p1 = 0; ff->zeta = (KElem){2, 1}; }
    else if (q == 13) { ff->p0 = 2; ff->p1 = 0; ff->zeta = (KElem){2, 1}; }
    else if (q == 17) { ff->p0 = 3; ff->p1 = 0; ff->zeta = (KElem){3, 1}; }
    else if (q == 19) { ff->p0 = 2; ff->p1 = 0; ff->zeta = (KElem){2, 1}; }

    ff->eta = k_pow(ff, ff->zeta, q - 1);
    for (int a = 0; a < MAX_Q; a++)
        for (int b = 0; b < MAX_Q; b++) { ff->k_log[a][b] = -1; ff->k_idx[a][b] = -1; }

    for (int e = 0; e <= ff->k_order; e++) {
        ff->zeta_pow[e] = k_pow(ff, ff->zeta, e);
        if (e < ff->k_order) ff->k_log[ff->zeta_pow[e].a][ff->zeta_pow[e].b] = (int16_t)e;
    }
    for (int e = 0; e < ff->n_orb; e++) ff->eta_pow[e] = k_pow(ff, ff->eta, e);

    int idx = 0;
    for (int a = 0; a < q; a++) {
        for (int b = 0; b < q; b++) {
            if (a == 0 && b == 0) continue;
            ff->k_nonzero[idx] = (KElem){(uint8_t)a, (uint8_t)b};
            ff->k_idx[a][b] = (int16_t)idx;
            idx++;
        }
    }
    for (int i = 0; i < ff->k_order; i++) {
        KElem z = ff->k_nonzero[i];
        KElem zq = k_pow(ff, z, q);
        KElem zi = k_pow(ff, z, ff->k_order - 1);
        KElem nm = k_mul(ff, z, zq);
        ff->k_conj[i] = ff->k_idx[zq.a][zq.b];
        ff->k_inv[i] = ff->k_idx[zi.a][zi.b];
        ff->k_norm[i] = nm.a;
        for (int j = 0; j < ff->k_order; j++) {
            KElem p = k_mul(ff, z, ff->k_nonzero[j]);
            ff->k_mul_idx[i][j] = ff->k_idx[p.a][p.b];
        }
    }
}

/* ---------- Fast Rank/Det Helpers ---------- */
static inline int rank6_full(const FF *ff, uint8_t m[6][6]) {
    for (int col = 0; col < 6; col++) {
        int piv = -1;
        for (int r = col; r < 6; r++) if (m[r][col] != 0) { piv = r; break; }
        if (piv < 0) return 0;
        if (piv != col) {
            for (int j = col; j < 6; j++) { uint8_t t = m[col][j]; m[col][j] = m[piv][j]; m[piv][j] = t; }
        }
        uint8_t inv_p = ff->inv[m[col][col]];
        for (int r = col + 1; r < 6; r++) {
            uint8_t v = m[r][col];
            if (v != 0) {
                uint8_t f = ff->mul[v][inv_p];
                for (int j = col + 1; j < 6; j++) m[r][j] = ff->sub[m[r][j]][ff->mul[f][m[col][j]]];
            }
        }
    }
    return 1;
}

static inline int rank4_full(const FF *ff, uint8_t m[4][4]) {
    for (int col = 0; col < 4; col++) {
        int piv = -1;
        for (int r = col; r < 4; r++) if (m[r][col] != 0) { piv = r; break; }
        if (piv < 0) return 0;
        if (piv != col) {
            for (int j = col; j < 4; j++) { uint8_t t = m[col][j]; m[col][j] = m[piv][j]; m[piv][j] = t; }
        }
        uint8_t inv_p = ff->inv[m[col][col]];
        for (int r = col + 1; r < 4; r++) {
            uint8_t v = m[r][col];
            if (v != 0) {
                uint8_t f = ff->mul[v][inv_p];
                for (int j = col + 1; j < 4; j++) m[r][j] = ff->sub[m[r][j]][ff->mul[f][m[col][j]]];
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

static void compute_nullspace(const FF *ff, int a, const uint8_t A_in[4][6], uint8_t N_out[4][6]) {
    uint8_t M[4][6];
    memcpy(M, A_in, (size_t)a * 6);
    int piv_col[4], is_piv[6] = {0, 0, 0, 0, 0, 0};
    int r = 0;
    for (int col = 0; col < 6 && r < a; col++) {
        int p = -1;
        for (int i = r; i < a; i++) if (M[i][col] != 0) { p = i; break; }
        if (p < 0) continue;
        if (p != r) {
            for (int j = 0; j < 6; j++) { uint8_t t = M[r][j]; M[r][j] = M[p][j]; M[p][j] = t; }
        }
        uint8_t inv_p = ff->inv[M[r][col]];
        for (int j = col; j < 6; j++) M[r][j] = ff->mul[M[r][j]][inv_p];
        for (int i = 0; i < a; i++) {
            if (i != r && M[i][col] != 0) {
                uint8_t f = M[i][col];
                for (int j = col; j < 6; j++) M[i][j] = ff->sub[M[i][j]][ff->mul[f][M[r][j]]];
            }
        }
        piv_col[r] = col; is_piv[col] = 1; r++;
    }
    if (r != a) { fprintf(stderr, "FATAL nullspace rank %d != %d\n", r, a); exit(1); }
    int fi = 0;
    for (int col = 0; col < 6; col++) {
        if (!is_piv[col]) {
            memset(N_out[fi], 0, 6);
            N_out[fi][col] = 1;
            for (int i = 0; i < a; i++) N_out[fi][piv_col[i]] = ff->sub[0][M[i][col]];
            fi++;
        }
    }
}

/* ---------- Row Builders ---------- */
static void build_R1_A(const FF *ff, uint8_t R1_A[MAX_ORB][6]) {
    int q = ff->q;
    for (int k = 0; k < ff->n_orb; k++) {
        KElem w = ff->zeta_pow[k];
        KElem c1 = k_pow(ff, w, 5), c2 = k_pow(ff, w, 4 + q), c3 = k_pow(ff, w, 3 + 2 * q);
        R1_A[k][0] = c1.a; R1_A[k][1] = c1.b;
        R1_A[k][2] = c2.a; R1_A[k][3] = c2.b;
        R1_A[k][4] = c3.a; R1_A[k][5] = c3.b;
    }
}

static void build_R1_B(const FF *ff, KElem g1, KElem g2, uint8_t R1_B[MAX_ORB][6]) {
    int q = ff->q;
    for (int k = 0; k < ff->n_orb; k++) {
        KElem w = ff->zeta_pow[k];
        KElem c1 = k_mul(ff, g1, k_pow(ff, w, 5));
        KElem c2 = k_mul(ff, g2, k_pow(ff, w, 4 + q));
        KElem c3 = k_pow(ff, w, 3 + 2 * q);
        R1_B[k][0] = c1.a; R1_B[k][1] = c1.b;
        R1_B[k][2] = c2.a; R1_B[k][3] = c2.b;
        R1_B[k][4] = c3.a; R1_B[k][5] = c3.b;
    }
}

static void build_R2_A(const FF *ff, uint8_t R2_A[MAX_ORB][6]) {
    for (int k = 0; k < ff->n_orb; k++) {
        KElem u = ff->eta_pow[k], u2 = k_mul(ff, u, u);
        R2_A[k][0] = u2.a; R2_A[k][1] = u2.b;
        R2_A[k][2] = u.a;  R2_A[k][3] = u.b;
        R2_A[k][4] = 1;    R2_A[k][5] = 0;
    }
}

static void build_R2_B(const FF *ff, KElem alpha, KElem beta, int m2, uint8_t R2_B[MAX_ORB][6]) {
    int n = ff->n_orb;
    for (int k = 0; k < n; k++) {
        KElem u = ff->eta_pow[(m2 * k) % n], u2 = k_mul(ff, u, u);
        KElem a2 = k_mul(ff, alpha, u2), b1 = k_mul(ff, beta, u);
        R2_B[k][0] = a2.a; R2_B[k][1] = a2.b;
        R2_B[k][2] = b1.a; R2_B[k][3] = b1.b;
        R2_B[k][4] = 0;    R2_B[k][5] = 1;
    }
}

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

/* ---------- Critical Tuple Table + Compressed Z_{q+1}-Orbit Table ---------- */
typedef struct {
    uint8_t a_cnt;
    uint8_t a_idx[4];
    uint8_t b_idx[4];
    uint16_t a_comb_id;
    uint16_t b_comb_id;
    uint32_t col_mask;
} CritTuple;

typedef struct {
    int n_orb;
    int n_42, n_33, n_24, n_total;
    int w_42_end, w_33_end, w_total;
    int off_42, off_33, off_24;
    CritTuple *tuples;
    int *bit_pos;

    int nA2, nA3, nA4;
    uint8_t comb2[91][2];
    uint8_t comb3[364][3];
    uint8_t comb4[1001][4];

    uint8_t N1_4[1001][2][6], N1_3[364][3][6], N1_2[91][4][6];
    uint8_t N2_4[1001][2][6], N2_3[364][3][6], N2_2[91][4][6];

    int16_t mask2id[16384];

    /* Z_{q+1} orbits */
    int n_orbits;
    int *orb_rep;
    int *orb_len;
    int *orb_start;
    int *orb_members;

    /* Compressed orbit bit layout for m2 == 1:
     * Full-length orbits (len == n_orb) in word-aligned [f42][f33][f24];
     * Short orbits (len < n_orb) in a single uint64_t (max 64 short orbits for q<=13!). */
    int nf_42, nf_33, nf_24;
    int ow_42_end, ow_33_end, ow_total;
    int *orb_bit;       /* >= 0: bit in full-orbit mask; < 0: -(short_idx + 1) */
    int n_short;
    uint8_t short_acnt[64];
    uint8_t short_len[64];
    int short_oid[64];
} CritTable;

static void init_crit_table(CritTable *ct, const FF *ff,
                            const uint8_t R1_A[MAX_ORB][6], const uint8_t R2_A[MAX_ORB][6]) {
    memset(ct, 0, sizeof(*ct));
    int n = ff->n_orb;
    ct->n_orb = n;
    for (int i = 0; i < 16384; i++) ct->mask2id[i] = -1;

    ct->nA2 = 0;
    for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++) {
        ct->comb2[ct->nA2][0] = (uint8_t)i; ct->comb2[ct->nA2][1] = (uint8_t)j;
        ct->mask2id[(1 << i) | (1 << j)] = (int16_t)ct->nA2++;
    }
    ct->nA3 = 0;
    for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
    for (int k = j + 1; k < n; k++) {
        ct->comb3[ct->nA3][0] = (uint8_t)i; ct->comb3[ct->nA3][1] = (uint8_t)j; ct->comb3[ct->nA3][2] = (uint8_t)k;
        ct->mask2id[(1 << i) | (1 << j) | (1 << k)] = (int16_t)ct->nA3++;
    }
    ct->nA4 = 0;
    for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
    for (int k = j + 1; k < n; k++)
    for (int l = k + 1; l < n; l++) {
        ct->comb4[ct->nA4][0] = (uint8_t)i; ct->comb4[ct->nA4][1] = (uint8_t)j;
        ct->comb4[ct->nA4][2] = (uint8_t)k; ct->comb4[ct->nA4][3] = (uint8_t)l;
        ct->mask2id[(1 << i) | (1 << j) | (1 << k) | (1 << l)] = (int16_t)ct->nA4++;
    }

    uint8_t mat[4][6], Ntmp[4][6];
    for (int id = 0; id < ct->nA4; id++) {
        for (int r = 0; r < 4; r++) memcpy(mat[r], R1_A[ct->comb4[id][r]], 6);
        compute_nullspace(ff, 4, mat, Ntmp); memcpy(ct->N1_4[id], Ntmp, 12);
        for (int r = 0; r < 4; r++) memcpy(mat[r], R2_A[ct->comb4[id][r]], 6);
        compute_nullspace(ff, 4, mat, Ntmp); memcpy(ct->N2_4[id], Ntmp, 12);
    }
    for (int id = 0; id < ct->nA3; id++) {
        for (int r = 0; r < 3; r++) memcpy(mat[r], R1_A[ct->comb3[id][r]], 6);
        compute_nullspace(ff, 3, mat, Ntmp); memcpy(ct->N1_3[id], Ntmp, 18);
        for (int r = 0; r < 3; r++) memcpy(mat[r], R2_A[ct->comb3[id][r]], 6);
        compute_nullspace(ff, 3, mat, Ntmp); memcpy(ct->N2_3[id], Ntmp, 18);
    }
    for (int id = 0; id < ct->nA2; id++) {
        for (int r = 0; r < 2; r++) memcpy(mat[r], R1_A[ct->comb2[id][r]], 6);
        compute_nullspace(ff, 2, mat, Ntmp); memcpy(ct->N1_2[id], Ntmp, 24);
        for (int r = 0; r < 2; r++) memcpy(mat[r], R2_A[ct->comb2[id][r]], 6);
        compute_nullspace(ff, 2, mat, Ntmp); memcpy(ct->N2_2[id], Ntmp, 24);
    }

    ct->n_42 = ct->nA4 * ct->nA2;
    ct->n_33 = ct->nA3 * ct->nA3;
    ct->n_24 = ct->nA2 * ct->nA4;
    ct->n_total = ct->n_42 + ct->n_33 + ct->n_24;

    int w42 = (ct->n_42 + 63) / 64, w33 = (ct->n_33 + 63) / 64, w24 = (ct->n_24 + 63) / 64;
    ct->off_42 = 0; ct->w_42_end = w42;
    ct->off_33 = w42 * 64; ct->w_33_end = w42 + w33;
    ct->off_24 = (w42 + w33) * 64; ct->w_total = w42 + w33 + w24;

    ct->tuples = (CritTuple *)malloc((size_t)ct->n_total * sizeof(CritTuple));
    ct->bit_pos = (int *)malloc((size_t)ct->n_total * sizeof(int));

    int t = 0;
    for (int ia = 0; ia < ct->nA4; ia++)
        for (int ib = 0; ib < ct->nA2; ib++) {
            CritTuple *x = &ct->tuples[t];
            x->a_cnt = 4; x->a_comb_id = (uint16_t)ia; x->b_comb_id = (uint16_t)ib;
            uint32_t cm = 0;
            for (int r = 0; r < 4; r++) { x->a_idx[r] = ct->comb4[ia][r]; cm |= 1U << x->a_idx[r]; }
            for (int r = 0; r < 2; r++) { x->b_idx[r] = ct->comb2[ib][r]; cm |= 1U << (n + x->b_idx[r]); }
            x->col_mask = cm; ct->bit_pos[t] = ct->off_42 + ia * ct->nA2 + ib; t++;
        }
    for (int ia = 0; ia < ct->nA3; ia++)
        for (int ib = 0; ib < ct->nA3; ib++) {
            CritTuple *x = &ct->tuples[t];
            x->a_cnt = 3; x->a_comb_id = (uint16_t)ia; x->b_comb_id = (uint16_t)ib;
            uint32_t cm = 0;
            for (int r = 0; r < 3; r++) { x->a_idx[r] = ct->comb3[ia][r]; cm |= 1U << x->a_idx[r]; }
            for (int r = 0; r < 3; r++) { x->b_idx[r] = ct->comb3[ib][r]; cm |= 1U << (n + x->b_idx[r]); }
            x->col_mask = cm; ct->bit_pos[t] = ct->off_33 + ia * ct->nA3 + ib; t++;
        }
    for (int ia = 0; ia < ct->nA2; ia++)
        for (int ib = 0; ib < ct->nA4; ib++) {
            CritTuple *x = &ct->tuples[t];
            x->a_cnt = 2; x->a_comb_id = (uint16_t)ia; x->b_comb_id = (uint16_t)ib;
            uint32_t cm = 0;
            for (int r = 0; r < 2; r++) { x->a_idx[r] = ct->comb2[ia][r]; cm |= 1U << x->a_idx[r]; }
            for (int r = 0; r < 4; r++) { x->b_idx[r] = ct->comb4[ib][r]; cm |= 1U << (n + x->b_idx[r]); }
            x->col_mask = cm; ct->bit_pos[t] = ct->off_24 + ia * ct->nA4 + ib; t++;
        }

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
        int ac = base->a_cnt, bc = 6 - ac;
        for (int sh = 0; sh < n; sh++) {
            int ma = 0, mb = 0;
            for (int r = 0; r < ac; r++) ma |= 1 << ((base->a_idx[r] + sh) % n);
            for (int r = 0; r < bc; r++) mb |= 1 << ((base->b_idx[r] + sh) % n);
            int ia = ct->mask2id[ma], ib = ct->mask2id[mb];
            int tid = (ac == 4) ? (ia * ct->nA2 + ib)
                    : (ac == 3) ? (ct->n_42 + ia * ct->nA3 + ib)
                                : (ct->n_42 + ct->n_33 + ia * ct->nA4 + ib);
            if (!vis[tid]) {
                vis[tid] = 1;
                ct->orb_members[mem_pos++] = tid;
                len++;
            }
        }
        ct->orb_len[oid] = len;
    }
    free(vis);

    /* Partition orbits into full-length (42, 33, 24) and short (< n_orb) */
    ct->nf_42 = ct->nf_33 = ct->nf_24 = ct->n_short = 0;
    for (int oid = 0; oid < ct->n_orbits; oid++) {
        int ac = ct->tuples[ct->orb_rep[oid]].a_cnt;
        if (ct->orb_len[oid] == n) {
            if (ac == 4) ct->nf_42++;
            else if (ac == 3) ct->nf_33++;
            else ct->nf_24++;
        } else {
            ct->n_short++;
        }
    }
    if (ct->n_short > 64) {
        fprintf(stderr, "FATAL: n_short=%d > 64\n", ct->n_short);
        exit(1);
    }
    int ow42 = (ct->nf_42 + 63) / 64, ow33 = (ct->nf_33 + 63) / 64, ow24 = (ct->nf_24 + 63) / 64;
    ct->ow_42_end = ow42;
    ct->ow_33_end = ow42 + ow33;
    ct->ow_total = ow42 + ow33 + ow24;

    ct->orb_bit = (int *)malloc((size_t)ct->n_orbits * sizeof(int));
    int p42 = 0, p33 = ow42 * 64, p24 = (ow42 + ow33) * 64, ps = 0;
    for (int oid = 0; oid < ct->n_orbits; oid++) {
        int ac = ct->tuples[ct->orb_rep[oid]].a_cnt;
        if (ct->orb_len[oid] == n) {
            if (ac == 4) ct->orb_bit[oid] = p42++;
            else if (ac == 3) ct->orb_bit[oid] = p33++;
            else ct->orb_bit[oid] = p24++;
        } else {
            ct->short_acnt[ps] = (uint8_t)ac;
            ct->short_len[ps] = (uint8_t)ct->orb_len[oid];
            ct->short_oid[ps] = oid;
            ct->orb_bit[oid] = -(ps + 1);
            ps++;
        }
    }
}

static void free_crit_table(CritTable *ct) {
    free(ct->tuples); free(ct->bit_pos);
    free(ct->orb_rep); free(ct->orb_len); free(ct->orb_start); free(ct->orb_members);
    free(ct->orb_bit);
}

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

/* Build compressed orbit-mask (ow_total words + 1 short_mask word) for cyclic Row 1 or Row 2(m2=1) */
static int build_orb_mask(const FF *ff, const CritTable *ct, int is_row2,
                          const uint8_t B[MAX_ORB][6], uint64_t *omask, uint64_t *short_mask) {
    memset(omask, 0, (size_t)ct->ow_total * sizeof(uint64_t));
    uint64_t sm = 0;
    int dep = 0;
    for (int oid = 0; oid < ct->n_orbits; oid++) {
        if (!check_tuple_nullspace(ff, ct, ct->orb_rep[oid], is_row2, B)) {
            dep += ct->orb_len[oid];
            int ob = ct->orb_bit[oid];
            if (ob >= 0) omask[ob >> 6] |= 1ULL << (ob & 63);
            else sm |= 1ULL << (-(ob + 1));
        }
    }
    *short_mask = sm;
    return dep;
}

/* Expand an orbit-mask into a full-tuple bitmask (w_total words) */
static void expand_orb_to_full(const CritTable *ct, const uint64_t *omask, uint64_t sm, uint64_t *fmask) {
    memset(fmask, 0, (size_t)ct->w_total * sizeof(uint64_t));
    for (int oid = 0; oid < ct->n_orbits; oid++) {
        int ob = ct->orb_bit[oid];
        int set = (ob >= 0) ? (int)((omask[ob >> 6] >> (ob & 63)) & 1ULL)
                            : (int)((sm >> (-(ob + 1))) & 1ULL);
        if (set) {
            int st = ct->orb_start[oid], len = ct->orb_len[oid];
            for (int j = 0; j < len; j++) {
                int bp = ct->bit_pos[ct->orb_members[st + j]];
                fmask[bp >> 6] |= 1ULL << (bp & 63);
            }
        }
    }
}

/* Permute Orbit-B indices of a full mask: new_B[k] = old_B[perm[k]] */
static void permute_full_mask_B(const CritTable *ct, const uint64_t *src,
                                const uint8_t perm[MAX_ORB], uint64_t *dst) {
    memset(dst, 0, (size_t)ct->w_total * sizeof(uint64_t));
    int map2[91], map3[364], map4[1001];
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

/* ---------- Exact Minimum Hitting Set (Iterative Deepening Branch & Bound) ---------- */
typedef struct {
    int n_edges;
    int k_cols;
    uint32_t *edges;
    int target_depth;
    int found;
    uint32_t sol_mask;
    uint64_t nodes;
    uint64_t node_limit;
    int aborted;
} HitIDState;

static void hit_id_dfs(HitIDState *hs, uint32_t chosen, int depth, int first_unc) {
    if (hs->found || hs->aborted) return;
    if (++hs->nodes > hs->node_limit) { hs->aborted = 1; return; }

    /* Find uncovered edge and compute vertex degrees + greedy disjoint-edge packing lower bound */
    int rem_unc = 0;
    int deg[MAX_K];
    memset(deg, 0, (size_t)hs->k_cols * sizeof(int));
    int first_u = -1;
    uint32_t pack_used = 0;
    int pack_lb = 0;

    for (int i = first_unc; i < hs->n_edges; i++) {
        uint32_t e = hs->edges[i];
        if ((e & chosen) == 0) {
            if (first_u < 0) first_u = i;
            rem_unc++;
            if ((e & pack_used) == 0) {
                pack_used |= e;
                pack_lb++;
            }
            uint32_t tmp = e;
            while (tmp) {
                int v = __builtin_ctz(tmp);
                deg[v]++;
                tmp &= tmp - 1;
            }
        }
    }
    if (rem_unc == 0) {
        hs->found = 1;
        hs->sol_mask = chosen;
        return;
    }
    int rem_slots = hs->target_depth - depth;
    if (rem_slots <= 0 || pack_lb > rem_slots) return;

    int max_deg = 0;
    for (int v = 0; v < hs->k_cols; v++) if (deg[v] > max_deg) max_deg = deg[v];
    if (max_deg * rem_slots < rem_unc) return;

    if (rem_slots == 1) {
        /* Only need to check if any single vertex hits all rem_unc edges */
        for (int v = 0; v < hs->k_cols; v++) {
            if (deg[v] == rem_unc) {
                hs->found = 1;
                hs->sol_mask = chosen | (1U << v);
                return;
            }
        }
        return;
    }

    /* Choose branching edge: pick uncovered edge with smallest sum of vertex degrees (tightest constraint)
       or first_u; wait: picking edge with minimum max-degree or minimum total-degree shrinks branching! */
    int best_e_idx = first_u;
    int best_score = 1000000000;
    int scan_cap = (hs->n_edges < first_u + 128) ? hs->n_edges : (first_u + 128);
    for (int i = first_u; i < scan_cap; i++) {
        uint32_t e = hs->edges[i];
        if ((e & chosen) == 0) {
            int sc = 0;
            uint32_t tmp = e;
            while (tmp) { int v = __builtin_ctz(tmp); sc += deg[v]; tmp &= tmp - 1; }
            if (sc < best_score) { best_score = sc; best_e_idx = i; }
        }
    }

    /* Order vertices of chosen edge by descending degree */
    uint32_t e = hs->edges[best_e_idx];
    int verts[6], vdeg[6], nv = 0;
    while (e) {
        int v = __builtin_ctz(e);
        verts[nv] = v; vdeg[nv] = deg[v]; nv++;
        e &= e - 1;
    }
    for (int i = 0; i < nv; i++)
        for (int j = i + 1; j < nv; j++)
            if (vdeg[j] > vdeg[i]) {
                int tv = verts[i]; verts[i] = verts[j]; verts[j] = tv;
                int td = vdeg[i]; vdeg[i] = vdeg[j]; vdeg[j] = td;
            }

    for (int j = 0; j < nv; j++) {
        hit_id_dfs(hs, chosen | (1U << verts[j]), depth + 1, first_u);
        if (hs->found || hs->aborted) return;
    }
}

/* Compute exact minimum hitting set tau (returns tau; sets *out_exact=1 if proven exact, 0 if greedy/capped) */
static int compute_min_hitting_set(const CritTable *ct, const uint64_t *m1, const uint64_t *m2,
                                   int max_exact_tau, uint64_t node_limit,
                                   uint32_t *out_del_mask, int *out_exact, int *out_greedy_tau,
                                   int *out_max_col_deg) {
    int k_cols = 2 * ct->n_orb;
    uint32_t *edges = (uint32_t *)malloc((size_t)ct->n_total * sizeof(uint32_t));
    int n_edges = 0;
    int col_deg[MAX_K];
    memset(col_deg, 0, sizeof(col_deg));

    for (int t = 0; t < ct->n_total; t++) {
        int bp = ct->bit_pos[t];
        if (((m1[bp >> 6] & m2[bp >> 6]) >> (bp & 63)) & 1ULL) {
            uint32_t cm = ct->tuples[t].col_mask;
            edges[n_edges++] = cm;
            uint32_t tmp = cm;
            while (tmp) { int v = __builtin_ctz(tmp); col_deg[v]++; tmp &= tmp - 1; }
        }
    }
    int max_cd = 0;
    for (int v = 0; v < k_cols; v++) if (col_deg[v] > max_cd) max_cd = col_deg[v];
    if (out_max_col_deg) *out_max_col_deg = max_cd;

    if (n_edges == 0) {
        free(edges);
        if (out_del_mask) *out_del_mask = 0;
        if (out_exact) *out_exact = 1;
        if (out_greedy_tau) *out_greedy_tau = 0;
        return 0;
    }

    /* Greedy upper bound */
    uint32_t gmask = 0;
    int gdel = 0;
    while (1) {
        int best_v = -1, best_d = 0;
        for (int v = 0; v < k_cols; v++) {
            if ((gmask >> v) & 1U) continue;
            int d = 0;
            for (int i = 0; i < n_edges; i++)
                if ((edges[i] & gmask) == 0 && ((edges[i] >> v) & 1U)) d++;
            if (d > best_d) { best_d = d; best_v = v; }
        }
        if (best_d == 0) break;
        gmask |= 1U << best_v;
        gdel++;
    }
    if (out_greedy_tau) *out_greedy_tau = gdel;

    /* Lower bound from max degree */
    int lb = (n_edges + max_cd - 1) / max_cd;
    if (lb >= gdel) {
        free(edges);
        if (out_del_mask) *out_del_mask = gmask;
        if (out_exact) *out_exact = 1;
        return gdel;
    }

    int cap = (gdel - 1 < max_exact_tau) ? (gdel - 1) : max_exact_tau;
    for (int d = lb; d <= cap; d++) {
        HitIDState hs;
        hs.n_edges = n_edges;
        hs.k_cols = k_cols;
        hs.edges = edges;
        hs.target_depth = d;
        hs.found = 0;
        hs.sol_mask = 0;
        hs.nodes = 0;
        hs.node_limit = node_limit;
        hs.aborted = 0;
        hit_id_dfs(&hs, 0, 0, 0);
        if (hs.found) {
            free(edges);
            if (out_del_mask) *out_del_mask = hs.sol_mask;
            if (out_exact) *out_exact = 1;
            return d;
        }
        if (hs.aborted) {
            free(edges);
            if (out_del_mask) *out_del_mask = gmask;
            if (out_exact) *out_exact = 0;
            return gdel;
        }
    }
    free(edges);
    if (out_del_mask) *out_del_mask = gmask;
    if (out_exact) *out_exact = (cap == gdel - 1) ? 1 : 0;
    return gdel;
}

/* ---------- Candidate List Management ---------- */
typedef struct {
    int g1_idx, g2_idx;
    int a_coset, b_idx, m2;
    int tot, b42, b33, b24;
    int tau, exact_tau, greedy_tau, max_col_deg;
    uint64_t del_mask;
} Cand;

typedef struct {
    Cand *items;
    int count;
    int cap;
} CandHeap;

static void cand_init(CandHeap *ch, int cap) {
    ch->items = (Cand *)malloc((size_t)cap * sizeof(Cand));
    ch->count = 0;
    ch->cap = cap;
}

static void cand_add(CandHeap *ch, Cand c) {
    if (ch->count < ch->cap) {
        ch->items[ch->count++] = c;
        int pos = ch->count - 1;
        while (pos > 0 && ch->items[pos].tot < ch->items[pos - 1].tot) {
            Cand tmp = ch->items[pos]; ch->items[pos] = ch->items[pos - 1]; ch->items[pos - 1] = tmp;
            pos--;
        }
    } else if (c.tot < ch->items[ch->cap - 1].tot) {
        int pos = ch->cap - 1;
        ch->items[pos] = c;
        while (pos > 0 && ch->items[pos].tot < ch->items[pos - 1].tot) {
            Cand tmp = ch->items[pos]; ch->items[pos] = ch->items[pos - 1]; ch->items[pos - 1] = tmp;
            pos--;
        }
    }
}

/* ---------- Symmetry Reduction Tables ---------- */
/* Row-1 C2 x C2 orbit reps: (g1, g2) ~ (g1^q, g2^q) ~ (g1^{-1}, g2^{-1}) ~ (g1^{-q}, g2^{-q}) */
typedef struct { int g1_idx, g2_idx; int orb_size; } R1Rep;

static int build_r1_reps(const FF *ff, int use_sym, R1Rep *out) {
    int nk = ff->k_order;
    int cnt = 0;
    for (int i = 0; i < nk; i++) {
        for (int j = 0; j < nk; j++) {
            if (!use_sym) {
                out[cnt++] = (R1Rep){i, j, 1};
                continue;
            }
            int k0 = i * nk + j;
            int i_c = ff->k_conj[i], j_c = ff->k_conj[j];
            int i_v = ff->k_inv[i],  j_v = ff->k_inv[j];
            int i_cv = ff->k_conj[i_v], j_cv = ff->k_conj[j_v];
            int ks[4] = {k0, i_c * nk + j_c, i_v * nk + j_v, i_cv * nk + j_cv};
            int min_k = k0;
            for (int t = 1; t < 4; t++) if (ks[t] < min_k) min_k = ks[t];
            if (min_k == k0) {
                int uniq = 1;
                for (int t = 1; t < 4; t++) {
                    int seen = 0;
                    for (int u = 0; u < t; u++) if (ks[t] == ks[u]) seen = 1;
                    if (!seen) uniq++;
                }
                out[cnt++] = (R1Rep){i, j, uniq};
            }
        }
    }
    return cnt;
}

/* Normalize (alpha, beta) mod F_q^* to (zeta^{a_coset}, beta') with a_coset in 0..q */
static void normalize_r2_ab(const FF *ff, KElem alpha, KElem beta, int *out_ac, int *out_bidx) {
    int la = ff->k_log[alpha.a][alpha.b];
    int n = ff->n_orb;
    int ac = la % n;
    /* alpha = zeta^{ac} * lambda where lambda = zeta^{la - ac} in F_q^* */
    int lam_exp = (la - ac + ff->k_order) % ff->k_order;
    int inv_lam_exp = (ff->k_order - lam_exp) % ff->k_order;
    KElem beta_p = k_mul(ff, beta, ff->zeta_pow[inv_lam_exp]);
    *out_ac = ac;
    *out_bidx = ff->k_idx[beta_p.a][beta_p.b];
}

typedef struct { int a_coset, b_idx, m2; int base_idx; } R2Rep;

/* For a fixed m2, build Row-2 reps modulo simultaneous shift (alpha, beta) -> (alpha*eta^{2(m2-1)r}, beta*eta^{(m2-1)r}) */
static int build_r2_reps_for_m2(const FF *ff, int m2, int use_sym, R2Rep *out) {
    int n = ff->n_orb, nk = ff->k_order;
    int cnt = 0;
    for (int ac = 0; ac < n; ac++) {
        for (int bi = 0; bi < nk; bi++) {
            int base_idx = ac * nk + bi;
            if (!use_sym || m2 == 1) {
                out[cnt++] = (R2Rep){ac, bi, m2, base_idx};
                continue;
            }
            int min_key = base_idx;
            KElem alpha = ff->zeta_pow[ac];
            KElem beta = ff->k_nonzero[bi];
            for (int r = 1; r < n; r++) {
                int sh = ((m2 - 1) * r) % n;
                if (sh < 0) sh += n;
                KElem a2 = k_mul(ff, alpha, ff->eta_pow[(2 * sh) % n]);
                KElem b2 = k_mul(ff, beta, ff->eta_pow[sh]);
                int nac, nbi;
                normalize_r2_ab(ff, a2, b2, &nac, &nbi);
                int key = nac * nk + nbi;
                if (key < min_key) min_key = key;
            }
            if (min_key == base_idx) {
                out[cnt++] = (R2Rep){ac, bi, m2, base_idx};
            }
        }
    }
    return cnt;
}

/* Save verified CPHF matrix JSON (after removing del_mask columns) */
static void save_cphf_hit_json(const char *path, const FF *ff,
                               const uint8_t R1_A[MAX_ORB][6], const uint8_t R2_A[MAX_ORB][6],
                               const Cand *c) {
    uint8_t R1_B[MAX_ORB][6], R2_B[MAX_ORB][6];
    build_R1_B(ff, ff->k_nonzero[c->g1_idx], ff->k_nonzero[c->g2_idx], R1_B);
    build_R2_B(ff, ff->zeta_pow[c->a_coset], ff->k_nonzero[c->b_idx], c->m2, R2_B);

    uint8_t R1_out[MAX_K][6], R2_out[MAX_K][6];
    int kA = 0, kB = 0;
    for (int i = 0; i < ff->n_orb; i++) {
        if (!((c->del_mask >> i) & 1ULL)) {
            memcpy(R1_out[kA], R1_A[i], 6);
            memcpy(R2_out[kA], R2_A[i], 6);
            kA++;
        }
    }
    for (int i = 0; i < ff->n_orb; i++) {
        if (!((c->del_mask >> (ff->n_orb + i)) & 1ULL)) {
            memcpy(R1_out[kA + kB], R1_B[i], 6);
            memcpy(R2_out[kA + kB], R2_B[i], 6);
            kB++;
        }
    }
    int k = kA + kB;
    FILE *fp = fopen(path, "w");
    if (!fp) { perror("fopen hit"); return; }
    KElem g1 = ff->k_nonzero[c->g1_idx], g2 = ff->k_nonzero[c->g2_idx];
    KElem al = ff->zeta_pow[c->a_coset], be = ff->k_nonzero[c->b_idx];
    fprintf(fp, "{\n  \"q\": %d,\n  \"k\": %d,\n  \"n_orbit_a\": %d,\n", ff->q, k, kA);
    fprintf(fp, "  \"meta\": {\"g1\":[%d,%d],\"g2\":[%d,%d],\"alpha\":[%d,%d],\"beta\":[%d,%d],\"m2\":%d,"
                "\"full_unc\":%d,\"splits\":[%d,%d,%d],\"tau\":%d,\"exact_tau\":%d,\"del_mask\":%llu},\n",
            g1.a, g1.b, g2.a, g2.b, al.a, al.b, be.a, be.b, c->m2,
            c->tot, c->b42, c->b33, c->b24, c->tau, c->exact_tau, (unsigned long long)c->del_mask);
    fprintf(fp, "  \"R1\": [\n");
    for (int i = 0; i < k; i++)
        fprintf(fp, "    [%d, %d, %d, %d, %d, %d]%s\n",
                R1_out[i][0], R1_out[i][1], R1_out[i][2], R1_out[i][3], R1_out[i][4], R1_out[i][5],
                (i + 1 < k) ? "," : "");
    fprintf(fp, "  ],\n  \"R2\": [\n");
    for (int i = 0; i < k; i++)
        fprintf(fp, "    [%d, %d, %d, %d, %d, %d]%s\n",
                R2_out[i][0], R2_out[i][1], R2_out[i][2], R2_out[i][3], R2_out[i][4], R2_out[i][5],
                (i + 1 < k) ? "," : "");
    fprintf(fp, "  ]\n}\n");
    fclose(fp);
}

/* ---------- Core Scan Function (used by both dump-ap1 and scan) ---------- */
static void run_scan(int q, int use_sym, int m2_mode, int chunk_start, int chunk_end,
                     const char *out_json, const char *jsonl_path, const char *save_hit_dir,
                     int n_threads, double timeout_sec, int dump_all_zeros) {
    double t0 = now_sec();
    double deadline = t0 + timeout_sec;
    omp_set_num_threads(n_threads);

    FF ff;
    ff_init(&ff, q);
    uint8_t R1_A[MAX_ORB][6], R2_A[MAX_ORB][6];
    build_R1_A(&ff, R1_A);
    build_R2_A(&ff, R2_A);

    CritTable ct;
    init_crit_table(&ct, &ff, R1_A, R2_A);

    /* Build Row-1 representatives */
    int max_r1 = ff.k_order * ff.k_order;
    R1Rep *r1_reps = (R1Rep *)malloc((size_t)max_r1 * sizeof(R1Rep));
    int n1_all = build_r1_reps(&ff, use_sym, r1_reps);
    if (chunk_start < 0) chunk_start = 0;
    if (chunk_end <= 0 || chunk_end > n1_all) chunk_end = n1_all;
    int n1 = chunk_end - chunk_start;

    /* Build Row-1 orbit masks for chunk [chunk_start, chunk_end) */
    uint64_t *r1_omasks = (uint64_t *)malloc((size_t)n1 * ct.ow_total * sizeof(uint64_t));
    uint64_t *r1_smasks = (uint64_t *)malloc((size_t)n1 * sizeof(uint64_t));
    int *r1_deps = (int *)malloc((size_t)n1 * sizeof(int));

    #pragma omp parallel for schedule(static)
    for (int idx = 0; idx < n1; idx++) {
        R1Rep rep = r1_reps[chunk_start + idx];
        uint8_t R1_B[MAX_ORB][6];
        build_R1_B(&ff, ff.k_nonzero[rep.g1_idx], ff.k_nonzero[rep.g2_idx], R1_B);
        r1_deps[idx] = build_orb_mask(&ff, &ct, 0, R1_B,
                                      r1_omasks + (size_t)idx * ct.ow_total, &r1_smasks[idx]);
    }
    double t_r1 = now_sec() - t0;

    /* Build all base Row-2 (m2 = 1) orbit masks */
    int n2_base = ff.n_orb * ff.k_order;
    uint64_t *r2_omasks = (uint64_t *)malloc((size_t)n2_base * ct.ow_total * sizeof(uint64_t));
    uint64_t *r2_smasks = (uint64_t *)malloc((size_t)n2_base * sizeof(uint64_t));
    int *r2_deps = (int *)malloc((size_t)n2_base * sizeof(int));

    #pragma omp parallel for schedule(static)
    for (int base = 0; base < n2_base; base++) {
        int ac = base / ff.k_order, bi = base % ff.k_order;
        uint8_t R2_B[MAX_ORB][6];
        build_R2_B(&ff, ff.zeta_pow[ac], ff.k_nonzero[bi], 1, R2_B);
        r2_deps[base] = build_orb_mask(&ff, &ct, 1, R2_B,
                                       r2_omasks + (size_t)base * ct.ow_total, &r2_smasks[base]);
    }
    double t_r2 = now_sec() - t0 - t_r1;

    /* Prepare coprime m2 list */
    int coprimes[MAX_ORB], n_cop = 0;
    for (int m = 1; m < ff.n_orb; m++) if (gcd_int(m, ff.n_orb) == 1) coprimes[n_cop++] = m;

    /* Global accumulators */
    CandHeap top_global;
    cand_init(&top_global, 200);
    CandHeap top_per_m2[MAX_ORB];
    for (int c = 0; c < n_cop; c++) cand_init(&top_per_m2[c], 50);

    Cand *zero_list = NULL;
    int zero_cap = dump_all_zeros ? 4096 : 64;
    int zero_cnt = 0;
    zero_list = (Cand *)malloc((size_t)zero_cap * sizeof(Cand));

    int min_42 = 1000000000, min_33 = 1000000000, min_24 = 1000000000, min_tot = 1000000000;
    uint64_t pairs_m2eq1 = 0, pairs_m2ne1 = 0;
    uint64_t total_zeros_raw = 0;
    int timed_out = 0;

    /* ---------- PASS A: m2 == 1 (Ultra-fast compressed Z_{q+1}-orbit intersection) ---------- */
    double t_pa_start = now_sec();
    if (m2_mode == 0 || m2_mode == 1) {
        int ow42 = ct.ow_42_end, ow33 = ct.ow_33_end, owtot = ct.ow_total;
        int n_orb = ff.n_orb;

        #pragma omp parallel
        {
            CandHeap loc_top;
            cand_init(&loc_top, 200);
            int l_m42 = 1000000000, l_m33 = 1000000000, l_m24 = 1000000000, l_mtot = 1000000000;
            uint64_t l_pairs = 0, l_zeros = 0;

            #pragma omp for schedule(dynamic, 16)
            for (int i1 = 0; i1 < n1; i1++) {
                if (timed_out) continue;
                if ((i1 & 63) == 0 && now_sec() > deadline) { timed_out = 1; continue; }
                const uint64_t *m1 = r1_omasks + (size_t)i1 * owtot;
                uint64_t sm1 = r1_smasks[i1];
                R1Rep rep1 = r1_reps[chunk_start + i1];

                for (int i2 = 0; i2 < n2_base; i2++) {
                    const uint64_t *m2 = r2_omasks + (size_t)i2 * owtot;
                    int c42 = 0, c33 = 0, c24 = 0;
                    for (int w = 0; w < ow42; w++) c42 += __builtin_popcountll(m1[w] & m2[w]);
                    for (int w = ow42; w < ow33; w++) c33 += __builtin_popcountll(m1[w] & m2[w]);
                    for (int w = ow33; w < owtot; w++) c24 += __builtin_popcountll(m1[w] & m2[w]);
                    int b42 = c42 * n_orb, b33 = c33 * n_orb, b24 = c24 * n_orb;
                    uint64_t sm = sm1 & r2_smasks[i2];
                    while (sm) {
                        int sb = __builtin_ctzll(sm);
                        sm &= sm - 1;
                        uint8_t sl = ct.short_len[sb];
                        uint8_t ac = ct.short_acnt[sb];
                        if (ac == 4) b42 += sl;
                        else if (ac == 3) b33 += sl;
                        else b24 += sl;
                    }
                    int tot = b42 + b33 + b24;
                    l_pairs++;
                    if (b42 < l_m42) l_m42 = b42;
                    if (b33 < l_m33) l_m33 = b33;
                    if (b24 < l_m24) l_m24 = b24;
                    if (tot < l_mtot) l_mtot = tot;
                    if (tot == 0) {
                        l_zeros++;
                        #pragma omp critical(zeros)
                        {
                            if (zero_cnt < zero_cap) {
                                zero_list[zero_cnt++] = (Cand){
                                    rep1.g1_idx, rep1.g2_idx, i2 / ff.k_order, i2 % ff.k_order, 1,
                                    0, 0, 0, 0, 0, 1, 0, 0, 0
                                };
                            }
                        }
                    }
                    if (loc_top.count < loc_top.cap || tot < loc_top.items[loc_top.cap - 1].tot) {
                        Cand c = {rep1.g1_idx, rep1.g2_idx, i2 / ff.k_order, i2 % ff.k_order, 1,
                                  tot, b42, b33, b24, -1, 0, -1, 0, 0};
                        cand_add(&loc_top, c);
                    }
                }
            }
            #pragma omp critical(merge_a)
            {
                pairs_m2eq1 += l_pairs;
                total_zeros_raw += l_zeros;
                if (l_m42 < min_42) min_42 = l_m42;
                if (l_m33 < min_33) min_33 = l_m33;
                if (l_m24 < min_24) min_24 = l_m24;
                if (l_mtot < min_tot) min_tot = l_mtot;
                for (int k = 0; k < loc_top.count; k++) {
                    cand_add(&top_global, loc_top.items[k]);
                    cand_add(&top_per_m2[0], loc_top.items[k]);
                }
            }
            free(loc_top.items);
        }
    }
    double t_pa = now_sec() - t_pa_start;

    /* ---------- PASS B: m2 != 1 (Batched streaming full-mask intersection with shift reduction) ---------- */
    double t_pb_start = now_sec();
    if ((m2_mode == 0 || m2_mode == 2) && !timed_out) {
        int w42 = ct.w_42_end, w33 = ct.w_33_end, wtot = ct.w_total;
        /* Build shift-reduced Row-2 full masks for all m2 != 1 */
        R2Rep *r2_ne1 = (R2Rep *)malloc((size_t)(n_cop * n2_base) * sizeof(R2Rep));
        int *r2_m2_cidx = (int *)malloc((size_t)(n_cop * n2_base) * sizeof(int));
        int n2_ne1 = 0;
        for (int cm = 1; cm < n_cop; cm++) {
            int m2 = coprimes[cm];
            int added = build_r2_reps_for_m2(&ff, m2, use_sym, r2_ne1 + n2_ne1);
            for (int k = 0; k < added; k++) r2_m2_cidx[n2_ne1 + k] = cm;
            n2_ne1 += added;
        }
        uint64_t *r2_fmasks = (uint64_t *)malloc((size_t)n2_ne1 * wtot * sizeof(uint64_t));

        #pragma omp parallel for schedule(static)
        for (int idx = 0; idx < n2_ne1; idx++) {
            R2Rep r = r2_ne1[idx];
            uint64_t *tmp = (uint64_t *)malloc((size_t)wtot * sizeof(uint64_t));
            expand_orb_to_full(&ct, r2_omasks + (size_t)r.base_idx * ct.ow_total, r2_smasks[r.base_idx], tmp);
            uint8_t perm[MAX_ORB];
            for (int k = 0; k < ff.n_orb; k++) perm[k] = (uint8_t)((r.m2 * k) % ff.n_orb);
            permute_full_mask_B(&ct, tmp, perm, r2_fmasks + (size_t)idx * wtot);
            free(tmp);
        }

        /* Dynamic early-exit threshold: track per-m2 top-50 safely */
        int shared_cutoff = (min_tot < 1000000) ? (min_tot * 3 + 200) : 1000000000;
        if (shared_cutoff < 400) shared_cutoff = 400;

        #pragma omp parallel
        {
            uint64_t *f1 = (uint64_t *)malloc((size_t)wtot * sizeof(uint64_t));
            CandHeap loc_glob;
            cand_init(&loc_glob, 200);
            CandHeap loc_m2[MAX_ORB];
            for (int c = 1; c < n_cop; c++) cand_init(&loc_m2[c], 50);
            uint64_t l_pairs = 0, l_zeros = 0;
            int l_mtot = 1000000000;

            #pragma omp for schedule(dynamic, 8)
            for (int i1 = 0; i1 < n1; i1++) {
                if (timed_out) continue;
                if ((i1 & 15) == 0 && now_sec() > deadline) { timed_out = 1; continue; }
                expand_orb_to_full(&ct, r1_omasks + (size_t)i1 * ct.ow_total, r1_smasks[i1], f1);
                R1Rep rep1 = r1_reps[chunk_start + i1];

                for (int i2 = 0; i2 < n2_ne1; i2++) {
                    const uint64_t *m2 = r2_fmasks + (size_t)i2 * wtot;
                    int cm = r2_m2_cidx[i2];
                    int cap_m2 = (loc_m2[cm].count == loc_m2[cm].cap)
                               ? loc_m2[cm].items[loc_m2[cm].cap - 1].tot : 1000000000;
                    int cut = (cap_m2 > shared_cutoff) ? cap_m2 : shared_cutoff;
                    /* For q <= 9, never skip early so split minima are 100% exact */
                    int use_cut = (q >= 11 && loc_m2[cm].count == loc_m2[cm].cap);

                    int b42 = 0, b33 = 0, b24 = 0;
                    for (int w = 0; w < w42; w++) b42 += __builtin_popcountll(f1[w] & m2[w]);
                    if (use_cut && b42 >= cut) { l_pairs++; continue; }
                    for (int w = w33; w < wtot; w++) b24 += __builtin_popcountll(f1[w] & m2[w]);
                    if (use_cut && b42 + b24 >= cut) { l_pairs++; continue; }
                    for (int w = w42; w < w33; w++) {
                        b33 += __builtin_popcountll(f1[w] & m2[w]);
                        if (use_cut && b42 + b24 + b33 >= cut) break;
                    }
                    int tot = b42 + b33 + b24;
                    l_pairs++;
                    if (tot < l_mtot) l_mtot = tot;
                    if (tot == 0) {
                        l_zeros++;
                        #pragma omp critical(zeros)
                        {
                            if (zero_cnt < zero_cap) {
                                zero_list[zero_cnt++] = (Cand){
                                    rep1.g1_idx, rep1.g2_idx, r2_ne1[i2].a_coset, r2_ne1[i2].b_idx, r2_ne1[i2].m2,
                                    0, 0, 0, 0, 0, 1, 0, 0, 0
                                };
                            }
                        }
                    }
                    if (!use_cut || tot < cut) {
                        Cand c = {rep1.g1_idx, rep1.g2_idx, r2_ne1[i2].a_coset, r2_ne1[i2].b_idx, r2_ne1[i2].m2,
                                  tot, b42, b33, b24, -1, 0, -1, 0, 0};
                        cand_add(&loc_m2[cm], c);
                        cand_add(&loc_glob, c);
                    }
                }
            }
            #pragma omp critical(merge_b)
            {
                pairs_m2ne1 += l_pairs;
                total_zeros_raw += l_zeros;
                if (l_mtot < min_tot) min_tot = l_mtot;
                for (int k = 0; k < loc_glob.count; k++) cand_add(&top_global, loc_glob.items[k]);
                for (int cm = 1; cm < n_cop; cm++)
                    for (int k = 0; k < loc_m2[cm].count; k++) cand_add(&top_per_m2[cm], loc_m2[cm].items[k]);
            }
            free(f1);
            free(loc_glob.items);
            for (int cm = 1; cm < n_cop; cm++) free(loc_m2[cm].items);
        }
        free(r2_ne1); free(r2_m2_cidx); free(r2_fmasks);
    }
    double t_pb = now_sec() - t_pb_start;

    /* ---------- Exact Hitting-Set Evaluation on Top Candidates (overall + per m2) ---------- */
    double t_hs_start = now_sec();
    /* Deduplicate union of top_global (up to 100) and top_per_m2 (up to 30 each) */
    int max_eval = 100 + n_cop * 30;
    Cand *eval_list = (Cand *)malloc((size_t)max_eval * sizeof(Cand));
    int n_eval = 0;
    for (int i = 0; i < top_global.count && i < 100; i++) eval_list[n_eval++] = top_global.items[i];
    for (int cm = 0; cm < n_cop; cm++) {
        for (int i = 0; i < top_per_m2[cm].count && i < 30; i++) {
            Cand c = top_per_m2[cm].items[i];
            int dup = 0;
            for (int j = 0; j < n_eval; j++) {
                if (eval_list[j].g1_idx == c.g1_idx && eval_list[j].g2_idx == c.g2_idx &&
                    eval_list[j].a_coset == c.a_coset && eval_list[j].b_idx == c.b_idx && eval_list[j].m2 == c.m2) {
                    dup = 1; break;
                }
            }
            if (!dup && n_eval < max_eval) eval_list[n_eval++] = c;
        }
    }

    int max_exact_tau = (q <= 9) ? 8 : 7;
    uint64_t hs_node_limit = (q <= 9) ? 5000000ULL : 2000000ULL;

    #pragma omp parallel for schedule(dynamic, 1)
    for (int i = 0; i < n_eval; i++) {
        if (now_sec() > deadline) continue;
        Cand *c = &eval_list[i];
        uint8_t R1_B[MAX_ORB][6], R2_B[MAX_ORB][6];
        build_R1_B(&ff, ff.k_nonzero[c->g1_idx], ff.k_nonzero[c->g2_idx], R1_B);
        build_R2_B(&ff, ff.zeta_pow[c->a_coset], ff.k_nonzero[c->b_idx], 1, R2_B);

        uint64_t *o1 = (uint64_t *)malloc((size_t)ct.ow_total * sizeof(uint64_t));
        uint64_t *o2 = (uint64_t *)malloc((size_t)ct.ow_total * sizeof(uint64_t));
        uint64_t s1 = 0, s2 = 0;
        build_orb_mask(&ff, &ct, 0, R1_B, o1, &s1);
        build_orb_mask(&ff, &ct, 1, R2_B, o2, &s2);

        uint64_t *f1 = (uint64_t *)malloc((size_t)ct.w_total * sizeof(uint64_t));
        uint64_t *f2_base = (uint64_t *)malloc((size_t)ct.w_total * sizeof(uint64_t));
        uint64_t *f2 = (uint64_t *)malloc((size_t)ct.w_total * sizeof(uint64_t));
        expand_orb_to_full(&ct, o1, s1, f1);
        expand_orb_to_full(&ct, o2, s2, f2_base);
        if (c->m2 == 1) {
            memcpy(f2, f2_base, (size_t)ct.w_total * sizeof(uint64_t));
        } else {
            uint8_t perm[MAX_ORB];
            for (int k = 0; k < ff.n_orb; k++) perm[k] = (uint8_t)((c->m2 * k) % ff.n_orb);
            permute_full_mask_B(&ct, f2_base, perm, f2);
        }

        uint32_t dmask32 = 0;
        c->tau = compute_min_hitting_set(&ct, f1, f2, max_exact_tau, hs_node_limit,
                                         &dmask32, &c->exact_tau, &c->greedy_tau, &c->max_col_deg);
        c->del_mask = (uint64_t)dmask32;
        free(o1); free(o2); free(f1); free(f2_base); free(f2);
    }
    double t_hs = now_sec() - t_hs_start;

    int best_tau = 1000000, best_tau_idx = -1;
    for (int i = 0; i < n_eval; i++) {
        if (eval_list[i].tau < 0) continue;
        int better = 0;
        if (best_tau_idx < 0 || eval_list[i].tau < best_tau) {
            better = 1;
        } else if (eval_list[i].tau == best_tau) {
            const Cand *a = &eval_list[i], *b = &eval_list[best_tau_idx];
            if (a->tot != b->tot) better = (a->tot < b->tot);
            else if (a->m2 != b->m2) better = (a->m2 < b->m2);
            else if (a->g1_idx != b->g1_idx) better = (a->g1_idx < b->g1_idx);
            else if (a->g2_idx != b->g2_idx) better = (a->g2_idx < b->g2_idx);
            else if (a->a_coset != b->a_coset) better = (a->a_coset < b->a_coset);
            else if (a->b_idx != b->b_idx) better = (a->b_idx < b->b_idx);
        }
        if (better) {
            best_tau = eval_list[i].tau;
            best_tau_idx = i;
        }
    }
    int best_kpunc = (best_tau_idx >= 0) ? (ff.k_full - best_tau) : 0;
    double t_tot = now_sec() - t0;

    printf("SCAN q=%d (k=%d, crit=%d, orbits=%d, short=%d, sym=%d, chunk=[%d,%d)/%d, m2_mode=%d): status=%s\n",
           q, ff.k_full, ct.n_total, ct.n_orbits, ct.n_short, use_sym,
           chunk_start, chunk_end, n1_all, m2_mode, timed_out ? "TIMEOUT" : "COMPLETE");
    printf("  times: r1=%.3fs r2=%.3fs passA(m2=1)=%.3fs passB(m2!=1)=%.3fs hitset(%d)=%.3fs total=%.3fs\n",
           t_r1, t_r2, t_pa, t_pb, n_eval, t_hs, t_tot);
    printf("  pairs: m2eq1=%llu m2ne1=%llu total=%llu, zero_hits=%llu (stored=%d)\n",
           (unsigned long long)pairs_m2eq1, (unsigned long long)pairs_m2ne1,
           (unsigned long long)(pairs_m2eq1 + pairs_m2ne1),
           (unsigned long long)total_zeros_raw, zero_cnt);
    if (top_global.count > 0) {
        Cand b = top_global.items[0];
        KElem g1 = ff.k_nonzero[b.g1_idx], g2 = ff.k_nonzero[b.g2_idx];
        KElem al = ff.zeta_pow[b.a_coset], be = ff.k_nonzero[b.b_idx];
        printf("  min_unc=%d (42=%d, 33=%d, 24=%d) at g1=(%d,%d) g2=(%d,%d) alpha=(%d,%d) beta=(%d,%d) m2=%d\n",
               b.tot, b.b42, b.b33, b.b24, g1.a, g1.b, g2.a, g2.b, al.a, al.b, be.a, be.b, b.m2);
    }
    if (best_tau_idx >= 0) {
        Cand b = eval_list[best_tau_idx];
        KElem g1 = ff.k_nonzero[b.g1_idx], g2 = ff.k_nonzero[b.g2_idx];
        KElem al = ff.zeta_pow[b.a_coset], be = ff.k_nonzero[b.b_idx];
        printf("  best_tau=%d (exact=%d, greedy=%d, k_punc=%d/%d, from unc=%d [42=%d,33=%d,24=%d], del_mask=0x%llx) at g1=(%d,%d) g2=(%d,%d) alpha=(%d,%d) beta=(%d,%d) m2=%d\n",
               b.tau, b.exact_tau, b.greedy_tau, best_kpunc, ff.k_full, b.tot, b.b42, b.b33, b.b24,
               (unsigned long long)b.del_mask,
               g1.a, g1.b, g2.a, g2.b, al.a, al.b, be.a, be.b, b.m2);
    }
    for (int cm = 0; cm < n_cop; cm++) {
        if (top_per_m2[cm].count > 0) {
            Cand b = top_per_m2[cm].items[0];
            printf("    m2=%d: min_unc=%d (42=%d, 33=%d, 24=%d)\n", coprimes[cm], b.tot, b.b42, b.b33, b.b24);
        }
    }

    /* Save hit CPHF JSON if requested and best_kpunc > 0 */
    if (save_hit_dir && best_tau_idx >= 0) {
        char path[512];
        snprintf(path, sizeof(path), "%s/cphf_q%d_k%d_punc.json", save_hit_dir, q, best_kpunc);
        save_cphf_hit_json(path, &ff, R1_A, R2_A, &eval_list[best_tau_idx]);
        printf("  SAVED BEST CPHF -> %s\n", path);
    }

    /* Write compact summary + candidates JSON if requested */
    if (out_json) {
        FILE *fp = fopen(out_json, "w");
        if (fp) {
            fprintf(fp, "{\n  \"q\": %d, \"k_full\": %d, \"use_sym\": %d, \"m2_mode\": %d, "
                        "\"chunk\": [%d, %d, %d], \"status\": \"%s\",\n",
                    q, ff.k_full, use_sym, m2_mode, chunk_start, chunk_end, n1_all,
                    timed_out ? "TIMEOUT" : "COMPLETE");
            fprintf(fp, "  \"pairs_m2eq1\": %llu, \"pairs_m2ne1\": %llu, \"zero_hits\": %llu,\n",
                    (unsigned long long)pairs_m2eq1, (unsigned long long)pairs_m2ne1,
                    (unsigned long long)total_zeros_raw);
            fprintf(fp, "  \"times\": {\"r1\": %.4f, \"r2\": %.4f, \"passA\": %.4f, \"passB\": %.4f, \"hitset\": %.4f, \"total\": %.4f},\n",
                    t_r1, t_r2, t_pa, t_pb, t_hs, t_tot);
            fprintf(fp, "  \"min_unc\": %d, \"best_tau\": %d, \"best_kpunc\": %d,\n",
                    top_global.count > 0 ? top_global.items[0].tot : -1,
                    best_tau_idx >= 0 ? best_tau : -1, best_kpunc);
            fprintf(fp, "  \"zeros\": [\n");
            for (int i = 0; i < zero_cnt; i++) {
                Cand z = zero_list[i];
                KElem g1 = ff.k_nonzero[z.g1_idx], g2 = ff.k_nonzero[z.g2_idx];
                KElem al = ff.zeta_pow[z.a_coset], be = ff.k_nonzero[z.b_idx];
                fprintf(fp, "    {\"g1\":[%d,%d],\"g2\":[%d,%d],\"alpha\":[%d,%d],\"beta\":[%d,%d],\"m2\":%d}%s\n",
                        g1.a, g1.b, g2.a, g2.b, al.a, al.b, be.a, be.b, z.m2, (i + 1 < zero_cnt) ? "," : "");
            }
            fprintf(fp, "  ],\n  \"evaluated\": [\n");
            for (int i = 0; i < n_eval; i++) {
                Cand c = eval_list[i];
                KElem g1 = ff.k_nonzero[c.g1_idx], g2 = ff.k_nonzero[c.g2_idx];
                KElem al = ff.zeta_pow[c.a_coset], be = ff.k_nonzero[c.b_idx];
                fprintf(fp, "    {\"g1\":[%d,%d],\"g2\":[%d,%d],\"alpha\":[%d,%d],\"beta\":[%d,%d],\"m2\":%d,"
                            "\"unc\":%d,\"b42\":%d,\"b33\":%d,\"b24\":%d,\"tau\":%d,\"exact_tau\":%d,"
                            "\"greedy_tau\":%d,\"max_col_deg\":%d,\"del_mask\":%llu}%s\n",
                        g1.a, g1.b, g2.a, g2.b, al.a, al.b, be.a, be.b, c.m2,
                        c.tot, c.b42, c.b33, c.b24, c.tau, c.exact_tau, c.greedy_tau,
                        c.max_col_deg, (unsigned long long)c.del_mask, (i + 1 < n_eval) ? "," : "");
            }
            fprintf(fp, "  ]\n}\n");
            fclose(fp);
        }
    }

    if (jsonl_path) {
        FILE *fp = fopen(jsonl_path, "a");
        if (fp) {
            fprintf(fp, "{\"q\":%d,\"chunk\":[%d,%d,%d],\"m2_mode\":%d,\"status\":\"%s\",\"min_unc\":%d,"
                        "\"best_tau\":%d,\"best_kpunc\":%d,\"zeros\":%llu,\"time\":%.3f}\n",
                    q, chunk_start, chunk_end, n1_all, m2_mode, timed_out ? "TIMEOUT" : "COMPLETE",
                    top_global.count > 0 ? top_global.items[0].tot : -1,
                    best_tau_idx >= 0 ? best_tau : -1, best_kpunc,
                    (unsigned long long)total_zeros_raw, t_tot);
            fclose(fp);
        }
    }

    free(r1_reps); free(r1_omasks); free(r1_smasks); free(r1_deps);
    free(r2_omasks); free(r2_smasks); free(r2_deps);
    free(top_global.items);
    for (int c = 0; c < n_cop; c++) free(top_per_m2[c].items);
    free(zero_list); free(eval_list);
    free_crit_table(&ct);
}

/* ---------- Benchmark Mode (AP 2.1) ---------- */
static void run_bench(int q, int n_threads) {
    omp_set_num_threads(n_threads);
    FF ff;
    ff_init(&ff, q);
    uint8_t R1_A[MAX_ORB][6], R2_A[MAX_ORB][6];
    build_R1_A(&ff, R1_A);
    build_R2_A(&ff, R2_A);

    double t0 = now_sec();
    CritTable ct;
    init_crit_table(&ct, &ff, R1_A, R2_A);
    double t_init = now_sec() - t0;

    R1Rep *r1_reps = (R1Rep *)malloc((size_t)(ff.k_order * ff.k_order) * sizeof(R1Rep));
    int n1_sym = build_r1_reps(&ff, 1, r1_reps);
    int n2_base = ff.n_orb * ff.k_order;
    int coprimes[MAX_ORB], n_cop = 0;
    for (int m = 1; m < ff.n_orb; m++) if (gcd_int(m, ff.n_orb) == 1) coprimes[n_cop++] = m;
    int n2_ne1 = 0;
    R2Rep *tmp_r2 = (R2Rep *)malloc((size_t)n2_base * sizeof(R2Rep));
    for (int cm = 1; cm < n_cop; cm++) n2_ne1 += build_r2_reps_for_m2(&ff, coprimes[cm], 1, tmp_r2);
    free(tmp_r2);

    /* Benchmark building 32 Row-1 orbit masks in parallel */
    int sample_n1 = 32;
    uint64_t *om = (uint64_t *)malloc((size_t)sample_n1 * ct.ow_total * sizeof(uint64_t));
    uint64_t sm[32];
    double tb1 = now_sec();
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < sample_n1; i++) {
        uint8_t B[MAX_ORB][6];
        build_R1_B(&ff, ff.k_nonzero[r1_reps[i].g1_idx], ff.k_nonzero[r1_reps[i].g2_idx], B);
        build_orb_mask(&ff, &ct, 0, B, om + (size_t)i * ct.ow_total, &sm[i]);
    }
    double dt_r1 = (now_sec() - tb1) / sample_n1;

    /* Benchmark m2=1 orbit intersection: 32 x 2000 pairs */
    double tb2 = now_sec();
    volatile int sink = 0;
    #pragma omp parallel for reduction(+:sink)
    for (int i = 0; i < sample_n1; i++) {
        const uint64_t *m1 = om + (size_t)i * ct.ow_total;
        for (int j = 0; j < 2000; j++) {
            const uint64_t *m2 = om + (size_t)(j % sample_n1) * ct.ow_total;
            int s = 0;
            for (int w = 0; w < ct.ow_total; w++) s += __builtin_popcountll(m1[w] & m2[w]);
            sink += s;
        }
    }
    double dt_pair_a = (now_sec() - tb2) / (sample_n1 * 2000.0);

    double est_r1 = dt_r1 * n1_sym;
    double est_r2 = dt_r1 * n2_base;
    double est_pa = dt_pair_a * (double)n1_sym * (double)n2_base;
    double est_pb_full = est_pa * ((double)n2_ne1 / (double)n2_base) * ((double)ct.w_total / (double)ct.ow_total);

    printf("BENCH q=%d (k=%d, crit=%d, orbits=%d, short=%d, ow=%d, fw=%d, threads=%d):\n",
           q, ff.k_full, ct.n_total, ct.n_orbits, ct.n_short, ct.ow_total, ct.w_total, n_threads);
    printf("  init=%.3fs | n1_raw=%d -> n1_sym=%d | n2_m2eq1=%d | n2_m2ne1_sym=%d (n_cop=%d)\n",
           t_init, ff.k_order * ff.k_order, n1_sym, n2_base, n2_ne1, n_cop);
    printf("  1 R1 build: %.4f ms (est all R1=%.2fs, all R2=%.2fs)\n", dt_r1 * 1e3, est_r1, est_r2);
    printf("  est Pass A (m2=1, %llu pairs): %.2fs\n", (unsigned long long)n1_sym * n2_base, est_pa);
    printf("  est Pass B (m2!=1, %llu pairs, no early-exit): %.2fs (with early-exit ~%.2fs)\n",
           (unsigned long long)n1_sym * n2_ne1, est_pb_full, est_pb_full * 0.2);

    free(om); free(r1_reps); free_crit_table(&ct);
}

/* ============================================================================
 * MEMORY-LEAN ORBIT-ONLY ENGINE FOR q <= 19 (Invariant Slice + Control Samples)
 * Supports q in {5, 7, 8, 9, 11, 13, 17, 19} (k <= 40, uint64_t bitmasks)
 * ============================================================================ */

#define MAX_SHORT_ORB 128

typedef struct {
    uint8_t a_cnt;       /* 4, 3, or 2 */
    uint8_t len;         /* orbit length (divides n_orb) */
    uint16_t ca_id;      /* canonical A-orbit index */
    uint16_t b_id;       /* B combination index */
} OrbitRep;

typedef struct {
    int n_orb;
    /* Canonical A-orbits of sizes 2, 3, 4 (only ~310 total at q=19!) */
    int nCA2, nCA3, nCA4;
    uint8_t ca2[64][2], ca3[128][3], ca4[512][4];
    uint8_t ca2_stab[64], ca3_stab[128], ca4_stab[512];
    uint8_t N1_4[512][2][6], N1_3[128][3][6], N1_2[64][4][6];
    uint8_t N2_4[512][2][6], N2_3[128][3][6], N2_2[64][4][6];

    /* All B combinations of sizes 2, 3, 4 */
    int nB2, nB3, nB4;
    uint8_t combB2[200][2];
    uint8_t combB3[1200][3];
    uint8_t combB4[5000][4];
    uint32_t maskB2[200], maskB3[1200], maskB4[5000];

    /* Z_n orbits */
    int n_orbits;
    OrbitRep *orbs;
    int nf_42, nf_33, nf_24;
    int ow_42_end, ow_33_end, ow_total;
    int *orb_bit; /* >= 0: bit in full-length mask; < 0: -(short_idx + 1) */
    int *bit_to_oid; /* inverse map for full-length bits -> oid */
    int n_short;
    uint8_t short_acnt[MAX_SHORT_ORB];
    uint8_t short_len[MAX_SHORT_ORB];
    int short_oid[MAX_SHORT_ORB];
} OrbitTable;

static uint32_t shift_mask_n(uint32_t m, int sh, int n) {
    uint32_t res = 0;
    while (m) {
        int b = __builtin_ctz(m);
        res |= 1U << ((b + sh) % n);
        m &= m - 1;
    }
    return res;
}

static void init_orbit_table(OrbitTable *ot, const FF *ff,
                             const uint8_t R1_A[MAX_ORB][6], const uint8_t R2_A[MAX_ORB][6]) {
    memset(ot, 0, sizeof(*ot));
    int n = ff->n_orb;
    ot->n_orb = n;

    /* Enumerate all B combinations of sizes 2, 3, 4 */
    ot->nB2 = 0;
    for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++) {
        ot->combB2[ot->nB2][0] = (uint8_t)i; ot->combB2[ot->nB2][1] = (uint8_t)j;
        ot->maskB2[ot->nB2] = (1U << i) | (1U << j);
        ot->nB2++;
    }
    ot->nB3 = 0;
    for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
    for (int k = j + 1; k < n; k++) {
        ot->combB3[ot->nB3][0] = (uint8_t)i; ot->combB3[ot->nB3][1] = (uint8_t)j; ot->combB3[ot->nB3][2] = (uint8_t)k;
        ot->maskB3[ot->nB3] = (1U << i) | (1U << j) | (1U << k);
        ot->nB3++;
    }
    ot->nB4 = 0;
    for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
    for (int k = j + 1; k < n; k++)
    for (int l = k + 1; l < n; l++) {
        ot->combB4[ot->nB4][0] = (uint8_t)i; ot->combB4[ot->nB4][1] = (uint8_t)j;
        ot->combB4[ot->nB4][2] = (uint8_t)k; ot->combB4[ot->nB4][3] = (uint8_t)l;
        ot->maskB4[ot->nB4] = (1U << i) | (1U << j) | (1U << k) | (1U << l);
        ot->nB4++;
    }

    /* Extract canonical A-orbits (smallest bitmask among all shifts sh=0..n-1) */
    uint8_t mat[4][6], Ntmp[4][6];
    ot->nCA2 = 0;
    for (int id = 0; id < ot->nB2; id++) {
        uint32_t m = ot->maskB2[id], min_m = m;
        int period = n;
        for (int sh = 1; sh < n; sh++) {
            uint32_t ms = shift_mask_n(m, sh, n);
            if (ms < min_m) min_m = ms;
            if (ms == m && period == n) period = sh;
        }
        if (min_m == m) {
            int cid = ot->nCA2++;
            memcpy(ot->ca2[cid], ot->combB2[id], 2);
            ot->ca2_stab[cid] = (uint8_t)period;
            for (int r = 0; r < 2; r++) memcpy(mat[r], R1_A[ot->ca2[cid][r]], 6);
            compute_nullspace(ff, 2, mat, Ntmp); memcpy(ot->N1_2[cid], Ntmp, 24);
            for (int r = 0; r < 2; r++) memcpy(mat[r], R2_A[ot->ca2[cid][r]], 6);
            compute_nullspace(ff, 2, mat, Ntmp); memcpy(ot->N2_2[cid], Ntmp, 24);
        }
    }
    ot->nCA3 = 0;
    for (int id = 0; id < ot->nB3; id++) {
        uint32_t m = ot->maskB3[id], min_m = m;
        int period = n;
        for (int sh = 1; sh < n; sh++) {
            uint32_t ms = shift_mask_n(m, sh, n);
            if (ms < min_m) min_m = ms;
            if (ms == m && period == n) period = sh;
        }
        if (min_m == m) {
            int cid = ot->nCA3++;
            memcpy(ot->ca3[cid], ot->combB3[id], 3);
            ot->ca3_stab[cid] = (uint8_t)period;
            for (int r = 0; r < 3; r++) memcpy(mat[r], R1_A[ot->ca3[cid][r]], 6);
            compute_nullspace(ff, 3, mat, Ntmp); memcpy(ot->N1_3[cid], Ntmp, 18);
            for (int r = 0; r < 3; r++) memcpy(mat[r], R2_A[ot->ca3[cid][r]], 6);
            compute_nullspace(ff, 3, mat, Ntmp); memcpy(ot->N2_3[cid], Ntmp, 18);
        }
    }
    ot->nCA4 = 0;
    for (int id = 0; id < ot->nB4; id++) {
        uint32_t m = ot->maskB4[id], min_m = m;
        int period = n;
        for (int sh = 1; sh < n; sh++) {
            uint32_t ms = shift_mask_n(m, sh, n);
            if (ms < min_m) min_m = ms;
            if (ms == m && period == n) period = sh;
        }
        if (min_m == m) {
            int cid = ot->nCA4++;
            memcpy(ot->ca4[cid], ot->combB4[id], 4);
            ot->ca4_stab[cid] = (uint8_t)period;
            for (int r = 0; r < 4; r++) memcpy(mat[r], R1_A[ot->ca4[cid][r]], 6);
            compute_nullspace(ff, 4, mat, Ntmp); memcpy(ot->N1_4[cid], Ntmp, 12);
            for (int r = 0; r < 4; r++) memcpy(mat[r], R2_A[ot->ca4[cid][r]], 6);
            compute_nullspace(ff, 4, mat, Ntmp); memcpy(ot->N2_4[cid], Ntmp, 12);
        }
    }

    /* Count and enumerate Z_n orbits directly */
    int cap_orbs = ot->nCA4 * ot->nB2 + ot->nCA3 * ot->nB3 + ot->nCA2 * ot->nB4;
    ot->orbs = (OrbitRep *)malloc((size_t)cap_orbs * sizeof(OrbitRep));
    ot->n_orbits = 0;

    /* (4,2) */
    for (int ca = 0; ca < ot->nCA4; ca++) {
        int p = ot->ca4_stab[ca];
        for (int ib = 0; ib < ot->nB2; ib++) {
            if (p == n) {
                ot->orbs[ot->n_orbits++] = (OrbitRep){4, (uint8_t)n, (uint16_t)ca, (uint16_t)ib};
            } else {
                uint32_t mb = ot->maskB2[ib], min_mb = mb;
                int olen = n;
                for (int sh = p; sh < n; sh += p) {
                    uint32_t mbs = shift_mask_n(mb, sh, n);
                    if (mbs < min_mb) min_mb = mbs;
                    if (mbs == mb && olen == n) olen = sh;
                }
                if (min_mb == mb)
                    ot->orbs[ot->n_orbits++] = (OrbitRep){4, (uint8_t)olen, (uint16_t)ca, (uint16_t)ib};
            }
        }
    }
    /* (3,3) */
    for (int ca = 0; ca < ot->nCA3; ca++) {
        int p = ot->ca3_stab[ca];
        for (int ib = 0; ib < ot->nB3; ib++) {
            if (p == n) {
                ot->orbs[ot->n_orbits++] = (OrbitRep){3, (uint8_t)n, (uint16_t)ca, (uint16_t)ib};
            } else {
                uint32_t mb = ot->maskB3[ib], min_mb = mb;
                int olen = n;
                for (int sh = p; sh < n; sh += p) {
                    uint32_t mbs = shift_mask_n(mb, sh, n);
                    if (mbs < min_mb) min_mb = mbs;
                    if (mbs == mb && olen == n) olen = sh;
                }
                if (min_mb == mb)
                    ot->orbs[ot->n_orbits++] = (OrbitRep){3, (uint8_t)olen, (uint16_t)ca, (uint16_t)ib};
            }
        }
    }
    /* (2,4) */
    for (int ca = 0; ca < ot->nCA2; ca++) {
        int p = ot->ca2_stab[ca];
        for (int ib = 0; ib < ot->nB4; ib++) {
            if (p == n) {
                ot->orbs[ot->n_orbits++] = (OrbitRep){2, (uint8_t)n, (uint16_t)ca, (uint16_t)ib};
            } else {
                uint32_t mb = ot->maskB4[ib], min_mb = mb;
                int olen = n;
                for (int sh = p; sh < n; sh += p) {
                    uint32_t mbs = shift_mask_n(mb, sh, n);
                    if (mbs < min_mb) min_mb = mbs;
                    if (mbs == mb && olen == n) olen = sh;
                }
                if (min_mb == mb)
                    ot->orbs[ot->n_orbits++] = (OrbitRep){2, (uint8_t)olen, (uint16_t)ca, (uint16_t)ib};
            }
        }
    }

    ot->nf_42 = ot->nf_33 = ot->nf_24 = ot->n_short = 0;
    for (int oid = 0; oid < ot->n_orbits; oid++) {
        if (ot->orbs[oid].len == n) {
            if (ot->orbs[oid].a_cnt == 4) ot->nf_42++;
            else if (ot->orbs[oid].a_cnt == 3) ot->nf_33++;
            else ot->nf_24++;
        } else {
            ot->n_short++;
        }
    }
    if (ot->n_short > MAX_SHORT_ORB) {
        fprintf(stderr, "FATAL: n_short=%d > %d\n", ot->n_short, MAX_SHORT_ORB);
        exit(1);
    }
    int ow42 = (ot->nf_42 + 63) / 64, ow33 = (ot->nf_33 + 63) / 64, ow24 = (ot->nf_24 + 63) / 64;
    ot->ow_42_end = ow42;
    ot->ow_33_end = ow42 + ow33;
    ot->ow_total = ow42 + ow33 + ow24;

    ot->orb_bit = (int *)malloc((size_t)ot->n_orbits * sizeof(int));
    ot->bit_to_oid = (int *)malloc((size_t)(ot->ow_total * 64) * sizeof(int));
    for (int i = 0; i < ot->ow_total * 64; i++) ot->bit_to_oid[i] = -1;

    int p42 = 0, p33 = ow42 * 64, p24 = (ow42 + ow33) * 64, ps = 0;
    for (int oid = 0; oid < ot->n_orbits; oid++) {
        if (ot->orbs[oid].len == n) {
            int bp = (ot->orbs[oid].a_cnt == 4) ? p42++
                   : (ot->orbs[oid].a_cnt == 3) ? p33++ : p24++;
            ot->orb_bit[oid] = bp;
            ot->bit_to_oid[bp] = oid;
        } else {
            ot->short_acnt[ps] = ot->orbs[oid].a_cnt;
            ot->short_len[ps] = ot->orbs[oid].len;
            ot->short_oid[ps] = oid;
            ot->orb_bit[oid] = -(ps + 1);
            ps++;
        }
    }
}

static void free_orbit_table(OrbitTable *ot) {
    free(ot->orbs); free(ot->orb_bit); free(ot->bit_to_oid);
}

/* Precompute N_A * B[k] for one canonical A and all k in 0..n-1 for massive speedup! */
static int build_orb_mask_fast(const FF *ff, const OrbitTable *ot, int is_row2,
                               const uint8_t B[MAX_ORB][6], uint64_t *omask, uint64_t smask[2]) {
    memset(omask, 0, (size_t)ot->ow_total * sizeof(uint64_t));
    smask[0] = smask[1] = 0;
    int n = ot->n_orb;
    int dep = 0;

    /* Precompute projections for all canonical A (tiny: <= 512 x 20 x 4 bytes!) */
    uint8_t P4[512][MAX_ORB][2];
    uint8_t P3[128][MAX_ORB][3];
    uint8_t P2[64][MAX_ORB][4];

    for (int ca = 0; ca < ot->nCA4; ca++) {
        const uint8_t (*N)[6] = is_row2 ? ot->N2_4[ca] : ot->N1_4[ca];
        for (int k = 0; k < n; k++)
            for (int c = 0; c < 2; c++) {
                uint8_t acc = 0;
                for (int j = 0; j < 6; j++) acc = ff->add[acc][ff->mul[N[c][j]][B[k][j]]];
                P4[ca][k][c] = acc;
            }
    }
    for (int ca = 0; ca < ot->nCA3; ca++) {
        const uint8_t (*N)[6] = is_row2 ? ot->N2_3[ca] : ot->N1_3[ca];
        for (int k = 0; k < n; k++)
            for (int c = 0; c < 3; c++) {
                uint8_t acc = 0;
                for (int j = 0; j < 6; j++) acc = ff->add[acc][ff->mul[N[c][j]][B[k][j]]];
                P3[ca][k][c] = acc;
            }
    }
    for (int ca = 0; ca < ot->nCA2; ca++) {
        const uint8_t (*N)[6] = is_row2 ? ot->N2_2[ca] : ot->N1_2[ca];
        for (int k = 0; k < n; k++)
            for (int c = 0; c < 4; c++) {
                uint8_t acc = 0;
                for (int j = 0; j < 6; j++) acc = ff->add[acc][ff->mul[N[c][j]][B[k][j]]];
                P2[ca][k][c] = acc;
            }
    }

    for (int oid = 0; oid < ot->n_orbits; oid++) {
        const OrbitRep *o = &ot->orbs[oid];
        int ok;
        if (o->a_cnt == 4) {
            const uint8_t *bc = ot->combB2[o->b_id];
            uint8_t m[2][2] = {
                {P4[o->ca_id][bc[0]][0], P4[o->ca_id][bc[0]][1]},
                {P4[o->ca_id][bc[1]][0], P4[o->ca_id][bc[1]][1]}
            };
            ok = det2_nonzero(ff, m);
        } else if (o->a_cnt == 3) {
            const uint8_t *bc = ot->combB3[o->b_id];
            uint8_t m[3][3];
            for (int r = 0; r < 3; r++) memcpy(m[r], P3[o->ca_id][bc[r]], 3);
            ok = det3_nonzero(ff, m);
        } else {
            const uint8_t *bc = ot->combB4[o->b_id];
            uint8_t m[4][4];
            for (int r = 0; r < 4; r++) memcpy(m[r], P2[o->ca_id][bc[r]], 4);
            ok = rank4_full(ff, m);
        }
        if (!ok) {
            dep += o->len;
            int ob = ot->orb_bit[oid];
            if (ob >= 0) omask[ob >> 6] |= 1ULL << (ob & 63);
            else {
                int s = -(ob + 1);
                smask[s >> 6] |= 1ULL << (s & 63);
            }
        }
    }
    return dep;
}

/* Extract exact uncovered 6-tuple uint64_t hyperedges directly from (o1 & o2, s1 & s2) */
static int extract_edges_from_orbits(const OrbitTable *ot,
                                     const uint64_t *o1, const uint64_t s1[2],
                                     const uint64_t *o2, const uint64_t s2[2],
                                     uint64_t *edges, int max_edges) {
    int n = ot->n_orb;
    int ne = 0;
    /* Helper lambda-style block via array of uncovered oids */
    int cap_oids = 4096;
    int *oids = (int *)malloc((size_t)cap_oids * sizeof(int));
    int n_oids = 0;

    for (int w = 0; w < ot->ow_total; w++) {
        uint64_t x = o1[w] & o2[w];
        while (x) {
            int b = __builtin_ctzll(x);
            x &= x - 1;
            int oid = ot->bit_to_oid[(w << 6) | b];
            if (n_oids < cap_oids) oids[n_oids++] = oid;
        }
    }
    for (int sw = 0; sw < 2; sw++) {
        uint64_t x = s1[sw] & s2[sw];
        while (x) {
            int b = __builtin_ctzll(x);
            x &= x - 1;
            int s = (sw << 6) | b;
            if (n_oids < cap_oids) oids[n_oids++] = ot->short_oid[s];
        }
    }

    for (int i = 0; i < n_oids; i++) {
        const OrbitRep *o = &ot->orbs[oids[i]];
        uint32_t mA = 0, mB = 0;
        if (o->a_cnt == 4) {
            for (int r = 0; r < 4; r++) mA |= 1U << ot->ca4[o->ca_id][r];
            mB = ot->maskB2[o->b_id];
        } else if (o->a_cnt == 3) {
            for (int r = 0; r < 3; r++) mA |= 1U << ot->ca3[o->ca_id][r];
            mB = ot->maskB3[o->b_id];
        } else {
            for (int r = 0; r < 2; r++) mA |= 1U << ot->ca2[o->ca_id][r];
            mB = ot->maskB4[o->b_id];
        }
        for (int sh = 0; sh < o->len && ne < max_edges; sh++) {
            uint64_t eA = (uint64_t)shift_mask_n(mA, sh, n);
            uint64_t eB = (uint64_t)shift_mask_n(mB, sh, n);
            edges[ne++] = eA | (eB << n);
        }
    }
    free(oids);
    return ne;
}

/* ---------- Upgraded uint64_t Exact Hitting-Set Solver (forbid + unit propagation) ---------- */
typedef struct {
    int n_edges;
    int k_cols;
    uint64_t *edges;
    int target_depth;
    int found;
    uint64_t sol_mask;
    uint64_t nodes;
    uint64_t node_limit;
    int aborted;
} Hit64State;

static void hit64_dfs(Hit64State *hs, uint64_t chosen, uint64_t forbid, int depth) {
    if (hs->found || hs->aborted) return;
    if (++hs->nodes > hs->node_limit) { hs->aborted = 1; return; }

    /* Unit propagation loop: if an uncovered edge has only 1 allowed vertex, force it! */
    while (1) {
        int rem_unc = 0;
        int deg[MAX_K];
        memset(deg, 0, (size_t)hs->k_cols * sizeof(int));
        uint64_t pack_used = 0;
        int pack_lb = 0;
        int best_e = -1, best_sz = 100;
        uint64_t forced = 0;

        for (int i = 0; i < hs->n_edges; i++) {
            uint64_t e = hs->edges[i];
            if ((e & chosen) != 0) continue;
            rem_unc++;
            uint64_t avail = e & ~forbid;
            if (avail == 0) return; /* Dead branch: uncovered edge has no allowed vertex */
            int sz = __builtin_popcountll(avail);
            if (sz == 1) { forced = avail; break; }
            if (sz < best_sz) { best_sz = sz; best_e = i; }
            if ((e & pack_used) == 0) { pack_used |= e; pack_lb++; }
            uint64_t tmp = avail;
            while (tmp) {
                int v = __builtin_ctzll(tmp);
                deg[v]++;
                tmp &= tmp - 1;
            }
        }
        if (forced) {
            if (depth >= hs->target_depth) return;
            chosen |= forced;
            depth++;
            continue;
        }
        if (rem_unc == 0) {
            hs->found = 1;
            hs->sol_mask = chosen;
            return;
        }
        int rem_slots = hs->target_depth - depth;
        if (rem_slots <= 0 || pack_lb > rem_slots) return;

        int max_deg = 0;
        for (int v = 0; v < hs->k_cols; v++) if (deg[v] > max_deg) max_deg = deg[v];
        if (max_deg == 0 || max_deg * rem_slots < rem_unc) return;

        if (rem_slots == 1) {
            for (int v = 0; v < hs->k_cols; v++) {
                if (deg[v] == rem_unc) {
                    hs->found = 1;
                    hs->sol_mask = chosen | (1ULL << v);
                    return;
                }
            }
            return;
        }

        /* Among edges of size == best_sz, pick one with smallest total degree (tightest) */
        int best_score = 1000000000;
        int checked = 0;
        for (int i = 0; i < hs->n_edges && checked < 64; i++) {
            uint64_t e = hs->edges[i];
            if ((e & chosen) != 0) continue;
            uint64_t avail = e & ~forbid;
            if (__builtin_popcountll(avail) != best_sz) continue;
            checked++;
            int sc = 0;
            uint64_t tmp = avail;
            while (tmp) { int v = __builtin_ctzll(tmp); sc += deg[v]; tmp &= tmp - 1; }
            if (sc < best_score) { best_score = sc; best_e = i; }
        }

        uint64_t avail = hs->edges[best_e] & ~forbid;
        int verts[6], vdeg[6], nv = 0;
        while (avail) {
            int v = __builtin_ctzll(avail);
            verts[nv] = v; vdeg[nv] = deg[v]; nv++;
            avail &= avail - 1;
        }
        for (int i = 0; i < nv; i++)
            for (int j = i + 1; j < nv; j++)
                if (vdeg[j] > vdeg[i]) {
                    int tv = verts[i]; verts[i] = verts[j]; verts[j] = tv;
                    int td = vdeg[i]; vdeg[i] = vdeg[j]; vdeg[j] = td;
                }

        uint64_t cur_forbid = forbid;
        for (int j = 0; j < nv; j++) {
            hit64_dfs(hs, chosen | (1ULL << verts[j]), cur_forbid, depth + 1);
            if (hs->found || hs->aborted) return;
            cur_forbid |= 1ULL << verts[j];
        }
        return;
    }
}

static int compute_min_hitting_set_u64(int k_cols, uint64_t *edges, int n_edges,
                                       int max_exact_tau, uint64_t node_limit,
                                       uint64_t *out_del_mask, int *out_exact,
                                       int *out_greedy_tau, int *out_max_col_deg) {
    int col_deg[MAX_K];
    memset(col_deg, 0, sizeof(col_deg));
    for (int i = 0; i < n_edges; i++) {
        uint64_t tmp = edges[i];
        while (tmp) { int v = __builtin_ctzll(tmp); col_deg[v]++; tmp &= tmp - 1; }
    }
    int max_cd = 0;
    for (int v = 0; v < k_cols; v++) if (col_deg[v] > max_cd) max_cd = col_deg[v];
    if (out_max_col_deg) *out_max_col_deg = max_cd;
    if (n_edges == 0) {
        if (out_del_mask) *out_del_mask = 0;
        if (out_exact) *out_exact = 1;
        if (out_greedy_tau) *out_greedy_tau = 0;
        return 0;
    }

    /* Greedy upper bound */
    uint64_t gmask = 0;
    int gdel = 0;
    while (1) {
        int best_v = -1, best_d = 0;
        for (int v = 0; v < k_cols; v++) {
            if ((gmask >> v) & 1ULL) continue;
            int d = 0;
            for (int i = 0; i < n_edges; i++)
                if ((edges[i] & gmask) == 0 && ((edges[i] >> v) & 1ULL)) d++;
            if (d > best_d) { best_d = d; best_v = v; }
        }
        if (best_d == 0) break;
        gmask |= 1ULL << best_v;
        gdel++;
    }
    if (out_greedy_tau) *out_greedy_tau = gdel;

    int lb = (n_edges + max_cd - 1) / max_cd;
    if (lb >= gdel) {
        if (out_del_mask) *out_del_mask = gmask;
        if (out_exact) *out_exact = 1;
        return gdel;
    }
    int cap = (gdel - 1 < max_exact_tau) ? (gdel - 1) : max_exact_tau;
    int n_orb = k_cols / 2;
    uint64_t maskA = (1ULL << n_orb) - 1ULL;
    for (int d = lb; d <= cap; d++) {
        Hit64State hs = {n_edges, k_cols, edges, d, 0, 0, 0, node_limit, 0};
        /* Exact Z_{n_orb} cyclic symmetry breaking:
         * Case 1: H intersects A -> wlog 0 in H.
         * Case 2: H disjoint from A -> H subset B, wlog n_orb in H. */
        hit64_dfs(&hs, 1ULL << 0, 0ULL, 1);
        if (!hs.found && !hs.aborted) {
            hit64_dfs(&hs, 1ULL << n_orb, maskA, 1);
        }
        if (hs.found) {
            if (out_del_mask) *out_del_mask = hs.sol_mask;
            if (out_exact) *out_exact = 1;
            return d;
        }
        if (hs.aborted) {
            if (out_del_mask) *out_del_mask = gmask;
            if (out_exact) *out_exact = 0;
            return gdel;
        }
    }
    if (out_del_mask) *out_del_mask = gmask;
    if (out_exact) *out_exact = (cap == gdel - 1) ? 1 : 0;
    return gdel;
}

/* Build R1 and R2 parameter lists for slice modes:
 * slice_mode: 0=inv (g1,g2 in U, N(a)=N(b) non-sq), 1=sq-norm (g1,g2 in U, N(a)=N(b) sq),
 *             2=diff-norm (g1,g2 in U, N(a)!=N(b) sample), 3=non-u (g1,g2 not in U^2 sample x inv R2) */
static void build_slice_lists(const FF *ff, int slice_mode, int use_sym,
                              R1Rep *r1_out, int *out_n1, R2Rep *r2_out, int *out_n2) {
    int nk = ff->k_order, n = ff->n_orb;
    int u_idx[MAX_ORB], nu = 0;
    for (int i = 0; i < nk; i++) if (ff->k_norm[i] == 1) u_idx[nu++] = i;

    int n1 = 0;
    if (slice_mode == 3) {
        /* Deterministic sample of 100 (g1, g2) outside U^2 */
        uint64_t st = 20261128ULL + (uint64_t)ff->q * 997ULL;
        int tries = 0;
        while (n1 < 100 && tries < 10000) {
            tries++;
            st = st * 6364136223846793005ULL + 1442695040888963407ULL;
            int i = (int)((st >> 33) % (uint64_t)nk);
            st = st * 6364136223846793005ULL + 1442695040888963407ULL;
            int j = (int)((st >> 33) % (uint64_t)nk);
            if (ff->k_norm[i] == 1 && ff->k_norm[j] == 1) continue;
            r1_out[n1++] = (R1Rep){i, j, 1};
        }
    } else {
        /* All (g1, g2) in U^2 (optionally mod C2: (g1, g2) ~ (g1^q, g2^q) = (g1^-1, g2^-1)) */
        for (int a = 0; a < nu; a++) {
            for (int b = 0; b < nu; b++) {
                int i = u_idx[a], j = u_idx[b];
                if (use_sym) {
                    int k0 = i * nk + j;
                    int ic = ff->k_conj[i], jc = ff->k_conj[j];
                    if (ic * nk + jc < k0) continue;
                }
                r1_out[n1++] = (R1Rep){i, j, 1};
            }
        }
    }
    *out_n1 = n1;

    int n2 = 0;
    if (slice_mode == 0 || slice_mode == 3) {
        /* N(alpha) = N(beta) non-square (or all equal norms in char 2) */
        for (int ac = 0; ac < n; ac++) {
            KElem al = ff->zeta_pow[ac];
            int ai = ff->k_idx[al.a][al.b];
            uint8_t na = ff->k_norm[ai];
            if ((ff->q & 1) && ff->is_sq[na]) continue;
            for (int bi = 0; bi < nk; bi++) {
                if (ff->k_norm[bi] == na) r2_out[n2++] = (R2Rep){ac, bi, 1, ac * nk + bi};
            }
        }
    } else if (slice_mode == 1) {
        /* N(alpha) = N(beta) SQUARE */
        for (int ac = 0; ac < n; ac++) {
            KElem al = ff->zeta_pow[ac];
            int ai = ff->k_idx[al.a][al.b];
            uint8_t na = ff->k_norm[ai];
            if (!ff->is_sq[na]) continue;
            for (int bi = 0; bi < nk; bi++) {
                if (ff->k_norm[bi] == na) r2_out[n2++] = (R2Rep){ac, bi, 1, ac * nk + bi};
            }
        }
    } else if (slice_mode == 2) {
        /* N(alpha) != N(beta), deterministic sample of 200 pairs */
        uint64_t st = 13372026ULL + (uint64_t)ff->q * 313ULL;
        int tries = 0;
        while (n2 < 200 && tries < 20000) {
            tries++;
            st = st * 6364136223846793005ULL + 1442695040888963407ULL;
            int ac = (int)((st >> 33) % (uint64_t)n);
            st = st * 6364136223846793005ULL + 1442695040888963407ULL;
            int bi = (int)((st >> 33) % (uint64_t)nk);
            KElem al = ff->zeta_pow[ac];
            uint8_t na = ff->k_norm[ff->k_idx[al.a][al.b]];
            if (ff->k_norm[bi] == na) continue;
            r2_out[n2++] = (R2Rep){ac, bi, 1, ac * nk + bi};
        }
    }
    *out_n2 = n2;
}

static void run_slice_bench(int q, int n_threads) {
    omp_set_num_threads(n_threads);
    FF ff; ff_init(&ff, q);
    uint8_t R1_A[MAX_ORB][6], R2_A[MAX_ORB][6];
    build_R1_A(&ff, R1_A); build_R2_A(&ff, R2_A);

    double t0 = now_sec();
    OrbitTable ot;
    init_orbit_table(&ot, &ff, R1_A, R2_A);
    double t_init = now_sec() - t0;

    R1Rep r1[512]; R2Rep r2[512];
    int n1 = 0, n2 = 0;
    build_slice_lists(&ff, 0, 1, r1, &n1, r2, &n2);

    int samp = (n1 < 10) ? n1 : 10;
    uint64_t *om = (uint64_t *)malloc((size_t)samp * ot.ow_total * sizeof(uint64_t));
    uint64_t sm[10][2];
    double tb = now_sec();
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < samp; i++) {
        uint8_t B[MAX_ORB][6];
        build_R1_B(&ff, ff.k_nonzero[r1[i].g1_idx], ff.k_nonzero[r1[i].g2_idx], B);
        build_orb_mask_fast(&ff, &ot, 0, B, om + (size_t)i * ot.ow_total, sm[i]);
    }
    double dt_1 = (now_sec() - tb) / samp;
    double est_build = dt_1 * (n1 + n2);

    printf("SLICE-BENCH q=%d (k=%d, canA=[%d,%d,%d], orbits=%d, short=%d, ow=%d, threads=%d):\n",
           q, ff.k_full, ot.nCA4, ot.nCA3, ot.nCA2, ot.n_orbits, ot.n_short, ot.ow_total, n_threads);
    printf("  init=%.3fs | S_inv sym: n1=%d x n2=%d = %d pairs (raw %d x %d = %d)\n",
           t_init, n1, n2, n1 * n2, ff.n_orb * ff.n_orb, n2, ff.n_orb * ff.n_orb * n2);
    printf("  1 build=%.2f ms (10 builds=%.3fs) | est full S_inv scan=%.2fs\n",
           dt_1 * 1e3, dt_1 * samp, est_build + (double)n1 * n2 * ot.ow_total * 0.6e-9);

    free(om); free_orbit_table(&ot);
}

/* Direct m2 != 1 control sample on q=17, 19: evaluate small sample of pairs directly on orbits */
static void run_m2ne1_control(int q, int n_threads) {
    double t0 = now_sec();
    omp_set_num_threads(n_threads);
    FF ff; ff_init(&ff, q);
    uint8_t R1_A[MAX_ORB][6], R2_A[MAX_ORB][6];
    build_R1_A(&ff, R1_A); build_R2_A(&ff, R2_A);

    /* Sample 12 (g1,g2) in U^2 x 12 (alpha,beta) in S_inv for m2=3 and m2=q (288 pairs) */
    R1Rep r1[512]; R2Rep r2[512];
    int n1_all = 0, n2_all = 0;
    build_slice_lists(&ff, 0, 1, r1, &n1_all, r2, &n2_all);
    int s1 = (n1_all < 10) ? n1_all : 10;
    int s2 = (n2_all < 10) ? n2_all : 10;
    int test_m2[2] = {3, ff.q}; /* both coprime to 18 and 20! Wait: gcd(3,18)=3, so pick first coprime > 1! */
    int m_alt = 2;
    while (gcd_int(m_alt, ff.n_orb) != 1) m_alt++;
    test_m2[0] = m_alt;
    test_m2[1] = ff.q;

    /* Check on 2000 random critical 6-tuples to estimate overlap density + exact check on 10 pairs */
    uint8_t B1s[10][MAX_ORB][6], B2s[2][10][MAX_ORB][6];
    for (int i = 0; i < s1; i++) build_R1_B(&ff, ff.k_nonzero[r1[i * (n1_all / s1)].g1_idx], ff.k_nonzero[r1[i * (n1_all / s1)].g2_idx], B1s[i]);
    for (int mi = 0; mi < 2; mi++)
        for (int j = 0; j < s2; j++) {
            R2Rep rr = r2[j * (n2_all / s2)];
            build_R2_B(&ff, ff.zeta_pow[rr.a_coset], ff.k_nonzero[rr.b_idx], test_m2[mi], B2s[mi][j]);
        }

    /* Fast Monte-Carlo exact-rank estimate over 50000 critical tuples per m2 to measure density */
    int n = ff.n_orb;
    for (int mi = 0; mi < 2; mi++) {
        int min_est = 1000000000;
        double sum_est = 0;
        int n_pairs = s1 * s2;
        int n_samp = 20000;
        #pragma omp parallel for reduction(min:min_est) reduction(+:sum_est)
        for (int p = 0; p < n_pairs; p++) {
            int i = p / s2, j = p % s2;
            uint64_t st = 987654321ULL + (uint64_t)p * 1000003ULL + (uint64_t)mi * 7777ULL;
            int hits = 0;
            uint8_t m1[6][6], m2[6][6];
            for (int t = 0; t < n_samp; t++) {
                st = st * 6364136223846793005ULL + 1442695040888963407ULL;
                int split = (int)((st >> 33) % 3); /* 0:(4,2), 1:(3,3), 2:(2,4) */
                int ac = (split == 0) ? 4 : (split == 1 ? 3 : 2);
                int bc = 6 - ac;
                uint32_t ua = 0, ub = 0;
                int row = 0;
                for (int r = 0; r < ac; r++) {
                    int c;
                    do { st = st * 6364136223846793005ULL + 1; c = (int)((st >> 33) % (uint64_t)n); } while ((ua >> c) & 1U);
                    ua |= 1U << c;
                    memcpy(m1[row], R1_A[c], 6); memcpy(m2[row], R2_A[c], 6); row++;
                }
                for (int r = 0; r < bc; r++) {
                    int c;
                    do { st = st * 6364136223846793005ULL + 1; c = (int)((st >> 33) % (uint64_t)n); } while ((ub >> c) & 1U);
                    ub |= 1U << c;
                    memcpy(m1[row], B1s[i][c], 6); memcpy(m2[row], B2s[mi][j][c], 6); row++;
                }
                if (!rank6_full(&ff, m1) && !rank6_full(&ff, m2)) hits++;
            }
            if (hits < min_est) min_est = hits;
            sum_est += (double)hits;
        }
        double n_crit = (q == 17) ? 1602216.0 : (q == 19 ? 3140700.0 : 113740.0);
        double avg_rate = (sum_est / n_pairs) / n_samp;
        double min_rate = (double)min_est / n_samp;
        printf("CTRL-M2NE1 q=%d m2=%d (%d pairs x %d MC tuples, %.2fs): min_rate=%.5f (est_unc~%.0f), avg_rate=%.5f (est_unc~%.0f)\n",
               q, test_m2[mi], n_pairs, n_samp, now_sec() - t0,
               min_rate, min_rate * n_crit, avg_rate, avg_rate * n_crit);
    }
}

static void run_slice_scan(int q, int slice_mode, int use_sym, int max_exact_tau,
                           const char *out_json, const char *save_hit_dir,
                           int n_threads, double timeout_sec) {
    double t0 = now_sec();
    double deadline = t0 + timeout_sec;
    omp_set_num_threads(n_threads);

    FF ff; ff_init(&ff, q);
    uint8_t R1_A[MAX_ORB][6], R2_A[MAX_ORB][6];
    build_R1_A(&ff, R1_A); build_R2_A(&ff, R2_A);

    OrbitTable ot;
    init_orbit_table(&ot, &ff, R1_A, R2_A);
    double t_init = now_sec() - t0;

    R1Rep r1[512]; R2Rep r2[512];
    int n1 = 0, n2 = 0;
    build_slice_lists(&ff, slice_mode, use_sym, r1, &n1, r2, &n2);

    uint64_t *r1_om = (uint64_t *)malloc((size_t)n1 * ot.ow_total * sizeof(uint64_t));
    uint64_t (*r1_sm)[2] = (uint64_t (*)[2])malloc((size_t)n1 * sizeof(uint64_t[2]));
    uint64_t *r2_om = (uint64_t *)malloc((size_t)n2 * ot.ow_total * sizeof(uint64_t));
    uint64_t (*r2_sm)[2] = (uint64_t (*)[2])malloc((size_t)n2 * sizeof(uint64_t[2]));

    #pragma omp parallel for schedule(static)
    for (int i = 0; i < n1; i++) {
        uint8_t B[MAX_ORB][6];
        build_R1_B(&ff, ff.k_nonzero[r1[i].g1_idx], ff.k_nonzero[r1[i].g2_idx], B);
        build_orb_mask_fast(&ff, &ot, 0, B, r1_om + (size_t)i * ot.ow_total, r1_sm[i]);
    }
    double t_r1 = now_sec() - t0 - t_init;

    #pragma omp parallel for schedule(static)
    for (int j = 0; j < n2; j++) {
        uint8_t B[MAX_ORB][6];
        build_R2_B(&ff, ff.zeta_pow[r2[j].a_coset], ff.k_nonzero[r2[j].b_idx], 1, B);
        build_orb_mask_fast(&ff, &ot, 1, B, r2_om + (size_t)j * ot.ow_total, r2_sm[j]);
    }
    double t_r2 = now_sec() - t0 - t_init - t_r1;

    /* Intersect ALL n1 x n2 pairs */
    double t_int_s = now_sec();
    CandHeap top_tot, top_pure33;
    cand_init(&top_tot, 100);
    cand_init(&top_pure33, 50);
    int min_42 = 1000000000, min_33 = 1000000000, min_24 = 1000000000, min_tot = 1000000000;
    uint64_t zero_hits = 0;
    double sum_tot = 0;
    int ow42 = ot.ow_42_end, ow33 = ot.ow_33_end, owtot = ot.ow_total, n_orb = ff.n_orb;

    #pragma omp parallel
    {
        CandHeap lt, lp;
        cand_init(&lt, 100); cand_init(&lp, 50);
        int lm42 = 1000000000, lm33 = 1000000000, lm24 = 1000000000, lmtot = 1000000000;
        uint64_t lz = 0;
        double lsum = 0;

        #pragma omp for schedule(dynamic, 4)
        for (int i = 0; i < n1; i++) {
            const uint64_t *m1 = r1_om + (size_t)i * owtot;
            uint64_t s10 = r1_sm[i][0], s11 = r1_sm[i][1];
            for (int j = 0; j < n2; j++) {
                const uint64_t *m2 = r2_om + (size_t)j * owtot;
                int c42 = 0, c33 = 0, c24 = 0;
                for (int w = 0; w < ow42; w++) c42 += __builtin_popcountll(m1[w] & m2[w]);
                for (int w = ow42; w < ow33; w++) c33 += __builtin_popcountll(m1[w] & m2[w]);
                for (int w = ow33; w < owtot; w++) c24 += __builtin_popcountll(m1[w] & m2[w]);
                int b42 = c42 * n_orb, b33 = c33 * n_orb, b24 = c24 * n_orb;
                uint64_t sm0 = s10 & r2_sm[j][0], sm1 = s11 & r2_sm[j][1];
                while (sm0) {
                    int sb = __builtin_ctzll(sm0); sm0 &= sm0 - 1;
                    if (ot.short_acnt[sb] == 4) b42 += ot.short_len[sb];
                    else if (ot.short_acnt[sb] == 3) b33 += ot.short_len[sb];
                    else b24 += ot.short_len[sb];
                }
                while (sm1) {
                    int sb = 64 + __builtin_ctzll(sm1); sm1 &= sm1 - 1;
                    if (ot.short_acnt[sb] == 4) b42 += ot.short_len[sb];
                    else if (ot.short_acnt[sb] == 3) b33 += ot.short_len[sb];
                    else b24 += ot.short_len[sb];
                }
                int tot = b42 + b33 + b24;
                lsum += (double)tot;
                if (b42 < lm42) lm42 = b42;
                if (b33 < lm33) lm33 = b33;
                if (b24 < lm24) lm24 = b24;
                if (tot < lmtot) lmtot = tot;
                if (tot == 0) lz++;
                if (lt.count < lt.cap || tot < lt.items[lt.cap - 1].tot) {
                    Cand c = {r1[i].g1_idx, r1[i].g2_idx, r2[j].a_coset, r2[j].b_idx, 1,
                              tot, b42, b33, b24, -1, 0, -1, 0, 0};
                    cand_add(&lt, c);
                }
                if (b42 == 0 && b24 == 0 && (lp.count < lp.cap || tot < lp.items[lp.cap - 1].tot)) {
                    Cand c = {r1[i].g1_idx, r1[i].g2_idx, r2[j].a_coset, r2[j].b_idx, 1,
                              tot, b42, b33, b24, -1, 0, -1, 0, 0};
                    cand_add(&lp, c);
                }
            }
        }
        #pragma omp critical(merge_slice)
        {
            zero_hits += lz; sum_tot += lsum;
            if (lm42 < min_42) min_42 = lm42;
            if (lm33 < min_33) min_33 = lm33;
            if (lm24 < min_24) min_24 = lm24;
            if (lmtot < min_tot) min_tot = lmtot;
            for (int k = 0; k < lt.count; k++) cand_add(&top_tot, lt.items[k]);
            for (int k = 0; k < lp.count; k++) cand_add(&top_pure33, lp.items[k]);
        }
        free(lt.items); free(lp.items);
    }
    double t_int = now_sec() - t_int_s;

    /* Merge top-60 by unc + top-30 pure (3,3) for exact hitting-set evaluation */
    Cand eval_list[120];
    int n_eval = 0;
    for (int i = 0; i < top_tot.count && i < 60; i++) eval_list[n_eval++] = top_tot.items[i];
    for (int i = 0; i < top_pure33.count && i < 30; i++) {
        Cand c = top_pure33.items[i];
        int dup = 0;
        for (int j = 0; j < n_eval; j++)
            if (eval_list[j].g1_idx == c.g1_idx && eval_list[j].g2_idx == c.g2_idx &&
                eval_list[j].a_coset == c.a_coset && eval_list[j].b_idx == c.b_idx) { dup = 1; break; }
        if (!dup && n_eval < 120) eval_list[n_eval++] = c;
    }

    /* Map back to r1/r2 mask indices and run exact hitting set */
    double t_hs_s = now_sec();
    #pragma omp parallel for schedule(dynamic, 1)
    for (int idx = 0; idx < n_eval; idx++) {
        if (now_sec() > deadline) continue;
        Cand *c = &eval_list[idx];
        int i1 = -1, i2 = -1;
        for (int i = 0; i < n1; i++) if (r1[i].g1_idx == c->g1_idx && r1[i].g2_idx == c->g2_idx) { i1 = i; break; }
        for (int j = 0; j < n2; j++) if (r2[j].a_coset == c->a_coset && r2[j].b_idx == c->b_idx) { i2 = j; break; }
        if (i1 < 0 || i2 < 0) continue;
        int cap_e = c->tot + 64;
        uint64_t *edges = (uint64_t *)malloc((size_t)cap_e * sizeof(uint64_t));
        int ne = extract_edges_from_orbits(&ot, r1_om + (size_t)i1 * owtot, r1_sm[i1],
                                           r2_om + (size_t)i2 * owtot, r2_sm[i2], edges, cap_e);
        uint64_t nl = (ne <= 1500) ? 50000000ULL : 2000000ULL;
        c->tau = compute_min_hitting_set_u64(ff.k_full, edges, ne, max_exact_tau, nl,
                                             &c->del_mask, &c->exact_tau, &c->greedy_tau, &c->max_col_deg);
        free(edges);
    }
    double t_hs = now_sec() - t_hs_s;

    int best_tau = 1000000, best_idx = -1;
    for (int i = 0; i < n_eval; i++) {
        if (eval_list[i].tau < 0) continue;
        int better = 0;
        if (best_idx < 0 || eval_list[i].tau < best_tau) better = 1;
        else if (eval_list[i].tau == best_tau) {
            const Cand *a = &eval_list[i], *b = &eval_list[best_idx];
            if (a->tot != b->tot) better = (a->tot < b->tot);
            else if (a->g1_idx != b->g1_idx) better = (a->g1_idx < b->g1_idx);
            else if (a->g2_idx != b->g2_idx) better = (a->g2_idx < b->g2_idx);
            else if (a->a_coset != b->a_coset) better = (a->a_coset < b->a_coset);
            else if (a->b_idx != b->b_idx) better = (a->b_idx < b->b_idx);
        }
        if (better) { best_tau = eval_list[i].tau; best_idx = i; }
    }
    int best_kpunc = (best_idx >= 0) ? (ff.k_full - best_tau) : 0;
    const char *snames[4] = {"inv", "sq-norm", "diff-norm", "non-u"};
    double t_tot = now_sec() - t0;

    printf("SLICE-SCAN q=%d slice=%s (k=%d, orbits=%d, short=%d, sym=%d): n1=%d x n2=%d = %d pairs, avg_unc=%.1f, zero_hits=%llu\n",
           q, snames[slice_mode], ff.k_full, ot.n_orbits, ot.n_short, use_sym,
           n1, n2, n1 * n2, sum_tot / (double)(n1 * n2), (unsigned long long)zero_hits);
    printf("  times: init=%.3fs r1=%.3fs r2=%.3fs inter=%.3fs hitset(%d)=%.3fs total=%.3fs\n",
           t_init, t_r1, t_r2, t_int, n_eval, t_hs, t_tot);
    printf("  indep split minima: min_42=%d, min_33=%d, min_24=%d | pure33_cnt=%d\n",
           min_42, min_33, min_24, top_pure33.count);
    if (top_tot.count > 0) {
        Cand b = top_tot.items[0];
        KElem g1 = ff.k_nonzero[b.g1_idx], g2 = ff.k_nonzero[b.g2_idx];
        KElem al = ff.zeta_pow[b.a_coset], be = ff.k_nonzero[b.b_idx];
        printf("  min_unc=%d (42=%d, 33=%d, 24=%d) at g1=(%d,%d) g2=(%d,%d) alpha=(%d,%d) beta=(%d,%d)\n",
               b.tot, b.b42, b.b33, b.b24, g1.a, g1.b, g2.a, g2.b, al.a, al.b, be.a, be.b);
    }
    if (best_idx >= 0) {
        Cand b = eval_list[best_idx];
        KElem g1 = ff.k_nonzero[b.g1_idx], g2 = ff.k_nonzero[b.g2_idx];
        KElem al = ff.zeta_pow[b.a_coset], be = ff.k_nonzero[b.b_idx];
        printf("  best_tau=%d (exact=%d, greedy=%d, k_punc=%d/%d, from unc=%d [42=%d,33=%d,24=%d], del_mask=0x%llx) at g1=(%d,%d) g2=(%d,%d) alpha=(%d,%d) beta=(%d,%d)\n",
               b.tau, b.exact_tau, b.greedy_tau, best_kpunc, ff.k_full, b.tot, b.b42, b.b33, b.b24,
               (unsigned long long)b.del_mask, g1.a, g1.b, g2.a, g2.b, al.a, al.b, be.a, be.b);
    }
    if (save_hit_dir && best_idx >= 0) {
        char path[512];
        snprintf(path, sizeof(path), "%s/cphf_q%d_k%d_punc.json", save_hit_dir, q, best_kpunc);
        save_cphf_hit_json(path, &ff, R1_A, R2_A, &eval_list[best_idx]);
        printf("  SAVED BEST CPHF -> %s\n", path);
    }
    if (out_json) {
        FILE *fp = fopen(out_json, "w");
        if (fp) {
            fprintf(fp, "{\n  \"q\": %d, \"k_full\": %d, \"slice\": \"%s\", \"use_sym\": %d, \"n1\": %d, \"n2\": %d, \"pairs\": %d,\n",
                    q, ff.k_full, snames[slice_mode], use_sym, n1, n2, n1 * n2);
            fprintf(fp, "  \"avg_unc\": %.2f, \"zero_hits\": %llu, \"min_unc\": %d, \"best_tau\": %d, \"best_kpunc\": %d,\n",
                    sum_tot / (double)(n1 * n2), (unsigned long long)zero_hits,
                    top_tot.count > 0 ? top_tot.items[0].tot : -1,
                    best_idx >= 0 ? best_tau : -1, best_kpunc);
            fprintf(fp, "  \"times\": {\"init\": %.4f, \"r1\": %.4f, \"r2\": %.4f, \"inter\": %.4f, \"hitset\": %.4f, \"total\": %.4f},\n",
                    t_init, t_r1, t_r2, t_int, t_hs, t_tot);
            fprintf(fp, "  \"evaluated\": [\n");
            for (int i = 0; i < n_eval; i++) {
                Cand c = eval_list[i];
                KElem g1 = ff.k_nonzero[c.g1_idx], g2 = ff.k_nonzero[c.g2_idx];
                KElem al = ff.zeta_pow[c.a_coset], be = ff.k_nonzero[c.b_idx];
                fprintf(fp, "    {\"g1\":[%d,%d],\"g2\":[%d,%d],\"alpha\":[%d,%d],\"beta\":[%d,%d],\"m2\":1,"
                            "\"unc\":%d,\"b42\":%d,\"b33\":%d,\"b24\":%d,\"tau\":%d,\"exact_tau\":%d,"
                            "\"greedy_tau\":%d,\"max_col_deg\":%d,\"del_mask\":%llu}%s\n",
                        g1.a, g1.b, g2.a, g2.b, al.a, al.b, be.a, be.b,
                        c.tot, c.b42, c.b33, c.b24, c.tau, c.exact_tau, c.greedy_tau,
                        c.max_col_deg, (unsigned long long)c.del_mask, (i + 1 < n_eval) ? "," : "");
            }
            fprintf(fp, "  ]\n}\n");
            fclose(fp);
        }
    }

    free(r1_om); free(r1_sm); free(r2_om); free(r2_sm);
    free(top_tot.items); free(top_pure33.items);
    free_orbit_table(&ot);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <check|bench|dump-ap1|scan|ctrl-m2ne1> ...\n", argv[0]);
        return 1;
    }
    if (strcmp(argv[1], "check") == 0) {
        int q = atoi(argv[2]);
        KElem g1 = {(uint8_t)atoi(argv[3]), (uint8_t)atoi(argv[4])};
        KElem g2 = {(uint8_t)atoi(argv[5]), (uint8_t)atoi(argv[6])};
        KElem al = {(uint8_t)atoi(argv[7]), (uint8_t)atoi(argv[8])};
        KElem be = {(uint8_t)atoi(argv[9]), (uint8_t)atoi(argv[10])};
        int m2 = atoi(argv[11]);
        FF ff; ff_init(&ff, q);
        uint8_t R1_A[MAX_ORB][6], R1_B[MAX_ORB][6], R2_A[MAX_ORB][6], R2_B[MAX_ORB][6];
        build_R1_A(&ff, R1_A); build_R1_B(&ff, g1, g2, R1_B);
        build_R2_A(&ff, R2_A); build_R2_B(&ff, al, be, m2, R2_B);
        uint8_t R1[MAX_K][6], R2[MAX_K][6];
        for (int i = 0; i < ff.n_orb; i++) {
            memcpy(R1[i], R1_A[i], 6); memcpy(R1[ff.n_orb + i], R1_B[i], 6);
            memcpy(R2[i], R2_A[i], 6); memcpy(R2[ff.n_orb + i], R2_B[i], 6);
        }
        int d1[7], d2[7], bt[7];
        full_check_matrices(&ff, ff.n_orb, ff.n_orb, R1, R2, d1, d2, bt);
        printf("{\"dep1\":[%d,%d,%d,%d,%d,%d,%d],\"dep2\":[%d,%d,%d,%d,%d,%d,%d],\"both\":[%d,%d,%d,%d,%d,%d,%d]}\n",
               d1[0], d1[1], d1[2], d1[3], d1[4], d1[5], d1[6],
               d2[0], d2[1], d2[2], d2[3], d2[4], d2[5], d2[6],
               bt[0], bt[1], bt[2], bt[3], bt[4], bt[5], bt[6]);
        return 0;
    } else if (strcmp(argv[1], "bench") == 0) {
        int q = atoi(argv[2]), threads = 2, inv_slice = (q > 13);
        for (int i = 3; i < argc; i++) {
            if (strcmp(argv[i], "--threads") == 0 && i + 1 < argc) threads = atoi(argv[++i]);
            else if (strcmp(argv[i], "--invariant-slice") == 0) inv_slice = 1;
        }
        if (inv_slice) run_slice_bench(q, threads);
        else run_bench(q, threads);
        return 0;
    } else if (strcmp(argv[1], "ctrl-m2ne1") == 0) {
        int q = atoi(argv[2]), threads = 2;
        for (int i = 3; i < argc; i++)
            if (strcmp(argv[i], "--threads") == 0 && i + 1 < argc) threads = atoi(argv[++i]);
        run_m2ne1_control(q, threads);
        return 0;
    } else if (strcmp(argv[1], "dump-ap1") == 0) {
        int q = atoi(argv[2]), threads = 2;
        const char *out = NULL;
        for (int i = 3; i < argc; i++) {
            if (strcmp(argv[i], "--out") == 0 && i + 1 < argc) out = argv[++i];
            else if (strcmp(argv[i], "--threads") == 0 && i + 1 < argc) threads = atoi(argv[++i]);
        }
        run_scan(q, 0, 0, 0, 0, out, NULL, NULL, threads, 300.0, 1);
        return 0;
    } else if (strcmp(argv[1], "scan") == 0) {
        int q = atoi(argv[2]), use_sym = 1, m2_mode = 0, cs = 0, ce = 0, threads = 2;
        int slice_mode = -1, max_tau = (q >= 17) ? 10 : 7;
        double timeout = 500.0;
        const char *out = NULL, *jsonl = NULL, *hit_dir = NULL;
        for (int i = 3; i < argc; i++) {
            if (strcmp(argv[i], "--no-sym") == 0) use_sym = 0;
            else if (strcmp(argv[i], "--invariant-slice") == 0) slice_mode = 0;
            else if (strcmp(argv[i], "--slice") == 0 && i + 1 < argc) {
                const char *sm = argv[++i];
                if (strcmp(sm, "inv") == 0) slice_mode = 0;
                else if (strcmp(sm, "sq-norm") == 0) slice_mode = 1;
                else if (strcmp(sm, "diff-norm") == 0) slice_mode = 2;
                else if (strcmp(sm, "non-u") == 0) slice_mode = 3;
            }
            else if (strcmp(argv[i], "--max-tau") == 0 && i + 1 < argc) max_tau = atoi(argv[++i]);
            else if (strcmp(argv[i], "--m2-mode") == 0 && i + 1 < argc) {
                const char *mm = argv[++i];
                if (strcmp(mm, "all") == 0) m2_mode = 0;
                else if (strcmp(mm, "m2eq1") == 0) m2_mode = 1;
                else if (strcmp(mm, "m2ne1") == 0) m2_mode = 2;
            }
            else if (strcmp(argv[i], "--chunk-start") == 0 && i + 1 < argc) cs = atoi(argv[++i]);
            else if (strcmp(argv[i], "--chunk-end") == 0 && i + 1 < argc) ce = atoi(argv[++i]);
            else if (strcmp(argv[i], "--out") == 0 && i + 1 < argc) out = argv[++i];
            else if (strcmp(argv[i], "--jsonl") == 0 && i + 1 < argc) jsonl = argv[++i];
            else if (strcmp(argv[i], "--save-hit-dir") == 0 && i + 1 < argc) hit_dir = argv[++i];
            else if (strcmp(argv[i], "--threads") == 0 && i + 1 < argc) threads = atoi(argv[++i]);
            else if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) timeout = atof(argv[++i]);
        }
        if (slice_mode >= 0 || q > 13) {
            if (slice_mode < 0) slice_mode = 0;
            run_slice_scan(q, slice_mode, use_sym, max_tau, out, hit_dir, threads, timeout);
        } else {
            run_scan(q, use_sym, m2_mode, cs, ce, out, jsonl, hit_dir, threads, timeout, 1);
        }
        return 0;
    }
    fprintf(stderr, "Unknown mode: %s\n", argv[1]);
    return 1;
}
