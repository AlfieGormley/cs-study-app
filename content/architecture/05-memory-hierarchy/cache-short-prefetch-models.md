---
id: cache-short-prefetch-models
title: Prefetch safely and choose a lead distance
level: advanced
minutes: 4
sourceLesson: cache-arch-dram
summary: Hardware pattern capabilities and page crossing are engine-specific.
---

This unit builds on the earlier cache lessons and focuses on prefetch safely and choose a lead distance. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Prefetching: hiding demand latency

A prefetch fetches a line before the demand load asks for it. A timely, retained prefetch can turn a later demand miss into an L1 or L2 hit; it does not eliminate the earlier transfer cost.

## Hardware prefetchers

Depending on the processor, engines may detect adjacent lines, sequential streams or constant strides associated with a load instruction. Their triggering, how far ahead they run, target cache and page-crossing behaviour vary.

Conventional stream/stride predictors struggle with irregular indirection. However, it is false that all hardware prefetchers are unable to use indirect data: Intel documents a **data-dependent prefetcher** that can use loaded values to predict addresses in supported patterns. That feature is not an unrestricted recursive pointer-chasing engine. Likewise, a universal “all prefetchers stop at 4 KiB boundaries” rule is incorrect; translation and boundary handling are engine-specific.

## Software prefetching

For irregular but *computable* addresses, you can issue the prefetch yourself. GCC and Clang provide `__builtin_prefetch`:

```c
#define D 16  /* prefetch distance */
for (size_t i = 0; i < n; i++) {
    // Check the future index before use.
    if (n - i > D)
        __builtin_prefetch(
            &table[idx[i + D]]);
    // The demand load computes the sum.
    sum += table[idx[i]];
}
```

Assume every index used here is in bounds for `table`, `idx` contains at least n entries, and sum arithmetic is valid. A prefetch hint may be ignored, but evaluating its address must still be valid.

The prefetch must be issued early enough that the data arrives by the time the loop reaches it. With a constant cost per iteration, an initial **prefetch-distance estimate** is:

```formula
D = ⌈L_mem / t_iter⌉
D = ⌈100 ns / (5 ns)⌉ = 20
where
D: the prefetch distance: how many iterations ahead to prefetch
L_mem: the memory latency to hide, in nanoseconds (ns); 100 ns assumed
t_iter: the time one loop iteration takes, in ns; 5 ns assumed
⌈ ⌉: ceiling: round up to the next whole number
ns: nanosecond, one billionth of a second
In words: if a miss takes as long as 20 iterations, ask for the data 20 iterations before you need it.
```

With assumed 100 ns latency and 5 ns per iteration, a lead of 20 iterations is a starting estimate. Actual latency, issue overhead, resource limits and evictions determine whether it hides the miss. Too small and the data arrives late; too large and it may be evicted before use, or waste fill buffers.

## When prefetching hurts

- **Cache pollution**: prefetched lines that are never used evict useful ones.
- Bandwidth waste: on a memory-bound multi-threaded workload, useless prefetches steal bandwidth from demand misses. Some firmware configuration interfaces expose controls for individual prefetchers; whether disabling one helps depends on the measured workload.
- Overhead: software prefetches are instructions too; in a loop that is already compute-bound they only cost.

## Putting it together

Some practical consequences:

- A sufficiently concurrent streaming loop can become bandwidth-limited. Too few outstanding requests or substantial computation can prevent this. Measure achieved GB/s.
- A strictly dependent, cache-missing **pointer chain** is often latency-limited: one next demand address at a time. Restructure the data (arrays, B-trees), or interleave several independent chases so their misses overlap.
- On **multi-socket** machines, check `numastat` and placement before blaming the code.
- Bandwidth is shared. Several cores streaming at once can saturate the channels before exhausting arithmetic resources; adding threads to a memory-bound loop stops helping once DRAM is full.

## Key takeaways
- Hardware pattern capabilities and page crossing are engine-specific.
- Software hints need valid address evaluation and a useful lead distance without excessive pollution or overhead.

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
