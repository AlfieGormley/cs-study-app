---
id: mem-buddy-orders
sourceLesson: mem-allocators
title: Splitting power-of-two page blocks
level: advanced
minutes: 3
summary: Buddy orders count powers of two base pages.
---

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
2^k: k copies of 2 multiplied together (2^0 = 1)
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

For an example with 4 KiB pages and maximum order 10, sizes run from 4 KiB to 4 MiB; architecture and kernel configuration determine the actual maximum. A three-page request needs order two: the smallest power-of-two block large enough holds four pages.

To allocate order k: take a free block from the order-k list. If empty, take a bigger block and **split** it in halves repeatedly. The two halves of a split are **buddies**.

> [!example] Allocating 8 KiB from a 64 KiB block
> Order 1 (2 pages) is wanted; only an order-4 (64 KiB) block is free.
> - Split 64 → 32 + 32. Keep one 32 on the order-3 list.
> - Split 32 → 16 + 16. Keep one 16 on the order-2 list.
> - Split 16 → 8 + 8. Return one 8, keep the other on the order-1 list.

## Key takeaways
- Buddy orders count powers of two base pages.
- Allocation splits larger blocks until the requested order is reached.

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
