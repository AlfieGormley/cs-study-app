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

A function is a **pure function** if:

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

Copying data on every change sounds expensive. Functional languages use **persistent data structures** that share most of their structure between versions. A map stored as a balanced tree only needs a fresh copy of the nodes on the path from the root to the changed key; every other node is shared with the old version. The path is short:

```formula
copies = O(log_2(n))
log_2(1000000) ≈ 20
where
copies: the number of tree nodes copied to make the new version of the map
n: the number of entries in the map, here 1,000,000
log_2: the base-2 logarithm: how many times you can halve n before reaching 1
O(...): Big-O notation: grows no faster than the expression inside, ignoring constant factors
≈: approximately equal to
In words: changing one key copies a number of nodes that grows with the logarithm of the map's size, not with the size itself.
```

So "copying" a 1-million-element map to change one key copies about 20 nodes of a binary tree, not a million entries: O(log n) rather than O(n). Real persistent maps such as Clojure's branch 32 ways at each node, so the path is only about 4 nodes deep. This assumes the tree stays balanced; a later module covers how.

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
> In Python 3, `map` and `filter` return lazy iterators. Once consumed, they are empty: `sq = map(f, xs); sum(sq); sum(sq)` gives the right total, then `0`. Java streams also can't be reused; implementations may throw `IllegalStateException` when reuse is detected.

## Folds

A **fold** walks a list, combining each element with an **accumulator**. It is the general pattern behind `sum`, `max`, `len` and even `map` itself.

```python
from functools import reduce
digits = [1, 2, 3]
n = reduce(lambda acc, d: acc * 10 + d,
           digits, 0)
# 123
```

Each step applies the same rule to the accumulator:

```formula
acc_new = acc × 10 + d
((0 × 10 + 1) × 10 + 2) × 10 + 3
= (1 × 10 + 2) × 10 + 3 = 123
where
acc: the accumulator: the number built so far, starting from the seed 0
acc_new: the accumulator after the next digit has been added
d: the next digit taken from the list
10: the base of decimal numbers; multiplying by 10 shifts the number one place left to make room for the new digit
In words: shift the number so far one decimal place left, then put the new digit on the end.
```

Haskell distinguishes the direction:

- `foldl f z [a, b, c]` = `f (f (f z a) b) c`: groups from the left.
- `foldr f z [a, b, c]` = `f a (f b (f c z))`: groups from the right.

For a finite list, the two directions give the same mathematical result when the operation is **associative** and the seed is a two-sided **identity element** for it:

```formula
(a ⊕ b) ⊕ c = a ⊕ (b ⊕ c)
z ⊕ a = a ⊕ z = a
where
⊕: the combining operation the fold uses, such as + or −
a: any value the fold combines
b: any value the fold combines
c: any value the fold combines
z: the seed (starting value) passed to the fold
In words: the first line (associativity) says moving the brackets never changes the answer; the second (identity) says combining with the seed changes nothing. With both, folding from the left and from the right agree.
```

Integer addition with seed 0 has both properties. Floating-point addition is not associative, because each step rounds. Subtraction is not associative either, so the direction matters:

```formula
((z − a) − b) − c
((0 − 1) − 2) − 3 = −6
a − (b − (c − z))
1 − (2 − (3 − 0)) = 2
where
z: the seed, here 0
a: the first list element, here 1
b: the second list element, here 2
c: the third list element, here 3
−: subtraction, which is not associative
In words: foldl (first two lines) brackets from the left and gives −6; foldr (last two lines) brackets from the right and gives 2.
```

In Haskell those are `foldl (-) 0 [1,2,3]` and `foldr (-) 0 [1,2,3]`.

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

**Function composition** glues functions end to end. In maths it is written with a small circle:

```formula
(f ∘ g)(x) = f(g(x))
where
∘: composition, read "f after g"
f: the function applied second
g: the function applied first
x: the input value
In words: to run f composed with g, apply g to the input, then apply f to g's result; the right-hand function runs first.
```

For example, if f doubles a number and g adds 1, then (f ∘ g)(3) is f(4), which is 8. Haskell writes the circle as a dot, `(f . g) x = f (g x)`, so `.` also reads right to left:

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
