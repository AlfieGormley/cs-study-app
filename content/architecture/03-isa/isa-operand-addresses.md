---
id: isa-operand-addresses
title: Addressing modes, pointer updates and LEA
level: intermediate
minutes: 4
sourceLesson: isa-risc-cisc
summary: Trace scaled addresses, post-indexed loads and arithmetic using LEA.
---

The examples use Intel syntax for x86-64 and A64 syntax for AArch64. Register contents and byte-sized element widths are stated for each address calculation.

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
- **PC-relative**: globals and constants, so code works wherever it is loaded (position-independent code, covered in the later linking units). Its reach is limited by the signed offset field; the next unit develops the reach formulas.
- **Pre/post-index**: ARM64 updates the base register as a side effect. `ldr w9, [x0], #4` loads `*x0` then adds 4 to `x0`: a pointer walk in one instruction. With `[x0, #-16]!`, the base is updated first, which is how ARM64 pushes onto the stack.

> [!tip] `lea` is the address calculator
> x86's `lea` (load effective address) computes the address and puts it in a register *without touching memory*. Compilers use it as a shift-and-add that preserves flags (it still consumes execution resources): `lea rax, [rdi + rdi*4 + 7]` multiplies by 5 and adds 7 in one instruction, as the formula below shows.

```formula
rax = x + x × 4 + 7
rax = 5x + 7
where
rax: the destination register, which receives the computed number
x: the input value held in register rdi
In words: the address arithmetic adds x to four times x, then 7, so with x = 10 the result is 57, and no memory is read.
```

These formulas describe values that fit the destination. At machine width, LEA and integer arithmetic keep the permitted low bits; the 32-bit LEA form also clears the upper half of its destination register.

## Key takeaways
- Effective addresses combine a base, scaled index and displacement.
- AArch64 pre/post-index forms update their base register.
- LEA computes address arithmetic without loading memory or changing flags.

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
