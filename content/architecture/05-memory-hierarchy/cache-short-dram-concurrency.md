---
id: cache-short-dram-concurrency
title: Keep enough memory requests in flight
level: advanced
minutes: 4
sourceLesson: cache-arch-dram
summary: Little’s law relates steady-state request residency to throughput and bytes in flight.
---

This unit builds on the earlier cache lessons and focuses on keep enough memory requests in flight. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Little's law: requests in flight

Peak bandwidth is only reached if enough requests are in flight at once. Little's law, from queueing theory, says that in a steady state the number of items inside a system equals the rate they flow through it times how long each stays. Rearranged for memory:

```formula
BW = Q / L
Q = N_req B_line
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
BW = 768 B / (80 ns) = 9.6 B/ns
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
Q = BW L
Q = 51.2 B/ns × 80 ns = 4,096 B
N_req = 4,096 B / (64 B) = 64
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

So at 51.2 GB/s and an 80 ns average request residency you need 64 lines in flight. The hypothetical 12-request limit cannot sustain that rate by itself. Actual limits and prefetch queues are implementation-specific. One strictly dependent cold pointer chain can expose only one next demand address at a time: with the assumed 80 ns per line, it moves one 64-byte line per 80 ns, which is 0.8 GB/s of line traffic. Useful pointer-byte throughput is lower, and other chains or hardware speculation can create additional requests.

## Key takeaways
- Little’s law relates steady-state request residency to throughput and bytes in flight.
- One dependent cold chain exposes fewer independent demand requests than a concurrent stream.

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
