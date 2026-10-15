---
id: para-pure-functions
title: Pure functions and observable effects
level: intermediate
minutes: 3
sourceLesson: para-functional-basics
summary: Purity requires explicit inputs and no observable external mutation.
---

Functional programming (FP) emphasises constructing programs from functions and their composition. Pure functional programming uses functions in the mathematical sense: for the same inputs, a terminating call returns the same value without observable side effects. Functional languages and functional style can also include explicit effects or mutation. Programs are made by combining small functions into bigger ones, rather than by sequencing commands that change state.

Its roots are in Alonzo Church's **lambda calculus** (1930s), a model of computation with nothing but function definition and application. **Lisp** (1958) brought those ideas to real computers, followed by ML, Erlang, **Haskell** (1990), Scala, Clojure, F# and Elixir. FP ideas also appear in many mainstream languages: lambdas in Java 8, `map`/`filter` in JavaScript, comprehensions in Python, and React's push for immutable state.

This lesson covers the basics. The functional programming module later goes deeper into laziness, monads and persistent data structures.

## Pure functions

A function is a **pure function** if:

1. Its result depends only on its arguments.
2. It has no **side effects**: no mutating variables outside itself, no I/O, no exceptions that depend on hidden state, no reading the clock.

```python
# Compare hidden state with explicit input.
# Impure: depends on and changes
# outside state
count = 0
def tick():
    global count
    count += 1
    return count

# Pure: output depends only on input
def add(a, b):
    return a + b
```

In a value-oriented model with immutable inputs/results and no observable identity or timing effects, pure calls support **referential transparency**: any call can be replaced by its result without changing the program. If `add(2, 3)` appears anywhere, you can write `5` instead. You cannot do that with `tick()`, because the first call gives 1 and the second gives 2.

Why that matters:

- Reasoning: you understand a pure function by reading it alone. No hidden state, no "it depends what ran before".
- Testing: no mocks or setup; call it and check the output.
- Caching: results can be **memoised** when keys represent all inputs and cached values are safe to share; Python `functools.cache` requires hashable arguments and returns the same cached result object.
- **Concurrency**: two threads calling pure functions can't race, because nothing is shared and mutated.
- Optimisation: compilers can sometimes reorder, merge or skip pure calls when the transformation also preserves termination, exceptions and other observable semantics.

Real programs must do I/O, of course. The usual approach is **functional core, imperative shell**: keep the business logic pure and push side effects (database, network, clock) to a thin outer layer that calls into it.

## Key takeaways
- Purity requires explicit inputs and no observable external mutation.
- Cache keys and result sharing must preserve the intended value semantics.

## Further reading
- [Python: functional programming](https://docs.python.org/3.12/howto/functional.html)
- [Functional Core, Imperative Shell](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
