---
id: fp-lazy-resource-costs
title: Lazy resources, forcing and repeated use
level: intermediate
minutes: 4
sourceLesson: fp-laziness
summary: Keep a lazy producer resource alive during consumption.
---

Keep a lazy producer resource alive during consumption. This unit develops that mechanism using the earlier units as prerequisites.

## The costs of laziness

Laziness is powerful but it makes when things happen harder to predict. That leads to a family of characteristic bugs.

## Space leaks

A thunk holds references to everything it needs. If thunks pile up unevaluated, memory grows even though the eventual value is small.

```haskell
-- Strictness controls accumulator
-- retention.
-- may build a long accumulator thunk chain
foldl (+) 0 [1 .. 10^7]
-- forces as it goes
foldl' (+) 0 [1 .. 10^7]
```

The lazy `foldl` accumulates `(((0 + 1) + 2) + 3) ...` as a chain of suspended additions. `foldl'` uses `seq` to force the accumulator at each step.

Note that `seq` only forces to **weak head normal form** (WHNF): the outermost constructor or function value. This is shallow forcing; newtype wrappers have special semantics and do not create an ordinary data-constructor layer. Forcing a pair `(a, b)` to WHNF does not evaluate `a` or `b`. Use deepseq with an appropriate NFData instance to force the represented data more deeply; it does not execute function bodies or I/O actions merely by forcing their values.

## Effects happen at the wrong time

Laziness and side effects mix badly. This Python function looks fine:

```python
# Returning exits and closes the file.
def read_lines(path):
    with open(path) as f:
        return (l.strip() for l in f)

list(read_lines("a.txt"))
# ValueError: I/O operation
#             on closed file.
```

The `with` block closes the file on `return`, but the generator hasn't read anything yet. When it finally runs, the file is gone. Fix: `yield from` inside the `with`, or return a list.

Haskell's lazy `readFile` has a similar trap: the file is read on demand, so the handle can stay open far longer than expected, or reading the same file for output can encounter a still-open handle. This is why Haskell has strict and streaming alternatives (`Data.Text.IO`, and the conduit and pipes libraries).

## One-shot iterators

Python generators can be consumed only once. A function that iterates its argument twice silently gets nothing the second time if passed a generator. LINQ has the opposite trap: re-enumerating a deferred query re-runs it, possibly hitting the database twice.

## Errors and timing move

An exception inside a lazy expression surfaces wherever the value is first forced, which may be far from where the expression was written. Likewise, performance profiles are harder to read: cost shows up at the consumer, not the producer.

## When to choose laziness

| Use laziness for | Prefer strictness for |
|---|---|
| Large or infinite streams | Small, fixed data |
| Early-exit searches | Accumulators and counters |
| Pipelines over files/APIs | Code with side effects |
| Expensive optional values | Predictable latency |

Most modern languages land on **strict by default, lazy on request**: Python generators, JavaScript iterators, Scala `LazyList` and `lazy val`, Kotlin `Sequence` and `by lazy`, Rust iterators. Haskell is the notable exception, lazy by default with strictness on request (`seq`, bang patterns, the `Strict` extension).

## Key takeaways
- Keep a lazy producer resource alive during consumption.
- WHNF forcing is shallow and one-shot iterators cannot be replayed.

## Further reading
- [Haskell List](https://hackage.haskell.org/package/base/docs/Data-List.html)
- [Haskell Deepseq](https://hackage.haskell.org/package/deepseq/docs/Control-DeepSeq.html)
- [Python Expressions](https://docs.python.org/3/reference/expressions.html)
- [Haskell Io](https://hackage.haskell.org/package/base/docs/System-IO.html)
- [Haskell Text](https://hackage.haskell.org/package/text/docs/Data-Text-IO.html)
- [Ghc Strict](https://downloads.haskell.org/ghc/latest/docs/users_guide/exts/strict.html)
