---
id: mem-buddy-coalescing
sourceLesson: mem-allocators
title: Finding and merging a block’s buddy
level: advanced
minutes: 3
summary: XOR with a block’s size identifies its aligned buddy within the modelled region.
---

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

Illustrative command/output sample; actual values depend on the workload, system and observation interval:

```
$ cat /proc/buddyinfo
Node 0, zone Normal 4123 2210 980 ...
```

Each column is the count of free blocks of order 0, 1, 2 and so on. Zeros in high-order columns mean no free blocks of those orders in that zone; they can reflect fragmentation or simply low available memory.

## Key takeaways
- XOR with a block’s size identifies its aligned buddy within the modelled region.
- Only compatible free buddies can merge; scattered pages can obstruct high-order allocations.

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
