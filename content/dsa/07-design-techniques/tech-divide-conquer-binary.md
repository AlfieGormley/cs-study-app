---
id: tech-divide-conquer-binary
title: Binary search and one shrinking subproblem
level: intermediate
minutes: 2
sourceLesson: tech-divide-conquer
summary: Use the master theorem to count midpoint probes when only one half survives.
---

Here n is the number of sorted items. The previous unit compared local work with leaf growth; binary search is its equal-exponent case with just one surviving half at each step.

### Binary search

Compare the target with the middle element and discard the half that can't contain it. That is one subproblem of half the size, with a constant amount of work per call:

```formula
T(n) = T(n / 2) + O(1)
a = 1,  b = 2,  d = 0
c = log_2(1) = 0 = d
T(n) = Θ(n^0 log(n)) = Θ(log(n))
where
T(n): the worst-case running time of binary search on n sorted items
n: the number of items still in the search range
O(1): a constant amount of work (one probe and comparison), however large n is
a: the number of subproblems per call; 1, because one half is thrown away
b: the shrink factor; 2, because the range halves
d: the exponent of the per-call work; 0, because n^0 = 1 is constant
c: the critical exponent, log_2(a)
log_2(1): the base-2 logarithm of 1, which is 0 because 2^0 = 1
n^0: n to the power 0, which is 1
log: logarithm (the base only changes a constant)
Θ: Big-Theta, grows at exactly this rate up to constant factors
In words: d equals the critical exponent, so this is the "every level equal" case: a constant amount of work on each of about log n levels.
```

```formula
p_max = floor(log_2(n)) + 1
p_max = floor(log_2(10^9)) + 1 = 30
where
p_max: the maximum midpoint probes of ordinary binary search on a non-empty sorted range
n: the number of items, one billion here
floor: round down to the nearest integer
log_2: the base-two logarithm
In words: Binary search on a billion items needs at most thirty midpoint probes.
```

A three-way comparator can classify a probe in one comparison; separate equality and ordering tests may perform more.

Binary search is the degenerate case where "combine" is free and one half is thrown away entirely. Some people call this *decrease and conquer*.

## Key takeaways
- A midpoint comparison discards one half and leaves no costly combination.
- Count midpoint probes separately from language-level equality and ordering tests.

## Further reading
- [Recursive cost analysis — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
