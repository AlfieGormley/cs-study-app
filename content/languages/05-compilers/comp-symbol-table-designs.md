---
id: comp-symbol-table-designs
title: "Symbol table costs and Python local scope"
level: intermediate
minutes: 3
sourceLesson: comp-semantic-analysis
summary: "A stack of dictionaries searches outward; a dictionary of stacks needs scope-exit bookkeeping."
---

## Two ways to build the table

The table below uses Big O notation for lookup cost. O(depth) means the number of dictionary probes grows in proportion to the nesting depth, the number of scopes currently on the stack, because lookup may have to try every scope from the innermost outwards. O(1) means the cost stays the same however deep the nesting is. "Expected" is there because a hash probe is fast on average but can occasionally be slower.

| Design | Lookup | Used by |
|---|---|---|
| Stack of dicts | O(depth) expected hash probes | Teaching implementation |
| Dict of stacks | O(1) expected probes in name table | Alternative design |

The alternative keeps one dictionary from name to a *stack* of symbols. Defining pushes onto that name's stack; leaving a scope pops every name it defined. Lookup is a single hash probe however deep the nesting, which matters when C headers put thousands of names in scope.

## Real languages do this at compile time

Python is often called dynamic, but it decides each function's scopes at compile time, using a symbol table you can inspect:

```python
import symtable
src = """x = 1
def f(a):
    b = a + x
    return b
"""
mod = symtable.symtable(src, "m", "exec")
f = mod.lookup("f").get_namespace()
# These are compile-time scope
# classifications.
print(f.get_locals())   # ('a', 'b')
print(f.get_globals())  # ('x',)
```

Because `a` and `b` are known locals, CPython compiles them to `LOAD_FAST` and `STORE_FAST` (3.14's `dis` shows versions such as `LOAD_FAST_BORROW`), which index a fixed array of slots exactly like Calc's, while `x` uses `LOAD_GLOBAL`, a dictionary lookup. The same compile-time decision explains a classic surprise:

```python
x = 1
def g():
    print(x)   # UnboundLocalError
    # This assignment makes x local
    # throughout g.
    x = 2
```

The assignment anywhere in `g` makes `x` local to the *whole* function, so the `print` reads a local slot that has not been filled yet.

## Key takeaways
- A stack of dictionaries searches outward; a dictionary of stacks needs scope-exit bookkeeping.
- Python decides function-local bindings at compile time, before those assignments execute.

## Further reading
- [Resolving and binding — Crafting Interpreters](https://craftinginterpreters.com/resolving-and-binding.html)
- [clang.llvm.org — IntroductionToTheClangAST.html](https://clang.llvm.org/docs/IntroductionToTheClangAST.html)
- [clang.llvm.org — classclang_1_1RecursiveASTVisitor.html](https://clang.llvm.org/doxygen/classclang_1_1RecursiveASTVisitor.html)
- [Python symbol-table interface](https://docs.python.org/3/library/symtable.html)
- [docs.python.org — programming.html](https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value)
- [rustc-dev-guide.rust-lang.org — overview.html](https://rustc-dev-guide.rust-lang.org/overview.html)
- [Python arithmetic operators](https://docs.python.org/3/library/operator.html)
