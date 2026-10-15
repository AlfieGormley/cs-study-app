---
id: pipe-five-stage-regular-isa-and-depth
sourceLesson: pipe-five-stage
title: Regular encodings and deeper pipelines
level: basic
minutes: 3
summary: Explain which ISA properties simplify pipelining and why splitting one stage changes the bottleneck.
---

The previous units showed that the slowest stage sets the pipeline period. This unit asks what makes fetching and decoding manageable, and what changes when a designer adds stages. These are implementation choices; the ISA alone does not prescribe one pipeline.

## Why RISC was designed for this

Regular encodings and load/store operations, as in the base RISC teaching model here, simplify pipeline design:

- **Fixed-length base instructions** (32 bits in the model; compressed forms such as RISC-V C differ) let IF fetch one per cycle and let ID start decoding before it knows what the instruction is.
- **Register specifiers** in regular positions across formats, allow register selection alongside opcode decoding.
- **Load/store data operations**: ordinary arithmetic in this model uses registers; separate loads and stores transfer data. Instruction fetch and specialised atomic operations are outside that simplification.
- **Naturally aligned scalar accesses** avoid line splits when their power-of-two size does not exceed the line size and divides it. Real ISAs can also allow unaligned accesses, with additional handling.

x86, with variable-length instructions from 1 to 15 bytes and memory operands on arithmetic, needs additional instruction-boundary and operand handling relative to this simplified fixed-width, load/store teaching design. Many Intel and AMD implementations translate x86 instructions into simple, RISC-like **micro-operations** (µops), and pipeline those.

## Real pipelines

The five-stage design is a teaching model. Real implementations divide work differently, and “pipeline depth” may refer to different instruction paths or recovery events. A cross-product table of stage counts is omitted because comparable primary documentation was not established for every entry.

Splitting a critical stage can shorten the clock period, while adding register overhead and potentially delaying particular result or branch-resolution paths. Not every hazard penalty necessarily increases: that depends on where stages are added and which bypass paths exist.

## Where it goes wrong

The ideal "one instruction per cycle" assumes every instruction can enter the pipeline the cycle after the previous one. Three things break that:

- **Structural hazards**: two instructions need the same hardware in the same cycle.
- **Data hazards**: an instruction needs a result the previous one hasn't produced yet.
- **Control hazards**: after a branch, the CPU doesn't know which instruction to fetch next.

The following hazard units cover each kind and the tricks, chiefly **forwarding**, that keep this pipeline flowing.

## Key takeaways
- Regular register fields and load/store data operations simplify the teaching pipeline.
- RISC-V compressed instructions and real unaligned accesses need extra handling.
- Splitting one stage helps only until another path or overhead sets the period.

## Further reading
- [RISC-V unprivileged ISA specification](https://riscv.github.io/riscv-isa-manual/snapshot/spec/)
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
- [BOOM implementation: pipeline](https://docs.boom-core.org/en/latest/sections/intro-overview/boom-pipeline.html)

- [Intel implementation and optimisation manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel64-and-ia32-architectures-optimization.html)
