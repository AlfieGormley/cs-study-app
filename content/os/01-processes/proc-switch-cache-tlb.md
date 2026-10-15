---
id: proc-switch-cache-tlb
sourceLesson: proc-context-switching
title: "Caches, TLBs and migration"
level: advanced
minutes: 4
summary: "Cache refill latency sums are models, not automatic elapsed-time predictions."
---

Cache refill latency sums are models, not automatic elapsed-time predictions. This lesson focuses on caches, tlbs and migration.

## The indirect cost: caches and the TLB

Direct hand-off work is only one cost. Cache and translation effects can add more work afterwards; their size depends on the workload.

### Caches

Caches have finite, processor-specific capacities. Another task can evict useful code/data lines, making later accesses require a lower cache level or memory. The number and latency of misses depend on the working sets and memory-level parallelism.

> [!example] Paying for a cold cache
> Say task A's hot working set is 512 KiB, and while A was switched out another task evicted all of it. Assume each refill takes a hypothetical 15 ns and refills are fully serialised. The calculation below shows A then spends over 100 µs just refilling.

To estimate a refill cost, count the cache lines in the working set and multiply by the time to refill one line:

```formula
N_lines = W / L
T_refill = N_lines t_line
N_lines = 524,288 B / 64 B = 8,192
T_refill = 8,192 × 15 ns = 122,880 ns
T_refill ≈ 122.88 µs
where
N_lines: the number of cache lines the working set fills
W: the working set, the data a task touches repeatedly; here 512 KiB = 524,288 B
L: the cache-line size, the unit a cache stores and refills; 64 B on typical x86-64 CPUs
T_refill: the total time spent refilling, if the refills happen one after another
t_line: the time to refill one line from a lower cache level or memory; 15 ns is a hypothetical figure
B: byte, 8 bits
KiB: kibibyte, 1,024 bytes
ns: nanosecond, one billionth of a second
µs: microsecond, one millionth of a second (1,000 ns)
≈: approximately equal to
In words: a half-megabyte working set is about eight thousand cache lines, and refilling them one at a time at 15 ns each adds up to about 123 µs.
```

This is a simplified latency sum, not a prediction of real elapsed time; overlapping refills and bandwidth matter. Not every switch is that bad, but this is why a switch's true cost depends on the working set.

### The TLB

The **TLB** caches virtual-to-physical page translations. A miss means a page-table walk: several dependent memory reads. Switching to a different address space makes the old translations meaningless.

- Without tagging, writing `CR3` flushes all non-global TLB entries. The new task starts with a cold TLB.
- With tagging, entries carry an address-space ID: **PCID** on x86 (used by Linux since 4.14), **ASID** on ARM. Entries for several processes can coexist, so switching back to a recent process can find its translations still there.

PCID became much more important after Meltdown: when KPTI is enabled, it switches page tables on user/kernel entry and return, and without PCID each switch would flush the TLB.

### Migrations

Moving to another core can lose private-cache locality; shared caches, previously cached data and cache-coherence transfers complicate the actual cost. Linux tries to keep tasks where they last ran (cache affinity). `perf stat -e context-switches,cpu-migrations` shows both counts.

## Key takeaways
- Cache refill latency sums are models, not automatic elapsed-time predictions.
- Address-space tags can preserve TLB translations across switches.

## Further reading
- [Mechanism: Limited Direct Execution — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Context switch — Wikipedia](https://en.wikipedia.org/wiki/Context_switch)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Page Table Isolation (PTI) — Linux kernel docs](https://docs.kernel.org/arch/x86/pti.html)
- [proc(5): /proc/pid/status — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Thread (computing) — Wikipedia](https://en.wikipedia.org/wiki/Thread_(computing))
