---
id: pattern-creational
title: Creational patterns
level: basic
minutes: 14
summary: Factory method, abstract factory, builder, prototype and singleton, what each solves, how they look in idiomatic Python, when to avoid them, and where real libraries use them.
---

Creating an object looks trivial: `Thing()`. The trouble is that a constructor call hard-codes three decisions at the call site: **which class**, **how it's configured** and **whether a new one is made at all**.

When those decisions need to vary (by platform, by configuration, by test), every call site has to change. Creational patterns move those decisions to one place.

Python changes the picture a lot. Classes are objects you can pass around, functions are first-class, and keyword arguments with defaults remove much of the need for builders. So for each pattern below, we'll see the classic shape and then the Python way.

## Factory method

### The problem

A framework class knows *when* it needs an object but not *which* class to make. Its subclasses do.

For example, a generic list view knows it must fetch records, but only a specific view knows which records.

### The structure

```
  Creator                  Product
  +make() -> Product  ...> (interface)
  +operation()                ^
      ^                       |
      |                       |
  ConcreteCreator ------> ConcreteProduct
  +make()   creates
```

`operation()` in the base class calls `self.make()`. Subclasses override `make()` to return their own product.

### In Python

```python
class Exporter:
    def make_writer(self):
        raise NotImplementedError

    def export(self, rows):
        w = self.make_writer()
        for row in rows:
            w.write(row)
        return w.result()

class CsvWriter:
    # Toy: fields contain no commas,
    # quotes or newlines. Use csv.writer
    # for general CSV serialization.
    def __init__(self):
        self.lines = []

    def write(self, row):
        self.lines.append(",".join(row))

    def result(self):
        return "\n".join(self.lines)

class CsvExporter(Exporter):
    def make_writer(self):
        return CsvWriter()

print(CsvExporter().export([["a", "b"]]))
# a,b
```

Often a simpler Python version is to pass the class (or any callable) in: `Exporter(writer_factory=CsvWriter)`. `collections.defaultdict(list)` does exactly this: `list` is the factory it calls for missing-key indexing (d[key]); get() does not invoke it.

### When not to use it

- When there's only ever one product class. Just call it.
- When the subclass exists *only* to override the factory. Passing a callable is lighter than a subclass per product.

### In real libraries

- **Django class-based views**: `get_queryset()` and `get_form_class()` are factory methods that subclasses override.
- **Django REST Framework**: `get_serializer_class()`.
- **Alternative constructors** such as `datetime.fromtimestamp()` and `dict.fromkeys()` are `classmethod` factories. They're not the GoF pattern exactly, but they serve the same purpose: named ways to create an object.

## Abstract factory

### The problem

You need to create **families** of related objects that must match. A dark-theme button must go with a dark-theme scrollbar; a PostgreSQL connection must go with a PostgreSQL query compiler.

### The structure

```
        UIFactory
   +button()  +menu()
      ^             ^
      |             |
  MacFactory     WinFactory
  MacButton      WinButton
  MacMenu        WinMenu
```

If the client obtains every part from one correctly implemented factory, the family stays consistent. The pattern itself does not prevent bypassing the factory or a faulty implementation.

### In Python

```python
class DarkTheme:
    def button(self, label):
        return f"[{label}] on black"

    def text(self, s):
        return f"{s} in white"

class LightTheme:
    def button(self, label):
        return f"[{label}] on white"

    def text(self, s):
        return f"{s} in black"

def render(theme):
    return [theme.button("OK"),
            theme.text("Saved")]

print(render(DarkTheme()))
# ['[OK] on black', 'Saved in white']
```

No base class is needed; duck typing does the job. Add an ABC or `typing.Protocol` if you want type checkers to verify each theme has every method.

### When not to use it

- When there's only one family, or the parts don't actually need to match.
- When families change often. Adding a new *kind* of part (say, `slider()`) means changing every factory.

### In real libraries

- **Java's `javax.xml.parsers.DocumentBuilderFactory`** picks an XML parser implementation at run time and hands out matching builders.
- **Database drivers and dialects** are close cousins: SQLAlchemy picks a dialect from the URL, and that dialect supplies the matching type compiler, SQL compiler and DB-API module.

## Builder

### The problem

Some objects need many optional settings, or have to be assembled step by step. A constructor with twelve positional arguments is unreadable, and partial objects can leak out before they're valid.

### The structure

```
 Client --> Builder ------------> Product
            .with_a(x) -> self
            .with_b(y) -> self
            .build() validates,
                     returns Product
```

### In Python

Keyword arguments with defaults already solve the "telescoping constructor" problem that drove builders in Java. A `dataclass` gives you that for free.

Builders still earn their place when construction is genuinely **incremental**, when you want to **validate once at the end**, or when the result should be **immutable**:

```python
class QueryBuilder:
    def __init__(self, table):
        self.table = table
        self.wheres = []
        self.limit_n = None

    def where(self, cond):
        self.wheres.append(cond)
        return self

    def limit(self, n):
        self.limit_n = n
        return self

    def build(self):
        sql = f"SELECT * FROM {self.table}"
        if self.wheres:
            sql += " WHERE "
            sql += " AND ".join(self.wheres)
        if self.limit_n is not None:
            sql += f" LIMIT {self.limit_n}"
        return sql

q = (QueryBuilder("users")
     .where("age > 18")
     .where("active")
     .limit(10)
     .build())
print(q)
```

That prints one line: `SELECT * FROM users WHERE age > 18 AND active LIMIT 10`.

> [!warning] Not for real SQL
> This toy pastes strings together, which invites SQL injection. Real query builders keep values as bound parameters.

### When not to use it

- When a constructor with keyword arguments, or a `dataclass`, would do. In Python that's most of the time.
- When there's no validation or ordering between steps. Then the builder is just a slower constructor.

### In real libraries

- **SQLAlchemy**: `select(User).where(User.age > 18).order_by(User.name)` builds a statement step by step. Each call returns a new statement object, so partial queries can be safely reused.
- **Java**: `StringBuilder`, and the `newBuilder()...build()` builders generated by **Protocol Buffers**.
- **OkHttp** (Java/Kotlin): `Request.Builder().url(...).header(...).build()`.

## Prototype

### The problem

Making an object from scratch is expensive or complicated, but you have a configured example. You want "another one like that", without knowing its concrete class.

### The structure

```
 Client ---> Prototype
             +clone() -> copy
                ^
                |
          ConcretePrototype
          clone(): copy self
```

### In Python

Python's `copy` module is the prototype pattern. `copy.copy()` makes a shallow copy; `copy.deepcopy()` recursively copies supported components, respecting memoisation and class hooks. It can preserve shared objects and returns some objects, including functions and classes, unchanged. Classes customise this with `__copy__` and `__deepcopy__`.

```python
import copy

base = {"retries": 3,
        "headers": {"User-Agent": "app"}}

a = copy.copy(base)
a["headers"]["X-Trace"] = "1"
print("X-Trace" in base["headers"])
# True: shallow copy shares the dict

b = copy.deepcopy(base)
b["headers"]["X-Id"] = "2"
print("X-Id" in base["headers"])
# False: deep copy has its own dict
```

### When not to use it

- When construction is cheap: just call the constructor.
- When objects hold resources that can't be meaningfully copied (open sockets, locks, file handles). `deepcopy` will either fail or produce something broken.
- When the shallow/deep distinction will confuse readers. Shared nested state is a classic source of bugs.

### In real libraries

- **Python's `copy` module** and the `__copy__`/`__deepcopy__` hooks.
- **Java's `Object.clone()`** and the `Cloneable` interface (widely regarded as awkward; copy constructors are usually preferred).
- **JavaScript's prototypes** share the name and a similar spirit: objects inherit from another object rather than a class.

## Singleton

### The problem

Exactly one instance of something should exist, with a global access point: a configuration registry, a connection pool, a logging system.

### The structure

```
   Singleton
   -_instance (class field)
   +instance() -> Singleton
     if no _instance: create
     return _instance
```

### In Python

You *can* enforce a singleton by overriding `__new__`, but the idiomatic answer is simpler: **ordinary imports share a cached module within one interpreter**. Normal imports of the same name reuse sys.modules; reloads, aliases, cache manipulation and separate processes mean this is not a universal singleton guarantee.

```python
# settings.py
class _Settings:
    def __init__(self):
        self.debug = False

settings = _Settings()

# anywhere else:
# from settings import settings
```

The standard library does this all over the place. `None`, `True` and `False` are single instances. `logging.getLogger("app")` returns the same logger object every time for the same name (a registry of named instances).

### When not to use it

Singleton is the most criticised GoF pattern, for good reason:

- **It's global mutable state.** Any code can change it, so behaviour depends on hidden history.
- **It hides dependencies.** A function that reaches for `Database.instance()` doesn't say so in its signature.
- **It's hard to test.** Tests share the instance and leak state into each other unless you reset it carefully.
- **"Only one" often stops being true.** Two databases, a second tenant, a per-test config.

> [!tip] Prefer passing the object in
> Create one instance at start-up and pass it to whatever needs it (dependency injection). You still get one instance, but the dependency is visible and tests can pass a fake.

### In real libraries

- **Python modules**, `None`, and `logging.getLogger(name)`.
- **Java's `Runtime.getRuntime()`**.
- **Spring beans** default to singleton scope per bean definition per container, not one object globally across all containers; they are managed and injected, which avoids most of the testing pain.

## Choosing between them

| Need | Pattern | Python shortcut |
|---|---|---|
| Subclass picks class | Factory method | Pass a callable |
| Matching families | Abstract factory | Object with methods |
| Many options, validate | Builder | Keyword args |
| Copy a configured one | Prototype | `copy` module |
| One shared instance | Singleton | Module object |

## Key takeaways
- Creational patterns move "which class, how configured, new or shared" out of call sites into one place.
- Factory method lets subclasses choose the product; in Python, passing a class or callable is often enough.
- Abstract factory centralises creation of matching families of objects but makes adding a new kind of part expensive.
- Builders are mostly replaced by keyword arguments in Python; use one for incremental construction or end-of-build validation.
- Prototype is the `copy` module; watch the shallow/deep distinction.
- Singleton is global state in disguise. Use a module-level object or, better, create one instance and pass it in.

## Further reading
- [Factory method pattern — Wikipedia](https://en.wikipedia.org/wiki/Factory_method_pattern)
- [The Factory Method pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/factory-method/)
- [The Builder pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/builder/)
- [The Singleton pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/singleton/)
- [copy — Shallow and deep copy operations — Python docs](https://docs.python.org/3/library/copy.html)
- [Using SELECT statements — SQLAlchemy docs](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html)
