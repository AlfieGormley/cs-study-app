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

## Fragmentation, the central problem

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

An ordinary arena allocation is an **arena chunk** with an 8-byte size/status word immediately before the returned pointer. The layout also has a preceding previous-size field; for an in-use arena chunk, usable space can borrow the next chunk's previous-size word. Separately mmapped chunks have different overhead. On x86-64 chunks are multiples of 16 bytes with a minimum of 32. A request needs its own bytes plus the 8-byte header, rounded up to a multiple of 16:

```formula
C = max(32, 16 × ⌈(n + 8) / 16⌉)
U = C − 8
where
C: the chunk size in bytes
n: the number of bytes requested from malloc
⌈ ⌉: ceiling: round up to a whole number, so 16 × ⌈x / 16⌉ is x rounded up to a multiple of 16
max: the larger of its two arguments; 32 is the minimum chunk size
U: the usable bytes in the chunk, which is what malloc_usable_size reports
In words: add the 8-byte header, round up to the next multiple of 16 (at least 32), and everything except the header is usable.
```

For example, malloc(100) needs 108 bytes, which rounds up to a 112-byte chunk with 104 usable. This model holds for ordinary arena chunks in the stated glibc release; separately mmapped chunks follow different rules.

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

So a service that allocates a flood of temporary objects, then frees most of them, often keeps its peak RSS. Allocator retention can explain this without a leak, but RSS alone cannot distinguish retention from leaked or unprofiled live allocations.

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
w_max ≈ (1.25 × c − c) / (1.25 × c)
w_max = 0.25 / 1.25 = 0.2 = 20 %
where
w: the rounding waste, as a fraction of the slot
S: the slot size: the size class the request is rounded up to
n: the requested size in bytes
w_max: the largest possible waste with four classes per doubling
c: a power-of-two size class such as 256; the next class is 1.25 × c (320)
≈: approximately equal to (the request is c + 1 bytes, so the true waste is a hair under 20 %)
%: per cent
In words: with four classes per doubling, the gap above a power of two is a quarter of it, which is at most a fifth of the slot.
```

For example, a 257-byte object goes in a 320-byte slot: 63 bytes, or about 19.7% of the slot, are wasted.

**tcmalloc** (Google): a front end supporting **per-CPU** caches or legacy per-thread mode (using Linux restartable sequences so no locks or atomics are needed on the fast path), a middle tier of transfer caches and central free lists, and a page heap. Its newer page heap is **huge-page aware**, packing allocations into huge-page regions (2 MiB in the usual x86-64 example) to improve TLB use.

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
> In a standard GIL-enabled build using **pymalloc**, small allocations of up to 512 bytes use pools in larger arenas, with larger requests falling back to raw allocation. Build/runtime settings matter: free-threaded CPython uses mimalloc. Extension modules can also allocate directly, so not every Python object allocation follows pymalloc.

## The kernel: the buddy allocator

Inside the kernel, physical frames are handed out by the **buddy allocator**. It manages free blocks whose size is a power of two pages, over a configured range of **buddy orders**:

```formula
S_k = 2^k × P
S_0 = 2^0 × 4 KiB = 4 KiB
S_10 = 2^10 × 4 KiB = 4,096 KiB = 4 MiB
k = ⌈log_2(N)⌉
where
S_k: the size of a block of order k
k: the order of a block: the block holds 2^k pages
2^k: 2 multiplied by itself k times (2^0 = 1)
P: the base page size; 4 KiB in this lesson's examples
S_0: the smallest block, one page
S_10: the block at order 10
N: the number of pages a request needs
log_2: the base-2 logarithm: the power of 2 that gives the number (log_2(8) = 3)
⌈ ⌉: ceiling: round up to a whole number
KiB: kibibyte, 1,024 bytes
MiB: mebibyte, 1,024 KiB
In words: each order doubles the block size, and a request gets the smallest order whose block holds all the pages it needs.
```

For an example with 4 KiB pages and maximum order 10, sizes run from 4 KiB to 4 MiB; architecture and kernel configuration determine the actual maximum. A 3-page request needs order ⌈log_2(3)⌉ = 2, a 4-page block.

To allocate order k: take a free block from the order-k list. If empty, take a bigger block and **split** it in halves repeatedly. The two halves of a split are **buddies**.

> [!example] Allocating 8 KiB from a 64 KiB block
> Order 1 (2 pages) is wanted; only an order-4 (64 KiB) block is free.
> - Split 64 → 32 + 32. Keep one 32 on the order-3 list.
> - Split 32 → 16 + 16. Keep one 16 on the order-2 list.
> - Split 16 → 8 + 8. Return one 8, keep the other on the order-1 list.

On free, the kernel checks whether the block's buddy is also free. If so, it merges them into the next order up, and repeats. Finding a buddy is a single XOR, because buddies differ only in the bit equal to their size:

```formula
a_b = a XOR S
a_m = min(a, a_b)
S_m = 2 × S
where
a_b: the offset of the block's buddy
a: the block's offset: its address measured from the start of the allocator's region, in bytes; always a multiple of S
XOR: exclusive or, bit by bit: a result bit is 1 when exactly one of the two input bits is 1. XOR with S flips the single bit worth S, which turns the lower buddy into the upper one and back
S: the block's size in bytes, a power of two
a_m: the offset of the merged block: the lower of the two buddies
min: the smaller of its two arguments
S_m: the size of the merged block, twice the original
In words: flip the bit worth the block's size to find the buddy; if both are free they merge into a block twice as big that starts at the lower one.
```

For example, a 0x2000-byte (8 KiB) block at offset 0x6000:

```formula
a_b = 0x6000 XOR 0x2000 = 0x4000
a_m = min(0x6000, 0x4000) = 0x4000
S_m = 2 × 0x2000 = 0x4000
where
a_b: the buddy's offset
XOR: exclusive or, bit by bit; 0x6000 is binary 0110 0000 0000 0000 and 0x2000 is 0010 0000 0000 0000, so flipping that bit gives 0100 0000 0000 0000
a_m: the merged block's offset
min: the smaller of its two arguments
S_m: the merged block's size, 0x4000 = 16 KiB
In words: the buddy of the 8 KiB block at 0x6000 is the 8 KiB block at 0x4000, and together they form a 16 KiB block at 0x4000.
```

The rule relies on blocks being aligned to their own size, which the allocator guarantees by only ever splitting blocks in half.

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

The slot count is the slab size divided by the object size, rounded down, because an object cannot hang off the end of the slab:

```formula
N = ⌊S_slab / s⌋
W = S_slab − N × s
N = ⌊4,096 B / 192 B⌋ = ⌊21.33⌋ = 21
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
