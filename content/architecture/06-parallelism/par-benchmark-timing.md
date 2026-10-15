---
id: par-benchmark-timing
title: Timing a workload honestly
level: advanced
minutes: 3
sourceLesson: par-measuring
summary: Choose warm-up and timing statistics to match the objective.
---

Everything in this module so far, from SIMD lanes to GPU warps to systolic arrays, is a way to raise *peak* performance. Real programs rarely reach peak. The difference between "this chip can do 1 TFLOP/s" and "my loop does 4 GFLOP/s" is where performance engineering lives.

The rule is simple and constantly broken: **measure before you optimise**. Intuition about where time goes is wrong surprisingly often. This lesson covers three levels of measurement: timing a program honestly, asking the hardware what it was doing, and using the **roofline model** to know what is even possible.

## Level 1: timing, honestly

Wall-clock time is the number users feel, but it is noisy. A single run tells you little. Common traps:

- **Warm-up.** The first run pays for page faults, cold caches, lazy loading and, in JIT-compiled languages, compilation. Exclude warm-up only when measuring steady state; retain it when startup or cold-request latency is the objective.
- **Frequency scaling.** Turbo boost and thermal throttling can change the clock between runs. Long AVX-512 loops can lower it further. Benchmark on a quiet, fixed-frequency machine if you can.
- **Dead-code elimination.** If a benchmark's result is never used, an optimising compiler may delete the work entirely and report impossible speeds.
- **Noise.** Other processes, interrupts and memory placement (NUMA) add variance. Run many times and look at the spread, not one number.

In Python, use `time.perf_counter()` (a high-resolution monotonic clock, unlike `time.time()`) or the `timeit` module, which runs a snippet many times:

```python
import timeit

setup = "xs = list(range(100_000))"
# Five samples, each timing 100 calls.
t = timeit.repeat("sum(xs)", setup,
                  number=100, repeat=5)
# Divide a sample total by calls per sample.
print(min(t) / 100)  # seconds per call
```

The `timeit` docs recommend the minimum as a useful estimate with less added interference for a controlled microbenchmark when interference mainly adds delay. It is not a universal ‘true cost’: cache state, frequency, input and warm-up may change the work or execution conditions. Report the distribution when it matters, especially for user-facing latency. `timeit` disables garbage collection by default; enable it when collection is part of the workload being measured.

Timing tells you *how long*. It does not tell you *why*.

## Key takeaways
- Choose warm-up and timing statistics to match the objective.
- Prevent deleted work and report relevant variance and execution conditions.

## Further reading
- [The original Roofline paper](https://people.eecs.berkeley.edu/~kubitron/cs252/handouts/papers/RooflineVyNoYellow.pdf)
- [Python timeit measurement contract](https://docs.python.org/3/library/timeit.html)
- [Linux perf stat reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-stat.txt)
- [Linux perf record reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-record.txt)
- [Flame graphs from their creator](https://www.brendangregg.com/flamegraphs.html)
- [STREAM traffic conventions](https://www.cs.virginia.edu/stream/ref.html)
- [Python Linux perf integration](https://docs.python.org/3/howto/perf_profiling.html)
