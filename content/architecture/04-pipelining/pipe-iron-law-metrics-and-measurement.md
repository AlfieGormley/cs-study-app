---
id: pipe-iron-law-metrics-and-measurement
sourceLesson: pipe-iron-law
title: Avoid misleading performance metrics
level: basic
minutes: 4
summary: Distinguish task completion time from the MIPS rating, clock frequency and peak throughput scores.
---

Earlier units established CPU execution time, IPC and weighted CPI. This unit tests performance headlines against those definitions. The examples remain hypothetical fixed-frequency measurements unless explicitly identified otherwise.

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
In words: the MIPS rating is the instruction count divided by the time, in millions; equivalently, the clock rate divided by CPI.
```

As a throughput score it does not account for how many instructions the task requires, so it rewards a machine or compiler that runs lots of cheap instructions. For example, on a 1 GHz CPU, compiler P emits 1.2 × 10⁹ instructions at CPI 1.0, and compiler Q emits 0.6 × 10⁹ instructions at CPI 1.5:

```formula
T_P = (1.2 × 10^9 × 1.0) / (10^9 Hz)
T_P = 1.2 s
MIPS_P = (1.2 × 10^9) / (1.2 s × 10^6)
MIPS_P = 1000
T_Q = (0.6 × 10^9 × 1.5) / (10^9 Hz)
T_Q = 0.9 s
MIPS_Q = (0.6 × 10^9) / (0.9 s × 10^6)
MIPS_Q ≈ 667
where
T_P, T_Q: the run times of the code from compilers P and Q, in seconds (s), from instruction count × CPI / clock frequency
MIPS_P, MIPS_Q: each version's score in millions of instructions per second
Hz: hertz, cycles per second; the clock is 1 GHz = 10^9 Hz
s: seconds
≈: approximately equal to (rounded)
In words: Q finishes first while scoring a third lower on the MIPS rating, because it simply needs fewer instructions.
```

A MIPS rating can describe instruction throughput, but it predicts task completion time only when the relevant dynamic instruction counts are fixed. The same binary can still execute different counts on different inputs or execution paths.

### Peak numbers

Vendors quote peak IPC or peak FLOPS: what the chip can do if every functional unit is busy every cycle. Real code waits on memory and mispredicted branches. Realized IPC depends on instruction mix, dependency chains, front-end delivery, memory behaviour and prediction. No universal IPC value or dominant bottleneck is asserted for databases or web servers.

> [!tip] Measure, don't guess
> `perf stat` gives you cycles, instructions and IPC for a real run. Low IPC alone does not identify the cause: serial arithmetic dependencies, execution-unit pressure, front-end limits, branch recovery and memory stalls can all contribute. Use architecture-specific counters and profiles before choosing a fix.

## How the performance techniques fit

Every technique in the following lessons attacks one term of the iron law, and usually costs something in another:

- **Pipelining** overlaps instructions so CPI approaches 1 and the clock can be shorter. Cost: hazards.
- **Forwarding and branch prediction** claw back the CPI lost to hazards.
- **Superscalar and out-of-order** execution push CPI below 1 (IPC above 1). Cost: area, power and complexity.
- **Power and thermal limits** constrained frequency scaling and encouraged multicore designs. Frequency did not stop increasing altogether. Multiple cores can improve throughput and can reduce the time of a parallelizable single job.

## Key takeaways
- The MIPS rating measures instruction throughput and predicts time only when the relevant dynamic count is fixed.
- Peak IPC or FLOPS needs a workload and a stated counting convention.
- Low IPC suggests investigation, not a unique bottleneck diagnosis.

## Further reading
- [Linux perf tutorial](https://perfwiki.github.io/main/tutorial/)
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
- [Intel: top-down analysis](https://www.intel.com/content/www/us/en/docs/vtune-profiler/cookbook/2024-0/top-down-microarchitecture-analysis-method.html)

- [MIT: processor-performance equation and pipeline mechanics](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/pages/c15/c15s1/)
