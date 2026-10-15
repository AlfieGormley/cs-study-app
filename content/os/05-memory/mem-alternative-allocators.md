---
id: mem-alternative-allocators
sourceLesson: mem-allocators
title: Size classes and scalable allocator designs
level: advanced
minutes: 4
summary: Allocator designs differ in caches, object grouping and memory-return policy.
---

## jemalloc, tcmalloc and mimalloc

Several allocators were written to scale better than ptmalloc and fragment less over long runs.

**jemalloc**:

- Fine-grained **size classes**: 16-byte steps for small sizes, then four classes per doubling (160, 192, 224, 256, 320...). For these classes (excluding the smallest sizes), rounding waste is bounded at about 20% of the slot (worked out below).
- Objects of one class live together in **slabs** (runs of pages), so no per-object header is needed.
- Per-thread caches in front of multiple **arenas**; the documented automatic arena limit defaults to four times CPUs, or one for a single CPU. Assignment is not a promised round-robin API contract.
- Unused pages are returned to the OS gradually on a **time-based decay** schedule, using `madvise`, rather than all at once.
- Rich built-in statistics and heap profiling, useful for finding leaks in production.

Where does the 20% bound come from? The rounding waste is the unused part of the slot. The worst case is a request one byte above a power-of-two class, because the next class is then only 1.25 times as big:

```formula
w = (S − n) / S
w_max ≈ (1.25c − c) / (1.25c)
w_max = 0.25 / 1.25 = 0.2 = 20 %
where
w: the rounding waste, as a fraction of the slot
S: the slot size: the size class the request is rounded up to
n: the requested size in bytes
w_max: the largest possible waste with four classes per doubling
c: a power-of-two size class such as 256; the next class is 1.25c (320)
≈: approximately equal to (the request is c + 1 bytes, so the true waste is a hair under 20 %)
%: per cent
In words: with four classes per doubling, the gap above a power of two is a quarter of it, which is at most a fifth of the slot.
```

For example, a 257-byte object goes in a 320-byte slot: 63 bytes, or about 19.7% of the slot, are wasted.

**tcmalloc** (Google): a front end supporting **per-CPU** caches or legacy per-thread mode. The per-CPU mode uses Linux restartable sequences so its local cache operations need no locks or atomic instructions. It has a middle tier of transfer caches and central free lists, and a page heap. Its newer page heap is **huge-page aware**, packing allocations into huge-page regions (2 MiB in the usual x86-64 example) to improve TLB use.

**mimalloc** (Microsoft Research): **free-list sharding**, with many small free lists per page rather than one big one, which keeps related objects close together and makes the fast path a few instructions.

| | glibc | jemalloc | tcmalloc |
|---|---|---|---|
| Fast path | per-thread tcache | per-thread cache | per-CPU or per-thread |
| Small objects | headers on chunks | headerless slabs | headerless spans |
| Return to OS | trim top, mmap free | decay over time | background release |

For a compatible dynamically linked program, an installed allocator can sometimes be interposed with `LD_PRELOAD=/actual/path/libjemalloc.so ./server`. The library's file location, ABI and allocation/deallocation boundaries must match. Static linking and some runtime/build choices require another integration method.

> [!note] Performance evidence gap
> No benchmark record accompanies this lesson, so comparative RSS, latency and cross-thread-free rankings are omitted. Measure representative workloads, retention and contention before selecting an allocator.

> [!note] Python has its own layer
> In a standard GIL-enabled build using **pymalloc**, small allocations of up to 512 bytes use pools in larger arenas, with larger requests falling back to raw allocation. Build/runtime settings matter: free-threaded CPython uses mimalloc. C extensions can also allocate directly, so not every Python object allocation follows pymalloc.

## Key takeaways
- Allocator designs differ in caches, object grouping and memory-return policy.
- Class rounding can be bounded separately from total allocator overhead.
- Compare representative lifetime and concurrency patterns before switching allocators.

## Further reading
- [MallocInternals — glibc wiki](https://sourceware.org/glibc/wiki/MallocInternals)
- [mallopt(3) — Linux manual page](https://man7.org/linux/man-pages/man3/mallopt.3.html)
- [OSTEP: Free-Space Management (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-freespace.pdf)
- [jemalloc](https://jemalloc.net/)
- [TCMalloc design](https://google.github.io/tcmalloc/design.html)
- [mimalloc on GitHub](https://github.com/microsoft/mimalloc)
- [Buddy memory allocation — Wikipedia](https://en.wikipedia.org/wiki/Buddy_memory_allocation)
- [Slab allocation — Wikipedia](https://en.wikipedia.org/wiki/Slab_allocation)
- [Physical Page Allocation, from Understanding the Linux Virtual Memory Manager](https://www.kernel.org/doc/gorman/html/understand/understand009.html)
