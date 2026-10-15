---
id: isa-instruction-count-runtime
title: Instruction count is only one performance factor
level: intermediate
minutes: 3
sourceLesson: isa-risc-cisc
summary: Use the performance equation to compare instruction counts and clock costs.
---

## Who won?

Neither, really. The battle lines blurred:

- Many high-performance x86 cores decode instructions into internal **micro-ops** and execute them out of order. Neither out-of-order execution nor any particular micro-op format is mandated by x86; some x86 implementations are in-order.
- RISC ISAs grew complex instructions where they pay off: ARM64 has load/store pair (`ldp`/`stp`), atomic read-modify-write instructions, and SIMD and vector extensions.

Encoding, available operations, memory-ordering rules and compatibility requirements remain important differences. Do not infer a whole chip’s power consumption or performance from “RISC” or “CISC” alone.

A detailed account of market-share causes and a universal quantitative decoder-power comparison are omitted: these require evidence about particular products, workloads and periods, beyond the architectural contracts reviewed here.

## Pitfalls

- **"CISC is slower."** Instruction count is not speed. What matters is total run time, which the next module's iron law splits into three factors:

```formula
T = N CPI t_clk
where
T: the time the program takes to run, in seconds (s)
N: the number of instructions executed
CPI: cycles per instruction: the average number of clock cycles each instruction takes
t_clk: the clock period: the length of one clock cycle, in seconds; 1 nanosecond at 1 GHz
In words: run time is how many instructions run, times how many cycles each takes on average, times how long a cycle lasts.
```

At the same clock, 1 million instructions at an average of 2 cycles each take exactly as long as 2 million at 1 cycle each. Both styles have world-class implementations.
- **Counting instructions, not bytes.** Three ARM64 instructions can be the same size as one long x86 instruction.
- **Assuming any constant fits.** The A64 immediate ADD form accepts 0–4095, optionally shifted left 12. Other constants need a different sequence.
- **Forgetting x86 is two-operand.** `sub rax, rdi` subtracts RDI from RAX and overwrites RAX; reading it as three-operand gets the direction wrong.

## Key takeaways
- Instruction count, average cycles and clock period jointly determine run time.
- Internal micro-ops and out-of-order execution are implementation choices.
- Compare byte counts and actual workloads instead of predicting speed from ISA labels.

## Further reading
- [Reduced instruction set computer — Wikipedia](https://en.wikipedia.org/wiki/Reduced_instruction_set_computer)
- [Complex instruction set computer — Wikipedia](https://en.wikipedia.org/wiki/Complex_instruction_set_computer)
- [Addressing mode — Wikipedia](https://en.wikipedia.org/wiki/Addressing_mode)
- [x86 and amd64 instruction reference — Félix Cloutier](https://www.felixcloutier.com/x86/)
- [AArch64 — Wikipedia](https://en.wikipedia.org/wiki/AArch64)
- [RISC-V — Wikipedia](https://en.wikipedia.org/wiki/RISC-V)
- [Micro-operation — Wikipedia](https://en.wikipedia.org/wiki/Micro-operation)

### Primary references
- [Arm: A64 ISA and compilers](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/the-a64-isa-and-compilers)
- [Intel XED encoding documentation](https://github.com/intelxed/xed/blob/main/docsrc/xed-doc-top.txt)
- [RISC-V compressed extension specification](https://docs.riscv.org/reference/isa/v20260120/unpriv/c-st-ext.html)
- [IBM’s RISC history](https://www.ibm.com/history/risc)
