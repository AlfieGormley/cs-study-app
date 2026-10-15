---
id: mem-fault-accounting
sourceLesson: mem-page-faults
title: Minor faults, major faults and average cost
level: intermediate
minutes: 4
summary: Minor and major counters distinguish page-in work, rather than promising fixed latency.
---

## Minor and major faults

- A **minor fault** is accounted as resolved without the page-in I/O required by a major fault, for example demand-zero allocation or mapping resident backing. Its handler may still incur allocation, reclaim or contention work.
- A **major fault** is accounted as requiring page-in I/O, for example missing file or swap backing. Latency depends on caching, device, queueing and kernel behavior.

An ordinary COW fault that copies resident private data is normally minor, as is populating a mapping from resident, up-to-date file-cache backing. Resource pressure can still make either path expensive.

Fault type is useful evidence, but it does not alone determine duration.

> [!note] Content gap
> Fixed minor/major fault latencies are omitted because no reproducible benchmark configuration is provided. Times in the arithmetic exercise below are hypothetical inputs.

Illustrative command/output sample; actual values depend on the workload, system and observation interval:

```
$ /usr/bin/time -v ./prog
  Major (requiring I/O) page
    faults: 3
  Minor (reclaiming a frame) page
    faults: 16450
```

`ps -o min_flt,maj_flt -p <pid>` reports the process’s minor and major counters. `perf stat -e page-faults,major-faults` measures selected faults over its configured scope and interval: `page-faults` is a total, not a synonym for minor faults. These outputs need not be numerically identical.

### The cost in numbers

Treat the page fault rate like a TLB miss rate. Each access either completes normally or takes a major fault, so the average access time is a weighted average of the two:

```formula
EAT = (1 − p)t_mem + p t_fault
where
EAT: the effective access time: the average time of one memory access, in nanoseconds (ns)
p: the page-fault rate: the fraction of accesses that take a major page fault, from 0 to 1 (0.001 is one in a thousand)
1 − p: the fraction of accesses that do not fault
t_mem: the time of an ordinary memory access, in ns; 100 ns in the example below
t_fault: the total time of an access that faults, including servicing the fault, in ns; a storage read makes it millions of ns
ns: nanosecond, a billionth of a second (10^-9 s)
In words: because a fault costs tens of thousands of times more than a normal access, even a tiny fault rate dominates the average.
```

This is a hypothetical model: it assumes one fixed cost per fault and accesses happening one after another. Real fault costs vary widely (see the content-gap note above), and a minor fault is not guaranteed to be faster than every major fault; reclaim, contention and the backing path matter.

> [!example] One fault per thousand accesses
> Memory access 100 ns, major fault 8 ms (8,000,000 ns), one fault per thousand accesses.

```formula
t_fault = 8 ms = 8,000,000 ns
EAT = 0.999 × 100 ns + 0.001 × 8,000,000 ns
EAT = 99.9 ns + 8,000 ns ≈ 8,100 ns
where
t_fault: the time of an access that takes a major fault
ms: millisecond, a thousandth of a second, which is 1,000,000 ns
EAT: the effective (average) access time
ns: nanosecond, 10^-9 seconds
≈: approximately equal to
In words: one access in a thousand costing 8 ms raises the average from 100 ns to about 8,100 ns, so memory is now about 80 times slower.
```

How rare must faults be to keep the slowdown under 10%, so that the average stays below 110 ns? Rearrange the formula and solve for p:

```formula
EAT = t_mem + p(t_fault − t_mem)
100 ns + p × 7,999,900 ns < 110 ns
p × 7,999,900 ns < 10 ns
p < 10 / 7,999,900 ≈ 1.25 × 10^-6
where
EAT: the effective (average) access time
t_mem: an ordinary access, 100 ns
p: the page-fault rate, the fraction of accesses that fault
t_fault: the time of a faulting access, 8,000,000 ns
ns: nanosecond
≈: approximately equal to
10^-6: one millionth
In words: the extra cost per access is the fault rate times the 7,999,900 ns penalty, and it must stay under 10 ns, so fewer than one major fault per 800,000 accesses.
```

That is fewer than **one major fault per 800,000 accesses**.

This is why a machine that is swapping heavily feels frozen rather than merely slow.

## Key takeaways
- Minor and major counters distinguish page-in work, rather than promising fixed latency.
- Even rare expensive faults can dominate a serial average-access model.

## Further reading
- [OSTEP: Beyond Physical Memory: Mechanisms (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys.pdf)
- [OSTEP: Complete Virtual Memory Systems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-complete.pdf)
- [Concepts overview — Linux kernel memory management docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/concepts.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [zswap — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/zswap.html)
- [Page fault — Wikipedia](https://en.wikipedia.org/wiki/Page_fault)
