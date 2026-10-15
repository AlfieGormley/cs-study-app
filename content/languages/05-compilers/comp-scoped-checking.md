---
id: comp-scoped-checking
title: "Scoped symbols, slots and a checker"
level: intermediate
minutes: 4
sourceLesson: comp-semantic-analysis
summary: "Check a nonrecursive initializer before introducing its binding."
---

The AST and evaluator already established Calc’s nonrecursive let scopes. Here the checker records Symbol objects before code generation. Its complete wrapper and handlers for numbers and negation are omitted scaffolding; the shown handlers are the important scope-sensitive operations.

## Scopes and symbol tables

The evaluator *finds* undefined names only when it runs and hits a `KeyError`. A compiler should find them before running anything. To do that it keeps a **symbol table**: for every name in scope, a record of what it is (its type, its storage location, where it was declared, whether it has been used).

Calc's scoping rule is simple. In `let NAME = e1 in e2`, NAME is visible in `e2` only. Scopes nest, so the symbol table is a **stack of dictionaries**: push a new dictionary when a scope opens, pop it when it closes, and search from the innermost outwards.

```python
class Scopes:
    def __init__(self):
        self.stack = [{}]
        self.nslots = 0

    def push(self):
        self.stack.append({})

    def pop(self):
        self.stack.pop()

    def define(self, name, pos):
        sym = Symbol(name, self.nslots, pos)
        # Give every binding a distinct
        # slot.
        self.nslots += 1
        self.stack[-1][name] = sym
        return sym

    def lookup(self, name):
        # Search from the innermost binding
        # out.
        for scope in reversed(self.stack):
            if name in scope:
                return scope[name]
        return None
```

A `Symbol` holds `name`, `slot`, `pos` and a `used` flag. The **variable slot** is a small integer giving the binding its own numbered storage cell; the bytecode compiler in the stack-code-generation unit uses it so the VM can read `slots[1]` instead of looking up a string in a dictionary.

## The checker

```python
    def check_Var(self, node):
        sym = self.scopes.lookup(node.name)
        if sym is None:
            self.errors.append(
                f"{node.pos}: undefined"
                f" name {node.name!r}")
            return
        sym.used = True
        # Record the resolved binding for
        # codegen.
        self.slot[id(node)] = sym.slot

    def check_BinOp(self, node):
        self.check(node.left)
        self.check(node.right)
        if (node.op == "/"
                and node.right == Num(0)):
            self.errors.append(
                f"{node.pos}: division"
                " by zero")
```

```python
    def check_Let(self, node):
        # value first: name not in scope
        self.check(node.value)
        name, pos = node.name, node.pos
        if self.scopes.lookup(name):
            self.warnings.append(
                f"{pos}: {name!r} shadows"
                " an outer binding")
        self.scopes.push()
        sym = self.scopes.define(name, pos)
        # Record the resolved binding for
        # codegen.
        self.slot[id(node)] = sym.slot
        self.check(node.body)
        # Outer uses must not see the inner
        # name.
        self.scopes.pop()
        if not sym.used:
            self.warnings.append(
                f"{pos}: {name!r} is"
                " never used")
```

The **order** inside `check_Let` encodes the language's scoping rule. The value is checked *before* the name is defined, so in `let x = x + 1 in x` the inner `x` refers to an outer `x`, or is an error if there is none. Defining the symbol before checking its initializer permits self-reference statically, but does not implement recursive-binding runtime semantics; the evaluator must change too.

Running it:

```
>>> c = check(parse("let x = 5 in y / 0"))
>>> c.errors
["13: undefined name 'y'",
 '15: division by zero']
>>> c.warnings
["0: 'x' is never used"]
>>> check(parse(
...   "let x = 1 in let x = x + 1 in x"
... )).warnings
["13: 'x' shadows an outer binding"]
```

Two design choices matter here. The checker collects several errors rather than stopping at the first; this does not guarantee detecting every defect. And it distinguishes **errors** (the program is meaningless) from **warnings** (legal but suspicious), just as GCC's `-Wunused-variable` or Rust's `unused_variables` lint do.

The division check only catches a *literal* zero. `1 / (2 - 2)` passes, because this checker implements only a syntactic literal test. Constant folding in the later IR units reduces `2 - 2` to 0, so a check run after folding would catch this case too, while exact fault prediction for unrestricted Turing-complete programs is undecidable.

## Key takeaways
- Check a nonrecursive initializer before introducing its binding.
- Push and pop scopes; bind each variable use to the correct unique storage slot.

## Further reading
- [Resolving and binding — Crafting Interpreters](https://craftinginterpreters.com/resolving-and-binding.html)
- [clang.llvm.org — IntroductionToTheClangAST.html](https://clang.llvm.org/docs/IntroductionToTheClangAST.html)
- [clang.llvm.org — classclang_1_1RecursiveASTVisitor.html](https://clang.llvm.org/doxygen/classclang_1_1RecursiveASTVisitor.html)
- [Python symbol-table interface](https://docs.python.org/3/library/symtable.html)
- [docs.python.org — programming.html](https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value)
- [rustc-dev-guide.rust-lang.org — overview.html](https://rustc-dev-guide.rust-lang.org/overview.html)
- [Python arithmetic operators](https://docs.python.org/3/library/operator.html)
