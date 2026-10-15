---
id: dp-held-karp-resources
title: Count Held–Karp work and storage
level: advanced
minutes: 2
summary: Held–Karp reduces factorial enumeration to exponential DP.
sourceLesson: dp-advanced
---

The visited-set recurrence is exact for the stated cost matrix. Its resource requirements depend on the table representation and on which states are reachable.

Let n be the number of cities. The allocated table has one slot per subset and endpoint, and each reachable state tries up to n next cities:

```formula
T = O(n n 2^n) = O(n^2 2^n)
M = O(n 2^n)
T(20) ≈ 400 × 1,048,576 ≈ 4.2 × 10^8
where
T: the running time, in basic steps
M: the memory, in table entries
n: the number of cities
2^n: the number of subsets (bitmasks) of the n cities
n^2: n × n
O(...): Big-O, growing at most in proportion to the expression inside
≈: approximately equal to
In words: there are 2^n sets times n end cities, and each state tries about n next cities.
```

So **O(n² · 2ⁿ) time, O(n · 2ⁿ) space**. Compare 4.2 × 10⁸ with the 1.2 × 10¹⁷ brute-force tours: about 300 million times fewer. It is a work-bound proxy, not this implementation’s exact transition count: many allocated states are unreachable.

> [!note] Content gap
> C++/Python running-time predictions and a universal city-count cutoff are omitted because no pinned implementation, machine and benchmark support them.

Held–Karp remains exponential, but its bound is much smaller than factorial enumeration. NP-hardness does not prove that every exact TSP algorithm must take exponential time; even a proof that polynomial-time solving differs from polynomial-time verification would rule out polynomial time, not every subexponential possibility. Concorde uses branch-and-cut techniques and has solved particular large benchmark instances, which is not a worst-case guarantee.

> [!note] Content gap
> A claim that this is the current best exact worst-case TSP bound is omitted: that research frontier requires a separately scoped, up-to-date comparison of weight models and algorithm variants.

## Key takeaways
- Held–Karp reduces factorial enumeration to exponential DP.
- Allocated table states and executed transitions are different counts.
- Memory layout and available resources matter as much as the growth bound.

## Further reading
- [Held–Karp algorithm](https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
