---
id: mem-cgroup-memory
sourceLesson: mem-in-practice
title: Memory charges, limits and reclaim
level: advanced
minutes: 2
summary: Cgroup memory accounting includes file cache and many kernel allocations.
---

## cgroup v2 memory limits

Containers do not get their own kernel or their own OOM killer; they get a **cgroup**. The memory controller accounts for anonymous memory, file cache and many kernel allocations. Shared pages normally have one owning cgroup charge rather than a full charge to every accessor; accounting scope and special memory types have exceptions.

The main files in `/sys/fs/cgroup/<group>/`:

| File | Purpose |
|---|---|
| `memory.current` | Usage now, cache included |
| `memory.max` | Hard limit |
| `memory.high` | Throttle point |
| `memory.min` / `.low` | Protection from reclaim |
| `memory.events` | Counts of high, max, oom_kill |

What happens as usage rises:

1. Past **memory.high**: the group's tasks are made to reclaim their own memory and are slowed down. Crossing high does not itself invoke the kernel OOM killer. Independent global/ancestor pressure or a user-space OOM policy can still kill tasks.
2. At **memory.max**: charged allocations may trigger reclaim within the constrained subtree. If the limit cannot be met, eligible allocation paths can invoke cgroup OOM; some allocations instead fail. Victims stay within the constrained subtree. `memory.oom.group` requests group killing, with exceptions including tasks protected by oom_score_adj=-1000.

So a container can be OOM-killed while the host has plenty of free RAM. `memory.events` will show `oom_kill` incrementing, and `memory.stat` breaks usage into anon, file, kernel and more.

> [!warning] Page cache counts
> A container reading a large file can accumulate a page-cache charge, depending on ownership, readahead and reclaim. Clean cache that is not pinned in place is reclaimable, but the file counter alone does not prove that usage is safe or all reclaim can succeed. But dirty pages and tmpfs (`/dev/shm`, `emptyDir` with `medium: Memory`) cannot simply be dropped, and tmpfs counts against the limit like anonymous memory.

## Key takeaways
- Cgroup memory accounting includes file cache and many kernel allocations.
- High throttles through reclaim; max can force constrained reclaim, failures or cgroup OOM.
- Dirty cache and tmpfs need backing rather than being safely dropped as clean cache.

## Further reading
- [Overcommit accounting — Linux kernel docs](https://www.kernel.org/doc/html/latest/mm/overcommit-accounting.html)
- [Control Group v2 (memory controller) — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [proc_pid_smaps(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc_pid_smaps.5.html)
- [Taming the OOM killer — LWN.net](https://lwn.net/Articles/317814/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Redis administration (overcommit advice) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/admin/)
- [AddressSanitizer — Clang docs](https://clang.llvm.org/docs/AddressSanitizer.html)
- [tracemalloc — Python docs](https://docs.python.org/3/library/tracemalloc.html)
