---
id: comp-live-intervals
title: "Live intervals and ideal register demand"
level: advanced
minutes: 3
sourceLesson: comp-codegen-regalloc
summary: "A value is live when a future path can read its current value."
---

## Target 2: a register machine

Real CPUs compute in **registers**: baseline x86-64 has 16 general-purpose integer registers (APX extends this to 32), and AArch64 names 31 general-purpose X registers, with SP handled separately. Our IR has unlimited temporaries. Register allocation is the mapping, and it is one of the most important things a back end does, because keeping values in registers avoids spill loads and stores; costs depend on the processor and instruction.

## Liveness

A value is live where a future execution path can use it before redefinition. In this straight-line example, definition-to-last-use intervals summarize liveness. Distinct values not proven equal can share a freely interchangeable register only when their live requirements do not overlap. Proven-equal values and target-specific register constraints require additional reasoning. On straight-line code, liveness is a simple scan:

```python
def live_ranges(code, result, params):
    start = {p: -1 for p in params}
    end = {p: -1 for p in params}
    for i, ins in enumerate(code):
        start[ins.dest] = end[ins.dest] = i
        for a in filter(is_temp, ins.args):
            end[a] = i
    # Returning a value is its final use.
    if is_temp(result):
        end[result] = len(code)
    return start, end
```

Inputs are defined at -1 (they arrive before the first instruction) and the result is used by `ret`. Take `(x + y) * (x + y) - x * 8`, after the earlier IR units’ optimiser:

```
 i  instruction     live after it
-1  (inputs)        x  y
 0  t1 = x + y      x  t1
 1  t3 = t1 * t1    x  t3
 2  t4 = x * 8      t3 t4
 3  t5 = t3 - t4    t5
 4  ret t5
```

At most **two** values are live at any point. `y` dies at instruction 0 and `x` at instruction 2, so their registers can be reused. The peak has a name, **MaxLive**:

```formula
MaxLive = max(L_p for all p)
MaxLive = max(2, 2, 2, 2, 1) = 2
where
MaxLive: the largest number of values live at the same time, anywhere in the code
L_p: the number of values live just after point p (the "live after it" column)
p: a point in the code: after the inputs arrive (−1), or after instruction 0, 1, 2 or 3
max: the largest of the listed values
In words: count the live values at every point and take the biggest count; here it never exceeds two.
```

In this idealized model, MaxLive is the number of freely interchangeable registers needed without spills, allowing a dying operand register to hold the result. Real targets impose additional operand, register-class and ABI constraints.

## Key takeaways
- A value is live when a future path can read its current value.
- The ideal straight-line MaxLive model permits a dying source register to hold the new result.

## Further reading
- [LLVM code generator design](https://llvm.org/docs/CodeGenerator.html)
- [Linear scan register allocation — Poletto and Sarkar](https://web.cs.ucla.edu/~palsberg/course/cs132/linearscan.pdf)
- [Register allocation and coalescing research](https://www.cs.princeton.edu/~appel/modern/text/color1.html)
- [C11 committee draft: expressions and integer arithmetic](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [AArch64 procedure-call standard](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
