---
id: sched-pool-capacity-deadlock
title: Size pools and avoid nested-job deadlock
level: basic
minutes: 4
sourceLesson: sched-thread-apis
summary: Start pool sizing from available compute capacity and measured waiting time.
---

## How big should the pool be?

It depends on what the jobs spend their time doing:

- **CPU-bound** jobs (compression, image processing): start near the effective logical CPU capacity or quota, then measure. SMT, memory bandwidth, blocking, the GIL and job size can change the best size.
- **I/O-bound** jobs (waiting on network or disk): more threads than cores, so that something is computing while others wait.

Where does the I/O-bound number come from? A thread that waits 90 ms for every 10 ms it computes keeps a core busy only a tenth of the time, so you need about ten such threads per core to keep the core busy. In general, each thread keeps a core busy for its compute time divided by its total (wait plus compute) time, and the number of threads needed per core is that fraction turned upside down. A common rule of thumb follows:

```formula
N_thr = N_cpu(1 + (t_wait / t_cpu))
N_thr = 8 × (1 + 90 ms / 10 ms)
N_thr = 8 × (1 + 9) = 80
where
N_thr: the suggested number of threads in the pool
N_cpu: the number of CPU cores the pool can use, 8 here
t_wait: how long each job spends waiting (on a database, disk or network) per piece of work, in milliseconds (ms); 90 ms here
t_cpu: positive CPU-compute time per piece of work, in milliseconds (ms); 10 ms here (the estimate is undefined for zero compute time)
ms: milliseconds, thousandths of a second
In words: the longer jobs wait compared with how long they compute, the more threads you need to keep every core busy; with no waiting at all it gives one thread per core.
```

So 8 cores and jobs that wait 90 ms on a database for every 10 ms of CPU give 80 threads. Treat it as a starting point and measure: it assumes whatever the threads wait on (the database here) can serve 80 requests at once, and it ignores memory per thread and, in Python, the GIL.

Python's own default is simpler. Since Python 3.13, `ThreadPoolExecutor` sizes itself like this when you don't pass `max_workers`:

```formula
N_max = min(32, N_cpu + 4)
N_max = min(32, 8 + 4) = 12
N_max = min(32, 64 + 4) = 32
where
N_max: the default maximum number of worker threads
min(a, b): the smaller of the two values a and b
N_cpu: the number of logical CPUs this process may use, from os.process_cpu_count() (or 1 if that is unknown); 8 and then 64 in the examples
In words: four more workers than CPUs, to cover some I/O waiting, but never more than 32.
```

In Python code that is `min(32, (os.process_cpu_count() or 1) + 4)`, which replaced the earlier formula based on `os.cpu_count()`.

> [!warning] Pool-induced deadlock
> If jobs in a pool submit child jobs to the *same* pool and wait for them, they can deadlock. With 2 workers, two parent jobs each wait for a child; both children sit in the queue with no free worker to run them. Use a separate pool for child jobs, or avoid blocking waits inside jobs.

Also watch the **queue**. An unbounded queue hides overload: under a sustained spike it grows until you run out of memory, and every queued request is already late. Bounded queues that reject or apply backpressure fail more honestly.

## Key takeaways
- Start pool sizing from available compute capacity and measured waiting time.
- The waiting-to-compute ratio is a starting estimate, subject to downstream capacity and memory limits.
- Workers waiting for queued children in the same exhausted pool can deadlock; bound queues to expose overload.

## Further reading
- [pthread_create(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_create.3.html)
- [pthread_detach(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_detach.3.html)
- [Interlude: Thread API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-api.pdf)
- [concurrent.futures — Python docs](https://docs.python.org/3/library/concurrent.futures.html)
- [Python support for free threading — Python docs](https://docs.python.org/3/howto/free-threading-python.html)
- [PEP 703: Making the GIL optional in CPython](https://peps.python.org/pep-0703/)
