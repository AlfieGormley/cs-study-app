---
id: sched-multicore-balancing-affinity
title: Balance load or constrain placement with affinity
level: advanced
minutes: 3
sourceLesson: sched-multicore
summary: Scheduling domains represent hardware locality and guide balancing.
---

## How Linux balances load

Linux describes the topology as nested **scheduling domains**, built at boot:

```
NUMA   : node0 <---------> node1
MC(LLC): [c0 c1 c2 c3]   [c4 c5 c6 c7]
SMT    : [t0 t1] [t2 t3] ...
```

Balancing happens at each level, more often and more eagerly at the bottom, where moving a thread is cheap (siblings share caches), and less often at the top, where it is expensive (crossing NUMA nodes loses cache *and* memory locality).

Three triggers drive it:

1. **Periodic balancing**: from the scheduler tick, each CPU checks whether its domain is imbalanced and pulls tasks if so. Intervals grow with domain level.
2. **Idle balancing**: a CPU that is about to go idle first tries to pull a task from a busier CPU ("newidle" balancing).
3. **Wake-up placement**: when a thread wakes, the kernel chooses a CPU for it. It prefers the previous CPU (warm cache), or an idle CPU sharing the same last-level cache, and considers placing a wakee near its waker.

The balancer also avoids moving a task that ran very recently, treating it as **cache-hot** (the default threshold, `sched_migration_cost`, is 0.5 ms). Balancing considers several signals, including runnable task counts and PELT averages. PELT tracks load, runnable time and running utilization separately; weighted load and CPU utilization are not interchangeable.

> [!note] SMT is treated specially
> Two busy threads on sibling hyper-threads of one core, while another core sits idle, is a bad placement. Linux's balancer prefers spreading busy work across physical cores first, and only then doubling up on siblings.
## CPU affinity: pinning threads

Sometimes you know better than the balancer. **Affinity** restricts which CPUs a thread may run on. The following output is illustrative for an eight-CPU Linux environment where CPUs 2 and 3 are allowed; identifiers and masks differ on other hosts.

```python
import os

print(os.sched_getaffinity(0))
# {0, 1, 2, 3, 4, 5, 6, 7}


# Replace this thread's allowed CPU mask.
os.sched_setaffinity(0, {2, 3})
print(os.sched_getaffinity(0))
# {2, 3}
```

From the shell: `taskset -c 2,3 ./server`, or `taskset -cp <pid>` to inspect. In C, `sched_setaffinity()` or `pthread_setaffinity_np()` per thread. Affinity is inherited across `fork()`.

Layers of control, from soft to hard:

- **Default (soft affinity)**: the scheduler prefers the last CPU but migrates freely.
- **`sched_setaffinity` / `taskset`**: a hard mask per thread.
- **cpuset cgroups** (`cpuset.cpus`, `cpuset.mems`): a mask for a whole group, which processes inside cannot widen. Kubernetes's static CPU manager can give eligible Guaranteed containers with integer CPU requests exclusive logical CPUs. Whole-core allocation additionally depends on policy options such as `full-pcpus-only`.
- **`isolcpus=` / `nohz_full=` boot options**: selected isolcpus modes can exclude CPUs from general domain balancing; nohz_full can suppress periodic ticks when its conditions are met. Neither option alone removes every interrupt, kernel task or housekeeping activity. Used for packet processing, HFT and real-time control.

When pinning helps:

- Latency-critical threads that must never share a core (with the rest of the system kept off those CPUs).
- Keeping a thread on the same NUMA node as its memory or NIC interrupts.
- Benchmarks, where migrations add noise.

When it hurts:

- Pinning everything to the same few CPUs while others idle; the balancer can't fix a mask you set.
- Pinning two hot threads to SMT siblings, so they compete for one core.
- Hard-coded CPU numbers that are wrong on the next machine, or inside a container that was given different CPUs.

## Key takeaways
- Scheduling domains represent hardware locality and guide balancing.
- The scheduler balances periodically, before idling and when placing waking tasks.
- Hard affinity and cpusets limit the balancer’s choices; validate CPU numbers and measure the result.

## Further reading
- [Multiprocessor Scheduling (Advanced) — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-multi.pdf)
- [Scheduler Domains — Linux kernel docs](https://docs.kernel.org/scheduler/sched-domains.html)
- [CFS Bandwidth Control — Linux kernel docs](https://docs.kernel.org/scheduler/sched-bwc.html)
- [Control Group v2 — Linux kernel docs](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [sched_setaffinity(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html)
- [numa(7) — Linux manual page](https://man7.org/linux/man-pages/man7/numa.7.html)
- [Non-uniform memory access — Wikipedia](https://en.wikipedia.org/wiki/Non-uniform_memory_access)
- [Go 1.25 release notes (container-aware GOMAXPROCS)](https://go.dev/doc/go1.25)
