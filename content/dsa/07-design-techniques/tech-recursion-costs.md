---
id: tech-recursion-costs
title: Repeated calls and hidden slice costs
level: basic
minutes: 3
sourceLesson: tech-recursion
summary: A recursion tree counts repeated work, not just distinct arguments.
---

## The cost of recursion: recursion trees

When a function makes more than one recursive call, draw the **recursion tree** to estimate its cost. Each non-base invocation of naive Fibonacci makes two recursive calls:

```python
def fib(n):
    # Reject inputs outside the stated
    # domain.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n < 2:
        return n
    # The two branches repeat smaller
    # arguments.
    return fib(n - 1) + fib(n - 2)
```

```
            fib(4)
          /        \
      fib(3)       fib(2)
      /    \       /    \
  fib(2) fib(1) fib(1) fib(0)
  /    \
fib(1) fib(0)
```

`fib(4)` makes 9 calls, `fib(5)` 15, `fib(30)` over 2.6 million. Counting the calls gives a recurrence of its own, because each call is itself plus the calls its two children make:

```formula
C(n) = 1 + C(n − 1) + C(n − 2)
C(0) = C(1) = 1
C(n) = 2 × F(n + 1) − 1 = Θ(φ^n)
C(30) = 2 × F(31) − 1
C(30) = 2 × 1,346,269 − 1 = 2,692,537
where
C(n): the total number of calls that fib(n) makes, including itself
n: a non-negative integer argument passed to fib; the recursive recurrence applies from two upwards
F(n): the nth Fibonacci number (F(0) = 0, F(1) = 1, each later one the sum of the previous two)
φ: phi, the golden ratio, (1 + √5) / 2 ≈ 1.618
φ^n: n copies of φ multiplied together
Θ: Big-Theta, grows at exactly this rate up to a constant factor (here C(n) is about 1.45 × φ^n)
In words: the call count follows the Fibonacci pattern itself, so each extra 1 on the argument multiplies the work by about 1.6.
```

The total grows that fast because the same subproblems are solved again and again. Caching results (memoisation) reduces this to O(n) additions; integer bit costs grow with n, so this is not an O(n) bit-time claim; that idea is the heart of the dynamic programming module.

> [!warning] Hidden O(n) work per call
> Here n is the original list length. `return xs[0] + total(xs[1:])` looks linear, but each slice copies the list. Because every frame holds its slice until it returns, memory grows the same way. Pass an index instead of slicing.

Adding up the copies on a list of n items:

```formula
S = (n − 1) + (n − 2) + … + 1 + 0
S = (n(n − 1)) / 2 = O(n^2)
S = 1000 × 999 / 2 = 499,500
where
S: the total number of list references copied by all the slices
n: the length of the original list; 1000 in the last line
…: and so on, one fewer each time
O(n^2): grows in proportion to n squared (n × n)
In words: the slices copy n − 1, then n − 2, and so on, which adds up to about n²/2 copies; 1000 items cost about half a million copies instead of 1000.
```

That gives O(n²) time (assuming constant-cost element addition) and, because the slices are all alive at the deepest point, O(n²) memory at its peak.

## Key takeaways
- A recursion tree counts repeated work, not just distinct arguments.
- A copied slice retained by each frame can turn linear-looking recursion into quadratic work and storage.

## Further reading
- [Recursive cost analysis — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
- [Python lists and slices](https://docs.python.org/3/tutorial/introduction.html#lists)
