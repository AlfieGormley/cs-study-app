---
id: pipe-iron-law-execution-time
sourceLesson: pipe-iron-law
title: Calculate CPU execution time
level: basic
minutes: 4
summary: Combine completed instruction count, cycles per instruction and clock period in one fixed-frequency measurement.
---

Two processors can run at the same clock frequency and complete the same task in different times. Clock speed alone does not specify how much useful work a processor completes.

To reason about CPU performance you need one equation. Computer architects call it the **iron law of processor performance**, and every other lesson in this module is about improving one of its three terms.

## The equation

For one thread’s measured CPU execution interval at a fixed clock frequency, using matching instruction and cycle counts, run time is the product of three ratios: instructions per program, cycles per instruction and seconds per cycle.

```formula
T = IC × CPI × T_clk
T_clk = 1 / f
T = (IC × CPI) / f
where
T: the CPU execution time of the measured interval, in seconds (s)
IC: instruction count: how many instructions actually executed and completed in the interval, not how many lines the program has
CPI: cycles per instruction: the total counted clock cycles divided by IC, so an average over the whole run; it can be below 1 on a core that finishes several instructions per cycle
T_clk: the clock period, the length of one clock cycle, in seconds; a fraction of a nanosecond on a modern CPU
f: the clock frequency, how many clock cycles happen per second, in hertz (Hz); for example 3 GHz, which is 3 × 10^9 cycles per second
In words: run time is how many instructions you execute, times how many clock cycles each takes on average, times how long one cycle lasts.
```

What each term really means:

- **IC** (instruction count) is the dynamic count of architecturally completed instructions in the measured scope, not how many lines it has. A loop of 3 instructions that runs a million times contributes 3 million.
- **CPI** (cycles per instruction) is total counted cycles divided by completed instructions. It is not the average latency of individual overlapping instructions.
- The **clock period** is the length of one cycle, the reciprocal of the clock frequency.

The clock period follows directly from the frequency. For a 3 GHz clock:

```formula
T_clk = 1 / f
T_clk = 1 / (3 × 10^9 Hz)
T_clk ≈ 0.333 × 10^-9 s = 0.333 ns
where
T_clk: the clock period, the length of one clock cycle, in seconds (s)
f: the clock frequency, here 3 gigahertz (GHz), which is 3 × 10^9 hertz
Hz: hertz, one cycle per second
s: seconds
ns: nanoseconds; 1 ns = 10^-9 s, a billionth of a second
≈: approximately equal to (the result is rounded)
In words: at 3 GHz a single clock tick lasts about a third of a nanosecond.
```

With variable frequency, use compatible cycle/time accounting or sum over fixed-frequency intervals. Waiting off-CPU and concurrent threads need separate accounting; CPU time is not automatically wall-clock response time.

The units cancel neatly: instructions × cycles per instruction × seconds per cycle leaves seconds. That is a good check whenever you do one of these calculations.

### A first calculation

A program executes 2 × 10⁹ instructions with an average CPI of 1.5 on a 3 GHz CPU. First count the cycles, then divide by how many cycles happen each second:

```formula
N_cyc = IC × CPI
N_cyc = 2 × 10^9 × 1.5 = 3 × 10^9
T = N_cyc / f
T = 3 × 10^9 / (3 × 10^9 Hz) = 1 s
where
N_cyc: the total number of clock cycles the program takes
IC: instruction count, the number of instructions executed; 2 × 10^9 here
CPI: cycles per instruction, the average clock cycles per instruction; 1.5 here
T: the run time, in seconds (s)
f: the clock frequency, 3 GHz = 3 × 10^9 cycles per second
Hz: hertz, cycles per second
s: seconds
In words: 2 billion instructions at 1.5 cycles each is 3 billion cycles, and a 3 GHz clock gets through 3 billion cycles in exactly one second.
```

## Key takeaways
- Use matching instruction, cycle and time scopes at a fixed clock frequency.
- CPI is a measured average; overlapping instruction latency is a different quantity.
- Account separately for off-CPU waiting and variable frequency.

## Further reading
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
- [Linux perf tutorial](https://perfwiki.github.io/main/tutorial/)

- [MIT: processor-performance equation and pipeline mechanics](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/pages/c15/c15s1/)
