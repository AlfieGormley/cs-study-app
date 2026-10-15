---
id: dp-fibonacci-call-tree
title: Why naive Fibonacci repeats work
level: basic
minutes: 5
summary: Base cases stop the recurrence at zero and one.
sourceLesson: dp-intro
---

## Fibonacci: the classic example

The Fibonacci numbers start 0, 1, 1, 2, 3, 5, 8, 13, ...: each one after the first two is the sum of the two before it. Written as a **recurrence** (a rule that defines each value from earlier values of the same sequence):

```formula
F(0) = 0
F(1) = 1
F(n) = F(n − 1) + F(n − 2)   for n ≥ 2
where
F(n): the nth Fibonacci number, counting from F(0) = 0
n: the position in the sequence, a whole number 0, 1, 2, ...
F(n − 1), F(n − 2): the two Fibonacci numbers just before position n
≥: greater than or equal to
In words: the first two values are 0 and 1; every later value is the sum of the previous two.
```

Substituting the preceding values gives:

```formula
F(2) = 1 + 0 = 1
F(3) = 1 + 1 = 2
F(4) = 2 + 1 = 3
F(5) = 3 + 2 = 5
where
F(k): the Fibonacci number at whole-number position k, with values zero and one at positions zero and one
k: a nonnegative whole-number position
In words: Build each value from the preceding two, giving five at position five.
```

 The first two lines are the **base cases**: without them the rule would never stop asking for smaller values. The definition translates directly into code:

```python
def fib(n):
    # Reject values outside the recurrence.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    # The first two positions are base
    # cases.
    if n < 2:
        return n
    # Both smaller answers contribute.
    return fib(n - 1) + fib(n - 2)
```

For nonnegative integer n it is correct, but becomes expensive as n grows. Look at the call tree for `fib(5)`:

```
              fib(5)
           /         \
       fib(4)        fib(3)
       /    \        /    \
   fib(3) fib(2)  fib(2) fib(1)
   /   \   / \     / \
 f(2) f(1) ...    ...
```

`fib(3)` is computed twice, `fib(2)` three times, `fib(1)` five times. These are the overlapping subproblems.

How many calls does `fib(n)` make in total? Each call makes one call for itself plus all the calls of its two children, and the total turns out to be tied to the Fibonacci numbers themselves:

```formula
calls(n) = 1 + calls(n − 1) + calls(n − 2)
calls(n) = 2F(n + 1) − 1
calls(5) = 2F(6) − 1 = 2 × 8 − 1 = 15
where
calls(n): the total number of calls made by the naive fib(n), including the first one
n: the nonnegative Fibonacci position asked for; the recursive line applies only from position two onwards
F(n + 1): the Fibonacci number at position n + 1 (F(6) = 8)
In words: one call for the current value, plus every call made while computing the two smaller values; this works out to twice the next Fibonacci number, minus one.
```

The closed form has the same two base values and the same recurrence:

```formula
calls(0) = calls(1) = 1
2F(1) − 1 = 2F(2) − 1 = 1
where
calls(k): the total naive function calls for Fibonacci position k
F(k): the Fibonacci number at position k
k: a nonnegative whole-number position
In words: Each base call counts once; twice the next Fibonacci value minus one also gives one. The recursive rule then preserves the identity.
```

For `fib(30)` it is 2,692,537 calls; for `fib(40)` it is about 331 million.

The Fibonacci numbers themselves grow by a factor of about 1.618 at each step, so the call count does too:

```formula
calls(n) ≈ cφ^n
φ = (1 + √(5)) / 2 ≈ 1.618
where
calls(n): the number of calls made by the naive fib(n); the approximation describes growth for large n
c: a constant that does not depend on n (about 1.45 here, which is 2 × φ / √5)
φ: phi, the golden ratio, about 1.618
φ^n: n copies of φ multiplied together
n: the Fibonacci position asked for
√(5): the square root of 5, about 2.236
≈: approximately equal to
In words: each step up in n multiplies the work by about 1.6, so adding 10 to n multiplies it by about 120.
```

The exact call counts at positions thirty and forty agree closely with the golden-ratio estimate:

```formula
R = 331,160,281 / 2,692,537
R ≈ 123
φ^10 ≈ 123
where
R: the ratio of the naive call counts at positions forty and thirty
φ: the golden ratio, about 1.618
≈: approximately equal after rounding
In words: Ten extra positions multiply the work by about 123.
```

This is **exponential** growth even though the distinct subproblems are just the positions from zero through the requested position.

## Key takeaways
- Base cases stop the recurrence at zero and one.
- The naive call tree repeats states and grows exponentially.

## Further reading
- [Python caching](https://docs.python.org/3/library/functools.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
