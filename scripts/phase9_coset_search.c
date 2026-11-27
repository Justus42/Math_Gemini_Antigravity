/*
 * Phase 9: Fast C local search (Parallel Tempering SA + focused 1/2-flip proposals)
 * for coset-union covering arrays (Sitjar Lemma 1) without 2-zero-column restriction,
 * supporting both free representatives and F_q*-scaling-invariant orbits (--scale-inv).
 *
 * Also supports --selftest and --prune (greedy redundancy deletion on rolled-out CA).
 *
 * Compile:
 *   gcc -O3 -march=native -pthread -Wall -Wextra -o /tmp/phase9/coset_search scripts/phase9_coset_search.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <pthread.h>
#include <stdatomic.h>

#define MAX_K 10
#define MAX_T 5
#define MAX_D 3
#define MAX_Q 7
#define MAX_Q2 49
#define MAX_SUB 126
#define MAX_M 100
#define MAX_PAIRS_IN_SUB 15
#define N_REP 8

typedef struct {
    const char *name;
    int q, k, t, d;
    int G[MAX_D][MAX_K];
} CodeSpec;

static const CodeSpec SPECS[] = {
    {
        "c1", 5, 7, 4, 2,
        {
            {1, 1, 1, 1, 1, 0, 1},
            {0, 1, 2, 3, 4, 1, 0}
        }
    },
    {
        "c2", 5, 7, 4, 2,
        {
            {1, 1, 1, 1, 1, 0, 0},
            {0, 1, 2, 3, 4, 1, 0}
        }
    },
    {
        "c0", 5, 7, 4, 2,
        {
            {1, 1, 1, 1, 1, 0, 0},
            {0, 1, 2, 3, 4, 0, 0}
        }
    },
    {
        "all1_5", 5, 7, 3, 1,
        {
            {1, 1, 1, 1, 1, 1, 1}
        }
    },
    {
        "all1_7", 7, 9, 3, 1,
        {
            {1, 1, 1, 1, 1, 1, 1, 1, 1}
        }
    }
};
static const int NUM_SPECS = (int)(sizeof(SPECS) / sizeof(SPECS[0]));

/* Precomputed problem geometry */
static CodeSpec SPEC;
static int Q, K, T, D, Q2;
static int SCALE_INV = 0;
static int HAS_ZERO = 0;
static int N_TARGETS = 0;     /* Q2 for free mode, Q+2 for scale-inv mode */
static int TARGET_START = 0;  /* 0 normally; 1 if SCALE_INV && HAS_ZERO */
static uint8_t SYN_TO_TGT[MAX_Q2]; /* identity in free mode; ray id in 0..Q+1 in scale-inv mode */

static int INV_Q[MAX_Q];
static int SUB_ADD[MAX_Q2][MAX_Q2];
static int SUB_DIFF[MAX_Q2][MAX_Q2];

static int N_SUB;
static int SUBS[MAX_SUB][MAX_T];
static int H_MAT[MAX_SUB][2][MAX_T];
static int H_COL[MAX_SUB][MAX_K][2];

static int COL_DEG[MAX_K];
static int COL_SUBS[MAX_K][MAX_SUB];
static uint8_t SHIFT1[MAX_K][MAX_SUB][MAX_Q][MAX_Q2];

typedef struct {
    int n_subs;
    int subs[MAX_SUB];
    int e1[MAX_SUB];
    int e2[MAX_SUB];
} PairSubs;
static PairSubs PAIR_SUBS[MAX_K][MAX_K];

static int SUB_FREE_COLS[MAX_SUB][MAX_T];
static int SUB_N_FREE[MAX_SUB];
static int8_t SOLVE1[MAX_SUB][MAX_T][MAX_Q2];

typedef struct {
    int j1, j2;
    int8_t dv1[MAX_Q2];
    int8_t dv2[MAX_Q2];
} SubPairSolver;
static int SUB_N_PAIR[MAX_SUB];
static SubPairSolver SUB_PAIR[MAX_SUB][MAX_PAIRS_IN_SUB];

static inline uint64_t splitmix64(uint64_t *x) {
    uint64_t z = (*x += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

typedef struct {
    uint64_t s[2];
} Rng;

static inline void rng_init(Rng *r, uint64_t seed) {
    r->s[0] = splitmix64(&seed);
    r->s[1] = splitmix64(&seed);
    if (r->s[0] == 0 && r->s[1] == 0) r->s[0] = 1;
}

static inline uint64_t rng_next(Rng *r) {
    uint64_t s1 = r->s[0];
    const uint64_t s0 = r->s[1];
    r->s[0] = s0;
    s1 ^= s1 << 23;
    r->s[1] = s1 ^ s0 ^ (s1 >> 18) ^ (s0 >> 5);
    return r->s[1] + s0;
}

static inline int rng_int(Rng *r, int bound) {
    return (int)(rng_next(r) % (uint64_t)bound);
}

static inline double rng_dbl(Rng *r) {
    return (double)(rng_next(r) >> 11) * (1.0 / 9007199254740992.0);
}

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static void init_subsets_rec(int start, int depth, int cur[MAX_T]) {
    if (depth == T) {
        for (int i = 0; i < T; i++) SUBS[N_SUB][i] = cur[i];
        N_SUB++;
        return;
    }
    for (int c = start; c <= K - (T - depth); c++) {
        cur[depth] = c;
        init_subsets_rec(c + 1, depth + 1, cur);
    }
}

static void init_geometry(const CodeSpec *spec) {
    SPEC = *spec;
    Q = spec->q;
    K = spec->k;
    T = spec->t;
    D = spec->d;
    Q2 = Q * Q;

    INV_Q[0] = 0;
    for (int a = 1; a < Q; a++) {
        for (int b = 1; b < Q; b++) {
            if ((a * b) % Q == 1) { INV_Q[a] = b; break; }
        }
    }

    for (int u = 0; u < Q2; u++) {
        int u0 = u / Q, u1 = u % Q;
        for (int v = 0; v < Q2; v++) {
            int v0 = v / Q, v1 = v % Q;
            SUB_ADD[u][v] = ((u0 + v0) % Q) * Q + ((u1 + v1) % Q);
            SUB_DIFF[u][v] = ((u0 - v0 + Q) % Q) * Q + ((u1 - v1 + Q) % Q);
        }
        if (!SCALE_INV) {
            SYN_TO_TGT[u] = (uint8_t)u;
        } else {
            if (u0 == 0 && u1 == 0) SYN_TO_TGT[u] = 0;
            else if (u0 != 0) SYN_TO_TGT[u] = (uint8_t)(1 + (u1 * INV_Q[u0]) % Q);
            else SYN_TO_TGT[u] = (uint8_t)(Q + 1);
        }
    }
    N_TARGETS = SCALE_INV ? (Q + 2) : Q2;
    TARGET_START = (SCALE_INV && HAS_ZERO) ? 1 : 0;

    N_SUB = 0;
    int cur[MAX_T];
    init_subsets_rec(0, 0, cur);
    memset(H_COL, 0, sizeof(H_COL));

    for (int s = 0; s < N_SUB; s++) {
        int A[MAX_D][MAX_T];
        for (int r = 0; r < D; r++)
            for (int c = 0; c < T; c++)
                A[r][c] = ((spec->G[r][SUBS[s][c]] % Q) + Q) % Q;

        int piv_col[MAX_D];
        int is_piv[MAX_T];
        memset(is_piv, 0, sizeof(is_piv));
        int rank = 0;
        for (int c = 0; c < T && rank < D; c++) {
            int p = -1;
            for (int r = rank; r < D; r++) if (A[r][c] != 0) { p = r; break; }
            if (p < 0) continue;
            if (p != rank) {
                for (int j = 0; j < T; j++) {
                    int tmp = A[p][j]; A[p][j] = A[rank][j]; A[rank][j] = tmp;
                }
            }
            int inv = INV_Q[A[rank][c]];
            for (int j = 0; j < T; j++) A[rank][j] = (A[rank][j] * inv) % Q;
            for (int r = 0; r < D; r++) {
                if (r != rank && A[r][c] != 0) {
                    int f = A[r][c];
                    for (int j = 0; j < T; j++)
                        A[r][j] = (A[r][j] - f * A[rank][j] % Q + Q) % Q;
                }
            }
            piv_col[rank] = c;
            is_piv[c] = 1;
            rank++;
        }
        if (rank != D) { fprintf(stderr, "FATAL: subset %d rank %d != %d\n", s, rank, D); exit(2); }
        int free_pos[2], nf = 0;
        for (int c = 0; c < T; c++) if (!is_piv[c]) free_pos[nf++] = c;
        for (int hr = 0; hr < 2; hr++) {
            for (int c = 0; c < T; c++) H_MAT[s][hr][c] = 0;
            H_MAT[s][hr][free_pos[hr]] = 1;
            for (int r = 0; r < D; r++)
                H_MAT[s][hr][piv_col[r]] = (Q - A[r][free_pos[hr]]) % Q;
        }
        for (int hr = 0; hr < 2; hr++) {
            for (int r = 0; r < D; r++) {
                int dot = 0;
                for (int c = 0; c < T; c++)
                    dot = (dot + H_MAT[s][hr][c] * spec->G[r][SUBS[s][c]]) % Q;
                if (dot != 0) { fprintf(stderr, "FATAL: H_S * G_S^T != 0\n"); exit(2); }
            }
        }
        for (int c = 0; c < T; c++) {
            int gcol = SUBS[s][c];
            H_COL[s][gcol][0] = H_MAT[s][0][c];
            H_COL[s][gcol][1] = H_MAT[s][1][c];
        }
    }

    for (int j = D; j < K; j++) {
        COL_DEG[j] = 0;
        for (int s = 0; s < N_SUB; s++) {
            int present = 0;
            for (int c = 0; c < T; c++) if (SUBS[s][c] == j) present = 1;
            if (!present) continue;
            int e = COL_DEG[j]++;
            COL_SUBS[j][e] = s;
            int h0 = H_COL[s][j][0], h1 = H_COL[s][j][1];
            for (int dv = 0; dv < Q; dv++) {
                int dsyn = ((h0 * dv) % Q) * Q + ((h1 * dv) % Q);
                for (int u = 0; u < Q2; u++)
                    SHIFT1[j][e][dv][u] = (uint8_t)SUB_ADD[u][dsyn];
            }
        }
    }

    for (int j1 = D; j1 < K; j1++) {
        for (int j2 = j1 + 1; j2 < K; j2++) {
            PairSubs *ps = &PAIR_SUBS[j1][j2];
            ps->n_subs = 0;
            for (int s = 0; s < N_SUB; s++) {
                int e1 = -1, e2 = -1;
                for (int e = 0; e < COL_DEG[j1]; e++) if (COL_SUBS[j1][e] == s) { e1 = e; break; }
                for (int e = 0; e < COL_DEG[j2]; e++) if (COL_SUBS[j2][e] == s) { e2 = e; break; }
                if (e1 >= 0 || e2 >= 0) {
                    int idx = ps->n_subs++;
                    ps->subs[idx] = s;
                    ps->e1[idx] = e1;
                    ps->e2[idx] = e2;
                }
            }
        }
    }

    for (int s = 0; s < N_SUB; s++) {
        SUB_N_FREE[s] = 0;
        for (int c = 0; c < T; c++) {
            int j = SUBS[s][c];
            if (j >= D) {
                int fi = SUB_N_FREE[s]++;
                SUB_FREE_COLS[s][fi] = j;
                for (int u = 0; u < Q2; u++) SOLVE1[s][fi][u] = -1;
                int h0 = H_COL[s][j][0], h1 = H_COL[s][j][1];
                for (int dv = 1; dv < Q; dv++) {
                    int dsyn = ((h0 * dv) % Q) * Q + ((h1 * dv) % Q);
                    if (dsyn != 0) SOLVE1[s][fi][dsyn] = (int8_t)dv;
                }
            }
        }
        SUB_N_PAIR[s] = 0;
        for (int a = 0; a < SUB_N_FREE[s]; a++) {
            for (int b = a + 1; b < SUB_N_FREE[s]; b++) {
                int j1 = SUB_FREE_COLS[s][a];
                int j2 = SUB_FREE_COLS[s][b];
                int a0 = H_COL[s][j1][0], a1 = H_COL[s][j1][1];
                int b0 = H_COL[s][j2][0], b1 = H_COL[s][j2][1];
                int det = ((a0 * b1 - a1 * b0) % Q + Q) % Q;
                if (det == 0) continue;
                int inv_det = INV_Q[det];
                SubPairSolver *sp = &SUB_PAIR[s][SUB_N_PAIR[s]++];
                sp->j1 = j1;
                sp->j2 = j2;
                for (int u = 0; u < Q2; u++) {
                    int u0 = u / Q, u1 = u % Q;
                    int dv1 = (((b1 * u0 - b0 * u1) % Q + Q) % Q) * inv_det % Q;
                    int dv2 = (((-a1 * u0 + a0 * u1) % Q + Q) % Q) * inv_det % Q;
                    sp->dv1[u] = (int8_t)dv1;
                    sp->dv2[u] = (int8_t)dv2;
                }
            }
        }
    }
}

typedef struct {
    int M; /* number of active rows (M in free mode, R_orb in scale-inv mode) */
    uint8_t rep[MAX_M][MAX_K];
    uint8_t syn[MAX_M][MAX_SUB];
    uint16_t cnt[MAX_SUB][MAX_Q2]; /* counts indexed by target id in [0, N_TARGETS) */
    int unc;
    int unc_list[MAX_SUB * MAX_Q2];
    int unc_pos[MAX_SUB * MAX_Q2];
    int best_unc;
} State;

static void state_recompute(State *st) {
    memset(st->cnt, 0, sizeof(st->cnt));
    for (int i = 0; i < st->M; i++) {
        for (int s = 0; s < N_SUB; s++) {
            int u0 = 0, u1 = 0;
            for (int c = 0; c < T; c++) {
                int gcol = SUBS[s][c];
                int v = st->rep[i][gcol];
                u0 += H_MAT[s][0][c] * v;
                u1 += H_MAT[s][1][c] * v;
            }
            int u = (u0 % Q) * Q + (u1 % Q);
            st->syn[i][s] = (uint8_t)u;
            int tgt = SYN_TO_TGT[u];
            st->cnt[s][tgt]++;
        }
    }
    st->unc = 0;
    for (int s = 0; s < N_SUB; s++) {
        for (int t = 0; t < N_TARGETS; t++) {
            int key = s * N_TARGETS + t;
            if (t >= TARGET_START && st->cnt[s][t] == 0) {
                st->unc_pos[key] = st->unc;
                st->unc_list[st->unc++] = key;
            } else {
                st->unc_pos[key] = -1;
            }
        }
    }
}

static inline void unc_add(State *st, int s, int t) {
    if (t < TARGET_START) return;
    int key = s * N_TARGETS + t;
    st->unc_pos[key] = st->unc;
    st->unc_list[st->unc++] = key;
}

static inline void unc_rem(State *st, int s, int t) {
    if (t < TARGET_START) return;
    int key = s * N_TARGETS + t;
    int pos = st->unc_pos[key];
    int last_key = st->unc_list[--st->unc];
    st->unc_list[pos] = last_key;
    st->unc_pos[last_key] = pos;
    st->unc_pos[key] = -1;
}

static inline int eval_1flip(const State *st, int row, int col, int dv) {
    int delta = 0;
    int deg = COL_DEG[col];
    for (int e = 0; e < deg; e++) {
        int s = COL_SUBS[col][e];
        int old_u = st->syn[row][s];
        int new_u = SHIFT1[col][e][dv][old_u];
        int old_t = SYN_TO_TGT[old_u];
        int new_t = SYN_TO_TGT[new_u];
        if (new_t != old_t) {
            if (old_t >= TARGET_START && st->cnt[s][old_t] == 1) delta++;
            if (new_t >= TARGET_START && st->cnt[s][new_t] == 0) delta--;
        }
    }
    return delta;
}

static inline void apply_1flip(State *st, int row, int col, int dv) {
    st->rep[row][col] = (uint8_t)((st->rep[row][col] + dv) % Q);
    int deg = COL_DEG[col];
    for (int e = 0; e < deg; e++) {
        int s = COL_SUBS[col][e];
        int old_u = st->syn[row][s];
        int new_u = SHIFT1[col][e][dv][old_u];
        int old_t = SYN_TO_TGT[old_u];
        int new_t = SYN_TO_TGT[new_u];
        st->syn[row][s] = (uint8_t)new_u;
        if (new_t != old_t) {
            if (--st->cnt[s][old_t] == 0) unc_add(st, s, old_t);
            if (st->cnt[s][new_t]++ == 0) unc_rem(st, s, new_t);
        }
    }
}

static inline int eval_2flip(const State *st, int row, int j1, int dv1, int j2, int dv2) {
    int delta = 0;
    const PairSubs *ps = &PAIR_SUBS[j1][j2];
    int ns = ps->n_subs;
    for (int idx = 0; idx < ns; idx++) {
        int s = ps->subs[idx];
        int old_u = st->syn[row][s];
        int new_u = old_u;
        int e1 = ps->e1[idx], e2 = ps->e2[idx];
        if (e1 >= 0) new_u = SHIFT1[j1][e1][dv1][new_u];
        if (e2 >= 0) new_u = SHIFT1[j2][e2][dv2][new_u];
        int old_t = SYN_TO_TGT[old_u];
        int new_t = SYN_TO_TGT[new_u];
        if (new_t != old_t) {
            if (old_t >= TARGET_START && st->cnt[s][old_t] == 1) delta++;
            if (new_t >= TARGET_START && st->cnt[s][new_t] == 0) delta--;
        }
    }
    return delta;
}

static inline void apply_2flip(State *st, int row, int j1, int dv1, int j2, int dv2) {
    st->rep[row][j1] = (uint8_t)((st->rep[row][j1] + dv1) % Q);
    st->rep[row][j2] = (uint8_t)((st->rep[row][j2] + dv2) % Q);
    const PairSubs *ps = &PAIR_SUBS[j1][j2];
    int ns = ps->n_subs;
    for (int idx = 0; idx < ns; idx++) {
        int s = ps->subs[idx];
        int old_u = st->syn[row][s];
        int new_u = old_u;
        int e1 = ps->e1[idx], e2 = ps->e2[idx];
        if (e1 >= 0) new_u = SHIFT1[j1][e1][dv1][new_u];
        if (e2 >= 0) new_u = SHIFT1[j2][e2][dv2][new_u];
        int old_t = SYN_TO_TGT[old_u];
        int new_t = SYN_TO_TGT[new_u];
        st->syn[row][s] = (uint8_t)new_u;
        if (new_t != old_t) {
            if (--st->cnt[s][old_t] == 0) unc_add(st, s, old_t);
            if (st->cnt[s][new_t]++ == 0) unc_rem(st, s, new_t);
        }
    }
}

static void state_random_init(State *st, Rng *rng) {
    for (int i = 0; i < st->M; i++) {
        for (int j = 0; j < D; j++) st->rep[i][j] = 0;
        for (int j = D; j < K; j++) st->rep[i][j] = (uint8_t)rng_int(rng, Q);
    }
    state_recompute(st);
}

static int run_selftest(int M) {
    State *st = (State *)calloc(1, sizeof(State));
    st->M = M;
    Rng rng;
    rng_init(&rng, 1234567ULL);
    state_random_init(st, &rng);
    int n_free = K - D;
    for (int iter = 0; iter < 5000; iter++) {
        int row = rng_int(&rng, M);
        if (iter % 2 == 0) {
            int col = D + rng_int(&rng, n_free);
            int dv = 1 + rng_int(&rng, Q - 1);
            int pred = st->unc + eval_1flip(st, row, col, dv);
            apply_1flip(st, row, col, dv);
            int inc = st->unc;
            state_recompute(st);
            if (pred != inc || inc != st->unc) {
                fprintf(stderr, "SELFTEST FAIL 1flip iter=%d pred=%d inc=%d true=%d\n", iter, pred, inc, st->unc);
                free(st);
                return 1;
            }
        } else {
            int j1 = D + rng_int(&rng, n_free);
            int j2 = D + rng_int(&rng, n_free);
            if (j1 == j2) j2 = D + ((j1 - D + 1) % n_free);
            if (j1 > j2) { int tmp = j1; j1 = j2; j2 = tmp; }
            int dv1 = 1 + rng_int(&rng, Q - 1);
            int dv2 = 1 + rng_int(&rng, Q - 1);
            int pred = st->unc + eval_2flip(st, row, j1, dv1, j2, dv2);
            apply_2flip(st, row, j1, dv1, j2, dv2);
            int inc = st->unc;
            state_recompute(st);
            if (pred != inc || inc != st->unc) {
                fprintf(stderr, "SELFTEST FAIL 2flip iter=%d pred=%d inc=%d true=%d\n", iter, pred, inc, st->unc);
                free(st);
                return 1;
            }
        }
    }
    printf("SELFTEST PASS (scale_inv=%d has_zero=%d): 5000 random 1/2-flips exact match\n", SCALE_INV, HAS_ZERO);
    free(st);
    return 0;
}

static atomic_int G_FOUND = 0;
static atomic_int G_STOP = 0;
static pthread_mutex_t G_LOCK = PTHREAD_MUTEX_INITIALIZER;
static uint8_t G_BEST_REP[MAX_M][MAX_K];
static int G_BEST_UNC = 1000000;

typedef struct {
    int tid;
    int M;
    uint64_t seed;
    double deadline;
    uint64_t moves;
    uint64_t evals;
    int swaps;
    int best_unc;
} WorkerArgs;

static void *worker_sa(void *arg) {
    WorkerArgs *wa = (WorkerArgs *)arg;
    State *reps = (State *)calloc(N_REP, sizeof(State));
    Rng rng;
    rng_init(&rng, wa->seed);

    double temps[N_REP];
    double T_lo = (wa->tid % 2 == 0) ? 0.16 : 0.14;
    double T_hi = (wa->tid % 2 == 0) ? 1.40 : 1.80;
    for (int r = 0; r < N_REP; r++) {
        temps[r] = T_lo * pow(T_hi / T_lo, (double)r / (double)(N_REP - 1));
    }
    double prob_tbl[N_REP][64];
    for (int r = 0; r < N_REP; r++) {
        for (int d = 0; d < 64; d++) prob_tbl[r][d] = exp(-(double)d / temps[r]);
    }

    int n_free = K - D;
    int local_best_unc = 1000000;
    for (int r = 0; r < N_REP; r++) {
        reps[r].M = wa->M;
        state_random_init(&reps[r], &rng);
        if (reps[r].unc < local_best_unc) {
            local_best_unc = reps[r].unc;
            pthread_mutex_lock(&G_LOCK);
            if (local_best_unc < G_BEST_UNC) {
                G_BEST_UNC = local_best_unc;
                memcpy(G_BEST_REP, reps[r].rep, sizeof(reps[r].rep));
            }
            pthread_mutex_unlock(&G_LOCK);
        }
    }

    uint64_t evals = 0;
    uint64_t moves = 0;
    int swaps = 0;
    int epoch = 0;

    while (!atomic_load_explicit(&G_FOUND, memory_order_relaxed) &&
           !atomic_load_explicit(&G_STOP, memory_order_relaxed)) {
        if ((epoch & 31) == 0) {
            if (now_sec() >= wa->deadline) break;
        }
        epoch++;

        for (int r = 0; r < N_REP; r++) {
            State *st = &reps[r];
            double *pt = prob_tbl[r];
            int focus_mask = (r < 3) ? 3 : 7;
            for (int it = 0; it < 512; it++) {
                if (st->unc == 0) {
                    state_recompute(st);
                    if (st->unc != 0) { fprintf(stderr, "BUG: unc drift\n"); exit(3); }
                    pthread_mutex_lock(&G_LOCK);
                    G_BEST_UNC = 0;
                    memcpy(G_BEST_REP, st->rep, sizeof(st->rep));
                    pthread_mutex_unlock(&G_LOCK);
                    atomic_store(&G_FOUND, 1);
                    goto done;
                }

                int did_focused = 0;
                if (!SCALE_INV && (it & focus_mask) == 0) {
                    int key = st->unc_list[rng_int(&rng, st->unc)];
                    int s = key / N_TARGETS;
                    int target = key % N_TARGETS;
                    int row = rng_int(&rng, st->M);
                    int diff = SUB_DIFF[target][st->syn[row][s]];
                    int fi = rng_int(&rng, SUB_N_FREE[s]);
                    int dv = SOLVE1[s][fi][diff];
                    if (dv > 0) {
                        int col = SUB_FREE_COLS[s][fi];
                        int delta = eval_1flip(st, row, col, dv);
                        evals++;
                        if (delta <= 0 || (delta < 64 && rng_dbl(&rng) < pt[delta])) {
                            apply_1flip(st, row, col, dv);
                            moves++;
                        }
                        did_focused = 1;
                    } else if (r <= 1 && st->unc <= 25) {
                        int pi = rng_int(&rng, SUB_N_PAIR[s]);
                        const SubPairSolver *sp = &SUB_PAIR[s][pi];
                        int dv1 = sp->dv1[diff], dv2 = sp->dv2[diff];
                        if (dv1 != 0 && dv2 != 0) {
                            int delta = eval_2flip(st, row, sp->j1, dv1, sp->j2, dv2);
                            evals++;
                            if (delta <= 0 || (delta < 64 && rng_dbl(&rng) < pt[delta])) {
                                apply_2flip(st, row, sp->j1, dv1, sp->j2, dv2);
                                moves++;
                            }
                            did_focused = 1;
                        }
                    }
                } else if (SCALE_INV && (it & 7) == 0) {
                    /* Occasional 2-flip in scale-inv mode */
                    int row = rng_int(&rng, st->M);
                    int j1 = D + rng_int(&rng, n_free);
                    int j2 = D + rng_int(&rng, n_free);
                    if (j1 != j2) {
                        if (j1 > j2) { int tmp = j1; j1 = j2; j2 = tmp; }
                        int dv1 = 1 + rng_int(&rng, Q - 1);
                        int dv2 = 1 + rng_int(&rng, Q - 1);
                        int delta = eval_2flip(st, row, j1, dv1, j2, dv2);
                        evals++;
                        if (delta <= 0 || (delta < 64 && rng_dbl(&rng) < pt[delta])) {
                            apply_2flip(st, row, j1, dv1, j2, dv2);
                            moves++;
                        }
                        did_focused = 1;
                    }
                }
                if (!did_focused) {
                    int row = rng_int(&rng, st->M);
                    int col = D + rng_int(&rng, n_free);
                    int dv = 1 + rng_int(&rng, Q - 1);
                    int delta = eval_1flip(st, row, col, dv);
                    evals++;
                    if (delta <= 0 || (delta < 64 && rng_dbl(&rng) < pt[delta])) {
                        apply_1flip(st, row, col, dv);
                        moves++;
                    }
                }

                if (st->unc < local_best_unc) {
                    local_best_unc = st->unc;
                    pthread_mutex_lock(&G_LOCK);
                    if (local_best_unc < G_BEST_UNC) {
                        G_BEST_UNC = local_best_unc;
                        memcpy(G_BEST_REP, st->rep, sizeof(st->rep));
                    }
                    pthread_mutex_unlock(&G_LOCK);
                    if (local_best_unc == 0) {
                        state_recompute(st);
                        if (st->unc != 0) { fprintf(stderr, "BUG: unc drift\n"); exit(3); }
                        atomic_store(&G_FOUND, 1);
                        goto done;
                    }
                }
            }
        }

        int start_r = (epoch & 1);
        for (int r = start_r; r + 1 < N_REP; r += 2) {
            int e1 = reps[r].unc;
            int e2 = reps[r + 1].unc;
            double dbeta = (1.0 / temps[r]) - (1.0 / temps[r + 1]);
            double log_acc = dbeta * (double)(e1 - e2);
            if (log_acc >= 0.0 || rng_dbl(&rng) < exp(log_acc)) {
                State tmp = reps[r];
                reps[r] = reps[r + 1];
                reps[r + 1] = tmp;
                swaps++;
            }
        }
    }

done:
    wa->moves = moves;
    wa->evals = evals;
    wa->swaps = swaps;
    wa->best_unc = local_best_unc;
    free(reps);
    return NULL;
}

static int rollout_ca(int M_total, int active_rows, const uint8_t reps[MAX_M][MAX_K], uint8_t **out_rows) {
    uint8_t full_reps[MAX_M][MAX_K];
    int m_idx = 0;
    if (!SCALE_INV) {
        for (int i = 0; i < active_rows; i++)
            memcpy(full_reps[m_idx++], reps[i], K);
    } else {
        if (HAS_ZERO) {
            memset(full_reps[m_idx++], 0, K);
        }
        for (int i = 0; i < active_rows; i++) {
            for (int sc = 1; sc < Q; sc++) {
                for (int j = 0; j < K; j++)
                    full_reps[m_idx][j] = (uint8_t)((reps[i][j] * sc) % Q);
                m_idx++;
            }
        }
    }
    if (m_idx != M_total) { fprintf(stderr, "FATAL: m_idx=%d != M_total=%d\n", m_idx, M_total); exit(5); }

    int qd = 1;
    for (int i = 0; i < D; i++) qd *= Q;
    int N = M_total * qd;
    uint8_t *rows = (uint8_t *)malloc((size_t)N * (size_t)K);
    int ridx = 0;
    for (int i = 0; i < M_total; i++) {
        for (int cw = 0; cw < qd; cw++) {
            int coeff[MAX_D];
            int tmp = cw;
            for (int c = 0; c < D; c++) { coeff[c] = tmp % Q; tmp /= Q; }
            for (int j = 0; j < K; j++) {
                int val = full_reps[i][j];
                for (int c = 0; c < D; c++) val += coeff[c] * SPEC.G[c][j];
                rows[ridx * K + j] = (uint8_t)(val % Q);
            }
            ridx++;
        }
    }
    *out_rows = rows;
    return N;
}

static void write_ca(const char *path, int N, const uint8_t *rows, const int *keep) {
    FILE *f = fopen(path, "w");
    if (!f) { perror("fopen out"); exit(1); }
    for (int r = 0; r < N; r++) {
        if (keep && !keep[r]) continue;
        for (int j = 0; j < K; j++)
            fprintf(f, "%d%c", (int)rows[r * K + j], (j + 1 == K) ? '\n' : ' ');
    }
    fclose(f);
}

static int greedy_prune(int N, const uint8_t *rows, int *best_keep, uint64_t seed) {
    int qt = 1;
    for (int i = 0; i < T; i++) qt *= Q;
    int total_tuples = N_SUB * qt;
    uint16_t *base_cov = (uint16_t *)calloc((size_t)total_tuples, sizeof(uint16_t));
    int *row_tup = (int *)malloc((size_t)N * (size_t)N_SUB * sizeof(int));

    for (int r = 0; r < N; r++) {
        for (int s = 0; s < N_SUB; s++) {
            int code = 0;
            for (int c = 0; c < T; c++) code = code * Q + rows[r * K + SUBS[s][c]];
            row_tup[r * N_SUB + s] = code;
            base_cov[s * qt + code]++;
        }
    }
    for (int i = 0; i < total_tuples; i++) {
        if (base_cov[i] == 0) { fprintf(stderr, "FATAL: uncovered tuple in rolled-out CA!\n"); exit(4); }
    }

    uint16_t *cov = (uint16_t *)malloc((size_t)total_tuples * sizeof(uint16_t));
    int *keep = (int *)malloc((size_t)N * sizeof(int));
    int *order = (int *)malloc((size_t)N * sizeof(int));
    int best_deleted = -1;
    Rng rng;
    rng_init(&rng, seed ^ 0xdeadbeefULL);

    for (int trial = 0; trial <= 100; trial++) {
        memcpy(cov, base_cov, (size_t)total_tuples * sizeof(uint16_t));
        for (int r = 0; r < N; r++) { keep[r] = 1; order[r] = r; }
        int deleted = 0;
        if (trial == 0) {
            for (;;) {
                int pick = -1, pick_score = -1;
                for (int r = 0; r < N; r++) {
                    if (!keep[r]) continue;
                    int min_c = 1000000, sum_c = 0;
                    for (int s = 0; s < N_SUB; s++) {
                        int c = cov[s * qt + row_tup[r * N_SUB + s]];
                        if (c < min_c) min_c = c;
                        sum_c += c;
                    }
                    if (min_c >= 2) {
                        int score = min_c * 100000 + sum_c;
                        if (score > pick_score) { pick_score = score; pick = r; }
                    }
                }
                if (pick < 0) break;
                keep[pick] = 0;
                deleted++;
                for (int s = 0; s < N_SUB; s++) cov[s * qt + row_tup[pick * N_SUB + s]]--;
            }
        } else {
            for (int r = N - 1; r > 0; r--) {
                int j = rng_int(&rng, r + 1);
                int tmp = order[r]; order[r] = order[j]; order[j] = tmp;
            }
            for (int idx = 0; idx < N; idx++) {
                int r = order[idx];
                int ok = 1;
                for (int s = 0; s < N_SUB; s++) {
                    if (cov[s * qt + row_tup[r * N_SUB + s]] <= 1) { ok = 0; break; }
                }
                if (ok) {
                    keep[r] = 0;
                    deleted++;
                    for (int s = 0; s < N_SUB; s++) cov[s * qt + row_tup[r * N_SUB + s]]--;
                }
            }
        }
        if (deleted > best_deleted) {
            best_deleted = deleted;
            memcpy(best_keep, keep, (size_t)N * sizeof(int));
        }
    }

    free(base_cov); free(cov); free(row_tup); free(keep); free(order);
    return best_deleted;
}

int main(int argc, char **argv) {
    const char *mode = NULL;
    int M = -1;
    double max_sec = 55.0;
    uint64_t seed = 42;
    int threads = 2;
    const char *out_path = NULL;
    const char *prune_out = NULL;
    int do_prune = 0;
    int do_selftest = 0;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--mode") && i + 1 < argc) mode = argv[++i];
        else if (!strcmp(argv[i], "--m") && i + 1 < argc) M = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--time") && i + 1 < argc) max_sec = atof(argv[++i]);
        else if (!strcmp(argv[i], "--seed") && i + 1 < argc) seed = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--threads") && i + 1 < argc) threads = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--out") && i + 1 < argc) out_path = argv[++i];
        else if (!strcmp(argv[i], "--prune")) do_prune = 1;
        else if (!strcmp(argv[i], "--prune-out") && i + 1 < argc) { do_prune = 1; prune_out = argv[++i]; }
        else if (!strcmp(argv[i], "--selftest")) do_selftest = 1;
        else if (!strcmp(argv[i], "--scale-inv")) SCALE_INV = 1;
        else { fprintf(stderr, "Unknown arg: %s\n", argv[i]); return 1; }
    }
    if (!mode || M <= 0 || M > MAX_M) {
        fprintf(stderr, "Usage: %s --mode <c1|c2|c0|all1_5|all1_7> --m M [--scale-inv] [--time S] [--seed U] [--threads T] [--out FILE] [--prune] [--prune-out FILE] [--selftest]\n", argv[0]);
        return 1;
    }

    const CodeSpec *spec = NULL;
    for (int i = 0; i < NUM_SPECS; i++) {
        if (!strcmp(SPECS[i].name, mode)) { spec = &SPECS[i]; break; }
    }
    if (!spec) { fprintf(stderr, "Unknown mode: %s\n", mode); return 1; }

    int active_rows = M;
    if (SCALE_INV) {
        int rem = M % (spec->q - 1);
        if (rem != 0 && rem != 1) {
            fprintf(stderr, "FATAL: --scale-inv requires M mod (q-1) in {0, 1}, got M=%d q=%d\n", M, spec->q);
            return 2;
        }
        HAS_ZERO = rem;
        active_rows = M / (spec->q - 1);
    }

    init_geometry(spec);

    if (do_selftest) {
        return run_selftest(active_rows);
    }

    int qd = 1;
    for (int i = 0; i < D; i++) qd *= Q;

    printf("mode=%s scale_inv=%d has_zero=%d active=%d q=%d k=%d t=%d d=%d n_sub=%d tgts=%d M=%d N=%d threads=%d time=%.1fs seed=%llu\n",
           spec->name, SCALE_INV, HAS_ZERO, active_rows, Q, K, T, D, N_SUB, N_TARGETS - TARGET_START, M, M * qd, threads, max_sec, (unsigned long long)seed);
    fflush(stdout);

    double t0 = now_sec();
    double deadline = t0 + max_sec;

    pthread_t th[16];
    WorkerArgs wa[16];
    if (threads > 16) threads = 16;
    for (int i = 0; i < threads; i++) {
        wa[i].tid = i;
        wa[i].M = active_rows;
        wa[i].seed = seed + (uint64_t)i * 1000003ULL;
        wa[i].deadline = deadline;
        wa[i].moves = 0;
        wa[i].evals = 0;
        wa[i].swaps = 0;
        wa[i].best_unc = 1000000;
        pthread_create(&th[i], NULL, worker_sa, &wa[i]);
    }
    for (int i = 0; i < threads; i++) pthread_join(th[i], NULL);

    double elapsed = now_sec() - t0;
    uint64_t tot_moves = 0, tot_evals = 0;
    int tot_swaps = 0;
    for (int i = 0; i < threads; i++) {
        tot_moves += wa[i].moves;
        tot_evals += wa[i].evals;
        tot_swaps += wa[i].swaps;
    }

    if (G_BEST_UNC == 0) {
        printf("RESULT: FOUND unc=0 elapsed=%.3fs moves=%llu evals=%llu moves/s=%.0f evals/s=%.0f swaps=%d\n",
               elapsed, (unsigned long long)tot_moves, (unsigned long long)tot_evals,
               tot_moves / (elapsed > 1e-6 ? elapsed : 1e-6),
               tot_evals / (elapsed > 1e-6 ? elapsed : 1e-6),
               tot_swaps);
        uint8_t *rows = NULL;
        int N = rollout_ca(M, active_rows, G_BEST_REP, &rows);
        if (out_path) {
            write_ca(out_path, N, rows, NULL);
            printf("WROTE: %s (N=%d t=%d k=%d v=%d)\n", out_path, N, T, K, Q);
        }
        if (do_prune) {
            int *keep = (int *)malloc((size_t)N * sizeof(int));
            int del = greedy_prune(N, rows, keep, seed);
            printf("PRUNE: original_N=%d deleted=%d pruned_N=%d\n", N, del, N - del);
            if (prune_out && del > 0) {
                write_ca(prune_out, N, rows, keep);
                printf("WROTE_PRUNED: %s (N=%d t=%d k=%d v=%d)\n", prune_out, N - del, T, K, Q);
            }
            free(keep);
        }
        free(rows);
        return 0;
    } else {
        printf("RESULT: TIMEOUT (best_unc=%d) elapsed=%.3fs moves=%llu evals=%llu moves/s=%.0f evals/s=%.0f swaps=%d\n",
               G_BEST_UNC, elapsed, (unsigned long long)tot_moves, (unsigned long long)tot_evals,
               tot_moves / (elapsed > 1e-6 ? elapsed : 1e-6),
               tot_evals / (elapsed > 1e-6 ? elapsed : 1e-6),
               tot_swaps);
        return 1;
    }
}
