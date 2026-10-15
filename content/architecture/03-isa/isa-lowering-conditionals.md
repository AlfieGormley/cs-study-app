---
id: isa-lowering-conditionals
title: Lower an if/else into branches or flags
level: intermediate
minutes: 3
sourceLesson: isa-loops-arrays-structs
summary: Trace branch-based and branch-free implementations of the same conditional.
---

The CPU has no idea what a `for` loop, a `switch` or a `struct` is. It has compares, conditional branches, and loads and stores with an address. Everything structured in your source code is *lowered* to those; this translation step is called **compiler lowering**.

Once you know the handful of patterns compilers use, optimised assembly stops looking like noise. You can spot the loop in a profile, see why a `switch` became an indirect jump, and work out from `[rdi + rax*8 + 4]` which field of which array element is being read.

The listings are illustrative scalar implementations using Linux LP64 type sizes and System V x86-64 or AAPCS64 conventions. They are not promises of exact Clang output; version, flags and target change instruction selection. Assume valid object bounds and no signed C arithmetic overflow. Partial dispatch listings explicitly omit case bodies. Try them yourself on [Compiler Explorer](https://godbolt.org/).

## if/else: test, then branch around

One common lowering of an `if` uses a compare that sets flags and a conditional jump that **skips** the body. The jump condition is therefore usually the *inverse* of the source condition. Schematically:

```
// if (x > 0) y = 1; else y = 2;
    test  edi, edi
    jle   .Lelse       # skip if x <= 0
    mov   eax, 1
    jmp   .Ldone
.Lelse:
    mov   eax, 2
.Ldone:
```

When both arms are cheap and have no side effects, the compiler often removes the branch entirely with `cmov` (x86) or `csel` (ARM64). This can trade branch-misprediction costs for evaluating both candidate values; whether it helps depends on the core, dependencies and workload. A universal cycle penalty is omitted because no particular core or measurement is specified.

For this snippet another valid lowering is possible. It notices the result is 1 plus a 0-or-1 flag:

```formula
y = 1 + c
c = 1 if x ≤ 0, otherwise 0
where
y: the result the if/else produces, 1 or 2
x: the input, held in edi
c: the condition turned into a number; `setle` (set if less than or equal) writes it
≤: less than or equal to
In words: a positive x gives 1 + 0 = 1, and anything else gives 1 + 1 = 2, exactly what the if/else computes.
```

```
    xor   eax, eax
    test  edi, edi
    setle al           # al = (x <= 0)
    inc   eax          # 1 or 2
```

No branch, no `cmov`: just flags turned into a number. This illustrates one possible rewrite; inspect actual compiler output to see whether it is used.

## Key takeaways
- Lowering translates source constructs into simpler machine operations.
- A branch can skip a body by testing the opposite condition.
- Conditional moves and SETcc offer alternative lowerings when semantics permit.

## Further reading
- [Compiler Explorer](https://godbolt.org/)
- [Branch table — Wikipedia](https://en.wikipedia.org/wiki/Branch_table)
- [Data structure alignment — Wikipedia](https://en.wikipedia.org/wiki/Data_structure_alignment)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Strength reduction — Wikipedia](https://en.wikipedia.org/wiki/Strength_reduction)
- [Loop unrolling — Wikipedia](https://en.wikipedia.org/wiki/Loop_unrolling)
- [Computer Systems: A Programmer's Perspective (CS:APP), chapter 3](https://csapp.cs.cmu.edu/)
