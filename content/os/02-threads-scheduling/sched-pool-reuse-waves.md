---
id: sched-pool-reuse-waves
title: Reuse workers and estimate waiting-job waves
level: basic
minutes: 3
sourceLesson: sched-thread-apis
summary: A pool reuses a bounded number of workers rather than creating an unbounded thread per request.
---

## Thread pools

Creating a thread involves allocation and runtime/OS work; no reproducible creation-time benchmark is supplied here. More importantly, a server that creates one thread per request without admission or concurrency limits has **no application-level bound**: a traffic spike can create thousands of threads until resource limits or failures intervene.

A bounded **thread pool** reuses workers and caps active jobs; its submission queue still needs an overload policy. A fixed set of worker threads pulls jobs from a shared queue:

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
    # Sleep releases the GIL while waiting.
    time.sleep(0.5)  # stands in for I/O
    return i * i

start = time.perf_counter()
pool = ThreadPoolExecutor(max_workers=10)
with pool as ex:
    # map yields results in input order.
    results = list(ex.map(fetch, range(20)))
took = time.perf_counter() - start

# Squares are fixed; duration varies.
print(results[:5], f"{took:.1f}s")
```

The values are `[0, 1, 4, 9, 16]`; the elapsed-time suffix is machine-dependent and should be near or above the ideal one-second schedule. When every job takes the same time, a pool works through them in "waves": each wave runs one job on every worker at once.

```formula
N_waves = ⌈N_jobs / N_workers⌉
T ≈ N_waves t_job
N_waves = ⌈20 / 10⌉ = 2
T ≈ 2 × 0.5 s = 1 s
where
N_waves: how many rounds of jobs the pool needs
N_jobs: the number of jobs submitted, 20 here
N_workers: the number of worker threads, 10 here (max_workers)
⌈x⌉: ceiling: round x up to the next whole number, because a part-filled last wave still takes a whole job's time
T: the total elapsed time, in seconds (s)
t_job: how long one job takes, 0.5 s here
≈: approximately equal to (ignores start-up and switching overhead)
s: seconds
In words: divide the jobs between the workers, round up to whole waves, and each wave takes as long as one job.
```

So twenty half-second jobs on ten workers take about 1 second instead of 20 × 0.5 = 10 seconds serially. This assumes the jobs mostly wait (here they sleep), so the workers do not compete for CPU; Pure-Python CPU-bound jobs in one GIL-enabled interpreter cannot run bytecode simultaneously. The later GIL unit covers native extensions and other interpreter builds. `map` returns results in input order, regardless of which finished first.

## Key takeaways
- A pool reuses a bounded number of workers rather than creating an unbounded thread per request.
- Equal-duration waiting jobs finish in whole waves; map preserves input order.
- Elapsed time depends on scheduling and overhead; the wave calculation is an ideal approximation.

## Further reading
- [pthread_create(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_create.3.html)
- [pthread_detach(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_detach.3.html)
- [Interlude: Thread API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-api.pdf)
- [concurrent.futures — Python docs](https://docs.python.org/3/library/concurrent.futures.html)
- [Python support for free threading — Python docs](https://docs.python.org/3/howto/free-threading-python.html)
- [PEP 703: Making the GIL optional in CPython](https://peps.python.org/pep-0703/)
