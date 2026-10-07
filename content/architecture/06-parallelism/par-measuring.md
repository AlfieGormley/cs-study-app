---
id: par-measuring
title: Measuring performance: perf and the roofline model
level: advanced
minutes: 15
summary: How to benchmark honestly, read hardware counters with perf, find hot spots with sampling profilers, and use the roofline model to compare arithmetic and memory-bandwidth ceilings.
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
t = timeit.repeat("sum(xs)", setup,
                  number=100, repeat=5)
print(min(t) / 100)  # seconds per call
```

The `timeit` docs recommend the minimum as a useful lower-bound estimate for a controlled microbenchmark when interference mainly adds delay. It is not a universal ‘true cost’: cache state, frequency, input and warm-up may change the work or execution conditions. Report the distribution when it matters, especially for user-facing latency. `timeit` disables garbage collection by default; enable it when collection is part of the workload being measured.

Timing tells you *how long*. It does not tell you *why*.

## Level 2: hardware performance counters

Many processors provide a **performance monitoring unit** (PMU) for events such as cycles, retired instructions and cache or branch events. Linux `perf` can access supported events when permissions and the execution environment allow it. Available events, semantics and overhead depend on the processor, kernel, virtualisation and configuration; counters are not universally accessible.

### Counting with `perf stat`

```
$ perf stat -e cycles,instructions,\
  cache-misses,branch-misses ./app

 4,012,000,000  cycles
 2,808,000,000  instructions # 0.70 IPC
    61,000,000  cache-misses
     3,100,000  branch-misses

   1.35 s elapsed
```

(Illustrative numbers.) The most useful single derived figure is **IPC**, instructions per cycle:

```
IPC = 2.808e9 / 4.012e9 = 0.70
```

IPC below a core’s maximum retirement width does not identify the cause. Serial arithmetic dependencies, long-latency execution units, instruction-to-micro-op expansion, memory delays, frontend limits and speculation can all contribute. Architectural instructions are not identical to issue slots. Even high IPC can reflect unnecessary work; measure useful completed results.

`perf stat -r 10` repeats the run and reports variation. This helps describe variability but does not remove warm-up, placement or workload bias.

### Where does the time go? Top-down analysis

Raw counters are hard to interpret: is 61 million cache misses a lot? Intel's **top-down microarchitecture analysis** attributes pipeline *slots* using model-specific metrics. The top-level categories are:

| Category | Meaning |
|---|---|
| Retiring | Slots attributed to retiring work, not necessarily algorithmically useful |
| Bad speculation | Work thrown away |
| Frontend bound | Fetch/decode starved |
| Backend bound | Waiting on memory or units |

Backend bound splits further into *memory bound* and *core bound*. On supported CPUs, `perf stat --topdown` prints this breakdown. Use the largest categories to guide investigation, then compare achievable total-time savings. A slot percentage is not an elapsed-time fraction or a guaranteed speedup bound.

### Finding hot spots with `perf record`

Counting aggregates events; **sampling** associates selected events with locations in the program. For example:

```
$ perf record -g ./app
$ perf report
```

Choose and record the event and sampling settings. Samples taken from cycles are weighted toward cycles, not necessarily wall time, and the default event can depend on availability. Call-stack quality requires suitable unwinding support, symbols and build configuration. Overhead and statistical precision depend on frequency, event support and workload; sample locations may skid from the causative instruction.

Brendan Gregg’s **flame graphs** show aggregated stack samples. Rectangle width represents inclusive sample weight; stack depth is vertical and horizontal ordering is **not a timeline**. The selected event determines what that weight means. A supported Linux build of Python 3.12 or later can expose Python names to `perf` with `python -X perf`; check its build and profiling prerequisites.

## Level 3: the roofline model

Counters say what the hardware did. They do not say how far you are from what it *could* do. For that, Samuel Williams, Andrew Waterman and David Patterson proposed the **roofline model** (2009).

### Arithmetic intensity

The key property of a kernel is its **arithmetic intensity** (AI): floating-point operations performed per byte moved to or from main memory.

```
AI = FLOPs / bytes of DRAM traffic
```

A machine has two limits: peak compute `P` (FLOP/s) and memory bandwidth `B` (bytes/s). A kernel can go no faster than either allows:

```
performance <= min(P, AI x B)
```

Plotted on log–log axes, that is a sloped line (bandwidth-limited) meeting a flat line (compute-limited): a roof.

For example, at P = 1,000 GFLOP/s and B = 100 GB/s:

| AI (FLOP/byte) | Bandwidth ceiling (GFLOP/s) | Combined roof (GFLOP/s) |
|---|---|---|
| 0.01 | 1 | 1 |
| 0.1 | 10 | 10 |
| 1 | 100 | 100 |
| 10 | 1,000 | 1,000 |
| 100 | 10,000 | 1,000 |

The corner is the **ridge point**, `P / B`. To its left, bandwidth is the lower of these two ceilings; to its right, arithmetic throughput is lower. At the ridge they are equal. An actual kernel may run below both because of dependencies, latency, limited concurrency or other resource ceilings. Position alone does not prove its observed bottleneck.

### Worked example

Take a machine with P = 1,000 GFLOP/s and B = 100 GB/s, so the ridge is at 10 FLOP/byte. Consider three kernels on 8-byte doubles:

Use a cold streaming model with disjoint arrays, 8-byte doubles, write-back/write-allocate caches, full-line utilisation and eventual dirty-line writeback. Exclude non-temporal stores and traffic-elimination optimisations unless stated.

- **Vector add** `c[i] = a[i] + b[i]`: one FLOP; 16 input bytes, 8 bytes of output read-for-ownership and 8 bytes of eventual output writeback per element. AI = 1/32.
- **DAXPY** `y[i] = a * x[i] + y[i]`: count two FLOPs per multiply-add. Reading x and y plus writing y back moves 24 bytes per element in this model, so AI = 1/12.
- **Matrix multiply**: conventionally count 2n³ FLOPs, treating each MAC as two. Idealised traffic of one read each for A and B and one write for C is 24n² bytes, giving AI = n/12. This deliberately excludes write allocation and assumes enough reuse; it is not achievable for arbitrary n with fixed cache capacity.

```python
def attainable(ai, peak, bw):
    """GFLOP/s bound; nonnegative inputs."""
    return min(peak, ai * bw)

PEAK, BW = 1000, 100  # GFLOP/s, GB/s
RIDGE = PEAK / BW     # 10 FLOP/B
kernels = {"vec add": 1 / 32,
           "daxpy": 2 / 24,
           "matmul": 1000 / 12}
for k, ai in kernels.items():
    g = attainable(ai, PEAK, BW)
    kind = ("bw roof" if ai < RIDGE
            else "compute roof")
    print(f"{k:8}{ai:6.2f}{g:7.1f}", kind)
```

```
vec add   0.03    3.1 bw roof
daxpy     0.08    8.3 bw roof
matmul   83.33 1000.0 compute roof
```

The vector-add bound is about 0.3125% of the assumed compute peak under this traffic model. Matrix multiplication’s ideal intensity permits a compute ceiling, but does not guarantee reaching it. A naive loop may repeatedly fetch data if it exceeds cache capacity; small matrices may remain cached. Blocking can improve reuse, although real traffic need not equal the ideal three-matrix estimate.

### Using the roofline

1. **Plot the kernel.** Measure its FLOPs and DRAM bytes (with counters, or tools such as Intel Advisor or NVIDIA Nsight Compute, which draw rooflines for you) and its achieved GFLOP/s.
2. **Find the roof above it.** That is your ceiling for this algorithm.
3. **Investigate the gap.** If measured bandwidth is saturated, reduce traffic or improve useful reuse. If arithmetic resources are limiting, investigate instruction choice and independent work. SIMD, threads or fusion can affect several resources; smaller types and FMA must satisfy numerical requirements. Measure again after a change.

Real rooflines add lower **ceilings**: peak without SIMD, peak without FMA, bandwidth from a single core. They also add rooflines per memory level (L1, L2, L3, DRAM), because a kernel's AI against DRAM can be much higher than against L1.

> [!tip] Calibrate a consistent bandwidth model
> Measure bandwidth using a relevant access pattern, for example STREAM. STREAM reports useful array bytes, which may differ from physical DRAM bytes because of write allocation. Use the same byte convention for AI and B; do not multiply a physical-traffic intensity by an incompatible useful-bandwidth figure. A compute ceiling also requires the actual sustained instruction issue rate and clock, not just a count of FMA units.

### Concurrency and memory bandwidth

Little’s law relates average data in flight to byte throughput times average residence time. At a hypothetical 100 GB/s and 100 ns, that is 10,000 bytes or 156.25 average 64-byte requests; at least 157 whole request slots would be needed to accommodate that amount simultaneously. A core’s demand queues, prefetchers and lower-level memory resources affect available concurrency. Some workloads saturate bandwidth with one core; others require several. No universal L1 miss-buffer count or core threshold applies.

## Pitfalls

- **Counting the wrong bytes.** AI from the source code ("I read two arrays") ignores write-allocate, cache reuse and prefetching. Measure traffic where you can.
- **Peak FLOP/s for the wrong precision.** Peak depends on precision, instruction shape and the selected device; use the matching rate.
- **Optimising the wrong thing.** Changing an arithmetic ceiling alone cannot raise a fixed saturated-bandwidth ceiling; the real implementation may also change concurrency or traffic.
- **Profiling a different program.** Debug builds, tiny inputs and an idle laptop on battery all behave differently from production.

> [!note] Evidence limits
> A universal perf sampling default, PMU overhead figure and CPU miss-buffer count is omitted because these depend on tool version, permissions, processor and workload and were not reliably established for a single stated target.

## Key takeaways
- Match warm-up, repeats and timing statistics to the objective; account for frequency, placement and dead-code elimination.
- IPC is a ratio, not a diagnosis. Use supported counters and model-specific metrics to investigate causes.
- Sampling profiles represent their chosen event; flame-graph widths are inclusive sample weights, not chronological durations.
- Roofline bounds performance by arithmetic throughput and consistently measured traffic bandwidth; actual performance can be lower.
- Validate both numerical correctness and end-to-end performance after changing layout, precision, SIMD, threading or fusion.

## Further reading
- [Roofline: an insightful visual performance model (Williams, Waterman, Patterson)](https://people.eecs.berkeley.edu/~kubitron/cs252/handouts/papers/RooflineVyNoYellow.pdf)
- [Roofline performance model — NERSC documentation](https://docs.nersc.gov/tools/performance/roofline/)
- [Linux perf examples — Brendan Gregg](https://www.brendangregg.com/perf.html)
- [Flame graphs — Brendan Gregg](https://www.brendangregg.com/flamegraphs.html)
- [Top-down analysis — perf wiki](https://perfwiki.github.io/main/top-down-analysis/)
- [Python support for the Linux perf profiler](https://docs.python.org/3/howto/perf_profiling.html)
- [STREAM benchmark — John McCalpin](https://www.cs.virginia.edu/stream/)

- [Python timeit](https://docs.python.org/3/library/timeit.html)

- [STREAM reference conventions](https://www.cs.virginia.edu/stream/ref.html)
