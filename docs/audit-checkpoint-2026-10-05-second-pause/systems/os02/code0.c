#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NT 4
_Static_assert(sizeof(long) >= 8,
               "needs 64-bit long");
#define LEN 1000000

struct job {
    const long *data;
    size_t lo, hi;
    long sum;           /* result */
};

static void *sum_part(void *arg) {
    struct job *j = arg;
    long s = 0;         /* local: fast */
    for (size_t i = j->lo; i < j->hi; i++)
        s += j->data[i];
    j->sum = s;
    return NULL;
}

int main(void) {
    long *data = malloc(LEN * sizeof *data);
    if (!data) return 1;
    for (long i = 0; i < LEN; i++)
        data[i] = i;

    pthread_t tid[NT];
    struct job jobs[NT];
    size_t chunk = LEN / NT;

    for (int t = 0; t < NT; t++) {
        jobs[t].data = data;
        jobs[t].lo = t * chunk;
        jobs[t].hi = (t + 1) * chunk;
        int rc = pthread_create(
            &tid[t], NULL,
            sum_part, &jobs[t]);
        if (rc != 0) {
            fprintf(stderr, "create: %s\n",
                    strerror(rc));
            return 1;
        }
    }

    long total = 0;
    for (int t = 0; t < NT; t++) {
        int rc = pthread_join(tid[t], NULL);
        if (rc != 0) return 1;
        total += jobs[t].sum;
    }
    printf("%ld\n", total);
    free(data);
    return 0;
}
