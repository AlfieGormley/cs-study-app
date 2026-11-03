---
id: adv-fenwick-prefix-blocks
title: Prefix sums as binary-sized blocks
level: advanced
minutes: 4
summary: Subtract two prefix totals to answer a range sum.
sourceLesson: adv-fenwick-trees
---

Here n is the number of input elements. Fenwick positions start at 1; the empty prefix is valid, but an update at zero is not. Arithmetic costs assume word-sized values.

A **Fenwick tree**, or **binary indexed tree** (BIT), maintains point updates and prefix sums: totals from position one through a chosen endpoint. To obtain a range sum, subtract the prefix before its left end from the prefix through its right end. The empty prefix totals zero.

For example, if the prefix through position two totals seven and the prefix through position five totals twenty-five, positions three through five total eighteen. This cancellation works because subtraction undoes addition. Two prefix minima cannot be cancelled this way.

What it gives up in generality it repays in simplicity. The whole structure is one array of n + 1 numbers and two loops of about four lines each. Historical accounts commonly credit Boris Ryabko’s 1989 coding work. Peter Fenwick’s 1994 paper presents the binary indexed tree for cumulative-frequency tables in arithmetic-coding compression.

## The intuition: binary decomposition of a prefix

Any positive whole number is a sum of distinct powers of two. Thirteen uses eight, four and one, so its prefix can be tiled by positions 1–8, 9–12 and 13.

A Fenwick entry stores the block ending at its own index. Its block length is the value of that index's **lowest set bit**, the rightmost one in binary. A prefix query reads its final block, then the preceding block, until the entire prefix is covered without overlap.

Each step removes one set bit. An index has only logarithmically many bits, so the query needs O(log n) stored blocks rather than a scan of n elements.

## Key takeaways

- Subtract two prefix totals to answer a range sum.
- A prefix decomposes into one block for each set bit in its index.

## Further reading
- [Fenwick trees — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
