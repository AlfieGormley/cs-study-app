---
id: sort-search-root-applications
title: Integer square roots and search applications
level: intermediate
minutes: 2
sourceLesson: sort-binary-search
summary: A feasible lower endpoint and infeasible upper endpoint converge to the integer root.
---

This unit builds on the preceding search units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

**Integer square root** is another instance, using the `hi - lo > 1` style:

```python
def isqrt(n):
    if type(n) is not int or n < 0:
        raise ValueError(
            "nonnegative integer"
        )
    lo, hi = 0, n + 1   # lo*lo <= n < hi*hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        # Keep a feasible floor-root
        # candidate.
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid
    return lo
```

For **real-valued** answers, use a suitable tolerance and an iteration limit, and stop when the computed midpoint equals an endpoint. A fixed 100 halvings does not cover every possible binary64 interval, especially across large exponent ranges or near subnormal values.

## Binary search in the wild

- **`git bisect`** narrows commit ancestry using good/bad tests. On a linear, monotone history with no skipped commits, 1,000 candidates take about 10 tests; merge graphs, flaky tests and fixes/reintroductions complicate that model.
- **B-tree pages** in databases (PostgreSQL, InnoDB) binary search the sorted keys inside each page.
- **Timsort's galloping** (covered earlier in this module) is an exponential search: probe 1, 3, 7, 15 ... until overshooting, then binary search. That is the right tool when the answer is probably near the start or the range is unbounded.
- **Standard libraries:** Python's `bisect`, C++'s `lower_bound`, `upper_bound` and `equal_range`, Java's `Arrays.binarySearch` (returns `-(insertion point) - 1` when absent), and Go's `sort.Search`, which is binary search on a predicate.

## Key takeaways
- A feasible lower endpoint and infeasible upper endpoint converge to the integer root.
- Library and real-valued searches require their own ordering, rounding and termination contracts.

## Further reading
- [Insertion-bound searches — Python bisect](https://docs.python.org/3/library/bisect.html)
- [Integer square-root contract — Python math](https://docs.python.org/3/library/math.html#math.isqrt)
