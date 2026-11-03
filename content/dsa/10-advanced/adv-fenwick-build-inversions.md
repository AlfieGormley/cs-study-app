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

An **inversion** is an earlier element paired with a strictly smaller later element. Equal values do not count. Sorted input has no inversions; reversing distinct elements reverses the order of every pair.

Walk left to right with a Fenwick tree of frequencies for values already seen. For each current value, count earlier elements, then subtract how many are less than or equal to it. The remainder is how many earlier values are strictly greater. Insert the current value only after that query.

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

The query includes the current value's rank, so equal earlier values are excluded from the inversion count. Compressing values to sorted ranks preserves comparisons while keeping the tree compact.

For `[3, 1, 2, 5, 4]` the three inversions are the pairs (3, 1), (3, 2) and (5, 4). For an array of n elements it runs in O(n log n), the same as the merge-sort approach, and the same pattern answers "count of smaller numbers after self" and rank queries in leaderboards.

**Coordinate compression** (mapping values to ranks) is what keeps the tree size equal to the number of distinct values rather than the largest value.

## Key takeaways

- A forward pass builds block totals in linear time.
- Coordinate-compressed counts reveal how many earlier elements exceed each value.

## Further reading
- [Fenwick trees — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
