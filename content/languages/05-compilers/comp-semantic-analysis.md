---
id: comp-semantic-analysis
title: ASTs, semantic analysis and symbol tables
level: intermediate
minutes: 13
summary: How compilers represent programs as abstract syntax trees, walk them with pattern matching and visitors, and use scoped symbol tables to catch undefined names, shadowing and checks beyond this grammar.
---

A parser guarantees that a program is *shaped* correctly. It cannot tell you that `let x = 5 in y + 1` is nonsense, because `y` is a perfectly good NAME token in a perfectly good position. Knowing that `y` was never defined requires remembering what *was* defined, and where. That is **semantic analysis**: checking the meaning of a program, not just its form.

It runs on the tree the parser built, so we start there.

## Parse trees versus abstract syntax trees

A **parse tree** (or concrete syntax tree) records every grammar rule used, including brackets and the intermediate `term` and `factor` levels. For `(2 + 3) * 4`:

```
 parse tree               AST
   expr
    |
   term                    *
  / | \                   / \
fac '*' fac              +   4
 |       |              / \
( expr )  4             2   3
  / | \
term + term
 |      |
 2      3
```

Calc's abstract syntax tree omits redundant grammar structure such as brackets. Other ASTs retain more source detail: Clang, for example, preserves parentheses. Chains of single-child nodes vanish too. Many compilers build an AST directly in the parser and never materialise the parse tree. Tools that must reproduce source exactly, such as formatters and refactoring tools, keep a *concrete* tree with whitespace and comments: Roslyn and rust-analyzer use lossless syntax representations. Tree-sitter preserves concrete nodes and source ranges but does not necessarily store every whitespace character as a node; tooling also retains source text.

### Calc's AST

Calc's AST is five Python dataclasses. Each node also records the position of the token it came from, so later errors can point at the source.

```python
from dataclasses import dataclass, field

# pos is left out of == and repr, so trees
# compare by structure only.
POS = dict(default=0, compare=False,
           repr=False)

@dataclass
class Num:
    value: int
    pos: int = field(**POS)

@dataclass
class Var:
    name: str
    pos: int = field(**POS)

@dataclass
class Neg:
    operand: object
    pos: int = field(**POS)

@dataclass
class BinOp:
    op: str
    left: object
    right: object
    pos: int = field(**POS)

@dataclass
class Let:
    name: str
    value: object
    body: object
    pos: int = field(**POS)
```

Excluding `pos` from comparison means `parse("1+2") == parse("1 + 2")` is `True`, which makes tests pleasant to write.

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
            b = evaluate(right, env)
            return ARITH[op](a, b)
        case Let(name, value, body):
            v = evaluate(value, env)
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
    return a ** b

ARITH = {
    "+": operator.add, "-": operator.sub,
    "*": operator.mul,
    "/": operator.floordiv,
    "^": power,
}
```

`ARITH` maps operators to these implementations. `evaluate(parse("let x = 5 in let y = x * 2 in y + x"), {})` returns 15.

Notice how `Let` creates a *new* dictionary `{**env, name: v}` rather than modifying `env`. When the body finishes, the outer code still sees the old `env`, so the binding disappears exactly when its scope ends. This is called an **environment**: a map from names to values that follows the program's nesting.

### The visitor pattern

One alternative to pattern matching is the visitor pattern: each node class has an `accept(visitor)` method that calls `visitor.visitBinOp(self)` and so on. javac exposes TreeVisitor APIs. Clang's RecursiveASTVisitor is a template-based traversal framework using static dispatch, rather than requiring this exact virtual accept implementation. In Python you can get the same effect by dispatching on the class name, which is what Calc's checker does:

```python
    def check(self, node):
        kind = type(node).__name__
        getattr(self, "check_" + kind)(node)
```

Both a pattern-matching pass and a visitor can group the operations for one pass together. Putting methods directly on nodes instead groups operations by node type. Compilers have many passes and a fairly fixed set of nodes, so both styles are common.

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
        self.nslots += 1
        self.stack[-1][name] = sym
        return sym

    def lookup(self, name):
        for scope in reversed(self.stack):
            if name in scope:
                return scope[name]
        return None
```

A `Symbol` holds `name`, `slot`, `pos` and a `used` flag. The **slot** is a small integer giving the binding its own numbered storage cell; the bytecode compiler in lesson 6 uses it so the VM can read `slots[1]` instead of looking up a string in a dictionary.

### The checker

```python
    def check_Var(self, node):
        sym = self.scopes.lookup(node.name)
        if sym is None:
            self.errors.append(
                f"{node.pos}: undefined"
                f" name {node.name!r}")
            return
        sym.used = True
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
        self.slot[id(node)] = sym.slot
        self.check(node.body)
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

The division check only catches a *literal* zero. `1 / (2 - 2)` passes, because this checker implements only a syntactic literal test. Constant folding in lesson 5 reduces `2 - 2` to 0, so a check run after folding would catch this case too, while exact fault prediction for unrestricted Turing-complete programs is undecidable.

### Two ways to build the table

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
print(f.get_locals())   # ('a', 'b')
print(f.get_globals())  # ('x',)
```

Because `a` and `b` are known locals, CPython compiles them to `LOAD_FAST` and `STORE_FAST` (3.14's `dis` shows variants such as `LOAD_FAST_BORROW`), which index a fixed array of slots exactly like Calc's, while `x` uses `LOAD_GLOBAL`, a dictionary lookup. The same compile-time decision explains a classic surprise:

```python
x = 1
def g():
    print(x)   # UnboundLocalError
    x = 2
```

The assignment anywhere in `g` makes `x` local to the *whole* function, so the `print` reads a local slot that has not been filled yet.

## Types

Calc has one type, so there is nothing to check. Add booleans and `if c then a else b`, and the checker gains a second job: computing a **type** for every node and rejecting mismatches.

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
            need(c, "bool", env)
            t = type_of(a, env)
            need(b, t, env)
            return t
```

Here `env` maps names to *types* rather than values, and `need` raises a type error when a node's type is not the expected one. Same tree walk, same scopes; only the "values" are now types. This is why type checking is often described as *abstract interpretation*: running the program on types instead of numbers.

Java supports local var inference alongside explicit declaration types. ML-family and Haskell inference extends the Hindley–Milner core; Rust, Kotlin, TypeScript and C++ use their own inference rules, including some results beyond a single function body.

## In production compilers

- **Clang**'s `Sema` library performs name lookup, overload resolution, implicit conversions and type checking while the parser builds the AST.
- **rustc** runs name resolution, then type checking, then the borrow checker, each a separate analysis over successively lower representations.
- TypeScript performs type analysis in its checker. Exact file-size rankings and causal claims about complexity are omitted because no versioned repository measurement is supplied.
- **Cascading errors.** After one error, a good checker gives the bad node a special *error type* that is compatible with everything, so a single typo does not produce dozens of follow-on errors.

## Pitfalls

- **Defining the name before checking its initializer** incorrectly accepts self-reference unless recursive binding is deliberately supported. Write a test like `let x = x in x` that must fail.
- **Forgetting to pop a scope** leaks names: `(let x = 1 in x) + x` would wrongly pass.
- **Keying side tables by `id(node)`** is quick but fragile. If a later pass copies or rebuilds nodes, the ids change; bigger compilers store the resolved symbol on the node itself.
- Errors without positions are harder to locate in large programs. Every node carries `pos` for this reason.

## Key takeaways
- Calc's AST omits brackets; other ASTs may preserve them, and source tools often retain additional concrete syntax.
- AST-based passes can be tree walks; later stages may instead analyze control-flow graphs or other IRs.
- A symbol table maps names to what they are; a stack of scopes models nesting, and lookup goes innermost first.
- The order of operations in the checker defines the scoping rules, such as whether a binding can see itself.
- Type checking is the same walk computing types instead of values; good checkers collect many errors and avoid cascades.

## Further reading
- [Resolving and Binding — Crafting Interpreters](https://craftinginterpreters.com/resolving-and-binding.html)
- [Abstract syntax tree — Wikipedia](https://en.wikipedia.org/wiki/Abstract_syntax_tree)
- [Symbol table — Wikipedia](https://en.wikipedia.org/wiki/Symbol_table)
- [symtable: Access to the compiler's symbol tables — Python docs](https://docs.python.org/3/library/symtable.html)
- [Understanding UnboundLocalError — Python FAQ](https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value)
- [Hindley–Milner type system — Wikipedia](https://en.wikipedia.org/wiki/Hindley%E2%80%93Milner_type_system)
- [Primary verification source 1](https://clang.llvm.org/docs/IntroductionToTheClangAST.html)
- [Primary verification source 2](https://clang.llvm.org/doxygen/classclang_1_1RecursiveASTVisitor.html)
- [Primary verification source 4](https://docs.python.org/3/library/operator.html)
