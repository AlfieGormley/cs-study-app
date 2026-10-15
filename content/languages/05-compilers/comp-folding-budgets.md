---
id: comp-folding-budgets
title: "Constant propagation with compile-time budgets"
level: advanced
minutes: 4
sourceLesson: comp-ir-ssa
summary: "Substitute known operands and fold arithmetic only when it is safe and within budget."
---

Lowering and SSA have made dependencies explicit. The snippets below use Ins and is_temp from the earlier lowering unit, and ARITH from tree evaluation. Constant propagation updates later operands as well as the returned result. A retained instruction is still part of the runtime program, even if the compiler declines to evaluate it.

## Optimisations

Calc's optimiser has four passes. Each takes `(code, result)` and returns a new pair, so they compose freely.

## 1. Constant folding and propagation

If both operands are known constants, compute the answer now and remember it for later instructions:

```python
def fold_const(op, a, b):
    """Compute a op b now, or None if it is
    unsafe to do at compile time."""
    if op == "/" and b == 0:
        return None   # keep runtime error
    if op == "^":
        # Estimate result size before
        # exponentiation.
        bits = max(1, abs(a).bit_length())
        if not 0 <= b <= 64:
            return None
        if bits * b > 4096:
            return None
    return ARITH[op](a, b)
```

```python
def const_fold(code, result):
    known, out = {}, []
    for ins in code:
        args = tuple(known.get(a, a)
                     for a in ins.args)
        if any(map(is_temp, args)):
            out.append(Ins(ins.dest, ins.op,
                           args))
            continue
        if ins.op == "neg":
            v = -args[0]
        else:
            v = fold_const(ins.op, *args)
        # None means retain the runtime
        # operation.
        if v is None:
            out.append(Ins(ins.dest, ins.op,
                           args))
        else:
            # Later uses now see the folded
            # value.
            known[ins.dest] = v
    return out, known.get(result, result)
```

`fold_const` is where correctness lives. Folding `1 / 0` would crash the *compiler*, and the program must instead fail when it runs. And folding `2 ^ 1000000` would make the compiler build a number about 300,000 digits long for a value that might never be used. The digit count of a power follows from logarithms:

```formula
D = ⌊b × log_10(a)⌋ + 1
D = ⌊1000000 × 0.3010299957⌋ + 1
D = 301029 + 1 = 301030
where
D: the number of decimal digits in a raised to the power b, for a a positive integer and b a nonnegative integer
a: the positive integer base, here 2
b: the nonnegative integer exponent, here 1,000,000
log_10: the base-10 logarithm: log_10(a) is the power 10 must be raised to to give a; log_10(2) ≈ 0.30103
⌊ ⌋: floor: round down to the nearest whole number
≈: approximately equal to
In words: each factor of 2 adds about 0.3 of a decimal digit, so a million of them make a number 301,030 digits long.
```

`fold_const` avoids this by estimating the size of the answer *before* computing it. That is what its `bits * b > 4096` test does:

```formula
B_r ≤ B_a × b   when b ≥ 1
B_a × b ≤ 4096
where
B_r: the number of bits (binary digits) in the result, a raised to the power b
B_a: the number of bits in a, as Python's `abs(a).bit_length()` gives, counted as at least 1
a: the base of the power
b: the exponent, which `fold_const` also requires to be between 0 and 64
4096: `fold_const`'s size budget in bits; a number below 2^4096 has at most 1,234 decimal digits
≤: less than or equal to
≥: greater than or equal to (for b = 0 the answer is 1, which still needs one bit)
In words: a raised to the power b is b copies of a multiplied together, and a product of b numbers of B_a bits each has at most B_a × b bits, so `fold_const` only evaluates powers whose estimate fits the 4,096-bit budget.
```

For example, `3 ^ 64` has a two-bit base (3 is `11` in binary), so the estimate is 128 bits (the true result has 102), which is within budget, so it is computed at compile time; `2 ^ 1000000` fails the 0 to 64 exponent check and stays as a runtime instruction. Compilers need explicit resource budgets. This example bounds folded powers; it is not a complete resource-limit policy for all arithmetic.

## Key takeaways
- Substitute known operands and fold arithmetic only when it is safe and within budget.
- Retain defined runtime arithmetic errors and bound expensive exponentiation.

## Further reading
- [LLVM language reference](https://llvm.org/docs/LangRef.html#phi-instruction)
- [LLVM analysis and transform passes](https://llvm.org/docs/Passes.html)
- [SSA construction — Cytron and colleagues](https://www.cs.utexas.edu/~pingali/CS380C/2010/papers/ssaCytron.pdf)
- [blog.llvm.org — what-every-c-programmer-should-know.html](https://blog.llvm.org/2011/05/what-every-c-programmer-should-know.html)
- [Finding compiler bugs with Csmith](https://users.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf)
