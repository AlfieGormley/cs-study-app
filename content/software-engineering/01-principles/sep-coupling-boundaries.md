---
id: sep-coupling-boundaries
title: How dependencies cross module boundaries
level: intermediate
minutes: 5
summary: Coupling concerns connections between modules; cohesion concerns what belongs together inside.
sourceLesson: sep-coupling-cohesion
---

Ask why a "small" change took three days and touched eleven files, and one possible cause is the code was **tightly coupled** and **poorly cohesive**. Larry Constantine developed these two ideas in the 1960s. They were published in the 1974 paper *Structured Design* (with Wayne Stevens and Glenford Myers) and in Yourdon and Constantine's later book, and they still underpin much later design advice, including SOLID and microservice boundaries.

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

## Information hiding: what a module keeps to itself

Where should the boundaries go in the first place? David Parnas's 1972 paper *On the Criteria To Be Used in Decomposing Systems into Modules* gave a classic answer. Rather than making one module per step of a flowchart, start from the **design decisions that are difficult or likely to change**, such as an input format, how data is stored or which sorting algorithm is used. Give each module one such decision to hide behind its interface. This is **information hiding**: when the hidden decision changes, only the module that owns it has to change.

> [!analogy] Real-world analogy: a restaurant's order slip
> A waiter hands the kitchen an order slip. The kitchen decides how to cook it, which fridge holds the fish and who works the grill. Each station (pastry, grill) keeps its own tools and ingredients together.
>
> **How it maps:** The order slip is a narrow interface that passes only the data needed. The recipes and storage are the kitchen's hidden decisions. A waiter who walks in and takes fish from the fridge is depending on internals: rearrange the fridge and the waiter's routine breaks. A station that holds everything for one kind of dish is a cohesive module.
>
> **Where it stops:** People notice a change and adapt; code does not. A broken software dependency fails at build time, at runtime or silently, and an implicit agreement (such as an assumed time zone) has no slip that anyone can read.

## Coupling: what it really means

Every dependency is a reason a change in one place might force a change elsewhere. The question is not "is there a dependency?" (there always is) but "how much does each side need to know about the other?"

### The classic coupling scale

A traditional ordering from tighter to looser coupling follows. Read it with information hiding in mind: the tighter forms let one module see more of another's hidden decisions. It is a design heuristic, not a universal ranking of harm:

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

Some of the most troublesome coupling is **implicit**: two modules agree on something that isn't written in either's interface.

- Both assume dates are in UTC.
- A consumer relies on a list being sorted, though the producer never promised it.
- Two services both know that status `3` means "cancelled".

Change one side and the other breaks with no compile error and often no test failure.

## Key takeaways
- Coupling concerns connections between modules; cohesion concerns what belongs together inside.
- Information hiding draws boundaries around decisions likely to change, so each change stays inside one module.
- An implicit agreement can couple modules even when their interfaces look narrow.
- The classic coupling scale is a diagnostic vocabulary, not a universal ranking of harm.

## Further reading
- [Constantine: history and early publications](https://history.computer.org/constantine.html)
- [Information hiding (Parnas 1972 and later work)](https://en.wikipedia.org/wiki/Information_hiding)
- [Martin Fowler: Reducing Coupling (IEEE Software)](https://martinfowler.com/ieeeSoftware/coupling.pdf)
- [Coupling (computer programming)](https://en.wikipedia.org/wiki/Coupling_(computer_programming))
