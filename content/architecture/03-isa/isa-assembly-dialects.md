---
id: isa-assembly-dialects
title: Read Intel, AT&T and A64 syntax
level: intermediate
minutes: 4
sourceLesson: isa-reading-assembly
summary: Translate operand order and recognise the main instruction families.
---

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

Both memory spellings describe the same effective address:

```formula
EA = b + i × s + d
where
EA: the effective address: the memory address the operand points at
b: the value in the base register
i: the value in the index register
s: the scale: 1, 2, 4 or 8
d: the displacement: a constant byte offset
In words: Intel writes [b + i*s + d] and AT&T writes d(b,i,s); both mean base plus scaled index plus offset, so AT&T's 7(%rdi,%rdi,4) is rdi + rdi × 4 + 7.
```

All three listings compute the same number. The ARM64 version builds five times x from a shift: `lsl #2` (logical shift left by 2 bits) multiplies by 4.

```formula
x8 = x0 + x0 × 2^2 = 5 × x0
x0_out = 5x0 + 7
x0_out = 5 × 10 + 7 = 57
where
x0: the argument x, which arrives in register x0
x8: a scratch register holding 5 × x
x0_out: the return value, written back into x0
2^2: 4: shifting left by 2 bits multiplies by 4
In words: x plus four times x is five times x; add 7 and return it, so f(10) is 57.
```

GNU GDB and GNU `objdump` normally default to AT&T on x86; `objdump -d -M intel` and GDB's `set disassembly-flavor intel` switch. This module uses Intel syntax with GNU assembler conventions (`#` comments) for x86, and standard syntax with `//` comments for ARM64. A64 instructions with an explicit result normally put the destination first; stores such as `str w0, [x1]` put the source register before the destination address.

## The core instructions

| Job | x86-64 | ARM64 |
|---|---|---|
| Copy | `mov` | `mov` |
| Load / store | `mov` with `[...]` | `LDR` / `STR` |
| Address arithmetic | `lea` | `add`, `adr`, `adrp` |
| Arithmetic | `add sub imul neg` | `add sub mul neg` |
| Bitwise | `and or xor not shl shr sar` | `and orr eor mvn lsl lsr asr` |
| Compare | `cmp`, `test` | `cmp`, `tst` |
| Branch | `jmp`, `jcc` | `b`, `b.cond`, `cbz`, `cbnz` |
| Call / return | `call`, `ret` | `bl`, `ret` |
| Conditional select | `cmovcc`, `setcc` | `csel`, `cset`, `cinc` |

## Practical reading tips

- **Compile at `-O1` or `-O2` to learn.** `-O0` output often stores locals to the stack and reloads them, which is accurate but noisy.
- **Start at the end.** For a simple integer result, look for `rax`/`x0` before `ret`; other return types follow different ABI rules.
- **Map arguments first.** For ordinary fixed-parameter integer/pointer arguments under the conventions shown: `rdi, rsi, rdx, rcx, r8, r9` on x86-64 and `x0`–`x7` on ARM64.
- **Look for backward branches** to find loops, and **scaled addressing** to find array indexing.
- **Use the tools.** `objdump -d -M intel prog`, GDB's `disassemble` and `layout asm`, `perf annotate` for hot instructions.

## Key takeaways
- Intel syntax writes destination first; AT&T reverses ordinary two-operand order.
- The same address arithmetic has different bracket/parenthesis notation.
- Stores on A64 list the source register before its destination address.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [x86 and amd64 instruction reference — Félix Cloutier](https://www.felixcloutier.com/x86/)
- [x86-64 machine-level programming — CMU handout (PDF)](https://www.cs.cmu.edu/~fp/courses/15213-s07/misc/asm64-handout.pdf)
- [X86-64 — Wikipedia](https://en.wikipedia.org/wiki/X86-64)
- [AArch64 — Wikipedia](https://en.wikipedia.org/wiki/AArch64)
- [FLAGS register — Wikipedia](https://en.wikipedia.org/wiki/FLAGS_register)
