---
id: pattern-visitors-and-extension
title: Visitors and the extension trade-off
level: advanced
minutes: 3
sourceLesson: pattern-behavioural-2
summary: A visitor groups one operation across a family of node types.
---

## Visitor pattern

### The problem

You have a stable set of node types (the nodes of a syntax tree, say) and want to add many **operations** over them: pretty-printing, type checking, evaluation, optimisation. Putting every operation as a method on every node class scatters each operation across many files and bloats the nodes.

### The structure

```
 Node              Visitor
 +accept(v)        +visit_Num(n)
   ^    ^          +visit_Add(n)
   |    |             ^       ^
  Num  Add            |       |
  accept(v):      Evaluator  Printer
   v.visit_Num(self)
```

Each operation becomes one visitor class with a method per node type. Choosing the right method depends on **two** types: the node's and the visitor's. This is called **double dispatch**: `node.accept(visitor)` dispatches on the node, which then calls `visitor.visit_Num(self)`, dispatching on the visitor.

### In Python

Python doesn't need `accept`. You can dispatch on the class name, which is exactly what `ast.NodeVisitor` does:

```python
class Num:
    def __init__(self, v):
        self.v = v

class Add:
    def __init__(self, l, r):
        self.l, self.r = l, r

class Visitor:
    def visit(self, node):
        name = type(node).__name__
        # Select the method for this node.
        m = getattr(self, "visit_" + name)
        return m(node)

class Evaluate(Visitor):
    def visit_Num(self, n):
        return n.v

    def visit_Add(self, n):
        v = self.visit
        # Recursively evaluate both
        # operands.
        return v(n.l) + v(n.r)

class Show(Visitor):
    def visit_Num(self, n):
        return str(n.v)

    def visit_Add(self, n):
        l = self.visit(n.l)
        r = self.visit(n.r)
        return f"({l} + {r})"

e = Add(Num(1), Add(Num(2), Num(3)))
print(Show().visit(e), "=",
      Evaluate().visit(e))
# (1 + (2 + 3)) = 6
```

Since Python 3.10, structural pattern matching gives another option: one function with `match node:` and a `case Add(l, r):` arm per type (with `__match_args__` set on the classes). `functools.singledispatch` dispatches a function on its first argument's type.

### The expression problem

Visitor sits on one side of a famous trade-off, named the **expression problem** by Philip Wadler in 1998:

| Design | New operation | New node type |
|---|---|---|
| Methods on nodes | Edit every node | One new class |
| Visitors | One new visitor | Edit every visitor |

So visitor is right when the **types are stable and the operations keep growing**. A compiler with a relatively stable node family is a classic case: additional passes (type checking, constant folding, code generation, linting) can each live in one visitor. If a language’s node types change frequently, the cost shifts back towards updating visitors.

### When not to use it

- When node types change often. Every new type means editing every visitor.
- When there are only one or two operations. Methods on the nodes are simpler.
- When visitors need lots of node internals. Visitors work from the outside, so nodes may have to expose state they'd otherwise keep private.

### In real libraries

- **Python's `ast.NodeVisitor` and `ast.NodeTransformer`**: define `visit_Call`, `visit_Name` and so on; `generic_visit` recurses into children. Linters, formatters and code-modding tools are built on this.
- **Clang's `RecursiveASTVisitor`** and many other compiler front ends.
- **Babel** (JavaScript) plugins are written as visitors over the syntax tree.
- **Java's annotation processing** API has `ElementVisitor`.

## Key takeaways
- A visitor groups one operation across a family of node types.
- Classic visitors use double dispatch; Python can dispatch by node class name.
- Visitors favour adding operations over adding node types.
- Pattern matching or singledispatch can be clearer for small trees.

## Further reading
- [ast — Python documentation](https://docs.python.org/3/library/ast.html)
- [The Expression Problem — Philip Wadler](https://homepages.inf.ed.ac.uk/wadler/papers/expression/expression.txt)
- [PEP 636 — Structural pattern matching tutorial](https://peps.python.org/pep-0636/)
- [functools — Python documentation](https://docs.python.org/3/library/functools.html)
- [State pattern — Wikipedia](https://en.wikipedia.org/wiki/State_pattern)
- [Template method pattern — Wikipedia](https://en.wikipedia.org/wiki/Template_method_pattern)
- [The Iterator pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/iterator/)
- [ast — Abstract syntax trees (NodeVisitor) — Python docs](https://docs.python.org/3/library/ast.html)
- [Expression problem — Wikipedia](https://en.wikipedia.org/wiki/Expression_problem)
