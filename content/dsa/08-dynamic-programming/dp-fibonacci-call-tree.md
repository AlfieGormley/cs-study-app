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

```formula essential
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

For a nonnegative whole number n it is correct, but it becomes expensive as n grows. Look at the call tree for `fib(5)`:

```
              fib(5)
           /         \
       fib(4)        fib(3)
       /    \        /    \
   fib(3) fib(2)  fib(2) fib(1)
   /   \   / \     / \
 f(2) f(1) ...    ...
```

`fib(3)` is computed twice, `fib(2)` three times and `fib(1)` five times. These are the **overlapping subproblems**. Notice the pattern: the smaller the argument, the more branches lead to it, so the repeats pile up near the base cases.

## How fast the work grows

Each call counts itself plus every call its two children make. So the call count follows a Fibonacci-like rule of its own: `fib(5)` makes 15 calls, `fib(30)` makes 2,692,537 and `fib(40)` about 331 million.

```formula reference
calls(n) = 1 + calls(n − 1) + calls(n − 2)
calls(n) = 2F(n + 1) − 1
where
calls(n): the total number of calls made by the naive fib(n), including the first one; calls(0) = calls(1) = 1, and the first line applies from n = 2
n: the nonnegative Fibonacci position asked for
F(n + 1): the Fibonacci number at position n + 1
In words: one call for the current value plus every call made for the two smaller values, which works out to twice the next Fibonacci number, minus one.
```

Because Fibonacci numbers grow by a factor of about 1.618 (the golden ratio) at each step, so does the work: ten more positions multiply the number of calls by about 123. This is **exponential** growth, even though there are only n + 1 distinct subproblems (positions 0 to n). Almost all of the calls repeat an answer that has already been worked out somewhere else in the tree.

## Key takeaways
- Base cases stop the recurrence at zero and one.
- The naive call tree repeats states and grows exponentially.

## Further reading
- [Python caching](https://docs.python.org/3/library/functools.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
