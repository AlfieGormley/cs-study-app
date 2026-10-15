---
id: isa-risc-cisc-traditions
title: RISC, CISC and load/store organisation
level: intermediate
minutes: 3
sourceLesson: isa-risc-cisc
summary: Compare the same non-atomic update on x86-64 and AArch64.
---

An instruction is a number. The earlier toy machine put the operation in the hundreds digit of a decimal number and the address in the last two digits. Real ISAs pack the operation, registers, constants and addressing information into bit fields. How they do that, and how much one instruction is allowed to do, splits ISAs into two broad families.

## Two philosophies

**CISC** (complex instruction set computer) is the older style: VAX, Motorola 68000, and Intel x86. In the 1970s memory was expensive and compilers were weak, so designers made each instruction do a lot. One instruction could load from memory, do arithmetic and store the result. Instructions had many lengths, so common ones could be short.

**RISC** (reduced instruction set computer) grew from research in the 1970s and 1980s, including IBM's 801, Berkeley RISC (which led to SPARC) and Stanford MIPS. Their measurements showed compilers mostly used simple instructions anyway. So they designed ISAs that were:

- **Load/store**: ordinary ALU operations use registers/immediates, with separate memory-transfer instructions. Atomic read-modify-write instructions are an important extension.
- **Fixed-length encoding**: often a 32-bit base encoding, simplifying boundary detection; compressed extensions are exceptions.
- **Register-rich**: typically a relatively large register file, reducing register spills; exact counts vary by ISA.
- **Regular**: few formats, so the hardware is simple and easy to pipeline.

ARM64 (AArch64), RISC-V, MIPS and POWER are RISC. x86-64 is CISC.

### The same statement both ways

Take `a[i] += 1` where `a` points to 32-bit integers, the index is in range and the increment does not overflow a signed C `int`. These are ordinary non-atomic updates. On x86-64 one instruction does it, with a memory operand:

```
# rdi = a, rsi = i
add  dword ptr [rdi + rsi*4], 1
```

Using ordinary AArch64 load, add and store instructions takes three:

```
// x0 = a, x1 = i
ldr  w8, [x0, x1, lsl #2]   // w8 = a[i]
add  w8, w8, #1
str  w8, [x0, x1, lsl #2]   // a[i] = w8
```

The shown x86 encoding is 4 bytes; the A64 sequence is 12. The x86 instruction still requires a read, arithmetic and a write internally; the number and fusion of micro-ops depend on the core. A single memory-operand instruction is not automatically an atomic inter-thread increment.

> [!note] "Reduced" is about complexity, not count
> RISC does not mean few instructions. ARM64 has hundreds, including SIMD, crypto and atomics. The label describes design tendencies, not a rule that every instruction does only one simple operation. AArch64 includes atomic read-modify-write and other specialized operations.

## Key takeaways
- RISC and CISC describe design traditions rather than performance rankings.
- Ordinary AArch64 arithmetic uses registers and separate loads/stores.
- A single x86 memory update still performs a read, arithmetic and a write.

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
