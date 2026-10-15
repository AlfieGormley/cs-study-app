---
id: mem-allocation-fragmentation
sourceLesson: mem-allocators
title: From page ranges to object size classes
level: advanced
minutes: 3
summary: Object allocators divide larger page-backed ranges and trade speed, waste and concurrency.
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

A fixed-stride pool or array can amortise allocation metadata across many records instead of allocating each record separately. Compare total slot bytes under explicit alignment and metadata assumptions; this does not eliminate every source of page or pool overhead.

## Key takeaways
- Object allocators divide larger page-backed ranges and trade speed, waste and concurrency.
- Internal waste is inside allocations; external waste is free space split into unusable holes.

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
