---
id: para-functional-basics
title: Functional programming basics
level: intermediate
minutes: 12
summary: Pure functions, immutability, higher-order functions, folds, currying and composition, with the same ideas in Haskell, Python, JavaScript and Java.
---

**Functional programming (FP)** builds programs out of **functions** in the mathematical sense: given the same input, a function always returns the same output and does nothing else. Programs are made by combining small functions into bigger ones, rather than by sequencing commands that change state.

Its roots are in Alonzo Church's **lambda calculus** (1930s), a model of computation with nothing but function definition and application. **Lisp** (1958) brought those ideas to real computers, followed by ML, Erlang, **Haskell** (1990), Scala, Clojure, F# and Elixir. FP ideas also appear in many mainstream languages: lambdas in Java 8, `map`/`filter` in JavaScript, comprehensions in Python, and React's push for immutable state.

This lesson covers the basics. The functional programming module later goes deeper into laziness, monads and persistent data structures.

## Pure functions

A function is **pure** if:

1. Its result depends only on its arguments.
2. It has no **side effects**: no mutating variables outside itself, no I/O, no exceptions that depend on hidden state, no reading the clock.

```python
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

- **Reasoning**: you understand a pure function by reading it alone. No hidden state, no "it depends what ran before".
- **Testing**: no mocks or setup; call it and check the output.
- **Caching**: results can be **memoised** when keys represent all inputs and cached values are safe to share; Python `functools.cache` requires hashable arguments and returns the same cached result object.
- **Concurrency**: two threads calling pure functions can't race, because nothing is shared and mutated.
- **Optimisation**: compilers can reorder, merge or skip pure calls.

Real programs must do I/O, of course. The usual approach is **functional core, imperative shell**: keep the business logic pure and push side effects (database, network, clock) to a thin outer layer that calls into it.

## Immutability

In FP, data is **immutable**: instead of changing a value, you create a new one.

```python
# Mutating
cart.append(item)

# Immutable style
new_cart = cart + [item]
```

Immutability removes a whole class of bugs: no function can change your data behind your back, and no other thread can observe a half-updated object.

Languages give you different tools, and some are weaker than they look:

| Language | Tool | Catch |
|---|---|---|
| Python | `tuple`, `frozenset` | Contents may be mutable |
| JavaScript | `const` | Binding only |
| JavaScript | `Object.freeze` | Shallow |
| Java | `record`, `List.of` | Elements may be mutable |
| Haskell | Ordinary pure values | Mutable references/arrays exist inside controlled IO/ST effects |

> [!warning] `const` is not immutability
> In JavaScript, `const xs = [1, 2]` stops you rebinding `xs`, but `xs.push(3)` works fine. `const` freezes the **name**, not the **value**. Likewise `Object.freeze` freezes only the top level of an object.

Copying data on every change sounds expensive. Functional languages use **persistent data structures** that share most of their structure between versions, so "copying" a 1-million-element map to change one key costs roughly O(log n), not O(n). A later module covers how.

## Functions as values

In FP, functions are **first-class**: you can store them in variables, pass them as arguments and return them from other functions. A function that takes or returns a function is a **higher-order function**.

The three workhorses replace most loops:

- `map f xs`: apply `f` to every element.
- `filter p xs`: keep elements where `p` is true.
- `reduce` / **fold**: combine all elements into one value.

The same pipeline, *sum the squares of the even numbers*, in four languages:

```haskell
-- Haskell
total = sum
      . map (^2)
      . filter even
      $ nums
```

```python
# Python
total = sum(map(lambda n: n * n,
            filter(lambda n: n % 2 == 0,
                   nums)))
```

```javascript
// JavaScript
const total = nums
  .filter(n => n % 2 === 0)
  .map(n => n * n)
  .reduce((a, b) => a + b, 0);
```

```java
// Java (streams)
int total = nums.stream()
    .filter(n -> n % 2 == 0)
    .mapToInt(n -> n * n)
    .sum();
```

In Python, a comprehension (`sum(n * n for n in nums if n % 2 == 0)`) is usually considered more idiomatic than `map` and `filter` with lambdas.

> [!warning] Python's `map` is a one-shot iterator
> In Python 3, `map` and `filter` return lazy iterators. Once consumed, they are empty: `sq = map(f, xs); sum(sq); sum(sq)` gives the right total, then `0`. Java streams also must not be reused; implementations may throw `IllegalStateException` when reuse is detected.

## Folds

A **fold** walks a list, combining each element with an **accumulator**. It is the general pattern behind `sum`, `max`, `len` and even `map` itself.

```python
from functools import reduce
digits = [1, 2, 3]
n = reduce(lambda acc, d: acc * 10 + d,
           digits, 0)
# ((0*10+1)*10+2)*10+3 = 123
```

Haskell distinguishes the direction:

- `foldl f z [a, b, c]` = `f (f (f z a) b) c`: groups from the left.
- `foldr f z [a, b, c]` = `f a (f b (f c z))`: groups from the right.

For a finite list, an associative operation with a two-sided identity seed gives the same mathematical result. Integer addition with zero is an example; floating-point addition is not associative. For others they do not: `foldl (-) 0 [1,2,3]` is `((0-1)-2)-3 = -6`, but `foldr (-) 0 [1,2,3]` is `1-(2-(3-0)) = 2`.

## Recursion instead of loops

Pure functional code avoids mutable loop counters, so repetition is expressed by **recursion**, often with **pattern matching** on the shape of the data:

```haskell
len :: [a] -> Int
len []     = 0
len (_:xs) = 1 + len xs
```

Read it as two equations: the length of an empty list is 0; the length of a list with a head and a tail `xs` is one more than the length of `xs`.

Deep recursion needs care. Each call normally uses a stack frame. Many functional-language implementations support **tail-call optimisation (TCO)**: when the recursive call is the very last thing a function does, the frame is reused, so the tail-call stack can stay bounded. This does not guarantee constant total memory: lazy accumulators, retained data or allocation can still grow. Mainstream languages differ:

- **Python** does not do TCO, by design, and has a default recursion limit of 1,000 frames (`sys.getrecursionlimit()`). Recursing over a 10,000-element list raises `RecursionError`.
- **JavaScript**: ES2015 specified proper tail calls, but in practice JavaScriptCore (used by Safari) implements them; V8 (Chrome, Node) does not.
- **Java**: the JVM does not eliminate tail calls; Scala and Kotlin offer `@tailrec` / `tailrec` for self-recursion, compiled into loops.

In practice, use `map`, `filter` and folds where you can; they express intent, but their space behavior still depends on language, implementation and strictness.

## Currying, partial application and composition

In Haskell, every function takes exactly one argument. A "two-argument" function is really a function that returns a function. This is **currying**, named after Haskell Curry.

```haskell
add :: Int -> Int -> Int
add x y = x + y

addTen = add 10   -- Int -> Int
addTen 5          -- 15
```

The type `Int -> Int -> Int` means `Int -> (Int -> Int)`. Supplying only some arguments is **partial application**. Other languages do it explicitly:

```python
from functools import partial
add_ten = partial(lambda x, y: x + y, 10)
add_ten(5)   # 15
```

```javascript
const add = x => y => x + y;
add(10)(5);  // 15
```

**Composition** glues functions end to end. In Haskell, `(f . g) x = f (g x)`, so `.` reads right to left:

```haskell
import Data.Char (toUpper)

shout = map toUpper . reverse
shout "abc"   -- "CBA"
```

Writing functions purely as compositions, without naming the argument, is **point-free style**. Used sparingly it is elegant; overused it becomes cryptic.

> [!note] Evidence gap
> No universal cache-lookup latency or cross-engine tail-call support matrix is supplied: this review did not establish measurements or an exhaustive current engine survey. Check the target runtime and benchmark the actual workload.

## Trade-offs and pitfalls

- **Performance**: immutable updates allocate. Persistent structures and good garbage collectors make this cheap, but tight numeric loops are still often faster with mutation.
- **Stack depth**: naive recursion in Python or Java overflows on large inputs.
- **Readability**: long chains of `map`/`filter`/`reduce` with complex lambdas can be harder to follow than a plain loop. Name the intermediate functions.
- **Hidden impurity**: a "pure-looking" lambda that logs, mutates a captured list or reads a global breaks the guarantees silently.
- **Mutating sorts**: JavaScript's `arr.sort()` and Python's `list.sort()` mutate in place. Use `toSorted()` (ES2023) or `sorted()` for a new copy.

## Key takeaways
- A pure function's output depends only on its inputs and it has no side effects; that gives referential transparency.
- Purity makes code easier to test, cache, parallelise and optimise. Keep side effects in a thin imperative shell.
- Immutable data is never changed in place; JavaScript `const` and shallow freezing are weaker than they look.
- Higher-order functions (`map`, `filter`, folds) replace most loops; `foldl` and `foldr` differ for non-associative operations.
- Recursion replaces loops in pure languages; tail calls run in constant space only where the implementation optimises them (not in Python, V8 or the JVM).
- Currying and composition let you build functions out of other functions.

## Further reading
- [Functional programming — Wikipedia](https://en.wikipedia.org/wiki/Functional_programming)
- [Functional Programming HOWTO — Python docs](https://docs.python.org/3/howto/functional.html)
- [Higher-order function — Wikipedia](https://en.wikipedia.org/wiki/Higher-order_function)
- [Referential transparency — Wikipedia](https://en.wikipedia.org/wiki/Referential_transparency)
- [Object.freeze() — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze)
- [Functional Core, Imperative Shell — Destroy All Software](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
