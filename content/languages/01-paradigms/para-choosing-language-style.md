---
id: para-choosing-language-style
title: Choosing a language and a working style
level: intermediate
minutes: 4
sourceLesson: para-multi-paradigm
summary: Language and style choices depend on the ecosystem, team and workload.
---

Compiler optimisation and runtime support influence which idioms work well. Use those constraints alongside the team, ecosystem and shape of the problem when choosing a language or style.

## JavaScript

JavaScript has had first-class functions and closures since 1995, and `map`, `filter` and `reduce` on arrays since ES5 (2009). Its objects use prototypes, with `class` syntax added in ES2015 as a cleaner way to write the same thing. ES2015 also specified proper tail calls, but in practice JavaScriptCore (used by Safari) implements them, so deep recursion in Chrome or Node still overflows the stack.

## Rust and C++

Here the functional style is often *free*. A chain like `v.iter().map(f).filter(g).sum()` can compile, after suitable optimisation and inlining, to code comparable to a hand-written loop. The result depends on the functions, types, target and compiler options; the abstraction is not a universal performance guarantee. Rust's ownership rules also nudge you away from shared mutable state, the thing that makes OOP code hard to reason about.

## Java

Streams are pleasant but have overhead: pipeline objects and boxing can add overhead, though JIT optimization can remove some allocations and boxed values may be cached or already exist. For hot loops over primitives, use `IntStream` or a plain `for`.

## Choosing a language

The paradigm is rarely the deciding factor. In rough order of importance for most teams:

1. Ecosystem and platform. Swift is a common native iOS choice, though Objective-C and cross-platform approaches also exist. The browser means JavaScript or TypeScript (or something that compiles to it or to WebAssembly). Python is widely used in data science, because that's where NumPy, pandas and PyTorch live.
2. The team. A language five people know well beats a better one nobody knows. Hiring and onboarding count.
3. Runtime needs. Latency, memory and startup time. A garbage collector may be fine for a web service and a problem for a game engine or an embedded device.
4. Correctness needs. Strong static types and exhaustive matching catch whole classes of bug before production. That matters more for a payments ledger than a one-off script.
5. Problem shape. Rules and queries suggest SQL or Datalog. Tree transformations suggest an ML-family language. Highly concurrent servers suggest Go, Erlang/Elixir or Rust.

Most real systems use several languages: SQL for queries, a general-purpose language for services, a shell for glue, a configuration language for infrastructure. Choosing a language is often choosing which part of the system gets which one.

## Choosing a style within a language

Inside one codebase, a few rules of thumb help:

- Data transformations: pipelines, comprehensions or iterator chains.
- Long-lived things with state and identity (a connection pool, a game entity): objects with encapsulated state.
- A closed set of variants (AST nodes, message types, results): sealed types or enums with pattern matching.
- An open set of implementations (storage back ends, payment providers): interfaces, traits or protocols.
- Effects: at the edges, so the middle stays pure and testable.

## Pitfalls

- Style soup. One module uses classes, the next uses closures and dictionaries, the next uses inheritance six levels deep. Pick conventions per layer and write them down.
- Clever over clear. A three-line loop is often more readable than a nested `reduce` with a lambda. Use the declarative form when it states the intent better, not to show off.
- Importing idioms that don't fit. Monad libraries in Python, or faking class inheritance in Rust by abusing `Deref`, usually fight the language.
- Choosing for the paradigm. Rewriting a working system in a "better paradigm" language rarely pays for itself. The ecosystem, team and runtime usually matter more.

## Key takeaways
- Language and style choices depend on the ecosystem, team and workload.
- Optimisation claims need the actual compiler and workload assumptions.

## Further reading
- [Rust: loops versus iterators](https://doc.rust-lang.org/book/ch13-04-performance.html)
- [WebKit: proper tail calls](https://webkit.org/blog/6240/ecmascript-6-proper-tail-calls-in-webkit/)
