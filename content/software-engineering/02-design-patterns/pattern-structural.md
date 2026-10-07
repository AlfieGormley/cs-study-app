---
id: pattern-structural
title: Structural patterns
level: intermediate
minutes: 16
summary: Adapter, decorator, proxy, facade, composite, bridge and flyweight, how to tell the wrappers apart, idiomatic Python for each, and where they live in io, requests, Django and the JDK.
---

Structural patterns are about **fitting objects together**: making mismatched interfaces line up, adding behaviour without subclassing, hiding complexity, and treating groups of things like single things.

Four of them (adapter, decorator, proxy, facade) look almost identical in code: one object holds another and forwards calls to it. What separates them is **intent**, and the quickest way to tell them apart is to ask what happens to the interface.

| Pattern | Interface it presents | Why |
|---|---|---|
| Adapter | A *different* one | Make it fit |
| Decorator | The *same* one | Add behaviour |
| Proxy | The *same* one | Control access |
| Facade | A *simpler* one | Hide a subsystem |

## Adapter

### The problem

You have code that expects interface A and a class that provides interface B. You can't (or shouldn't) change either. A typical case: wrapping a third-party SDK so the rest of your code depends on your own interface.

### The structure

```
 Client ---> Target interface
                  ^
                  |
              Adapter ------> Adaptee
              send(m)          post(body)
              calls post()
```

### In Python

```python
class LegacySms:
    def transmit(self, number, body):
        return f"sent {body!r} to {number}"

class SmsAdapter:
    """Presents send(to, msg)."""
    def __init__(self, legacy):
        self.legacy = legacy

    def send(self, to, msg):
        return self.legacy.transmit(
            number=to, body=msg)

def notify(channel):
    to = "+447700900000"
    return channel.send(to, "hi")

print(notify(SmsAdapter(LegacySms())))
# sent 'hi' to +447700900000
```

### When not to use it

- When you own both sides. Just change one of them.
- When the mismatch is semantic, not just a matter of names. If one API is synchronous and the other is callback-based, or one has transactions and the other doesn't, a thin adapter will leak.

### In real libraries

- **`io.TextIOWrapper`** adapts a binary stream (bytes) to a text stream (str), handling encoding and newlines. `open("f.txt")` returns one wrapped around a buffered binary file.
- **requests** has `HTTPAdapter`, which adapts requests' session API to urllib3's connection pools. You can `mount()` your own adapter for a URL prefix.
- **SLF4J** (Java) ships adapters (it calls them bindings or providers) that route its API to Logback, Log4j and others.

## Decorator

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
        return self.inner.read().upper()

class Exclaim:
    def __init__(self, inner):
        self.inner = inner

    def read(self):
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

## Proxy

### The problem

You want a stand-in that controls access to a real object: create it lazily, check permissions, call it over the network, or cache its results.

### The structure

```
 Client ---> Subject interface
               ^           ^
               |           |
          RealSubject <-- Proxy
                          +request():
                           check/load,
                           then forward
```

Structurally identical to decorator. The difference is intent: a proxy *manages* the real object (often creating it), while a decorator *adds* features to one it's given.

### In Python

A lazy (virtual) proxy:

```python
class BigReport:
    def __init__(self):
        print("expensive load")
        self.rows = list(range(3))

    def total(self):
        return sum(self.rows)

class LazyReport:
    def __init__(self):
        self._real = None

    def total(self):
        if self._real is None:
            self._real = BigReport()
        return self._real.total()

r = LazyReport()      # nothing loaded yet
print(r.total())      # expensive load, 3
print(r.total())      # 3 (no reload)
```

### When not to use it

- When the "transparent" stand-in hides behaviour that callers need to know about. A **remote proxy** makes a network call look like a local method call, but networks fail, time out and can have much higher and more variable latency than a local call; the ratio depends on the work and environment. Treating it as local falls for two classic fallacies of distributed computing: "the network is reliable" and "latency is zero".
- Lazy proxies can cause the **N+1 query problem**: looping over 100 lazily loaded ORM objects triggers 100 separate queries.

### In real libraries

- **`xmlrpc.client.ServerProxy`**: method calls become XML-RPC requests to a server.
- **`weakref.proxy`**: forwards to an object without keeping it alive.
- **Django's `SimpleLazyObject`**: `request.user` defers authentication lookup until needed; whether that lookup queries a database depends on the session and authentication backend.
- **ORM lazy loading** in SQLAlchemy and Hibernate: related objects are proxies or loaders that query on first access.

## Facade

### The problem

A subsystem has many classes and steps. Most callers want one common task done simply.

### The structure

```
 Client ---> Facade
             +do_task()
               |   |   |
               v   v   v
             [A]  [B]  [C]  subsystem
```

The subsystem stays available for callers who need the full power.

### In Python

```python
import subprocess

result = subprocess.run(
    ["echo", "hi"],
    capture_output=True, text=True)
print(result.stdout.strip())
# hi
```

`subprocess.run` is a facade over `Popen`: it starts the process, wires up pipes, waits, collects output and returns one result object. When you need streaming or bidirectional pipes, you drop down to `Popen` directly.

### When not to use it

- When the facade becomes a **god object** that every feature is bolted onto. A facade should cover the common path, not everything.
- When it hides options that callers genuinely need, forcing them round it in awkward ways.

### In real libraries

- **requests**: `requests.get(url)` creates a session, picks an adapter, manages the connection pool, follows redirects and returns a Response. Text decoding and JSON parsing are accessed through the response API; a one-shot call does not share a persistent session pool across unrelated calls.
- **`subprocess.run`** over `Popen`; **`shutil.copytree`** over `os` and file operations.
- **SLF4J** stands for *Simple Logging Facade for Java*.

## Composite

### The problem

You have a tree (files and folders, UI widgets, an expression) and want clients to treat a single item and a group of items **the same way**.

### The structure

```
        Component
        +size()
        ^       ^
        |       |
      Leaf    Composite
      size()  children: [Component]
              size(): sum of children
```

### In Python

```python
class File:
    def __init__(self, n):
        self.n = n

    def size(self):
        return self.n

class Folder:
    def __init__(self, *children):
        self.children = children

    def size(self):
        return sum(c.size()
                   for c in self.children)

tree = Folder(File(10),
              Folder(File(5), File(7)))
print(tree.size())
# 22
```

### When not to use it

- When leaves and groups genuinely behave differently. Forcing `add_child()` onto a leaf (to keep one interface) means a method that can only raise errors.
- Very deep trees can hit the active recursion limit; inspect sys.getrecursionlimit() rather than assuming a universal depth.

### In real libraries

- **scikit-learn's `Pipeline`** is itself an estimator, so a pipeline can sit inside another pipeline or a grid search.
- **The DOM**: elements contain elements, and most operations work on any node.
- **GUI toolkits** (Qt, Tkinter): a frame is a widget that contains widgets.
- **Python's `ast`**: a `Module` node contains statement nodes, which contain expression nodes.

## Bridge

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
        return self.renderer.circle(self.r)

print(Circle(3, Ascii()).draw())   # ooo
```

Extending the example to 2 shapes gives 2 shapes plus 2 renderers instead of 2 × 2 concrete combinations, and the gap widens as either list grows.

### When not to use it

When only one dimension actually varies. Then it's plain composition and needs no special name.

### In real libraries

- **JDBC**: your code uses the `Connection` and `Statement` API; each database vendor's driver supplies the implementation.
- **Python's `logging`**: loggers (what to log) and handlers (where it goes) vary independently.

## Flyweight

### The problem

You need huge numbers of small objects, and most of their state is identical. Store the shared (**intrinsic**) state once and pass the varying (**extrinsic**) state in.

### The structure

```
 Client --> FlyweightFactory
            cache: key -> Flyweight
            get(key): reuse or create
 Flyweight holds shared state only;
 position etc. passed in by client
```

### In Python

CPython already does this. Small integers from -5 to 256 are cached, and `sys.intern()` returns a canonical interned string; keep and use that return value. It does not rewrite existing references to equal non-interned strings. You can build your own with a cache:

```python
from functools import lru_cache
from dataclasses import dataclass

@dataclass(frozen=True)
class Glyph:
    char: str
    font: str

@lru_cache(maxsize=None)
def glyph(char, font):
    return Glyph(char, font)

a = glyph("e", "Arial")
b = glyph("e", "Arial")
print(a is b)   # True: one shared object
```

Each character on screen can store a reference to a shared glyph plus its own position. This sequential example reuses one cached object, but simultaneous first calls to `lru_cache` can construct duplicates. The unbounded cache also retains objects until cleared.

### When not to use it

- When there aren't many objects. The savings are negligible and the code is harder to follow.
- When the "shared" state is mutable. A change through one reference changes it for everyone.

### In real libraries

- **CPython's small-int cache and string interning**.
- **Java's `Integer.valueOf()`**, which caches values from -128 to 127.
- **`__slots__`** is a related memory technique: it can avoid a per-instance __dict__ when bases do not supply one and the class does not request one, which matters at millions of instances.

## Key takeaways
- Adapter, decorator, proxy and facade all wrap an object; tell them apart by intent: change the interface, add behaviour, control access, or simplify a subsystem.
- Decorators stack, so order matters; Python's `@` syntax applies the same idea to functions.
- Proxies that hide the network or lazy loading can hide failures and N+1 queries.
- Composite lets you treat one item and a tree of items the same way.
- Bridge replaces a grid of subclasses with two independent hierarchies.
- Flyweight shares immutable state across huge numbers of objects; CPython does it for small ints and interned strings.

## Further reading
- [The Decorator pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/decorator-pattern/)
- [The Composite pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/composite/)
- [The Flyweight pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/flyweight/)
- [io — Core tools for working with streams — Python docs](https://docs.python.org/3/library/io.html)
- [Transport adapters — Requests advanced usage](https://requests.readthedocs.io/en/latest/user/advanced/)
- [Proxy pattern — Wikipedia](https://en.wikipedia.org/wiki/Proxy_pattern)
