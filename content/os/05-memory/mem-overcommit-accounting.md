---
id: mem-overcommit-accounting
sourceLesson: mem-in-practice
title: Memory promises and strict commit limits
level: advanced
minutes: 5
summary: Successful reservation does not ensure every later write can obtain backing.
---

The earlier lessons built the machinery. This one is about living with it on real servers: reading memory numbers correctly, understanding why a process was killed, and setting limits that hold.

Three facts drive most production surprises:

1. Linux can permit commitments beyond available physical backing (**overcommit**), according to policy.
2. Severe allocation pressure can cause reclaim, allocation failure or an **OOM kill**, depending on context and policy.
3. Every common memory metric measures something slightly different from what people assume.

## Overcommit and delayed failure

A successful `malloc` or `mmap` need not make every requested byte resident. Existing allocator pages, metadata and population flags can already consume memory; new anonymous backing is often supplied on first touch. So the kernel faces a choice at allocation time: should it promise memory it does not yet have?

The policy is `vm.overcommit_memory`:

| Mode | Behaviour |
|---|---|
| 0 (default) | Heuristic: refuse only obviously impossible requests |
| 1 | Skip the overcommit admission check; other limits and allocation failures still apply |
| 2 | Strict: refuse beyond a commit limit |

Mode 0 applies a heuristic, not a guarantee that each request below RAM succeeds. Resource limits, address-space availability, mapping limits, metadata allocation and current memory conditions can still reject requests.

> [!example] Promises versus reality
> A box has 16 GiB of RAM and no swap. A program calls `malloc(8 GiB)` ten times. Assume all ten allocations succeed under the current limits and heuristic. They request 80 GiB, far more than the available backing.
>
> Nothing goes wrong until the program writes to the memory. If those pages must remain backed and reclaim cannot satisfy demand, allocation can fail or trigger OOM handling before the requested 80 GiB is populated. Other users of memory and policy determine when and what happens.

Why would anyone want this? Because most programs reserve far more than they use: large mostly unused thread-stack reservations and mostly untouched, sparse arrays, JVM heaps reserved up front, and above all `fork`. An ordinary fork can share private writable data through copy-on-write. Strict accounting reserves for eligible writable private mappings that the child could copy; it does not simply duplicate VSZ or RSS, and special mappings have exceptions. Overcommit lets that `fork` succeed.

### Strict mode

In mode 2 the kernel tracks **Committed_AS** (total promised) and refuses allocations that would push it over **CommitLimit**. The limit counts all of swap but only a percentage of RAM:

```formula
CommitLimit = S_swap + (Rr) / 100
Committed_AS + A ≤ CommitLimit
where
CommitLimit: the most memory the kernel will promise in strict mode, shown in /proc/meminfo
S_swap: the total swap space
R: the usable RAM: physical RAM minus pages reserved for HugeTLB
r: vm.overcommit_ratio, the percentage of RAM that counts; 50 by default
Committed_AS: the memory already promised to all processes, also shown in /proc/meminfo
A: the size of the new commitment being requested
≤: less than or equal to; a request that would break this fails with ENOMEM
In words: strict mode adds all of swap to a fixed percentage of RAM, and refuses any allocation that would take the total promised past that limit.
```

A nonzero `vm.overcommit_kbytes` supplies an absolute RAM contribution instead of the ratio. Per-user/admin reserves can further restrict admission.

> [!example] Calculating the limit
> 64 GiB of RAM, 8 GiB of swap, ratio 50, no HugeTLB reservation and overcommit_kbytes zero.

```formula
CommitLimit = 8 GiB + 64 GiB × 50 / 100
CommitLimit = 8 GiB + 32 GiB = 40 GiB
where
CommitLimit: the strict-mode commit limit
GiB: gibibyte, 2^30 bytes
In words: all 8 GiB of swap plus half of the 64 GiB of RAM gives a 40 GiB limit.
```

Even with 30 GiB of RAM physically free, an allocation that pushes the committed total past 40 GiB fails with `ENOMEM`.

Both numbers are visible in `/proc/meminfo`. Strict admission can make insufficient commitment visible as an allocation error, but does not rule out cgroup OOM or every later failure. RAM outside the commit limit is not necessarily wasted: file-backed cache and kernel users can use it. Large forks can fail admission. Redis recommends mode 1 to avoid this particular overcommit rejection; fork can still fail for other reasons and COW still needs real headroom.

## Key takeaways
- Successful reservation does not ensure every later write can obtain backing.
- Strict overcommit combines swap with a ratio or absolute RAM budget and admission reserves.
- Fork commitments can fail even while some RAM is physically free.

## Further reading
- [Overcommit accounting — Linux kernel docs](https://www.kernel.org/doc/html/latest/mm/overcommit-accounting.html)
- [Control Group v2 (memory controller) — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [proc_pid_smaps(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc_pid_smaps.5.html)
- [Taming the OOM killer — LWN.net](https://lwn.net/Articles/317814/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Redis administration (overcommit advice) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/admin/)
- [AddressSanitizer — Clang docs](https://clang.llvm.org/docs/AddressSanitizer.html)
- [tracemalloc — Python docs](https://docs.python.org/3/library/tracemalloc.html)
