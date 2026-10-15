---
id: isa-relative-address-reach
title: How far PC-relative instructions reach
level: intermediate
minutes: 3
sourceLesson: isa-risc-cisc
summary: Calculate the reference point and reach of RIP-relative and ADRP addressing.
---

How far can a PC-relative offset reach? A signed field of k bits (two's complement) holds half its patterns as negatives:

```formula
−2^{k−1} ≤ d ≤ 2^{k−1} − 1
where
d: the signed offset stored in the instruction
k: the width of the offset field, in bits
≤: less than or equal to
In words: a signed k-bit field runs from minus 2 to the power (k − 1) up to one less than plus that amount; the positive side is one short because zero takes one of the non-negative patterns.
```

A normal x86-64 RIP-relative operand has a 32-bit displacement (disp32), measured from the next instruction:

```formula
target = rip_next + d
−2^31 ≤ d ≤ 2^31 − 1
2^31 B = 2 GiB
where
target: the address being referred to
rip_next: the address of the instruction after this one (x86-64's instruction pointer, RIP, after the fetch)
d: the signed 32-bit displacement, in bytes
B: byte
GiB: gibibyte: 2^30 = 1,073,741,824 bytes
≤: less than or equal to
In words: a RIP-relative operand reaches from 2 GiB before the next instruction to 1 byte short of 2 GiB after it.
```

AArch64 `adrp` counts in 4 KiB pages from the current PC rounded down to a 4 KiB boundary:

```formula
PC_page = PC − (PC mod 4096)
target = PC_page + imm21 × 4096
−2^20 ≤ imm21 ≤ 2^20 − 1
where
PC_page: the address of the adrp instruction rounded down to a multiple of 4096
PC: the address of the adrp instruction itself
mod: modulo: the remainder after division, so PC mod 4096 is how far PC sits past a 4 KiB boundary
target: the start of the 4 KiB page being referred to
imm21: the signed 21-bit offset in the instruction, counted in 4 KiB units
4096: 4 KiB (kibibytes) = 4096 bytes, the unit adrp counts in
≤: less than or equal to
In words: adrp reaches about a million (1,048,576) 4 KiB pages either side of the current page, from 4 GiB below it to 4 KiB short of 4 GiB above it; a following instruction adds the low 12 bits of the exact address.
```

These are encoding units, not a requirement that the OS use 4 KiB pages.

## Key takeaways
- Signed offsets have an asymmetric negative and positive range.
- RIP-relative displacement starts from the next instruction.
- ADRP uses four-kibibyte encoding units, independently of the OS page size.

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
