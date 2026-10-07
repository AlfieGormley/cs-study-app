---
id: mem-allocators
title: Memory allocators, from malloc to slab
level: advanced
minutes: 16
summary: How user-space malloc carves pages into objects (glibc's chunks, bins, tcache and arenas), why freed memory often doesn't return to the OS, and how the kernel allocates memory with the buddy system and the slab allocator, plus what jemalloc, tcmalloc and mimalloc do differently.
---

User allocators obtain virtual address ranges through interfaces such as `mmap` and `brk`; physical pages are often supplied lazily on access. This lesson uses 4 KiB pages for arithmetic, not as a universal Linux page size. Programs want objects: 24 bytes for a node, 100 bytes for a string, 3 MiB for a buffer. A **memory allocator** sits in between, buying pages from the OS in bulk and carving them into objects.

There are two layers on Linux:

```
 your code: malloc(100)
      |
 user-space allocator (glibc, jemalloc)
      |  brk / mmap, in pages
 kernel: page allocator (buddy system)
      |  plus slab caches for the
      |  kernel's own objects
 physical frames
```

Every allocator juggles the same three goals: be **fast** (allocation can be frequent), waste little memory (**fragmentation**), and scale across **threads** without lock contention.

## Fragmentation, the core problem

- **Internal fragmentation**: you asked for 100 bytes and got a 112-byte block. The 12 bytes inside the block are wasted.
- **External fragmentation**: there is 1 MiB free in total, but in scattered 64-byte holes, so a 4 KiB request cannot be satisfied from it.

A C allocator cannot fix external fragmentation after the fact, because it cannot move objects: the program holds raw pointers to them. Garbage-collected runtimes can compact; malloc cannot. So allocators fight fragmentation through their **placement policy** when memory is handed out.

Classic placement policies for a free list:

| Policy | Picks | Trait |
|---|---|---|
| First fit | First hole big enough | Fast, splinters the front |
| Best fit | Smallest hole that fits | Smallest immediate remainder; search and fragmentation depend on indexing/workload |
| Segregated | A list per size class | Fast, some internal waste |

Modern allocators are almost all **segregated**: round each request up to a **size class** and keep a separate free list per class. A cached fast path can be a constant-time pop from a size-class list. Refill, coalescing and requesting memory need additional work.

## glibc malloc (ptmalloc2)

The following concrete model is **glibc 2.39 on ordinary x86-64 Linux**, with default alignment and no replacement/debug allocator. Its lineage includes dlmalloc and ptmalloc2, but glibc has substantially changed it. Other versions and tunables differ; inspect the deployed version rather than treating these defaults as permanent.

### Chunks

An ordinary arena allocation is a **chunk** with an 8-byte size/status word immediately before the returned pointer. The layout also has a preceding previous-size field; for an in-use arena chunk, usable space can borrow the next chunk's previous-size word. Separately mmapped chunks have different overhead. On x86-64 chunks are multiples of 16 bytes with a minimum of 32. A request of *n* bytes needs roughly *n* + 8, rounded up to 16:

```
malloc(1)   -> 32-byte chunk, 24 usable
malloc(24)  -> 32-byte chunk, 24 usable
malloc(25)  -> 48-byte chunk, 40 usable
malloc(100) -> 112-byte chunk, 104 usable
```

You can check it:

```c
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t n[] = {1, 24, 25, 100};
    for (int i = 0; i < 4; i++) {
        void *p = malloc(n[i]);
        if (!p) return 1;
        printf("%zu -> %zu\n", n[i],
               malloc_usable_size(p));
        free(p);
    }
}
/* 1 -> 24, 24 -> 24,
   25 -> 40, 100 -> 104 */
```

The header is also why a heap buffer overflow is so dangerous: an overflow can damage adjacent payload or allocator metadata, potentially enabling exploitation despite integrity checks. Not every out-of-bounds byte reaches a size field.

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

So a service that allocates a burst of temporary objects, then frees most of them, often keeps its peak RSS. Allocator retention can explain this without a leak, but RSS alone cannot distinguish retention from leaked or unprofiled live allocations.

## jemalloc, tcmalloc and mimalloc

Several allocators were written to scale better than ptmalloc and fragment less over long runs.

**jemalloc**:

- Fine-grained **size classes**: 16-byte steps for small sizes, then four classes per doubling (160, 192, 224, 256, 320...). For these classes (excluding the smallest sizes), rounding waste is bounded at about 20% of the slot.
- Objects of one class live together in **slabs** (runs of pages), so no per-object header is needed.
- Per-thread caches in front of multiple **arenas**; the documented automatic arena limit defaults to four times CPUs, or one for a single CPU. Assignment is not a promised round-robin API contract.
- Unused pages are returned to the OS gradually on a time-based **decay** schedule, using `madvise`, rather than all at once.
- Rich built-in statistics and heap profiling, useful for finding leaks in production.

**tcmalloc** (Google): a front end supporting **per-CPU** caches or legacy per-thread mode (using Linux restartable sequences so no locks or atomics are needed on the fast path), a middle tier of transfer caches and central free lists, and a page heap. Its newer page heap is **huge-page aware**, packing allocations into huge-page regions (2 MiB in the usual x86-64 example) to improve TLB use.

**mimalloc** (Microsoft Research): **free-list sharding**, with many small free lists per page rather than one big one, which keeps related objects close together and makes the fast path a few instructions.

| | glibc | jemalloc | tcmalloc |
|---|---|---|---|
| Fast path | per-thread tcache | per-thread cache | per-CPU or per-thread |
| Small objects | headers on chunks | headerless slabs | headerless spans |
| Return to OS | trim top, mmap free | decay over time | background release |

For a compatible dynamically linked program, an installed allocator can sometimes be interposed with `LD_PRELOAD=/actual/path/libjemalloc.so ./server`. The path, ABI and allocation/deallocation boundaries must match. Static linking and some runtime/build choices require another integration method.

> [!note] Performance evidence gap
> No benchmark record accompanies this lesson, so comparative RSS, latency and cross-thread-free rankings are omitted. Measure representative workloads, retention and contention before selecting an allocator.

> [!note] Python has its own layer
> In a standard GIL-enabled build using **pymalloc**, small allocations of up to 512 bytes use pools in larger arenas, with larger requests falling back to raw allocation. Build/runtime settings matter: free-threaded CPython uses mimalloc. Extension modules can also allocate directly, so not every Python object allocation follows pymalloc.

## The kernel: the buddy allocator

Inside the kernel, physical frames are handed out by the **buddy allocator**. It manages free blocks of 2^k pages, over a configured range of **orders**. For an example with 4 KiB pages and maximum order 10, sizes run from 4 KiB to 4 MiB; architecture and kernel configuration determine the actual maximum.

To allocate order *k*: take a free block from the order-*k* list. If empty, take a bigger block and **split** it in halves repeatedly. The two halves of a split are **buddies**.

> [!example] Allocating 8 KiB from a 64 KiB block
> Order 1 (2 pages) is wanted; only an order-4 (64 KiB) block is free.
> - Split 64 → 32 + 32. Keep one 32 on the order-3 list.
> - Split 32 → 16 + 16. Keep one 16 on the order-2 list.
> - Split 16 → 8 + 8. Return one 8, keep the other on the order-1 list.

On free, the kernel checks whether the block's buddy is also free. If so, it merges them into the next order up, and repeats. Finding a buddy is a single XOR, because buddies differ only in the bit equal to their size:

```
block offset 0x6000, size 0x2000
buddy = 0x6000 XOR 0x2000 = 0x4000
merged block: 0x4000, size 0x4000
```

This gives cheap splitting and coalescing, and physically contiguous blocks when drivers or huge pages need them. The weaknesses are internal fragmentation (a 9-page request takes 16 pages) and long-term external fragmentation: under sustained allocation/free activity, scattered order-0 pages can make order-9 (2 MiB) blocks scarce. That is why THP needs **compaction**, and why the kernel groups pages by mobility so movable ones can be migrated.

```
$ cat /proc/buddyinfo
Node 0, zone Normal 4123 2210 980 ...
```

Each column is the count of free blocks of order 0, 1, 2 and so on. Zeros in high-order columns mean no free blocks of those orders in that zone; they can reflect fragmentation or simply low available memory.

## The kernel: slab allocation

The kernel allocates millions of small, same-sized objects: inodes, dentries, socket buffers, task structs. Asking the buddy allocator for a page each time would waste most of it.

The **slab allocator** (Jeff Bonwick, Solaris, 1994) keeps a **cache** per object type. Each cache owns **slabs**, one or more contiguous pages divided into equal-sized slots:

```
illustrative cache (192 B slots)
 slab (one 4 KiB page): 21 slots
 [obj][obj][free][obj][free]...
```

The simple fast path takes or returns a slot. Fixed-size caches do not need a malloc-style size header on every live object, but maintain slab/free-list metadata; debugging, alignment and hardening can add per-object overhead. Refill and partial-slab selection require additional work. Generic `kmalloc` is built from caches of fixed sizes (8, 16, 32, 64, 96, 128, 192, 256 bytes and so on).

Linux has had three implementations. **SLUB** is the default and, since SLOB was removed in 6.4 and SLAB in 6.8, the only one. It uses per-CPU state and partial-slab management; synchronization and the exact fast path depend on architecture, configuration and kernel version.

Inspect it with `slabtop` or `/proc/slabinfo`. A kernel memory leak, or a workload that creates millions of dentries, shows up here rather than in any process's RSS.

User-space allocators use related grouping ideas, with different metadata, caching and reclamation policies.

## Pitfalls

- **Benchmarks need representative workloads.** A microbenchmark that allocates and frees one size in a loop can mostly hit a cached fast path. Mixed lifetimes and sizes can expose retention or fragmentation on a different timescale.
- **Cross-thread frees.** A producer thread allocates, a consumer frees. Thread caches fill on one side and drain on the other, and remote frees affect reuse. A glibc chunk can enter another thread's tcache without changing its owning arena. Performance depends on the allocator and workload.
- **Mixing allocators.** Memory from one allocator must be freed by the same one. Passing a jemalloc-owned allocation to an incompatible glibc `free` is undefined behavior and can corrupt memory or crash.
- **Don't assume RSS falls after free.** Use the allocator's own statistics (`malloc_stats()`, `mallctl` in jemalloc) to see free-but-retained memory.

## Key takeaways
- Allocators trade speed, fragmentation and thread scalability; C allocators cannot move objects, so placement, coalescing, segregating lifetimes and releasing suitable free regions help manage external fragmentation.
- In the specified glibc 2.39 x86-64 model, ordinary chunks use 16-byte rounding, tcache and arena/bin machinery; large mapping decisions depend on existing space and thresholds.
- Freed memory often stays in the process because brk can only shrink from the top and pages with live objects cannot be returned.
- jemalloc, tcmalloc and mimalloc use size-class slabs, per-thread or per-CPU caches and gradual return to the OS; their tradeoffs should be measured on the target workload.
- The kernel's buddy allocator splits and merges power-of-two blocks of pages (over a configured order range); buddies are found by XOR, and fragmentation of high orders limits huge pages.
- The slab allocator (SLUB in Linux) gives each kernel object type its own cache of pre-sized slots; inspect it with slabtop.

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
