---
id: comp-value-reuse
title: "Integer identities and common subexpressions"
level: advanced
minutes: 4
sourceLesson: comp-ir-ssa
summary: "SSA values support reusing equivalent pure deterministic computations."
---

These are two neighbouring optimisation passes, not a complete optimiser listing. The integer identity rules are shown explicitly; the small identity and simplify helpers are omitted scaffolding. The executable CSE pass uses Ins and is_temp from earlier units. Inputs are already-evaluated SSA operands, so simplifying a use does not itself erase the operations that produced them.

## 2. Algebraic simplification

Some operations are known without knowing both operands:

```formula
x + 0 = x
x × 1 = x
x − x = 0
x × 0 = 0
where
x: any Calc integer, whether or not its value is known at compile time
In words: adding zero or multiplying by one changes nothing, and a value minus itself, or anything times zero, is always zero.
```

So in Calc's IR, `t2 = t1 + 0` can be replaced by `t1` without knowing what `t1` is. The `identity` function holds the rules, and `simplify` replaces the instruction with the shortcut, recording an alias so later uses see through it.

These rules are valid for Calc's unbounded integers. For floating point, some are not generally valid: `x * 0` is `NaN` when `x` is infinity, and `x - x` is `NaN` for `NaN`. Compilers need proofs or suitable floating-point permissions for transformations that change observable results; fast-math is one way to grant such permissions.

## 3. Common subexpression elimination

For these deterministic, pure arithmetic operations in one block, reuse an operation previously computed on the same operands. Loads and calls require additional effect and alias analysis. Because of SSA, "same operands" means the same values, guaranteed.

```python
def cse(code, result):
    seen, alias, out = {}, {}, []
    for ins in code:
        args = tuple(alias.get(a, a)
                     for a in ins.args)
        if ins.op in ("+", "*"):  # a+b=b+a
            args = tuple(sorted(args,
                                key=repr))
        # Pure operations with this key
        # agree.
        key = (ins.op, args)
        if key in seen:
            # Reuse the earlier SSA value.
            alias[ins.dest] = seen[key]
        else:
            seen[key] = ins.dest
            out.append(Ins(ins.dest, ins.op,
                           args))
    return out, alias.get(result, result)
```

This is **local value numbering**. An operator is **commutative** when swapping its operands never changes the answer:

```formula
a + b = b + a
a × b = b × a
where
a: any integer value
b: any integer value
In words: for + and ×, operand order does not matter, so the optimiser may put the operands in a fixed order before comparing them.
```

Subtraction and division are not commutative (`5 - 3` is 2 but `3 - 5` is -2), so `cse` leaves their order alone. Sorting the operands of commutative operators makes `x + y` and `y + x` the same key:

```
(x + y) * (y + x)      optimised
t1 = x + y             t1 = x + y
t2 = y + x             t3 = t1 * t1
t3 = t1 * t2           ret t3
ret t3
```

## Floating-point boundary cases

Under round-to-nearest, adding positive zero to negative zero gives positive zero. That makes removing `x + 0.0` observably wrong when the sign of zero matters. Multiplication and division by positive one preserve the numerical value and zero sign, including infinity, under this model. These examples ignore signalling NaNs, NaN payload details and floating-point status flags; production transformations must honour the complete floating-point contract. Calc’s integer identity helper also removes division by positive one and zero on the left of addition.

## Key takeaways
- SSA values support reusing equivalent pure deterministic computations.
- Integer identities do not automatically preserve floating-point signed zero or NaNs.

## Further reading
- [LLVM language reference](https://llvm.org/docs/LangRef.html#phi-instruction)
- [LLVM analysis and transform passes](https://llvm.org/docs/Passes.html)
- [SSA construction — Cytron and colleagues](https://www.cs.utexas.edu/~pingali/CS380C/2010/papers/ssaCytron.pdf)
- [blog.llvm.org — what-every-c-programmer-should-know.html](https://blog.llvm.org/2011/05/what-every-c-programmer-should-know.html)
- [Finding compiler bugs with Csmith](https://users.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf)
