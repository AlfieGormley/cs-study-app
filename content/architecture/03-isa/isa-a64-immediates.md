---
id: isa-a64-immediates
title: A64 immediates and building constants
level: intermediate
minutes: 3
sourceLesson: isa-risc-cisc
summary: Choose between immediate fields, move-wide sequences and literal pools.
---

### The price: immediates

A 32-bit instruction cannot encode every possible 64-bit constant. ARM64 offers several immediate formats:

| Instruction | Immediate allowed |
|---|---|
| `add`/`sub` | 12 bits (0–4095), optionally shifted left 12 |
| 64-bit `movz`/`movk` | 16 bits, placed at bit 0, 16, 32 or 48 |
| Immediate `and`/`orr` | repeated, rotated runs of ones and zeros within power-of-two-sized elements; neither all-zeros nor all-ones values are encodable |
| Unsigned-offset scalar `LDR`/`STR` | 12 bits, scaled by access size; other addressing forms differ |

How big can an unsigned immediate be? A field of k bits has 2 to the power k patterns, and the smallest is 0:

```formula
v_max = 2^k − 1
v_max = 2^12 − 1 = 4096 − 1 = 4095
v = imm12 × 2^12
v = 3 × 4096 = 12288
where
v_max: the largest value an unsigned k-bit field can hold
k: the width of the immediate field, in bits: 12 for add/sub
v: the constant actually added when the "shifted left 12" option is used
imm12: the 12-bit immediate field written in the instruction, 0 to 4095
2^12: 4096: shifting a number left by 12 bits multiplies it by 2^12
In words: 12 bits reach 0 to 4095; the shifted form multiplies the field by 4096, so it reaches exact multiples of 4096 up to 4095 × 4096 = 16,773,120.
```

So `add x0, x0, #4095` is one instruction but `#4097` will not assemble: 4097 is above 4095 and is not a multiple of 4096. A full 64-bit constant takes up to four instructions:

```
mov   x0, #0xcdef            // movz
movk  x0, #0x90ab, lsl #16   // keep rest
movk  x0, #0x5678, lsl #32
movk  x0, #0x1234, lsl #48
// x0 = 0x1234567890abcdef
```

Each `movk` drops a 16-bit chunk into place without disturbing the rest, so the register ends up holding:

```formula
x0 = c_0 + c_1 × 2^16
   + c_2 × 2^32 + c_3 × 2^48
where
x0: the 64-bit register being built
c_0, c_1, c_2, c_3: the four 16-bit chunks, lowest first: 0xcdef, 0x90ab, 0x5678 and 0x1234 (0x marks a hexadecimal number)
2^16, 2^32, 2^48: the place values of bit positions 16, 32 and 48: `lsl #16` (logical shift left by 16 bits) multiplies a chunk by 2^16 = 65,536
In words: the 64-bit constant is four 16-bit pieces placed side by side, each moved to its slot by a shift.
```

MOV aliases are assembler spellings for encodable instruction forms; they are not a promise that an arbitrary constant expands automatically into a sequence. A rejected immediate requires an explicit supported sequence.

Some odd-looking constants are cheap: `0xff00ff00ff00ff00` is a repeating pattern, so it fits one `orr`-based `mov`. Compilers also put large constants in a nearby **literal pool** and load them with one PC-relative `ldr`.

## Key takeaways
- Immediate encodings cannot represent every 64-bit value.
- ADD immediates use twelve bits with an optional twelve-bit shift.
- MOVZ and MOVK can assemble any 64-bit constant from sixteen-bit chunks.

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
