---
id: pipe-out-of-order-ready-independent-work
sourceLesson: pipe-out-of-order
title: Find independent work beyond a stall
level: advanced
minutes: 3
summary: Distinguish superscalar width from out-of-order scheduling and preserve the architectural execution contract.
---

A scalar pipeline, however well forwarded and predicted, peaks at one instruction per cycle. In this instruction-level model, sustaining CPI below 1 requires starting more than one instruction per cycle on average. That is **superscalar** execution.

In-order superscalar execution can improve throughput, but a blocked instruction can prevent younger independent work from issuing. **Out-of-order** execution finds ready work further ahead while preserving the architectural rules. The 200-cycle load used below is hypothetical, not a universal DRAM latency. In-order retirement does not imply sequentially consistent interthread memory ordering. The following units separate scheduling, register versions and recovery.

## Instruction-level parallelism

**Instruction-level parallelism** (ILP) is the number of instructions in a stretch of code that could, in principle, run at the same time.

Assume `b`, `c`, `e` and `f` are already available input values. This Python fragment illustrates the data-flow edges; it does not print a result.

```python
# First two results use only ready inputs.
a = b + c      # independent
d = e + f      # independent
g = a * d      # needs both
```

The first two can run together; the third must wait. True (RAW) dependences limit the independent operations available in a trace. Branches, fetch limits and memory behaviour also constrain how much parallelism a core can discover and exploit.

## In-order superscalar

A simple in-order superscalar design can issue two instructions per cycle when pairing rules, operands and execution resources allow. Multiple issue does not itself require out-of-order scheduling.

The weakness of in-order issue: when one instruction stalls, everything behind it stalls too, even independent work.

```
lw   x1, 0(x2)    # assume a long cache miss
add  x3, x1, x4   # must wait: depends on x1
mul  x5, x6, x7   # independent, but stuck
sub  x8, x9, x10  # independent, but stuck
```

An out-of-order core runs `mul` and `sub` while the load is outstanding.

## The out-of-order pipeline

A common out-of-order (OoO) teaching design has three parts. Real designs differ in µop grouping, scheduler organisation and retirement bookkeeping:

```
IN ORDER: fetch, decode, rename,
          allocate ROB entry
              |
              v
OUT OF ORDER: scheduler waits for
              operands, issues to
              ALUs / load-store unit
              |
              v
IN ORDER: reorder buffer retires
          (commits) oldest first
```

1. **Front end, in order**: fetch (guided by the branch predictor), decode into µops, **rename** registers, and allocate tracking space in the **reorder buffer** (ROB) and in a scheduler.
2. **Execution, out of order**: each µop waits in the scheduler until its source operands are ready and a suitable unit is free, then becomes eligible to issue. The scheduler chooses among ready operations; result delivery wakes dependent µops.
3. **Retirement, in order**: the ROB commits results to the architectural state strictly in program order, so exceptions and mispredictions can be handled precisely.

## Key takeaways
- Multiple issue and out-of-order scheduling are separate choices.
- A true dependence chain limits throughput even on a wide core.
- A common design fetches/renames in order, executes ready work out of order, then retires in order.

## Further reading
- [BOOM implementation: pipeline](https://docs.boom-core.org/en/latest/sections/intro-overview/boom-pipeline.html)
- [BOOM implementation: rename stage](https://docs.boom-core.org/en/latest/sections/rename-stage.html)
- [BOOM implementation: reorder buffer](https://docs.boom-core.org/en/latest/sections/reorder-buffer.html)
