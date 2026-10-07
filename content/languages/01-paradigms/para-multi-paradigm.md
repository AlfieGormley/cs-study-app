---
id: para-multi-paradigm
title: Multi-paradigm languages and choosing one
level: intermediate
minutes: 12
summary: Why almost every modern language mixes paradigms, the expression problem that decides which style suits which code, and how to choose a language and a style on purpose.
---

The earlier lessons treated paradigms as separate worlds. In practice, almost no popular language is "pure" anything. Python has classes, first-class functions, comprehensions and a `match` statement. Java added lambdas, records and pattern matching. Rust has no classes yet feels object-oriented and functional at once.

A **multi-paradigm language** gives you several styles in one toolbox. That's powerful, but it moves the decision from the language designer to you. This lesson is about making that decision well.

## Why languages converged

Paradigms began as rival camps. Smalltalk was objects all the way down; Haskell was pure functions; Prolog was logic. Over the last two decades, mainstream languages borrowed the best ideas from each:

| Language | Base | Borrowed |
|---|---|---|
| Java | OOP | Lambdas, streams (8), records (16), sealed types (17) |
| C# | OOP | LINQ (3.0), pattern matching |
| C++ | Imperative/OOP | Lambdas (C++11), ranges (C++20) |
| Python | Imperative/OOP | Comprehensions, `match` (3.10) |
| JavaScript | Prototypes | First-class functions from day one |

Newer languages were designed mixed from the start. **Scala** and **Kotlin** fuse OOP and FP on the JVM. **Swift** pairs classes with value-type structs and enums with payloads. **F#** and **OCaml** are functional-first but have objects and mutable state when you need them.

**Rust** is a good example of how far the mix can go. It has:

- Structs and `impl` blocks with methods (object-like encapsulation)
- Traits for polymorphism, but no class inheritance
- Enums with data and exhaustive `match` (from the ML family)
- Iterator chains like `map` and `filter` that compile to tight loops
- Ordinary mutable variables and `for` loops

The reason for the convergence is simple: each paradigm is good at different parts of a program, and real programs have all those parts.

## The expression problem

The clearest way to see what each style is good at is the **expression problem**, a name Philip Wadler gave it in 1998. You have some *types* of data and some *operations* on them. Over time you'll add both. Which is easy depends on how you organised the code.

Here is the object-oriented version. Each class carries its own operations:

```python
class Circle:
    def __init__(self, r):
        self.r = r
    def area(self):
        return 3.14159 * self.r ** 2

class Square:
    def __init__(self, s):
        self.s = s
    def area(self):
        return self.s ** 2
```

Adding a new *type* (`Triangle`) is easy: write one new class, without editing existing shape operations, assuming construction/registration is handled separately. Adding a new *operation* (`perimeter`) is hard: you edit every class.

Here is the functional version, with plain data and functions that match on it:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Circle:
    r: float

@dataclass(frozen=True)
class Square:
    s: float

def area(shape):
    match shape:
        case Circle(r):
            return 3.14159 * r ** 2
        case Square(s):
            return s ** 2
```

Now it flips. Adding `perimeter` is one new function. Adding `Triangle` means editing every function that matches on shapes.

```
              add a type   add an operation
OOP classes   easy         edit every class
FP matching   edit every   easy
              function
```

Neither is wrong. The question is which axis your code grows along:

- **New types, fixed operations**: GUI widgets, plugins, payment providers. Each new kind of thing implements a known interface. OOP fits.
- **Fixed types, new operations**: compilers and interpreters. The syntax tree has a stable set of node kinds, and you keep adding passes (type check, optimise, generate code). Pattern matching fits, which is why compilers are so often written in OCaml, Haskell, Rust or Scala.

> [!note] The visitor pattern
> OOP languages without pattern matching use the **visitor pattern** to get the functional trade-off: each node has an `accept(visitor)` method, and each operation is a visitor class with one method per node type. It uses double dispatch to make new operations cheap, at the cost of making new node types expensive. It's pattern matching written the long way.

Closed variant sets support exhaustiveness checks where the language requires them, such as Rust match and Java 21 pattern-switch (Java sealed types themselves arrived in 17). Requirements vary by construct/language. Python’s interpreter does not check match exhaustiveness: no matching case continues after the statement, returning None only if the function then falls off its end.

## Functional core, imperative shell

A common way to mix paradigms in one program is the pattern Gary Bernhardt called **functional core, imperative shell**. Put the decisions in pure functions. Keep the side effects (network, database, clock, files) in a thin outer layer that calls them.

```python
# Core: pure, easy to test
def apply_discount(order, today):
    if today.weekday() == 4:   # Friday
        return order.total * 0.9
    return order.total

# Shell: effects, kept thin
def handle(order_id, db, clock):
    order = db.load(order_id)
    total = apply_discount(
        order, clock.today())
    db.save_total(order_id, total)
```

The core is tested with plain values and no mocks: pass in an order and a date, check the number. The shell still needs integration tests for failures, retries, transactions and other relevant boundary behavior. Notice that `today` is a *parameter*, not a call to `date.today()` inside the core. Hiding the clock call inside would make the function impure and its tests depend on the day you run them.

```
+---------------------------------+
| shell: HTTP, DB, clock, logging |
|   +-------------------------+   |
|   | core: pure decisions    |   |
|   | (values in, values out) |   |
|   +-------------------------+   |
+---------------------------------+
```

This scales up to architecture. Redux reducers, Elm's update function and event-sourced systems all put a pure "state + event → new state" function at the centre.

## Work with the language, not against it

A multi-paradigm language still has a *grain*: styles it supports well and styles it only tolerates. Fighting the grain costs performance and readability.

### Python

Python supports functional style but isn't built around it:

- **No tail-call optimisation.** Guido van Rossum rejected it deliberately, partly to keep full stack traces. The default recursion limit is 1,000 frames, so a recursive sum over a 10,000-item list raises `RecursionError`. Use a loop or `sum()`.
- **Lambdas are single expressions.** Anything longer should be a named `def`.
- **Immutability is shallow and opt-in.** A `frozen=True` dataclass blocks ordinary field assignment, but a list stored in a field can still be mutated. Use tuples and `frozenset` for the contents and ensure their nested contents are immutable too.
- **Copying is not free.** `sum(list_of_lists, [])` looks elegant but builds a new list at every step, which is quadratic for n single-element lists; more generally cost depends on both the number and lengths of the lists. `itertools.chain.from_iterable` is linear.

### JavaScript

JavaScript has had first-class functions and closures since 1995, and `map`, `filter` and `reduce` on arrays since ES5 (2009). Its objects use prototypes, with `class` syntax added in ES2015 as a cleaner way to write the same thing. ES2015 also specified proper tail calls, but in practice JavaScriptCore (used by Safari) implements them, so deep recursion in Chrome or Node still overflows the stack.

### Rust and C++

Here the functional style is often *free*. A chain like `v.iter().map(f).filter(g).sum()` compiles, after inlining, to roughly the same machine code as a hand-written loop. Rust's ownership rules also nudge you away from shared mutable state, the thing that makes OOP code hard to reason about.

### Java

Streams are pleasant but have overhead: pipeline objects and boxing can add overhead, though JIT optimization can remove some allocations and boxed values may be cached or already exist. For hot loops over primitives, use `IntStream` or a plain `for`.

## Choosing a language

The paradigm is rarely the deciding factor. In rough order of importance for most teams:

1. **Ecosystem and platform.** Swift is a common native iOS choice, though Objective-C and cross-platform approaches also exist. The browser means JavaScript or TypeScript (or something that compiles to it or to WebAssembly). Python is widely used in data science, because that's where NumPy, pandas and PyTorch live.
2. **The team.** A language five people know well beats a better one nobody knows. Hiring and onboarding count.
3. **Runtime needs.** Latency, memory and startup time. A garbage collector may be fine for a web service and a problem for a game engine or an embedded device.
4. **Correctness needs.** Strong static types and exhaustive matching catch whole classes of bug before production. That matters more for a payments ledger than a one-off script.
5. **Problem shape.** Rules and queries suggest SQL or Datalog. Tree transformations suggest an ML-family language. Highly concurrent servers suggest Go, Erlang/Elixir or Rust.

Most real systems use several languages: SQL for queries, a general-purpose language for services, a shell for glue, a configuration language for infrastructure. Choosing a language is often choosing which part of the system gets which one.

## Choosing a style within a language

Inside one codebase, a few rules of thumb help:

- **Data transformations**: pipelines, comprehensions or iterator chains.
- **Long-lived things with state and identity** (a connection pool, a game entity): objects with encapsulated state.
- **A closed set of variants** (AST nodes, message types, results): sealed types or enums with pattern matching.
- **An open set of implementations** (storage back ends, payment providers): interfaces, traits or protocols.
- **Effects**: at the edges, so the middle stays pure and testable.

## Pitfalls

- **Style soup.** One module uses classes, the next uses closures and dictionaries, the next uses inheritance six levels deep. Pick conventions per layer and write them down.
- **Clever over clear.** A three-line loop is often more readable than a nested `reduce` with a lambda. Use the declarative form when it states the intent better, not to show off.
- **Importing idioms that don't fit.** Monad libraries in Python, or faking class inheritance in Rust by abusing `Deref`, usually fight the language.
- **Choosing for the paradigm.** Rewriting a working system in a "better paradigm" language rarely pays for itself. The ecosystem, team and runtime usually matter more.

## Key takeaways
- Almost every mainstream language is multi-paradigm; the choice of style has moved from the language to the programmer.
- The expression problem: OOP makes new types cheap and new operations expensive; pattern matching does the opposite. Pick the one that matches how your code grows.
- Sealed types plus exhaustive matching give compile-time checks that every case is handled.
- "Functional core, imperative shell" keeps decisions pure and pushes effects to a thin outer layer.
- Every language has a grain: Python lacks tail calls and deep immutability; Rust iterator chains can optimize to loop-like code; Java stream overhead depends on boxing, workload and JIT optimization.
- Pick a language mainly on ecosystem, team, runtime and correctness needs; paradigm comes after.

## Further reading
- [Expression problem — Wikipedia](https://en.wikipedia.org/wiki/Expression_problem)
- [Comparison of multi-paradigm programming languages — Wikipedia](https://en.wikipedia.org/wiki/Comparison_of_multi-paradigm_programming_languages)
- [Functional Core, Imperative Shell — Destroy All Software](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
- [Tail Recursion Elimination — Guido van Rossum](https://neopythonic.blogspot.com/2009/04/tail-recursion-elimination.html)
- [PEP 636 – Structural Pattern Matching: Tutorial](https://peps.python.org/pep-0636/)
- [Comparing performance: loops vs. iterators — The Rust Book](https://doc.rust-lang.org/book/ch13-04-performance.html)
