/* Phase 8 Teil 3.2: Schnelle C-Tabu-Suche fuer p = 7, v = 7 im Modell M(R) (m = 67 / 66).
 *
 * Kompilieren: gcc -O3 -pthread scripts/phase8_p7_tabu.c -o /tmp/phase8_p7_tabu
 * Aufruf:      timeout 60 /tmp/phase8_p7_tabu --m 67 --time 55 --threads 2 --seed 42 \
 *                  --init data/phase7/R_q7_m68.txt --out /tmp/R_q7_m67.txt
 *
 * Modell M(R) fuer q = p = 7, v = 7:
 *   - 49 Basiszeilen 0..48 decken alle 49 Punkte (c, d) in F_7^2 exakt einmal ab
 *     (damit sind alle C(7,2)=21 eval-eval-Spaltenpaare automatisch vollstaendig gedeckt).
 *   - (m - 49) Zusatzzeilen 49..m-1 mit freiem (c, d, a, b) in F_7^4.
 *   - Zielfunktion unc = ungedeckte Paare aus ca[7][7][7], cb[7][7][7], ab[7][7] (735 Paare).
 *   - Konfliktgetriebene Tabu-Suche mit Neustarts (Warmstart ab R_q7_m68 minus 1 Zeile
 *     und Kaltstarts mit Zufalls-/Skelett-Initialisierung).
 */

#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define Q 7
#define V 7
#define N_PTS 49
#define MAX_M 80

typedef struct {
    int c, d, a, b;
} Rep;

typedef struct {
    uint64_t s;
} Rng;

static inline uint64_t rng_next(Rng *r) {
    uint64_t x = r->s;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    r->s = x;
    return x;
}

static inline int rng_int(Rng *r, int n) {
    return (int)(rng_next(r) % (uint64_t)n);
}

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

/* Precomputed eval[pt][al] = (c + al*d) % 7, pt = c*7 + d */
static int EVAL[N_PTS][Q];
/* Precomputed line_pts[al][val][0..6] = the 7 points pt with (c + al*d) % 7 == val */
static int LINE_PTS[Q][Q][Q];

static void init_tables(void) {
    int cnt[Q][Q];
    memset(cnt, 0, sizeof(cnt));
    for (int c = 0; c < Q; c++) {
        for (int d = 0; d < Q; d++) {
            int pt = c * Q + d;
            for (int al = 0; al < Q; al++) {
                int v = (c + al * d) % Q;
                EVAL[pt][al] = v;
                LINE_PTS[al][v][cnt[al][v]++] = pt;
            }
        }
    }
}

typedef struct {
    int tid;
    int target_m;
    double time_limit;
    uint64_t seed;
    int has_init;
    Rep init_reps[MAX_M];
    int init_m;

    /* outputs */
    int found;
    int best_unc;
    Rep best_sol[MAX_M];
    uint64_t total_evals;
    uint64_t total_steps;
    int restarts;
    double elapsed;
} WorkerArgs;

static volatile int g_stop = 0;

typedef struct {
    int m;
    int pt[MAX_M];
    int a[MAX_M];
    int b[MAX_M];
    int ca[Q][Q][V];
    int cb[Q][Q][V];
    int ab[V][V];
    int unc;
    int tabu_a[MAX_M][V];
    int tabu_b[MAX_M][V];
    int tabu_pt[MAX_M][N_PTS];
} State;

static void state_recompute(State *st) {
    memset(st->ca, 0, sizeof(st->ca));
    memset(st->cb, 0, sizeof(st->cb));
    memset(st->ab, 0, sizeof(st->ab));
    for (int i = 0; i < st->m; i++) {
        int p = st->pt[i], av = st->a[i], bv = st->b[i];
        st->ab[av][bv]++;
        for (int al = 0; al < Q; al++) {
            int val = EVAL[p][al];
            st->ca[al][val][av]++;
            st->cb[al][val][bv]++;
        }
    }
    int u = 0;
    for (int al = 0; al < Q; al++)
        for (int val = 0; val < Q; val++)
            for (int s = 0; s < V; s++) {
                if (st->ca[al][val][s] == 0) u++;
                if (st->cb[al][val][s] == 0) u++;
            }
    for (int av = 0; av < V; av++)
        for (int bv = 0; bv < V; bv++)
            if (st->ab[av][bv] == 0) u++;
    st->unc = u;
}

static inline int delta_change_a(const State *st, int i, int na) {
    int oa = st->a[i], bv = st->b[i], p = st->pt[i];
    if (na == oa) return 0;
    int d = 0;
    if (st->ab[oa][bv] == 1) d++;
    if (st->ab[na][bv] == 0) d--;
    const int *ev = EVAL[p];
    for (int al = 0; al < Q; al++) {
        int val = ev[al];
        if (st->ca[al][val][oa] == 1) d++;
        if (st->ca[al][val][na] == 0) d--;
    }
    return d;
}

static inline int delta_change_b(const State *st, int i, int nb) {
    int av = st->a[i], ob = st->b[i], p = st->pt[i];
    if (nb == ob) return 0;
    int d = 0;
    if (st->ab[av][ob] == 1) d++;
    if (st->ab[av][nb] == 0) d--;
    const int *ev = EVAL[p];
    for (int al = 0; al < Q; al++) {
        int val = ev[al];
        if (st->cb[al][val][ob] == 1) d++;
        if (st->cb[al][val][nb] == 0) d--;
    }
    return d;
}

static inline int delta_change_pt(const State *st, int i, int np) {
    int op = st->pt[i], av = st->a[i], bv = st->b[i];
    if (np == op) return 0;
    int d = 0;
    const int *ev_old = EVAL[op];
    const int *ev_new = EVAL[np];
    for (int al = 0; al < Q; al++) {
        int vo = ev_old[al], vn = ev_new[al];
        if (vo != vn) {
            if (st->ca[al][vo][av] == 1) d++;
            if (st->ca[al][vn][av] == 0) d--;
            if (st->cb[al][vo][bv] == 1) d++;
            if (st->cb[al][vn][bv] == 0) d--;
        }
    }
    return d;
}

static inline void apply_change_a(State *st, int i, int na, int delta) {
    int oa = st->a[i], bv = st->b[i], p = st->pt[i];
    st->ab[oa][bv]--;
    st->ab[na][bv]++;
    const int *ev = EVAL[p];
    for (int al = 0; al < Q; al++) {
        int val = ev[al];
        st->ca[al][val][oa]--;
        st->ca[al][val][na]++;
    }
    st->a[i] = na;
    st->unc += delta;
}

static inline void apply_change_b(State *st, int i, int nb, int delta) {
    int av = st->a[i], ob = st->b[i], p = st->pt[i];
    st->ab[av][ob]--;
    st->ab[av][nb]++;
    const int *ev = EVAL[p];
    for (int al = 0; al < Q; al++) {
        int val = ev[al];
        st->cb[al][val][ob]--;
        st->cb[al][val][nb]++;
    }
    st->b[i] = nb;
    st->unc += delta;
}

static inline void apply_change_pt(State *st, int i, int np, int delta) {
    int op = st->pt[i], av = st->a[i], bv = st->b[i];
    const int *ev_old = EVAL[op];
    const int *ev_new = EVAL[np];
    for (int al = 0; al < Q; al++) {
        int vo = ev_old[al], vn = ev_new[al];
        if (vo != vn) {
            st->ca[al][vo][av]--;
            st->ca[al][vn][av]++;
            st->cb[al][vo][bv]--;
            st->cb[al][vn][bv]++;
        }
    }
    st->pt[i] = np;
    st->unc += delta;
}

static void init_state(State *st, const WorkerArgs *wa, Rng *rng, int mode) {
    st->m = wa->target_m;
    memset(st->tabu_a, 0, sizeof(st->tabu_a));
    memset(st->tabu_b, 0, sizeof(st->tabu_b));
    memset(st->tabu_pt, 0, sizeof(st->tabu_pt));

    if (mode == 0 && wa->has_init && wa->init_m >= wa->target_m) {
        /* Warmstart: nehme alle 49 Basiszeilen (je 1 pro Punkt) + zufaellige Auswahl der Zusatzzeilen */
        int used_pt[N_PTS];
        memset(used_pt, 0, sizeof(used_pt));
        Rep extras[MAX_M];
        int n_ext = 0;
        for (int i = 0; i < wa->init_m; i++) {
            int p = wa->init_reps[i].c * Q + wa->init_reps[i].d;
            if (!used_pt[p]) {
                used_pt[p] = 1;
                st->pt[p] = p;
                st->a[p] = wa->init_reps[i].a;
                st->b[p] = wa->init_reps[i].b;
            } else {
                extras[n_ext++] = wa->init_reps[i];
            }
        }
        /* Shuffle extras */
        for (int i = n_ext - 1; i > 0; i--) {
            int j = rng_int(rng, i + 1);
            Rep tmp = extras[i]; extras[i] = extras[j]; extras[j] = tmp;
        }
        int need = wa->target_m - N_PTS;
        for (int i = 0; i < need; i++) {
            if (i < n_ext) {
                st->pt[N_PTS + i] = extras[i].c * Q + extras[i].d;
                st->a[N_PTS + i] = extras[i].a;
                st->b[N_PTS + i] = extras[i].b;
            } else {
                st->pt[N_PTS + i] = rng_int(rng, N_PTS);
                st->a[N_PTS + i] = rng_int(rng, V);
                st->b[N_PTS + i] = rng_int(rng, V);
            }
        }
        /* Optional kleine Perturbation bei spaeteren Warmstarts */
        int pert = rng_int(rng, 10);
        for (int k = 0; k < pert; k++) {
            int idx = rng_int(rng, st->m);
            if (rng_int(rng, 2)) st->a[idx] = rng_int(rng, V);
            else st->b[idx] = rng_int(rng, V);
        }
    } else if (mode == 1) {
        /* Skelett-Start: d = 0..4 tragen volle Geraden fuer a=d (und verschoben fuer b) */
        for (int c = 0; c < Q; c++) {
            for (int d = 0; d < Q; d++) {
                int p = c * Q + d;
                st->pt[p] = p;
                st->a[p] = (d < 5) ? d : rng_int(rng, V);
                st->b[p] = (d < 5) ? ((d + 2) % 5) : rng_int(rng, V);
            }
        }
        for (int i = N_PTS; i < st->m; i++) {
            st->pt[i] = rng_int(rng, Q) * Q + 0; /* schwer auf d=0 oder zufaellig */
            if (rng_int(rng, 3) == 0) st->pt[i] = rng_int(rng, N_PTS);
            st->a[i] = rng_int(rng, V);
            st->b[i] = rng_int(rng, V);
        }
    } else {
        /* Reiner Zufallsstart */
        for (int p = 0; p < N_PTS; p++) {
            st->pt[p] = p;
            st->a[p] = rng_int(rng, V);
            st->b[p] = rng_int(rng, V);
        }
        for (int i = N_PTS; i < st->m; i++) {
            st->pt[i] = rng_int(rng, N_PTS);
            st->a[i] = rng_int(rng, V);
            st->b[i] = rng_int(rng, V);
        }
    }
    state_recompute(st);
}

static void *worker_fn(void *arg) {
    WorkerArgs *wa = (WorkerArgs *)arg;
    double t0 = now_sec();
    Rng rng = { wa->seed ^ ((uint64_t)(wa->tid + 1) * 0x9e3779b97f4a7c15ULL) };
    if (rng.s == 0) rng.s = 123456789ULL + (uint64_t)wa->tid;

    State st;
    wa->best_unc = 999999;
    wa->found = 0;
    wa->total_evals = 0;
    wa->total_steps = 0;
    wa->restarts = 0;

    int unc_list_type[800];
    int unc_list_x[800];
    int unc_list_y[800];
    int unc_list_z[800];

    while (!g_stop && (now_sec() - t0) < wa->time_limit) {
        int mode = wa->restarts % 3;
        init_state(&st, wa, &rng, mode);
        wa->restarts++;

        int run_best = st.unc;
        int no_imp = 0;
        int max_no_imp = 35000;
        int step = 0;

        while (!g_stop && no_imp < max_no_imp) {
            if ((step & 1023) == 0 && (now_sec() - t0) >= wa->time_limit) break;
            step++;
            wa->total_steps++;

            if (st.unc == 0) {
                wa->found = 1;
                wa->best_unc = 0;
                for (int i = 0; i < st.m; i++) {
                    wa->best_sol[i].c = st.pt[i] / Q;
                    wa->best_sol[i].d = st.pt[i] % Q;
                    wa->best_sol[i].a = st.a[i];
                    wa->best_sol[i].b = st.b[i];
                }
                g_stop = 1;
                break;
            }

            /* Sammle ungedeckte Paare */
            int nu = 0;
            for (int al = 0; al < Q; al++)
                for (int val = 0; val < Q; val++)
                    for (int s = 0; s < V; s++) {
                        if (st.ca[al][val][s] == 0) {
                            unc_list_type[nu] = 0;
                            unc_list_x[nu] = al; unc_list_y[nu] = val; unc_list_z[nu] = s;
                            nu++;
                        }
                        if (st.cb[al][val][s] == 0) {
                            unc_list_type[nu] = 1;
                            unc_list_x[nu] = al; unc_list_y[nu] = val; unc_list_z[nu] = s;
                            nu++;
                        }
                    }
            for (int av = 0; av < V; av++)
                for (int bv = 0; bv < V; bv++)
                    if (st.ab[av][bv] == 0) {
                        unc_list_type[nu] = 2;
                        unc_list_x[nu] = av; unc_list_y[nu] = bv; unc_list_z[nu] = 0;
                        nu++;
                    }

            int pick = rng_int(&rng, nu);
            int ut = unc_list_type[pick];
            int ux = unc_list_x[pick];
            int uy = unc_list_y[pick];
            int uz = unc_list_z[pick];

            int best_d = 999999;
            int best_kind = -1; /* 0=a, 1=b, 2=pt */
            int best_row = -1;
            int best_val = -1;
            int ties = 0;

            if (ut == 0) {
                /* ungedecktes (al=ux, val=uy, a=uz) */
                /* (i) Aendere a -> uz in einer Zeile auf der Geraden c + al*d = val */
                for (int i = 0; i < st.m; i++) {
                    if (EVAL[st.pt[i]][ux] == uy) {
                        int d = delta_change_a(&st, i, uz);
                        wa->total_evals++;
                        int is_tabu = (st.tabu_a[i][uz] > step);
                        if (!is_tabu || st.unc + d < run_best) {
                            if (d < best_d) {
                                best_d = d; best_kind = 0; best_row = i; best_val = uz; ties = 1;
                            } else if (d == best_d && rng_int(&rng, ++ties) == 0) {
                                best_kind = 0; best_row = i; best_val = uz;
                            }
                        }
                    }
                }
                /* (ii) Verschiebe Zusatzzeile i >= 49 mit a[i] == uz auf einen Punkt der Geraden */
                for (int i = N_PTS; i < st.m; i++) {
                    if (st.a[i] == uz) {
                        for (int k = 0; k < Q; k++) {
                            int np = LINE_PTS[ux][uy][k];
                            int d = delta_change_pt(&st, i, np);
                            wa->total_evals++;
                            int is_tabu = (st.tabu_pt[i][np] > step);
                            if (!is_tabu || st.unc + d < run_best) {
                                if (d < best_d) {
                                    best_d = d; best_kind = 2; best_row = i; best_val = np; ties = 1;
                                } else if (d == best_d && rng_int(&rng, ++ties) == 0) {
                                    best_kind = 2; best_row = i; best_val = np;
                                }
                            }
                        }
                    }
                }
            } else if (ut == 1) {
                /* ungedecktes (al=ux, val=uy, b=uz) */
                for (int i = 0; i < st.m; i++) {
                    if (EVAL[st.pt[i]][ux] == uy) {
                        int d = delta_change_b(&st, i, uz);
                        wa->total_evals++;
                        int is_tabu = (st.tabu_b[i][uz] > step);
                        if (!is_tabu || st.unc + d < run_best) {
                            if (d < best_d) {
                                best_d = d; best_kind = 1; best_row = i; best_val = uz; ties = 1;
                            } else if (d == best_d && rng_int(&rng, ++ties) == 0) {
                                best_kind = 1; best_row = i; best_val = uz;
                            }
                        }
                    }
                }
                for (int i = N_PTS; i < st.m; i++) {
                    if (st.b[i] == uz) {
                        for (int k = 0; k < Q; k++) {
                            int np = LINE_PTS[ux][uy][k];
                            int d = delta_change_pt(&st, i, np);
                            wa->total_evals++;
                            int is_tabu = (st.tabu_pt[i][np] > step);
                            if (!is_tabu || st.unc + d < run_best) {
                                if (d < best_d) {
                                    best_d = d; best_kind = 2; best_row = i; best_val = np; ties = 1;
                                } else if (d == best_d && rng_int(&rng, ++ties) == 0) {
                                    best_kind = 2; best_row = i; best_val = np;
                                }
                            }
                        }
                    }
                }
            } else {
                /* ungedecktes (a=ux, b=uy) */
                for (int i = 0; i < st.m; i++) {
                    if (st.a[i] == ux) {
                        int d = delta_change_b(&st, i, uy);
                        wa->total_evals++;
                        int is_tabu = (st.tabu_b[i][uy] > step);
                        if (!is_tabu || st.unc + d < run_best) {
                            if (d < best_d) {
                                best_d = d; best_kind = 1; best_row = i; best_val = uy; ties = 1;
                            } else if (d == best_d && rng_int(&rng, ++ties) == 0) {
                                best_kind = 1; best_row = i; best_val = uy;
                            }
                        }
                    }
                    if (st.b[i] == uy) {
                        int d = delta_change_a(&st, i, ux);
                        wa->total_evals++;
                        int is_tabu = (st.tabu_a[i][ux] > step);
                        if (!is_tabu || st.unc + d < run_best) {
                            if (d < best_d) {
                                best_d = d; best_kind = 0; best_row = i; best_val = ux; ties = 1;
                            } else if (d == best_d && rng_int(&rng, ++ties) == 0) {
                                best_kind = 0; best_row = i; best_val = ux;
                            }
                        }
                    }
                }
            }

            /* Fallback falls alle Zuege tabu waren: zufaelliger Zug */
            if (best_kind < 0) {
                int i = rng_int(&rng, st.m);
                if (i >= N_PTS && rng_int(&rng, 3) == 0) {
                    int np = rng_int(&rng, N_PTS);
                    if (np != st.pt[i]) {
                        int d = delta_change_pt(&st, i, np);
                        best_kind = 2; best_row = i; best_val = np; best_d = d;
                    }
                }
                if (best_kind < 0) {
                    int side = rng_int(&rng, 2);
                    int ns = rng_int(&rng, V);
                    if (side == 0 && ns != st.a[i]) {
                        best_kind = 0; best_row = i; best_val = ns; best_d = delta_change_a(&st, i, ns);
                    } else if (ns != st.b[i]) {
                        best_kind = 1; best_row = i; best_val = ns; best_d = delta_change_b(&st, i, ns);
                    } else {
                        continue;
                    }
                }
            }

            int tenure = 7 + rng_int(&rng, 14);
            if (best_kind == 0) {
                st.tabu_a[best_row][st.a[best_row]] = step + tenure;
                apply_change_a(&st, best_row, best_val, best_d);
            } else if (best_kind == 1) {
                st.tabu_b[best_row][st.b[best_row]] = step + tenure;
                apply_change_b(&st, best_row, best_val, best_d);
            } else {
                st.tabu_pt[best_row][st.pt[best_row]] = step + tenure;
                apply_change_pt(&st, best_row, best_val, best_d);
            }

            if (st.unc < run_best) {
                run_best = st.unc;
                no_imp = 0;
                if (st.unc < wa->best_unc) {
                    wa->best_unc = st.unc;
                    for (int i = 0; i < st.m; i++) {
                        wa->best_sol[i].c = st.pt[i] / Q;
                        wa->best_sol[i].d = st.pt[i] % Q;
                        wa->best_sol[i].a = st.a[i];
                        wa->best_sol[i].b = st.b[i];
                    }
                }
            } else {
                no_imp++;
            }
        }
    }

    wa->elapsed = now_sec() - t0;
    return NULL;
}

static int read_init_file(const char *path, Rep *out) {
    FILE *fp = fopen(path, "r");
    if (!fp) return 0;
    int n = 0;
    char line[256];
    while (fgets(line, sizeof(line), fp) && n < MAX_M) {
        char *h = strchr(line, '#');
        if (h) *h = '\0';
        int c, d, a, b;
        if (sscanf(line, "%d %d %d %d", &c, &d, &a, &b) == 4) {
            out[n].c = c; out[n].d = d; out[n].a = a; out[n].b = b;
            n++;
        }
    }
    fclose(fp);
    return n;
}

int main(int argc, char **argv) {
    init_tables();
    int target_m = 67;
    double time_limit = 55.0;
    int n_threads = 2;
    uint64_t seed = 20261127ULL;
    const char *init_path = NULL;
    const char *out_path = NULL;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--m") && i + 1 < argc) target_m = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--time") && i + 1 < argc) time_limit = atof(argv[++i]);
        else if (!strcmp(argv[i], "--threads") && i + 1 < argc) n_threads = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--seed") && i + 1 < argc) seed = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--init") && i + 1 < argc) init_path = argv[++i];
        else if (!strcmp(argv[i], "--out") && i + 1 < argc) out_path = argv[++i];
    }

    if (n_threads < 1) n_threads = 1;
    if (n_threads > 8) n_threads = 8;

    Rep init_reps[MAX_M];
    int init_m = 0;
    if (init_path) init_m = read_init_file(init_path, init_reps);

    WorkerArgs args[8];
    pthread_t th[8];
    double t0 = now_sec();
    for (int t = 0; t < n_threads; t++) {
        args[t].tid = t;
        args[t].target_m = target_m;
        args[t].time_limit = time_limit;
        args[t].seed = seed;
        args[t].has_init = (init_m > 0);
        args[t].init_m = init_m;
        memcpy(args[t].init_reps, init_reps, sizeof(init_reps));
        pthread_create(&th[t], NULL, worker_fn, &args[t]);
    }
    for (int t = 0; t < n_threads; t++) pthread_join(th[t], NULL);
    double wall = now_sec() - t0;

    int best_t = 0;
    uint64_t sum_evals = 0, sum_steps = 0;
    int sum_restarts = 0;
    for (int t = 0; t < n_threads; t++) {
        sum_evals += args[t].total_evals;
        sum_steps += args[t].total_steps;
        sum_restarts += args[t].restarts;
        if (args[t].best_unc < args[best_t].best_unc) best_t = t;
    }

    printf("p=7 v=7 target_m=%d threads=%d seed=%llu wall=%.3fs restarts=%d steps=%llu evals=%llu (%.0f moves/s, %.0f evals/s) best_unc=%d\n",
           target_m, n_threads, (unsigned long long)seed, wall, sum_restarts,
           (unsigned long long)sum_steps, (unsigned long long)sum_evals,
           wall > 0 ? (double)sum_steps / wall : 0.0,
           wall > 0 ? (double)sum_evals / wall : 0.0,
           args[best_t].best_unc);

    if (args[best_t].found && out_path) {
        FILE *fp = fopen(out_path, "w");
        if (fp) {
            fprintf(fp, "# q=7 v=7 m=%d seed=%llu tid=%d\n", target_m, (unsigned long long)seed, best_t);
            for (int i = 0; i < target_m; i++) {
                fprintf(fp, "%d %d %d %d\n",
                        args[best_t].best_sol[i].c, args[best_t].best_sol[i].d,
                        args[best_t].best_sol[i].a, args[best_t].best_sol[i].b);
            }
            fclose(fp);
            printf("FOUND valid M(R) list m=%d -> %s\n", target_m, out_path);
        }
        return 0;
    }
    return args[best_t].found ? 0 : 1;
}
