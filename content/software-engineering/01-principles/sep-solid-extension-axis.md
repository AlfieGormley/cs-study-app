---
id: sep-solid-extension-axis
title: Open/closed: choose the axis of extension
level: intermediate
minutes: 3
summary: An extension point protects a particular kind of change.
sourceLesson: sep-solid
---

SOLID examines responsibility, extension, subtyping, interfaces and dependency direction. This unit focuses on one of those questions; the earlier units establish the shared vocabulary.

## O: Open/closed principle

Bertrand Meyer’s open/closed principle says software entities should be **open for extension but closed for modification**. You should be able to add new behaviour by adding code, not by editing code that already works.

```python
# The dispatcher must learn each new kind.
# Before: every new shape edits this
def area(shape):
    if shape.kind == "circle":
        return math.pi * shape.r ** 2
    elif shape.kind == "square":
        return shape.side ** 2
    # add triangle here... and in
    # perimeter(), draw(), to_json()...
```

The real cost isn't one `elif`. It's that the same `if kind ==` ladder tends to appear in many functions, so a new shape means finding and editing all of them.

```python
# Each shape supplies its own calculation.
# After: new shapes are new classes
import math
from dataclasses import dataclass
from typing import Protocol

class Shape(Protocol):
    def area(self) -> float: ...

@dataclass
class Circle:
    r: float
    def area(self):
        return math.pi * self.r ** 2

@dataclass
class Square:
    side: float
    def area(self):
        return self.side ** 2
```

Adding `Triangle` touches no existing code. Plug-in architectures, middleware chains and strategy objects are all OCP in practice.

> [!warning] You can't be closed against everything
> OCP protects you along the axis you predicted. Polymorphic shapes make adding a *shape* easy but adding an *operation* (say `volume`) harder, since every class changes. Choose the axis that actually varies. This trade-off is known as the **expression problem**.

## Key takeaways
- An extension point protects a particular kind of change.
- Shape classes make new shapes easier; operations over a stable set of types may fit separate functions.
- Avoid scattering the same type switch through many operations.

## Further reading
- [Martin: principles and patterns](https://objectmentor.com/resources/articles/Principles_and_Patterns.pdf)
- [Wadler: the expression problem](https://homepages.inf.ed.ac.uk/wadler/papers/expression/expression.txt)
- [Open%E2%80%93closed_principle](https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle)
- [peps.python.org](https://peps.python.org/pep-0544/)
