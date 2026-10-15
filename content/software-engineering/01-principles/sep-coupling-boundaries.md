---
id: sep-coupling-boundaries
title: How dependencies cross module boundaries
level: intermediate
minutes: 4
summary: Coupling concerns connections between modules; cohesion concerns what belongs together inside.
sourceLesson: sep-coupling-cohesion
---

Ask why a "small" change took three days and touched eleven files, and one possible cause is the code was **tightly coupled** and **poorly cohesive**. These two ideas, developed by Larry Constantine in the 1960s and expanded in later *structured design* work, still underpin most design advice, including SOLID and microservice boundaries.

- **Coupling** is how much one module depends on another. Low coupling reduces how often a change in one requires changing the other.
- **Cohesion** is how closely the things *inside* a module belong together. High cohesion means a module has one clear purpose.

The goal is **low coupling, high cohesion**. They pull in the same direction: if related things live together, fewer connections have to cross module boundaries.

```
 Poor                    Good
 +-----+  +-----+        +-----+  +-----+
 | a c |==| b d |        | a b |--| c d |
 | e   |==| f   |        | e f |  |     |
 +-----+  +-----+        +-----+  +-----+
 many links across       related things
 the boundary            together, one link
```

## Coupling: what it really means

Every dependency is a reason a change in one place might force a change elsewhere. The question is not "is there a dependency?" (there always is) but "how much does each side need to know about the other?"

### The classic coupling scale

A traditional ordering from tighter to looser coupling follows. It is a design heuristic, not a universal ranking of harm:

| Type | One module... |
|---|---|
| Content | reaches into another's internals |
| Common | shares global mutable data |
| External | shares a format or device |
| Control | passes a mode flag steering the other |
| Stamp | passes a whole record, uses a bit |
| Data | passes only the values needed |

Some Python examples:

```python
# Content: poking a private field
order._items.append(item)

# Common: shared mutable global
CONFIG["currency"] = "EUR"

# Control: caller steers internal logic
report(data, mode="summary")

# Stamp: whole object, uses one field
def greet(user):
    return f"Hi {user.name}"

# Data: just what it needs
def greet(name):
    return f"Hi {name}"
```

Stamp coupling isn't always bad: passing `user` lets the function evolve without changing its signature. The dependency here is on an object exposing `name`. In dynamically typed Python it need not be a complete `User`; a small test double with that attribute works.

### Coupling you can't see

The most dangerous coupling is **implicit**: two modules agree on something that isn't written in either's interface.

- Both assume dates are in UTC.
- A consumer relies on a list being sorted, though the producer never promised it.
- Two services both know that status `3` means "cancelled".

Change one side and the other breaks with no compile error and often no test failure.

## Key takeaways
- Coupling concerns connections between modules; cohesion concerns what belongs together inside.
- An implicit agreement can couple modules even when their interfaces look narrow.
- The classic coupling scale is a diagnostic vocabulary, not a universal ranking of harm.

## Further reading
- [Constantine: history and early publications](https://history.computer.org/constantine.html)
- [coupling.pdf](https://martinfowler.com/ieeeSoftware/coupling.pdf)
- [Coupling_(computer_programming)](https://en.wikipedia.org/wiki/Coupling_(computer_programming))
