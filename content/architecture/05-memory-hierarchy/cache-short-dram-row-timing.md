---
id: cache-short-dram-row-timing
title: Row hits, conflicts and clock timings
level: advanced
minutes: 5
sourceLesson: cache-arch-dram
summary: A simplified command path distinguishes an open-row hit, an empty bank and a conflicting row.
---

This unit builds on the earlier cache lessons and focuses on row hits, conflicts and clock timings. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## The three cases of an access

Each bank's DRAM row buffer retains an activated row. The table gives simplified command-to-first-data minima, assuming precharge is already legal, the command bus is available, and all other timing constraints are satisfied. Queueing, transfer completion and earlier operations can add delay:

| Case | Commands | Cost |
|---|---|---|
| Row hit | READ | CL |
| Row empty | ACT, READ | tRCD + CL |
| Row conflict | PRE, ACT, READ | tRP + tRCD + CL |

- **CL** (CAS latency): column read from an open row to first data.
- **tRCD**: minimum delay from row activation (ACT) to a column command such as READ, while sensing and restoration proceed.
- **tRP**: precharge time to close the row and prepare/equalise the bit lines for another activation. Cell restoration occurs while the row is active.

Timings are quoted in clock cycles, as in "DDR4-3200 CL22-22-22". To convert to nanoseconds you need the clock. DDR means **double data rate**: two transfers per clock. So DDR4-3200 runs 3,200 mega-transfers per second (MT/s) on a 1,600 MHz clock, and one clock is 0.625 ns.

To turn a timing quoted in clock cycles into nanoseconds, divide the cycles by the clock frequency. The clock is half the data-transfer rate, which is where the 2,000 comes from:

```formula
t = N_cyc × 2,000 / R
t = (22 × 2,000 / 3,200) ns
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

## Worked example: hit, empty, conflict

Assume a DDR4-3200 timing configuration with CL, tRCD and tRP all equal to 22 clocks, so each is 13.75 ns. Add up the steps each case needs, from the table above:

```formula
t_hit = t_CL = 13.75 ns
t_empty = t_RCD + t_CL
t_empty = 13.75 ns + 13.75 ns
t_empty = 27.5 ns
t_conf = t_RP + t_RCD + t_CL
t_conf = 3 × 13.75 ns = 41.25 ns
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
> DDR4-3200 CL16 and DDR4-3600 CL18 both work out to 10 ns of CAS latency (calculation below). A higher CL number at a higher data-transfer rate can be the same latency, with more bandwidth.

```formula
t = N_cyc × 2,000 / R
t = (16 × 2,000 / 3,200) ns = 10 ns
t = (18 × 2,000 / 3,600) ns = 10 ns
where
t: the CAS latency in nanoseconds (ns)
N_cyc: the CAS latency in clock cycles (the CL number)
R: the data-transfer rate in MT/s
MT/s: mega-transfers per second
2,000: 1,000 (millions per second to nanoseconds) × 2 (two transfers per clock)
ns: nanosecond, one billionth of a second
In words: more cycles at a proportionally faster clock take the same time.
```

## Key takeaways
- A simplified command path distinguishes an open-row hit, an empty bank and a conflicting row.
- DDR clock-cycle timings convert to time using half the data-transfer rate.

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
