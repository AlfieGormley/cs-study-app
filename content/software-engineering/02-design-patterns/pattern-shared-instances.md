---
id: pattern-shared-instances
title: Shared instances and singleton trade-offs
level: basic
minutes: 3
sourceLesson: pattern-creational
summary: Ordinary same-name imports share a module cache within one interpreter.
---

## Singleton pattern

### The problem

Exactly one instance of something should exist, reachable from anywhere through one global name: a configuration registry, a connection pool, a logging system.

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

# Normal same-name imports reuse this.
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
- **Spring beans** default to singleton scope per bean definition per Spring IoC container, not one object globally across all Spring IoC containers; they are managed and injected, which avoids most of the testing pain.

## Choosing between them

| Need | Pattern | Python shortcut |
|---|---|---|
| Subclass picks class | Factory method | Pass a callable |
| Matching families | Abstract factory | Object with methods |
| Many options, validate | Builder | Keyword args |
| Copy a configured one | Prototype | `copy` module |
| One shared instance | Singleton | Module object |

## Key takeaways
- Ordinary same-name imports share a module cache within one interpreter.
- One shared Python instance can be created at start-up and passed in explicitly.
- A singleton lifecycle does not justify hidden mutable dependencies.

## Further reading
- [The import system — Python documentation](https://docs.python.org/3/reference/import.html)
- [logging — Python documentation](https://docs.python.org/3/library/logging.html)
- [Bean scopes — Spring Framework documentation](https://docs.spring.io/spring-framework/reference/core/beans/factory-scopes.html)
- [Factory method pattern — Wikipedia](https://en.wikipedia.org/wiki/Factory_method_pattern)
- [The Factory Method pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/factory-method/)
- [The Builder pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/builder/)
- [The Singleton pattern in Python — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/singleton/)
- [copy — Shallow and deep copy operations — Python docs](https://docs.python.org/3/library/copy.html)
- [Using SELECT statements — SQLAlchemy docs](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html)
