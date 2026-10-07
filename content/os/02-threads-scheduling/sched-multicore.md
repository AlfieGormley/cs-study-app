---
id: sched-multicore
title: Multicore scheduling, affinity, NUMA and containers
level: advanced
minutes: 15
summary: Scheduling across many CPUs - per-CPU run queues, load balancing and cache affinity, pinning with sched_setaffinity and cpusets, NUMA locality, and why CPU limits in containers cause throttling and tail latency.
---

Everything so far assumed one CPU. Servers may expose many logical CPUs, arranged in hardware-dependent hierarchies of SMT threads, cores, caches and memory nodes. The scheduler now answers two questions: *which* thread runs next, and *where*. Getting "where" wrong costs cache misses, remote memory accesses, and, inside containers, whole periods of enforced idleness.

## The hardware the scheduler sees

```
Socket / NUMA node 0        node 1
+-----------------------+   +-------
| L3 (shared)           |   | L3 ...
| core0     core1  ...  |   |
| [t0 t1]   [t2 t3]     |   |
| L1/L2     L1/L2       |   |
+--------local DRAM-----+   +-------
```

- **SMT siblings** (hyper-threads) share one core's execution units and L1/L2 caches. Resource contention can make two busy siblings slower than using separate physical cores; the effect depends on the workloads.
- **Cores in one socket** (or one chiplet) share a last-level cache (L3).
- **NUMA nodes** each have their own memory. Reaching another node's memory goes over an interconnect and is slower.

A thread that has been running on a CPU has a **warm cache** there: its working set is in L1, L2 and L3. Move it, and it pays to reload that state. This is **cache affinity**, and it is the central tension of multicore scheduling: keep threads where their data is, but don't leave CPUs idle while work waits elsewhere.

## One queue or many?

OSTEP frames the two basic designs:

| Design | Pros | Cons |
|---|---|---|
| Single shared queue | Simple, balanced by construction | Lock contention, poor affinity |
| Per-CPU queues | Scalable, natural affinity | Load imbalance |

In a simple global-queue design, scheduling decisions contend for one lock and may move tasks between CPUs. The scaling limit and cache cost depend on implementation and workload; a global queue can also incorporate affinity heuristics.

With **per-CPU run queues**, each CPU schedules from its own queue with no shared lock, and threads tend to stay put. The cost is **imbalance**: CPU 0 might have four runnable threads while CPU 1 is idle. The fix is **migration**, moving threads between queues, typically by **work stealing**: an idle or lightly loaded CPU pulls work from a busier one.

Linux has used per-CPU run queues since the O(1) scheduler in 2.6.0. Go's runtime, Java's ForkJoinPool and Tokio use the same per-worker-queue-plus-stealing idea in user space.

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

Sometimes you know better than the balancer. **Affinity** restricts which CPUs a thread may run on.

```python
import os

print(os.sched_getaffinity(0))
# {0, 1, 2, 3, 4, 5, 6, 7}

os.sched_setaffinity(0, {2, 3})
print(os.sched_getaffinity(0))
# {2, 3}
```

From the shell: `taskset -c 2,3 ./server`, or `taskset -cp <pid>` to inspect. In C, `sched_setaffinity()` or `pthread_setaffinity_np()` per thread. Affinity is inherited across `fork()`.

Layers of control, from soft to hard:

- **Default (soft affinity)**: the scheduler prefers the last CPU but migrates freely.
- **`sched_setaffinity` / `taskset`**: a hard mask per thread.
- **cpuset cgroups** (`cpuset.cpus`, `cpuset.mems`): a mask for a whole group, which processes inside cannot widen. Kubernetes's static CPU manager can give eligible Guaranteed containers with integer CPU requests exclusive logical CPUs. Whole-core allocation additionally depends on policy options such as `full-pcpus-only`.
- **`isolcpus=` / `nohz_full=` boot options**: remove CPUs from general balancing and, with `nohz_full`, stop the scheduler tick when one task runs there. Used for packet processing, HFT and real-time control.

When pinning helps:

- Latency-critical threads that must never share a core (with the rest of the system kept off those CPUs).
- Keeping a thread on the same NUMA node as its memory or NIC interrupts.
- Benchmarks, where migrations add noise.

When it hurts:

- Pinning everything to the same few CPUs while others idle; the balancer can't fix a mask you set.
- Pinning two hot threads to SMT siblings, so they compete for one core.
- Hard-coded CPU numbers that are wrong on the next machine, or inside a container that was given different CPUs.

## NUMA: memory has an address *and* a location

On a multi-socket server, each node's memory is local to its cores. Remote access cost and interconnect bandwidth depend on the machine and workload.

> [!note] Content gap
> No reproducible machine-specific NUMA measurements accompany this lesson, so no universal remote/local latency multiplier is provided. `numactl --hardware` shows the nodes and a distance table (10 means local; remote nodes are larger, commonly around 20).

Linux normally prefers local allocation. For new private anonymous memory, the first write fault commonly allocates a page near the executing CPU. Explicit policies, cpusets, fallback under memory pressure, huge pages and later migration can change placement. That causes a classic bug:

> [!example] The single-threaded initialiser
> A program allocates and zeroes a 64 GiB array in its main thread on node 0, then starts 32 worker threads spread across both nodes. Assume the main thread stays on node 0, local memory is sufficient, writes fault in new pages and no policy or migration changes placement. The pages then start on node 0. Half the workers make every access remotely, and node 0's memory bandwidth is shared by everyone. Fix: initialise each slice from the thread that will use it, or interleave.

Tools and policies:

- `numactl --cpunodebind=0 --membind=0 ./db` runs a process on node 0's CPUs with node 0's memory.
- `numactl --interleave=all` spreads pages round robin across nodes: distributed allocation rather than guaranteed per-thread locality. It can reduce concentration on one node, but does not guarantee removal of all hot spots. Often a good choice for large shared caches, such as a database buffer pool.
- **Automatic NUMA balancing** (since Linux 3.8, `kernel.numa_balancing`): the kernel periodically unmaps pages to sample which node touches them through "hinting faults", then migrates pages towards their users, or tasks towards their memory. It helps long-running, well-partitioned workloads, at the cost of some overhead.
- `numastat -p <pid>` shows where a process's memory actually lives.

The scheduler is NUMA-aware: its top-level domain balances reluctantly across nodes, because moving a thread can turn accesses to its existing memory into remote accesses; cache hits and pages already elsewhere are exceptions.

## Containers: shares versus quotas

Containers use cgroups to control CPU in two very different ways.

| Control | cgroup v2 file | Behaviour |
|---|---|---|
| Weight | `cpu.weight` | Share *under contention* |
| Quota | `cpu.max` | Hard cap, even when idle CPUs exist |

**Weight** (default 100) is proportional sharing between groups, just like nice between threads. If the machine is otherwise idle, a low-weight container can still use every CPU. It's *work-conserving*.

**Quota** is CFS bandwidth control. `cpu.max` holds "quota period" in microseconds; `200000 100000` means 200 ms of CPU time per 100 ms period, i.e. 2 CPUs' worth. Fair-class CPU time is charged across the group. Exhausted local bandwidth allocations cause throttling even with idle CPUs. Ancestor quotas, per-CPU runtime accounting and configured burst credit also affect the exact timeline.

In Kubernetes, a pod's CPU **request** becomes its cgroup weight, and its CPU **limit** becomes its `cpu.max` quota (with the default 100 ms period).

### How throttling wrecks tail latency

> [!example] Two CPUs of quota, eight busy threads
> A container has `cpu.max = 200000 100000` and a server with 8 worker threads, on a 32-core host. In an idealized model, all 8 run simultaneously from the period boundary, with no other contention, overhead, burst credit or carried local runtime.
> - The group consumes 8 CPU-ms per ms of wall time.
> - 200 ms of quota lasts 200 / 8 = **25 ms**.
> - For the remaining **75 ms** of the period, nothing in the container runs.
>
> A request arriving at t = 26 ms waits at least 74 ms for replenishment in this model. If it then immediately receives a CPU for 5 ms, its latency is 79 ms; queueing behind existing work can add more. Average usage is "2 CPUs, within limit", so dashboards look fine.

The symptom is p99 latency far above p50 while CPU usage looks modest. Check `cpu.stat`:

```
nr_periods 36000
nr_throttled 9100
throttled_usec 412000000
```

Here a quarter of periods were throttled. Ways out:

- **Size thread pools to the quota, not the host.** Eight threads chewing through two CPUs' quota in a quarter of the period is worse than two threads using it smoothly.
- **Remove CPU limits** for latency-sensitive services and rely on requests (weights) for fairness. The trade-off is weaker isolation from competing workloads; inherited parent quotas can still throttle the group.
- **Allow bursting**: `cpu.max.burst` (Linux 5.14+) lets a group bank unused quota for short spikes.
- **Use exclusive CPUs** (eligible Guaranteed containers under Kubernetes static CPU management; whole cores require appropriate policy options) when you need both isolation and predictability.

### Runtimes that count the wrong CPUs

Many runtimes size their worker pools from the CPU count, and the CPU count visible inside a container is usually the **host's**:

- Python's `os.cpu_count()` returns the host's logical CPUs. `os.process_cpu_count()` (3.13+) respects the affinity mask, but **not** a `cpu.max` quota.
- Go 1.25 introduced container-aware defaults: logical CPUs, affinity and cgroup CPU bandwidth all participate. Fractional quotas are rounded up, and the default generally stays at least 2 unless CPU count or affinity is lower. Explicit settings and compatibility controls can override this.
- The JVM has been container-aware since JDK 10 (backported to 8u191).

For example, 64 visible logical CPUs, no narrower affinity and no Python CPU-count override can yield a default maximum of 64 processes despite a two-CPU quota. Workers start as jobs are submitted, with behavior depending on Python version and start method. A simple cgroup-v2 quota reader is:

```python
PATH = "/sys/fs/cgroup/cpu.max"

def cpu_quota():
    try:
        with open(PATH) as f:
            quota, period = f.read().split()
    except FileNotFoundError:
        return None  # not cgroup v2
    if quota == "max":
        return None  # no limit
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
- Linux uses per-CPU run queues for scalability and cache affinity, and fixes imbalance by migrating tasks: periodically, when a CPU goes idle, and at wake-up.
- Scheduling domains mirror the hardware (SMT, shared cache, NUMA); balancing is eager where migration is cheap and reluctant across NUMA nodes.
- Affinity (`sched_setaffinity`, `taskset`, cpusets, `isolcpus`) trades the balancer's flexibility for predictability; measure before pinning.
- On NUMA machines, remote memory is slower; first-touch allocation, `numactl` and automatic NUMA balancing decide where pages live.
- `cpu.weight` shares CPU only under contention; `cpu.max` is a hard per-period quota across all threads, and exhausting it early in a period throttles the whole container, hurting tail latency.

## Further reading
- [Multiprocessor Scheduling (Advanced) — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-multi.pdf)
- [Scheduler Domains — Linux kernel docs](https://docs.kernel.org/scheduler/sched-domains.html)
- [CFS Bandwidth Control — Linux kernel docs](https://docs.kernel.org/scheduler/sched-bwc.html)
- [Control Group v2 — Linux kernel docs](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [sched_setaffinity(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html)
- [numa(7) — Linux manual page](https://man7.org/linux/man-pages/man7/numa.7.html)
- [Non-uniform memory access — Wikipedia](https://en.wikipedia.org/wiki/Non-uniform_memory_access)
- [Go 1.25 release notes (container-aware GOMAXPROCS)](https://go.dev/doc/go1.25)
