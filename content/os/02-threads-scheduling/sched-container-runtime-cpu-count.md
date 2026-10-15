---
id: sched-container-runtime-cpu-count
title: Count usable CPU capacity inside containers
level: advanced
minutes: 2
sourceLesson: sched-multicore
summary: Visible host CPU count, affinity and cgroup quota describe different limits.
---

## Runtimes that count the wrong CPUs

Many runtimes size their worker pools from the CPU count, and the CPU count visible inside a container is usually the **host's**:

- Python's `os.cpu_count()` returns the host's logical CPUs. `os.process_cpu_count()` (3.13+) respects the affinity mask, but **not** a `cpu.max` quota.
- Go 1.25 introduced container-aware defaults: logical CPUs, affinity and cgroup CPU bandwidth all participate. Fractional quotas are rounded up, and the default generally stays at least 2 unless CPU count or affinity is lower. Explicit settings and compatibility controls can override this.
- The JVM has been container-aware since JDK 10 (backported to 8u191).

For example, 64 visible logical CPUs, no narrower affinity and no Python CPU-count override can yield a default maximum of 64 processes despite a two-CPU quota. Workers start as jobs are submitted, with behavior depending on Python version and start method. A simple cgroup-v2 quota reader is:

```python
PATH = "/sys/fs/cgroup/cpu.max"

def cpu_quota():
    try:
        # Read one visible budget pair.
        with open(PATH) as f:
            quota, period = f.read().split()
    except FileNotFoundError:
        return None  # not cgroup v2
    if quota == "max":
        return None  # no limit
    # CPU-time budget per unit wall time.
    return int(quota) / int(period)

# "200000 100000" -> 2.0
# Assumes this path is the relevant cgroup.
```

This helper reads one visible cgroup only. It does not discover the process's cgroup or ancestor limits, handle cgroup v1, or combine quota with affinity. An unlimited leaf can still have a constrained ancestor.
## Pitfalls

- **Treating CPU limits as harmless.** A quota caps every period, not the average. Bursty, multi-threaded services get throttled while looking underused.
- **Ignoring SMT.** "16 CPUs" may be 8 cores. Two hot threads on siblings don't double throughput.
- **Over-pinning.** A hard affinity mask disables the balancer's ability to help; it's only better when you've measured.
- **NUMA-blind initialisation.** First touch puts memory where it's first written, not where it's used.
- **Trusting `cpu_count()`** inside containers.

## Key takeaways
- Visible host CPU count, affinity and cgroup quota describe different limits.
- Runtime defaults depend on versions and configuration; verify what the deployed interpreter uses.
- A single cpu.max reader is illustrative and does not discover ancestor limits or combine all constraints.

## Further reading
- [Multiprocessor Scheduling (Advanced) — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-multi.pdf)
- [Scheduler Domains — Linux kernel docs](https://docs.kernel.org/scheduler/sched-domains.html)
- [CFS Bandwidth Control — Linux kernel docs](https://docs.kernel.org/scheduler/sched-bwc.html)
- [Control Group v2 — Linux kernel docs](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [sched_setaffinity(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html)
- [numa(7) — Linux manual page](https://man7.org/linux/man-pages/man7/numa.7.html)
- [Non-uniform memory access — Wikipedia](https://en.wikipedia.org/wiki/Non-uniform_memory_access)
- [Go 1.25 release notes (container-aware GOMAXPROCS)](https://go.dev/doc/go1.25)
