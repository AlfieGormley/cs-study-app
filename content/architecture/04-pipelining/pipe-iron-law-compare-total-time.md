---
id: pipe-iron-law-compare-total-time
sourceLesson: pipe-iron-law
title: Compare machines and compiler changes
level: basic
minutes: 4
summary: Calculate total time or cycles when clock rate, instruction count and CPI change together.
---

Use the fixed-frequency iron law from the earlier units. Each example below changes one or more terms, so a headline clock rate or instruction count cannot settle the comparison.

## Comparing machines correctly

The iron law stops you being fooled by any one number.

### Faster clock, slower machine

Same program, same instruction count (10⁹). Machine A runs at 2 GHz with CPI 1.2; machine B runs at 3 GHz with CPI 2.0. Apply the iron law to each:

```formula
T_A = (IC × CPI_A) / f_A
T_A = 10^9 × 1.2 / (2 × 10^9 Hz) = 0.60 s
T_B = (IC × CPI_B) / f_B
T_B = 10^9 × 2.0 / (3 × 10^9 Hz) ≈ 0.67 s
where
T_A, T_B: the run times on machines A and B, in seconds (s)
IC: instruction count, 10^9 instructions on both machines
CPI_A, CPI_B: the average cycles per instruction on each machine: 1.2 and 2.0
f_A, f_B: the clock frequencies: 2 GHz (2 × 10^9 Hz) and 3 GHz (3 × 10^9 Hz)
Hz: hertz, cycles per second
s: seconds
≈: approximately equal to (rounded)
In words: B's clock is faster, but it needs so many more cycles per instruction that it still finishes later.
```

A is about 1.11× faster despite a clock 33% slower.

### More instructions, less time

The same trap catches compilers. Compiler X emits 1.0 × 10⁹ instructions at CPI 1.1; compiler Y emits 0.8 × 10⁹ instructions at CPI 1.5. On the same clock, compare total cycles:

```formula
N_X = IC_X × CPI_X = 1.0 × 10^9 × 1.1
N_X = 1.1 × 10^9
N_Y = IC_Y × CPI_Y = 0.8 × 10^9 × 1.5
N_Y = 1.2 × 10^9
where
N_X, N_Y: the total clock cycles for the code from compilers X and Y
IC_X, IC_Y: the instruction counts: 1.0 × 10^9 and 0.8 × 10^9
CPI_X, CPI_Y: the average cycles per instruction: 1.1 and 1.5
In words: X runs 25% more instructions but needs fewer cycles in total, so on the same clock X finishes first.
```

When you compare, compute **total cycles** (IC × CPI) on the same clock, or total time on different clocks. Never compare one term in isolation.

### Speedup

Performance is the reciprocal of time, so "A is S times faster than B" means:

```formula
S = T_B / T_A
S = 0.667 s / (0.600 s) ≈ 1.11
where
S: the speedup of A over B: how many times faster A is; above 1 means A is faster
T_A: the run time on machine A, in seconds (s); 0.600 s in the first example
T_B: the run time on machine B, in seconds; 0.667 s in the first example
s: seconds
≈: approximately equal to (rounded)
In words: speedup is the old (or other) time divided by the new time, so a bigger number means a bigger win.
```

Be careful with phrases like "50% faster": it means a speedup of 1.5, not that time fell by 50% (which would be a speedup of 2, twice as fast).

## Key takeaways
- On one fixed clock, compare total cycles; on different clocks, compare execution time.
- A reduction in instruction count can lose if CPI rises enough.
- Speedup divides old time by new time; halving time doubles speed.

## Further reading
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)

- [MIT: processor-performance equation and pipeline mechanics](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/pages/c15/c15s1/)
