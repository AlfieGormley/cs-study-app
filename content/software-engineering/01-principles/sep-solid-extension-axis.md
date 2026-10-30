---
id: sep-solid-extension-axis
title: Open/closed: choose the axis of extension
level: intermediate
minutes: 3
summary: An extension point protects a particular kind of change.
sourceLesson: sep-solid
---

Some changes keep arriving in the same shape: a new payment method, a new file format, a new shape to draw. This lesson is about arranging code so that kind of change means adding code rather than editing it, and about the cost of guessing the wrong kind.

## O: Open/closed principle

Bertrand Meyer coined the open/closed principle in *Object-Oriented Software Construction* (1988): software entities should be **open for extension but closed for modification**. You should be able to add new behaviour by adding code, not by editing code that already works.

Meyer's mechanism was implementation inheritance: a finished class stays closed, and new subclasses extend it. The version usually taught today is Robert C. Martin's 1996 reformulation, which uses abstract interfaces and polymorphism: callers depend on an interface, and new implementations plug in behind it.

```python
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

> [!analogy] Real-world analogy: an electrical outlet
> A house's outlets let you add a lamp, a kettle or a phone charger without rewiring anything. The outlet is a fixed standard, and each new appliance's plug just has to fit it.
>
> **How it maps:** The outlet is the stable interface (`Shape.area`). Each appliance is a new class that plugs in, and the house wiring is the existing code that stays closed to modification.
>
> **Where it stops:** The outlet only protects the kind of change it was designed for. New appliances are easy; changing what every appliance must do, such as running from a car battery, means changing every plug and outlet. That is the trade-off in the warning below.

> [!warning] You can't be closed against everything
> OCP protects you along the axis you predicted. Polymorphic shapes make adding a *shape* easy but adding an *operation* (say `volume`) harder, since every class changes. Choose the axis that actually varies. This trade-off is known as the **expression problem**.

## Key takeaways
- An extension point protects a particular kind of change.
- Shape classes make new shapes easier; operations over a stable set of types may fit separate functions.
- Avoid scattering the same type switch through many operations.

## Further reading
- [Martin: Design Principles and Design Patterns (2000)](https://objectmentor.com/resources/articles/Principles_and_Patterns.pdf)
- [Wadler: the expression problem](https://homepages.inf.ed.ac.uk/wadler/papers/expression/expression.txt)
- [Open–closed principle (Meyer and Martin versions)](https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle)
- [PEP 544: Protocols](https://peps.python.org/pep-0544/)
