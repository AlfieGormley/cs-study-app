---
id: isa-comparison-flags
title: Flags, signed comparisons and conditional operations
level: intermediate
minutes: 3
sourceLesson: isa-reading-assembly
summary: Choose condition codes and trace fixed-width comparison and conditional-negation behaviour.
---

## Flags and conditional branches

Flag-based branches such as x86 `jcc` and A64 `b.cond` read flags set by an earlier instruction. Other branches test a register directly, such as A64 `cbz`/`cbnz` and `tbz`/`tbnz`.

- For same-width operands called first and second, Intel/A64 `cmp` sets flags as if subtracting the second from the first, without retaining the subtraction result.
- `test a, b` computes `a & b`, sets flags and throws the result away. `test rax, rax` is the idiomatic "is rax zero or negative?" check.
- Ordinary arithmetic (`add`, `sub`, `and`) sets flags too on x86. On ARM64 ordinary ADD/SUB/AND leave flags unchanged unless using the flag-setting forms: `adds`, `subs`, `ands`, plus `cmp` and `tst`.

Call the first compared value **a** and the second **b**, with the same operand width. After the comparison, choose the branch by **signedness**:

| Meaning | x86 signed / unsigned | ARM64 signed / unsigned |
|---|---|---|
| first greater than second | `jg` / `ja` | `b.gt` / `b.hi` |
| first greater than or equal | `jge` / `jae` | `b.ge` / `b.hs` |
| first less than second | `jl` / `jb` | `b.lt` / `b.lo` |
| first less than or equal | `jle` / `jbe` | `b.le` / `b.ls` |
| equal | `je` | `b.eq` |

For these same-width integer comparisons, signedness determines which condition code interprets the flags. It can also affect earlier conversions and instruction selection. The bits in the register are the same; `jg` tests the sign, overflow and zero flags, while `ja` tests the carry and zero flags.

AArch64 conditional operations also read these flags: `cneg w0, w0, lt` negates the low 32-bit value only when the signed less-than condition holds. It operates on fixed-width bits; negating the smallest signed value still leaves its two’s-complement bit pattern. A C absolute-value function needs a representable-result precondition.

## Pitfalls

- **Mixing up AT&T and Intel order.** `sub %rdi, %rax` is `rax -= rdi`. Check for `%` signs before reading.
- **Reading `cmp` backwards.** In Intel x86 syntax and A64 syntax, `cmp a, b` then "greater than" means `a > b`.
- **Assuming flags survive.** On x86 nearly every arithmetic instruction overwrites them; `mov` and `lea` do not, which is one reason compilers like `lea`.
- **Treating `inc` like `add 1`.** On x86, `inc` leaves the carry flag unchanged.
- **Forgetting zero-extension.** `mov eax, ...` silently clears the top of `rax`; `mov al, ...` does not.

## Key takeaways
- CMP records a subtraction’s flags without keeping the result.
- Signed and unsigned branches interpret those flags differently.
- A flag-changing instruction between comparison and branch changes the tested condition.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [x86 and amd64 instruction reference — Félix Cloutier](https://www.felixcloutier.com/x86/)
- [x86-64 machine-level programming — CMU handout (PDF)](https://www.cs.cmu.edu/~fp/courses/15213-s07/misc/asm64-handout.pdf)
- [X86-64 — Wikipedia](https://en.wikipedia.org/wiki/X86-64)
- [AArch64 — Wikipedia](https://en.wikipedia.org/wiki/AArch64)
- [FLAGS register — Wikipedia](https://en.wikipedia.org/wiki/FLAGS_register)
