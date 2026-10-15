---
id: isa-x86-byte-decoding
title: Decode variable-length x86 instructions
level: intermediate
minutes: 3
sourceLesson: isa-risc-cisc
summary: Read REX, opcode and ModRM bytes and compare encoding trade-offs.
---

## Variable-length encoding: x86-64

x86 instructions are anywhere from 1 to 15 bytes. A common legacy/REX encoding uses these pieces. This is a schematic, not the complete encoding grammar: VEX, EVEX and APX/REX2 add other forms, and not every combination below is valid.

```
field      size     purpose
prefixes   varies   lock, rep, size...
REX        0-1 B    64-bit, r8-r15
opcode     1-3 B    the operation
ModRM      0-1 B    operand registers
SIB        0-1 B    base + index*scale
disp       0-4 B    displacement
imm        0-8 B    immediate
```

- **REX** (`0x40`–`0x4F`) was added for 64-bit mode: its W bit selects 64-bit operands and three more bits extend register numbers from 3 bits (8 registers) to 4 bits (16 registers), by the same doubling rule as the A64 register fields.
- **ModRM** says which register and which memory or register operand: `mod` (2 bits), `reg` (3), `rm` (3).
- **SIB** (scale, index, base) describes a base register plus an index register multiplied by a scale (see the effective-address formula below).
- **disp** and **imm** are a displacement and an immediate constant.

Some real encodings:

| Instruction | Bytes |
|---|---|
| `ret` | `c3` |
| `push rbp` | `55` |
| `add rax, rdi` | `48 01 f8` |
| `mov eax, 1` | `b8 01 00 00 00` |
| `mov dword ptr [rax+rbx*4+16], 5` | `c7 44 98 10 05 00 00 00` |
| `movabs rax, 0x1122334455667788` | `48 b8` + 8 bytes |

### Decoding `48 01 f8` by hand

```
48  REX: 0100 W=1 R=0 X=0 B=0
    W=1 -> 64-bit operand size
01  opcode: ADD r/m64, r64
f8  ModRM: 11 111 000
    mod=11 -> rm is a register
    reg=111 -> rdi (source)
    rm =000 -> rax (destination)
=> add rax, rdi
```

Note that x86 arithmetic is mostly **two-operand**: `add rax, rdi` means add RDI into RAX, destroying the old `rax`. ARM64 is **three-operand**: `add x0, x1, x2` leaves both distinct source registers intact. x86 also has three-operand instruction families, including AVX and APX forms; do not generalize the legacy ADD syntax to the whole ISA.

### Why variable length hurts and helps

- It helps **code density**: short encodings can reduce instruction-cache footprint; actual code density depends on the instruction mix.
- It hurts **instruction decoding**: the decoder cannot know where the next instruction starts until it has worked out the length of the current one. Boundary detection adds work, although predecoding and parallel candidate decoding can help. Some x86 cores cache decoded **micro-ops**; this is not an ISA requirement or a universal core feature.

RISC ISAs claw back density with compressed formats: ARM's 16/32-bit Thumb-2 (on 32-bit ARM) and RISC-V's "C" extension of 16-bit instructions.

## Key takeaways
- Legacy x86 encodings combine optional prefixes and operand fields.
- Decode ModRM together with REX and the opcode.
- Variable length can improve density while adding boundary-detection work.

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
