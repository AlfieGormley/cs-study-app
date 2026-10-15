---
id: mem-tlb-locality
sourceLesson: mem-tlb
title: Translation caches and access locality
level: intermediate
minutes: 5
summary: A TLB caches page translations and permissions; its miss is distinct from an OS page fault.
---

The earlier units ended with a problem. An uncached four-level x86-64 walk to a 4 KiB page reads four entries before the data access. That simplified read count is not a universal 5× latency prediction.

Hardware fixes this with a small, very fast cache of recent translations: the **translation lookaside buffer (TLB)**. Most memory accesses find their translation in the TLB and skip the walk entirely.

## What the TLB stores

Each TLB entry maps one virtual page to one physical frame, with the permission bits copied from the PTE:

```
 TLB entry
 +---------+---------+---------------+
 |   VPN   |   PFN   | R/W U/S NX .. |
 +---------+---------+---------------+
   tag       data      permissions
```

On every memory access the MMU does:

1. Look up the VPN in the TLB.
2. **Hit**: take the PFN, check permissions, and form the physical address. Many designs overlap lookup with cache indexing; actual latency and throughput depend on the CPU.
3. **Miss**: walk the page tables (the hardware **page walker** on x86 and ARM), insert the result into the TLB, then retry.

Some older architectures, notably MIPS, use a **software-managed TLB**: a miss raises an exception and the OS refills the entry itself. That gives the OS freedom over page-table format with handler cost depending on the architecture and implementation. x86 and ARM do it in hardware.

## Typical sizes and costs

TLB organizations differ by CPU, page size and instruction/data access type. Many cores have separate first-level instruction/data TLBs and another translation-cache level. Consult the exact CPU's documentation or hardware enumeration rather than assuming one capacity.

A miss served by another translation cache avoids a full walk. Page walks can use data caches and paging-structure caches; a TLB miss is not synonymous with a DRAM access or an OS page fault.

> [!note] Content gap
> Universal entry counts and cycle/microsecond costs are omitted: this lesson has no measured CPU configuration or reproducible benchmark record for those figures. The following capacities and times are explicit arithmetic examples.

## Why hit rates are high

The TLB works for the same reason caches work: **locality**.

> [!example] Scanning an array
> A loop reads a large array of 4-byte ints in order. Each 4 KiB page holds 1,024 ints.
>
> In a cold, aligned scalar-access model without translation prefetching or interfering evictions, the first access to each page misses and the next 1,023 hit.

As a formula, for a sequential scan:

```formula
A = P / s
h = (A − 1) / A
A = 4,096 B / 4 B = 1,024
h = 1,023 / 1,024 ≈ 0.999 = 99.9 %
where
A: the number of accesses that land on each page
P: the page size in bytes; 4,096 for 4 KiB pages
s: the size of each element read, in bytes; 4 for an int
h: the TLB hit rate: the fraction of accesses whose translation is already in the TLB
B: bytes
≈: approximately equal to
%: per cent
In words: each page costs one miss and then serves every other access on it, so the bigger the page compared with the element, the closer the hit rate gets to 100 %.
```

Now read only one int per page (stride 4,096 bytes). Every access lands on a new page, so there is only one access per page and the formula gives a hit rate of zero on a cold pass without translation prefetching. On repeated passes, capacity and replacement determine the hit rate.

```c
/* Same address range, different
   access counts and TLB miss rates. */
/* Consecutive ints reuse translations. */
for (size_t i = 0; i < n; i++)
    sum += a[i];        /* stride 4 B */

/* One int per assumed 4 KiB page. */
for (size_t i = 0; i < n; i += 1024)
    sum += a[i];        /* stride 4 KiB */
```

On supported Linux PMUs, `perf stat -e dTLB-load-misses ./prog` can help investigate. Check `perf list`, event semantics, permissions and CPU model: a generic event need not count every L1-TLB miss.

Random access over a large data structure (a big hash table, a graph, a B-tree spread across GiB of RAM) is the hard case. Each access may touch a different page, and the TLB cannot hold them all.

## Key takeaways
- A TLB caches page translations and permissions; its miss is distinct from an OS page fault.
- Sequential access can reuse one translation many times, while page-sized strides can miss each time.

## Further reading
- [OSTEP: Paging: Faster Translations (TLBs) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-tlbs.pdf)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Transparent Hugepage Support — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/transhuge.html)
- [HugeTLB Pages — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/hugetlbpage.html)
- [Diagnosing latency issues (THP section) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [What Every Programmer Should Know About Memory, Ulrich Drepper (PDF)](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
