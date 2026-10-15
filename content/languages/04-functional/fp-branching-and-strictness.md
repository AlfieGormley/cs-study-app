---
id: fp-branching-and-strictness
title: Branching recursion and lazy accumulators
level: intermediate
minutes: 4
sourceLesson: fp-recursion-tail-calls
summary: Naive Fibonacci repeats subproblems exponentially.
---

Naive Fibonacci repeats subproblems exponentially. This unit develops that mechanism using the earlier units as prerequisites.

## Recursion that branches

Some recursion calls itself more than once. Naive Fibonacci is the classic warning:

```python
# The two branches repeat subproblems.
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

Each non-base invocation makes two recursive calls; the branches stop at different depths:

```
            fib(4)
          /        \
      fib(3)       fib(2)
     /     \       /    \
  fib(2) fib(1) fib(1) fib(0)
  /   \
fib(1) fib(0)
```

`fib(2)` is computed twice, `fib(1)` three times. Counting the calls gives a recurrence (a formula defined in terms of itself) with a known closed form. The exponential approximation describes growth for large arguments rather than an exact equality at the small base cases:

```formula
C(0) = C(1) = 1
C(n) = 1 + C(n − 1) + C(n − 2) for n ≥ 2
C(n) = 2F(n + 1) − 1
C(n) ≈ 1.45φ^n
C(30) = 2 × 1346269 − 1 = 2692537
where
C(n): the total number of calls made to evaluate fib(n), counting the first call
n: the argument passed to fib, a whole number
F(n): the n-th Fibonacci number: F(0) = 0, F(1) = 1, and each later one is the sum of the two before it (F(31) = 1,346,269)
φ: phi, the golden ratio, (1 + √5) / 2 ≈ 1.618; consecutive Fibonacci numbers grow by about this factor
φ^n: n copies of φ multiplied together
√: square root
1.45: the constant 2 × φ / √5 ≈ 1.447, which comes from Binet's closed-form formula for Fibonacci numbers
≈: approximately equal to
In words: each call costs one call plus the calls of its two children, so the count itself grows like the Fibonacci numbers: about 1.6 times more calls for each step up in n.
```

So `fib(30)` makes about 2.7 million calls, and `fib(31)` about 1.6 times as many. Stack depth is only O(n), but time is exponential.

Two fixes:

- **Memoisation**: cache results (`@functools.cache`), so each body computes a distinct fib(k) once: O(n) additions and cached entries in a unit-cost arithmetic model.
- **Accumulators**: a loop carries two Fibonacci values with O(n) additions and O(1) numeric variables. Exact integers grow with n, so bit costs are larger; tail recursion also needs TCO for constant call space.

```python
# Carry consecutive Fibonacci values.
def fib(n, a=0, b=1):
    if n == 0:
        return a
    return fib(n - 1, b, a + b)
```

## Haskell's twist: laziness and space leaks

In a lazy language, the accumulator can betray you. This sum looks tail-recursive:

```haskell
-- Lazy acc can retain deferred additions.
mySum acc []     = acc
mySum acc (x:xs) = mySum (acc + x) xs
```

But Haskell doesn't evaluate `acc + x` until something needs it. The accumulator becomes a growing chain of unevaluated additions (**thunks**): `((0 + 1) + 2) + 3 ...`. Evaluating that chain at the end can itself overflow the stack.

The fix is to force the accumulator at each step: `foldl'` from `Data.List`, a bang pattern (`!acc`), or `seq`. For strict finite folds such as numeric sums, foldl' is commonly the appropriate choice; lazy foldl still has uses and WHNF forcing is not deep evaluation. The next lesson covers laziness in depth.

## Key takeaways
- Naive Fibonacci repeats subproblems exponentially.
- Laziness can retain an accumulator thunk chain even in tail-recursive code.

## Further reading
- [Sicp](https://sicp.sourceacademy.org/chapters/1.2.2.html)
- [Haskell List](https://hackage.haskell.org/package/base/docs/Data-List.html)
- [Python Functools](https://docs.python.org/3/library/functools.html)
