---
id: pattern-stacked-decorators
title: Stacking behaviour with decorators
level: intermediate
minutes: 3
sourceLesson: pattern-structural
summary: A GoF decorator preserves the relevant interface while adding responsibilities.
---

## Decorator pattern

### The problem

You want to add responsibilities to an object (buffering, logging, retries, caching) without subclassing, and you want to **stack** them in any combination.

### The structure

```
        Component
        +read()
        ^      ^
        |      |
  Concrete   Decorator --> Component
  +read()    +read(): extra work,
              then inner.read()
```

The decorator implements the same interface as the thing it wraps, so wrappers can wrap wrappers.

### In Python

```python
class Source:
    def read(self):
        return "hello"

class Upper:
    def __init__(self, inner):
        self.inner = inner

    def read(self):
        # Transform the wrapped result.
        return self.inner.read().upper()

class Exclaim:
    def __init__(self, inner):
        self.inner = inner

    def read(self):
        # This layer adds its own behaviour.
        return self.inner.read() + "!"

print(Exclaim(Upper(Source())).read())
# HELLO!
```

> [!note] Python's `@decorator` syntax is related, not identical
> `@functools.lru_cache` wraps a *function* in another callable with the same calling interface. That is the decorator idea applied to functions. The GoF pattern wraps *objects*. Same intent, different granularity.

### When not to use it

- When order matters in subtle ways. `Encrypt(Compress(x))` and `Compress(Encrypt(x))` behave very differently (encrypted data barely compresses).
- When code checks the concrete type (`isinstance(f, FileIO)`). The wrapper hides it.
- Deep stacks make debugging painful: a stack trace may pass through ten wrappers.

### In real libraries

- **Java I/O**: `new BufferedInputStream(new FileInputStream(f))` is the textbook example.
- **Python I/O**: `BufferedReader` wraps a raw `FileIO` and adds buffering behind the same `read()` interface.
- **WSGI and ASGI middleware**: each middleware is an application that wraps another application.
- **`functools.lru_cache`** adds caching to a callable; **`functools.wraps`** helps preserve wrapper metadata. Python decorator syntax is broader than the GoF pattern: Flask route decorators register a view and can return it unchanged; decorators need not wrap calls.

## Key takeaways
- A GoF decorator preserves the relevant interface while adding responsibilities.
- Wrappers can compose, but the order of compression and encryption matters.
- Python decorator syntax can register or replace a function without wrapping its calls.

## Further reading
- [io — Python documentation](https://docs.python.org/3/library/io.html)
- [functools — Python documentation](https://docs.python.org/3/library/functools.html)
