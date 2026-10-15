---
id: comp-production-optimisation
title: "Production optimisations and arithmetic limits"
level: advanced
minutes: 3
sourceLesson: comp-ir-ssa
summary: "Production passes combine inlining, data-flow reasoning, loop changes and target costs."
---

## What else real optimisers do

| Pass | Idea |
|---|---|
| Inlining | Copy a callee's body in |
| SCCP | Constants through branches |
| GVN | CSE across blocks |
| LICM | Hoist work out of loops |
| Strength red. | `x * 2` to `x << 1` |
| Vectorise | One SIMD operation on several lanes |

**Inlining** can expose many other optimisation opportunities: once a small function's body sits in its caller, its parameters may be constants. **SCCP** (sparse conditional constant propagation, Wegman and Zadeck) propagates constants and deletes branches that can never be taken. **GVN** (global value numbering) is CSE across basic blocks. **LICM** (loop-invariant code motion) moves computations that do not change out of loops.

**Strength reduction** replaces an expensive operation with a cheaper equivalent. The classic case is multiplying by a power of two, which is the same as a left shift (`<<`):

```formula
x × 2^k = x << k
x × 8 = x × 2^3 = x << 3
where
x: an integer value
k: how many places the bits move, a whole number from 0 upwards
2^k: k copies of 2 multiplied together
<<: left shift: move every bit of the left operand k places towards the more significant end, filling the gap with zeros
In words: shifting left by k places doubles the value k times, so ×2 is a shift by 1 and ×8 a shift by 3.
```

For unbounded Calc integers this identity is exact. A machine instruction also has a fixed width and shift-count rules. In C, signed left shift additionally requires a nonnegative left operand and a representable result, while unsigned arithmetic follows modular rules; merely fitting a negative mathematical result does not make a C signed left shift defined.

## Pitfalls

- **Floating point is not real arithmetic.** In Python, `(0.1 + 0.2) + 0.3` is `0.6000000000000001` while `0.1 + (0.2 + 0.3)` is `0.6`. A compiler that reassociates floats changes results, so a transformation needs suitable permissions or a proof that observable results are preserved.
- **Compile-time blow-up.** Constant folding, inlining and loop unrolling can all make the compiler slow or huge. Every such pass needs limits, like `fold_const`'s exponent cap.
- **Undefined behaviour cuts both ways.** It lets C compilers optimise aggressively, and it is why "the compiler deleted my null check" is a real bug report.
- **Optimisers have bugs.** Csmith, a random C program generator from the University of Utah, found hundreds of bugs in GCC and LLVM by comparing optimised and unoptimised builds. This teaching compiler supplies excerpts; identity, simplify and display helpers must be supplied to assemble a complete demonstration. Bounded example tests do not prove every possible optimisation correct.

## Key takeaways
- Production passes combine inlining, data-flow reasoning, loop changes and target costs.
- Resource limits, floating-point rules and source-language undefined behaviour constrain transformations.

## Further reading
- [LLVM language reference](https://llvm.org/docs/LangRef.html#phi-instruction)
- [LLVM analysis and transform passes](https://llvm.org/docs/Passes.html)
- [SSA construction — Cytron and colleagues](https://www.cs.utexas.edu/~pingali/CS380C/2010/papers/ssaCytron.pdf)
- [blog.llvm.org — what-every-c-programmer-should-know.html](https://blog.llvm.org/2011/05/what-every-c-programmer-should-know.html)
- [Finding compiler bugs with Csmith](https://users.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf)
