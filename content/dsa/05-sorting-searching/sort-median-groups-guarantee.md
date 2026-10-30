---
id: sort-median-groups-guarantee
title: Median-of-medians pivot guarantees
level: advanced
minutes: 5
sourceLesson: sort-selection
summary: Groups of five guarantee a fixed fraction on each side, allowing rounding corrections.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Median of medians: worst-case O(n)

In 1973 Blum, Floyd, Pratt, Rivest and Tarjan showed that selection can be done in O(n) **guaranteed**. The trick is to spend a little linear work finding a pivot that is provably not too far from the middle.

1. Split the array into groups of 5.
2. Find the median of each group (constant work per group).
3. **Recursively** select the median of the group medians (one per five items, rounded up). Use it as the pivot.
4. Partition and recurse into the side containing k.

```python
def select(a, k):
    if not 0 <= k < len(a):
        raise IndexError(
            "rank out of range"
        )
    if len(a) <= 5:
        return sorted(a)[k]
    groups = [a[i:i + 5]
              for i in range(0, len(a), 5)]
    medians = [sorted(g)[len(g) // 2]
               for g in groups]
    mid = len(medians) // 2
    # Recursively find a well-balanced
    # pivot.
    pivot = select(medians, mid)
    lows = [x for x in a if x < pivot]
    highs = [x for x in a if x > pivot]
    # Count equal keys without another
    # array.
    n_eq = len(a) - len(lows) - len(highs)
    if k < len(lows):
        return select(lows, k)
    # Every rank in the equal block is
    # pivot.
    if k < len(lows) + n_eq:
        return pivot
    return select(highs,
                  k - len(lows) - n_eq)
```

### Why the pivot is good

Picture the groups as columns, each sorted with its median in the middle row, and the columns ordered by their medians. M is the median of medians.

```
 smaller medians    larger medians
   .  .  .  |  .  .  .
   .  .  .  |  .  .  .
   m  m  m  M  m  m  m
   .  .  .  |  .  .  .
   .  .  .  |  .  .  .
```

Half of the medians are no larger than the chosen median M. Each of those medians has two more elements in its group below it. So at least 3 elements in each of about half the groups are no bigger than M, and by symmetry the same number are no smaller:

```formula reference
s ≥ 3n / 10 − 6
r ≤ 7n / 10 + 6
where
s: the number of elements guaranteed to be no bigger than M (and, by symmetry, no smaller than M)
M: the median of the group medians, used as the pivot
n: the number of elements
r: the most elements the recursive call in step 4 can receive
≥: greater than or equal to
≤: less than or equal to
In words: three elements from each of half the groups lie on each side of M, so at least about 30% of the input is discarded every round and the recursive call gets at most about 70%; the small constant allows for the ragged last group and M's own group.
```

For 1,000 elements the conservative finite bound excludes at least 294 and leaves at most 706 for the retained recursive side, whatever the input order.

That gives two recursive calls per round: one on the group medians (a fifth of the input) to choose the pivot, and one on the retained side (at most about seven tenths). Together they handle at most about **nine tenths** of the input, so each level of recursion does at most about 90% of the previous level's work.

```formula reference
T(n) ≤ T(⌈n / 5⌉) + T(r) + cn
r ≤ 7n / 10 + 6
1/5 + 7/10 = 9/10
T(n) = O(n)
where
T(n): the worst-case running time of median of medians on n elements
n: the number of elements
r: size of the retained recursive side
c: a fixed per-element upper bound on grouping and partition work, in operations per element
⌈ ⌉: ceiling, round upward for the ragged group
O: Big O: grows at most this fast, up to a constant factor
≤: less than or equal to
In words: the pivot search and the retained side together receive about nine tenths of the input, apart from small rounding allowances, so the work shrinks geometrically from level to level and the total is linear.
```

Ignoring constant rounding allowances for the asymptotic argument, the two recursive size fractions sum to nine tenths, which is less than one. The total work at each level of recursion shrinks geometrically, and the whole algorithm is **O(n)**.

> [!note] Why groups of 5?
> With groups of 3, the guarantee is only about a third on each side. The pivot search then gets a third of the input and the retained side up to two thirds: together the whole input, so the work no longer shrinks from level to level and this analysis establishes only O(n log n), not a matching lower bound. Five is the smallest odd group size giving linear time by this simple argument; other algorithms can use repeated grouping or different methods.

## Key takeaways
- Groups of five guarantee a fixed fraction on each side, allowing rounding corrections.
- Selecting the medians and the retained side together uses less than the whole input per asymptotic level.

## Further reading
- [Heap operations and top-k — Python heapq](https://docs.python.org/3/library/heapq.html)
- [Time bounds for selection — Blum, Floyd, Pratt, Rivest and Tarjan](https://people.csail.mit.edu/rivest/pubs/BFPRT73.pdf)
