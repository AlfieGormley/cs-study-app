---
id: adv-fenwick-trees
title: Fenwick trees
level: advanced
minutes: 13
summary: The binary indexed tree, a ten-line structure for prefix sums with updates in O(log n), how the lowbit trick drives it, and when to choose it over a segment tree.
---

A **Fenwick tree**, or **binary indexed tree** (BIT), solves a narrower problem than a segment tree: maintain an array under point updates and answer **prefix sums** `a[1] + ... + a[i]`. Range sums follow by subtraction.

What it gives up in generality it repays in simplicity. The whole structure is one array of n + 1 numbers and two loops of about four lines each. It was described by Boris Ryabko in 1989 and popularised by Peter Fenwick's 1994 paper, where it maintained cumulative frequency tables for arithmetic-coding compression.

## The intuition: binary decomposition of a prefix

Any number is a sum of distinct powers of two: 13 = 8 + 4 + 1. In the same way, the prefix `a[1..13]` can be split into blocks whose lengths are powers of two:

```
a[1..13] = a[1..8] + a[9..12] + a[13..13]
            len 8     len 4      len 1
```

A Fenwick tree stores exactly these blocks. Entry `t[i]` holds the sum of a block **ending at i** whose length is the **lowest set bit** of i. A prefix sum then needs one block per set bit of i: at most log2(n) + 1 of them.

## The lowbit trick

The lowest set bit of i is `i & -i`. This works because of two's complement: `-i` is `~i + 1`. Flipping every bit of i and adding one carries through the trailing zeros and stops at the lowest 1, so i and −i share exactly that one bit.

```
 i = 12  ->  ...0000 1100
-i       ->  ...1111 0100
i & -i   ->  ...0000 0100  = 4
```

Python integers behave as if they had infinitely many sign bits, so `i & -i` works there too.

So `t[i]` covers `a[i - lowbit(i) + 1 .. i]`. For n = 8:

| i | binary | lowbit | t[i] covers |
|---|---|---|---|
| 1 | 0001 | 1 | a[1] |
| 2 | 0010 | 2 | a[1..2] |
| 3 | 0011 | 1 | a[3] |
| 4 | 0100 | 4 | a[1..4] |
| 5 | 0101 | 1 | a[5] |
| 6 | 0110 | 2 | a[5..6] |
| 7 | 0111 | 1 | a[7] |
| 8 | 1000 | 8 | a[1..8] |

Odd indices hold single elements; powers of two hold whole prefixes.

## The code

Assume n ≥ 0, valid 1-based update positions and ranges, and 0 ≤ i ≤ n for prefix queries. `add(n + 1, delta)` is an intentional no-op used by range-update boundaries. Complexity counts constant-time word arithmetic; arbitrary-size integer arithmetic has additional bit costs.

```python
class Fenwick:
    def __init__(self, n):
        self.n = n
        # 1-indexed
        self.t = [0] * (n + 1)

    def add(self, i, delta):
        # a[i] += delta
        while i <= self.n:
            self.t[i] += delta
            i += i & -i

    def prefix(self, i):
        # a[1] + ... + a[i]
        s = 0
        while i > 0:
            s += self.t[i]
            i -= i & -i
        return s

    def range_sum(self, l, r):
        return (self.prefix(r)
                - self.prefix(l - 1))
```

### Querying: strip the lowest bit

`prefix(i)` adds `t[i]`, then removes i's lowest bit to jump to the end of the previous block, and repeats until i is 0.

```
prefix(13): 13 = 1101
  t[13]  covers a[13]       13 -> 12
  t[12]  covers a[9..12]    12 -> 8
  t[8]   covers a[1..8]      8 -> 0
```

Each step clears one set bit, so it takes at most about log2(n) steps.

### Updating: add the lowest bit

`add(i, delta)` must change every block that contains position i. Those are `t[i]`, then `t[i + lowbit(i)]`, and so on: adding the lowest bit jumps to the next larger block that also covers i.

```
add(5, d) with n = 16:
  t[5]   covers a[5]       5 -> 6
  t[6]   covers a[5..6]    6 -> 8
  t[8]   covers a[1..8]    8 -> 16
  t[16]  covers a[1..16]
```

Each step moves the lowest set bit at least one place left, so this is also O(log n).

> [!warning] Fenwick trees are 1-indexed
> Index 0 has lowbit 0, so `i += i & -i` would loop forever on `add(0, ...)`. Store `a[k]` at `k + 1` if your data is 0-indexed, and do the shift in one place.

## Building in O(n)

Calling `add` n times builds the tree in O(n log n). There is a linear method: copy the array in, then push each entry's total up to its immediate parent block once.

```python
def build(a):  # a is 0-indexed
    n = len(a)
    t = [0] + list(a)
    for i in range(1, n + 1):
        j = i + (i & -i)
        if j <= n:
            t[j] += t[i]
    return t
```

By the time the loop reaches i, `t[i]` already contains everything from its smaller sub-blocks, so a single forward pass suffices.

## Worked application: counting inversions

An **inversion** is a pair `i < j` with `a[i] > a[j]`. Walk left to right, keeping a Fenwick tree of how many times each value has been seen. For each element, the number of earlier elements greater than it is "elements seen so far" minus "seen elements ≤ it".

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
        inv += seen - fw.prefix(r)
        fw.add(r, 1)
    return inv
```

For `[3, 1, 2, 5, 4]` this returns 3: the pairs (3, 1), (3, 2) and (5, 4). It runs in O(n log n), the same as the merge-sort method, and the same pattern answers "count of smaller numbers after self" and rank queries in leaderboards.

**Coordinate compression** (mapping values to ranks) is what keeps the tree size equal to the number of distinct values rather than the largest value.

## Variations

### Range update, point query

Store a **difference array** in the tree. To add x to `a[l..r]`, call `add(l, x)` and `add(r + 1, -x)`. Now `prefix(i)` is the current value of `a[i]`.

### Range update, range query

Use two trees, `b1` and `b2`. A range add touches each tree twice, and

```
sum(a[1..i]) = prefix(b1, i) * i
               - prefix(b2, i)
```

```python
class RangeFenwick:
    def __init__(self, n):
        self.b1 = Fenwick(n)
        self.b2 = Fenwick(n)

    def range_add(self, l, r, x):
        self.b1.add(l, x)
        self.b1.add(r + 1, -x)
        self.b2.add(l, x * (l - 1))
        self.b2.add(r + 1, -x * r)

    def prefix(self, i):
        return (self.b1.prefix(i) * i
                - self.b2.prefix(i))
```

`b1` is the difference array; `b2` is a correction so that positions before l and after r come out right.

### Finding the k-th element

If the tree stores non-negative counts and 1 ≤ k ≤ the total count, "find the smallest i with `prefix(i) >= k`" (the k-th smallest element) can be done in O(log n) by walking down powers of two, rather than O(log² n) by binary searching over `prefix`.

### Two dimensions

Nest the loops (`t[i][j]`, each loop using lowbit) for 2D prefix sums with point updates in O(log n · log m).

## Fenwick tree vs segment tree

| | Fenwick | Segment tree |
|---|---|---|
| Memory | n + 1 | about 2n to 4n |
| Code | ~10 lines | ~40+ lines |
| Operations | Commutative group (sum, XOR) | Any associative |
| Range min/max | Awkward | Natural |
| Range updates | Tricks above | Lazy tags |

The key limitation: range queries come from `prefix(r) - prefix(l - 1)`, which needs an **inverse**. For the standard point-delta update shown here, combining must also be associative and commutative, with an identity: an abelian group. Sum has subtraction, XOR is its own inverse, but **min and max have no inverse**: knowing the minimum of `a[1..r]` and of `a[1..l-1]` tells you nothing about the minimum of `a[l..r]`. A Fenwick tree can maintain *prefix* minima if values only decrease, but for general range min with updates, use a segment tree.

Fenwick trees are also fast in practice: the loops are tight, the array is compact, and there is no recursion.

## Pitfalls

- **0-indexing**: an infinite loop on index 0, or off-by-one errors at the ends. Keep the shift in one place.
- **Assigning instead of adding**: `add` adds a delta. To *set* `a[i] = x`, keep a copy of the array and add `x - a[i]`.
- **Using it for min/max range queries**: subtraction does not work for them.
- **Overflow** in fixed-width languages: prefix sums of many large values can exceed 32 bits. Choose a width justified by the maximum total, or use arbitrary-precision integers; even 64 bits can overflow.

## Key takeaways
- `t[i]` stores the sum of the block of length `lowbit(i)` ending at i, where `lowbit(i) = i & -i`.
- `prefix` strips the lowest bit each step; `add` adds it. Both are O(log n), and an O(n) build exists.
- Range sum is `prefix(r) - prefix(l - 1)`, which only works for invertible operations.
- Difference-array tricks give range updates; coordinate compression makes counting problems like inversions fit.
- Prefer a Fenwick tree for sums and counts; use a segment tree for min, max or arbitrary combines.

## Further reading
- [Fenwick Tree — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
- [Fenwick tree — Wikipedia](https://en.wikipedia.org/wiki/Fenwick_tree)
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
