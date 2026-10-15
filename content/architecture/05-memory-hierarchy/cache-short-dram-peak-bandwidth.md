---
id: cache-short-dram-peak-bandwidth
title: Compute DDR channel bandwidth
level: advanced
minutes: 4
sourceLesson: cache-arch-dram
summary: Peak data bandwidth is transfers per second times bytes per transfer.
---

This unit builds on the earlier cache lessons and focuses on compute ddr channel bandwidth. Keep each example’s stated hardware geometry and model assumptions when applying its result.

DDR means two data transfers per memory clock. Here bandwidth counts data bytes, excluding ECC overhead, and uses decimal gigabytes. Command scheduling and transfer rate are separate from end-to-end core-load latency.

## Bandwidth maths

The most data a channel can ever move is one bus-width of bytes per transfer, times the number of transfers each second:

```formula
BW = R W_bus
BW = 3,200 M/s × 8 B
BW = 25,600 MB/s = 25.6 GB/s
BW_2 = 2 × 25.6 GB/s = 51.2 GB/s
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

A conventional **DDR5 DIMM** splits its 64-bit data interface into two independent 32-bit sub-channels, excluding additional ECC bits, each using bursts of 16 (BL16 × 4 B = 64 B, still one line). Two narrower channels give the controller more parallelism.

The same peak-bandwidth formula applies, counting both sub-channels together as 8 bytes per transfer:

```formula
BW = R W_bus
BW = 4,800 M/s × 8 B = 38.4 GB/s
BW_s = N_ch BW
BW_s = 12 × 38.4 GB/s = 460.8 GB/s
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

DDR5 devices add on-die ECC, while conventional DDR5 DIMMs include on-module power management; bank counts depend on device geometry. On-die ECC protects internal storage and does not replace end-to-end memory-system ECC. For an example DDR5-4800 CL40 timing, CAS latency is about 16.7 ns, versus the example DDR4-3200 CL22 timing’s 13.75 ns. The preceding timing unit defines the conversion; the extra worked card below repeats it locally. These two configurations do not establish a universal latency ordering between generations.

```formula
t_CAS = (40 × 2,000 / 4,800) ns
t_CAS ≈ 16.7 ns
where
t_CAS: CAS latency for the illustrative DDR5-4800 CL40 configuration, in nanoseconds
2,000: conversion factor for two transfers per clock and a transfer rate expressed in millions per second
ns: nanosecond, one billionth of a second
≈: approximately equal to, rounded
In words: forty memory clocks at 4,800 million transfers per second take about 16.7 nanoseconds; this is not complete load latency.
```

## Key takeaways
- Peak data bandwidth is transfers per second times bytes per transfer.
- DDR5 sub-channels improve scheduling opportunities without making peak bandwidth a measured result.

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
