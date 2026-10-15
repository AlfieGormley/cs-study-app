---
id: pipe-five-stage-fill-latency-speedup
sourceLesson: pipe-five-stage
title: Fill, latency and pipeline speedup
level: basic
minutes: 4
summary: Count a finite burst and distinguish instruction latency from long-run throughput.
---

Use a scalar five-stage pipeline with one-cycle stages and no hazards. The earlier timing unit used an 800 ps single-cycle period and a 200 ps pipelined period before register overhead; IF, EX and MEM each took 200 ps, while ID and WB took 100 ps. Keep these assumptions explicit in the calculations.

## How much faster?

Take a run of instructions on an initially empty, single-issue pipeline with no stalls. The first instruction needs one cycle per stage to come out, and each later one comes out 1 cycle after the one before:

```formula
N_cyc = k + (n − 1)
where
N_cyc: the total clock cycles from the first fetch to the last write-back
k: the number of pipeline stages; 5 here
n: the number of instructions in the run, at least 1
In words: filling the pipeline costs one cycle per stage, then every further instruction adds just one more cycle.
```

For 1,000 instructions, compare the single-cycle design with the pipelined one:

```formula
T_single = n × T_1 = 1000 × 800 ps = 800 ns
T_pipe = (k + n − 1) × T_clk
T_pipe = 1004 × 200 ps = 200.8 ns
S = T_single / T_pipe
S = 800 ns / (200.8 ns) ≈ 3.98
where
T_single: the total time on the single-cycle design, measured here in picoseconds or nanoseconds
T_pipe: the total time on the pipelined design, measured here in picoseconds or nanoseconds
n: the number of instructions, 1,000
k: the number of pipeline stages, 5
T_1: the single-cycle clock period, 800 ps
T_clk: the pipelined clock period, 200 ps (no register overhead)
S: the speedup: how many times faster the pipeline is
ps: picoseconds, 10^-12 seconds
ns: nanoseconds, 10^-9 seconds; 1 ns = 1,000 ps
≈: approximately equal to (rounded)
In words: the pipeline runs the 1,000 instructions about 3.98 times faster than the single-cycle design.
```

The ideal long-run speedup approaches the number of stages, here five: that requires perfectly balanced stages, so each stage takes one fifth of the single-cycle period, and no register overhead. We got about 4 for two reasons:

1. **Unbalanced stages.** ID and WB need only 100 ps but get a full 200 ps slot. The pipeline runs at the pace of its slowest stage.
2. **Fill and drain.** The first four cycles have at least one empty stage in this five-stage model. With 1,000 instructions this barely matters (4 cycles); with 5 it would matter a lot.

For a long run, the instruction count is so large that the fill cycles become negligible and the speedup settles at the ratio of the two clock periods:

```formula
S_max = T_1 / T_clk
S_max = 800 ps / (200 ps) = 4
S_max = 800 ps / (220 ps) ≈ 3.6
where
S_max: the long-run speedup as the number of instructions grows very large
T_1: the single-cycle clock period, 800 ps
T_clk: the pipelined clock period: 200 ps without register overhead, 220 ps with 20 ps of overhead
ps: picoseconds, 10^-12 seconds
≈: approximately equal to (rounded)
In words: in the long run the pipeline wins by the ratio of the old clock tick to the new one, so register overhead eats directly into the gain.
```

> [!warning] Throughput and latency differ
> With a 200 ps cycle, a single load now takes five cycles of 200 ps, 1,000 ps in all, to pass through, compared with 800 ps unpipelined. In this comparison, pipelining raises throughput while increasing instruction latency. Balanced stages with no register overhead could preserve latency; real overhead and imbalance often increase it. Enough independent work allows the improved throughput to outweigh fill/drain overhead; billions of instructions are not required.

## Key takeaways
- An initially empty unstalled scalar run needs the stage count plus one cycle for each additional instruction.
- Fill/drain overhead matters more for a short burst.
- Stage imbalance and register overhead reduce long-run gains; latency need not improve.

## Further reading
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
