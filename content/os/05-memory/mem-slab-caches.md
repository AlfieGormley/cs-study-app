---
id: mem-slab-caches
sourceLesson: mem-allocators
title: Kernel object caches and allocator pitfalls
level: advanced
minutes: 4
summary: A slab divides backing pages into fixed-size object slots, with real metadata and alignment overhead.
---

## The kernel: slab allocation

The kernel allocates millions of small, same-sized objects: inodes, dentries, socket buffers, task structs. Asking the buddy allocator for a page each time would waste most of it.

The **slab allocator** (Jeff Bonwick, Solaris, 1994) keeps a **cache** per object type. Each cache owns **slabs**, one or more contiguous pages divided into equal-sized slots:

```
illustrative cache (192 B slots)
 slab (one 4 KiB page): 21 slots
 [obj][obj][free][obj][free]...
```

The slot count is the slab size divided by the object size, rounded down, because an object cannot hang off the end of the slab:

```formula
N = ⌊S_slab / s⌋
W = S_slab − Ns
N = ⌊4,096 B / 192 B⌋ = 21
W = 4,096 B − 21 × 192 B = 64 B
where
N: the number of objects that fit in one slab
S_slab: the slab size in bytes; one 4 KiB page here
s: the slot size per object in bytes; 192 here
⌊ ⌋: floor: round down to a whole number
W: the leftover bytes at the end of the slab
B: bytes
In words: fit as many whole slots as possible and the remainder is wasted; here 21 slots use 4,032 bytes and 64 are left over.
```

This simplified model ignores slab metadata and alignment padding, which the real allocator adds.

The simple fast path takes or returns a slot. Fixed-size caches do not need a malloc-style size header on every live object, but maintain slab/free-list metadata; debugging, alignment and hardening can add per-object overhead. Refill and partial-slab selection require additional work. Generic `kmalloc` is built from caches of fixed sizes (8, 16, 32, 64, 96, 128, 192, 256 bytes and so on).

Linux has had three implementations. **SLUB** is the default and, since SLOB was removed in 6.4 and SLAB in 6.8, the only one. It uses per-CPU state and partial-slab management; synchronization and the exact fast path depend on architecture, configuration and kernel version.

Inspect it with `slabtop` or `/proc/slabinfo`. A kernel memory leak, or a workload that creates millions of dentries, shows up here rather than in any process's RSS.

User-space allocators use related grouping ideas, with different metadata, caching and memory-return policies.

## Pitfalls

- **Benchmarks need representative workloads.** A microbenchmark that allocates and frees one size in a loop can mostly hit a cached fast path. Mixed lifetimes and sizes can expose retention or fragmentation on a different timescale.
- **Cross-thread frees.** A producer thread allocates, a consumer frees. Thread caches fill on one side and drain on the other, and remote frees affect reuse. A glibc chunk can enter another thread's tcache without changing its owning arena. Performance depends on the allocator and workload.
- **Mixing allocators.** Memory from one allocator must be freed by the same one. Passing a jemalloc-owned allocation to an incompatible glibc `free` is undefined behavior and can corrupt memory or crash.
- **Don't assume RSS falls after free.** Use the allocator's own statistics (`malloc_stats()`, `mallctl` in jemalloc) to see free-but-retained memory.

## Key takeaways
- A slab divides backing pages into fixed-size object slots, with real metadata and alignment overhead.
- SLUB supplies kernel caches; per-process RSS does not include all kernel objects.
- Measure retention and cross-thread behaviour, and keep allocation/deallocation APIs compatible.

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
