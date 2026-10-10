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

- A **memory channel** is an independent bus with its own controller logic. More channels means more bandwidth in parallel.
- A **DRAM rank** groups DRAM devices operated together. In the illustrated 64-data-bit DDR4 channel, eight ×8 (8-bit-wide) devices supply the data width; ECC may add bits. DDR5 DIMMs divide their data interface into sub-channels.
- Each chip has several **DRAM banks**, with counts depending on device width and generation; DDR5 configurations can have up to 32. Each bank has its own row buffer, so different banks can work on different rows at the same time.
- A **DRAM row** (sometimes called a page) is distinct from an operating-system page. Its aggregate byte size depends on device geometry and rank width; no universal row size is assumed here.

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

To turn a timing quoted in clock cycles into nanoseconds, divide the cycles by the clock frequency. The clock is half the data-transfer rate, which is where the 2,000 comes from:

```formula
t = N_cyc × 2,000 / R
t = 22 × 2,000 / 3,200
t = 13.75 ns
where
t: the timing in nanoseconds (ns)
N_cyc: the timing in memory clock cycles, e.g. CL = 22
R: the data-transfer rate in MT/s, e.g. 3,200 for DDR4-3200
MT/s: mega-transfers per second: millions of data transfers each second
2,000: 1,000 (to turn a frequency in millions per second into nanoseconds) × 2 (two transfers per clock)
ns: nanosecond, one billionth of a second
In words: a DDR4-3200 clock tick is 2,000 / 3,200 = 0.625 ns, so 22 ticks take 13.75 ns.
```

The rule holds for any DDR generation, because all of them make two transfers per clock. It converts the quoted minimum only; real loads add queueing and other delays.

### Worked example: hit, empty, conflict

Assume a DDR4-3200 timing configuration with CL, tRCD and tRP all equal to 22 clocks, so each is 13.75 ns. Add up the steps each case needs, from the table above:

```formula
t_hit = t_CL = 13.75 ns
t_empty = t_RCD + t_CL
t_empty = 13.75 + 13.75 = 27.5 ns
t_conf = t_RP + t_RCD + t_CL
t_conf = 3 × 13.75 = 41.25 ns
where
t_hit: time to first data for a row hit, in nanoseconds (ns)
t_empty: time to first data when no row is open
t_conf: time to first data when a different row is open (a row-buffer conflict)
t_CL: the CAS latency, read from an open row: 22 cycles = 13.75 ns
t_RCD: the activate (row-to-column) delay: 22 cycles = 13.75 ns
t_RP: the precharge time to close the old row: 22 cycles = 13.75 ns
ns: nanosecond, one billionth of a second
In words: a hit pays one step, an empty bank two, and a conflict three, so here a conflict takes three times as long as a hit.
```

In this simplified example, the command-to-first-data interval for a conflict is three times the hit interval. That is why controllers reorder queued requests to group hits to the same open row (FR-FCFS scheduling), and why two streams repeatedly accessing different rows of the same bank are slow.

These are simplified DRAM command intervals. A measured core load also includes cache lookups, interconnect traversal, controller scheduling and possible contention; its latency cannot be inferred from CL alone.

> [!tip] Faster MT/s is not always lower latency
> DDR4-3200 CL16 and DDR4-3600 CL18 both work out to **10 ns** of CAS latency (calculation below). A higher CL number at a higher data-transfer rate can be the same latency, with more bandwidth.

```formula
t = N_cyc × 2,000 / R
t = 16 × 2,000 / 3,200 = 10 ns
t = 18 × 2,000 / 3,600 = 10 ns
where
t: the CAS latency in nanoseconds (ns)
N_cyc: the CAS latency in clock cycles (the CL number)
R: the data-transfer rate in MT/s
MT/s: mega-transfers per second
2,000: 1,000 (millions per second to nanoseconds) × 2 (two transfers per clock)
ns: nanosecond, one billionth of a second
In words: more cycles at a proportionally faster clock take the same time.
```

## Bandwidth maths

The most data a channel can ever move is one bus-width of bytes per transfer, times the number of transfers each second:

```formula
BW = R × W_bus
BW = 3,200 M/s × 8 B
BW = 25,600 MB/s = 25.6 GB/s
BW_2 = 2 × 25.6 = 51.2 GB/s
where
BW: peak bandwidth of one channel, in gigabytes per second (GB/s)
R: the data-transfer rate; DDR4-3200 makes 3,200 million (M) transfers per second
W_bus: the bus width in bytes; a 64-bit channel moves 8 bytes (B) per transfer
BW_2: peak bandwidth of two channels (dual channel)
M: mega, a million
B: byte, 8 bits
MB/s: megabytes (millions of bytes) per second
GB/s: gigabytes per second; here GB is 10^9 bytes, as memory vendors use
In words: 3.2 billion transfers a second of 8 bytes each is 25.6 GB/s; a second channel doubles it.
```

This is a ceiling: refresh, row-buffer conflicts, bus turnarounds and too few requests in flight keep real programs below it. A 64-byte line is one **DRAM burst** of 8 transfers of 8 bytes (BL8). Two transfers happen per clock, so that is 4 clocks of 0.625 ns, or 2.5 ns of bus time on DDR4-3200.

A conventional **DDR5 DIMM** splits its 64-bit data interface into **two independent 32-bit sub-channels**, excluding additional ECC bits, each using bursts of 16 (BL16 × 4 B = 64 B, still one line). Two narrower channels give the controller more parallelism.

The same peak-bandwidth formula applies, counting both sub-channels together as 8 bytes per transfer:

```formula
BW = R × W_bus
BW = 4,800 M/s × 8 B = 38.4 GB/s
BW_s = N_ch × BW
BW_s = 12 × 38.4 = 460.8 GB/s
where
BW: peak bandwidth of one DDR5-4800 DIMM channel, in GB/s
R: the data-transfer rate, 4,800 million (M) transfers per second
W_bus: bytes per transfer across both 32-bit sub-channels: 8 bytes (B)
BW_s: peak bandwidth of the whole CPU socket
N_ch: the number of memory channels, 12 in this hypothetical CPU socket
M: mega, a million
B: byte, 8 bits
GB/s: gigabytes (10^9 bytes) per second
In words: one DDR5-4800 DIMM peaks at 38.4 GB/s, and twelve channels at 460.8 GB/s.
```

DDR5 devices add on-die ECC, while conventional DDR5 DIMMs include on-module power management; bank counts depend on device geometry. On-die ECC protects internal storage and does not replace end-to-end memory-system ECC. For the **example** DDR5-4800 CL40, CAS latency is about 16.7 ns (40 × 2,000 / 4,800, using the conversion formula above) versus the example DDR4-3200 CL22's 13.75 ns. These two configurations do not establish a universal latency ordering between generations.

## Little's law: requests in flight

Peak bandwidth is only reached if enough requests are **in flight** at once. Little's law, from queueing theory, says that in a steady state the number of items inside a system equals the rate they flow through it times how long each stays. Rearranged for memory:

```formula
BW = Q / L
Q = N_req × B_line
where
BW: the sustained bandwidth, in bytes per nanosecond (B/ns); 1 B/ns = 1 GB/s
Q: bytes in flight: data requested but not yet returned, in bytes (B)
N_req: the number of outstanding requests
B_line: bytes per request, 64 for one cache line
L: the average time each request stays outstanding (its latency), in nanoseconds (ns)
B: byte, 8 bits
ns: nanosecond, one billionth of a second
GB/s: gigabytes (10^9 bytes) per second
In words: you can only receive as many bytes per nanosecond as you have waiting, divided by how long each wait lasts.
```

It applies to averages over a steady period, not to single requests. As an illustrative demand-request limit, assume 12 outstanding 64-byte transfers with a steady-state average residency of 80 ns:

```formula
Q = 12 × 64 B = 768 B
BW = 768 B / 80 ns = 9.6 B/ns
BW = 9.6 GB/s
where
Q: bytes in flight, in bytes (B)
BW: the sustained bandwidth
B/ns: bytes per nanosecond, the same as GB/s
B: byte, 8 bits
ns: nanosecond
GB/s: gigabytes (10^9 bytes) per second
In words: twelve 64-byte requests, each taking 80 ns, deliver at most 9.6 GB/s.
```

Turned round, the law says how many requests a target bandwidth needs:

```formula
Q = BW × L
Q = 51.2 B/ns × 80 ns = 4,096 B
N_req = 4,096 B / 64 B = 64
where
Q: bytes that must be in flight, in bytes (B)
BW: the target bandwidth: 51.2 GB/s = 51.2 B/ns (dual-channel DDR4-3200)
L: the average request latency, 80 ns
N_req: the number of 64-byte line requests outstanding
B/ns: bytes per nanosecond, the same as GB/s
B: byte, 8 bits
ns: nanosecond
In words: to fill 51.2 GB/s at 80 ns per request you need 64 lines in flight at all times.
```

So at 51.2 GB/s and an 80 ns average request residency you need **64 lines in flight**. The hypothetical 12-request limit cannot sustain that rate by itself. Actual limits and prefetch queues are implementation-specific. One strictly dependent cold pointer chain can expose only one next demand address at a time: with the assumed 80 ns per line, it moves one 64-byte line per 80 ns, which is 0.8 GB/s of line traffic. Useful pointer-byte throughput is lower, and other chains or hardware speculation can create additional requests.

## Refresh

DRAM retention requires periodic refresh; the interval, blocking time, temperature rules and supported modes are part-specific. For an **illustrative all-bank refresh model**, assume one operation every 7,812.5 ns, blocking the rank for 350 ns. The share of time lost is the blocked time divided by the interval:

```formula
f_ref = t_RFC / t_REFI
f_ref = 350 ns / 7,812.5 ns
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

DDR5 **same-bank refresh** targets one selected bank **in each bank group**, allowing other banks to remain available subject to timing constraints. It is not a refresh of only one bank in the entire device. A demand request can still be delayed by refresh.



> [!warning] Row hammer
> Activating one row very rapidly can disturb the charge in *neighbouring* rows and flip their bits, faster than refresh restores them. Researchers have used this to escalate privileges from unprivileged code. Mitigations include target row refresh (TRR) in the DRAM, DDR5's refresh management, and ECC, but none is perfect.

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



### Worked example: average latency

For a hypothetical workload with local 90 ns, remote 140 ns, and a quarter of accesses remote:

The average is a weighted mix: each latency counts in proportion to how often it happens.

```formula
L_avg = (1 − p) × L_loc + p × L_rem
L_avg = 0.75 × 90 + 0.25 × 140
L_avg = 67.5 + 35 = 102.5 ns
where
L_avg: the average memory latency, in nanoseconds (ns)
p: the fraction of accesses that go to remote memory; here 0.25
L_loc: the latency of a local-memory access, 90 ns
L_rem: the latency of a remote-memory access, 140 ns
ns: nanosecond, one billionth of a second
In words: three quarters of accesses at 90 ns and one quarter at 140 ns average 102.5 ns.
```

If all were remote: 140 ns, which is 140 / 90 ≈ 1.56 times the all-local figure, or 56% worse. The model assumes fixed latencies; in reality remote latency rises when the inter-socket link is busy.

### First touch

Under Linux's default local allocation policy, a newly faulted writable anonymous page is normally allocated near the CPU taking the fault, subject to allowed nodes, free memory and fallback. `malloc` may return **already backed** reused storage, so calling or writing through it does not necessarily cause a new allocation. Placement can also change through migration or automatic NUMA balancing. For the following example, assume fresh untouched pages, a pinned initialising thread, sufficient local memory, and no policy override or migration:

```c
double *a = malloc(n * sizeof *a);
for (size_t i = 0; i < n; i++)
    a[i] = 0.0;   /* main thread */
/* ...then 64 threads on 2 sockets
   each process a slice of a[] */
```

Under those assumptions, initial page faults place the pages on the main thread's node. Workers on another node then reach remote memory when accesses miss the cache hierarchy; hits in a core's own caches are not remote DRAM accesses.

Fixes:

- **Parallel first touch**: initialise newly allocated, unbacked slices with the workers that will later process them, pinned appropriately. Re-zeroing already placed pages does not by itself relocate them.
- **Pin** threads and memory: `numactl --cpunodebind=0 --membind=0 ./app`, or `taskset` plus `mbind`/`set_mempolicy` from libnuma.
- **Interleave**: `numactl --interleave=all` spreads pages round-robin. This can balance placement for large shared structures, but does not guarantee equal access latency or eliminate bandwidth hotspots.
- **Automatic NUMA balancing** (`kernel.numa_balancing`) migrates pages towards the threads that use them, at the cost of page faults to sample accesses.

Some database and managed-runtime configurations expose NUMA options. Collector/version-specific JVM behaviour is not detailed here because the necessary configuration-specific verification is unavailable.

## Prefetching: hiding the latency

A prefetch fetches a line **before** the demand load asks for it. Done well, a 100 ns miss becomes an L1 or L2 hit.

### Hardware prefetchers

Depending on the processor, engines may detect adjacent lines, sequential streams or constant strides associated with a load instruction. Their triggering, how far ahead they run, target cache and page-crossing behaviour vary.

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

The prefetch must be issued early enough that the data arrives by the time the loop reaches it. With a constant cost per iteration, an initial **prefetch-distance estimate** is:

```formula
D = ⌈L_mem / t_iter⌉
D = ⌈100 ns / 5 ns⌉ = 20
where
D: the prefetch distance: how many iterations ahead to prefetch
L_mem: the memory latency to hide, in nanoseconds (ns); 100 ns assumed
t_iter: the time one loop iteration takes, in ns; 5 ns assumed
⌈ ⌉: ceiling: round up to the next whole number
ns: nanosecond, one billionth of a second
In words: if a miss takes as long as 20 iterations, ask for the data 20 iterations before you need it.
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
- Convert timings to nanoseconds by multiplying the cycle count by 2,000 and dividing by the MT/s rating; DDR4-3200 CL22 is 13.75 ns.
- A 64-bit channel's peak bandwidth is its MT/s rating times 8 bytes (25.6 GB/s for DDR4-3200); reaching it needs many misses in flight (Little's law).
- Refresh blocks affected resources for part-specific intervals and can delay demand requests.
- NUMA placement matters when reaching DRAM. Under suitable allocation/policy conditions, parallel first touch can place fresh pages near their users; verify actual placement.
- Prefetch capabilities vary. A software prefetch distance of roughly the memory latency divided by the iteration time is an initial model, and safe address evaluation remains required.

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
