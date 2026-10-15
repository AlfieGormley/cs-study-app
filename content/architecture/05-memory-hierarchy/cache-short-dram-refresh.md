---
id: cache-short-dram-refresh
title: Refresh availability and disturbance
level: advanced
minutes: 3
sourceLesson: cache-arch-dram
summary: Refresh timing and affected resources depend on the device and operating mode.
---

This unit builds on the earlier cache lessons and focuses on refresh availability and disturbance. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Refresh

DRAM retention requires periodic refresh; the interval, blocking time, temperature rules and supported modes are part-specific. For an illustrative all-bank refresh model, assume one operation every 7,812.5 ns, blocking the rank for 350 ns. The share of time lost is the blocked time divided by the interval:

```formula
f_ref = t_RFC / t_REFI
f_ref = 350 ns / (7,812.5 ns)
f_ref ≈ 0.0448 = 4.48%
where
f_ref: the fraction of time the rank is busy refreshing
t_RFC: how long one refresh blocks the rank, 350 nanoseconds (ns) here
t_REFI: the interval between refresh operations, 7,812.5 ns here
≈: approximately equal to
%: per cent, parts per hundred
ns: nanosecond, one billionth of a second
In words: blocking for 350 ns out of every 7,812.5 ns loses about 4.5% of the rank's time.
```

If that interval halves while the blocking duration stays fixed, the fraction doubles to 8.96%. A product-specific density/temperature timing table is absent because those exact operating modes have not been reliably verified here.

DDR5 **same-bank refresh** targets one selected bank in each bank group, allowing other banks to remain available subject to timing constraints. It is not a refresh of only one bank in the entire device. A demand request can still be delayed by refresh.



> [!warning] Row hammer
> Activating one row very rapidly can disturb the charge in *neighbouring* rows and flip their bits, faster than refresh restores them. Researchers have used this to escalate privileges from unprivileged code. Mitigations include target row refresh (TRR) in the DRAM, DDR5's refresh management, and ECC, but none is perfect.

## Key takeaways
- Refresh timing and affected resources depend on the device and operating mode.
- The illustrative unavailable-time fraction divides blocking duration by interval.

## Further reading
- [Micron: DDR5 features and refresh](https://www.micron.com/products/memory/dram-components/ddr5-sdram)
- [Intel: Data-dependent prefetcher](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/data-dependent-prefetcher.html?source=study)
- [GCC: Prefetch builtin semantics](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html)
- [Dynamic random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_random-access_memory)
- [Memory timings — Wikipedia](https://en.wikipedia.org/wiki/Memory_timings)
- [DDR5 SDRAM — Wikipedia](https://en.wikipedia.org/wiki/DDR5_SDRAM)
- [Memory part 1: RAM, Ulrich Drepper (LWN)](https://lwn.net/Articles/250967/)
- [Memory part 4: NUMA support, Ulrich Drepper (LWN)](https://lwn.net/Articles/254445/)
- [NUMA memory policy — Linux kernel docs](https://docs.kernel.org/admin-guide/mm/numa_memory_policy.html)
- [numactl(8) — Linux manual page](https://man7.org/linux/man-pages/man8/numactl.8.html)
- [Cache prefetching — Wikipedia](https://en.wikipedia.org/wiki/Cache_prefetching)
- [Row hammer — Wikipedia](https://en.wikipedia.org/wiki/Row_hammer)
