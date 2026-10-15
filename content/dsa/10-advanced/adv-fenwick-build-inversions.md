---
id: adv-fenwick-build-inversions
title: Linear construction and inversion counting
level: advanced
minutes: 4
summary: A forward pass builds block totals in linear time.
sourceLesson: adv-fenwick-trees
---

Here n is the number of input elements. Fenwick positions start at 1; the empty prefix is valid, but an update at zero is not. Arithmetic costs assume word-sized values.

## Building in O(n)

For an array of n elements, calling `add` n times builds the tree in O(n log n). There is a linear, O(n), method: copy the array in, then push each entry's total up to its immediate parent block once.

```python
def build(a):  # a is 0-indexed
    n = len(a)
    t = [0] + list(a)
    for i in range(1, n + 1):
        j = i + (i & -i)
        if j <= n:
            # Forward this complete block
            # once.
            t[j] += t[i]
    return t
```

By the time the loop reaches i, `t[i]` already contains everything from its smaller sub-blocks, so a single forward pass suffices.

## Worked application: counting inversions

An **inversion** is a pair of positions whose values violate ascending order:

```formula
I(a) = #{(i, j) : i < j and a[i] > a[j]}
I([3, 1, 2, 5, 4]) = 3
I_max = n(n − 1) / 2
I_max = 5 × 4 / 2 = 10
where
a: the array, with a[k] its element at position k
i, j: two positions in the array
I(a): the number of inversions in a
n: the number of elements in the array, 5 in the example
I_max: the most inversions an array of n distinct elements can have, reached when it is in reverse order
#{ }: the number of items in the set described inside the braces
<: is less than
>: is greater than
In words: count every pair where the earlier element is bigger than the later one; a reversed array has every pair in descending order.
```

A sorted array has 0 inversions; a reversed array of n distinct elements has the most possible, I_max, 10 for five elements. Walk left to right, keeping a Fenwick tree of how many times each value has been seen. For each element, the number of earlier elements greater than it is "elements seen so far" minus "seen elements ≤ it".

```python
def count_inversions(a):
    # compress values to ranks 1..m
    ranks = {v: i + 1 for i, v in
             enumerate(sorted(set(a)))}
    fw = Fenwick(len(ranks))
    inv = 0
    for seen, v in enumerate(a):
        r = ranks[v]
        # earlier elements greater than v
        # Exclude prior values at most v.
        inv += seen - fw.prefix(r)
        # Record v only after counting its
        # pairs.
        fw.add(r, 1)
    return inv
```

Each element adds the number of earlier elements bigger than it:

```formula
g[j] = j − P(r[j])
I = g[0] + g[1] + g[2] + g[3] + g[4]
I = 0 + 1 + 1 + 0 + 1 = 3
where
j: how many elements have been seen before the current one (the loop's `seen`, from 0)
r[j]: the rank of the current value: its position among the distinct values in sorted order
P(r[j]): how many already-seen values have rank at most r[j], read from the Fenwick tree
g[j]: how many earlier elements are greater than the current one
I: the total number of inversions
In words: everything seen so far, minus the ones not bigger than the current value, is the number of earlier values that are bigger.
```

For `[3, 1, 2, 5, 4]` the three inversions are the pairs (3, 1), (3, 2) and (5, 4). For an array of n elements it runs in O(n log n), the same as the merge-sort method, and the same pattern answers "count of smaller numbers after self" and rank queries in leaderboards.

**Coordinate compression** (mapping values to ranks) is what keeps the tree size equal to the number of distinct values rather than the largest value.

## Key takeaways

- A forward pass builds block totals in linear time.
- Coordinate-compressed counts reveal how many earlier elements exceed each value.

## Further reading
- [Fenwick Tree — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
- [Fenwick tree — Wikipedia](https://en.wikipedia.org/wiki/Fenwick_tree)
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
