---
id: fp-laziness
title: Laziness
level: intermediate
minutes: 11
summary: Evaluating only what is needed, when it is needed - thunks, infinite structures, generators in Python and JavaScript, Haskell's call-by-need, and the space leaks and surprises laziness brings.
---

Most languages are **strict** (or *eager*): when you call `f(g(x))`, they compute `g(x)` first, then pass the result to `f`. If `f` never uses its argument, the work was wasted.

**Lazy** evaluation flips this. An expression isn't computed when it's written, only when its value is actually needed. If it's never needed, it's never computed.

You already use laziness every day without thinking of it that way:

```python
if user is not None and user.is_admin:
    ...
```

`and` doesn't evaluate `user.is_admin` if `user is not None` is false. That short-circuit is laziness on a small scale. Haskell is non-strict by default, with explicit strictness operations and compiler analysis that can evaluate known-needed work eagerly.

## Thunks: delaying work

A delayed computation is stored as a **thunk**: a small object that remembers *how* to compute a value without having computed it yet. In Python, the simplest thunk is a zero-argument function:

```python
expensive = lambda: slow_query()
# slow_query has not run yet
if need_it:
    result = expensive()
```

Haskell builds thunks automatically. Conceptually, let y = slowSum xs delays that work until demanded; a compiler may eliminate or evaluate the thunk when semantics allow.

### Call-by-need: compute once, share

There are two flavours of non-strict evaluation:

| Strategy | Evaluates argument |
|---|---|
| Call-by-value (strict) | Once, before the call |
| Call-by-name | Every time it's used |
| Call-by-need (lazy) | At most once, on first use |

Call-by-name re-runs the expression on each use, which can be very wasteful. **Call-by-need** evaluates a thunk the first time it's forced, then **overwrites the thunk with its value** so later uses reuse the result instead of repeating that computation. This is what Haskell does, and it's what people usually mean by "lazy".

```haskell
let y = expensive 42
in y + y   -- expensive runs once
```

## Infinite data structures

Laziness lets you define structures that are conceptually infinite, because only the parts you look at are ever built.

```haskell
nats = [1 ..]          -- 1, 2, 3, ...
take 5 nats            -- [1,2,3,4,5]

evens = filter even [1 ..]
take 3 evens           -- [2,4,6]
```

The famous self-referential Fibonacci list:

```haskell
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)
take 8 fibs   -- [0,1,1,2,3,5,8,13]
```

It works because each element only depends on the two before it, which already exist by the time it's demanded:

```
fibs        = 0 : 1 : 1 : 2 : 3 : ...
tail fibs   = 1 : 1 : 2 : 3 : ...
zipWith (+) = 1 : 2 : 3 : 5 : ...
```

### Separating producers from consumers

John Hughes's paper *Why Functional Programming Matters* argued that this is the real power of laziness: you can write a **producer** that generates every candidate, and a separate **consumer** that decides how many to take. Neither needs to know about the other.

```haskell
-- producer: all approximations
approx = iterate improve guess
-- consumer: stop when close enough
answer = within 1e-9 approx
```

Strict languages can also separate producers and consumers using iterators, callbacks or explicit thunks.

## Laziness in Python and JavaScript

Neither language is lazy by default, but both have opt-in laziness through **iterators** and **generators**.

### Python generators

A function containing `yield` returns a generator. Its body runs only as values are requested, pausing at each `yield`:

```python
def naturals():
    n = 1
    while True:      # infinite, but fine
        yield n
        n += 1

from itertools import islice
list(islice(naturals(), 5))
# [1, 2, 3, 4, 5]
```

Generator **expressions** look like list comprehensions with round brackets:

```python
squares = [x * x for x in range(10**6)]
# list: stores a million results now

squares = (x * x for x in range(10**6))
# generator: defers per-item squares
```

Many Python iterators defer per-item work. This does not guarantee bounded memory: itertools.product pools its inputs, cycle caches values, and tee buffers when consumers diverge. A streaming filter/map pipeline can avoid materializing the whole input:

```python
with open("access.log") as f:
    errors = (l for l in f if " 500 " in l)
    ips = (l.split()[0] for l in errors)
    first = list(islice(ips, 10))
```

This avoids storing the whole file and stops requesting lines after 10 matches. Memory still depends on the longest line, I/O buffers and the 10 collected results; the file reader may read ahead internally.

### JavaScript generators and iterators

```javascript
function* naturals() {
  let n = 1;
  while (true) yield n++;
}

function* take(n, it) {
  if (n <= 0) return;
  for (const x of it) {
    yield x;
    if (--n === 0) return;
  }
}

[...take(5, naturals())];  // [1,2,3,4,5]
```

Since ES2025, iterators also have lazy helper methods (`.map`, `.filter`, `.take`, `.drop`) via `Iterator.prototype`, so you don't need to hand-write `take` in modern engines. Array methods, by contrast, are **eager**: `arr.map(f)` builds a whole new array immediately.

### Elsewhere

The same idea shows up across the industry, usually under the name *deferred execution*:

- **Apache Spark**: transformations (`map`, `filter`) build a plan; nothing runs until an action (`count`, `collect`).
- **C# LINQ** and **Java Streams**: queries run when enumerated or when a terminal operation is called.
- **Django ORM**: QuerySets defer evaluation, but iteration is only one trigger; list(), len(), bool(), repr() and some other operations can execute queries.
- **Polars** lazy frames: the whole query is optimised before execution.

Deferring lets the system see the whole pipeline first and optimise it (push filters down, skip unused columns).

## The costs of laziness

Laziness is powerful but it makes **when** things happen harder to predict. That leads to a family of characteristic bugs.

### Space leaks

A thunk holds references to everything it needs. If thunks pile up unevaluated, memory grows even though the eventual value is small.

```haskell
-- may build a long accumulator thunk chain
foldl (+) 0 [1 .. 10^7]
-- forces as it goes
foldl' (+) 0 [1 .. 10^7]
```

The lazy `foldl` accumulates `(((0 + 1) + 2) + 3) ...` as a chain of suspended additions. `foldl'` uses `seq` to force the accumulator at each step.

Note that `seq` only forces to **weak head normal form** (WHNF): the outermost constructor. Forcing a pair `(a, b)` to WHNF does not evaluate `a` or `b`. Use deepseq with an appropriate NFData instance to force the represented data more deeply; it does not execute function bodies or I/O actions merely by forcing their values.

### Effects happen at the wrong time

Laziness and side effects mix badly. This Python function looks fine:

```python
def read_lines(path):
    with open(path) as f:
        return (l.strip() for l in f)

list(read_lines("a.txt"))
# ValueError: I/O operation
#             on closed file.
```

The `with` block closes the file on `return`, but the generator hasn't read anything yet. When it finally runs, the file is gone. Fix: `yield from` inside the `with`, or return a list.

Haskell's lazy `readFile` has a similar trap: the file is read on demand, so the handle can stay open far longer than expected, or reading the same file for output can encounter a still-open handle. This is why Haskell has strict and streaming alternatives (`Data.Text.IO`, conduit, pipes).

### One-shot iterators

Python generators can be consumed only once. A function that iterates its argument twice silently gets nothing the second time if passed a generator. LINQ has the opposite trap: re-enumerating a deferred query **re-runs** it, possibly hitting the database twice.

### Errors and timing move

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
- Lazy evaluation computes a value only when it's needed; a delayed computation is a thunk.
- Call-by-need evaluates each thunk at most once and shares the result; that's Haskell's strategy.
- Laziness enables infinite structures and lets producers and consumers be written independently.
- Python and JavaScript generators and iterators enable streaming; bounded memory additionally requires bounded state, records and buffering.
- The costs are space leaks from piled-up thunks, effects and errors at surprising times, and one-shot iterators.

## Further reading
- [Lazy evaluation — Wikipedia](https://en.wikipedia.org/wiki/Lazy_evaluation)
- [Why Functional Programming Matters — John Hughes](https://www.cse.chalmers.se/~rjmh/Papers/whyfp.html)
- [Generators — Python wiki](https://wiki.python.org/moin/Generators)
- [Iterators and generators — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Iterators_and_generators)
- [Weak head normal form — Haskell Wiki](https://wiki.haskell.org/Weak_head_normal_form)
- [itertools — Python docs](https://docs.python.org/3/library/itertools.html)
- [Primary verification source 2](https://docs.python.org/3/reference/expressions.html#generator-expressions)
- [Primary verification source 3](https://www.haskell.org/onlinereport/haskell2010/haskellch6.html)
- [Primary verification source 4](https://hackage.haskell.org/package/base/docs/Data-List.html)
- [Primary verification source 5](https://docs.djangoproject.com/en/5.2/ref/models/querysets/)
- [Primary verification source 6](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Primary verification source 7](https://tc39.es/ecma262/multipage/control-abstraction-objects.html)
