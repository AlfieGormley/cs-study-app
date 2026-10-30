---
id: pattern-independent-bridges
title: Bridging independent dimensions
level: intermediate
minutes: 3
sourceLesson: pattern-structural
summary: A bridge composes independently varying abstractions and implementations.
---

## Bridge pattern

### The problem

Two dimensions vary independently, say *shape* (circle, square) and *renderer* (SVG, PNG). Subclassing both gives one class per pair.

### The structure

```
 Abstraction ---------> Implementor
 +draw()      has-a     +render_*()
     ^                     ^     ^
     |                     |     |
 Circle, Square           Svg   Png
```

### In Python

```python
class Svg:
    def circle(self, r):
        return f'<circle r="{r}" />'

class Ascii:
    def circle(self, r):
        return "o" * r

class Circle:
    def __init__(self, r, renderer):
        self.r = r
        self.renderer = renderer

    def draw(self):
        # Delegate drawing to the selected
        # implementation, not a subclass.
        return self.renderer.circle(self.r)

print(Circle(3, Ascii()).draw())   # ooo
```

Why bother? With one subclass per (shape, renderer) pair, the classes *multiply*: every new renderer needs a new class for every shape. With a bridge, each shape and each renderer is written once, so they only *add*. At 2 shapes and 2 renderers there is no saving (4 classes either way); at 5 shapes and 4 renderers it is 20 classes against 9, and the gap widens as either list grows.

That saving assumes the two dimensions really are independent: every shape can be drawn by every renderer through the same small renderer interface. If one renderer needs special code for each shape, some of the multiplication comes back.

### When not to use it

When only one dimension actually varies. Then it's plain composition and needs no special name.

### In real libraries

- **JDBC**: your code uses the `Connection` and `Statement` API; each database vendor's driver supplies the implementation.
- **Python's `logging`**: loggers (what to log) and handlers (where it goes) vary independently.

## Key takeaways
- A bridge composes independently varying abstractions and implementations.
- Class counts add rather than multiply only when the dimensions truly fit the same interface.
- When just one dimension varies, ordinary composition may be enough.

## Further reading
- [Design Patterns — publisher catalogue](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-software-9780201633610)
- [logging — Python documentation](https://docs.python.org/3/library/logging.html)
