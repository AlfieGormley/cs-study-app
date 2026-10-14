---
id: cx-recursive-hidden-work
sourceLesson: cx-analysing-code
title: Recursive work and hidden costs
level: intermediate
minutes: 4
summary: Count recursive calls and uncover work hidden inside ordinary Python operations.
---

Here n is the input size or recursive argument. A small amount of source code can describe a large amount of executed work.

## Recursion

For recursive code, count **how many calls** happen and **how much work each does** outside the recursive calls.

Linear recursion makes one call per level:

```python
def fact(n):
    if n <= 1:
        return 1
    # Multiply after the smaller call ends.
    return n * fact(n - 1)
```

Θ(n) calls and multiplications in the unit-cost model, where n is the recursive argument. Actual Python multiplication gets more expensive as the factorial grows; factorial means the product of all positive integers up to the argument.

Branching recursion is where things explode. Naive Fibonacci makes two calls per level:

```python
# fib(5) returns 5; it makes 15 calls.
def fib(n):
    if n < 2:
        return n
    # Both branches can repeat earlier work.
    return fib(n - 1) + fib(n - 2)
```

Draw the **recursion tree**:

```
                 f5
           /            \
         f4              f3
       /    \          /    \
     f3      f2      f2      f1
    /  \    /  \    /  \
   f2  f1  f1  f0  f1  f0
  /  \
 f1  f0
```

(Here `f5` means `fib(5)`.) `fib(5)` makes 15 calls. In general:

```formula
calls(n) = 2F(n + 1) − 1
calls(5) = 2F(6) − 1 = 2 × 8 − 1 = 15
calls(n) = Θ(φ^n)
φ = (1 + √5) / 2 ≈ 1.618
where
calls(n): the total number of calls made by fib(n), counting the first one
F(n): the n-th Fibonacci number: 0, 1, 1, 2, 3, 5, 8, … (each is the sum of the two before; F(0) = 0, F(1) = 1, F(6) = 8)
n: the argument passed to fib
φ: phi, the golden ratio, about 1.618
φ^n: n copies of φ multiplied together
√5: the square root of 5, about 2.236
Θ: Big-Theta: grows at exactly this rate, up to a constant factor
≈: approximately equal to
In words: the number of calls is itself almost twice a Fibonacci number, and Fibonacci numbers grow by a factor of about 1.618 each step, so the call count grows exponentially.
```

`fib(30)` makes about 2.7 million calls; `fib(50)` would make about 4 × 10^10.

The waste is visible in the tree: `fib(3)` is computed twice, `fib(2)` three times. Caching results (**memoisation**, covered with dynamic programming later) reduces this to n distinct calls: Θ(n).

Divide-and-conquer recursion (halving the problem) needs the tools in the recurrence lessons, but a rough guide:

- One call on half the input, O(1) extra work: Θ(log n) (binary search).
- Two calls on halves, O(n) extra work: Θ(n log n) (merge sort).

## Hidden costs

Many "one-line" operations aren't O(1). In this CPython table, n is the list length:

| Operation | Cost |
|---|---|
| `x in some_list` | O(n) |
| `x in some_set` | O(1) average |
| `lst.append(x)` | O(1) amortised |
| `lst.insert(0, x)` | O(n) |
| `lst.pop(0)` | O(n) |
| `lst[a:b]` | O(b - a) copy |
| `sorted(lst)` | O(n log n) |
| `len(lst)` | O(1) |

This turns innocent-looking code quadratic:

```python
# unique([3, 1, 3]) returns [3, 1].
def unique(items):
    seen = []
    out = []
    for x in items:
        if x not in seen:   # O(n) scan
            seen.append(x)
            out.append(x)
    return out
```

The membership test scans `seen`, so the function is Θ(n^2) when most items are distinct. Changing `seen` to a `set` makes it Θ(n) on average. The algorithm didn't change; the data structure did.

> [!warning] Slicing in recursion
> `binary_search(arr[mid:], target)` looks logarithmic, but each slice copies the chosen half. The shrinking halves add to just under the original length, so a search on n items is O(n) rather than O(log n). Pass indices (`lo`, `hi`) instead.

```formula
C(n) ≈ n/2 + n/4 + n/8 + …
C(n) < n
where
C(n): the copied element slots over an absent-target search
n: the original list length
…: continue halving
≈: approximately, ignoring integer rounding
<: less than
In words: The series of copied halves is linear in the original length.
```

## Key takeaways
- Count all recursive calls and the work performed outside those calls.
- Naive Fibonacci repeats subproblems; memoisation stores their answers.
- Membership tests and slices can turn a short-looking Python function into expensive work.

## Further reading
- [TimeComplexity — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [Memoization — Wikipedia](https://en.wikipedia.org/wiki/Memoization)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
