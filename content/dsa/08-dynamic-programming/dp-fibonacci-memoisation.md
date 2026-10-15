---
id: dp-fibonacci-memoisation
title: Cache Fibonacci answers
level: basic
minutes: 2
summary: Memoisation computes a state on demand, then reuses its answer.
sourceLesson: dp-intro
---

The previous unit showed that the naive Fibonacci recursion requests the same positions repeatedly. Keep the same recurrence and add a cache rather than changing the mathematical answer.

### Fix 1: memoisation (top-down)

Here n is the nonnegative Fibonacci position. Keep the recursion, but remember every answer. Before computing `fib(k)`, check the cache.

```python
def fib(n, memo=None):
    # Reject values outside the recurrence.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    # One fresh cache per top-level request.
    if memo is None:
        memo = {}
    # The first two positions are base
    # cases.
    if n < 2:
        return n
    # Compute a state only on a cache miss.
    if n not in memo:
        # Store the result for later
        # callers.
        memo[n] = fib(n - 1, memo) + \
                  fib(n - 2, memo)
    return memo[n]
```

Python has this built in:

```python
from functools import cache

# Repeated arguments reuse stored answers.
@cache
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

In a cold-cache (initially empty), single-threaded `@cache` call with n of 2 or more, the body runs once for each value from 0 up to n; later requests hit the cache. The manual version does not cache its constant-time base cases. Counting integer additions and dictionary operations as unit cost gives **O(n) work and O(n) stored numbers**, plus recursive stack space.

The call tree collapses into a chain:

```
fib(5) -> fib(4) -> fib(3) -> fib(2) -> ...
   \         \         \
  fib(3)    fib(2)    fib(1)
  (hit)     (hit)     (hit)
```

## Key takeaways
- Memoisation computes a state on demand, then reuses its answer.
- A cold, single-threaded cache executes the Fibonacci body once per reachable argument.

## Further reading
- [Python caching](https://docs.python.org/3/library/functools.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
