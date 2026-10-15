---
id: para-functions-and-pipelines
title: Functions as values and lazy iterators
level: intermediate
minutes: 3
sourceLesson: para-functional-basics
summary: Higher-order functions accept or return functions.
---

Functions can be passed around just like other values. Each pipeline below assumes the finite integer input `nums` is `[3, 4, 7, 10, 1]`; the Java version uses a `List<Integer>`, and all four pipelines produce the numeric total 116.

## Functions as values

In FP, functions are **first-class functions**: you can store them in variables, pass them as arguments and return them from other functions. A function that takes or returns a function is a **higher-order function**.

The three workhorses replace most loops:

- `map f xs`: apply `f` to every element.
- `filter p xs`: keep elements where `p` is true.
- `reduce` / **fold**: combine all elements into one value.

The same pipeline, *sum the squares of the even numbers*, in four languages:

```haskell
-- Composition runs from right to left.
-- Haskell
total = sum
      . map (^2)
      . filter even
      $ nums
```

```python
# map/filter defer work until consumption.
# Python
total = sum(map(lambda n: n * n,
            filter(lambda n: n % 2 == 0,
                   nums)))
```

```javascript
// Each stage passes values to the next.
// JavaScript
const total = nums
  .filter(n => n % 2 === 0)
  .map(n => n * n)
  .reduce((a, b) => a + b, 0);
```

```java
// Primitive stream avoids boxed squares.
// Java (streams)
int total = nums.stream()
    .filter(n -> n % 2 == 0)
    .mapToInt(n -> n * n)
    .sum();
```

In Python, a comprehension (`sum(n * n for n in nums if n % 2 == 0)`) is usually considered more idiomatic than `map` and `filter` with lambdas.

> [!warning] Python's `map` is a one-shot iterator
> In Python 3, `map` and `filter` return lazy iterators. Once consumed, they are empty: `sq = map(f, xs); sum(sq); sum(sq)` gives the right total, then `0`. Java streams also can't be reused; implementations may throw `IllegalStateException` when reuse is detected.

## Key takeaways
- Higher-order functions accept or return functions.
- Python map/filter iterators are consumed once.

## Further reading
- [Python: functional programming](https://docs.python.org/3.12/howto/functional.html)
- [Haskell: standard Prelude definitions](https://www.haskell.org/onlinereport/haskell2010/haskellch9.html)
