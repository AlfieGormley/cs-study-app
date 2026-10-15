---
id: fp-fold-accumulators
title: Folds, accumulators and pipelines
level: basic
minutes: 4
sourceLesson: fp-higher-order
summary: A fold carries one running accumulator through the input.
---

A fold carries one running accumulator through the input. This unit develops that mechanism using the earlier units as prerequisites.

## reduce (fold): combine into one value

`reduce(f, xs, init)` walks the list carrying an **accumulator**: a running value that is updated at each step. The result can be anything: a number, a string, a dict, even another list.

```formula
acc_0 = init
acc_k = f(acc_{k−1}, x_k)   for 1 ≤ k ≤ n
reduce(f, xs, init) = acc_n
where
reduce: the higher-order function that folds a list into one value (also called fold)
f: the combining function: takes the accumulator so far and the next element, returns the new accumulator
xs: the input list, with elements x_1 to x_n
x_k: the k-th element of the list
init: the initial value of the accumulator
acc_0: the accumulator before any element is processed
acc_k: the accumulator after the first k elements
acc_{k−1}: the accumulator after the previous element
acc_n: the final accumulator, which reduce returns
k: the step number, counting from 1
n: the number of elements in xs
≤: less than or equal to
In words: start with init, then fold each element into the running value with f, from left to right; whatever is left at the end is the answer.
```

Summing [1, 2, 3, 4] from 0 with an addition function add:

```formula
acc_0 = 0
acc_1 = add(0, 1) = 1
acc_2 = add(1, 2) = 3
acc_3 = add(3, 3) = 6
acc_4 = add(6, 4) = 10
where
add: the two-argument addition function: add(a, b) returns a + b
acc_0, acc_1, acc_2, acc_3, acc_4: the accumulator after 0, 1, 2, 3 and 4 elements
In words: reduce(add, [1, 2, 3, 4], 0) adds the elements one at a time to a running total and returns 10.
```

`map` and `filter` are both special cases of `reduce`: you can write either as a fold that builds a list. That makes `reduce` the most general and also the hardest to read, so reach for it last.

## In three languages

```python
# Each stage explicitly consumes its input.
from functools import reduce
xs = [1, 2, 3, 4, 5]

evens = list(filter(lambda x: x % 2 == 0,
                    xs))
squares = list(map(lambda x: x * x, xs))
total = reduce(lambda a, x: a + x, xs, 0)
```

```javascript
// Each method builds or folds a new array.
const xs = [1, 2, 3, 4, 5];
const evens = xs.filter(x => x % 2 === 0);
const squares = xs.map(x => x * x);
const total = xs.reduce((a, x) => a + x, 0);
```

```haskell
-- The fold carries its seed through xs.
xs = [1 .. 5]
evens   = filter even xs
squares = map (\x -> x * x) xs
total   = foldl (+) 0 xs
```

Chained together they read as a pipeline: "the sum of the squares of the even numbers".

```javascript
// Filter, square, then accumulate.
xs.filter(x => x % 2 === 0)
  .map(x => x * x)
  .reduce((a, x) => a + x, 0);   // 20
```

> [!tip] Pythonic style
> In Python, list comprehensions are usually preferred over `map` and `filter` with a lambda. `[x * x for x in xs if x % 2 == 0]` does both in one readable line. `map` is still neat with a named function: `map(str.upper, words)`. Guido van Rossum moved `reduce` into `functools` in Python 3 because explicit loops are usually clearer.

## Key takeaways
- A fold carries one running accumulator through the input.
- Seed values make empty-input behaviour explicit.

## Further reading
- [Python Functools](https://docs.python.org/3/library/functools.html)
- [ECMAScript: indexed collections](https://tc39.es/ecma262/multipage/indexed-collections.html)
- [Haskell List](https://hackage.haskell.org/package/base/docs/Data-List.html)
