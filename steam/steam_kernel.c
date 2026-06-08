/*
 * steam_kernel.c
 * 
 * A self-contained C "kernel" that connects to the Steam store,
 * fetches game data via HTTPS, parses JSON, and performs
 * mathematical analysis (linear algebra, statistics).
 *
 * Compilation (Linux/macOS):
 *   gcc -o steam_kernel steam_kernel.c -lssl -lcrypto -lm
 *
 * Dependencies: OpenSSL (libssl-dev), math library (-lm)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <math.h>

/* ---------------------------------------------------------------------------
 *  Minimal JSON tokenizer (jsmn-style, fully embedded)
 * ------------------------------------------------------------------------- */
#define JSMN_STRICT
#include "jsmn.h"   /* <-- you can copy the public domain jsmn.h alongside */

/* ---------------------------------------------------------------------------
 *  Data structures
 * ------------------------------------------------------------------------- */
#define MAX_GAMES 100
#define MAX_STR_LEN 256

typedef struct {
    int    appid;
    char   name[MAX_STR_LEN];
    double final_price;      /* in USD */
    double original_price;
    int    discount_percent;
    int    review_percent;
    int    total_reviews;
} SteamGame;

typedef struct {
    SteamGame games[MAX_GAMES];
    int count;
} GameList;

/* ---------------------------------------------------------------------------
 *  Mathematical analysis functions
 * ------------------------------------------------------------------------- */

/* Mean */
double math_mean(const double *arr, int n) {
    double sum = 0.0;
    for (int i = 0; i < n; i++) sum += arr[i];
    return n > 0 ? sum / n : 0.0;
}

/* Median (requires sorted array) */
double math_median(double *arr, int n) {
    if (n == 0) return 0.0;
    /* sort a copy */
    double *copy = malloc(n * sizeof(double));
    memcpy(copy, arr, n * sizeof(double));
    for (int i = 0; i < n-1; i++)
        for (int j = i+1; j < n; j++)
            if (copy[i] > copy[j]) {
                double tmp = copy[i];
                copy[i] = copy[j];
                copy[j] = tmp;
            }
    double med = (n % 2) ? copy[n/2] : (copy[n/2 - 1] + copy[n/2]) / 2.0;
    free(copy);
    return med;
}

/* Standard deviation */
double math_stddev(const double *arr, int n) {
    if (n <= 1) return 0.0;
    double mean = math_mean(arr, n);
    double sum_sq = 0.0;
    for (int i = 0; i < n; i++) {
        double diff = arr[i] - mean;
        sum_sq += diff * diff;
    }
    return sqrt(sum_sq / (n - 1));
}

/* Bayesian Wilson score (lower bound of confidence interval) */
double bayesian_wilson(double positive, double total, double z) {
    if (total <= 0) return 0.0;
    double p = positive / total;
    double z2 = z * z;
    double denom = 1.0 + z2 / total;
    double center = (p + z2 / (2.0 * total)) / denom;
    double margin = z * sqrt((p * (1.0 - p) + z2 / (4.0 * total)) / total) / denom;
    return center - margin;
}

/* Cosine similarity between two feature vectors */
double cosine_similarity(const double *a, const double *b, int len) {
    double dot = 0.0, mag_a = 0.0, mag_b = 0.0;
    for (int i = 0; i < len; i++) {
        dot += a[i] * b[i];
        mag_a += a[i] * a[i];
        mag_b += b[i] * b[i];
    }
    mag_a = sqrt(mag_a);
    mag_b = sqrt(mag_b);
    if (mag_a < 1e-6 || mag_b < 1e-6) return 0.0;
    return dot / (mag_a * mag_b);
}

/* Convert a game to a feature vector (7 features) */
void game_to_features(const SteamGame *g, double *feat) {
    feat[0] = g->final_price / 100.0;            /* normalized price */
    feat[1] = g->original_price > 0 ? g->final_price / g->original_price : 1.0;
    feat[2] = g->discount_percent / 100.0;
    feat[3] = g->review_percent / 100.0;
    feat[4] = g->total_reviews > 0 ? log1p(g->total_reviews) / 15.0 : 0.0;
    feat[5] = 0.5;                               /* dummy tag count */
    feat[6] = 0.3;                               /* dummy age */
}

/* ---------------------------------------------------------------------------
 *  SSL/TCP networking
 * ------------------------------------------------------------------------- */

/* Global SSL context */
static SSL_CTX *ssl_ctx = NULL;

/* Initialize OpenSSL */
void ssl_init(void) {
    SSL_load_error_strings();
    OpenSSL_add_ssl_algorithms();
    ssl_ctx = SSL_CTX_new(TLS_client_method());
    if (!ssl_ctx) {
        fprintf(stderr, "SSL_CTX_new() failed\n");
        exit(EXIT_FAILURE);
    }
}

/* Cleanup */
void ssl_cleanup(void) {
    if (ssl_ctx) SSL_CTX_free(ssl_ctx);
    EVP_cleanup();
}

/* Connect to host:port and return file descriptor */
int tcp_connect(const char *host, int port) {
    struct hostent *hp = gethostbyname(host);
    if (!hp) {
        fprintf(stderr, "gethostbyname(%s) failed\n", host);
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    memcpy(&addr.sin_addr, hp->h_addr, hp->h_length);
    addr.sin_port = htons(port);

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket");
        return -1;
    }

    if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("connect");
        close(sock);
        return -1;
    }

    return sock;
}

/* Perform HTTPS GET request and return the response body */
char *https_get(const char *host, const char *path) {
    int sock = tcp_connect(host, 443);
    if (sock < 0) return NULL;

    SSL *ssl = SSL_new(ssl_ctx);
    SSL_set_fd(ssl, sock);
    if (SSL_connect(ssl) <= 0) {
        fprintf(stderr, "SSL_connect failed\n");
        close(sock);
        SSL_free(ssl);
        return NULL;
    }

    /* Build HTTP request */
    char request[1024];
    snprintf(request, sizeof(request),
        "GET %s HTTP/1.1\r\n"
        "Host: %s\r\n"
        "User-Agent: SteamKernel/1.0\r\n"
        "Accept: application/json\r\n"
        "Connection: close\r\n\r\n",
        path, host);

    SSL_write(ssl, request, strlen(request));

    /* Read response */
    char *response = malloc(1);
    int resp_size = 0;
    char buf[4096];
    int bytes;
    while ((bytes = SSL_read(ssl, buf, sizeof(buf))) > 0) {
        response = realloc(response, resp_size + bytes + 1);
        memcpy(response + resp_size, buf, bytes);
        resp_size += bytes;
    }
    response[resp_size] = '\0';

    SSL_shutdown(ssl);
    SSL_free(ssl);
    close(sock);

    /* Separate header/body */
    char *body = strstr(response, "\r\n\r\n");
    if (body) {
        body += 4;
        char *ret = strdup(body);
        free(response);
        return ret;
    } else {
        free(response);
        return NULL;
    }
}

/* ---------------------------------------------------------------------------
 *  JSON parsing helper (uses jsmn.h)
 * ------------------------------------------------------------------------- */
static int jsoneq(const char *json, jsmntok_t *tok, const char *s) {
    if (tok->type == JSMN_STRING && (int)strlen(s) == tok->end - tok->start &&
        strncmp(json + tok->start, s, tok->end - tok->start) == 0) {
        return 0;
    }
    return -1;
}

/* Parse the /api/featured/ JSON and fill GameList */
void parse_featured_json(const char *json_str, GameList *list) {
    jsmn_parser parser;
    jsmntok_t tokens[4096];
    jsmn_init(&parser);
    int num_tokens = jsmn_parse(&parser, json_str, strlen(json_str), tokens, 4096);
    if (num_tokens < 0) {
        fprintf(stderr, "JSON parse error %d\n", num_tokens);
        return;
    }

    /* Navigate JSON tree: find "featured_win" array */
    for (int i = 0; i < num_tokens; i++) {
        if (jsoneq(json_str, &tokens[i], "featured_win") == 0) {
            /* We are at the key, next token should be the array */
            if (i+1 < num_tokens && tokens[i+1].type == JSMN_ARRAY) {
                int arr_size = tokens[i+1].size;
                int obj_start = i+2;  /* first element inside array */
                for (int j = 0; j < arr_size && list->count < MAX_GAMES; j++) {
                    if (obj_start < num_tokens && tokens[obj_start].type == JSMN_OBJECT) {
                        SteamGame game;
                        memset(&game, 0, sizeof(game));
                        int obj_end = obj_start + 1;
                        /* count to end of object */
                        while (obj_end < num_tokens && tokens[obj_end].start < tokens[obj_start].end)
                            obj_end++;

                        /* Extract fields */
                        for (int k = obj_start; k < obj_end; k++) {
                            if (jsoneq(json_str, &tokens[k], "id") == 0 && k+1 < num_tokens) {
                                char tmp[32] = {0};
                                int len = tokens[k+1].end - tokens[k+1].start;
                                strncpy(tmp, json_str + tokens[k+1].start, len);
                                game.appid = atoi(tmp);
                            }
                            else if (jsoneq(json_str, &tokens[k], "name") == 0 && k+1 < num_tokens) {
                                int len = tokens[k+1].end - tokens[k+1].start;
                                len = len < MAX_STR_LEN-1 ? len : MAX_STR_LEN-1;
                                strncpy(game.name, json_str + tokens[k+1].start, len);
                            }
                            else if (jsoneq(json_str, &tokens[k], "final_price") == 0 && k+1 < num_tokens) {
                                char tmp[32] = {0};
                                int len = tokens[k+1].end - tokens[k+1].start;
                                strncpy(tmp, json_str + tokens[k+1].start, len);
                                game.final_price = atof(tmp) / 100.0;  /* Steam API returns cents */
                            }
                            else if (jsoneq(json_str, &tokens[k], "original_price") == 0 && k+1 < num_tokens) {
                                char tmp[32] = {0};
                                int len = tokens[k+1].end - tokens[k+1].start;
                                strncpy(tmp, json_str + tokens[k+1].start, len);
                                game.original_price = atof(tmp) / 100.0;
                            }
                            else if (jsoneq(json_str, &tokens[k], "discount_percent") == 0 && k+1 < num_tokens) {
                                char tmp[32] = {0};
                                int len = tokens[k+1].end - tokens[k+1].start;
                                strncpy(tmp, json_str + tokens[k+1].start, len);
                                game.discount_percent = atoi(tmp);
                            }
                            /* additional fields would be added similarly */
                        }
                        list->games[list->count++] = game;
                        obj_start = obj_end;
                    } else break;
                }
            }
        }
    }
}

/* ---------------------------------------------------------------------------
 *  Main kernel
 * ------------------------------------------------------------------------- */
int main(void) {
    printf("========================================\n");
    printf("  Steam Store C Kernel v1.0\n");
    printf("========================================\n\n");

    /* 1. Initialize SSL */
    ssl_init();

    /* 2. Download featured games JSON */
    printf("[1] Connecting to store.steampowered.com...\n");
    char *json = https_get("store.steampowered.com", "/api/featured/");
    if (!json) {
        fprintf(stderr, "Failed to retrieve JSON.\n");
        ssl_cleanup();
        return 1;
    }
    printf("    JSON received (%zu bytes)\n", strlen(json));

    /* 3. Parse JSON */
    GameList games;
    memset(&games, 0, sizeof(games));
    parse_featured_json(json, &games);
    free(json);

    printf("[2] Parsed %d featured games.\n\n", games.count);

    /* 4. Mathematical analysis */
    printf("=== Mathematical Analysis ===\n");

    /* Extract price array */
    double prices[MAX_GAMES];
    int price_count = 0;
    for (int i = 0; i < games.count; i++) {
        if (games.games[i].final_price > 0) {
            prices[price_count++] = games.games[i].final_price;
        }
    }

    if (price_count > 0) {
        printf("\nPrice statistics:\n");
        printf("  Mean:   $%.2f\n", math_mean(prices, price_count));
        printf("  Median: $%.2f\n", math_median(prices, price_count));
        printf("  StdDev: $%.2f\n", math_stddev(prices, price_count));
    }

    /* Bayesian rating (assuming review_percent is set; we'll simulate values) */
    printf("\nBayesian Wilson scores (simulated reviews):\n");
    for (int i = 0; i < games.count && i < 5; i++) {
        /* Simulate: we don't have review data from this API, so we'll assign arbitrary numbers */
        int reviews = 100 + rand() % 5000;
        int pos = (int)((70 + rand() % 30) / 100.0 * reviews); /* positive reviews 70-99% */
        double score = bayesian_wilson(pos, reviews, 1.96);
        printf("  %-30s score=%.3f\n", games.games[i].name, score);
    }

    /* Game similarity (feature vectors) */
    printf("\nCosine similarity between first 3 games:\n");
    if (games.count >= 3) {
        double f1[7], f2[7], f3[7];
        game_to_features(&games.games[0], f1);
        game_to_features(&games.games[1], f2);
        game_to_features(&games.games[2], f3);
        printf("  %s <-> %s : %.3f\n", games.games[0].name, games.games[1].name,
               cosine_similarity(f1, f2, 7));
        printf("  %s <-> %s : %.3f\n", games.games[0].name, games.games[2].name,
               cosine_similarity(f1, f3, 7));
        printf("  %s <-> %s : %.3f\n", games.games[1].name, games.games[2].name,
               cosine_similarity(f2, f3, 7));
    }

    printf("\n[✓] Steam kernel execution complete.\n");

    ssl_cleanup();
    return 0;
}