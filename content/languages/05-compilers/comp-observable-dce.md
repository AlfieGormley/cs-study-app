---
id: comp-observable-dce
title: "Dead values, defined errors and C undefined behaviour"
level: advanced
minutes: 3
sourceLesson: comp-ir-ssa
summary: "An unused result can still raise a defined error or perform another observable effect."
---

Earlier units introduced instructions, constant operands and algebraic identities. This backward pass keeps instructions needed by the result and those that might raise a defined Calc arithmetic error. The host interpreter’s memory exhaustion and other resource failures are outside this deliberately bounded teaching model.

## 4. Dead-code elimination

Walk backwards from the result, keeping only instructions whose value is needed:

```python
def dce(code, result):
    live, out = {result}, []
    # Work back from observably required
    # values.
    for ins in reversed(code):
        needed = ins.dest in live
        # An unused result may still raise
        # an error.
        if needed or may_trap(ins):
            out.append(ins)
            live.update(filter(is_temp,
                               ins.args))
    out.reverse()
    return out, result
```

Here is the trap check for Calc's defined arithmetic errors. Host resource exhaustion is outside this teaching model:

```python
def may_trap(ins):
    if ins.op not in ("/", "^"):
        return False
    b = ins.args[1]
    # An unknown divisor or exponent may
    # fail.
    if is_temp(b):
        return True
    if ins.op == "/":
        return b == 0
    return b < 0
```

The may_trap check is the subtle part. It returns `True` for a division whose divisor is not a known non-zero constant, and for `^` with a possibly negative exponent. Consider `(1/0)*0`:

```
t1 = 1 / 0       optimised
t2 = t1 * 0      t1 = 1 / 0
ret t2           ret 0
```

`simplify` turns `t1 * 0` into 0, which makes `t1` unused. Without `may_trap`, DCE would delete the division and the program would quietly return 0 instead of failing. An instruction with a **side effect** (raising, writing memory, doing I/O) is never dead just because its result is unused.

> [!warning] C plays by different rules
> In C, dividing by zero and signed overflow are *undefined behaviour*. The compiler may assume they never happen, so it can delete such a division. Clang compiles `return x + 1 > x;` to "return 1", because overflow "cannot" happen. Calc defines its errors, so its optimiser must preserve them.

## Key takeaways
- An unused result can still raise a defined error or perform another observable effect.
- C undefined behaviour gives a different optimisation contract from Calc’s defined exceptions.

## Further reading
- [LLVM language reference](https://llvm.org/docs/LangRef.html#phi-instruction)
- [LLVM analysis and transform passes](https://llvm.org/docs/Passes.html)
- [SSA construction — Cytron and colleagues](https://www.cs.utexas.edu/~pingali/CS380C/2010/papers/ssaCytron.pdf)
- [blog.llvm.org — what-every-c-programmer-should-know.html](https://blog.llvm.org/2011/05/what-every-c-programmer-should-know.html)
- [Finding compiler bugs with Csmith](https://users.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf)
