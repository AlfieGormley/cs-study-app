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

For one thread’s measured CPU execution interval at a fixed clock frequency, using matching instruction and cycle counts:

```
       instructions    cycles       seconds
time = ------------ x ----------- x -------
         program      instruction    cycle
```

Or, in short:

```
time = IC x CPI x Tclk
     = IC x CPI / f
```

- **IC** (instruction count) is the dynamic count of architecturally completed instructions in the measured scope, not how many lines it has. A loop of 3 instructions that runs a million times contributes 3 million.
- **CPI** (cycles per instruction) is total counted cycles divided by completed instructions. It is not the average latency of individual overlapping instructions.
- **Tclk** is the clock period, the length of one cycle. It is 1 / f, where f is the clock frequency. At 3 GHz, one cycle lasts 1 / (3 × 10⁹) s ≈ 0.333 ns.

With variable frequency, use compatible cycle/time accounting or sum over fixed-frequency intervals. Waiting off-CPU and concurrent threads need separate accounting; CPU time is not automatically wall-clock response time.

The units cancel neatly: instructions × cycles/instruction × seconds/cycle = seconds. That is a good check whenever you do one of these calculations.

> [!example] A first calculation
> A program executes 2 × 10⁹ instructions with an average CPI of 1.5 on a 3 GHz CPU.
> Cycles = 2 × 10⁹ × 1.5 = 3 × 10⁹.
> Time = 3 × 10⁹ cycles / (3 × 10⁹ cycles per second) = **1 second**.

## IPC: the same idea, inverted

Modern processors can finish several instructions in one cycle, which makes CPI less than 1. People then usually quote its reciprocal, **IPC** (instructions per cycle):

```
IPC = 1 / CPI
time = IC / (IPC x f)
```

A CPI of 0.5 is an IPC of 2. Both describe the same measured instruction/cycle totals; IPC is just more natural when the number is above 1. Linux's `perf stat` reports IPC directly:

```
$ perf stat ./myprog
  3,000,000,000  cycles
  6,000,000,000  instructions
    # 2.00 insn per cycle
```

(The real output has more columns; this is trimmed to the relevant lines.)

## Who controls which term?

The three terms are not independent knobs. Each is influenced by different people, and improving one often hurts another.

| Term | Mainly set by | Example |
|---|---|---|
| IC | Algorithm, compiler, ISA | O(n log n) vs O(n²) |
| CPI | Microarchitecture, compiler | Pipelining, caches |
| Tclk | Circuit design, process | logic depth, voltage and process |

- **The algorithm** can substantially change the work required. Hardware instructions, accelerators and compiler transformations can also reduce architectural IC. The best improvement depends on the measured bottleneck.
- **The compiler** changes IC (removing redundant work, vectorising four additions into one instruction) and CPI (ordering instructions so they don't wait on each other).
- **The instruction set** (ISA) matters too. A CISC instruction such as x86's `rep movsb` does a whole memory copy in one instruction, giving low IC but high CPI. Instruction count is not a fair standalone comparison across ISAs; counts also depend on vectorization and other instructions.
- **The microarchitecture** (how the chip implements the ISA) drives CPI: pipelining, branch prediction, out-of-order execution and caches all aim to lower it.
- **The circuit and process technology** set how short a cycle can be.

## CPI is an average over an instruction mix

For a simple non-overlapping cost model, assign each instruction class a cycle cost. The overall CPI is then its instruction-frequency-weighted average. On an overlapping superscalar processor, adding individual instruction latencies would double-count shared cycles; a measured CPI breakdown needs a consistent attribution method. The following numbers are hypothetical additive costs:

```
CPI = sum over classes of
      (fraction_i x CPI_i)
```

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

The working: 0.5 × 1 + 0.2 × 5 + 0.1 × 3 + 0.2 × 2 = 0.5 + 1.0 + 0.3 + 0.4 = **2.2**.

Notice that loads are only 20% of instructions but contribute 1.0 of the 2.2 cycles, almost half. This is how architects decide what to optimise: find the term that dominates the weighted sum. Halving the load cost (5 to 2.5) brings CPI to 1.7; halving the ALU cost (1 to 0.5) only brings it to 1.95.

## Comparing machines correctly

The iron law stops you being fooled by any single number.

> [!example] Faster clock, slower machine
> Same program, same instruction count (10⁹).
> Machine A: 2 GHz, CPI 1.2. Time = 10⁹ × 1.2 / (2 × 10⁹) = **0.60 s**.
> Machine B: 3 GHz, CPI 2.0. Time = 10⁹ × 2.0 / (3 × 10⁹) ≈ **0.67 s**.
> A is about 1.11× faster despite a clock 33% slower.

The same trap catches compilers:

> [!example] More instructions, less time
> Compiler X emits 1.0 × 10⁹ instructions at CPI 1.1, so 1.1 × 10⁹ cycles.
> Compiler Y emits 0.8 × 10⁹ instructions at CPI 1.5, so 1.2 × 10⁹ cycles.
> On the same clock, X is faster even though it executes 25% more instructions.

When you compare, compute **total cycles** (IC × CPI) on the same clock, or total time on different clocks. Never compare one term in isolation.

### Speedup

Performance is the reciprocal of time, so "A is n times faster than B" means:

```
speedup = time_B / time_A
```

In the first example, 0.667 / 0.6 ≈ 1.11. Be careful with phrases like "50% faster": it means time_B / time_A = 1.5, not that time fell by 50% (which would be 2× faster).

## Misleading metrics

### The megahertz myth

A shorter clock period can be offset by a larger CPI, for example if a deeper design incurs more recovery cycles on mispredicted branches. Exact historical processor stage counts and cross-product performance comparisons are omitted here: they need a specific primary hardware description and benchmark, rather than a general clock-speed anecdote.

### MIPS

MIPS (millions of instructions per second) is IC / (time × 10⁶), which equals f / (CPI × 10⁶). As a throughput score it does not account for how many instructions the task requires, so it rewards a machine or compiler that runs lots of cheap instructions.

> [!example] Higher MIPS, slower program
> On a 1 GHz CPU, compiler P emits 1.2 × 10⁹ instructions at CPI 1.0: 1.2 s, and 1,000 MIPS.
> Compiler Q emits 0.6 × 10⁹ instructions at CPI 1.5: 0.9 s, but only about 667 MIPS.
> Q finishes first while scoring a third lower on MIPS.

MIPS can describe instruction throughput, but it predicts task completion time only when the relevant dynamic instruction counts are fixed. The same binary can still execute different counts on different inputs or execution paths.

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
- CPU execution time in the stated fixed-frequency scope = instruction count × CPI × clock period. All three terms matter; none alone predicts speed.
- IPC is 1 / CPI. Modern cores can exceed 1 IPC, but real workloads often fall far short of peak.
- In the additive class-cost model, CPI is a weighted average over the instruction mix, so optimise the class that dominates the sum.
- Compare machines or compilers on total cycles or total time, never on clock rate, instruction count or MIPS alone.
- The algorithm and compiler set IC; the microarchitecture sets CPI; circuits and process set the clock.

## Further reading
- [Iron law of processor performance — Wikipedia](https://en.wikipedia.org/wiki/Iron_law_of_processor_performance)
- [Cycles per instruction — Wikipedia](https://en.wikipedia.org/wiki/Cycles_per_instruction)
- [Instructions per cycle — Wikipedia](https://en.wikipedia.org/wiki/Instructions_per_cycle)
- [Megahertz myth — Wikipedia](https://en.wikipedia.org/wiki/Megahertz_myth)
- [NetBurst (Pentium 4 microarchitecture) — Wikipedia](https://en.wikipedia.org/wiki/NetBurst)

- [Intel top-down performance analysis](https://www.intel.com/content/www/us/en/docs/vtune-profiler/cookbook/2024-0/top-down-microarchitecture-analysis-method.html)
- [Linux perf project tutorial](https://perfwiki.github.io/main/tutorial/)
