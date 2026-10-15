---
id: para-expression-extension
title: The expression problem and extension axes
level: intermediate
minutes: 3
sourceLesson: para-multi-paradigm
summary: Class-based interfaces make adding implementations convenient.
---

A design can make adding data variants convenient or make adding operations convenient. Identify which axis changes most often before choosing how to organise the code.

## The expression problem

The clearest way to see what each style is good at is the **expression problem**, a name Philip Wadler gave it in 1998. You have some *types* of data and some *operations* on them. Over time you'll add both. Which is easy depends on how you organised the code.

Here is the object-oriented version. Each class carries its own operations:

```python
# Each class owns its area operation.
class Circle:
    def __init__(self, r):
        self.r = r
    def area(self):
        return 3.14159 * self.r ** 2

class Square:
    def __init__(self, s):
        self.s = s
    def area(self):
        return self.s ** 2
```

Adding a new *type* (`Triangle`) is easy: write one new class, without editing existing shape operations, assuming construction/registration is handled separately. Adding a new *operation* (`perimeter`) is hard: you edit every class.

Here is the functional version, with plain data and functions that match on it:

```python
# Match data variants in one operation.
from dataclasses import dataclass

@dataclass(frozen=True)
class Circle:
    r: float

@dataclass(frozen=True)
class Square:
    s: float

def area(shape):
    match shape:
        case Circle(r):
            return 3.14159 * r ** 2
        case Square(s):
            return s ** 2
```

Now it flips. Adding `perimeter` is one new function. Adding `Triangle` means editing every function that matches on shapes.

```
              add a type   add an operation
OOP classes   easy         edit every class
FP matching   edit every   easy
              function
```

Neither is wrong. The question is which axis your code grows along:

- New types, fixed operations: GUI widgets, plugins, payment providers. Each new kind of thing implements a known interface. OOP fits.
- Fixed types, new operations: compilers and interpreters. The syntax tree has a stable set of node kinds, and you keep adding passes (type check, optimise, generate code). Pattern matching fits, which is why compilers are so often written in OCaml, Haskell, Rust or Scala.

> [!note] The visitor pattern
> OOP languages without pattern matching use the **visitor pattern** to get the functional trade-off: each node has an `accept(visitor)` method, and each operation is a visitor class with one method per node type. It uses double dispatch to make new operations cheap, at the cost of making new node types expensive. It's pattern matching written the long way.

Closed variant sets support exhaustiveness checks where the language requires them, such as Rust match and Java 21 pattern-switch (Java sealed types themselves arrived in 17). Requirements vary by construct/language. Python’s interpreter does not check match exhaustiveness: no matching case continues after the statement, returning None only if the function then falls off its end.

## Key takeaways
- Class-based interfaces make adding implementations convenient.
- Pattern matching over closed variants makes adding operations convenient.

## Further reading
- [Philip Wadler: the expression problem](https://homepages.inf.ed.ac.uk/wadler/papers/expression/expression.txt)
- [Python: pattern matching tutorial](https://peps.python.org/pep-0636/)
