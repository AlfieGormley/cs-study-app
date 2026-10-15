---
id: par-vector-peak
title: Calculating vector peak throughput
level: intermediate
minutes: 3
sourceLesson: par-simd
summary: Peak throughput requires a sustained instruction rate and clock, not ISA width alone.
---

### Peak throughput

A chip's theoretical peak arithmetic rate multiplies four things together: how many cores it has, how fast each clock ticks, how many vector instructions each core can start per cycle, and how much arithmetic each of those instructions does:

```formula
F_cyc = N_u L F_op
F_peak = N_c f_clk F_cyc
where
F_cyc: floating-point operations (FLOPs) one core can complete per clock cycle
N_u: the number of vector arithmetic units in a core that can each start an instruction every cycle
L: the number of lanes per vector instruction
F_op: FLOPs per lane per instruction: 2 for an FMA (a multiply and an add), 1 for a plain add or multiply
F_peak: the peak rate of the whole chip, in FLOPs per second (FLOP/s)
N_c: the number of CPU cores
f_clk: the sustained clock frequency, in hertz (Hz), that is cycles per second
In words: peak FLOP rate is cores times cycles per second times the FLOPs each core can do per cycle, and that last figure is units times lanes times FLOPs per instruction.
```

A hypothetical single core sustaining two 256-bit float32 FMAs per cycle at 3 GHz:

```formula
F_cyc = 2 × 8 × 2 = 32
F_peak = 1 × 3 × 10^9 Hz × 32 FLOP
F_peak = 96 × 10^9 FLOP/s = 96 GFLOP/s
where
F_cyc: FLOPs per cycle per core: 2 FMA units × 8 float32 lanes × 2 FLOPs per FMA
F_peak: the peak rate, in FLOPs per second
Hz: hertz, one cycle per second; 3 GHz is 3 × 10^9 Hz
FLOP: one floating-point operation
FLOP/s: floating-point operations per second
GFLOP/s: gigaFLOPs per second, 10^9 FLOP/s
In words: 32 FLOPs per cycle at 3 billion cycles a second is 96 billion FLOPs a second.
```

A hypothetical scalar baseline sustaining one add per cycle delivers 3 GFLOP/s; this compares different operations and assumes the stated throughput. Real peak and useful performance require target-specific instruction and memory measurements.

## Key takeaways
- Peak throughput requires a sustained instruction rate and clock, not ISA width alone.
- An accelerated loop still contributes only part of total application runtime.

## Further reading
- [LLVM vectoriser mechanisms and legality](https://llvm.org/docs/Vectorizers.html)
- [GCC optimisation contracts](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [Intel basic architecture and vector instructions](https://cdrdv2.intel.com/v1/dl/getContent/671436)
- [Arm SVE execution-context lengths](https://learn.arm.com/insights/sve/)
- [NumPy CPU dispatch](https://numpy.org/doc/stable/reference/simd/how-it-works.html)
