---
id: fp-referential-rewriting
title: Referential transparency and safe caching
level: basic
minutes: 3
sourceLesson: fp-pure-functions
summary: Replacing a pure call by its value must preserve observable behaviour.
---

Replacing a pure call by its value must preserve observable behaviour. This unit develops that mechanism using the earlier units as prerequisites.

## Referential transparency

A pure function call is **referentially transparent**: you can replace the call with its result without changing what the program does. If `total([2, 3])` is pure, every occurrence of it can be swapped for `5`.

This is what makes pure code easy to reason about. You can read it like algebra, rewriting one expression into an equal one:

```formula
y = f(x) + f(x)
z = f(x)
y = z + z
where
f: a pure function: its result depends only on its argument, and calling it has no side effects
x: any argument value passed to f
y: the value of the whole expression
z: a name for the result of f(x), computed once and then reused
In words: because f is pure, both calls f(x) give the same value, so you can compute it once, call it z, and write y = z + z without changing what the program means.
```

For example, let the function square its argument and choose the input three. Both versions return eighteen; the second calls the function once instead of twice.

If `f` printed something, or incremented a counter, the two lines would behave differently. That one rewrite is the basis of a whole list of practical benefits.

| Benefit | Why purity gives it |
|---|---|
| Testing | Dependencies supplied as inputs; no I/O mocks for the pure core |
| Caching | Same input means same output, so memoise |
| Parallelism | No shared state to race on |
| Refactoring | Calls can be moved, merged or removed |
| Debugging | Reproduce a bug with just the inputs |

Memoisation is the clearest example. `functools.lru_cache` preserves intended behavior when reusing a result is valid: arguments must be hashable, relevant inputs stable, and callers must not require a fresh mutable object. Explicitly managed caches can also tolerate documented staleness for impure I/O. Put it on `greeting()` and it would say "Morning" all day.

> [!note] Compilers love purity too
> GHC (the main Haskell compiler) can eliminate common subexpressions, inline and reuse pure expressions when doing so preserves semantics; divergence, exceptions and space usage still matter. C compilers can also optimize calls when analysis or annotations establish relevant properties.

## Key takeaways
- Replacing a pure call by its value must preserve observable behaviour.
- Memoisation additionally needs stable keys and safe result sharing.

## Further reading
- [Python Functools](https://docs.python.org/3/library/functools.html)
- [Ghc Optim](https://downloads.haskell.org/ghc/latest/docs/users_guide/using-optimisation.html)
