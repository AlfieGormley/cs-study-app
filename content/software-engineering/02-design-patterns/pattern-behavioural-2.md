---
id: pattern-behavioural-2
title: State, template method, iterator and visitor
level: advanced
minutes: 17
summary: Objects whose behaviour depends on their state, algorithms with overridable steps, uniform traversal, and operations over a tree of types, with double dispatch, the expression problem and the Python features that replace each pattern.
---

The patterns in this lesson all deal with **control flow that varies**: by the object's current state, by subclass, by how a collection is traversed, or by the type of each node in a structure.

They also show a recurring theme of this module. Each started as a class-based design in C++ or Smalltalk, and modern Python offers lighter alternatives: enums and transition tables, hooks, generators, and `match` or `singledispatch`. Knowing the pattern helps you choose between them.

## State

### The problem

An object's behaviour depends on its state, and the rules differ a lot between states. A document can be *draft*, *in review* or *published*: "edit" works in draft, is refused in review and creates a new revision when published.

Written naively, every method becomes a large `if self.status == ...` chain, and adding a state means editing every one of them.

### The structure

```
 Context ------------> State
 -state               +publish(ctx)
 +publish():          +edit(ctx)
   state.publish(self)   ^      ^
                         |      |
                      Draft  Review ...
 each state sets ctx.state to the next
```

Each state is an object that implements the behaviour for that state, and switches the context to the next state.

### In Python

```python
class Draft:
    def publish(self, doc):
        doc.state = Review()
        return "sent for review"

class Review:
    def publish(self, doc):
        if not doc.approved:
            return "needs approval"
        doc.state = Published()
        return "published"

class Published:
    def publish(self, doc):
        return "already published"

class Document:
    def __init__(self):
        self.state = Draft()
        self.approved = False

    def publish(self):
        return self.state.publish(self)

d = Document()
print(d.publish())   # sent for review
print(d.publish())   # needs approval
d.approved = True
print(d.publish())   # published
print(d.publish())   # already published
```

### The table-driven alternative

When states differ mainly in **which transitions are allowed**, rather than in rich behaviour, a transition table is clearer than a class per state:

```python
from enum import Enum

class S(Enum):
    DRAFT = 1
    REVIEW = 2
    PUBLISHED = 3

ALLOWED = {
    (S.DRAFT, "submit"): S.REVIEW,
    (S.REVIEW, "reject"): S.DRAFT,
    (S.REVIEW, "approve"): S.PUBLISHED,
}

def step(state, event):
    key = (state, event)
    if key not in ALLOWED:
        msg = f"{event} in {state}"
        raise ValueError(msg)
    return ALLOWED[key]
```

The whole state machine is visible in one place, can be drawn as a diagram, and can be tested by checking every pair.

### When not to use it

- Two or three states with trivial differences. An `if` is fine.
- When transitions, not behaviour, are the interesting part. Use a table.
- When state must be stored in a database. You'll be persisting an enum value anyway, so a class per state means converting back and forth.

### In real libraries

- The GoF's own example was a **TCP connection** whose `open`, `close` and `acknowledge` behave differently in Established, Listen and Closed states.
- **`transitions`** (Python) and **Spring Statemachine** (Java) are libraries for declaring state machines.
- Many real implementations are table- or enum-driven instead: the **h11** HTTP/1.1 library tracks each side's state (IDLE, SEND_BODY, DONE and so on) with explicit transition rules, and asyncio's `Future` moves between PENDING, CANCELLED and FINISHED.

## Template method

### The problem

Several classes share the same overall algorithm but differ in a few steps. You want the skeleton written once, with the steps filled in by subclasses.

### The structure

```
 AbstractClass
 +run():           (fixed skeleton)
   self.setup()
   self.step()     <- must override
   self.teardown()
       ^
       |
 ConcreteClass: step(), maybe setup()
```

The base class calls the subclass, not the other way round. This is sometimes called the **Hollywood principle**: "don't call us, we'll call you".

### In Python

```python
class Report:
    def render(self):
        parts = [self.header()]
        parts += [self.row(r)
                  for r in self.rows()]
        parts.append(self.footer())
        return "\n".join(parts)

    def header(self):
        return "REPORT"

    def footer(self):
        return "END"

    def rows(self):
        raise NotImplementedError

    def row(self, r):
        return str(r)

class Sales(Report):
    def rows(self):
        return [120, 80]

    def row(self, r):
        return f"£{r}"

print(Sales().render())
# REPORT
# £120
# £80
# END
```

Steps with a default (`header`, `row`) are optional **hooks**; `rows` is required. Mark required steps with `@abc.abstractmethod` if you want instantiation to fail fast when one is missing.

### When not to use it

- When subclasses would override most of the steps. The "shared skeleton" isn't really shared.
- When you need to vary steps independently and combine them. Inheritance gives one fixed combination per subclass; strategy objects passed in can be mixed freely.
- Deep hierarchies make template methods hard to follow: reading `render()` doesn't tell you which `row()` will run.

### In real libraries

- **`unittest.TestCase`**: `run()` normally calls setUp, the test and tearDown; tearDown is not run if setUp fails. Cleanup registered with addCleanup has separate guarantees.
- **`socketserver.BaseRequestHandler`**: after successful `setup()`, its constructor calls `handle()` and guarantees `finish()` via `finally`; if `setup()` raises, `finish()` is not called. You override `handle()`.
- **`threading.Thread`**: `start()` arranges for `run()` to be called on a new thread; you override `run()`.
- **Django's class-based views**: `dispatch()` routes to `get()` or `post()`, which you override.
- **`collections.abc.Mapping`**: implement `__getitem__`, `__iter__` and `__len__`, and you inherit `get`, `keys`, `items`, `__contains__` and more, all written in terms of those three.

## Iterator

### The problem

Clients want to walk through a collection without knowing how it's stored (array, tree, linked list, paginated API), and possibly have several walks in progress at once.

### The structure

```
 Aggregate              Iterator
 +__iter__() -------->  +__next__()
   returns new iter       next item or
                          StopIteration
```

### In Python

Python built this pattern into the language. A `for` loop calls `iter(x)` and then `next()` repeatedly until `StopIteration` is raised. A **generator** writes the iterator for you:

```python
class Tree:
    def __init__(self, val, kids=()):
        self.val = val
        self.kids = kids

    def __iter__(self):
        yield self.val
        for k in self.kids:
            yield from k

t = Tree(1, [Tree(2, [Tree(3)]), Tree(4)])
print(list(t))   # [1, 2, 3, 4]
```

Each call to `__iter__` returns a fresh generator, so two loops over `t` don't interfere.

The iterator protocol obtains one item per next() call; it does not require lazy construction or constant memory. Streaming can avoid loading the entire input, but memory still depends on buffering, maximum line/page size, retained output and traversal state (O(tree height) for this recursive generator).

> [!warning] Iterators are single-use
> An iterator is also iterable; once exhausted it stays exhausted. A re-iterable collection such as a list can supply a fresh iterator for another pass. `g = (x * 2 for x in range(3))` then `list(g)` gives `[0, 2, 4]`, and a second `list(g)` gives `[]`.

### When not to use it

- Don't write a hand-rolled iterator class when a generator function will do. It's longer and easier to get wrong.
- Lazy iteration can surprise you. Errors surface when the data is consumed, not when the generator is created, and structural mutation during iteration can invalidate traversal. Adding or deleting dictionary keys may raise `RuntimeError`; replacing values for existing keys need not. List insertions/deletions may skip or repeat elements, while replacing an existing element does not inherently invalidate iteration.

### In real libraries

- **Every Python container**, plus `itertools`, file objects (line by line), `os.scandir` and `csv.reader`.
- **Database cursors**: Many DB-API drivers provide iterable cursors (an optional DB-API extension). Server-side cursor modes can fetch batches without loading the whole result into the client.
- **Django QuerySets** are lazy and iterable; `.iterator()` bypasses the QuerySet result cache; database-driver buffering and backend support determine whether results are actually streamed.
- **Java's `Iterator`/`Iterable`** and C++ iterators (where the pattern is also the basis of the STL algorithms).

## Visitor

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
        m = getattr(self, "visit_" + name)
        return m(node)

class Evaluate(Visitor):
    def visit_Num(self, n):
        return n.v

    def visit_Add(self, n):
        v = self.visit
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

So visitor is right when the **types are stable and the operations keep growing**. A compiler is the classic case: the grammar changes rarely, but passes (type checking, constant folding, code generation, linting) are added all the time.

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
- State replaces `if status ==` chains with one object per state; when transitions matter more than behaviour, an enum plus a transition table is often clearer.
- Template method fixes an algorithm's skeleton in a base class and lets subclasses override steps; `unittest`, `socketserver` and Django views use it.
- Python builds iterator into the language: implement `__iter__` with a generator, and remember iterators can be exhausted, and the protocol alone does not guarantee lazy or bounded-memory execution.
- Visitor adds operations to a stable set of types via double dispatch; `ast.NodeVisitor` dispatches on `visit_<ClassName>`.
- The expression problem: methods on types make new types cheap, visitors make new operations cheap, and you can't have both for free.

## Further reading
- [State pattern — Wikipedia](https://en.wikipedia.org/wiki/State_pattern)
- [Template method pattern — Wikipedia](https://en.wikipedia.org/wiki/Template_method_pattern)
- [The Iterator pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/iterator/)
- [ast — Abstract syntax trees (NodeVisitor) — Python docs](https://docs.python.org/3/library/ast.html)
- [Expression problem — Wikipedia](https://en.wikipedia.org/wiki/Expression_problem)
- [PEP 636 — Structural pattern matching tutorial](https://peps.python.org/pep-0636/)
