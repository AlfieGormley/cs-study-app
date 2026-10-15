---
id: para-mixed-language-features
title: How languages mix paradigms
level: intermediate
minutes: 3
sourceLesson: para-multi-paradigm
summary: Most mainstream languages offer several ways to structure a program.
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

## Key takeaways
- Most mainstream languages offer several ways to structure a program.
- Feature support and release versions are concrete language facts.

## Further reading
- [Java 21 features](https://openjdk.org/projects/jdk/21/)
- [Rust: object-oriented features](https://doc.rust-lang.org/book/ch18-01-what-is-oo.html)
