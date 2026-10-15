---
id: mem-oom-selection
sourceLesson: mem-in-practice
title: Which tasks an OOM policy can kill
level: advanced
minutes: 3
summary: Kernel OOM handling depends on allocation context and eligible victim scope.
---

## The OOM killer

Some allocation failures invoke the **OOM killer** after permitted reclaim paths are exhausted. Others return failure, retry or follow configured panic policy. The ordinary victim-selection path compares eligible tasks within the relevant scope and sends SIGKILL; special cases such as killing the allocating task or an existing exiting victim can change the code path.

The score (`oom_badness`) is roughly the process's memory footprint as a share of what is available: its **RSS, swap usage and page tables**. Then the admin's bias is added:

- `/proc/<pid>/oom_score_adj` ranges from **−1000 to +1000**. In the simplified score, each unit adds one-thousandth of the applicable memory allowance; scope can be system-wide, cpuset/NUMA constrained or cgroup limited. +500 adds half that allowance, not necessarily half physical RAM.
- **−1000** exempts a process entirely. Service policies can set negative values to influence relative selection; verify the actual unit and process settings.
- `/proc/<pid>/oom_score` shows a rescaled form of the current score, including the adjustment.

In simplified form, with memory measured as a share of the allowance in thousandths:

```formula
S ≈ 1000M / T + a
where
S: the badness score; the eligible process with the highest score is killed
≈: approximately equal to (the kernel works in pages and rounds)
M: the process's memory: resident pages (RSS) plus swap entries plus page-table pages
T: the memory allowance for the scope: RAM plus swap system-wide, or the limit of the cgroup or cpuset
a: oom_score_adj, from −1000 to +1000 (−1000 instead exempts the process entirely)
In words: a process's share of the allowance, scaled to 0–1000, plus the admin's adjustment; +500 is worth half of the allowance.
```

For example, with a 16 GiB allowance, the simplified score is about 375 for a 6 GiB process with no adjustment, versus about 625 for a 2 GiB process with adjustment +500. If both are eligible and no exceptional path intervenes, the second is preferred as victim.

The kill leaves a trail in the kernel log:

Illustrative command/output sample; actual values depend on the workload, system and observation interval:

```
$ dmesg | grep -i oom
Out of memory: Killed process 4121
(java) total-vm:9123456kB,
anon-rss:7340032kB, file-rss:0kB,
oom_score_adj:0
```

Badness is not simply largest RSS: swap, page tables, adjustments and which tasks are eligible all matter. User-space tools can act on pressure before kernel OOM. **systemd-oomd** can target cgroups using configured pressure policy; **earlyoom** normally selects processes using available-memory/swap thresholds and process scores. Neither guarantees an earlier kill in every workload.

## Key takeaways
- Kernel OOM handling depends on allocation context and eligible victim scope.
- Resident, swapped and page-table usage combine with administrator adjustments.
- Pressure-based user-space killers are distinct policies.

## Further reading
- [Overcommit accounting — Linux kernel docs](https://www.kernel.org/doc/html/latest/mm/overcommit-accounting.html)
- [Control Group v2 (memory controller) — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [proc_pid_smaps(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc_pid_smaps.5.html)
- [Taming the OOM killer — LWN.net](https://lwn.net/Articles/317814/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Redis administration (overcommit advice) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/admin/)
- [AddressSanitizer — Clang docs](https://clang.llvm.org/docs/AddressSanitizer.html)
- [tracemalloc — Python docs](https://docs.python.org/3/library/tracemalloc.html)
