---
id: comp-semantic-types
title: "Types, production semantic passes and recovery"
level: intermediate
minutes: 3
sourceLesson: comp-semantic-analysis
summary: "Type analysis can walk the same syntax with types instead of values."
---

## Types

Calc has only an integer value type, so there are no arithmetic operand type mismatches to reject; scope and defined arithmetic errors still need analysis. Add booleans and `if c then a else b`, and the checker gains a second job: computing a **type** for every node and rejecting mismatches.

```python
def type_of(node, env):
    match node:
        case Num():
            return "int"
        case Bool():
            return "bool"
        case Var(name):
            return env[name]
        case BinOp("+", l, r):
            need(l, "int", env)
            need(r, "int", env)
            return "int"
        case If(c, a, b):
            # A condition must have boolean
            # type.
            need(c, "bool", env)
            t = type_of(a, env)
            # Both branches must agree on a
            # type.
            need(b, t, env)
            return t
```

Here `env` maps names to *types* rather than values, and `need` raises a type error when a node's type is not the expected one. Same tree walk, same scopes; only the "values" are now types. This is why type checking is often described as *abstract interpretation*: running the program on types instead of numbers.

Java supports local var inference alongside explicit declaration types. ML-family and Haskell inference extends the Hindley–Milner core; Rust, Kotlin, TypeScript and C++ use their own inference rules, including some results beyond a single function body.

## In production compilers

- **Clang**'s `Sema` library performs name lookup, overload resolution, implicit conversions and type checking while the parser builds the AST.
- **rustc** performs name resolution and type checking in its front end, and borrow checking on MIR. Analyses and representations in real compilers are more interleaved than a single strict pass per stage.
- TypeScript performs type analysis in its checker. Exact file-size rankings and causal claims about complexity are omitted because no versioned repository measurement is supplied.
- **Cascading errors.** After one error, a good checker gives the bad node a special *error type* that is compatible with everything, so a single typo does not produce dozens of follow-on errors.

## Pitfalls

- **Defining the name before checking its initializer** incorrectly accepts self-reference unless recursive binding is deliberately supported. Write a test like `let x = x in x` that must fail.
- **Forgetting to pop a scope** leaks names: `(let x = 1 in x) + x` would wrongly pass.
- **Keying side tables by `id(node)`** is quick but fragile. If a later pass copies or rebuilds nodes, the ids change; bigger compilers store the resolved symbol on the node itself.
- Errors without positions are harder to locate in large programs. Every node carries `pos` for this reason.

## Key takeaways
- Type analysis can walk the same syntax with types instead of values.
- Error types limit cascades; side-table identities must survive the transformations that use them.

## Further reading
- [Resolving and binding — Crafting Interpreters](https://craftinginterpreters.com/resolving-and-binding.html)
- [clang.llvm.org — IntroductionToTheClangAST.html](https://clang.llvm.org/docs/IntroductionToTheClangAST.html)
- [clang.llvm.org — classclang_1_1RecursiveASTVisitor.html](https://clang.llvm.org/doxygen/classclang_1_1RecursiveASTVisitor.html)
- [Python symbol-table interface](https://docs.python.org/3/library/symtable.html)
- [docs.python.org — programming.html](https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value)
- [rustc-dev-guide.rust-lang.org — overview.html](https://rustc-dev-guide.rust-lang.org/overview.html)
- [Python arithmetic operators](https://docs.python.org/3/library/operator.html)
