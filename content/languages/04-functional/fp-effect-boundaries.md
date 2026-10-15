---
id: fp-effect-boundaries
title: Promise laws and effect boundaries
level: intermediate
minutes: 3
sourceLesson: fp-functors-monads
summary: Promise assimilation differs from a generic lawful wrapper on all JavaScript values.
---

Promise assimilation differs from a generic lawful wrapper on all JavaScript values. This unit develops that mechanism using the earlier units as prerequisites.

## Pitfalls and trade-offs

## JavaScript Promises bend the rules

`then` acts as `map` *or* `flat_map` depending on what the callback returns, and Promises flatten automatically: Promise.resolve(p) returns p itself when p is a Promise whose constructor matches the receiver. Standard, unmodified Promises adopt returned Promises/thenables rather than fulfilling with a nested Promise value. That's convenient, but it breaks rule 1 in an edge case: if `x` is itself a Promise (or any object with a `then` method), `Promise.resolve(x).then(f)` unwraps `x` first, so `f` receives something different from what `f(x)` would. That's why purists say Promises are "not quite" monads.

## Java's Optional.map swallows null

If the function passed to `Optional.map` returns `null`, you get an empty `Optional`, not a box containing `null`. Usually helpful, occasionally surprising when `null` was a meaningful result.

## Different boxes don't stack for free

A function returning `Promise<Result<User, Error>>` has two layers of baggage, and `then` only knows about one. You end up unwrapping the inner `Result` by hand in every step. Haskell solves this with **monad transformers**; most other ecosystems settle for a pragmatic convention, such as "Promises reject on error", or libraries like Effect (TypeScript) and ZIO (Scala).

## Don't force it in Python

Python has no `?` operator or do-notation, so a hand-built `Maybe` class often reads worse than early returns. Use the *idea* (one place that handles absence or errors) rather than the class hierarchy. In Python, the idiomatic version is usually exceptions, `None` checks with early `return`, or generators and comprehensions.

## Exceptions versus Result

Exceptions also short-circuit a sequence of steps, so why bother with `Result`? A Result can expose failure in the return type, but handling enforcement varies: Rust warns on unused Results by default rather than universally rejecting them. Exceptions can also be declared, such as Java checked exceptions and Swift throws. Rust, Go-style error returns and Swift's `throws` all sit at different points on that trade-off.

## Key takeaways
- Promise assimilation differs from a generic lawful wrapper on all JavaScript values.
- Nested effects and error enforcement require language-specific handling.

## Further reading
- [Ecma Control](https://tc39.es/ecma262/multipage/control-abstraction-objects.html)
- [Java Optional](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Optional.html)
- [Rust Result](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html)
- [Haskell Transformers](https://hackage.haskell.org/package/transformers/docs/Control-Monad-Trans-Except.html)
- [Java Exception](https://docs.oracle.com/javase/specs/jls/se21/html/jls-11.html)
- [Swift Errors](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/errorhandling/)
