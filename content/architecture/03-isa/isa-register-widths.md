---
id: isa-register-widths
title: Register names, views and zero extension
level: intermediate
minutes: 3
sourceLesson: isa-reading-assembly
summary: Read x86 and AArch64 register names and track writes at different widths.
---

Very few engineers write assembly. Many more need to **read** it: a crash in a release build with no debug symbols, a `perf` profile pointing at one hot loop, checking whether the compiler vectorised something, or reverse engineering a binary. The goal of this lesson is to make compiler output readable, not to make you an assembly programmer.

The best way to practise is [Compiler Explorer](https://godbolt.org/): type C on the left, see assembly for any compiler and target on the right, with colour-matched lines.

## The registers

### x86-64

Baseline x86-64 provides sixteen 64-bit general-purpose registers; APX adds more on supporting implementations. The first eight have historical names; the 64-bit extension added `r8` to `r15`. Each can be used at smaller widths:

| 64-bit | 32 | 16 | 8 |
|---|---|---|---|
| `rax` | `eax` | `ax` | `al` |
| `rdi` | `edi` | `di` | `dil` |
| `rsp` | `esp` | `sp` | `spl` |
| `r8` | `r8d` | `r8w` | `r8b` |

The others follow the same pattern: `rbx`, `rcx`, `rdx`, `rsi`, `rbp`, `r9`–`r15`. `rsp` is the stack pointer. `rip` is the instruction pointer. `rflags` holds condition flags.

> [!warning] The 32-bit write rule
> Writing a 32-bit register **zeroes the upper 32 bits** of the 64-bit register. `mov eax, -1` leaves RAX holding 0x00000000ffffffff. Writing an 8- or 16-bit register leaves the other bits **unchanged**. Compilers lean on the first rule constantly: `mov eax, edi` is how they zero-extend a 32-bit value to 64 bits.

Why does −1 become `0xffffffff`? In two's complement, a negative 32-bit value is stored as the unsigned pattern 4,294,967,296 higher (one more than the largest 32-bit number):

```formula
u = v + 2^32   for v < 0
u = −1 + 4294967296 = 4294967295
u = 0xffffffff
where
u: the unsigned number formed by the 32 stored bits
v: the signed value written, here −1
2^32: 4,294,967,296, the number of different 32-bit patterns
<: less than
In words: −1 in 32 bits is the all-ones pattern, 0xffffffff in hexadecimal; writing it to eax clears the top half of rax, so rax holds 4,294,967,295, not −1.
```

### ARM64

Thirty-one 64-bit registers `x0` to `x30`, each with a 32-bit view `w0` to `w30`. Writing a `w` register zeroes the upper 32 bits, like x86.

- `x29` is the frame pointer and `x30` the **link register** (return address).
- Register number 31 is either `sp` (stack pointer) or `xzr`/`wzr`, a **zero register** that reads as 0 and discards writes. Which one depends on the instruction.
- The PC is not a general register; you reach it through `adr` and branch instructions.
- Flags live in `NZCV`: Negative, Zero, Carry, oVerflow.

## Key takeaways
- A 32-bit register write clears the upper half on both ISAs.
- x86 byte and sixteen-bit writes preserve the remaining bits.
- AArch64 register encoding 31 is instruction-dependent: stack pointer or zero.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [x86 and amd64 instruction reference — Félix Cloutier](https://www.felixcloutier.com/x86/)
- [x86-64 machine-level programming — CMU handout (PDF)](https://www.cs.cmu.edu/~fp/courses/15213-s07/misc/asm64-handout.pdf)
- [X86-64 — Wikipedia](https://en.wikipedia.org/wiki/X86-64)
- [AArch64 — Wikipedia](https://en.wikipedia.org/wiki/AArch64)
- [FLAGS register — Wikipedia](https://en.wikipedia.org/wiki/FLAGS_register)
