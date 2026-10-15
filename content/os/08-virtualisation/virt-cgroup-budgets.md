---
id: virt-cgroup-budgets
title: Cgroup v2 budgets, accounting and throttling
level: intermediate
minutes: 5
sourceLesson: virt-container-primitives
summary: CPU quota is aggregate CPU time per period; parallel threads can consume it quickly.
---

This unit focuses on cgroup v2 budgets, accounting and throttling. It builds on the earlier virtualisation units in this module.

## cgroups v2: limiting and accounting

**Control groups** organise processes into a tree and attach resource controllers to each node. Cgroups v2 uses a unified hierarchy, commonly mounted at `/sys/fs/cgroup`. Inspect the actual host: available/enabled controllers and boot configuration vary.

A simplified administrator example on a disposable, correctly delegated cgroup v2 hierarchy follows. It assumes the controllers are available, permissions allow these writes, and a service manager is not managing the same subtree. Commands must succeed before continuing; do not treat this as a universal host setup script.

```
$ cd /sys/fs/cgroup
$ echo +cpu +memory +pids \
    > cgroup.subtree_control
$ mkdir demo
$ echo "50000 100000" > demo/cpu.max
$ echo 256M > demo/memory.max
$ echo 100 > demo/pids.max
$ echo $$ > demo/cgroup.procs
```

After successful writes, the shell and later children share a fair-scheduler CPU quota averaging half a CPU, a 256 MiB accounted-memory limit and a 100-task limit (threads count). Ancestor limits also apply; pre-existing children are not automatically moved with the shell.

| File | Meaning |
|---|---|
| `cpu.max` | Quota and period in µs; `max 100000` means no limit |
| `cpu.weight` | Relative share under CPU contention, 1–10000, default 100 |
| `memory.max` | Accounted-memory limit; reclaim/OOM handling |
| `memory.high` | Throttling/reclaim threshold; may be exceeded |
| `pids.max` | Maximum tasks; stops fork bombs |
| `io.max` | Per-device bandwidth or IOPS limits |

A few mechanics are worth knowing precisely.

**CPU quota is enforced per period.** The two numbers in `cpu.max` are a quota and a period. The quota is CPU time summed *across all threads* in the group, so the average CPU share it allows, and how quickly parallel threads burn through it, follow directly:

```formula
f_CPU = Q / P
t_wall = Q / N
where
f_CPU: the long-run share of CPU the group may use, in CPUs (0.5 means half of one CPU, 2 means two whole CPUs)
Q: the quota, the first number in cpu.max: CPU time the whole group may use in each period, in microseconds (µs)
P: the period, the second number in cpu.max, in µs; 100000 µs = 100 ms is the usual default
t_wall: the wall-clock time from the start of a period until the quota runs out, in the same unit as Q
N: the number of the group's threads running at the same time, each on its own CPU
In words: the quota divided by the period is the average number of CPUs the group may use; N threads running in parallel use the quota up N times faster, and then the whole group waits for the next period.
```

For `50000 100000`, in an idealised case with four threads running continuously on four available CPUs, no burst credit and no tighter ancestor limit:

```formula
f_CPU = 50000 µs / 100000 µs = 0.5
t_wall = 50 ms / 4 = 12.5 ms
where
f_CPU: the average CPU share allowed, in CPUs
t_wall: wall-clock time until the quota is used up
µs: microsecond, one millionth of a second
ms: millisecond, one thousandth of a second; 50000 µs = 50 ms
In words: half a CPU on average, but four busy threads spend the whole 50 ms budget in the first 12.5 ms of each 100 ms period.
```

The group is then throttled for the remaining 87.5 ms of the period. The model assumes the busy-thread count is no more than the number of available CPUs, and it only predicts throttling when quota exhaustion comes before the next period; with fewer busy threads the quota may last the whole period. Scheduler accounting and runtime slices make actual traces less exact. The later unit on Kubernetes CPU limits shows why this hurts latency.

Three more mechanics:

- **`cpu.weight` only matters under CPU contention.** A sufficiently parallel group may use otherwise-idle allowed CPUs, subject to quota, affinity, cpuset and ancestor restrictions.
- **Memory limits count page cache too.** A process that reads large files fills its cgroup's page cache; reclaimable cache can reduce pressure, but unevictable/dirty data and other charges matter. memory.max can be exceeded temporarily, and some allocation failures do not invoke the OOM killer. A container can look "full" when much usage is reclaimable cache. `memory.stat` shows the breakdown, and `memory.events` counts `oom_kill`s.
- **The "no internal processes" rule.** For domain resource distribution, a non-root cgroup must have no internal processes before enabling domain controllers for children. The root and threaded-controller subtrees have exceptions; "processes only in leaves" is not a universal rule.

cgroups v1, still found on older hosts, had a separate tree per controller (`/sys/fs/cgroup/memory/...`, `/sys/fs/cgroup/cpu/...`), which made consistent limits awkward. Its CPU knob was CPU shares (the `cpu.shares` file, default 1024) rather than `cpu.weight`.

## Key takeaways

- CPU quota is aggregate CPU time per period; parallel threads can consume it quickly.
- Weights divide contended service, while memory charges include cache and other accounted allocations.

## Further reading

- [namespaces(7) — Linux manual page](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Control Group v2 — Linux kernel documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [pivot_root(2) — Linux manual page](https://man7.org/linux/man-pages/man2/pivot_root.2.html)
- [Overlay Filesystem — Linux kernel documentation](https://docs.kernel.org/filesystems/overlayfs.html)
- [pid_namespaces(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html)
