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

The last column is the base-two logarithm of the number of orderings, rounded up. For four elements, 24 possible orderings need five comparisons in the worst case, because four yes/no answers can tell apart only 16.

| n | n! | min worst-case compares |
|---|---|---|
| 3 | 6 | 3 |
| 4 | 24 | 5 |
| 5 | 120 | 7 |
| 1,000,000 | huge | ≈ 18.5 million |

How close does merge sort get? For a million elements, top-down merge sort's exact worst case (from the merge-sort units in this module) is about 18.95 million comparisons, only about 2.5% above the 18.5 million minimum. (The rough figure n log₂ n, about 19.9 million, itself overstates the true minimum by about 8%.) There is little left to win on comparison counts; real-world gains come from cache behaviour, branch prediction and exploiting existing order.

> [!note] Exact optimal sorting is hard
> For five items the bound says 7 comparisons. Plain merge sort needs 8 in the worst case. The Ford–Johnson "merge insertion" algorithm achieves 7, but finding the true minimum for every n is an open problem.

### What the bound does not say

- **It only covers comparisons.** If you can look inside the keys (use an integer as an array index, or inspect digits), the decision-tree model does not apply. That is how counting sort and radix sort run in linear time (covered later in this module).
- **It is about the worst or average case.** An adaptive sort can be O(n) on already sorted input. The bound applies to the set of all n! inputs; a more refined version says you need about log₂(number of possible inputs) comparisons, which is why sorting data with few runs or few distinct values can be faster.
- **It has consequences elsewhere.** Anything that would let you sort is also Ω(n log n). For example, building a binary search tree from n items and reading it in order sorts them, so building a comparison-based BST from arbitrary distinct unsorted keys has Ω(n log n) worst-case cost.
- **The same counting bounds searching.** A sorted array of n keys has one more possible insertion position than it has keys. Each yes/no order test can at best halve the remaining positions, so finding where a new key belongs needs about log₂ n tests in the worst case: 10 tests for 1,023 keys (1,024 positions). Lower-bound binary search achieves exactly that.

```formula reference
q ≥ ⌈log_2(n + 1)⌉
where
q: the worst-case number of yes/no order tests needed to find where a new key belongs
n: the number of elements already in the sorted array, which leaves n + 1 possible insertion positions
log_2: the base-2 logarithm
⌈ ⌉: the ceiling: round up to the next whole number
≥: greater than or equal to
In words: each yes/no test can at best halve the possible positions, so choosing among all the insertion positions needs about as many tests as the number of times their count can be halved.
```

## Key takeaways
- Merge sort’s comparison count is close to the information lower bound.
- The bound covers comparison-based worst or uniform-average cases, rather than sorted inputs or digit-indexing methods.

## Further reading
- [Priority queues and heapsort — Princeton Algorithms](https://algs4.cs.princeton.edu/24pq/)
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
