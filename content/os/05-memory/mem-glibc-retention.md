---
id: mem-glibc-retention
sourceLesson: mem-allocators
title: Thread caches, arenas and retained RSS
level: advanced
minutes: 3
summary: Thread caches and bins reuse chunks; arenas trade lock contention for retained address space.
---

### Bins and the tcache

The glibc 2.39 allocation machinery includes these structures; this is an overview, not a complete fixed search order:

1. **tcache** (since glibc 2.26): a per-thread cache of 64 small size classes, holding up to 7 chunks each by default. No locking at all: the fast path for most `malloc`/`free` pairs.
2. **fastbins**: singly linked lists for small chunks, not coalesced, so reuse is quick.
3. An **unsorted bin** stages many newly freed/coalesced chunks. **Small bins** hold exact size classes; **large bins** are size ordered. Eligible neighboring free chunks can coalesce; tcache and fastbin retention delay that.
4. The **top chunk** is an arena's remaining heap space. The main arena commonly grows using `brk`; non-main heaps use mappings.

### Big allocations use mmap

In the stated release, requests that cannot be satisfied from existing arena space may be served by a dedicated mapping when their normalized size meets the mmap threshold and mapping limits permit it. The default threshold starts at 128 KiB and can dynamically rise to 32 MiB on this model. This is not an unconditional bypass: suitable existing free chunks, settings, mapping limits and failures matter. Dedicated mapped chunks are normally unmapped on free; fault and TLB-invalidation costs depend on actual mappings and use.

### Arenas

One heap with one lock would serialise every thread. glibc assigns threads to **arenas**, which can be shared (the default cap in this release/model is 8 × online CPUs). A non-main arena can acquire multiple heaps, whose maximum reservation is commonly 64 MiB in this configuration, which is why a busy Java or Ruby process can show a huge VSZ made of many 64 MiB regions. Reducing `MALLOC_ARENA_MAX` can reduce retention but increase contention; choose a limit by measuring the application.

### Why free() doesn't shrink RSS

```
heap:  [A][B][C][D][E]...[Z][top]
free everything except Z:
       [   free space    ][Z][top]
```

`brk` can only move the end of the heap. If one live object sits near the top, the free space below it cannot be given back by shrinking the heap. glibc trims the top when it exceeds `M_TRIM_THRESHOLD` (128 KiB by default), and `malloc_trim(0)` can release whole free pages in the middle with `madvise(MADV_DONTNEED)`, but small long-lived objects scattered across many pages keep those pages resident.

So a service that allocates a flood of temporary objects, then frees most of them, often keeps its peak RSS. Allocator retention can explain this without a leak, but RSS alone cannot distinguish retention from leaked or unprofiled live allocations.

## Key takeaways
- Thread caches and bins reuse chunks; arenas trade lock contention for retained address space.
- Dedicated mappings depend on allocator state, thresholds and limits.
- Freeing objects need not release the pages that contain surviving objects.

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
