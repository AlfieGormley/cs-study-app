---
id: isa-reading-assembly
title: Reading x86-64 and ARM64 assembly
level: intermediate
minutes: 15
summary: The registers, syntax, flags and compiler idioms you need to read real x86-64 and ARM64 output from a compiler, debugger or profiler.
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
> Writing a 32-bit register **zeroes the upper 32 bits** of the 64-bit register. `mov eax, -1` leaves `rax = 0x00000000ffffffff`. Writing an 8- or 16-bit register leaves the other bits **unchanged**. Compilers lean on the first rule constantly: `mov eax, edi` is how they zero-extend a 32-bit value to 64 bits.

### ARM64

Thirty-one 64-bit registers `x0` to `x30`, each with a 32-bit view `w0` to `w30`. Writing a `w` register zeroes the upper 32 bits, like x86.

- `x29` is the frame pointer and `x30` the **link register** (return address).
- Register number 31 is either `sp` (stack pointer) or `xzr`/`wzr`, a **zero register** that reads as 0 and discards writes. Which one depends on the instruction.
- The PC is not a general register; you reach it through `adr` and branch instructions.
- Flags live in `NZCV`: Negative, Zero, Carry, oVerflow.

## Syntax: three dialects

You will meet Intel syntax, AT&T syntax and ARM syntax. Here is a representative implementation of `long f(long x) { return x * 5 + 7; }`, assuming 64-bit `long`, the System V x86-64 or AAPCS64 integer convention, and inputs without signed overflow:

```
# x86-64, Intel syntax (GCC/Clang)
f:
    lea   rax, [rdi + rdi*4 + 7]
    ret
```

```
# x86-64, AT&T syntax (GDB, objdump)
f:
    leaq  7(%rdi,%rdi,4), %rax
    ret
```

```
// ARM64
f:
    add   x8, x0, x0, lsl #2   // x8 = x*5
    add   x0, x8, #7
    ret
```

| | Intel | AT&T |
|---|---|---|
| Operand order | `dst, src` | `src, dst` |
| Registers | `rax` | `%rax` |
| Constants | `7` | `$7` |
| Memory | `[b + i*s + d]` | `d(b,i,s)` |
| Size | `qword ptr` | suffix `q`, `l`, `w`, `b` |

GNU GDB and GNU `objdump` normally default to AT&T on x86; `objdump -d -M intel` and GDB's `set disassembly-flavor intel` switch. This module uses Intel syntax with GNU assembler conventions (`#` comments) for x86, and standard syntax with `//` comments for ARM64. A64 instructions with an explicit result normally put the destination first; stores such as `str w0, [x1]` put the source register before the destination address.

## The core instructions

| Job | x86-64 | ARM64 |
|---|---|---|
| Copy | `mov` | `mov` |
| Load / store | `mov` with `[...]` | `ldr` / `str` |
| Address arithmetic | `lea` | `add`, `adr`, `adrp` |
| Arithmetic | `add sub imul neg` | `add sub mul neg` |
| Bitwise | `and or xor not shl shr sar` | `and orr eor mvn lsl lsr asr` |
| Compare | `cmp`, `test` | `cmp`, `tst` |
| Branch | `jmp`, `jcc` | `b`, `b.cond`, `cbz`, `cbnz` |
| Call / return | `call`, `ret` | `bl`, `ret` |
| Conditional select | `cmovcc`, `setcc` | `csel`, `cset`, `cinc` |

## Flags and conditional branches

Flag-based branches such as x86 `jcc` and A64 `b.cond` read flags set by an earlier instruction. Other branches test a register directly, such as A64 `cbz`/`cbnz` and `tbz`/`tbnz`.

- `cmp a, b` computes `a - b`, sets flags and throws the result away.
- `test a, b` computes `a & b`, sets flags and throws the result away. `test rax, rax` is the idiomatic "is rax zero or negative?" check.
- Ordinary arithmetic (`add`, `sub`, `and`) sets flags too on x86. On ARM64 ordinary ADD/SUB/AND leave flags unchanged unless using the flag-setting forms: `adds`, `subs`, `ands`, plus `cmp` and `tst`.

After `cmp a, b`, choose the branch by **signedness**:

| Meaning | x86 signed / unsigned | ARM64 signed / unsigned |
|---|---|---|
| a > b | `jg` / `ja` | `b.gt` / `b.hi` |
| a >= b | `jge` / `jae` | `b.ge` / `b.hs` |
| a < b | `jl` / `jb` | `b.lt` / `b.lo` |
| a <= b | `jle` / `jbe` | `b.le` / `b.ls` |
| a == b | `je` | `b.eq` |

For these same-width integer comparisons, signedness determines which condition code interprets the flags. It can also affect earlier conversions and instruction selection. The bits in the register are the same; `jg` tests the sign, overflow and zero flags, while `ja` tests the carry and zero flags.

## A worked example: counting positives

```
long count_pos(const long *a, long n) {
    long c = 0;
    for (long i = 0; i < n; i++)
        if (a[i] > 0) c++;
    return c;
}
```

The following is an illustrative scalar implementation, not a promise of exact output from any compiler version. Assume 64-bit `long` and a valid array of at least `n` elements when `n > 0`. Arguments arrive in `rdi` (`a`) and `rsi` (`n`); the result goes in `rax`. The calling-convention lesson explains why.

```
# long count_pos(const long *a, long n)
count_pos:
    xor   eax, eax         # c = 0
    test  rsi, rsi
    jle   .Ldone           # n <= 0: done
    xor   ecx, ecx         # i = 0
.Lloop:
    xor   edx, edx         # edx = 0
    cmp   qword ptr [rdi + rcx*8], 0
    setg  dl               # dl = (a[i] > 0)
    add   rax, rdx         # c += dl
    inc   rcx              # i++
    cmp   rcx, rsi
    jne   .Lloop           # i != n
.Ldone:
    ret
```

How to read it:

1. **Find the loop.** Here, the backward branch (`jne .Lloop`) forms a loop. In arbitrary code, inspect the control-flow paths rather than assuming every backward branch means a source-level loop. Everything between `.Lloop` and the branch is the body.
2. **Find the induction variable.** `rcx` starts at 0, is incremented, and is compared with `n`: that is `i`.
3. **Find the memory access.** `[rdi + rcx*8]` is `a[i]` with 8-byte elements.
4. **Notice there is no branch for the `if`.** `setg dl` turns "greater than" into a 0 or 1, and `add` adds it. The compiler replaced an unpredictable branch with arithmetic. `edx` is cleared *before* the `cmp`, because `xor` itself changes the flags.
5. **Find the return value.** `rax` is set to 0 at the top and accumulates `c`.

An equivalent A64 implementation:

```
// long count_pos(const long *a, long n)
count_pos:
    mov   x8, #0           // c = 0
    cmp   x1, #1
    b.lt  .Ldone           // n < 1: done
.Lloop:
    ldr   x9, [x0], #8     // x9 = *a++
    cmp   x9, #0
    cinc  x8, x8, gt       // if > 0: c++
    subs  x1, x1, #1       // n--, set flags
    b.ne  .Lloop
.Ldone:
    mov   x0, x8
    ret
```

The same ideas, with different instruction choices: this version rewrites `a[i]` as a pointer walk using a post-indexed load, counted `n` down to zero with `subs` (which sets the flags `b.ne` reads), and used `cinc` (conditional increment) instead of a branch.

## Idioms that look strange at first

| You see | It means |
|---|---|
| `xor eax, eax` | `eax = 0` (2 bytes, and many cores recognize a dependency-breaking zero idiom) |
| `test rdi, rdi` then `je` | `if (rdi == 0)` |
| `lea eax, [rdi + rdi*2]` | `eax = low32(rdi * 3)`, no memory access |
| `movsxd rax, edi` / `sxtw x0, w0` | sign-extend 32 to 64 bits (an `int` to 64-bit `long` here) |
| `mov eax, edi` / `mov w0, w0` | zero-extend `unsigned` to 64 bits |
| `cmovg`, `csel` | branch-free `a > b ? a : b` |
| `nop`, `nop dword ptr [rax]` | padding to align a loop or function |
| `endbr64` / `bti c` | landing pad for control-flow protection (lesson 6) |

### Division by a constant

Division can be more expensive than a suitable multiply/shift sequence; costs depend on the instruction and core. Signed `x / 2` must round towards zero, but an arithmetic right shift rounds towards minus infinity (the machine’s arithmetic shift of −7 by one yields −4; negative signed right shift in C17 is implementation-defined). So the compiler adds 1 to negative numbers first:

```
# int half(int x) { return x / 2; }
half:
    mov   eax, edi
    shr   eax, 31        # 1 if x<0 else 0
    add   eax, edi       # bias negatives
    sar   eax, 1         # arithmetic shift
    ret
```

For `x = -7`: the bias is 1, `-7 + 1 = -6`, and `-6 >> 1 = -3`, which is correct. For non-power-of-two divisors such as 10, compilers multiply by a "magic" reciprocal constant and shift. If you see a large odd constant and an `imul` where you expected a division, division by a constant is one possibility; confirm the complete sequence before drawing that conclusion.

### Branch-free max

```
# int max(int a, int b)
max:
    mov   eax, esi       # eax = b
    cmp   edi, esi       # compare a with b
    cmovg eax, edi       # if a > b: eax = a
    ret
```

```
// int max(int a, int b)
max:
    cmp   w0, w1
    csel  w0, w0, w1, gt   // a > b ? a : b
    ret
```

## Practical reading tips

- **Compile at `-O1` or `-O2` to learn.** `-O0` output often stores locals to the stack and reloads them, which is accurate but noisy.
- **Start at the end.** For a simple integer result, look for `rax`/`x0` before `ret`; other return types follow different ABI rules.
- **Map arguments first.** For ordinary fixed-parameter integer/pointer arguments under the conventions shown: `rdi, rsi, rdx, rcx, r8, r9` on x86-64 and `x0`–`x7` on ARM64.
- **Look for backward branches** to find loops, and **scaled addressing** to find array indexing.
- **Use the tools.** `objdump -d -M intel prog`, GDB's `disassemble` and `layout asm`, `perf annotate` for hot instructions.

## Pitfalls

- **Mixing up AT&T and Intel order.** `sub %rdi, %rax` is `rax -= rdi`. Check for `%` signs before reading.
- **Reading `cmp` backwards.** In Intel x86 syntax and A64 syntax, `cmp a, b` then "greater than" means `a > b`.
- **Assuming flags survive.** On x86 nearly every arithmetic instruction overwrites them; `mov` and `lea` do not, which is one reason compilers like `lea`.
- **Treating `inc` like `add 1`.** On x86, `inc` leaves the carry flag unchanged.
- **Forgetting zero-extension.** `mov eax, ...` silently clears the top of `rax`; `mov al, ...` does not.

## Key takeaways
- Baseline x86-64 has 16 GPRs (`rax`…`r15`) with 32/16/8-bit views; ARM64 has `x0`–`x30` plus `sp` and the zero register.
- Writing a 32-bit register zero-extends into the 64-bit register on both ISAs.
- Intel syntax is `dst, src`; AT&T is `src, dst` with `%` and `$`; A64 arithmetic normally places the result first; stores instead place their source register first.
- Flag-based branches read flags set by an earlier `cmp`/`test`/`subs`; signed and unsigned comparisons use different condition codes.
- Recognise idioms: `xor` zeroing, `lea` arithmetic, `setcc`/`cmov`/`csel`/`cinc` for branch-free code, shift-and-bias for signed division.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [x86 and amd64 instruction reference — Félix Cloutier](https://www.felixcloutier.com/x86/)
- [x86-64 machine-level programming — CMU handout (PDF)](https://www.cs.cmu.edu/~fp/courses/15213-s07/misc/asm64-handout.pdf)
- [X86-64 — Wikipedia](https://en.wikipedia.org/wiki/X86-64)
- [AArch64 — Wikipedia](https://en.wikipedia.org/wiki/AArch64)
- [FLAGS register — Wikipedia](https://en.wikipedia.org/wiki/FLAGS_register)
