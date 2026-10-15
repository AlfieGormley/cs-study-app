---
id: mem-tlb-capacity
sourceLesson: mem-tlb
title: TLB reach and large working sets
level: intermediate
minutes: 2
summary: Reach multiplies the entry count by the page size those entries support.
---

## TLB reach

**TLB reach** is the amount of memory the TLB can map at once. Each entry maps one whole page, so:

```formula
R = NP
R = 64 × 4 KiB = 256 KiB
R = 1,536 × 2 MiB = 3,072 MiB = 3 GiB
where
R: the TLB reach, in bytes
N: the number of TLB entries
P: the page size each entry maps
KiB: kibibyte, 1,024 bytes
MiB: mebibyte, 1,024 KiB
GiB: gibibyte, 1,024 MiB
In words: reach grows with both the entry count and the page size; with 2 MiB pages each entry covers 512 times as much memory as with 4 KiB pages.
```

Reach is a capacity, not a guarantee: conflicts between entries, separate capacities for each page size and cold misses mean a working set smaller than the reach can still miss.

| TLB | 4 KiB pages | 2 MiB pages |
|---|---|---|
| 64 entries | 256 KiB | 128 MiB |
| 1,536 entries | 6 MiB | 3 GiB |

A hot set beyond the effective reach can increase misses; locality, associativity, page-size-specific capacities and other translation-cache levels determine the rate. If all 50 GiB of a buffer pool is actively accessed, it greatly exceeds a hypothetical 6 MiB reach. Allocated pool capacity need not equal the hot working set. This is the main argument for huge pages.

## Key takeaways
- Reach multiplies the entry count by the page size those entries support.
- Conflicts, locality and separate page-size capacities can cause misses below nominal reach.

## Further reading
- [OSTEP: Paging: Faster Translations (TLBs) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-tlbs.pdf)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Transparent Hugepage Support — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/transhuge.html)
- [HugeTLB Pages — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/hugetlbpage.html)
- [Diagnosing latency issues (THP section) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [What Every Programmer Should Know About Memory, Ulrich Drepper (PDF)](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
