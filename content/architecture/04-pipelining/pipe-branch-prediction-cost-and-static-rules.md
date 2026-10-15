---
id: pipe-branch-prediction-cost-and-static-rules
sourceLesson: pipe-branch-prediction
title: Cost branch misses and apply static rules
level: intermediate
minutes: 4
summary: Estimate additive branch CPI and distinguish fixed prediction rules from learned behaviour.
---

A processor can fetch and execute instructions beyond a branch before its direction and target are known. If its prediction is wrong, it must discard younger wrong-path work and redirect execution. How much work is lost depends on the processor and when the branch resolves.

> [!note] Evidence limits
> Universal branch frequencies, prediction accuracies, pipeline depths and product-specific predictor details are omitted: they need a named workload and reliable documentation or measurements. The numerical examples below are explicit teaching models.

## What a misprediction costs

In an additive model with a fixed average recovery penalty and no overlap with other counted stalls, mispredictions add this many cycles to every instruction on average:

```formula
CPI_br = F_br × m × c_mis
m = 1 − A
where
CPI_br: the extra cycles per instruction caused by branch mispredictions
F_br: the branch fraction: the share of executed instructions that are branches, between 0 and 1
m: the misprediction rate: the share of branches predicted wrongly, between 0 and 1
A: the predictor's accuracy: the share of branches predicted correctly, between 0 and 1
c_mis: the misprediction penalty: the cycles lost recovering from each wrong prediction
In words: only mispredicted branches cost anything, so the extra CPI is how often branches occur, times how often they are guessed wrong, times what each wrong guess costs.
```

### Why 95% isn't good enough

Assume unchanged retired instruction count and clock frequency, with additive penalties. 20% of instructions are branches, the predictor is 95% accurate, and the penalty is 15 cycles. The core is 4-wide, with an ideal CPI of 0.25 when every prediction is right:

```formula
CPI_br = 0.2 × (1 − 0.95) × 15 = 0.15
CPI = CPI_base + CPI_br
CPI = 0.25 + 0.15 = 0.40
S = CPI / CPI_base = 0.40 / 0.25 = 1.6
where
CPI_br: the extra cycles per instruction from mispredictions
CPI_base: the CPI with perfect prediction, 0.25 for this 4-wide core (it can finish up to 4 instructions per cycle)
CPI: the actual average cycles per instruction
S: the slowdown factor relative to perfect prediction; with the same instruction count and clock, time is proportional to CPI
In words: 5% of branches being wrong adds 0.15 cycles to every instruction, which makes this core 1.6 times slower than with perfect prediction.
```

The program runs **1.6× slower** than with perfect prediction. Getting to 98% accuracy, with the other assumptions unchanged, brings the extra branch contribution down to 0.06 cycles per instruction. The wrong-prediction fraction is now 2% rather than 5%.

Lower base CPI makes a given additional CPI more significant. Width and pipeline organisation can affect recovery, but neither alone determines a universal penalty or area cost.

## Static prediction

The simplest predictors use fixed rules with no history:

- **Always not taken**: just keep fetching sequentially. Simple; it misses each taken iteration of a loop-back branch.
- **Backward taken, forward not taken (BTFN)**: a branch that jumps backwards is probably a loop, so predict taken; a forward branch is probably an `if`, so predict not taken. This is a heuristic, not a guarantee about source-level control flow.

Compilers help by laying out code so the likely path falls through. GCC and Clang's `__builtin_expect`, C++20's `[[likely]]` and `[[unlikely]]`, and profile-guided optimisation can inform these layout and optimisation decisions; they do not guarantee a particular hardware predictor action.

## Key takeaways
- Branch fraction, miss rate and recovery cycles determine the additive miss contribution.
- A small additional CPI is a larger slowdown when base CPI is already low.
- BTFN is a direction heuristic; compiler hints guide optimisation without guaranteeing hardware action.

## Further reading
- [McFarling: Combining Branch Predictors (original report)](https://shiftleft.com/mirrors/www.hpl.hp.com/techreports/Compaq-DEC/WRL-TN-36.pdf)
- [GCC: branch expectation built-in](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html)
- [BOOM implementation: branch prediction](https://docs.boom-core.org/en/latest/sections/branch-prediction/index.html)
