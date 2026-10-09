---
id: adv-fenwick-trees
title: Fenwick trees
level: advanced
minutes: 13
summary: The binary indexed tree, a ten-line structure for prefix sums with updates in O(log n), how the lowbit trick drives it, and when to choose it over a segment tree.
---

A **Fenwick tree**, or **binary indexed tree** (BIT), solves a narrower problem than a segment tree: maintain an array under point updates and answer **prefix sums**: the total of the first i elements. Range sums then follow by subtraction:

```formula
P(i) = a[1] + a[2] + … + a[i]
S(l, r) = P(r) − P(l − 1)
P(0) = 0
S(3, 5) = P(5) − P(2) = 25 − 7 = 18
a[3] + a[4] + a[5] = 8 + 1 + 9 = 18
where
a[k]: the value at position k of the array, counting from 1; the example uses a = [5, 2, 8, 1, 9, 3, 7, 4]
n: the length of the array (8 in the example)
i: a position from 0 to n
P(i): the prefix sum up to position i: the total of the first i elements
l, r: the first and last positions of a range, with l ≤ r
S(l, r): the sum of a[l] through a[r] inclusive
…: "and so on", every term in between
In words: the sum of a block is the running total at its right end minus the running total just before its left end.
```

The last line adds the three elements directly and matches. The trick only works because addition can be undone by subtraction; it fails for operations such as minimum (see below).

What it gives up in generality it repays in simplicity. The whole structure is one array of n + 1 numbers and two loops of about four lines each. It was described by Boris Ryabko in 1989 and popularised by Peter Fenwick's 1994 paper, where it maintained cumulative frequency tables for arithmetic-coding compression.

## The intuition: binary decomposition of a prefix

Any number is a sum of distinct powers of two: 13 = 8 + 4 + 1. In the same way, the prefix of the first 13 elements can be split into blocks whose lengths are powers of two, longest first:

```formula
13 = 8 + 4 + 1
P(13) = B(1, 8) + B(9, 12) + B(13, 13)
where
P(13): the prefix sum of the first 13 elements
B(l, r): the sum of the block of elements from position l to position r inclusive
In words: the blocks of lengths 8, 4 and 1 tile positions 1 to 13 exactly, one block per 1-bit of 13 written in binary.
```

A Fenwick tree stores exactly these blocks. Entry `t[i]` holds the sum of a block **ending at i** whose length is the **lowest set bit** of i (the value of the rightmost 1 when i is written in binary). A prefix sum then needs one block per set bit of i:

```formula
c(i) ≤ ⌊log_2(n)⌋ + 1
c(13) = 3 ≤ ⌊log_2(16)⌋ + 1 = 5
where
i: the position the prefix ends at, from 1 to n
n: the length of the array (16 in the example)
c(i): the number of 1-bits in i written in binary, which is how many blocks the prefix sum adds
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
⌊ ⌋: floor: round down to the nearest whole number
≤: is at most
In words: a number up to n has at most about log_2(n) + 1 binary digits, so a prefix sum never needs more blocks than that.
```

For a million elements that is at most 20 blocks per query.

## The lowbit trick

The lowest set bit of i is `i & -i` in code. This works because of two's complement, the way computers store negative integers:

```formula
lowbit(i) = i & (−i)
−i = (~i) + 1
12 = …0000 1100₂
~12 = …1111 0011₂
−12 = …1111 0100₂
12 & (−12) = …0000 0100₂ = 4
where
i: a positive whole number, a position in the tree
lowbit(i): the value of the lowest (rightmost) 1-bit of i
~i: bitwise NOT: i with every bit flipped
&: bitwise AND: a bit is 1 in the result only where it is 1 in both inputs
₂: the number is written in binary (base 2)
…: the same digit repeats to the left (all 0s for a positive number, all 1s for a negative one)
In words: flipping every bit and adding one carries through the trailing zeros and stops at the lowest 1, so i and −i share exactly that one bit, and AND keeps only it.
```

So `lowbit(12)` is 4: 12 is 1100 in binary, and its rightmost 1 is worth 4. For any odd number the answer is 1.

Python integers behave as if they had infinitely many sign bits, so `i & -i` works there too.

Each entry therefore covers this block:

```formula
t[i] = a[i − lowbit(i) + 1] + … + a[i]
t[6] = a[6 − 2 + 1] + … + a[6] = a[5] + a[6]
where
i: the index of the entry, from 1 to n
t[i]: the value stored at index i of the Fenwick array
a[k]: the array element at position k
lowbit(i): the value of the lowest 1-bit of i
…: every element in between
In words: entry i holds the sum of the lowbit(i) elements that end at position i.
```

For n = 8 (an array of 8 elements):

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

Assume n (the array length) is zero or more, update positions and ranges are valid 1-based positions, and a prefix query asks for anything from 0 to n elements. `add(n + 1, delta)` is an intentional no-op used by range-update boundaries. Complexity counts constant-time word arithmetic; arbitrary-size integer arithmetic has additional bit costs.

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

`prefix(i)` adds `t[i]`, then removes i's lowest bit to jump to the end of the previous block, and repeats until i is 0:

```formula
i_next = i − lowbit(i)
13 − lowbit(13) = 13 − 1 = 12
12 − lowbit(12) = 12 − 4 = 8
8 − lowbit(8) = 8 − 8 = 0
P(13) = t[13] + t[12] + t[8]
where
i: the current index, starting at the prefix length asked for
i_next: the next index to visit
lowbit(i): the value of the lowest 1-bit of i
t[i]: the stored block sum at index i
P(13): the sum of the first 13 elements
In words: subtracting the lowest bit jumps to the end of the block just before the current one, so the query reads t[13] (a[13]), t[12] (a[9] to a[12]) and t[8] (a[1] to a[8]).
```

In binary the walk is 1101 → 1100 → 1000 → 0: each step clears one set bit, so it takes at most about log_2(n) + 1 steps for an array of n elements.

### Updating: add the lowest bit

`add(i, delta)` must change every block that contains position i. Those are `t[i]`, then `t[i + lowbit(i)]`, and so on: adding the lowest bit jumps to the next larger block that also covers i.

```formula
i_next = i + lowbit(i)
5 + lowbit(5) = 5 + 1 = 6
6 + lowbit(6) = 6 + 2 = 8
8 + lowbit(8) = 8 + 8 = 16
16 + lowbit(16) = 32 > n = 16
where
i: the current index, starting at the position being changed
i_next: the next index to update
lowbit(i): the value of the lowest 1-bit of i
n: the length of the array, 16 in this example
>: is greater than, so the loop stops
In words: adding the lowest bit climbs to the next, longer block that still contains the position, until the index passes the end of the array.
```

So `add(5, d)` changes t[5] (element 5), t[6] (elements 5 to 6), t[8] (elements 1 to 8) and t[16] (elements 1 to 16). Each step moves the lowest set bit at least one place left, so this is also O(log n): the number of steps grows with the logarithm of the array length n.

> [!warning] Fenwick trees are 1-indexed
> Index 0 has lowbit 0, so `i += i & -i` would loop forever on `add(0, ...)`. Store `a[k]` at `k + 1` if your data is 0-indexed, and do the shift in one place.

## Building in O(n)

For an array of n elements, calling `add` n times builds the tree in O(n log n). There is a linear, O(n), method: copy the array in, then push each entry's total up to its immediate parent block once.

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

An **inversion** is a pair of positions that are out of order:

```formula
I(a) = #{(i, j) : i < j and a[i] > a[j]}
I([3, 1, 2, 5, 4]) = 3
I_max = n × (n − 1) / 2
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
In words: count every pair where the earlier element is bigger than the later one; a reversed array has every pair out of order.
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
        inv += seen - fw.prefix(r)
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

## Variations

### Range update, point query

Store a **difference array** in the tree: each entry holds how much an element differs from the one before it. Then a range add touches only two entries, and an element's value is a prefix sum:

```formula
d[k] = a[k] − a[k − 1]
a[i] = d[1] + d[2] + … + d[i]
d[l] ← d[l] + x
d[r + 1] ← d[r + 1] − x
where
a[k]: the current value at position k (a[0] is taken as 0)
d[k]: the difference between position k and the one before it
i: the position whose value is wanted
l, r: the first and last positions of the range being increased
x: the amount added to every element from l to r
←: "becomes": replace the left side with the right side
…: every term in between
In words: adding x to a range only changes the step up at its start and the step down just after its end, and summing the steps rebuilds any value.
```

In code that is `add(l, x)` and `add(r + 1, -x)`, and `prefix(i)` returns the current value of a_i. Example: on 6 zeros, adding 5 to positions 2 to 4 gives differences [0, 5, 0, 0, −5, 0], whose running totals are [0, 5, 5, 5, 0, 0].

### Range update, range query

Use two trees, `b1` and `b2`. A range add of x to positions l to r touches each tree twice: `b1` gets +x at l and −x at r + 1 (a difference array), and `b2` gets x × (l − 1) at l and −x × r at r + 1. The prefix sum is then:

```formula
P(i) = P_1(i) × i − P_2(i)
P_1(i) = x   when l ≤ i ≤ r
P_2(i) = x × (l − 1)   when l ≤ i ≤ r
P(i) = x × i − x × (l − 1) = x × (i − l + 1)
P_2(i) = x × (l − 1) − x × r   when i > r
P(i) = 0 − x × (l − 1 − r) = x × (r − l + 1)
P(4) = 5 × 4 − 5 × 2 = 10
P(7) = 0 × 7 − (10 − 30) = 20
where
i: the position the prefix sum ends at
P(i): the true sum of the first i elements
P_1(i): the prefix sum read from tree b1
P_2(i): the prefix sum read from tree b2, a correction term
l, r: the first and last positions of the range add
x: the amount added to each element in the range
≤: is at most
>: is greater than
In words: inside the range, b1 counts x for every position up to i, which is too much by the l − 1 positions before the range, and b2 subtracts exactly that; past the range, b2 alone leaves x times the range length.
```

Before the range both trees read 0, so the prefix sum is 0, as it should be. The last two lines are a worked example: add 5 to positions 3 to 6 of an 8-element array of zeros. At position 4 the answer is 10 (two elements of 5 so far); at position 7 it is 20 (all four elements of 5). Several range adds simply add up, because both trees are linear.

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

If the tree stores non-negative counts and k is between 1 and the total count, "find the smallest i with `prefix(i) >= k`" (the k-th smallest element) can be done in O(log n) by walking down powers of two, where n is the tree size. Binary searching over `prefix` instead costs O(log² n), meaning (log n) squared: about log n prefix queries of about log n steps each.

### Two dimensions

Nest the loops (`t[i][j]`, each loop using lowbit) for 2D prefix sums with point updates on an n-by-m grid in O(log n · log m): about log n steps in one direction, each doing about log m steps in the other.

## Fenwick tree vs segment tree

In this table n is the number of array elements.

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
- **Overflow** in fixed-width languages: prefix sums of many large values can exceed 32 bits. Choose a width justified by the maximum total, or use arbitrary-precision integers; even 64 bits can overflow. A quick check:

```formula
S_max = n × v_max
S_max = 10^6 × 10^4 = 10^10
L_32 = 2^31 − 1 ≈ 2.1 × 10^9
where
n: the number of elements, a million here
v_max: the largest value one element can hold, 10,000 here
S_max: the largest total any prefix sum can reach
L_32: the largest value a signed 32-bit integer can hold, 2,147,483,647
2^31: 2 multiplied by itself 31 times
≈: approximately equal to
In words: a million values of up to 10,000 can total ten billion, nearly five times more than a 32-bit signed integer can store.
```

Here a 64-bit integer (limit about 9.2 × 10^18) is plenty.

## Key takeaways
- Entry `t[i]` stores the sum of the block ending at position i whose length is the lowest set bit of i, computed as `i & -i`.
- `prefix` strips the lowest bit each step; `add` adds it. For n elements both are O(log n), and an O(n) build exists.
- A range sum is the prefix sum at the range's end minus the prefix sum just before its start, which only works for invertible operations.
- Difference-array tricks give range updates; coordinate compression makes counting problems like inversions fit.
- Prefer a Fenwick tree for sums and counts; use a segment tree for min, max or arbitrary combines.

## Further reading
- [Fenwick Tree — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
- [Fenwick tree — Wikipedia](https://en.wikipedia.org/wiki/Fenwick_tree)
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
