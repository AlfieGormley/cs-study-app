---
id: sort-comparison-bound-limits
title: Tight bounds and what they exclude
level: intermediate
minutes: 5
sourceLesson: sort-heapsort-lower-bound
summary: Merge sort’s comparison count is close to the information lower bound.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

### Real numbers

The last column rounds the base-two logarithm of the number of permutations upward. For four elements, 24 possible permutations require five comparisons in the worst case.

```formula
h ≥ ⌈log_2(n!)⌉
h ≥ ⌈log_2(24)⌉ = 5
where
h: worst-case number of Boolean key comparisons
n: number of distinct elements; four here
!: factorial, product of the integers from one through n
log_2: base-two logarithm
⌈ ⌉: ceiling, round upward
≥: greater than or equal to
In words: A binary comparison tree must be deep enough to distinguish all 24 permutations.
```

| n | n! | min worst-case compares |
|---|---|---|
| 3 | 6 | 3 |
| 4 | 24 | 5 |
| 5 | 120 | 7 |
| 1,000,000 | huge | ≈ 18.5 million |

How close does merge sort get? Use the exact worst-case count for top-down merge sort from the relevant unit in this module:

```formula
C_w = n⌈log_2(n)⌉ − 2^{⌈log_2(n)⌉} + 1
C_w = 10^6 × 20 − 2^20 + 1
C_w = 18951425 ≈ 1.895 × 10^7
r = C_w / log_2(n!)
r ≈ 1.895 × 10^7 / (1.849 × 10^7) ≈ 1.025
where
C_w: the most comparisons top-down merge sort makes on any input of n elements
n: the number of elements, a million (10^6)
log_2(n): the base-2 logarithm of n, about 19.93 here
⌈ ⌉: the ceiling: round up to a whole number, so ⌈19.93⌉ = 20
2^20: 20 copies of 2 multiplied together, 1,048,576
log_2(n!): the information lower bound on worst-case comparisons, about 18.49 million here; an exact optimum may be higher
r: the ratio of merge sort's worst case to that minimum
10^6: ten to the power 6, a million; 10^7 is ten million
≈: approximately equal to
In words: in its worst case, merge sort uses only about 2.5% more comparisons than the theoretical minimum for a million elements.
```

So merge sort's worst case is within about 3% of the absolute minimum (the rough estimate input size times its base-two logarithm would put it within about 8%). There is little left to win on comparison counts; real-world gains come from cache behaviour, branch prediction and exploiting existing order.

> [!note] Exact optimal sorting is hard
> For five items the bound says 7 comparisons. Plain merge sort needs 8 in the worst case. The Ford–Johnson "merge insertion" algorithm achieves 7, but finding the true minimum for every n is an open problem.

### What the bound does not say

- **It only covers comparisons.** If you can look inside the keys (use an integer as an array index, or inspect digits), the decision-tree model does not apply. That is how counting sort and radix sort run in linear time (covered later in this module).
- **It is about the worst or average case.** An adaptive sort can be O(n) on already sorted input. The bound applies to the set of all n! inputs; a more refined version says you need about log₂(number of possible inputs) comparisons, which is why sorting data with few runs or few distinct values can be faster.
- **It has consequences elsewhere.** Anything that would let you sort is also Ω(n log n). For example, building a binary search tree from n items and reading it in order sorts them, so building a comparison-based BST from arbitrary distinct unsorted keys has Ω(n log n) worst-case cost. Locating one of one more insertion position than the existing item count with Boolean order tests requires a matching minimum number of tests in the worst case (formula below), achieved by lower-bound binary search.

```formula
q ≥ ⌈log_2(n + 1)⌉
q ≥ ⌈log_2(1024)⌉ = 10
where
q: the worst-case number of yes/no order tests needed to find where a new key belongs
n: the number of elements already in the sorted array; here 1,023, which leaves 1,024 possible insertion positions
log_2: the base-2 logarithm
⌈ ⌉: the ceiling: round up to the next whole number
≥: greater than or equal to
In words: each yes/no test can at best halve the possible positions, so choosing among n + 1 positions needs about log_2(n + 1) tests.
```

## Key takeaways
- Merge sort’s comparison count is close to the information lower bound.
- The bound covers comparison-based worst or uniform-average cases, rather than sorted inputs or digit-indexing methods.

## Further reading
- [Priority queues and heapsort — Princeton Algorithms](https://algs4.cs.princeton.edu/24pq/)
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
