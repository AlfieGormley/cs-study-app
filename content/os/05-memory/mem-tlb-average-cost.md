---
id: mem-tlb-average-cost
sourceLesson: mem-tlb
title: Modelling the cost of translation misses
level: intermediate
minutes: 4
summary: Effective access time weights complete hit and miss costs by their probabilities.
---

## Effective access time

The **effective access time (EAT)** is the average cost of one memory access once TLB misses are included. Every access either hits or misses, so the average is a weighted average of the two costs, each weighted by how often it happens:

```formula
EAT = h t_hit + (1 − h)t_miss
where
EAT: the effective access time: the average time of one memory access, in nanoseconds (ns)
h: the TLB hit rate: the fraction of accesses whose translation is in the TLB, from 0 to 1 (0.98 means 98 %)
1 − h: the miss rate: the fraction of accesses that miss
t_hit: the time of an access whose translation hits in the TLB, in ns
t_miss: the time of an access that misses, including the page walk, in ns
ns: nanosecond, a billionth of a second (10^-9 s)
In words: average the hit cost and the miss cost, weighting each by how often it happens; a rare but very expensive miss can still move the average a lot.
```

The model is deliberately simple. It assumes accesses happen one at a time, every miss costs the same, and nothing overlaps. Real CPUs cache page-table entries, overlap walks with other work and have several TLB levels, so use it for reasoning, not for predicting a benchmark.

> [!example] Single-level table
> Memory access takes 100 ns, TLB lookup time is negligible, the page table has a single level, and the hit rate is 98%. A hit is just the data access; a miss reads the PTE from memory first.

```formula
t_hit = t_mem = 100 ns
t_miss = 2 × t_mem = 200 ns
EAT = 0.98 × 100 ns + 0.02 × 200 ns
EAT = 98 ns + 4 ns = 102 ns
where
t_hit: the cost of a TLB hit: just the data access
t_mem: the time of one memory access, 100 ns
t_miss: the cost of a miss: one PTE read plus the data access
EAT: the effective (average) access time
ns: nanosecond, 10^-9 seconds
In words: 98 % of accesses take 100 ns and 2 % take 200 ns, which averages 102 ns, a 2 % slowdown.
```

> [!example] x86-64, 4-level, no walk caching
> Same 100 ns memory, but a miss now reads 4 table entries before the data.

```formula
t_miss = (4 + 1) × t_mem = 500 ns
EAT = 0.99 × 100 ns + 0.01 × 500 ns
EAT = 99 ns + 5 ns = 104 ns
EAT = 0.90 × 100 ns + 0.10 × 500 ns
EAT = 90 ns + 50 ns = 140 ns
where
t_miss: the cost of a miss: 4 page-table reads plus the data access
t_mem: the time of one memory access, 100 ns
EAT: the effective (average) access time; the first pair of lines uses a 99 % hit rate, the second pair 90 %
ns: nanosecond, 10^-9 seconds
In words: at 99 % hits the average is 104 ns; at 90 % hits it is 140 ns, a 40 % slowdown, because each miss costs five memory accesses.
```

If the TLB lookup itself takes time (older textbooks often use 20 ns), it is paid on both the hit and the miss:

```formula
t_hit = t_TLB + t_mem
t_miss = t_TLB + (L + 1) × t_mem
where
t_hit: the cost of a TLB hit
t_miss: the cost of a TLB miss
t_TLB: the time of the TLB lookup itself
t_mem: the time of one memory access
L: the number of page-table levels read on a miss; 1 for a single-level table, 4 for x86-64
In words: a miss pays the lookup, one memory read per page-table level, and then the data access.
```

The lesson is the same: the hit rate dominates, and every percentage point of misses costs a multiple of itself once the walk is deep.

## Key takeaways
- Effective access time weights complete hit and miss costs by their probabilities.
- Walk depth increases the miss penalty in a serial uncached model.
- Real caching and overlap limit this model’s predictive power.

## Further reading
- [OSTEP: Paging: Faster Translations (TLBs) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-tlbs.pdf)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Transparent Hugepage Support — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/transhuge.html)
- [HugeTLB Pages — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/hugetlbpage.html)
- [Diagnosing latency issues (THP section) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [What Every Programmer Should Know About Memory, Ulrich Drepper (PDF)](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
