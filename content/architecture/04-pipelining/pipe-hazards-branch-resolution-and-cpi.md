---
id: pipe-hazards-branch-resolution-and-cpi
sourceLesson: pipe-hazards
title: Control hazards and additive CPI
level: intermediate
minutes: 5
summary: Compare branch-resolution choices and combine nonoverlapping hazard penalties.
---

Use the same scalar IF–ID–EX–MEM–WB teaching design. The earlier data-hazard units established forwarding and one-cycle load-use stalls; this unit adds branch control flow. All branch penalties below specify their resolution stage and prediction rule, so they are model-specific.

## Control hazards

After fetching a branch in cycle 1, what should IF fetch in cycle 2? The branch hasn't even been decoded, let alone compared its registers. This is a **control hazard**.

Suppose the branch outcome is known at the end of EX (cycle 3). Options:

1. **Stall** until the branch resolves: 2 lost cycles on every branch.
2. **Predict not taken**: keep fetching sequentially. If the branch isn't taken, no cost. If it is, **flush** the two wrongly fetched instructions (turn them into bubbles) and fetch from the target: a 2-cycle penalty.
3. **Resolve earlier**: add a comparator and target adder in ID so the branch is decided in cycle 2. The penalty falls to 1 cycle, but now the branch may need forwarding into ID and can stall on an instruction ahead of it.
4. **Branch delay slot**: classic MIPS normal delay slots execute on both paths; some branch-likely forms have annulment rules. The compiler fills the slot with useful work when it can (or a `nop`). It provides one architecturally executed slot; that does not necessarily hide the entire branch penalty of a particular implementation, but became a burden when pipelines got deeper and wider. RISC-V and ARM64 do not have delay slots.

Real processors use **dynamic branch prediction**, covered in the following prediction units.

## Putting numbers on it

For a long run in this scalar model, ignoring fill/drain and avoiding double-counting overlapping penalties, hazards add stall cycles to the ideal CPI of 1. Each hazard type contributes how often it can occur, times how often it actually bites, times what it costs:

```formula
CPI = 1 + s
s = Σ_h (F_h × p_h × c_h)
where
CPI: cycles per instruction, the average clock cycles per completed instruction
1: the ideal CPI of a single-issue pipeline, which completes one instruction per cycle when nothing stalls
s: the average stall cycles per instruction
Σ_h: sigma: add up the bracketed term over every hazard type h
h: one hazard type, such as load-use stalls or taken branches
F_h: the fraction of all instructions that can cause hazard h (for example, the fraction that are loads), between 0 and 1
p_h: the probability that such an instruction actually causes the stall (for example, that the next instruction depends on the load), between 0 and 1
c_h: the penalty each time, in stall cycles
In words: CPI is one plus the average number of stall cycles per instruction, and each hazard adds its frequency times its probability times its penalty.
```

A worked example: 25% of instructions are loads, and 40% of those are immediately followed by a dependent instruction (1-cycle stall each). 15% are branches; with predict-not-taken, 60% of them are taken, costing 2 cycles. Assume these penalties are additive, and the stated dependencies need operands in EX:

```formula
s_load = 0.25 × 0.4 × 1 = 0.10
s_br = 0.15 × 0.6 × 2 = 0.18
CPI = 1 + s_load + s_br
CPI = 1 + 0.10 + 0.18 = 1.28
where
s_load: the stall cycles per instruction from load-use hazards: fraction of loads × fraction followed by a dependent instruction × 1-cycle penalty
s_br: the stall cycles per instruction from taken branches: fraction of branches × fraction taken × 2-cycle penalty
CPI: cycles per instruction including the stalls
In words: load-use stalls add 0.10 cycles and taken branches add 0.18 cycles to every instruction on average, so CPI rises from 1 to 1.28.
```

Notice branches cost more than loads here. That is why branch prediction gets an entire lesson, and why it matters even more in deeper pipelines, where recovery penalties may be larger. Exact real-core cycle counts require a specified core and measurement.

> [!note] Keep the earlier zero-register rule
> The data-hazard units also excluded writes to RISC-V x0 from forwarding. Control-hazard accounting does not relax that correctness requirement.

## Key takeaways
- Resolving a branch later leaves more sequential fetches to discard in the stated model.
- Earlier resolution can trade fewer flushes for operand waits or a slower clock.
- Add hazard contributions only when their costs do not overlap.

## Further reading
- [MIPS architecture manual: branches and delay slots](https://hades.mech.northwestern.edu/images/a/af/MIPS32_Architecture_Volume_I-A_Introduction.pdf)
- [RISC-V unprivileged ISA specification](https://riscv.github.io/riscv-isa-manual/snapshot/spec/)
- [BOOM implementation: branch prediction](https://docs.boom-core.org/en/latest/sections/branch-prediction/index.html)
