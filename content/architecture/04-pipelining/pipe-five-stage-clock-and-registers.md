---
id: pipe-five-stage-clock-and-registers
sourceLesson: pipe-five-stage
title: Pipeline registers set the clock budget
level: basic
minutes: 4
summary: Compare a single-cycle clock with the slowest pipelined stage and explain why interstage registers are necessary.
---

Continue with the five-stage load/store teaching pipeline: IF fetches, ID decodes and reads registers, EX operates, MEM accesses data, and WB writes a result. The stage delays below are hypothetical. They illustrate timing budgets, not a particular fabricated processor.

## Without a pipeline

A simple **single-cycle** processor does all five steps in one long clock cycle. The cycle must be long enough for the slowest instruction. Using these hypothetical combinational stage delays, with single-cycle boundary overhead ignored:

```
IF   ID   EX   MEM  WB
200  100  200  200  100  (ps)
```

A load uses all five steps, so the single cycle must cover their sum:

```formula
T_1 = t_IF + t_ID + t_EX + t_MEM + t_WB
T_1 = (200 + 100 + 200 + 200 + 100) ps
T_1 = 800 ps
f_1 = 1 / T_1 = 1 / (800 ps)
f_1 = 1.25 GHz
where
T_1: the clock period of the single-cycle design, in picoseconds (ps)
t_IF, t_ID, t_EX, t_MEM, t_WB: the logic delay of each step (fetch, decode, execute, memory, write back), in picoseconds
f_1: the resulting clock frequency, in gigahertz (GHz)
ps: picoseconds; 1 ps = 10^-12 seconds, so 1,000 ps = 1 nanosecond
GHz: gigahertz, 10^9 cycles per second
In words: a single-cycle CPU's clock tick must be as long as all five steps of its slowest instruction put together.
```

So the clock period is 800 ps (1.25 GHz), and each instruction takes one cycle. Most of the hardware sits idle most of the time: while the ALU is working, the fetch unit has nothing to do.

### Pipeline registers

Between each pair of stages sits a **pipeline register** (named IF/ID, ID/EX, EX/MEM and MEM/WB). At every clock edge, each stage's output is latched into the next register. This holds everything the instruction still needs: its operand values, destination register number and control signals (is it a load? does it write a register?). Without these registers, the next instruction would overwrite the values the previous one is still using.

### The clock period

The clock now only needs to cover the slowest **pipeline stage**, not the whole instruction. In reality a pipeline register adds its own delay, setup time and clock skew, which must be budgeted:

```formula
T_clk = t_max + t_reg
t_max = max(t_IF, t_ID, t_EX, t_MEM, t_WB)
where
T_clk: the pipelined clock period, in picoseconds (ps)
t_IF, t_ID, t_EX, t_MEM, t_WB: the logic delay of each of the five stages, in picoseconds
max: the largest of the values listed
t_max: the delay of the slowest stage, in picoseconds
t_reg: the per-cycle overhead of a pipeline register (its own delay, setup time and clock skew), in picoseconds
ps: picoseconds, 10^-12 seconds
In words: every stage gets the same clock tick, so the tick must fit the slowest stage plus the register overhead.
```

Here the slowest stages are IF, EX and MEM at 200 ps. With no overhead the period is 200 ps. Assuming 20 ps of combined per-cycle boundary overhead gives 200 + 20 = 220 ps; this is a teaching assumption, not a measured device value.

## Key takeaways
- The single-cycle period covers the longest whole instruction path in this model.
- The pipeline period covers the slowest stage plus boundary overhead.
- Interstage registers keep one instruction’s operands and controls aligned.

## Further reading
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
- [BOOM implementation: pipeline](https://docs.boom-core.org/en/latest/sections/intro-overview/boom-pipeline.html)
