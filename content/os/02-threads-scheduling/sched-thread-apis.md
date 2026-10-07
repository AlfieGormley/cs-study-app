---
id: sched-thread-apis
title: Thread APIs in practice
level: basic
minutes: 12
summary: Creating, joining and detaching POSIX threads in C, the bugs everyone writes first, thread pools and how to size them, and what Python's GIL does and does not protect you from.
---

The previous lesson covered what a thread is. This one is about using them: the POSIX threads (**pthreads**) API that underlies threading on Linux and macOS, the thread pools that most real programs use instead of raw threads, and Python's Global Interpreter Lock.

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

### A worked example: summing an array in parallel

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
```

Compile with `cc -O2 -pthread sum.c`. It prints `499999500000`, the sum of 0 to 999,999 (n(n−1)/2 with n = 1,000,000).

Points worth noticing:

- **No locks are needed**, because no two threads write the same memory. Each writes only its own `jobs[t].sum`, and the main thread reads it only after `pthread_join` guarantees the thread has finished. Partitioning work so that threads don't share writable data is the best concurrency strategy there is.
- **Lifecycle calls such as create/join return an error number** (such as `EAGAIN`) rather than returning −1 and setting `errno`. Hence `strerror(rc)`.
- **The sum is kept in a local** and written once. The structs are adjacent; result fields from different structs may share a cache line depending on alignment and layout. If each thread updated `j->sum` on every iteration, the cores would keep stealing that cache line from each other (**false sharing**), which can make the parallel version slower than the serial one.

### Join, detach, or leak

When a thread finishes, its return value and stack stay around until someone collects them:

- **Joinable** (the default): another thread must call `pthread_join`. If nobody ever does, the finished thread's resources are never freed. It is the thread equivalent of a zombie process.
- **Detached**: call `pthread_detach(tid)` (or create it with the `PTHREAD_CREATE_DETACHED` attribute). Its resources are freed as soon as it exits. You can no longer join it or get its result.

Use join when you need the result or need to know the work is done. Use detach for fire-and-forget background threads.

> [!warning] Returning from `main` kills every thread
> Returning from `main` calls `exit()`, which ends the whole process, including threads still running. Join your threads first, or end `main` with `pthread_exit(NULL)`, which ends only the main thread and lets the others carry on.

### The bugs everyone writes first

**Passing the loop variable's address:**

```c
for (int i = 0; i < 4; i++)
    pthread_create(&t[i], NULL, f, &i);
```

All four threads get a pointer to the *same* `i`. Concurrent unsynchronized reads and writes constitute a C data race (undefined behavior), and use after the loop can also exceed its lifetime. Duplicates or `4` are possible symptoms, not guaranteed outcomes. Give each thread its own argument: an array element, a `malloc`'d struct, or a platform-supported value-through-pointer convention (not a universally portable integer transport).

**Returning a pointer to a local.** A thread that returns `&result`, where `result` is a local variable, hands back a pointer to an object whose lifetime has ended, regardless of whether its stack storage is physically reclaimed yet. Return a heap pointer or write into memory the caller owns.

**Assuming an order.** Thread creation order says nothing about execution order. Threads started 1, 2, 3 may run, print and finish in any order.

## Thread pools

Creating a thread involves allocation and runtime/OS work; no reproducible creation-time benchmark is supplied here. More importantly, a server that creates one thread per request has **no upper bound**: a traffic spike creates thousands of threads, which thrash the scheduler and exhaust memory.

A **thread pool** fixes both. A fixed set of worker threads pulls tasks from a shared queue:

```
 submit()     task queue      workers
 -------->  [t5][t4][t3]  -->  W1 (t1)
                          -->  W2 (t2)
                          -->  W3 (idle)
```

Threads are created once and reused, and the pool size caps concurrency. Examples include Java's `ExecutorService`, the worker pools in web servers, database connection handlers, and Python's `concurrent.futures`.

```python
from concurrent.futures import (
    ThreadPoolExecutor)
import time

def fetch(i):
    time.sleep(0.5)  # stands in for I/O
    return i * i

start = time.perf_counter()
pool = ThreadPoolExecutor(max_workers=10)
with pool as ex:
    results = list(ex.map(fetch, range(20)))
took = time.perf_counter() - start
print(results[:5], f"{took:.1f}s")
```

The values are `[0, 1, 4, 9, 16]`; the elapsed-time suffix is machine-dependent and should be near or above the ideal one-second schedule. Twenty half-second tasks on ten workers run in two waves of ten, so about 1 second instead of 10 serially. `map` returns results in input order, regardless of which finished first.

### How big should the pool be?

It depends on what the tasks spend their time doing:

- **CPU-bound** tasks (compression, image processing): start near the effective logical CPU capacity or quota, then measure. SMT, memory bandwidth, blocking, the GIL and task granularity can change the best size.
- **I/O-bound** tasks (waiting on network or disk): more threads than cores, so that something is computing while others wait. A common rule of thumb is

```
threads = cores × (1 + wait / compute)
```

For example, 8 cores and tasks that wait 90 ms on a database for every 10 ms of CPU give 8 × (1 + 9) = 80 threads. Treat it as a starting point and measure.

Since Python 3.13, ThreadPoolExecutor defaults to `min(32, (os.process_cpu_count() or 1) + 4)`, rather than the earlier os.cpu_count-based formula.

> [!warning] Pool-induced deadlock
> If tasks in a pool submit subtasks to the *same* pool and wait for them, they can deadlock. With 2 workers, two parent tasks each wait for a child; both children sit in the queue with no free worker to run them. Use a separate pool for subtasks, or avoid blocking waits inside tasks.

Also watch the **queue**. An unbounded queue hides overload: under a sustained spike it grows until you run out of memory, and every queued request is already late. Bounded queues that reject or apply backpressure fail more honestly.

## Python's GIL

A GIL-enabled CPython interpreter has a **Global Interpreter Lock**: a single lock that a thread must hold to execute Python bytecode. Python threads are real OS threads (1:1), but only one at a time runs Python code.

### Why it exists

CPython manages memory with **reference counts** on every object. Incrementing and decrementing those counts from several threads at once would need a lock or atomic operation on every object access. One big lock was simpler and made single-threaded code fast.

### What it means for CPU-bound code

```python
import threading, time

def spin(n):
    while n:
        n -= 1

N = 20_000_000
t0 = time.perf_counter()
spin(N); spin(N)
dt = time.perf_counter() - t0
print(f"serial:  {dt:.2f}s")

t0 = time.perf_counter()
ts = [threading.Thread(target=spin,
                       args=(N,))
      for _ in range(2)]
for t in ts: t.start()
for t in ts: t.join()
dt = time.perf_counter() - t0
print(f"threads: {dt:.2f}s")
```

On a standard build the two lines print roughly the same time. The threads take turns holding the GIL (a waiting thread asks the holder to drop it after the **switch interval**, 5 ms by default, see `sys.getswitchinterval()`), so there is no parallel speed-up.

### What it does not hurt

The GIL is **released** during blocking I/O (`socket.recv`, file reads, `time.sleep`) and by many C extensions during long computations (NumPy array operations, `hashlib` on large inputs, `zlib`). So threads work well for I/O-bound Python, as in the pool example above, and for code that spends its time in GIL-releasing libraries.

### What it does not prevent: races

A common myth is that the GIL makes Python code thread-safe. It only guarantees that the interpreter's own internals stay consistent. Thread-switch points depend on the CPython version, and bytecodes may invoke user code or extensions. Do not assume a shared **read-modify-write** sequence is atomic:

```python
import threading

counter = 0

def bump(x):
    return x + 1

def work():
    global counter
    for _ in range(1_000_000):
        counter = bump(counter)

ts = [threading.Thread(target=work)
      for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print(counter)
```

This is a race demonstration, not a reproducible output guarantee. Depending on build, scheduling and implementation, it may lose updates or print the expected count; a passing run does not establish correctness. A thread reads `counter`, loses the GIL inside `bump`, and later writes back a stale value, wiping out other threads' increments.

A plain `counter += 1` in the loop often *happens* to give the right answer on recent CPython versions, because of where the interpreter checks for thread switches. That is an implementation detail, not a guarantee, and it is not a safe shared-counter protocol on free-threaded builds. Protect shared state with a `threading.Lock` (the next module covers locks properly).

Some simple built-in operations have useful implementation-level locking or atomicity, but callbacks, custom key methods and free-threaded builds complicate the rules. Use documented guarantees and explicit synchronisation for shared invariants; check-then-insert is not automatically atomic.

### Getting real parallelism in Python

- **Processes**: `multiprocessing` or `ProcessPoolExecutor`. Each process has its own interpreter and GIL. The cost is pickling data between processes.
- **C extensions** that release the GIL (NumPy and friends).
- **Free-threaded CPython** ([PEP 703](https://peps.python.org/pep-0703/)): a build with no GIL, experimental in 3.13 and officially supported (but not the default) from 3.14. It's installed as a separate interpreter, e.g. `python3.14t`. Single-threaded code runs somewhat slower, and C extensions must be marked compatible or the GIL is turned back on.
- **Subinterpreters**: Python 3.14 added `concurrent.interpreters` and `InterpreterPoolExecutor`, where each interpreter has its own GIL.

> [!note] Content gap: runtime measurements
> No reproducible record supports exact thread-creation timing, a particular racy counter output, false-sharing slowdown or ideal pool speed-up. Examples show mechanisms; timing and capacity must be measured for the chosen runtime and workload.

## Key takeaways
- `pthread_create` starts a thread with one `void *` argument; `pthread_join` waits and collects its result; detached threads clean up themselves. Every thread should be joined or detached.
- Returning from `main` ends all threads. Many pthread lifecycle calls report errors directly rather than through errno.
- Give each thread its own argument and its own output slot; partitioned work needs no locks. Beware false sharing on adjacent results.
- Thread pools reuse threads and bound concurrency. Size them near the core count for CPU-bound work and larger for I/O-bound work.
- The GIL stops CPU-bound Python threads running in parallel, but is released for I/O and by many C extensions. It does not make compound operations atomic.

## Further reading
- [pthread_create(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_create.3.html)
- [pthread_detach(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_detach.3.html)
- [Interlude: Thread API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-api.pdf)
- [concurrent.futures — Python docs](https://docs.python.org/3/library/concurrent.futures.html)
- [Python support for free threading — Python docs](https://docs.python.org/3/howto/free-threading-python.html)
- [PEP 703: Making the GIL optional in CPython](https://peps.python.org/pep-0703/)
