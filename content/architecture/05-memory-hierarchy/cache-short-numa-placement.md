---
id: cache-short-numa-placement
title: Place fresh pages near their users
level: advanced
minutes: 4
sourceLesson: cache-arch-dram
summary: NUMA nodes and CPU sockets need not correspond one-to-one.
---

This unit builds on the earlier cache lessons and focuses on place fresh pages near their users. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## NUMA: not all DRAM is equally far

In a multi-socket server, each CPU socket has its own memory controllers and DRAM. A core can reach the other CPU socket's memory, but only over the inter-socket link (Intel UPI, AMD Infinity Fabric). This is **non-uniform memory access**.

```
 +---------+   UPI    +---------+
 | socket0 |<-------->| socket1 |
 | cores   |          | cores   |
 | MC      |          | MC      |
 +----+----+          +----+----+
      |                    |
   node 0 DRAM          node 1 DRAM
   local memory        remote memory
```

Remote access can add interconnect delay and encounter link-bandwidth limits. A universal local/remote latency ratio is absent because a specific measured topology is not established here. `numactl --hardware` reports node memory and relative distance values; these are not nanoseconds. A CPU socket can expose multiple NUMA nodes, and a NUMA node need not correspond one-to-one with a CPU socket.

## Worked example: average latency

For a hypothetical workload with local 90 ns, remote 140 ns, and a quarter of accesses remote:

The average is a weighted mix: each latency counts in proportion to how often it happens.

```formula
L_avg = (1 − p)L_loc + p L_rem
L_avg = 0.75 × 90 ns + 0.25 × 140 ns
L_avg = 67.5 ns + 35 ns = 102.5 ns
where
L_avg: the average memory latency, in nanoseconds (ns)
p: the fraction of accesses that go to remote memory; here 0.25
L_loc: the latency of a local-memory access, 90 ns
L_rem: the latency of a remote-memory access, 140 ns
ns: nanosecond, one billionth of a second
In words: three quarters of accesses at 90 ns and one quarter at 140 ns average 102.5 ns.
```

If every access were remote, the average would be 140 ns, about 1.56 times the all-local figure, or about 56% higher latency. The model assumes fixed latencies; in reality remote latency rises when the inter-socket link is busy.

## First touch

Under Linux's default local allocation policy, a newly faulted writable anonymous page is normally allocated near the CPU taking the fault, subject to allowed nodes, free memory and fallback. `malloc` may return already backed reused storage, so calling or writing through it does not necessarily cause a new allocation. Placement can also change through migration or automatic NUMA balancing. For the following example, assume fresh untouched pages, a pinned initialising thread, sufficient local memory, and no policy override or migration:

```c
// Allocation/initialisation sketch.
// A complete caller checks size and malloc.
double *a = malloc(n * sizeof *a);
for (size_t i = 0; i < n; i++)
    // A first write may allocate a page.
    a[i] = 0.0;   /* main thread */
/* ...then 64 threads on 2 sockets
   each process a slice of a[] */
```

Under those assumptions, initial page faults place the pages on the main thread's node. Workers on another node then reach remote memory when accesses miss the cache hierarchy; hits in a core's own caches are not remote DRAM accesses.

Fixes:

- **Parallel first touch**: initialise newly allocated, unbacked slices with the workers that will later process them, pinned appropriately. Re-zeroing already placed pages does not by itself relocate them.
- Pin threads and memory: `numactl --cpunodebind=0 --membind=0 ./app`, or `taskset` plus `mbind`/`set_mempolicy` from libnuma.
- Interleave: `numactl --interleave=all` spreads pages round-robin. This can balance placement for large shared structures, but does not guarantee equal access latency or eliminate bandwidth hotspots.
- **Automatic NUMA balancing** (`kernel.numa_balancing`) migrates pages towards the threads that use them, at the cost of page faults to sample accesses.

Some database and managed-runtime configurations expose NUMA options. Collector/version-specific JVM behaviour is not detailed here because the necessary configuration-specific verification is unavailable.

## Key takeaways
- NUMA nodes and CPU sockets need not correspond one-to-one.
- First-touch placement requires fresh unbacked pages, suitable policy, allowed nodes and sufficient memory.

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
