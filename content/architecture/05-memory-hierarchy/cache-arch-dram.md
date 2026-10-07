---
id: cache-arch-dram
title: DRAM, NUMA and prefetching
level: advanced
minutes: 15
summary: What happens below the last-level cache - DRAM cells, banks and row buffers, timings and bandwidth maths, refresh, NUMA on multi-socket machines, and how hardware and software prefetching hide memory latency.
---

Earlier examples used assumed DRAM latencies to explain cache arithmetic. Below the last-level cache is a memory system with controllers, channels, ranks, banks and rows. Access latency depends on its state, traffic and placement. Streaming throughput benefits from overlapping requests, including useful prefetches; it is not guaranteed to reach peak bandwidth.

The numerical examples below are explicit models. Representative end-to-end latency and speedup figures are absent where the necessary processor, memory configuration and benchmark have not been reliably verified.



## The DRAM cell and why it is slow

A conventional DRAM cell uses **one transistor and one capacitor**. Information is represented by charge state; the mapping of charged/discharged to logical 1/0 can depend on cell organisation. That makes DRAM dense and cheap, but it has three consequences:

- **Reads are destructive.** Activation shares the cell's small charge with a bit line. A **sense amplifier** resolves the voltage difference and restores the cell while the row is active. This disturbs the stored charge; it is not simply a complete drain followed by restoration during precharge.
- **Cells leak.** Charge drains away in milliseconds, so every row must be **refreshed** (read and rewritten) periodically, whether or not anyone uses it.
- **Access is row-at-a-time.** The chip cannot read one bit cheaply. It opens a whole **row** (thousands of bits) into the sense amplifiers, called the **row buffer**, and then reads columns from it.

## Inside a DIMM: channels, ranks, banks, rows

The following is an **illustrative DDR4-style topology**, excluding ECC bits; actual widths, ranks, bank counts and address mapping vary.

```
 memory controller (on the CPU)
   |-- channel 0 (64-bit bus)
   |     |-- rank 0: 8 chips side by side
   |     |     |-- bank 0 .. bank 15
   |     |     |     rows x columns
   |     |     |     + 1 row buffer
   |     |-- rank 1 ...
   |-- channel 1 ...
```

- A **channel** is an independent bus with its own controller logic. More channels means more bandwidth in parallel.
- A **rank** groups DRAM devices operated together. In the illustrated 64-data-bit DDR4 channel, eight x8 devices supply the data width; ECC may add bits. DDR5 DIMMs divide their data interface into sub-channels.
- Each chip has several **banks**, with counts depending on device width and generation; DDR5 configurations can have up to 32. Each bank has its own row buffer, so different banks can work on different rows at the same time.
- A DRAM **row** (sometimes called a page) is distinct from an operating-system page. Its aggregate byte size depends on device geometry and rank width; no universal row size is assumed here.

The memory controller maps, and may hash, physical address bits to choose channel, rank, bank, row and column. Consecutive cache lines are usually spread across channels and banks so that a stream keeps them all busy.

## The three cases of an access

Each bank's row buffer retains an activated row. The table gives simplified command-to-first-data minima, assuming precharge is already legal, the command bus is available, and all other timing constraints are satisfied. Queueing, transfer completion and earlier operations can add delay:

| Case | Commands | Cost |
|---|---|---|
| Row hit | READ | CL |
| Row empty | ACT, READ | tRCD + CL |
| Row conflict | PRE, ACT, READ | tRP + tRCD + CL |

- **CL** (CAS latency): column read from an open row to first data.
- **tRCD**: activate a row (copy it into the row buffer).
- **tRP**: precharge time to close the row and prepare/equalise the bit lines for another activation. Cell restoration occurs while the row is active.

Timings are quoted in clock cycles, as in "DDR4-3200 CL22-22-22". To convert to nanoseconds you need the clock. DDR means **double data rate**: two transfers per clock. So DDR4-3200 runs 3,200 mega-transfers per second (MT/s) on a 1,600 MHz clock, and one clock is 0.625 ns.

```
 ns = cycles x 2,000 / (MT/s)

 DDR4-3200 CL22:
   22 x 2,000 / 3,200 = 13.75 ns
```

### Worked example: hit, empty, conflict

Assume a DDR4-3200 timing configuration with CL, tRCD and tRP all equal to 22 clocks:

```
 row hit      = 13.75 ns
 row empty    = 13.75 + 13.75 = 27.5 ns
 row conflict = 13.75 x 3     = 41.25 ns
```

In this simplified example, the command-to-first-data interval for a conflict is three times the hit interval. That is why controllers reorder queued requests to group hits to the same open row (FR-FCFS scheduling), and why two streams hammering different rows of the same bank are slow.

These are simplified DRAM command intervals. A measured core load also includes cache lookups, interconnect traversal, controller scheduling and possible contention; its latency cannot be inferred from CL alone.

> [!tip] Faster MT/s is not always lower latency
> DDR4-3200 CL16 and DDR4-3600 CL18 both give 16 × 2,000 / 3,200 = 18 × 2,000 / 3,600 = **10 ns**. A higher CL number at a higher data rate can be the same latency, with more bandwidth.

## Bandwidth maths

Peak bandwidth of a channel = transfers per second × bus width.

```
 DDR4-3200, 64-bit (8-byte) channel:
   3,200 M x 8 B = 25.6 GB/s
 dual channel:     51.2 GB/s
```

(GB here is 10^9 bytes, as memory vendors use.) A 64-byte line is one **burst** of 8 transfers of 8 bytes (BL8), taking 4 clocks = 2.5 ns of bus time on DDR4-3200.

A conventional **DDR5 DIMM** splits its 64-bit data interface into **two independent 32-bit sub-channels**, excluding additional ECC bits, each using bursts of 16 (BL16 × 4 B = 64 B, still one line). Two narrower channels give the controller more parallelism.

```
 DDR5-4800 DIMM: 4,800 M x 8 B = 38.4 GB/s
 hypothetical 12-channel socket:
   12 x 38.4 = 460.8 GB/s per socket
```

DDR5 devices add on-die ECC, while conventional DDR5 DIMMs include on-module power management; bank counts depend on device geometry. On-die ECC protects internal storage and does not replace end-to-end memory-system ECC. For the **example** DDR5-4800 CL40, CAS latency is about 16.7 ns versus the example DDR4-3200 CL22's 13.75 ns. These two configurations do not establish a universal latency ordering between generations.

## Little's law: requests in flight

Peak bandwidth is only reached if enough requests are **in flight** at once. Little's law says:

```
 bandwidth = bytes in flight / latency
```

As an illustrative demand-request limit, assume 12 outstanding 64-byte transfers with a steady-state average residency of 80 ns:

```
 12 x 64 B / 80 ns = 9.6 B/ns = 9.6 GB/s
```

At 51.2 GB/s and an 80 ns average request residency, Little's law gives **64 lines in flight**. The hypothetical 12-request limit cannot sustain that rate by itself. Actual limits and prefetch queues are implementation-specific. One strictly dependent cold pointer chain can expose only one next demand address at a time: with the assumed 80 ns per line, its line-transfer rate is 0.8 GB/s. Useful pointer-byte throughput is lower, and other chains or hardware speculation can create additional requests.

## Refresh

DRAM retention requires periodic refresh; the interval, blocking time, temperature rules and supported modes are part-specific. For an **illustrative all-bank refresh model**, assume one operation every 7,812.5 ns, blocking the rank for 350 ns:

```
 350 / 7,812.5 = 4.48% of the time
```

If that interval halves while the blocking duration stays fixed, the fraction doubles to 8.96%. A product-specific density/temperature timing table is absent because those exact operating modes have not been reliably verified here.

DDR5 **same-bank refresh** targets one selected bank **in each bank group**, allowing other banks to remain available subject to timing constraints. It is not a refresh of only one bank in the entire device. A demand request can still be delayed by refresh.



> [!warning] Row hammer
> Activating one row very rapidly can disturb the charge in *neighbouring* rows and flip their bits, faster than refresh restores them. Researchers have used this to escalate privileges from unprivileged code. Mitigations include target row refresh (TRR) in the DRAM, DDR5's refresh management, and ECC, but none is perfect.

## NUMA: not all DRAM is equally far

In a multi-socket server, each socket has its own memory controllers and DRAM. A core can reach the other socket's memory, but only over the inter-socket link (Intel UPI, AMD Infinity Fabric). This is **non-uniform memory access**.

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

Remote access can add interconnect delay and encounter link-bandwidth limits. A universal local/remote latency ratio is absent because a specific measured topology is not established here. `numactl --hardware` reports node memory and relative distance values; these are not nanoseconds. A socket can expose multiple NUMA nodes, and a NUMA node need not correspond one-to-one with a socket.



### Worked example: average latency

For a hypothetical workload with local 90 ns, remote 140 ns, and a quarter of accesses remote:

```
 0.75 x 90 + 0.25 x 140
 = 67.5 + 35 = 102.5 ns
```

If all were remote: 140 ns, 56% worse than all-local.

### First touch

Under Linux's default local allocation policy, a newly faulted writable anonymous page is normally allocated near the CPU taking the fault, subject to allowed nodes, available memory and fallback. `malloc` may return **already backed** reused storage, so calling or writing through it does not necessarily cause a new allocation. Placement can also change through migration or automatic NUMA balancing. For the following example, assume fresh untouched pages, a pinned initialising thread, sufficient local memory, and no policy override or migration:

```c
double *a = malloc(n * sizeof *a);
for (size_t i = 0; i < n; i++)
    a[i] = 0.0;   /* main thread */
/* ...then 64 threads on 2 sockets
   each process a slice of a[] */
```

Under those assumptions, initial page faults place the pages on the main thread's node. Workers on another node then reach remote memory when accesses miss the cache hierarchy; local cache hits are not remote DRAM accesses.

Fixes:

- **Parallel first touch**: initialise newly allocated, unbacked slices with the workers that will later process them, pinned appropriately. Re-zeroing already placed pages does not by itself relocate them.
- **Pin** threads and memory: `numactl --cpunodebind=0 --membind=0 ./app`, or `taskset` plus `mbind`/`set_mempolicy` from libnuma.
- **Interleave**: `numactl --interleave=all` spreads pages round-robin. This can balance placement for large shared structures, but does not guarantee equal access latency or eliminate bandwidth hotspots.
- **Automatic NUMA balancing** (`kernel.numa_balancing`) migrates pages towards the threads that use them, at the cost of page faults to sample accesses.

Some database and managed-runtime configurations expose NUMA options. Collector/version-specific JVM behaviour is not detailed here because the necessary configuration-specific verification is unavailable.

## Prefetching: hiding the latency

A prefetch fetches a line **before** the demand load asks for it. Done well, a 100 ns miss becomes an L1 or L2 hit.

### Hardware prefetchers

Depending on the processor, engines may detect adjacent lines, sequential streams or constant strides associated with a load instruction. Their triggering, lookahead, target cache and page-crossing behaviour vary.

Conventional stream/stride predictors struggle with irregular indirection. However, it is false that **all** hardware prefetchers are unable to use indirect data: Intel documents a **data-dependent prefetcher** that can use loaded values to predict addresses in supported patterns. That feature is not an unrestricted recursive pointer-chasing engine. Likewise, a universal “all prefetchers stop at 4 KiB boundaries” rule is incorrect; translation and boundary handling are engine-specific.



### Software prefetching

For irregular but *computable* addresses, you can issue the prefetch yourself. GCC and Clang provide `__builtin_prefetch`:

```c
#define D 16  /* prefetch distance */
for (size_t i = 0; i < n; i++) {
    if (n - i > D)
        __builtin_prefetch(
            &table[idx[i + D]]);
    sum += table[idx[i]];
}
```

Assume every index used here is in bounds for `table`, `idx` contains at least n entries, and sum arithmetic is valid. A prefetch hint may be ignored, but evaluating its address must still be valid.

An initial **prefetch-distance estimate** under constant per-iteration cost is:

```
 D = ceil(memory latency / time per iter)
```

With assumed 100 ns latency and 5 ns per iteration, D = 20 is a starting estimate. Actual latency, issue overhead, resource limits and evictions determine whether it hides the miss. Too small and the data arrives late; too large and it may be evicted before use, or waste fill buffers.

### When prefetching hurts

- **Cache pollution**: prefetched lines that are never used evict useful ones.
- **Bandwidth waste**: on a memory-bound multi-threaded workload, useless prefetches steal bandwidth from demand misses. That is why BIOS settings let you switch individual prefetchers off, and some HPC sites do.
- **Overhead**: software prefetches are instructions too; in a loop that is already compute-bound they only cost.

## Putting it together

Some practical consequences:

- A sufficiently concurrent **streaming** loop can become bandwidth-limited. Too few outstanding requests or substantial computation can prevent this. Measure achieved GB/s.
- A strictly dependent, cache-missing **pointer chain** is often latency-limited: one next demand address at a time. Restructure the data (arrays, B-trees), or interleave several independent chases so their misses overlap.
- On **multi-socket** machines, check `numastat` and placement before blaming the code.
- **Bandwidth is shared.** Several cores streaming at once saturate the channels long before they saturate the cores; adding threads to a memory-bound loop stops helping once DRAM is full.

## Key takeaways
- Conventional DRAM activates a row into sense amplifiers. With other constraints already satisfied, simplified first-data intervals are CL, tRCD + CL, or tRP + tRCD + CL.
- Convert timings with ns = cycles × 2,000 / MT/s; DDR4-3200 CL22 is 13.75 ns.
- Peak bandwidth = MT/s × 8 bytes per 64-bit channel (25.6 GB/s for DDR4-3200); reaching it needs many misses in flight (Little's law).
- Refresh blocks affected resources for part-specific intervals and can delay demand requests.
- NUMA placement matters when reaching DRAM. Under suitable allocation/policy conditions, parallel first touch can place fresh pages near their users; verify actual placement.
- Prefetch capabilities vary. Software prefetch distance ≈ latency / iteration time is an initial model, and safe address evaluation remains required.

## Further reading
- [Micron: DDR5 features and refresh](https://www.micron.com/products/memory/dram-components/ddr5-sdram)
- [Intel: Data-dependent prefetcher](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/data-dependent-prefetcher.html)
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
