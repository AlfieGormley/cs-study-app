---
id: adv-fenwick-prefix-blocks
title: Prefix sums as binary-sized blocks
level: advanced
minutes: 4
summary: Subtract two prefix totals to answer a range sum.
sourceLesson: adv-fenwick-trees
---

Here n is the number of input elements. Fenwick positions start at 1; the empty prefix is valid, but an update at zero is not. Arithmetic costs assume word-sized values.

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

What it gives up in generality it repays in simplicity. The whole structure is one array of n + 1 numbers and two loops of about four lines each. Historical accounts commonly credit Boris Ryabko’s 1989 coding work. Peter Fenwick’s 1994 paper presents the binary indexed tree for cumulative-frequency tables in arithmetic-coding compression.

## The intuition: binary decomposition of a prefix

Any positive whole number is a sum of distinct powers of two. Thirteen uses eight, four and one. In the same way, the prefix of the first 13 elements can be split into blocks whose lengths are powers of two, longest first:

```formula
13 = 8 + 4 + 1
P(13) = B(1, 8) + B(9, 12) + B(13, 13)
where
P(13): the prefix sum of the first 13 elements
B(l, r): the sum of the block of elements from position l to position r inclusive
In words: the blocks of lengths 8, 4 and 1 tile positions 1 to 13 exactly, one block per 1-bit of 13 written in binary.
```

A Fenwick tree stores exactly these blocks. Entry `t[i]` holds the sum of a block ending at i whose length is the **lowest set bit** of i (the value of the rightmost 1 when i is written in binary). A prefix sum then needs one block per set bit of i:

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

## Key takeaways

- Subtract two prefix totals to answer a range sum.
- A prefix decomposes into one block for each set bit in its index.

## Further reading
- [Fenwick Tree — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
- [Fenwick tree — Wikipedia](https://en.wikipedia.org/wiki/Fenwick_tree)
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
