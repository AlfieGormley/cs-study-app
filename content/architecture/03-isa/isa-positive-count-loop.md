---
id: isa-positive-count-loop
title: Read a complete scalar counting loop
level: intermediate
minutes: 3
sourceLesson: isa-reading-assembly
summary: Trace equivalent positive-count loops using indexed x86 and pointer-walking A64 code.
---

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
    // Return the accumulated result.
    mov   x0, x8
    ret
```

The same ideas, with different instruction choices: this version rewrites `a[i]` as a pointer walk using a post-indexed load, counted `n` down to zero with `subs` (which sets the flags `b.ne` reads), and used `cinc` (conditional increment) instead of a branch.

## Key takeaways
- Find the guard, induction variable, data access and loop exit.
- SETG and CINC turn comparison results into increments.
- Clear the full temporary before SETG, and preserve the comparison flags until it executes.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [x86 and amd64 instruction reference — Félix Cloutier](https://www.felixcloutier.com/x86/)
- [x86-64 machine-level programming — CMU handout (PDF)](https://www.cs.cmu.edu/~fp/courses/15213-s07/misc/asm64-handout.pdf)
- [X86-64 — Wikipedia](https://en.wikipedia.org/wiki/X86-64)
- [AArch64 — Wikipedia](https://en.wikipedia.org/wiki/AArch64)
- [FLAGS register — Wikipedia](https://en.wikipedia.org/wiki/FLAGS_register)
