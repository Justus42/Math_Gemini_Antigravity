/*
 * Independent Standalone CPHF(2; k, q, 6) Full Verifier (Zero Shared Code with Scanner).
 *
 * Reads a saved CPHF JSON file directly (raw 2 x k matrices over F_q) and exhaustively
 * verifies ALL C(k, 6) 6-column submatrices via direct 6x6 Gaussian elimination over F_q.
 * Also runs built-in negative controls (duplicated column + corrupted entry) and checks
 * Sherwood avoiding hyperplanes in PG(5, q).
 *
 * Build:
 *   gcc -O3 -fopenmp -Wall -Wextra scripts/phase9_cphf_t6_verify.c -o /tmp/phase9_cphf_t6_verify
 *
 * Usage:
 *   /tmp/phase9_cphf_t6_verify <cphf.json> [--threads N]
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <omp.h>

#define V_MAX_Q 29
#define V_MAX_K 64

static double v_now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

typedef struct {
    int q;
    uint8_t add[V_MAX_Q][V_MAX_Q];
    uint8_t sub[V_MAX_Q][V_MAX_Q];
    uint8_t mul[V_MAX_Q][V_MAX_Q];
    uint8_t inv[V_MAX_Q];
} VField;

static void vfield_init(VField *f, int q) {
    memset(f, 0, sizeof(*f));
    f->q = q;
    if (q == 5 || q == 7 || q == 11 || q == 13 || q == 17 || q == 19 || q == 23 || q == 29) {
        for (int a = 0; a < q; a++)
            for (int b = 0; b < q; b++) {
                f->add[a][b] = (uint8_t)((a + b) % q);
                f->sub[a][b] = (uint8_t)((a - b + q) % q);
                f->mul[a][b] = (uint8_t)((a * b) % q);
            }
    } else if (q == 8) {
        for (int a = 0; a < 8; a++)
            for (int b = 0; b < 8; b++) {
                f->add[a][b] = (uint8_t)(a ^ b);
                f->sub[a][b] = (uint8_t)(a ^ b);
                int r = 0;
                for (int bit = 0; bit < 3; bit++) if ((b >> bit) & 1) r ^= (a << bit);
                for (int bit = 4; bit >= 3; bit--) if ((r >> bit) & 1) r ^= (0xB << (bit - 3));
                f->mul[a][b] = (uint8_t)r;
            }
    } else if (q == 9) {
        for (int a = 0; a < 9; a++)
            for (int b = 0; b < 9; b++) {
                int a0 = a % 3, a1 = a / 3, b0 = b % 3, b1 = b / 3;
                f->add[a][b] = (uint8_t)(((a0 + b0) % 3) + 3 * ((a1 + b1) % 3));
                f->sub[a][b] = (uint8_t)(((a0 - b0 + 3) % 3) + 3 * ((a1 - b1 + 3) % 3));
                int r0 = (a0 * b0 - a1 * b1 + 9) % 3, r1 = (a0 * b1 + a1 * b0) % 3;
                f->mul[a][b] = (uint8_t)(r0 + 3 * r1);
            }
    } else {
        fprintf(stderr, "Unsupported q=%d\n", q);
        exit(2);
    }
    for (int a = 1; a < q; a++)
        for (int b = 1; b < q; b++)
            if (f->mul[a][b] == 1) { f->inv[a] = (uint8_t)b; break; }
}

/* Direct naive 6x6 Gaussian elimination over F_q */
static int is_nonsingular_6x6(const VField *f, const uint8_t rows[6][6]) {
    uint8_t m[6][6];
    memcpy(m, rows, 36);
    for (int c = 0; c < 6; c++) {
        int piv = -1;
        for (int r = c; r < 6; r++) if (m[r][c] != 0) { piv = r; break; }
        if (piv < 0) return 0;
        if (piv != c) {
            for (int j = c; j < 6; j++) { uint8_t t = m[c][j]; m[c][j] = m[piv][j]; m[piv][j] = t; }
        }
        uint8_t invp = f->inv[m[c][c]];
        for (int r = c + 1; r < 6; r++) {
            if (m[r][c] != 0) {
                uint8_t fac = f->mul[m[r][c]][invp];
                for (int j = c + 1; j < 6; j++) m[r][j] = f->sub[m[r][j]][f->mul[fac][m[c][j]]];
            }
        }
    }
    return 1;
}

/* Minimal JSON extractor for q, k, n_orbit_a, R1, R2 */
static int parse_int_field(const char *buf, const char *key, int *out) {
    char pat[64];
    snprintf(pat, sizeof(pat), "\"%s\"", key);
    const char *p = strstr(buf, pat);
    if (!p) return 0;
    p = strchr(p, ':');
    if (!p) return 0;
    p++;
    while (*p && isspace((unsigned char)*p)) p++;
    *out = atoi(p);
    return 1;
}

static int parse_matrix_field(const char *buf, const char *key, int k, int q, uint8_t mat[V_MAX_K][6]) {
    char pat[64];
    snprintf(pat, sizeof(pat), "\"%s\"", key);
    const char *p = strstr(buf, pat);
    if (!p) return 0;
    p = strchr(p, '[');
    if (!p) return 0;
    p++;
    for (int i = 0; i < k; i++) {
        p = strchr(p, '[');
        if (!p) return 0;
        p++;
        for (int j = 0; j < 6; j++) {
            while (*p && (isspace((unsigned char)*p) || *p == ',')) p++;
            char *endp = NULL;
            long val = strtol(p, &endp, 10);
            if (endp == p || val < 0 || val >= q) return 0;
            mat[i][j] = (uint8_t)val;
            p = endp;
        }
        p = strchr(p, ']');
        if (!p) return 0;
        p++;
    }
    return 1;
}

static uint64_t verify_all_6tuples(const VField *f, int k, int n_orb_a,
                                   const uint8_t R1[V_MAX_K][6], const uint8_t R2[V_MAX_K][6],
                                   uint64_t dep1[7], uint64_t dep2[7], uint64_t both[7],
                                   uint64_t *out_checked) {
    memset(dep1, 0, 7 * sizeof(uint64_t));
    memset(dep2, 0, 7 * sizeof(uint64_t));
    memset(both, 0, 7 * sizeof(uint64_t));
    uint64_t checked = 0;

    #pragma omp parallel
    {
        uint64_t ld1[7] = {0}, ld2[7] = {0}, lbt[7] = {0}, lchk = 0;
        uint8_t m1[6][6], m2[6][6];

        #pragma omp for schedule(dynamic, 1)
        for (int c0 = 0; c0 < k - 5; c0++) {
            memcpy(m1[0], R1[c0], 6); memcpy(m2[0], R2[c0], 6);
            int a0 = (c0 < n_orb_a) ? 1 : 0;
            for (int c1 = c0 + 1; c1 < k - 4; c1++) {
                memcpy(m1[1], R1[c1], 6); memcpy(m2[1], R2[c1], 6);
                int a1 = a0 + ((c1 < n_orb_a) ? 1 : 0);
                for (int c2 = c1 + 1; c2 < k - 3; c2++) {
                    memcpy(m1[2], R1[c2], 6); memcpy(m2[2], R2[c2], 6);
                    int a2 = a1 + ((c2 < n_orb_a) ? 1 : 0);
                    for (int c3 = c2 + 1; c3 < k - 2; c3++) {
                        memcpy(m1[3], R1[c3], 6); memcpy(m2[3], R2[c3], 6);
                        int a3 = a2 + ((c3 < n_orb_a) ? 1 : 0);
                        for (int c4 = c3 + 1; c4 < k - 1; c4++) {
                            memcpy(m1[4], R1[c4], 6); memcpy(m2[4], R2[c4], 6);
                            int a4 = a3 + ((c4 < n_orb_a) ? 1 : 0);
                            for (int c5 = c4 + 1; c5 < k; c5++) {
                                memcpy(m1[5], R1[c5], 6); memcpy(m2[5], R2[c5], 6);
                                int a = a4 + ((c5 < n_orb_a) ? 1 : 0);
                                int ok1 = is_nonsingular_6x6(f, m1);
                                int ok2 = is_nonsingular_6x6(f, m2);
                                lchk++;
                                if (!ok1) ld1[a]++;
                                if (!ok2) ld2[a]++;
                                if (!ok1 && !ok2) lbt[a]++;
                            }
                        }
                    }
                }
            }
        }
        #pragma omp critical
        {
            checked += lchk;
            for (int i = 0; i < 7; i++) { dep1[i] += ld1[i]; dep2[i] += ld2[i]; both[i] += lbt[i]; }
        }
    }
    if (out_checked) *out_checked = checked;
    uint64_t unc = 0;
    for (int i = 0; i < 7; i++) unc += both[i];
    return unc;
}

static int find_sherwood(const VField *f, int k, const uint8_t R[V_MAX_K][6], uint8_t out_v[6]) {
    int q = f->q;
    for (int lead = 0; lead < 6; lead++) {
        uint64_t lim = 1;
        for (int t = 0; t < 5 - lead; t++) lim *= (uint64_t)q;
        for (uint64_t code = 0; code < lim; code++) {
            uint8_t v[6] = {0, 0, 0, 0, 0, 0};
            v[lead] = 1;
            uint64_t tmp = code;
            for (int pos = 5; pos > lead; pos--) { v[pos] = (uint8_t)(tmp % (uint64_t)q); tmp /= (uint64_t)q; }
            int ok = 1;
            for (int col = 0; col < k; col++) {
                uint8_t dot = 0;
                for (int j = lead; j < 6; j++) dot = f->add[dot][f->mul[v[j]][R[col][j]]];
                if (dot == 0) { ok = 0; break; }
            }
            if (ok) { memcpy(out_v, v, 6); return 1; }
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <cphf.json> [--threads N]\n", argv[0]);
        return 2;
    }
    const char *path = argv[1];
    int threads = 2;
    for (int i = 2; i < argc; i++)
        if (strcmp(argv[i], "--threads") == 0 && i + 1 < argc) threads = atoi(argv[++i]);
    omp_set_num_threads(threads);

    FILE *fp = fopen(path, "rb");
    if (!fp) { perror("fopen"); return 2; }
    fseek(fp, 0, SEEK_END);
    long sz = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    char *buf = (char *)malloc((size_t)sz + 1);
    if (fread(buf, 1, (size_t)sz, fp) != (size_t)sz) { perror("fread"); return 2; }
    buf[sz] = '\0';
    fclose(fp);

    int q = 0, k = 0, n_orb_a = 0;
    if (!parse_int_field(buf, "q", &q) || !parse_int_field(buf, "k", &k)) {
        fprintf(stderr, "ERROR: missing q or k in %s\n", path);
        return 2;
    }
    if (!parse_int_field(buf, "n_orbit_a", &n_orb_a)) n_orb_a = k / 2;
    if (k < 6 || k > V_MAX_K) { fprintf(stderr, "Invalid k=%d\n", k); return 2; }

    uint8_t R1[V_MAX_K][6], R2[V_MAX_K][6];
    if (!parse_matrix_field(buf, "R1", k, q, R1) || !parse_matrix_field(buf, "R2", k, q, R2)) {
        fprintf(stderr, "ERROR: failed to parse R1/R2 in %s\n", path);
        return 2;
    }
    free(buf);

    VField f;
    vfield_init(&f, q);

    double t0 = v_now();
    uint64_t dep1[7], dep2[7], both[7], checked = 0;
    uint64_t unc = verify_all_6tuples(&f, k, n_orb_a, R1, R2, dep1, dep2, both, &checked);
    double dt = v_now() - t0;

    printf("INDEPENDENT_C_VERIFY %s: q=%d k=%d n_orb_a=%d checked=%llu unc=%llu time=%.4fs\n",
           path, q, k, n_orb_a, (unsigned long long)checked, (unsigned long long)unc, dt);
    printf("  dep1=[%llu,%llu,%llu,%llu,%llu,%llu,%llu]\n",
           (unsigned long long)dep1[0], (unsigned long long)dep1[1], (unsigned long long)dep1[2],
           (unsigned long long)dep1[3], (unsigned long long)dep1[4], (unsigned long long)dep1[5],
           (unsigned long long)dep1[6]);
    printf("  dep2=[%llu,%llu,%llu,%llu,%llu,%llu,%llu]\n",
           (unsigned long long)dep2[0], (unsigned long long)dep2[1], (unsigned long long)dep2[2],
           (unsigned long long)dep2[3], (unsigned long long)dep2[4], (unsigned long long)dep2[5],
           (unsigned long long)dep2[6]);
    printf("  both=[%llu,%llu,%llu,%llu,%llu,%llu,%llu]\n",
           (unsigned long long)both[0], (unsigned long long)both[1], (unsigned long long)both[2],
           (unsigned long long)both[3], (unsigned long long)both[4], (unsigned long long)both[5],
           (unsigned long long)both[6]);

    /* Negative control 1: duplicate col 0 -> col 1 in both rows */
    uint8_t R1_b[V_MAX_K][6], R2_b[V_MAX_K][6];
    memcpy(R1_b, R1, sizeof(R1)); memcpy(R2_b, R2, sizeof(R2));
    memcpy(R1_b[1], R1_b[0], 6); memcpy(R2_b[1], R2_b[0], 6);
    uint64_t nd1[7], nd2[7], nbt[7], nchk = 0;
    uint64_t unc_neg1 = verify_all_6tuples(&f, k, n_orb_a, R1_b, R2_b, nd1, nd2, nbt, &nchk);
    printf("  neg_control_dup_col: unc=%llu (%s)\n", (unsigned long long)unc_neg1, unc_neg1 > 0 ? "FAIL as expected" : "UNEXPECTED PASS");

    /* Negative control 2: zero out col 0 in both rows */
    memcpy(R1_b, R1, sizeof(R1)); memcpy(R2_b, R2, sizeof(R2));
    memset(R1_b[0], 0, 6); memset(R2_b[0], 0, 6);
    uint64_t unc_neg2 = verify_all_6tuples(&f, k, n_orb_a, R1_b, R2_b, nd1, nd2, nbt, &nchk);
    printf("  neg_control_zero_col: unc=%llu (%s)\n", (unsigned long long)unc_neg2, unc_neg2 > 0 ? "FAIL as expected" : "UNEXPECTED PASS");

    /* Sherwood hyperplane check */
    uint8_t v1[6], v2[6];
    int s1 = find_sherwood(&f, k, R1, v1);
    int s2 = find_sherwood(&f, k, R2, v2);
    uint64_t q6 = 1; for (int i = 0; i < 6; i++) q6 *= (uint64_t)q;
    printf("  sherwood: R1=%s", s1 ? "" : "NONE");
    if (s1) printf("[%d,%d,%d,%d,%d,%d]", v1[0], v1[1], v1[2], v1[3], v1[4], v1[5]);
    printf(" R2=%s", s2 ? "" : "NONE");
    if (s2) printf("[%d,%d,%d,%d,%d,%d]", v2[0], v2[1], v2[2], v2[3], v2[4], v2[5]);
    if (s1 && s2) printf(" -> N=2*q^6-q=%llu\n", (unsigned long long)(2 * q6 - (uint64_t)q));
    else printf(" -> N=2*q^6-1=%llu\n", (unsigned long long)(2 * q6 - 1));

    return (unc == 0 && unc_neg1 > 0 && unc_neg2 > 0) ? 0 : 1;
}
