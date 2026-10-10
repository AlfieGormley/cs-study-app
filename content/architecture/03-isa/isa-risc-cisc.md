---
id: isa-risc-cisc
title: RISC vs CISC, instruction encoding and addressing modes
level: intermediate
minutes: 14
summary: How instructions are packed into bits on ARM64 and x86-64, why one is fixed-length and the other is not, the addressing modes both offer, and why the RISC vs CISC war mostly ended in a truce.
---

An instruction is a number. The previous lesson's toy machine put the operation in the hundreds digit of a decimal number and the address in the last two digits. Real ISAs pack the operation, registers, constants and addressing information into bit fields. How they do that, and how much one instruction is allowed to do, splits ISAs into two broad families.

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
R: how many different registers a register field can name
b: the width of the register field, in bits
In words: a 5-bit field has 32 possible patterns: 0 to 30 pick x0 to x30, and 31 picks the stack pointer or the zero register, depending on the instruction.
```

Regular field placement helps decoding, but not every A64 instruction uses this format. An exact Apple M1 decode-width claim is omitted because a primary hardware specification establishing it was not available in this review.

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

Some odd-looking constants are cheap: `0xff00ff00ff00ff00` is a repeating pattern, so it fits one `orr`-based `mov`. Compilers also put large constants in a nearby **literal pool** and load them with one PC-relative `ldr`.

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

Note that x86 arithmetic is mostly **two-operand**: `add rax, rdi` means `rax = rax + rdi`, destroying the old `rax`. ARM64 is **three-operand**: `add x0, x1, x2` leaves both distinct source registers intact. x86 also has three-operand instruction families, including AVX and APX forms; do not generalize the legacy ADD syntax to the whole ISA.

### Why variable length hurts and helps

- It helps **code density**: short encodings can reduce instruction-cache footprint; actual code density depends on the instruction mix.
- It hurts **instruction decoding**: the decoder cannot know where the next instruction starts until it has worked out the length of the current one. Boundary detection adds work, although predecoding and parallel candidate decoding can help. Some x86 cores cache decoded **micro-ops**; this is not an ISA requirement or a universal core feature.

RISC ISAs claw back density with compressed formats: ARM's 16/32-bit Thumb-2 (on 32-bit ARM) and RISC-V's "C" extension of 16-bit instructions.

## Addressing modes

An **addressing mode** is a rule for where an operand comes from. Here are the common ones, with `x86-64` and `ARM64` examples:

| Mode | x86-64 | ARM64 |
|---|---|---|
| Immediate | `mov eax, 5` | `mov w0, #5` |
| Register | `mov rax, rdi` | `mov x0, x1` |
| Register indirect | `[rdi]` | `[x0]` |
| Base + displacement | `[rdi + 8]` | `[x0, #8]` |
| Base + scaled index | `[rdi + rsi*4]` | `[x0, x1, lsl #2]` |
| PC-relative | `[rip + label]` | `adr`, `adrp`, literal `ldr` |
| General load/store pre-/post-index | no general bracket form; string/stack instructions can update pointers implicitly | `[x0, #8]!` / `[x0], #8` |

The **effective address** is the address the mode computes. The most general x86 memory operand adds a base, a scaled index and a displacement. Take this operand with `rdi = 0x1000` and `rsi = 3`:

```
[rdi + rsi*4 + 8]
```

```formula
EA = base + index × scale + disp
EA = 0x1000 + 3 × 4 + 8
EA = 0x1000 + 20 = 0x1014
where
EA: the effective address: the memory address the instruction actually reads or writes
base: the value in the base register, here rdi = 0x1000 (hexadecimal, 4096 in decimal)
index: the value in the index register, here rsi = 3
scale: a constant multiplier written into the instruction: 1, 2, 4 or 8 on x86; here 4, the size of an `int`
disp: the displacement: a constant offset in bytes written into the instruction, here 8
In words: start at the base address, step over index elements of scale bytes each, then add a fixed offset; 20 in decimal is 0x14, giving 0x1014.
```

Each part is optional: drop the index for base + displacement, drop the displacement for base + scaled index.

What each mode is for:

- **Base + displacement**: struct fields (`p->next` could be `[p + 8]` for a layout with that field offset) and stack slots (`[rsp + 24]`).
- **Scaled index**: arrays. Scales are 1, 2, 4 or 8 on x86, matching element sizes.
- **PC-relative**: globals and constants, so code works wherever it is loaded (position-independent code, lesson 6). Its reach is limited by the signed offset field; the reach formulas follow this list.
- **Pre/post-index**: ARM64 updates the base register as a side effect. `ldr w9, [x0], #4` loads `*x0` then adds 4 to `x0`: a pointer walk in one instruction. With `[x0, #-16]!`, the base is updated first, which is how ARM64 pushes onto the stack.

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

> [!tip] `lea` is the address calculator
> x86's `lea` (load effective address) computes the address and puts it in a register *without touching memory*. Compilers use it as a shift-and-add that preserves flags (it still consumes execution resources): `lea rax, [rdi + rdi*4 + 7]` multiplies by 5 and adds 7 in one instruction, as the formula below shows.

```formula
rax = x + x × 4 + 7
rax = 5 × x + 7
where
rax: the destination register, which receives the computed number
x: the input value held in register rdi
In words: the address arithmetic adds x to four times x, then 7, so with x = 10 the result is 57, and no memory is read.
```

## Who won?

Neither, really. The battle lines blurred:

- Many high-performance x86 cores decode instructions into internal **micro-ops** and execute them out of order. Neither out-of-order execution nor any particular micro-op format is mandated by x86; some x86 implementations are in-order.
- RISC ISAs grew complex instructions where they pay off: ARM64 has load/store pair (`ldp`/`stp`), atomic read-modify-write instructions, and SIMD and vector extensions.

Encoding, available operations, memory-ordering rules and compatibility requirements remain important differences. Do not infer a whole chip’s power consumption or performance from “RISC” or “CISC” alone.

A detailed account of market-share causes and a universal quantitative decoder-power comparison are omitted: these require evidence about particular products, workloads and periods, beyond the architectural contracts reviewed here.

## Pitfalls

- **"CISC is slower."** Instruction count is not speed. What matters is total run time, which the next module's iron law splits into three factors:

```formula
T = N × CPI × t_clk
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
- **Forgetting x86 is two-operand.** `sub rax, rdi` computes `rax - rdi` into `rax`; reading it as three-operand gets the direction wrong.

## Key takeaways
- RISC and CISC are broad design traditions. Load/store organization and regular formats are common RISC traits, with exceptions such as compressed encodings and atomic operations.
- A64 instructions are 32 bits with regular instruction formats; large constants need `movz`/`movk` sequences or a literal pool.
- x86-64 instructions are 1–15 bytes; the legacy/REX examples use opcode, optional ModRM/SIB, displacement and immediate fields. Newer prefix families add encoding forms.
- Addressing modes map to program structure: base+displacement for fields and stack slots, scaled index for arrays, PC-relative for globals.
- Many modern x86 cores use internal micro-ops, and RISC ISAs gained complex instructions, so the distinction today is mostly about decode cost, density and history.

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
