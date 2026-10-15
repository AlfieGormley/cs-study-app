---
id: mem-leak-investigation
sourceLesson: mem-in-practice
title: Finding growth that is actually a leak
level: advanced
minutes: 4
summary: Growth can come from retained free memory, useful in-process caches or unreachable/native allocations.
---

## Finding leaks

A leak is memory that is allocated, never freed, and no longer useful. Persistent RSS/PSS growth can motivate investigation but neither proves a leak nor catches every leak. Before blaming a leak, rule out allocator retention (the allocator units) and in-process caches that are simply warming up.

| Tool | Scope | Requirement |
|---|---|---|
| Valgrind Memcheck | Native memory checks | Supported platform, instrumented execution |
| ASan + LSan | Native memory errors / unreachable allocations | Supported toolchain, build instrumentation |
| heaptrack / bcc memleak | Native allocation history / outstanding allocations | Compatible hooks and permissions |
| jemalloc profiling | Sampled allocator stacks | Profiling-enabled allocator configuration |
| tracemalloc | Traced Python allocations | Enable before allocations of interest |

> [!note] Measurement gap
> No representative overhead measurements accompany this lesson. Fixed slowdown factors and claims that a tool is automatically safe for production are omitted. Benchmark the selected configuration and sampling rate.

AddressSanitizer is compiled in (`-fsanitize=address`). On supported Linux toolchains with leak detection enabled, it integrates LeakSanitizer to report detected unreachable allocations at exit with their allocation stacks. Valgrind generally needs no rebuild for instrumentation, though debug information improves reports. bcc memleak can attach to supported allocation functions, recording outstanding allocations observed after attachment; it does not by itself determine reachability or reconstruct all earlier allocations.

In Python, `tracemalloc` compares snapshots and points at the line responsible:

```python
import tracemalloc

cache = []

def handle(req):
    # Reachable cache entries accumulate.
    cache.append(b"x" * 10_000)

tracemalloc.start()
before = tracemalloc.take_snapshot()
for i in range(1000):
    handle(i)
after = tracemalloc.take_snapshot()

# Compare net traced growth by source line.
top = after.compare_to(before, "lineno")
print(top[0])
# Output varies with Python and platform.
```

The payload size works out as:

```formula
D = 1,000 × 10,000 B = 10,000,000 B
D = (10,000,000 / 2^20) MiB ≈ 9.54 MiB
where
D: the total payload bytes appended to the in-process cache
B: bytes
MiB: mebibyte, 2^20 = 1,048,576 bytes
≈: approximately equal to
In words: a thousand 10,000-byte objects is 10 million bytes, about 9.54 MiB (9,765.625 KiB), plus object and list overhead.
```

Python reports in binary units, so expect about 9.5 MiB, not 10. Snapshot attribution and exact counts vary by Python version and allocator. In garbage-collected languages the usual "leak" is exactly this: a reachable collection, in-process cache or listener list that only ever grows.

## A debugging checklist

When a service's memory looks wrong:

1. **Which number?** VSZ, RSS, PSS or `memory.current`? Each answers a different question.
2. **Anon or file?** RssAnon includes anonymous mappings beyond the heap. RssFile and cgroup file counters cover different scopes; inspect dirty, writeback, shmem, reclaim and pressure before calling growth harmless.
3. **Killed by whom?** `dmesg` for the kernel OOM killer, `memory.events` for a cgroup limit, kubelet events for eviction, the systemd journal for systemd-oomd.
4. **Leak or retention?** Compare the allocator's statistics or a heap profile with RSS.
5. **Is the limit right?** Heap cap plus non-heap overhead plus headroom must fit under `memory.max`.

## Key takeaways
- Growth can come from retained free memory, useful in-process caches or unreachable/native allocations.
- Use a compatible profiler and compare its allocation view with resident and cgroup metrics.
- Snapshot attribution and tool overhead depend on the actual runtime and configuration.

## Further reading
- [Overcommit accounting — Linux kernel docs](https://www.kernel.org/doc/html/latest/mm/overcommit-accounting.html)
- [Control Group v2 (memory controller) — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [proc_pid_smaps(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc_pid_smaps.5.html)
- [Taming the OOM killer — LWN.net](https://lwn.net/Articles/317814/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Redis administration (overcommit advice) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/admin/)
- [AddressSanitizer — Clang docs](https://clang.llvm.org/docs/AddressSanitizer.html)
- [tracemalloc — Python docs](https://docs.python.org/3/library/tracemalloc.html)
