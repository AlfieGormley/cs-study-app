---
id: pipe-iron-law-ipc-and-knobs
sourceLesson: pipe-iron-law
title: IPC and the three performance knobs
level: basic
minutes: 3
summary: Read IPC and understand how algorithms, compilers, instruction sets and circuits affect the performance equation.
---

The previous unit combined instruction count, CPI and clock frequency to obtain CPU execution time. This unit reads the same counts as IPC and asks which design decisions change them. All comparisons still need matching measurement scopes.

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

A CPI of 0.5 is an IPC of 2. Both describe the same measured instruction/cycle totals; IPC is just more natural when the number is above 1. Linux's `perf stat` can report IPC when compatible counters are available and permitted. This is an illustrative, trimmed transcript, not a measurement performed for this lesson:

```
$ perf stat ./myprog
  3,000,000,000  cycles
  6,000,000,000  instructions
    # 2.00 insn per cycle
```

(Actual tool output and available events depend on the system.) Here 6,000,000,000 instructions divided by 3,000,000,000 cycles gives the 2.00 shown, which is a CPI of 0.5.

## Who controls which term?

The three terms are not independent knobs. Each is influenced by different people, and improving one often hurts another.

| Term | Mainly set by | Example |
|---|---|---|
| IC | Algorithm, compiler, ISA | Different sorting algorithms |
| CPI | Microarchitecture, compiler | Pipelining, caches |
| Clock period | Circuit design, process | Logic depth, voltage |

- **The algorithm** can substantially change the work required. Hardware instructions, accelerators and compiler transformations can also reduce architectural IC. The best improvement depends on the measured bottleneck.
- **The compiler** changes IC (removing redundant work, vectorising four additions into one instruction) and CPI (ordering instructions so they don't wait on each other).
- **The instruction set** (ISA) matters too. x86's `rep movsb` encodes a repeated byte copy using one instruction encoding. Implementation work and performance-event counting of repeated instructions need inspection; one compact encoding is not a count of the operations performed. Instruction count is not a fair standalone comparison across ISAs; counts also depend on vectorization and other instructions.
- **The microarchitecture** (how the chip implements the ISA) drives CPI: pipelining, branch prediction, out-of-order execution and caches all aim to lower it.
- **The circuit and process technology** set how short a cycle can be.

## Key takeaways
- IPC and CPI are reciprocals for the same counted instructions and cycles.
- Instruction count is dynamic, so source lines and executable size do not determine it.
- Changing an algorithm, compiler or implementation can affect more than one performance term.

## Further reading
- [Linux perf tutorial](https://perfwiki.github.io/main/tutorial/)
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
- [RISC-V unprivileged ISA specification](https://riscv.github.io/riscv-isa-manual/snapshot/spec/)

- [MIT: processor-performance equation and pipeline mechanics](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/pages/c15/c15s1/)
