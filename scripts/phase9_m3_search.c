/*
 * Phase 9: Fast O(1)-incremental C solver for the Biaffine 3D Model M_3(R_3) (k = q + 3).
 *
 * Supports:
 *   - Prime powers q in {3, 4, 5, 7, 8, 9} with GF(q) tables matching GeneralGF(q)
 *     in scripts/gen_general_tqv.py.
 *   - Modes: tspec (3 <= t <= q) and full-bg3 (all q^2 directions D_1 and q^2 normals N_2).
 *   - Exact incremental counting for Typ 0, Typ 1, Typ 2, Typ 3 with cached per-row projections.
 *   - Focused conflict-driven Tabu + PAWS dynamic clause weighting + ILS kicks / restarts.
 *   - Optional Simulated Annealing (--algo sa) and multi-threaded search (--threads N).
 *   - Built-in --self-test comparing incremental updates against fresh from-scratch recomputation.
 *
 * Build:
 *   gcc -O3 -march=native -pthread -Wall -Wextra scripts/phase9_m3_search.c -o /tmp/phase9_m3_search -lm
 */

#include <ctype.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_Q 9
#define MAX_Q2 (MAX_Q * MAX_Q)
#define MAX_Q3 (MAX_Q * MAX_Q * MAX_Q)
#define MAX_M 1024
#define MAX_D MAX_Q2
#define MAX_N MAX_Q2
#define MAX_INTER (MAX_Q3 + 3 * MAX_D * MAX_Q * MAX_Q2 + 3 * MAX_N * MAX_Q2 * MAX_Q + MAX_Q3)

/* ---------- Fast PRNG: xoshiro256** ---------- */

typedef struct {
    uint64_t s[4];
} Rng;

static inline uint64_t splitmix64(uint64_t *x) {
    uint64_t z = (*x += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

static void rng_seed(Rng *rng, uint64_t seed) {
    uint64_t x = seed;
    for (int i = 0; i < 4; i++) rng->s[i] = splitmix64(&x);
}

static inline uint64_t rotl64(const uint64_t x, int k) {
    return (x << k) | (x >> (64 - k));
}

static inline uint64_t rng_next(Rng *rng) {
    const uint64_t result = rotl64(rng->s[1] * 5, 7) * 9;
    const uint64_t t = rng->s[1] << 17;
    rng->s[2] ^= rng->s[0];
    rng->s[3] ^= rng->s[1];
    rng->s[1] ^= rng->s[2];
    rng->s[0] ^= rng->s[3];
    rng->s[2] ^= t;
    rng->s[3] = rotl64(rng->s[3], 45);
    return result;
}

static inline uint32_t rng_bound(Rng *rng, uint32_t n) {
    return (uint32_t)(rng_next(rng) % n);
}

static inline double rng_double(Rng *rng) {
    return (double)(rng_next(rng) >> 11) * (1.0 / 9007199254740992.0);
}

static double wall_time(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

/* ---------- Finite Field GF(q) matching GeneralGF(q) ---------- */

typedef struct {
    int q;
    uint8_t add[MAX_Q][MAX_Q];
    uint8_t sub[MAX_Q][MAX_Q];
    uint8_t mul[MAX_Q][MAX_Q];
    uint8_t neg[MAX_Q];
    uint8_t inv[MAX_Q];
} GF;

static int gf_init(GF *gf, int q) {
    memset(gf, 0, sizeof(*gf));
    gf->q = q;
    if (q == 3 || q == 5 || q == 7) {
        for (int a = 0; a < q; a++) {
            for (int b = 0; b < q; b++) {
                gf->add[a][b] = (uint8_t)((a + b) % q);
                gf->mul[a][b] = (uint8_t)((a * b) % q);
            }
        }
    } else if (q == 4) {
        /* GF(2)[X]/(X^2 + X + 1) */
        for (int a = 0; a < 4; a++) {
            for (int b = 0; b < 4; b++) {
                gf->add[a][b] = (uint8_t)(a ^ b);
                int p = 0;
                int x = a, y = b;
                for (int i = 0; i < 2; i++) {
                    if (y & 1) p ^= x;
                    int hi = x & 2;
                    x <<= 1;
                    if (hi) x ^= 0x7; /* X^2 + X + 1 */
                    y >>= 1;
                }
                gf->mul[a][b] = (uint8_t)(p & 3);
            }
        }
    } else if (q == 8) {
        /* GF(2)[X]/(X^3 + X + 1) */
        for (int a = 0; a < 8; a++) {
            for (int b = 0; b < 8; b++) {
                gf->add[a][b] = (uint8_t)(a ^ b);
                int p = 0;
                int x = a, y = b;
                for (int i = 0; i < 3; i++) {
                    if (y & 1) p ^= x;
                    int hi = x & 4;
                    x <<= 1;
                    if (hi) x ^= 0xb; /* X^3 + X + 1 */
                    y >>= 1;
                }
                gf->mul[a][b] = (uint8_t)(p & 7);
            }
        }
    } else if (q == 9) {
        /* GF(3)[X]/(X^2 + 1) */
        for (int a = 0; a < 9; a++) {
            int a0 = a % 3, a1 = a / 3;
            for (int b = 0; b < 9; b++) {
                int b0 = b % 3, b1 = b / 3;
                int s0 = (a0 + b0) % 3;
                int s1 = (a1 + b1) % 3;
                gf->add[a][b] = (uint8_t)(s0 + 3 * s1);
                /* (a0 + a1 X)(b0 + b1 X) = (a0 b0 - a1 b1) + (a0 b1 + a1 b0) X */
                int m0 = (a0 * b0 - a1 * b1) % 3;
                if (m0 < 0) m0 += 3;
                int m1 = (a0 * b1 + a1 * b0) % 3;
                gf->mul[a][b] = (uint8_t)(m0 + 3 * m1);
            }
        }
    } else {
        return -1;
    }

    for (int a = 0; a < q; a++) {
        int found_neg = 0;
        for (int b = 0; b < q; b++) {
            if (gf->add[a][b] == 0) {
                gf->neg[a] = (uint8_t)b;
                found_neg = 1;
                break;
            }
        }
        if (!found_neg) return -2;
        if (a > 0) {
            int found_inv = 0;
            for (int b = 1; b < q; b++) {
                if (gf->mul[a][b] == 1) {
                    gf->inv[a] = (uint8_t)b;
                    found_inv = 1;
                    break;
                }
            }
            if (!found_inv) return -3;
        }
    }
    for (int a = 0; a < q; a++) {
        for (int b = 0; b < q; b++) {
            gf->sub[a][b] = gf->add[a][gf->neg[b]];
        }
    }
    return 0;
}

/* ---------- Problem specification (D_1, N_2, offsets) ---------- */

typedef enum { MODE_TSPEC = 0, MODE_FULL_BG3 = 1 } Mode;
typedef enum { INIT_BASE = 0, INIT_RAND = 1, INIT_FILE = 2 } InitMode;
typedef enum { ALGO_PAWS = 0, ALGO_SA = 1 } AlgoMode;

typedef struct {
    GF gf;
    int q, q2, q3;
    int t;
    Mode mode;
    int num_d1;
    uint8_t d1_v[MAX_D];
    uint8_t d1_w[MAX_D];
    int num_n2;
    uint8_t n2_al[MAX_N];
    uint8_t n2_be[MAX_N];

    int off0, off1, off2, off3, total_inter;
} Problem;

static void add_d1_from_subsets(Problem *P, int start, int depth, int target_k, int *sub, uint8_t seen[MAX_Q][MAX_Q]) {
    if (depth == target_k) {
        uint8_t e1 = 0, e2 = 0;
        for (int i = 0; i < target_k; i++) e1 = P->gf.add[e1][sub[i]];
        for (int i = 0; i < target_k; i++)
            for (int j = i + 1; j < target_k; j++)
                e2 = P->gf.add[e2][P->gf.mul[sub[i]][sub[j]]];
        uint8_t v = e2;
        uint8_t w = P->gf.neg[e1];
        seen[v][w] = 1;
        return;
    }
    for (int x = start; x <= P->q - (target_k - depth); x++) {
        sub[depth] = x;
        add_d1_from_subsets(P, x + 1, depth + 1, target_k, sub, seen);
    }
}

static void add_n2_from_subsets(Problem *P, int start, int depth, int target_k, int *sub, uint8_t seen[MAX_Q][MAX_Q]) {
    if (depth == target_k) {
        uint8_t e1 = 0, e2 = 0;
        for (int i = 0; i < target_k; i++) e1 = P->gf.add[e1][sub[i]];
        for (int i = 0; i < target_k; i++)
            for (int j = i + 1; j < target_k; j++)
                e2 = P->gf.add[e2][P->gf.mul[sub[i]][sub[j]]];
        uint8_t al = e1;
        uint8_t be = P->gf.sub[P->gf.mul[e1][e1]][e2];
        seen[al][be] = 1;
        return;
    }
    for (int x = start; x <= P->q - (target_k - depth); x++) {
        sub[depth] = x;
        add_n2_from_subsets(P, x + 1, depth + 1, target_k, sub, seen);
    }
}

static int problem_init(Problem *P, int q, Mode mode, int t) {
    memset(P, 0, sizeof(*P));
    if (gf_init(&P->gf, q) != 0) return -1;
    P->q = q;
    P->q2 = q * q;
    P->q3 = q * q * q;
    P->mode = mode;
    P->t = t;

    if (mode == MODE_FULL_BG3) {
        P->num_d1 = 0;
        for (int v = 0; v < q; v++) {
            for (int w = 0; w < q; w++) {
                P->d1_v[P->num_d1] = (uint8_t)v;
                P->d1_w[P->num_d1] = (uint8_t)w;
                P->num_d1++;
            }
        }
        P->num_n2 = 0;
        for (int al = 0; al < q; al++) {
            for (int be = 0; be < q; be++) {
                P->n2_al[P->num_n2] = (uint8_t)al;
                P->n2_be[P->num_n2] = (uint8_t)be;
                P->num_n2++;
            }
        }
    } else {
        if (t < 3 || t > q) return -2;
        uint8_t seen_d1[MAX_Q][MAX_Q] = {{0}};
        uint8_t seen_n2[MAX_Q][MAX_Q] = {{0}};
        int sub[MAX_Q];
        add_d1_from_subsets(P, 0, 0, t - 1, sub, seen_d1);
        add_n2_from_subsets(P, 0, 0, t - 2, sub, seen_n2);
        P->num_d1 = 0;
        for (int v = 0; v < q; v++)
            for (int w = 0; w < q; w++)
                if (seen_d1[v][w]) {
                    P->d1_v[P->num_d1] = (uint8_t)v;
                    P->d1_w[P->num_d1] = (uint8_t)w;
                    P->num_d1++;
                }
        P->num_n2 = 0;
        for (int al = 0; al < q; al++)
            for (int be = 0; be < q; be++)
                if (seen_n2[al][be]) {
                    P->n2_al[P->num_n2] = (uint8_t)al;
                    P->n2_be[P->num_n2] = (uint8_t)be;
                    P->num_n2++;
                }
    }

    P->off0 = 0;
    P->off1 = P->off0 + P->q3;
    P->off2 = P->off1 + 3 * P->num_d1 * P->q * P->q2;
    P->off3 = P->off2 + 3 * P->num_n2 * P->q2 * P->q;
    P->total_inter = P->off3 + P->q3;
    if (P->total_inter > MAX_INTER) return -3;
    return 0;
}

/* Pair index mapping: p=0:(a,b)=(3,4), p=1:(a,c)=(3,5), p=2:(b,c)=(4,5) */
static const int PAIR_U1[3] = {0, 0, 1};
static const int PAIR_U2[3] = {1, 2, 2};
/* For each u in {0,1,2}, the 2 pairs containing u, and which slot (0=first, 1=second) */
static const int U_PAIRS[3][2] = {{0, 1}, {0, 2}, {1, 2}};
static const int U_OTHER[3][2] = {{1, 2}, {0, 2}, {0, 1}};
static const int U_IS_SECOND[3][2] = {{0, 0}, {1, 0}, {1, 1}};

static inline int id_t0(const Problem *P, int c0, int c1, int c2) {
    return P->off0 + (c0 * P->q + c1) * P->q + c2;
}

static inline int id_t1(const Problem *P, int u, int d, int s, int proj) {
    return P->off1 + (((u * P->num_d1 + d) * P->q + s) * P->q2 + proj);
}

static inline int id_t2(const Problem *P, int p, int n, int sp, int val) {
    return P->off2 + (((p * P->num_n2 + n) * P->q2 + sp) * P->q + val);
}

static inline int id_t3(const Problem *P, int a, int b, int c) {
    return P->off3 + (a * P->q + b) * P->q + c;
}

static inline int inter_type(const Problem *P, int id) {
    if (id < P->off1) return 0;
    if (id < P->off2) return 1;
    if (id < P->off3) return 2;
    return 3;
}

/* ---------- Solver State ---------- */

typedef struct {
    const Problem *P;
    int m;
    uint8_t rows[MAX_M][6];
    uint8_t best_rows[MAX_M][6];
    uint8_t t1_proj[MAX_M][MAX_D]; /* p0 * q + p1 */
    uint8_t t2_val[MAX_M][MAX_N];

    uint16_t cnt[MAX_INTER];
    uint32_t weight[MAX_INTER];
    int unc_list[MAX_INTER];
    int unc_pos[MAX_INTER];
    int unc_count;
    int unc_by_type[4];

    int best_unc;
    int best_by_type[4];

    uint64_t tabu_val[MAX_M][6][MAX_Q];
    uint64_t step;
    uint64_t evals;
    uint64_t bumps;
    uint64_t restarts;
    uint32_t base_w03;
    Rng rng;
} State;

static inline void inc_inter(State *S, int id) {
    if (S->cnt[id]++ == 0) {
        int pos = S->unc_pos[id];
        int last_id = S->unc_list[--S->unc_count];
        S->unc_list[pos] = last_id;
        S->unc_pos[last_id] = pos;
        S->unc_pos[id] = -1;
        S->unc_by_type[inter_type(S->P, id)]--;
    }
}

static inline void dec_inter(State *S, int id) {
    if (--S->cnt[id] == 0) {
        S->unc_pos[id] = S->unc_count;
        S->unc_list[S->unc_count++] = id;
        S->unc_by_type[inter_type(S->P, id)]++;
    }
}

static void state_rebuild(State *S) {
    const Problem *P = S->P;
    const GF *gf = &P->gf;
    int q = P->q;

    memset(S->cnt, 0, (size_t)P->total_inter * sizeof(uint16_t));
    S->unc_count = P->total_inter;
    S->unc_by_type[0] = P->q3;
    S->unc_by_type[1] = 3 * P->num_d1 * P->q * P->q2;
    S->unc_by_type[2] = 3 * P->num_n2 * P->q2 * P->q;
    S->unc_by_type[3] = P->q3;
    for (int id = 0; id < P->total_inter; id++) {
        S->unc_list[id] = id;
        S->unc_pos[id] = id;
    }

    for (int r = 0; r < S->m; r++) {
        int c0 = S->rows[r][0], c1 = S->rows[r][1], c2 = S->rows[r][2];
        int a = S->rows[r][3], b = S->rows[r][4], c = S->rows[r][5];

        inc_inter(S, id_t0(P, c0, c1, c2));
        inc_inter(S, id_t3(P, a, b, c));

        for (int d = 0; d < P->num_d1; d++) {
            int p0 = gf->sub[c0][gf->mul[P->d1_v[d]][c2]];
            int p1 = gf->sub[c1][gf->mul[P->d1_w[d]][c2]];
            int proj = p0 * q + p1;
            S->t1_proj[r][d] = (uint8_t)proj;
            inc_inter(S, id_t1(P, 0, d, a, proj));
            inc_inter(S, id_t1(P, 1, d, b, proj));
            inc_inter(S, id_t1(P, 2, d, c, proj));
        }

        int sp0 = a * q + b;
        int sp1 = a * q + c;
        int sp2 = b * q + c;
        for (int n = 0; n < P->num_n2; n++) {
            int val = gf->add[gf->add[c0][gf->mul[P->n2_al[n]][c1]]][gf->mul[P->n2_be[n]][c2]];
            S->t2_val[r][n] = (uint8_t)val;
            inc_inter(S, id_t2(P, 0, n, sp0, val));
            inc_inter(S, id_t2(P, 1, n, sp1, val));
            inc_inter(S, id_t2(P, 2, n, sp2, val));
        }
    }
}

static inline uint32_t floor_weight(const State *S, int id) {
    return (id < S->P->off1 || id >= S->P->off3) ? S->base_w03 : 1U;
}

static void state_reset_weights_tabu(State *S) {
    for (int id = 0; id < S->P->total_inter; id++) S->weight[id] = floor_weight(S, id);
    memset(S->tabu_val, 0, sizeof(S->tabu_val));
}

static void state_record_best(State *S) {
    if (S->unc_count < S->best_unc) {
        S->best_unc = S->unc_count;
        for (int i = 0; i < 4; i++) S->best_by_type[i] = S->unc_by_type[i];
        memcpy(S->best_rows, S->rows, (size_t)S->m * 6);
    }
}

static void state_init_rows(State *S, InitMode imode, const uint8_t (*init_file_rows)[6], int init_file_m) {
    const Problem *P = S->P;
    const GF *gf = &P->gf;
    int q = P->q;
    int idx = 0;

    if (imode == INIT_FILE && init_file_rows != NULL && init_file_m > 0) {
        if (init_file_m >= S->m) {
            /* Randomly pick S->m rows without replacement */
            int perm[MAX_M];
            for (int i = 0; i < init_file_m; i++) perm[i] = i;
            for (int i = 0; i < S->m; i++) {
                int j = i + (int)rng_bound(&S->rng, (uint32_t)(init_file_m - i));
                int tmp = perm[i]; perm[i] = perm[j]; perm[j] = tmp;
                memcpy(S->rows[i], init_file_rows[perm[i]], 6);
            }
            idx = S->m;
        } else {
            for (int i = 0; i < init_file_m; i++) memcpy(S->rows[i], init_file_rows[i], 6);
            idx = init_file_m;
        }
    } else if (imode == INIT_BASE && S->m >= P->q3) {
        /* Linear base: (c0, c1, c2, c2, c0, c0 + c1 + 2*c2) in GF(q) */
        int coeff2 = (q > 2) ? 2 : 1;
        for (int c0 = 0; c0 < q; c0++) {
            for (int c1 = 0; c1 < q; c1++) {
                for (int c2 = 0; c2 < q; c2++) {
                    S->rows[idx][0] = (uint8_t)c0;
                    S->rows[idx][1] = (uint8_t)c1;
                    S->rows[idx][2] = (uint8_t)c2;
                    S->rows[idx][3] = (uint8_t)c2;
                    S->rows[idx][4] = (uint8_t)c0;
                    S->rows[idx][5] = gf->add[gf->add[c0][c1]][gf->mul[coeff2][c2]];
                    idx++;
                }
            }
        }
    }

    while (idx < S->m) {
        for (int col = 0; col < 6; col++) S->rows[idx][col] = (uint8_t)rng_bound(&S->rng, (uint32_t)q);
        idx++;
    }
    state_rebuild(S);
}

/* ---------- O(1)-Incremental Move Evaluation & Application ---------- */

static inline void eval_move(const State *S, int r, int col, int new_val, int *out_du, int64_t *out_dw) {
    const Problem *P = S->P;
    const GF *gf = &P->gf;
    int q = P->q;
    int old_val = S->rows[r][col];
    if (old_val == new_val) {
        *out_du = 0;
        *out_dw = 0;
        return;
    }

    int du = 0;
    int64_t dw = 0;
    const uint16_t *cnt = S->cnt;
    const uint32_t *w = S->weight;

    if (col < 3) {
        int c0 = S->rows[r][0], c1 = S->rows[r][1], c2 = S->rows[r][2];
        int nc0 = c0, nc1 = c1, nc2 = c2;
        if (col == 0) nc0 = new_val;
        else if (col == 1) nc1 = new_val;
        else nc2 = new_val;

        /* Typ 0 */
        int old0 = id_t0(P, c0, c1, c2);
        int new0 = id_t0(P, nc0, nc1, nc2);
        if (cnt[old0] == 1) { du++; dw += (int64_t)w[old0]; }
        if (cnt[new0] == 0) { du--; dw -= (int64_t)w[new0]; }

        int a = S->rows[r][3], b = S->rows[r][4], c = S->rows[r][5];
        int delta = gf->sub[new_val][old_val];

        /* Typ 1 */
        const uint8_t *t1p = S->t1_proj[r];
        if (col == 0) {
            for (int d = 0; d < P->num_d1; d++) {
                int old_proj = t1p[d];
                int p0 = old_proj / q, p1 = old_proj % q;
                int new_proj = gf->add[p0][delta] * q + p1;
                int base0 = P->off1 + ((0 * P->num_d1 + d) * P->q + a) * P->q2;
                int base1 = P->off1 + ((1 * P->num_d1 + d) * P->q + b) * P->q2;
                int base2 = P->off1 + ((2 * P->num_d1 + d) * P->q + c) * P->q2;
                if (cnt[base0 + old_proj] == 1) { du++; dw += (int64_t)w[base0 + old_proj]; }
                if (cnt[base0 + new_proj] == 0) { du--; dw -= (int64_t)w[base0 + new_proj]; }
                if (cnt[base1 + old_proj] == 1) { du++; dw += (int64_t)w[base1 + old_proj]; }
                if (cnt[base1 + new_proj] == 0) { du--; dw -= (int64_t)w[base1 + new_proj]; }
                if (cnt[base2 + old_proj] == 1) { du++; dw += (int64_t)w[base2 + old_proj]; }
                if (cnt[base2 + new_proj] == 0) { du--; dw -= (int64_t)w[base2 + new_proj]; }
            }
        } else if (col == 1) {
            for (int d = 0; d < P->num_d1; d++) {
                int old_proj = t1p[d];
                int p0 = old_proj / q, p1 = old_proj % q;
                int new_proj = p0 * q + gf->add[p1][delta];
                int base0 = P->off1 + ((0 * P->num_d1 + d) * P->q + a) * P->q2;
                int base1 = P->off1 + ((1 * P->num_d1 + d) * P->q + b) * P->q2;
                int base2 = P->off1 + ((2 * P->num_d1 + d) * P->q + c) * P->q2;
                if (cnt[base0 + old_proj] == 1) { du++; dw += (int64_t)w[base0 + old_proj]; }
                if (cnt[base0 + new_proj] == 0) { du--; dw -= (int64_t)w[base0 + new_proj]; }
                if (cnt[base1 + old_proj] == 1) { du++; dw += (int64_t)w[base1 + old_proj]; }
                if (cnt[base1 + new_proj] == 0) { du--; dw -= (int64_t)w[base1 + new_proj]; }
                if (cnt[base2 + old_proj] == 1) { du++; dw += (int64_t)w[base2 + old_proj]; }
                if (cnt[base2 + new_proj] == 0) { du--; dw -= (int64_t)w[base2 + new_proj]; }
            }
        } else {
            for (int d = 0; d < P->num_d1; d++) {
                int v = P->d1_v[d], wd = P->d1_w[d];
                if (v == 0 && wd == 0) continue;
                int old_proj = t1p[d];
                int p0 = old_proj / q, p1 = old_proj % q;
                int np0 = gf->sub[p0][gf->mul[v][delta]];
                int np1 = gf->sub[p1][gf->mul[wd][delta]];
                int new_proj = np0 * q + np1;
                int base0 = P->off1 + ((0 * P->num_d1 + d) * P->q + a) * P->q2;
                int base1 = P->off1 + ((1 * P->num_d1 + d) * P->q + b) * P->q2;
                int base2 = P->off1 + ((2 * P->num_d1 + d) * P->q + c) * P->q2;
                if (cnt[base0 + old_proj] == 1) { du++; dw += (int64_t)w[base0 + old_proj]; }
                if (cnt[base0 + new_proj] == 0) { du--; dw -= (int64_t)w[base0 + new_proj]; }
                if (cnt[base1 + old_proj] == 1) { du++; dw += (int64_t)w[base1 + old_proj]; }
                if (cnt[base1 + new_proj] == 0) { du--; dw -= (int64_t)w[base1 + new_proj]; }
                if (cnt[base2 + old_proj] == 1) { du++; dw += (int64_t)w[base2 + old_proj]; }
                if (cnt[base2 + new_proj] == 0) { du--; dw -= (int64_t)w[base2 + new_proj]; }
            }
        }

        /* Typ 2 */
        int sp0 = a * q + b, sp1 = a * q + c, sp2 = b * q + c;
        const uint8_t *t2v = S->t2_val[r];
        for (int n = 0; n < P->num_n2; n++) {
            int dval;
            if (col == 0) dval = delta;
            else if (col == 1) {
                int al = P->n2_al[n];
                if (al == 0) continue;
                dval = gf->mul[al][delta];
            } else {
                int be = P->n2_be[n];
                if (be == 0) continue;
                dval = gf->mul[be][delta];
            }
            int ov = t2v[n];
            int nv = gf->add[ov][dval];
            int base0 = P->off2 + ((0 * P->num_n2 + n) * P->q2 + sp0) * q;
            int base1 = P->off2 + ((1 * P->num_n2 + n) * P->q2 + sp1) * q;
            int base2 = P->off2 + ((2 * P->num_n2 + n) * P->q2 + sp2) * q;
            if (cnt[base0 + ov] == 1) { du++; dw += (int64_t)w[base0 + ov]; }
            if (cnt[base0 + nv] == 0) { du--; dw -= (int64_t)w[base0 + nv]; }
            if (cnt[base1 + ov] == 1) { du++; dw += (int64_t)w[base1 + ov]; }
            if (cnt[base1 + nv] == 0) { du--; dw -= (int64_t)w[base1 + nv]; }
            if (cnt[base2 + ov] == 1) { du++; dw += (int64_t)w[base2 + ov]; }
            if (cnt[base2 + nv] == 0) { du--; dw -= (int64_t)w[base2 + nv]; }
        }
    } else {
        int u = col - 3;
        int a = S->rows[r][3], b = S->rows[r][4], c = S->rows[r][5];
        int na = a, nb = b, nc = c;
        if (u == 0) na = new_val;
        else if (u == 1) nb = new_val;
        else nc = new_val;

        /* Typ 3 */
        int old3 = id_t3(P, a, b, c);
        int new3 = id_t3(P, na, nb, nc);
        if (cnt[old3] == 1) { du++; dw += (int64_t)w[old3]; }
        if (cnt[new3] == 0) { du--; dw -= (int64_t)w[new3]; }

        /* Typ 1: only column u */
        const uint8_t *t1p = S->t1_proj[r];
        for (int d = 0; d < P->num_d1; d++) {
            int proj = t1p[d];
            int oi = id_t1(P, u, d, old_val, proj);
            int ni = id_t1(P, u, d, new_val, proj);
            if (cnt[oi] == 1) { du++; dw += (int64_t)w[oi]; }
            if (cnt[ni] == 0) { du--; dw -= (int64_t)w[ni]; }
        }

        /* Typ 2: only the 2 pairs containing u */
        const uint8_t *t2v = S->t2_val[r];
        int pA = U_PAIRS[u][0], pB = U_PAIRS[u][1];
        int oA = S->rows[r][3 + U_OTHER[u][0]], oB = S->rows[r][3 + U_OTHER[u][1]];
        int old_spA = U_IS_SECOND[u][0] ? (oA * q + old_val) : (old_val * q + oA);
        int new_spA = U_IS_SECOND[u][0] ? (oA * q + new_val) : (new_val * q + oA);
        int old_spB = U_IS_SECOND[u][1] ? (oB * q + old_val) : (old_val * q + oB);
        int new_spB = U_IS_SECOND[u][1] ? (oB * q + new_val) : (new_val * q + oB);
        for (int n = 0; n < P->num_n2; n++) {
            int val = t2v[n];
            int oiA = id_t2(P, pA, n, old_spA, val);
            int niA = id_t2(P, pA, n, new_spA, val);
            int oiB = id_t2(P, pB, n, old_spB, val);
            int niB = id_t2(P, pB, n, new_spB, val);
            if (cnt[oiA] == 1) { du++; dw += (int64_t)w[oiA]; }
            if (cnt[niA] == 0) { du--; dw -= (int64_t)w[niA]; }
            if (cnt[oiB] == 1) { du++; dw += (int64_t)w[oiB]; }
            if (cnt[niB] == 0) { du--; dw -= (int64_t)w[niB]; }
        }
    }

    *out_du = du;
    *out_dw = dw;
}

static void apply_move(State *S, int r, int col, int new_val) {
    const Problem *P = S->P;
    const GF *gf = &P->gf;
    int q = P->q;
    int old_val = S->rows[r][col];
    if (old_val == new_val) return;

    if (col < 3) {
        int c0 = S->rows[r][0], c1 = S->rows[r][1], c2 = S->rows[r][2];
        int nc0 = c0, nc1 = c1, nc2 = c2;
        if (col == 0) nc0 = new_val;
        else if (col == 1) nc1 = new_val;
        else nc2 = new_val;

        dec_inter(S, id_t0(P, c0, c1, c2));
        inc_inter(S, id_t0(P, nc0, nc1, nc2));

        int a = S->rows[r][3], b = S->rows[r][4], c = S->rows[r][5];
        int delta = gf->sub[new_val][old_val];

        uint8_t *t1p = S->t1_proj[r];
        for (int d = 0; d < P->num_d1; d++) {
            int old_proj = t1p[d];
            int p0 = old_proj / q, p1 = old_proj % q;
            int np0 = p0, np1 = p1;
            if (col == 0) np0 = gf->add[p0][delta];
            else if (col == 1) np1 = gf->add[p1][delta];
            else {
                int v = P->d1_v[d], wd = P->d1_w[d];
                if (v == 0 && wd == 0) continue;
                np0 = gf->sub[p0][gf->mul[v][delta]];
                np1 = gf->sub[p1][gf->mul[wd][delta]];
            }
            int new_proj = np0 * q + np1;
            t1p[d] = (uint8_t)new_proj;
            dec_inter(S, id_t1(P, 0, d, a, old_proj));
            inc_inter(S, id_t1(P, 0, d, a, new_proj));
            dec_inter(S, id_t1(P, 1, d, b, old_proj));
            inc_inter(S, id_t1(P, 1, d, b, new_proj));
            dec_inter(S, id_t1(P, 2, d, c, old_proj));
            inc_inter(S, id_t1(P, 2, d, c, new_proj));
        }

        int sp0 = a * q + b, sp1 = a * q + c, sp2 = b * q + c;
        uint8_t *t2v = S->t2_val[r];
        for (int n = 0; n < P->num_n2; n++) {
            int dval;
            if (col == 0) dval = delta;
            else if (col == 1) {
                int al = P->n2_al[n];
                if (al == 0) continue;
                dval = gf->mul[al][delta];
            } else {
                int be = P->n2_be[n];
                if (be == 0) continue;
                dval = gf->mul[be][delta];
            }
            int ov = t2v[n];
            int nv = gf->add[ov][dval];
            t2v[n] = (uint8_t)nv;
            dec_inter(S, id_t2(P, 0, n, sp0, ov));
            inc_inter(S, id_t2(P, 0, n, sp0, nv));
            dec_inter(S, id_t2(P, 1, n, sp1, ov));
            inc_inter(S, id_t2(P, 1, n, sp1, nv));
            dec_inter(S, id_t2(P, 2, n, sp2, ov));
            inc_inter(S, id_t2(P, 2, n, sp2, nv));
        }
    } else {
        int u = col - 3;
        int a = S->rows[r][3], b = S->rows[r][4], c = S->rows[r][5];
        int na = a, nb = b, nc = c;
        if (u == 0) na = new_val;
        else if (u == 1) nb = new_val;
        else nc = new_val;

        dec_inter(S, id_t3(P, a, b, c));
        inc_inter(S, id_t3(P, na, nb, nc));

        const uint8_t *t1p = S->t1_proj[r];
        for (int d = 0; d < P->num_d1; d++) {
            int proj = t1p[d];
            dec_inter(S, id_t1(P, u, d, old_val, proj));
            inc_inter(S, id_t1(P, u, d, new_val, proj));
        }

        const uint8_t *t2v = S->t2_val[r];
        int pA = U_PAIRS[u][0], pB = U_PAIRS[u][1];
        int oA = S->rows[r][3 + U_OTHER[u][0]], oB = S->rows[r][3 + U_OTHER[u][1]];
        int old_spA = U_IS_SECOND[u][0] ? (oA * q + old_val) : (old_val * q + oA);
        int new_spA = U_IS_SECOND[u][0] ? (oA * q + new_val) : (new_val * q + oA);
        int old_spB = U_IS_SECOND[u][1] ? (oB * q + old_val) : (old_val * q + oB);
        int new_spB = U_IS_SECOND[u][1] ? (oB * q + new_val) : (new_val * q + oB);
        for (int n = 0; n < P->num_n2; n++) {
            int val = t2v[n];
            dec_inter(S, id_t2(P, pA, n, old_spA, val));
            inc_inter(S, id_t2(P, pA, n, new_spA, val));
            dec_inter(S, id_t2(P, pB, n, old_spB, val));
            inc_inter(S, id_t2(P, pB, n, new_spB, val));
        }
    }

    S->rows[r][col] = (uint8_t)new_val;
}

/* ---------- Focused Candidate Generation ---------- */

typedef struct {
    int r;
    int col;
    int val;
} Move;

static int collect_repair_moves(const State *S, int id, Move *out, int max_out) {
    const Problem *P = S->P;
    const GF *gf = &P->gf;
    int q = P->q;
    int n_out = 0;

    if (id < P->off1) {
        /* Typ 0: (c0*, c1*, c2*) */
        int rem = id - P->off0;
        int c2s = rem % q; rem /= q;
        int c1s = rem % q;
        int c0s = rem / q;
        for (int r = 0; r < S->m && n_out < max_out; r++) {
            int m0 = (S->rows[r][0] == c0s);
            int m1 = (S->rows[r][1] == c1s);
            int m2 = (S->rows[r][2] == c2s);
            if (m0 + m1 + m2 == 2) {
                if (!m0) out[n_out++] = (Move){r, 0, c0s};
                else if (!m1) out[n_out++] = (Move){r, 1, c1s};
                else out[n_out++] = (Move){r, 2, c2s};
            }
        }
    } else if (id < P->off2) {
        /* Typ 1: (u, d, s*, proj*) */
        int rem = id - P->off1;
        int projs = rem % P->q2; rem /= P->q2;
        int ss = rem % q; rem /= q;
        int d = rem % P->num_d1;
        int u = rem / P->num_d1;
        int p0s = projs / q, p1s = projs % q;
        int v = P->d1_v[d], wd = P->d1_w[d];
        int ucol = 3 + u;
        for (int r = 0; r < S->m && n_out + 4 <= max_out; r++) {
            int proj = S->t1_proj[r][d];
            int su = S->rows[r][ucol];
            if (proj == projs) {
                if (su != ss) out[n_out++] = (Move){r, ucol, ss};
            } else if (su == ss) {
                int p0 = proj / q, p1 = proj % q;
                int c0 = S->rows[r][0], c1 = S->rows[r][1], c2 = S->rows[r][2];
                if (p1 == p1s) {
                    int nc0 = gf->add[p0s][gf->mul[v][c2]];
                    if (nc0 != c0) out[n_out++] = (Move){r, 0, nc0};
                }
                if (p0 == p0s) {
                    int nc1 = gf->add[p1s][gf->mul[wd][c2]];
                    if (nc1 != c1) out[n_out++] = (Move){r, 1, nc1};
                }
                if (v != 0) {
                    int nc2 = gf->mul[gf->sub[c0][p0s]][gf->inv[v]];
                    if (nc2 != c2 && gf->sub[c1][gf->mul[wd][nc2]] == p1s) {
                        out[n_out++] = (Move){r, 2, nc2};
                    }
                } else if (wd != 0 && c0 == p0s) {
                    int nc2 = gf->mul[gf->sub[c1][p1s]][gf->inv[wd]];
                    if (nc2 != c2) out[n_out++] = (Move){r, 2, nc2};
                }
            }
        }
    } else if (id < P->off3) {
        /* Typ 2: (p, n, sp*, val*) */
        int rem = id - P->off2;
        int vals = rem % q; rem /= q;
        int sps = rem % P->q2; rem /= P->q2;
        int n = rem % P->num_n2;
        int p = rem / P->num_n2;
        int s1s = sps / q, s2s = sps % q;
        int col1 = 3 + PAIR_U1[p], col2 = 3 + PAIR_U2[p];
        int al = P->n2_al[n], be = P->n2_be[n];
        for (int r = 0; r < S->m && n_out + 4 <= max_out; r++) {
            int s1 = S->rows[r][col1], s2 = S->rows[r][col2];
            int val = S->t2_val[r][n];
            if (val == vals) {
                if (s1 == s1s && s2 != s2s) out[n_out++] = (Move){r, col2, s2s};
                if (s2 == s2s && s1 != s1s) out[n_out++] = (Move){r, col1, s1s};
            } else if (s1 == s1s && s2 == s2s) {
                int c0 = S->rows[r][0], c1 = S->rows[r][1], c2 = S->rows[r][2];
                int nc0 = gf->sub[vals][gf->add[gf->mul[al][c1]][gf->mul[be][c2]]];
                if (nc0 != c0) out[n_out++] = (Move){r, 0, nc0};
                if (al != 0) {
                    int rhs = gf->sub[vals][gf->add[c0][gf->mul[be][c2]]];
                    int nc1 = gf->mul[rhs][gf->inv[al]];
                    if (nc1 != c1) out[n_out++] = (Move){r, 1, nc1};
                }
                if (be != 0) {
                    int rhs = gf->sub[vals][gf->add[c0][gf->mul[al][c1]]];
                    int nc2 = gf->mul[rhs][gf->inv[be]];
                    if (nc2 != c2) out[n_out++] = (Move){r, 2, nc2};
                }
            }
        }
    } else {
        /* Typ 3: (a*, b*, c*) */
        int rem = id - P->off3;
        int cs = rem % q; rem /= q;
        int bs = rem % q;
        int as = rem / q;
        for (int r = 0; r < S->m && n_out < max_out; r++) {
            int m0 = (S->rows[r][3] == as);
            int m1 = (S->rows[r][4] == bs);
            int m2 = (S->rows[r][5] == cs);
            if (m0 + m1 + m2 == 2) {
                if (!m0) out[n_out++] = (Move){r, 3, as};
                else if (!m1) out[n_out++] = (Move){r, 4, bs};
                else out[n_out++] = (Move){r, 5, cs};
            }
        }
    }
    return n_out;
}

/* ---------- Self-Test ---------- */

static int run_self_test(void) {
    const struct { int q; Mode mode; int t; int m; } cases[] = {
        {3, MODE_TSPEC, 3, 35},
        {3, MODE_FULL_BG3, 3, 40},
        {4, MODE_TSPEC, 4, 80},
        {5, MODE_TSPEC, 4, 180},
        {5, MODE_FULL_BG3, 4, 200},
    };
    int n_cases = (int)(sizeof(cases) / sizeof(cases[0]));
    State *S = calloc(1, sizeof(State));
    State *Ref = calloc(1, sizeof(State));
    if (!S || !Ref) return 1;

    for (int ci = 0; ci < n_cases; ci++) {
        Problem P;
        if (problem_init(&P, cases[ci].q, cases[ci].mode, cases[ci].t) != 0) {
            fprintf(stderr, "self-test case %d problem_init failed\n", ci);
            free(S); free(Ref);
            return 1;
        }
        memset(S, 0, sizeof(*S));
        S->P = &P;
        S->m = cases[ci].m;
        S->base_w03 = 1;
        rng_seed(&S->rng, 1234567ULL + (uint64_t)ci * 99991ULL);
        state_reset_weights_tabu(S);
        state_init_rows(S, INIT_BASE, NULL, 0);

        /* Assign non-trivial weights to also test dw! */
        for (int id = 0; id < P.total_inter; id++) S->weight[id] = 1 + (uint32_t)(id % 7);

        for (int step = 0; step < 2000; step++) {
            int r = (int)rng_bound(&S->rng, (uint32_t)S->m);
            int col = (int)rng_bound(&S->rng, 6);
            int nv = (int)rng_bound(&S->rng, (uint32_t)P.q);

            int64_t w_before = 0;
            for (int i = 0; i < S->unc_count; i++) w_before += S->weight[S->unc_list[i]];
            int u_before = S->unc_count;

            int du = 0;
            int64_t dw = 0;
            eval_move(S, r, col, nv, &du, &dw);
            apply_move(S, r, col, nv);

            int64_t w_after = 0;
            for (int i = 0; i < S->unc_count; i++) w_after += S->weight[S->unc_list[i]];
            int u_after = S->unc_count;

            if (u_after - u_before != du || w_after - w_before != dw) {
                fprintf(stderr, "SELF-TEST FAIL case %d step %d (col=%d): du=%d vs %d, dw=%lld vs %lld\n",
                        ci, step, col, du, u_after - u_before, (long long)dw, (long long)(w_after - w_before));
                free(S); free(Ref);
                return 1;
            }

            if (step % 200 == 199) {
                /* Full rebuild comparison */
                memset(Ref, 0, sizeof(*Ref));
                Ref->P = &P;
                Ref->m = S->m;
                memcpy(Ref->rows, S->rows, (size_t)S->m * 6);
                state_rebuild(Ref);
                if (Ref->unc_count != S->unc_count ||
                    memcmp(Ref->cnt, S->cnt, (size_t)P.total_inter * sizeof(uint16_t)) != 0 ||
                    memcmp(Ref->unc_by_type, S->unc_by_type, sizeof(S->unc_by_type)) != 0) {
                    fprintf(stderr, "SELF-TEST REBUILD MISMATCH case %d step %d\n", ci, step);
                    free(S); free(Ref);
                    return 1;
                }
                /* Verify repair moves actually cover chosen uncovered interaction */
                if (S->unc_count > 0) {
                    int eid = S->unc_list[rng_bound(&S->rng, (uint32_t)S->unc_count)];
                    Move cands[256];
                    int nc = collect_repair_moves(S, eid, cands, 256);
                    for (int k = 0; k < nc; k++) {
                        int oldv = S->rows[cands[k].r][cands[k].col];
                        apply_move(S, cands[k].r, cands[k].col, cands[k].val);
                        if (S->cnt[eid] == 0) {
                            fprintf(stderr, "SELF-TEST REPAIR FAIL case %d eid=%d (type=%d) move=(%d,%d,%d)\n",
                                    ci, eid, inter_type(&P, eid), cands[k].r, cands[k].col, cands[k].val);
                            free(S); free(Ref);
                            return 1;
                        }
                        apply_move(S, cands[k].r, cands[k].col, oldv);
                    }
                }
            }
        }
        printf("self-test case %d (q=%d mode=%s t=%d m=%d |D1|=%d |N2|=%d inter=%d): PASS (2000 moves, 0 diffs)\n",
               ci, P.q, P.mode == MODE_TSPEC ? "tspec" : "full-bg3", P.t, S->m, P.num_d1, P.num_n2, P.total_inter);
    }
    free(S);
    free(Ref);
    return 0;
}

/* ---------- Worker Thread ---------- */

typedef struct {
    const Problem *P;
    int m;
    int tid;
    uint64_t seed;
    double time_limit;
    double start_time;
    InitMode init_mode;
    AlgoMode algo;
    const uint8_t (*init_file_rows)[6];
    int init_file_m;
    int tenure_base;
    int tenure_span;
    int smooth_period;
    uint32_t base_w03;
    double rw_prob;
    uint64_t restart_stag;
    atomic_int *stop_flag;

    /* outputs */
    int found_zero;
    int best_unc;
    int best_by_type[4];
    uint8_t best_rows[MAX_M][6];
    uint64_t steps;
    uint64_t evals;
    uint64_t restarts;
    double elapsed;
} WorkerArgs;

static void *worker_run(void *arg) {
    WorkerArgs *W = (WorkerArgs *)arg;
    State *S = calloc(1, sizeof(State));
    if (!S) return NULL;
    S->P = W->P;
    S->m = W->m;
    S->base_w03 = W->base_w03 > 0 ? W->base_w03 : 1U;
    S->best_unc = 1000000000;
    rng_seed(&S->rng, W->seed);

    /* Diversify thread 1 slightly when multi-threaded */
    int tenure_base = W->tenure_base + (W->tid % 2) * 4;
    int tenure_span = W->tenure_span + (W->tid % 2) * 4;
    int smooth_period = W->smooth_period * (1 + (W->tid % 2));
    double rw_prob = W->rw_prob;

    InitMode cur_init = W->init_mode;
    state_reset_weights_tabu(S);
    state_init_rows(S, cur_init, W->init_file_rows, W->init_file_m);
    state_record_best(S);

    if (S->unc_count == 0) {
        atomic_store(W->stop_flag, 1);
    }

    Move cands[512];
    uint64_t steps_since_best = 0;
    double last_check = W->start_time;

    if (W->algo == ALGO_SA) {
        double T_start = 2.0;
        double T_end = 0.08;
        double T = T_start;
        while (!atomic_load_explicit(W->stop_flag, memory_order_relaxed)) {
            if ((S->step & 4095ULL) == 0) {
                double now = wall_time();
                double el = now - W->start_time;
                if (el >= W->time_limit) break;
                double frac = el / W->time_limit;
                T = T_start * pow(T_end / T_start, frac);
                (void)last_check;
            }
            if (S->unc_count == 0) {
                atomic_store(W->stop_flag, 1);
                break;
            }
            int r, col, nv;
            if ((S->step & 3ULL) != 0) {
                /* 75% focused SA move */
                int eid = S->unc_list[rng_bound(&S->rng, (uint32_t)S->unc_count)];
                int nc = collect_repair_moves(S, eid, cands, 512);
                if (nc > 0) {
                    Move mv = cands[rng_bound(&S->rng, (uint32_t)nc)];
                    r = mv.r; col = mv.col; nv = mv.val;
                } else {
                    r = (int)rng_bound(&S->rng, (uint32_t)S->m);
                    col = (int)rng_bound(&S->rng, 6);
                    nv = (S->rows[r][col] + 1 + (int)rng_bound(&S->rng, (uint32_t)(W->P->q - 1))) % W->P->q;
                }
            } else {
                r = (int)rng_bound(&S->rng, (uint32_t)S->m);
                col = (int)rng_bound(&S->rng, 6);
                nv = (S->rows[r][col] + 1 + (int)rng_bound(&S->rng, (uint32_t)(W->P->q - 1))) % W->P->q;
            }
            int du = 0;
            int64_t dw = 0;
            eval_move(S, r, col, nv, &du, &dw);
            S->evals++;
            S->step++;
            if (du <= 0 || rng_double(&S->rng) < exp(-(double)du / T)) {
                apply_move(S, r, col, nv);
                if (S->unc_count < S->best_unc) {
                    state_record_best(S);
                    if (S->unc_count == 0) {
                        atomic_store(W->stop_flag, 1);
                        break;
                    }
                }
            }
        }
    } else {
        /* Focused Tabu + PAWS + ILS/Restart */
        while (!atomic_load_explicit(W->stop_flag, memory_order_relaxed)) {
            if ((S->step & 2047ULL) == 0) {
                double now = wall_time();
                if (now - W->start_time >= W->time_limit) break;
            }
            if (S->unc_count == 0) {
                atomic_store(W->stop_flag, 1);
                break;
            }

            /* Pick a random uncovered interaction */
            int eid = S->unc_list[rng_bound(&S->rng, (uint32_t)S->unc_count)];
            int nc = collect_repair_moves(S, eid, cands, 512);
            if (nc == 0) {
                for (int k = 0; k < 32; k++) {
                    int r = (int)rng_bound(&S->rng, (uint32_t)S->m);
                    int col = (int)rng_bound(&S->rng, 6);
                    int nv = (S->rows[r][col] + 1 + (int)rng_bound(&S->rng, (uint32_t)(W->P->q - 1))) % W->P->q;
                    cands[nc++] = (Move){r, col, nv};
                }
            }

            int best_idx = -1;
            int64_t best_dw = (1LL << 60);
            int best_du = 1000000000;
            int ties = 0;

            int best_any_idx = 0;
            int64_t best_any_dw = (1LL << 60);

            for (int i = 0; i < nc; i++) {
                int r = cands[i].r, col = cands[i].col, nv = cands[i].val;
                int du = 0;
                int64_t dw = 0;
                eval_move(S, r, col, nv, &du, &dw);
                S->evals++;

                if (dw < best_any_dw) {
                    best_any_dw = dw;
                    best_any_idx = i;
                }

                int is_tabu = (S->tabu_val[r][col][nv] > S->step);
                int aspire = (S->unc_count + du < S->best_unc) || (S->unc_count + du == 0);
                if (is_tabu && !aspire) continue;

                if (dw < best_dw || (dw == best_dw && du < best_du)) {
                    best_dw = dw;
                    best_du = du;
                    best_idx = i;
                    ties = 1;
                } else if (dw == best_dw && du == best_du) {
                    ties++;
                    if (rng_bound(&S->rng, (uint32_t)ties) == 0) best_idx = i;
                }
            }

            int chosen;
            if (best_idx < 0) {
                chosen = best_any_idx;
                best_dw = best_any_dw;
            } else if (best_dw >= 0 && rng_double(&S->rng) < rw_prob) {
                chosen = (int)rng_bound(&S->rng, (uint32_t)nc);
            } else {
                chosen = best_idx;
            }

            /* PAWS weight bump on plateau / local minimum */
            if (best_dw >= 0) {
                for (int i = 0; i < S->unc_count; i++) {
                    int uid = S->unc_list[i];
                    S->weight[uid] += (uid < W->P->off1 || uid >= W->P->off3) ? S->base_w03 : 1U;
                }
                S->bumps++;
                if (smooth_period > 0 && (S->bumps % (uint64_t)smooth_period) == 0) {
                    for (int id = 0; id < W->P->total_inter; id++) {
                        uint32_t fw = floor_weight(S, id);
                        if (S->weight[id] > fw) {
                            uint32_t dec = (fw > 1U) ? ((S->weight[id] - fw >= fw) ? fw : (S->weight[id] - fw)) : 1U;
                            S->weight[id] -= dec;
                        }
                    }
                }
            }

            int r = cands[chosen].r, col = cands[chosen].col, nv = cands[chosen].val;
            int ov = S->rows[r][col];
            int ten = tenure_base + (tenure_span > 0 ? (int)rng_bound(&S->rng, (uint32_t)tenure_span) : 0);
            S->tabu_val[r][col][ov] = S->step + (uint64_t)ten;

            apply_move(S, r, col, nv);
            S->step++;

            if (S->unc_count < S->best_unc) {
                state_record_best(S);
                steps_since_best = 0;
                if (S->unc_count == 0) {
                    atomic_store(W->stop_flag, 1);
                    break;
                }
            } else {
                steps_since_best++;
                if (W->restart_stag > 0 && steps_since_best >= W->restart_stag) {
                    S->restarts++;
                    steps_since_best = 0;
                    state_reset_weights_tabu(S);
                    if ((S->restarts & 1ULL) == 1ULL) {
                        /* ILS perturbation from best_rows */
                        memcpy(S->rows, S->best_rows, (size_t)S->m * 6);
                        int kick = S->best_unc + 8;
                        if (kick > S->m) kick = S->m;
                        if (kick < 12) kick = 12;
                        for (int k = 0; k < kick; k++) {
                            int kr = (int)rng_bound(&S->rng, (uint32_t)S->m);
                            int kcol = (int)rng_bound(&S->rng, 6);
                            S->rows[kr][kcol] = (uint8_t)rng_bound(&S->rng, (uint32_t)W->P->q);
                        }
                        state_rebuild(S);
                    } else {
                        /* Fresh restart (alternate base/rand on thread 1) */
                        InitMode rm = (W->tid % 2 == 1 && (S->restarts % 4 == 0)) ? INIT_RAND : cur_init;
                        state_init_rows(S, rm, W->init_file_rows, W->init_file_m);
                    }
                    state_record_best(S);
                }
            }
        }
    }

    W->found_zero = (S->best_unc == 0);
    W->best_unc = S->best_unc;
    for (int i = 0; i < 4; i++) W->best_by_type[i] = S->best_by_type[i];
    memcpy(W->best_rows, S->best_rows, (size_t)S->m * 6);
    W->steps = S->step;
    W->evals = S->evals;
    W->restarts = S->restarts;
    W->elapsed = wall_time() - W->start_time;
    free(S);
    return NULL;
}

/* ---------- I/O Helpers ---------- */

static int read_init_file(const char *path, int q, uint8_t (*rows)[6], int max_m) {
    FILE *fp = fopen(path, "r");
    if (!fp) return -1;
    char line[256];
    int n = 0;
    while (fgets(line, sizeof(line), fp)) {
        char *hash = strchr(line, '#');
        if (hash) *hash = '\0';
        int v[6];
        int got = sscanf(line, "%d %d %d %d %d %d", &v[0], &v[1], &v[2], &v[3], &v[4], &v[5]);
        if (got == 6) {
            if (n >= max_m) { fclose(fp); return -2; }
            for (int j = 0; j < 6; j++) {
                if (v[j] < 0 || v[j] >= q) { fclose(fp); return -3; }
                rows[n][j] = (uint8_t)v[j];
            }
            n++;
        }
    }
    fclose(fp);
    return n;
}

static int write_unique_rows(const char *path, uint8_t (*rows)[6], int m, int *out_unique) {
    FILE *fp = fopen(path, "w");
    if (!fp) return -1;
    int written = 0;
    for (int i = 0; i < m; i++) {
        int dup = 0;
        for (int j = 0; j < i; j++) {
            if (memcmp(rows[i], rows[j], 6) == 0) { dup = 1; break; }
        }
        if (dup) continue;
        fprintf(fp, "%d %d %d %d %d %d\n",
                rows[i][0], rows[i][1], rows[i][2], rows[i][3], rows[i][4], rows[i][5]);
        written++;
    }
    fclose(fp);
    if (out_unique) *out_unique = written;
    return 0;
}

static void usage(const char *prog) {
    fprintf(stderr,
            "Usage: %s --q Q --m M [--mode tspec|full-bg3] [--t T]\n"
            "          [--timeout SECS] [--seed SEED] [--threads N]\n"
            "          [--init base|rand] [--init-file FILE]\n"
            "          [--algo paws|sa] [--tenure B] [--smooth P] [--w03 W] [--rw R] [--restart K]\n"
            "          [--out FILE] [--self-test]\n",
            prog);
}

int main(int argc, char **argv) {
    int q = 0, m = 0, t = 4;
    Mode mode = MODE_TSPEC;
    InitMode init_mode = INIT_BASE;
    AlgoMode algo = ALGO_PAWS;
    double timeout_s = 60.0;
    uint64_t seed = 20260901ULL;
    int threads = 2;
    int tenure_base = 6;
    int tenure_span = 8;
    int smooth_period = 40;
    uint32_t base_w03 = 6;
    double rw_prob = 0.02;
    uint64_t restart_stag = 500000ULL;
    const char *init_file = NULL;
    const char *out_path = NULL;
    int do_self_test = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--self-test") == 0) do_self_test = 1;
        else if (strcmp(argv[i], "--q") == 0 && i + 1 < argc) q = atoi(argv[++i]);
        else if (strcmp(argv[i], "--m") == 0 && i + 1 < argc) m = atoi(argv[++i]);
        else if (strcmp(argv[i], "--t") == 0 && i + 1 < argc) t = atoi(argv[++i]);
        else if (strcmp(argv[i], "--mode") == 0 && i + 1 < argc) {
            i++;
            if (strcmp(argv[i], "tspec") == 0) mode = MODE_TSPEC;
            else if (strcmp(argv[i], "full-bg3") == 0) mode = MODE_FULL_BG3;
            else { fprintf(stderr, "unknown mode: %s\n", argv[i]); return 2; }
        } else if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) timeout_s = atof(argv[++i]);
        else if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) seed = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--threads") == 0 && i + 1 < argc) threads = atoi(argv[++i]);
        else if (strcmp(argv[i], "--init") == 0 && i + 1 < argc) {
            i++;
            if (strcmp(argv[i], "base") == 0) init_mode = INIT_BASE;
            else if (strcmp(argv[i], "rand") == 0) init_mode = INIT_RAND;
            else { fprintf(stderr, "unknown init: %s\n", argv[i]); return 2; }
        } else if (strcmp(argv[i], "--init-file") == 0 && i + 1 < argc) {
            init_file = argv[++i];
            init_mode = INIT_FILE;
        } else if (strcmp(argv[i], "--algo") == 0 && i + 1 < argc) {
            i++;
            if (strcmp(argv[i], "paws") == 0) algo = ALGO_PAWS;
            else if (strcmp(argv[i], "sa") == 0) algo = ALGO_SA;
            else { fprintf(stderr, "unknown algo: %s\n", argv[i]); return 2; }
        } else if (strcmp(argv[i], "--tenure") == 0 && i + 1 < argc) tenure_base = atoi(argv[++i]);
        else if (strcmp(argv[i], "--smooth") == 0 && i + 1 < argc) smooth_period = atoi(argv[++i]);
        else if (strcmp(argv[i], "--w03") == 0 && i + 1 < argc) base_w03 = (uint32_t)atoi(argv[++i]);
        else if (strcmp(argv[i], "--rw") == 0 && i + 1 < argc) rw_prob = atof(argv[++i]);
        else if (strcmp(argv[i], "--restart") == 0 && i + 1 < argc) restart_stag = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--out") == 0 && i + 1 < argc) out_path = argv[++i];
        else { usage(argv[0]); return 2; }
    }

    if (do_self_test) {
        return run_self_test();
    }

    if (q < 3 || m <= 0 || m > MAX_M || threads < 1 || threads > 8) {
        usage(argv[0]);
        return 2;
    }
    if (timeout_s > 90.0) {
        fprintf(stderr, "enforcing hard timeout cap <= 90.0 s (requested %.1f)\n", timeout_s);
        timeout_s = 90.0;
    }

    Problem P;
    if (problem_init(&P, q, mode, t) != 0) {
        fprintf(stderr, "problem_init failed for q=%d mode=%d t=%d\n", q, (int)mode, t);
        return 2;
    }

    static uint8_t init_rows[MAX_M][6];
    int init_file_m = 0;
    if (init_file) {
        init_file_m = read_init_file(init_file, q, init_rows, MAX_M);
        if (init_file_m <= 0) {
            fprintf(stderr, "failed to read init file %s (rc=%d)\n", init_file, init_file_m);
            return 2;
        }
    }

    double t0 = wall_time();
    atomic_int stop_flag = 0;
    WorkerArgs *W = calloc((size_t)threads, sizeof(WorkerArgs));
    pthread_t *th = calloc((size_t)threads, sizeof(pthread_t));

    for (int i = 0; i < threads; i++) {
        W[i].P = &P;
        W[i].m = m;
        W[i].tid = i;
        W[i].seed = seed + (uint64_t)i * 0x9e3779b97f4a7c15ULL;
        W[i].time_limit = timeout_s;
        W[i].start_time = t0;
        W[i].init_mode = init_mode;
        W[i].algo = algo;
        W[i].init_file_rows = init_file ? init_rows : NULL;
        W[i].init_file_m = init_file_m;
        W[i].tenure_base = tenure_base;
        W[i].tenure_span = tenure_span;
        W[i].smooth_period = smooth_period;
        W[i].base_w03 = base_w03;
        W[i].rw_prob = rw_prob;
        W[i].restart_stag = restart_stag;
        W[i].stop_flag = &stop_flag;
        pthread_create(&th[i], NULL, worker_run, &W[i]);
    }
    for (int i = 0; i < threads; i++) pthread_join(th[i], NULL);
    double total_el = wall_time() - t0;

    int best_i = 0;
    uint64_t tot_steps = 0, tot_evals = 0, tot_restarts = 0;
    for (int i = 0; i < threads; i++) {
        tot_steps += W[i].steps;
        tot_evals += W[i].evals;
        tot_restarts += W[i].restarts;
        if (W[i].best_unc < W[best_i].best_unc) best_i = i;
    }

    double mv_per_s = total_el > 0.0 ? (double)tot_steps / total_el : 0.0;
    double ev_per_s = total_el > 0.0 ? (double)tot_evals / total_el : 0.0;

    if (W[best_i].best_unc == 0) {
        int uniq = m;
        if (out_path) {
            if (write_unique_rows(out_path, W[best_i].best_rows, m, &uniq) != 0) {
                fprintf(stderr, "failed writing %s\n", out_path);
                free(W); free(th);
                return 3;
            }
        }
        printf("SOLVED q=%d mode=%s t=%d m=%d (unique=%d) |D1|=%d |N2|=%d | "
               "time=%.3fs steps=%llu (%.0f mv/s, %.0f ev/s) restarts=%llu winner_tid=%d seed=%llu\n",
               q, mode == MODE_TSPEC ? "tspec" : "full-bg3", t, m, uniq, P.num_d1, P.num_n2,
               total_el, (unsigned long long)tot_steps, mv_per_s, ev_per_s,
               (unsigned long long)tot_restarts, best_i, (unsigned long long)seed);
        free(W); free(th);
        return 0;
    } else {
        printf("TIMEOUT (best_unc=%d) q=%d mode=%s t=%d m=%d |D1|=%d |N2|=%d | "
               "by_type=(%d,%d,%d,%d) | time=%.3fs steps=%llu (%.0f mv/s, %.0f ev/s) restarts=%llu seed=%llu\n",
               W[best_i].best_unc, q, mode == MODE_TSPEC ? "tspec" : "full-bg3", t, m, P.num_d1, P.num_n2,
               W[best_i].best_by_type[0], W[best_i].best_by_type[1],
               W[best_i].best_by_type[2], W[best_i].best_by_type[3],
               total_el, (unsigned long long)tot_steps, mv_per_s, ev_per_s,
               (unsigned long long)tot_restarts, (unsigned long long)seed);
        free(W); free(th);
        return 1;
    }
}
