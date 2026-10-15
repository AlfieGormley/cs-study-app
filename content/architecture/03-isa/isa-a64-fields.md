---
id: isa-a64-fields
title: Read an A64 instruction’s bit fields
level: intermediate
minutes: 3
sourceLesson: isa-risc-cisc
summary: Decode the fields of a concrete A64 add/sub instruction.
---

## Fixed-length encoding: ARM64

Every A64 instruction is exactly 32 bits. Here is `add x0, x0, x1`, which assembles to `0x8b010000`:

```
0x8b010000 = add x0, x0, x1

bits   field  value   meaning
31     sf     1       64-bit (x regs)
30     op     0       add (1 = sub)
29     S      0       don't set flags
28-24  fixed  01011   add/sub, shifted reg
23-22  shift  00      LSL
21     -      0
20-16  Rm     00001   x1
15-10  imm6   000000  shift amount 0
9-5    Rn     00000   x0
4-0    Rd     00000   x0
```

The general-purpose register fields in this format are 5 bits: encodings 0–30 name numbered registers, while 31 has instruction-dependent special meaning. The number of registers a field can name doubles with every bit:

```formula
R = 2^b
R = 2^5 = 32
where
R: the number of distinct bit patterns in the register field; one pattern has instruction-dependent special meaning
b: the width of the register field, in bits
In words: a 5-bit field has 32 possible patterns: 0 to 30 pick x0 to x30, and 31 picks the stack pointer or the zero register, depending on the instruction; the shifted-register form shown uses the zero register.
```

Regular field placement helps decoding, but not every A64 instruction uses this format. An exact Apple M1 decode-width claim is omitted because a primary hardware specification establishing it was not available in this review.

## Key takeaways
- Every A64 instruction is four bytes.
- The shown shifted-register format encodes its operation and three register fields.
- A five-bit register field has 32 patterns, with instruction-specific meaning for 31.

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
