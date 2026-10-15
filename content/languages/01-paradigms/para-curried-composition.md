---
id: para-curried-composition
title: Currying, partial application and composition
level: intermediate
minutes: 3
sourceLesson: para-functional-basics
summary: Currying represents several arguments as nested one-argument functions.
---

Functions can return specialised functions and can be combined into pipelines. Keep track of which argument is supplied now and which operation runs first.

## Currying, partial application and composition

In Haskell, every function takes exactly one argument. A "two-argument" function is really a function that returns a function. This is **currying**, named after Haskell Curry.

```haskell
-- One argument returns another function.
add :: Int -> Int -> Int
add x y = x + y

addTen = add 10   -- Int -> Int
addTen 5          -- 15
```

The type `Int -> Int -> Int` means `Int -> (Int -> Int)`. Supplying only some arguments is **partial application**. Other languages do it explicitly:

```python
# Bind only the first argument.
from functools import partial
add_ten = partial(lambda x, y: x + y, 10)
add_ten(5)   # 15
```

```javascript
// The outer arrow returns the inner one.
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

For a concrete example, let the outer function double its input and the inner function add one:

```formula
f(x) = 2x
g(x) = x + 1
(f ∘ g)(3) = f(4) = 8
where
f: the dimensionless numeric function applied second, which doubles its argument
g: the dimensionless numeric function applied first, which adds one
x: a dimensionless numeric input
∘: function composition; the right-hand function acts first
In words: add one to three to get four, then double four to get eight.
```

Haskell writes the circle as a dot, `(f . g) x = f (g x)`, so `.` also reads right to left:

```haskell
-- Reverse first, then uppercase.
import Data.Char (toUpper)

shout = map toUpper . reverse
shout "abc"   -- "CBA"
```

Writing functions purely as compositions, without naming the argument, is **point-free style**. Used sparingly it is elegant; overused it becomes cryptic.

## Trade-offs and pitfalls

- Performance: immutable updates allocate. Persistent structures and good garbage collectors make this cheap, but tight numeric loops are still often faster with mutation.
- Stack depth: naive recursion in Python or Java overflows on large inputs.
- Readability: long chains of `map`/`filter`/`reduce` with complex lambdas can be harder to follow than a plain loop. Name the intermediate functions.
- Hidden impurity: a "pure-looking" lambda that logs, mutates a captured list or reads a global breaks the guarantees silently.
- Mutating sorts: JavaScript's `arr.sort()` and Python's `list.sort()` mutate in place. Use `toSorted()` (ES2023) or `sorted()` for a new copy.

## Key takeaways
- Currying represents several arguments as nested one-argument functions.
- Composition applies the right-hand function first.

## Further reading
- [Haskell: function expressions](https://www.haskell.org/onlinereport/haskell2010/haskellch3.html)
- [Python: partial application](https://docs.python.org/3/library/functools.html)
