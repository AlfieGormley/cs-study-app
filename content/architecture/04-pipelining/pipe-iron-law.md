---
id: pipe-iron-law
title: The iron law, CPI and IPC
level: basic
minutes: 10
summary: Why clock speed alone says little about performance, and how instruction count, cycles per instruction and clock period multiply together to give run time.
---

Two processors can run at the same clock frequency and complete the same task in different times. Clock speed alone does not specify how much useful work a processor completes.

To reason about CPU performance you need one equation. Computer architects call it the **iron law of processor performance**, and every other lesson in this module is about improving one of its three terms.

## The equation

For one thread’s measured CPU execution interval at a fixed clock frequency, using matching instruction and cycle counts, run time is the product of three ratios: instructions per program, cycles per instruction and seconds per cycle.

```formula
T = IC × CPI × T_clk
T_clk = 1 / f
T = IC × CPI / f
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

## IPC: the same idea, inverted

Modern processors can finish several instructions in one cycle, which makes CPI less than 1. People then usually quote its reciprocal, **IPC** (instructions per cycle):

```formula
IPC = 1 / CPI
T = IC / (IPC × f)
where
IPC: instructions per cycle: completed instructions divided by counted cycles; above 1 when a core finishes several instructions per cycle on average
CPI: cycles per instruction, the reciprocal of IPC
T: the CPU execution time, in seconds (s)
IC: instruction count, the number of instructions executed
f: the clock frequency, in hertz (Hz): cycles per second
In words: IPC is CPI turned upside down, so a higher IPC means less time for the same instructions at the same clock.
```

A CPI of 0.5 is an IPC of 2. Both describe the same measured instruction/cycle totals; IPC is just more natural when the number is above 1. Linux's `perf stat` reports IPC directly:

```
$ perf stat ./myprog
  3,000,000,000  cycles
  6,000,000,000  instructions
    # 2.00 insn per cycle
```

(The real output has more columns; this is trimmed to the relevant lines.) Here 6,000,000,000 instructions divided by 3,000,000,000 cycles gives the 2.00 shown, which is a CPI of 0.5.

## Who controls which term?

The three terms are not independent knobs. Each is influenced by different people, and improving one often hurts another.

| Term | Mainly set by | Example |
|---|---|---|
| IC | Algorithm, compiler, ISA | Sorting n items: O(n log n) vs O(n²) |
| CPI | Microarchitecture, compiler | Pipelining, caches |
| Clock period | Circuit design, process | Logic depth, voltage |

- **The algorithm** can substantially change the work required. Hardware instructions, accelerators and compiler transformations can also reduce architectural IC. The best improvement depends on the measured bottleneck.
- **The compiler** changes IC (removing redundant work, vectorising four additions into one instruction) and CPI (ordering instructions so they don't wait on each other).
- **The instruction set** (ISA) matters too. A CISC instruction such as x86's `rep movsb` does a whole memory copy in one instruction, giving low IC but high CPI. Instruction count is not a fair standalone comparison across ISAs; counts also depend on vectorization and other instructions.
- **The microarchitecture** (how the chip implements the ISA) drives CPI: pipelining, branch prediction, out-of-order execution and caches all aim to lower it.
- **The circuit and process technology** set how short a cycle can be.

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
cpi = sum(f * c for f, c in mix.values())
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

## Comparing machines correctly

The iron law stops you being fooled by any one number.

### Faster clock, slower machine

Same program, same instruction count (10⁹). Machine A runs at 2 GHz with CPI 1.2; machine B runs at 3 GHz with CPI 2.0. Apply the iron law to each:

```formula
T_A = IC × CPI_A / f_A
T_A = 10^9 × 1.2 / (2 × 10^9 Hz) = 0.60 s
T_B = IC × CPI_B / f_B
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
S = 0.667 s / 0.600 s ≈ 1.11
where
S: the speedup of A over B: how many times faster A is; above 1 means A is faster
T_A: the run time on machine A, in seconds (s); 0.600 s in the first example
T_B: the run time on machine B, in seconds; 0.667 s in the first example
s: seconds
≈: approximately equal to (rounded)
In words: speedup is the old (or other) time divided by the new time, so a bigger number means a bigger win.
```

Be careful with phrases like "50% faster": it means a speedup of 1.5, not that time fell by 50% (which would be a speedup of 2, twice as fast).

## Misleading metrics

### The megahertz myth

A shorter clock period can be offset by a larger CPI, for example if a deeper design incurs more recovery cycles on mispredicted branches. Exact historical processor stage counts and cross-product performance comparisons are omitted here: they need a specific primary hardware description and benchmark, rather than a general clock-speed anecdote.

### The MIPS rating

The **MIPS rating** (millions of instructions per second; nothing to do with the MIPS instruction set) counts how many millions of instructions a machine completes each second:

```formula
MIPS = IC / (T × 10^6)
MIPS = f / (CPI × 10^6)
where
MIPS: the instruction rate, in millions of instructions per second
IC: instruction count, the number of instructions executed
T: the run time, in seconds
f: the clock frequency, in hertz (Hz): cycles per second
CPI: cycles per instruction, the average clock cycles each instruction takes
10^6: one million, which turns instructions per second into millions of instructions per second
In words: MIPS is the instruction count divided by the time, in millions; equivalently, the clock rate divided by CPI.
```

As a throughput score it does not account for how many instructions the task requires, so it rewards a machine or compiler that runs lots of cheap instructions. For example, on a 1 GHz CPU, compiler P emits 1.2 × 10⁹ instructions at CPI 1.0, and compiler Q emits 0.6 × 10⁹ instructions at CPI 1.5:

```formula
T_P = 1.2 × 10^9 × 1.0 / 10^9 Hz = 1.2 s
MIPS_P = 1.2 × 10^9 / (1.2 × 10^6) = 1000
T_Q = 0.6 × 10^9 × 1.5 / 10^9 Hz = 0.9 s
MIPS_Q = 0.6 × 10^9 / (0.9 × 10^6) ≈ 667
where
T_P, T_Q: the run times of the code from compilers P and Q, in seconds (s), from instruction count × CPI / clock frequency
MIPS_P, MIPS_Q: each version's score in millions of instructions per second
Hz: hertz, cycles per second; the clock is 1 GHz = 10^9 Hz
s: seconds
≈: approximately equal to (rounded)
In words: Q finishes first while scoring a third lower on MIPS, because it simply needs fewer instructions.
```

A MIPS rating can describe instruction throughput, but it predicts task completion time only when the relevant dynamic instruction counts are fixed. The same binary can still execute different counts on different inputs or execution paths.

### Peak numbers

Vendors quote peak IPC or peak FLOPS: what the chip can do if every functional unit is busy every cycle. Real code waits on memory and mispredicted branches. Realized IPC depends on instruction mix, dependency chains, front-end delivery, memory behaviour and prediction. No universal IPC value or dominant bottleneck is asserted for databases or web servers.

> [!tip] Measure, don't guess
> `perf stat` gives you cycles, instructions and IPC for a real run. Low IPC alone does not identify the cause: serial arithmetic dependencies, execution-unit pressure, front-end limits, branch recovery and memory stalls can all contribute. Use architecture-specific counters and profiles before choosing a fix.

## Where the rest of this module fits

Every technique in the following lessons attacks one term of the iron law, and usually costs something in another:

- **Pipelining** overlaps instructions so CPI approaches 1 and the clock can be shorter. Cost: hazards.
- **Forwarding and branch prediction** claw back the CPI lost to hazards.
- **Superscalar and out-of-order** execution push CPI below 1 (IPC above 1). Cost: area, power and complexity.
- **Power and thermal limits** constrained frequency scaling and encouraged multicore designs. Frequency did not stop increasing altogether. Multiple cores can improve throughput and can reduce the time of a parallelizable single job.

## Key takeaways
- In the stated fixed-frequency scope, CPU execution time is the product of instruction count, CPI and clock period. All three terms matter; none alone predicts speed.
- IPC is the reciprocal of CPI. Modern cores can exceed 1 IPC, but real workloads often fall far short of peak.
- In the additive class-cost model, CPI is a weighted average over the instruction mix, so optimise the class that dominates the sum.
- Compare machines or compilers on total cycles or total time, never on clock rate, instruction count or MIPS rating alone.
- The algorithm and compiler set IC; the microarchitecture sets CPI; circuits and process set the clock.

## Further reading
- [Iron law of processor performance — Wikipedia](https://en.wikipedia.org/wiki/Iron_law_of_processor_performance)
- [Cycles per instruction — Wikipedia](https://en.wikipedia.org/wiki/Cycles_per_instruction)
- [Instructions per cycle — Wikipedia](https://en.wikipedia.org/wiki/Instructions_per_cycle)
- [Megahertz myth — Wikipedia](https://en.wikipedia.org/wiki/Megahertz_myth)
- [NetBurst (Pentium 4 microarchitecture) — Wikipedia](https://en.wikipedia.org/wiki/NetBurst)

- [Intel top-down performance analysis](https://www.intel.com/content/www/us/en/docs/vtune-profiler/cookbook/2024-0/top-down-microarchitecture-analysis-method.html)
- [Linux perf project tutorial](https://perfwiki.github.io/main/tutorial/)
