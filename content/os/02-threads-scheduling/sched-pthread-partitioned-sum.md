---
id: sched-pthread-partitioned-sum
title: Create threads and combine independent results
level: basic
minutes: 5
sourceLesson: sched-thread-apis
summary: Pass stable argument structures to pthread_create and check its returned error number.
---

The preceding units explain thread state and runtime mappings. This unit uses the POSIX threads (**pthreads**) API on Linux and macOS to partition an array and combine completed results. Later units cover ownership, pools and Python's interpreter lock.
## The pthreads lifecycle

Four calls cover most of what you need:

| Call | What it does |
|---|---|
| `pthread_create` | Start a thread running a function |
| `pthread_join` | Wait for a thread to finish, collect its result |
| `pthread_detach` | Let a thread clean up after itself; nobody will join it |
| `pthread_exit` | End the calling thread |

The signature of `pthread_create` is worth reading slowly:

```c
int pthread_create(
    pthread_t *thread,     /* out: id */
    const pthread_attr_t *attr, /* NULL */
    void *(*start)(void *),
    void *arg);
```

The new thread calls `start(arg)`. One `void *` in, one `void *` out: to pass several values you pass a pointer to a struct.
## A worked example: summing an array in parallel

Each thread sums a quarter of an array into its own struct. The main thread joins them in turn and adds up the parts.

```c
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
    /* Sum only this worker’s slice. */
    for (size_t i = j->lo; i < j->hi; i++)
        s += j->data[i];
    /* Publish once, after local updates. */
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
        /* Assign a distinct slice. */
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
        /* Join completes these writes. */
        total += jobs[t].sum;
    }
    /* Sum of integers 0 through LEN - 1. */
    printf("%ld\n", total);
    free(data);
    return 0;
}
```

Compile with `cc -O2 -pthread sum.c`. It prints `499999500000`, the sum of 0 to 999,999. You can check that without running it, using the classic formula for adding up consecutive whole numbers:

```formula
S = 0 + 1 + 2 + … + (n − 1)
S = (n(n − 1)) / 2
S = 1000000 × 999999 / 2
S = 499999500000
where
S: the total the program prints
n: how many numbers are added, LEN = 1,000,000 here (the values 0 to 999,999)
…: "and so on" through every whole number in between
In words: pair the smallest number with the largest, the next smallest with the next largest, and so on; every pair adds up to n − 1, and there are n / 2 pairs.
```

The answer is about 500 billion, far beyond the roughly 2.1 billion a 32-bit integer can hold, which is why the program insists on a 64-bit `long`.

Points worth noticing:

- **No locks are needed**, because no two threads write the same memory. Each writes only its own `jobs[t].sum`, and the main thread reads it only after `pthread_join` guarantees the thread has finished. Partitioning work so that threads don't share writable data is the best concurrency strategy there is.
- **Lifecycle calls such as create/join return an error number** (such as `EAGAIN`) rather than returning −1 and setting `errno`. Hence `strerror(rc)`.
- **The sum is kept in a local** and written once. The structs are adjacent; result fields from different structs may share a cache line depending on alignment and layout. If each thread updated `j->sum` on every iteration, the cores would keep stealing that cache line from each other (**false sharing**), which can make the parallel version slower than the serial one.

## Key takeaways
- Pass stable argument structures to pthread_create and check its returned error number.
- Partitioned writes followed by joins let the caller read completed results without a lock.
- Adjacent independent counters can still contend through a shared cache line.

## Further reading
- [pthread_create(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_create.3.html)
- [pthread_detach(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_detach.3.html)
- [Interlude: Thread API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-api.pdf)
- [concurrent.futures — Python docs](https://docs.python.org/3/library/concurrent.futures.html)
- [Python support for free threading — Python docs](https://docs.python.org/3/howto/free-threading-python.html)
- [PEP 703: Making the GIL optional in CPython](https://peps.python.org/pep-0703/)
