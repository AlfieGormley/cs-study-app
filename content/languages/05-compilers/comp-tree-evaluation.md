---
id: comp-tree-evaluation
title: "Tree evaluation and visitor passes"
level: intermediate
minutes: 3
sourceLesson: comp-semantic-analysis
summary: "Evaluate operands in the language’s order and apply its arithmetic rules."
---

## Walking the tree

An AST-based pass can be a tree walk: a recursive function with one case per node type. Python 3.10's `match` statement makes this direct. Here is a complete interpreter for Calc:

```python
def evaluate(node, env):
    match node:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Neg(operand):
            return -evaluate(operand, env)
        case BinOp(op, left, right):
            a = evaluate(left, env)
            # Preserve left-to-right
            # evaluation.
            b = evaluate(right, env)
            return ARITH[op](a, b)
        case Let(name, value, body):
            v = evaluate(value, env)
            # Shadow locally without
            # changing env.
            inner = {**env, name: v}
            return evaluate(body, inner)
```

The shared arithmetic helpers make Calc's integer-only behavior explicit:

```python
import operator

def power(a, b):
    if b < 0:
        raise ArithmeticError(
            "negative exponent")
    # Successful Calc powers stay integral.
    return a ** b

ARITH = {
    "+": operator.add, "-": operator.sub,
    "*": operator.mul,
    "/": operator.floordiv,
    "^": power,
}
```

`ARITH` maps operators to these implementations. `evaluate(parse("let x = 5 in let y = x * 2 in y + x"), {})` returns 15.

Notice how `Let` creates a *new* dictionary `{**env, name: v}` rather than modifying `env`. When the body finishes, the outer code still sees the old `env`, so the binding disappears exactly when its scope ends. This is called an **evaluation environment**: a map from names to values that follows the program's nesting.

## The visitor pattern

One alternative to pattern matching is the visitor pattern: each node class has an `accept(visitor)` method that calls `visitor.visitBinOp(self)` and so on. javac exposes TreeVisitor APIs. Clang's RecursiveASTVisitor is a template-based traversal framework using calls resolved at compile time, rather than requiring this exact virtual accept implementation. In Python you can get the same effect by choosing the method from the class name, which is what Calc's checker does:

```python
    def check(self, node):
        kind = type(node).__name__
        getattr(self, "check_" + kind)(node)
```

Both a pattern-matching pass and a visitor can group the operations for one pass together. Putting methods directly on nodes instead groups operations by node type. Compilers have many passes and a fairly fixed set of nodes, so both styles are common.

## Key takeaways
- Evaluate operands in the language’s order and apply its arithmetic rules.
- A fresh inner environment preserves the surrounding binding when a let finishes.

## Further reading
- [Resolving and binding — Crafting Interpreters](https://craftinginterpreters.com/resolving-and-binding.html)
- [clang.llvm.org — IntroductionToTheClangAST.html](https://clang.llvm.org/docs/IntroductionToTheClangAST.html)
- [clang.llvm.org — classclang_1_1RecursiveASTVisitor.html](https://clang.llvm.org/doxygen/classclang_1_1RecursiveASTVisitor.html)
- [Python symbol-table interface](https://docs.python.org/3/library/symtable.html)
- [docs.python.org — programming.html](https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value)
- [rustc-dev-guide.rust-lang.org — overview.html](https://rustc-dev-guide.rust-lang.org/overview.html)
- [Python arithmetic operators](https://docs.python.org/3/library/operator.html)
