---
id: par-roofline-investigation
title: Using rooflines, reuse and request concurrency
level: advanced
minutes: 4
sourceLesson: par-measuring
summary: Keep arithmetic intensity and bandwidth on the same byte convention.
---

### Using the roofline

1. **Plot the compute kernel.** Measure its FLOPs and DRAM bytes (with counters, or tools such as Intel Advisor or NVIDIA Nsight Compute, which draw rooflines for you) and its achieved GFLOP/s.
2. **Find the roof above it.** That is your ceiling for this algorithm.
3. **Investigate the gap.** If measured bandwidth is saturated, reduce traffic or improve useful reuse. If arithmetic resources are limiting, investigate instruction choice and independent work. SIMD, threads or fusion can affect several resources; smaller types and FMA must satisfy numerical requirements. Measure again after a change.

Real rooflines add lower **roofline ceilings**: peak without SIMD, peak without FMA, bandwidth from a single core. They also add rooflines per memory level (L1, L2, L3, DRAM), because a compute kernel's AI against DRAM can be much higher than against L1.

> [!tip] Calibrate a consistent bandwidth model
> Measure bandwidth using a relevant access pattern, for example STREAM. STREAM reports useful array bytes, which may differ from physical DRAM bytes because of write allocation. Use the same byte convention for AI and B; do not multiply a physical-traffic intensity by an incompatible useful-bandwidth figure. A compute ceiling also requires the actual sustained instruction issue rate and clock, not just a count of FMA units.

### Concurrency and memory bandwidth

Little’s law, from queueing theory, says the average amount of data in flight equals byte throughput times average residence time. At a hypothetical 100 GB/s and 100 ns:

```formula
D = R × t_res
D = 100 × 10^9 B/s × 100 × 10^-9 s
D = 10,000 B
N_req = D / L_line = 10,000 B / 64 B
N_req = 156.25
where
D: the average bytes in flight: requested but not yet delivered, in bytes (B)
R: the sustained bandwidth, in bytes per second (B/s); 100 GB/s here
t_res: the average time each request is outstanding, in seconds (s); 100 ns here
N_req: the average number of 64-byte line requests in flight
L_line: the size of one request, a 64-byte cache line
B: byte, 8 bits
s: second; 1 ns = 10^-9 s
In words: to sustain 100 GB/s when each request takes 100 ns, about 10 KB, or 156 cache-line requests, must be in flight at once.
```

So at least 157 whole request slots would be needed to accommodate that amount simultaneously. A core’s demand queues, prefetchers and lower-level memory resources affect available concurrency. Some workloads saturate bandwidth with one core; others require several. No universal L1 miss-buffer count or core threshold applies.

## Pitfalls

- **Counting the wrong bytes.** AI from the source code ("I read two arrays") ignores write-allocate, cache reuse and prefetching. Measure traffic where you can.
- **Peak FLOP/s for the wrong precision.** Peak depends on precision, instruction shape and the selected device; use the matching rate.
- **Optimising the wrong thing.** Changing an arithmetic ceiling alone cannot raise a fixed saturated-bandwidth ceiling; the real implementation may also change concurrency or traffic.
- **Profiling a different program.** Debug builds, tiny inputs and an idle laptop on battery all behave differently from production.

> [!note] Evidence limits
> A universal perf sampling default, PMU overhead figure and CPU miss-buffer count is omitted because these depend on tool version, permissions, processor and workload and were not reliably established for a single stated target.

## Key takeaways
- Keep arithmetic intensity and bandwidth on the same byte convention.
- Useful concurrency, traffic reduction and numerical correctness all need measurement.

## Further reading
- [Little’s original queueing-law paper](https://fisherp.scripts.mit.edu/wordpress/wp-content/uploads/2015/11/ContentServer.pdf)
- [The original Roofline paper](https://people.eecs.berkeley.edu/~kubitron/cs252/handouts/papers/RooflineVyNoYellow.pdf)
- [Python timeit measurement contract](https://docs.python.org/3/library/timeit.html)
- [Linux perf stat reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-stat.txt)
- [Linux perf record reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-record.txt)
- [Flame graphs from their creator](https://www.brendangregg.com/flamegraphs.html)
- [STREAM traffic conventions](https://www.cs.virginia.edu/stream/ref.html)
- [Python Linux perf integration](https://docs.python.org/3/howto/perf_profiling.html)
