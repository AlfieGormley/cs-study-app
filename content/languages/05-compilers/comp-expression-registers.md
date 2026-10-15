---
id: comp-expression-registers
title: "Sethi–Ullman numbers and evaluation order"
level: advanced
minutes: 3
sourceLesson: comp-codegen-regalloc
summary: "Equal subtree requirements need one extra register; unequal requirements use the larger count."
---

This expression-tree model assumes freely interchangeable registers, one register per leaf, and operations whose result can reuse a source register. It excludes let nodes, ABI constraints and target memory operands. The `Num(1)`, `Var("x")`, `Neg(...)` and `BinOp(...)` node classes come from the AST units.

## Sethi–Ullman numbering

For a single expression *tree*, Sethi and Ullman (1970) showed how to compute the minimum number of registers directly, and the evaluation order that achieves it:

```python
def sethi_ullman(node):
    match node:
        case Num() | Var():
            return 1
        case Neg(operand):
            return sethi_ullman(operand)
        case BinOp(_, left, right):
            a = sethi_ullman(left)
            b = sethi_ullman(right)
            # A tie needs room for one saved
            # result.
            if a == b:
                return a + 1
            return max(a, b)
```

The same rule, written as a formula:

```formula
R_leaf = 1
R_n = max(R_L, R_R)   if R_L ≠ R_R
R_n = R_L + 1         if R_L = R_R
where
R_leaf: the registers needed to evaluate a leaf, a number or a variable: just the one that holds it
R_n: the registers needed to evaluate operator node n and both its operands
n: a binary operator node, such as a `+` or `*`
R_L: the registers needed by n's left subtree
R_R: the registers needed by n's right subtree
max: the larger of the two values
≠: is not equal to
In words: if the two sides need different numbers of registers, the bigger need wins; only a tie costs one extra register.
```

A unary minus needs the same as its operand. Worked through: `a+b` and `c+d` each join two leaves (1 and 1, a tie), so each needs 2; `(a+b)*(c+d)` joins 2 and 2, another tie, so it needs 3. In `a+(b+(c+d))`, `c+d` needs 2, `b+(c+d)` joins 1 and 2 and needs 2, and the outer `+` joins 1 and 2 and still needs 2.

When reordering preserves effects and exception behavior, evaluate the subtree needing more registers first; its result then occupies one register while the smaller side uses the rest. Only when both sides need the same number does the total go up by one. So `(a+b)*(c+d)` needs 3, while `a+(b+(c+d))` needs only 2, *if* the compiler evaluates `c+d` first. Evaluating strictly left to right would hold `a`, `b` and `c` while computing `c+d`: four registers. (This version counts a leaf as one register; machines with memory or immediate operands can count a right-hand leaf as zero.)

## Key takeaways
- Equal subtree requirements need one extra register; unequal requirements use the larger count.
- Evaluate the needier subtree first only when language effects and exceptions allow it.

## Further reading
- [LLVM code generator design](https://llvm.org/docs/CodeGenerator.html)
- [Linear scan register allocation — Poletto and Sarkar](https://web.cs.ucla.edu/~palsberg/course/cs132/linearscan.pdf)
- [Register allocation and coalescing research](https://www.cs.princeton.edu/~appel/modern/text/color1.html)
- [C11 committee draft: expressions and integer arithmetic](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [AArch64 procedure-call standard](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst)
- [The generation of optimal code for arithmetic expressions — Sethi and Ullman, author institution publication record](https://experts.arizona.edu/en/publications/the-generation-of-optimal-code-for-arithmetic-expressions/)
