---
id: pattern-shared-flyweights
title: Sharing repeated immutable state
level: intermediate
minutes: 3
sourceLesson: pattern-structural
summary: Flyweights share intrinsic state while each use supplies its varying state.
---

## Flyweight pattern

### The problem

You need huge numbers of small objects, and most of their state is identical. Store the shared state (the **intrinsic state**) once and pass the varying state (the **extrinsic state**) in.

### The structure

```
 Client --> FlyweightFactory
            cache: key -> Flyweight
            get(key): reuse or create
 Flyweight holds shared state only;
 position etc. passed in by client
```

### In Python

CPython already does this. Its small-integer cache holds one shared Python instance for each integer from -5 to 256, and `sys.intern()` returns a canonical interned string; keep and use that return value. It does not rewrite existing references to equal non-interned strings. You can build your own with a cache:

```python
from functools import lru_cache
from dataclasses import dataclass

# Shared fields cannot be reassigned.
@dataclass(frozen=True)
class Glyph:
    char: str
    font: str

@lru_cache(maxsize=None)
def glyph(char, font):
    # Cache key: the character/font pair.
    return Glyph(char, font)

a = glyph("e", "Arial")
b = glyph("e", "Arial")
print(a is b)   # True: cached glyph
```

Each character on screen can store a reference to a shared glyph plus its own position. This sequential example reuses one cached object, but simultaneous first calls to `lru_cache` can construct duplicates. The unbounded cache also retains objects until cleared.

### When not to use it

- When there aren't many objects. The savings are negligible and the code is harder to follow.
- When the "shared" state is mutable. A change through one reference changes it for everyone.

### In real libraries

- **CPython's small-int cache and string interning**.
- **Java's `Integer.valueOf()`**, which always caches values from -128 to 127 and may cache more, so `==` on boxed integers is unreliable outside that range.
- **`__slots__`** is a related memory technique: it can avoid a per-instance __dict__ when bases do not supply one and the class does not request one, which matters at millions of instances.

## Key takeaways
- Flyweights share intrinsic state while each use supplies its varying state.
- Cache retention and concurrent first calls affect the resource trade-off.
- CPython integer identity is an implementation detail rather than a portable equality test.

## Further reading
- [Integer objects — CPython C API documentation](https://docs.python.org/3/c-api/long.html)
- [sys — Python documentation](https://docs.python.org/3/library/sys.html)
- [functools — Python documentation](https://docs.python.org/3/library/functools.html)
- [The Decorator pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/decorator-pattern/)
- [The Composite pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/composite/)
- [The Flyweight pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/flyweight/)
- [io — Core tools for working with streams — Python docs](https://docs.python.org/3/library/io.html)
- [Transport adapters — Requests advanced usage](https://requests.readthedocs.io/en/latest/user/advanced/)
- [Proxy pattern — Wikipedia](https://en.wikipedia.org/wiki/Proxy_pattern)
