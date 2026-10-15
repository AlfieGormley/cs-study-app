---
id: pipe-iron-law-weighted-cpi
sourceLesson: pipe-iron-law
title: Compute CPI from an instruction mix
level: basic
minutes: 3
summary: Use a hypothetical additive cost model to find which instruction class contributes most to average CPI.
---

A program mixes arithmetic, memory and control-flow instructions. This unit uses an explicitly additive teaching model: the listed cycle costs do not overlap. Real superscalar measurements need consistent cycle attribution rather than the sum of instruction latencies.

## CPI is an average over an instruction mix

For a simple non-overlapping cost model, assign a cycle cost to each instruction class. The overall CPI is then its instruction-frequency-weighted average. On an overlapping superscalar processor, adding individual instruction latencies would double-count shared cycles; a measured CPI breakdown needs a consistent attribution method. The following numbers are hypothetical additive costs:

```formula
CPI = Σ_i (F_i × CPI_i)
where
Σ_i: sigma: add up the bracketed term over every instruction class i
i: one instruction class, such as ALU operations, loads, stores or branches
F_i: the fraction of executed instructions that belong to class i, between 0 and 1; all the fractions add up to 1
CPI_i: the cycle cost of one instruction in class i, in clock cycles
CPI: the average cycles per instruction over the whole mix
In words: the overall CPI is each class's cycle cost weighted by how often that class occurs.
```

Here is the calculation in Python for a hypothetical mix:

```python
mix = {          # fraction, cycles
    "alu":    (0.50, 1),
    "load":   (0.20, 5),
    "store":  (0.10, 3),
    "branch": (0.20, 2),
}
# Weight each class by its frequency.
cpi = sum(f * c for f, c in mix.values())
# Output: average cycles per instruction.
print(round(cpi, 2))   # 2.2
```

The same working by hand:

```formula
CPI = F_ALU × 1 + F_load × 5
      + F_st × 3 + F_br × 2
CPI = 0.5 × 1 + 0.2 × 5 + 0.1 × 3 + 0.2 × 2
CPI = 0.5 + 1.0 + 0.3 + 0.4 = 2.2
where
CPI: the average cycles per instruction over the mix
F_ALU: the fraction of instructions that are ALU (arithmetic and logic) operations, 0.5 here, each costing 1 cycle
F_load: the fraction that are loads, 0.2 here, each costing 5 cycles
F_st: the fraction that are stores, 0.1 here, each costing 3 cycles
F_br: the fraction that are branches, 0.2 here, each costing 2 cycles
In words: weighting each class's cycle cost by its share of the instructions gives an average of 2.2 cycles per instruction.
```

Notice that loads are only 20% of instructions but contribute 1.0 of the 2.2 cycles, almost half. This is how architects decide what to optimise: find the term that dominates the weighted sum. Halving the load cost (5 cycles to 2.5) saves 0.2 × 2.5 = 0.5 cycles per instruction and brings CPI to 1.7; halving the ALU cost (1 cycle to 0.5) saves only 0.25 and brings it to 1.95.

## Key takeaways
- Weight each class cost by its share of executed instructions.
- Do not add overlapping instruction latencies as if execution were serial.
- Compare weighted savings before choosing which class to optimise.

## Further reading
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)

- [MIT: processor-performance equation and pipeline mechanics](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/pages/c15/c15s1/)
