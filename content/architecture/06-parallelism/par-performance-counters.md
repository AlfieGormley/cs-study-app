---
id: par-performance-counters
title: Hardware counters and top-down slots
level: advanced
minutes: 3
sourceLesson: par-measuring
summary: IPC summarises retired instructions per cycle; it does not identify a bottleneck.
---

## Level 2: hardware performance counters

Many processors provide a **performance monitoring unit** (PMU) for events such as cycles, retired instructions and cache or branch events. Linux `perf` can access supported events when permissions and the execution environment allow it. Available events, semantics and overhead depend on the processor, operating-system kernel, virtualisation and configuration; counters are not universally accessible.

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

(Illustrative numbers.) The most useful single derived figure is **IPC**, instructions per cycle: how many instructions the core retired (finished for good) on an average clock cycle. Its reciprocal, **CPI** (cycles per instruction), says the same thing the other way up.

```formula
IPC = N_ins / N_cyc
IPC = (2.808 × 10^9) / (4.012 × 10^9)
IPC ≈ 0.70
CPI = 1 / IPC ≈ 1.43
where
IPC: instructions per cycle, a plain ratio
N_ins: the number of instructions retired during the run; 2.808 billion here
N_cyc: the number of core clock cycles during the run; 4.012 billion here
CPI: cycles per instruction, the reciprocal of IPC
≈: approximately equal to
In words: the core finished about 0.7 instructions per clock cycle on average, or about 1.4 cycles per instruction.
```

IPC below a core’s maximum retirement width does not identify the cause. Serial arithmetic dependencies, long-latency execution units, instruction-to-micro-op expansion, memory delays, frontend limits and speculation can all contribute. Architectural instructions are not identical to issue slots. Even high IPC can reflect unnecessary work; measure useful completed results.

`perf stat -r 10` repeats the run and reports variation. This helps describe variability but does not remove warm-up, placement or workload bias.

### Where does the time go? Top-down analysis

Raw counters are hard to interpret: is 61 million cache misses a lot? Intel's **top-down microarchitecture analysis** attributes pipeline *slots* using model-specific metrics. The top-level categories are:

| Category | Meaning |
|---|---|
| Retiring | Slots attributed to retiring work, not necessarily algorithmically useful |
| Bad speculation | Discarded work and recovery slots |
| Frontend bound | Fetch/decode starved |
| Backend bound | Waiting on memory or units |

Backend bound splits further into *memory bound* and *core bound*. On supported CPUs, `perf stat --topdown` prints this breakdown. Use the largest categories to guide investigation, then compare achievable total-time savings. A slot percentage is not an elapsed-time fraction or a guaranteed speedup bound.

## Key takeaways
- IPC summarises retired instructions per cycle; it does not identify a bottleneck.
- Top-down slot categories are model-specific and are not elapsed-time fractions.

## Further reading
- [The original Roofline paper](https://people.eecs.berkeley.edu/~kubitron/cs252/handouts/papers/RooflineVyNoYellow.pdf)
- [Python timeit measurement contract](https://docs.python.org/3/library/timeit.html)
- [Linux perf stat reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-stat.txt)
- [Linux perf record reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-record.txt)
- [Flame graphs from their creator](https://www.brendangregg.com/flamegraphs.html)
- [STREAM traffic conventions](https://www.cs.virginia.edu/stream/ref.html)
- [Python Linux perf integration](https://docs.python.org/3/howto/perf_profiling.html)
