---
id: fp-callback-pitfalls
title: Iterator and callback pitfalls
level: basic
minutes: 3
sourceLesson: fp-higher-order
summary: One-shot iterators, callback arity and captured bindings can surprise callers.
---

One-shot iterators, callback arity and captured bindings can surprise callers. This unit develops that mechanism using the earlier units as prerequisites.

## Gotchas

## Python's map and filter are lazy

In Python 3, `map` and `filter` return **iterators**, not lists. They defer per-item mapping/filtering until consumed and are one-shot; construction still evaluates arguments and obtains iterators.

```python
# Materialisation advances the iterator.
m = map(lambda x: x * 2, [1, 2, 3])
list(m)   # [2, 4, 6]
list(m)   # []  already exhausted
```

## JavaScript's map passes three arguments

`Array.prototype.map` calls the callback with `(element, index, array)`. Functions with optional second parameters misbehave:

```javascript
// map also supplies the index as radix.
["1", "2", "3"].map(parseInt);
// [1, NaN, NaN]
```

`parseInt("2", 1)` treats 1 as the radix, which is invalid, giving `NaN`. `parseInt("3", 2)` fails because 3 isn't a binary digit. Write `.map(s => parseInt(s, 10))` or `.map(Number)`.

## reduce on an empty array

With no initial value, JavaScript's `reduce` uses the first element as the accumulator. On an empty array that throws `TypeError: Reduce of empty array with no initial value`. Python's `functools.reduce` raises a `TypeError` too. Always pass an initial value.

## Late-binding closures

Python closures capture **bindings**, not values:

```python
# The lambdas read i when called.
fs = [lambda: i for i in range(3)]
[f() for f in fs]   # [2, 2, 2]
```

All three lambdas share one `i`, which is 2 by the time they run. Bind the value at definition time with a default argument: `lambda i=i: i`. JavaScript's `let` in a `for` loop creates a fresh binding per iteration, so the equivalent JS gives `[0, 1, 2]`; with `var` it gives `[3, 3, 3]`.

## Trade-offs

- Readability. Short pipelines of `map`/`filter` are clearer than loops. Deeply nested `reduce` calls with clever accumulators are usually worse. If you need a comment to explain the fold, write a loop.
- Performance. In JavaScript, `xs.filter(...).map(...)` builds an intermediate array per step. Whether allocation matters depends on the workload; a single loop or lazy pipeline can avoid intermediate arrays. Haskell's GHC can often *fuse* such pipelines into one loop (**loop fusion**).
- **Early exit.** Fully consumed finite eager maps and strict folds normally process all eligible elements; Python map can be partially consumed and lazy Haskell folds can short-circuit. Use `any`/`all` (Python), `some`/`every`/`find` (JS) when you can stop early.

## Key takeaways
- One-shot iterators, callback arity and captured bindings can surprise callers.
- Preserve evaluation order, empty-input handling and callback semantics when refactoring.

## Further reading
- [Python Faq](https://docs.python.org/3/faq/programming.html)
- [Python Functions](https://docs.python.org/3/library/functions.html)
- [ECMAScript: indexed collections](https://tc39.es/ecma262/multipage/indexed-collections.html)
- [Ecma Numbers](https://tc39.es/ecma262/multipage/numbers-and-dates.html)
- [Ghc Optim](https://downloads.haskell.org/ghc/latest/docs/users_guide/using-optimisation.html)
