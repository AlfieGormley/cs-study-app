---
id: adv-fenwick-limits-selection
title: Fenwick selection, limits and alternatives
level: advanced
minutes: 3
summary: Order-statistic walks require non-negative counts so prefixes are monotone.
sourceLesson: adv-fenwick-trees
---

Here n is the number of input elements. Fenwick positions start at 1; the empty prefix is valid, but an update at zero is not. Arithmetic costs assume word-sized values.

### Finding the k-th element

If the tree stores non-negative counts and k is between 1 and the total count, "find the smallest i with `prefix(i) >= k`" (the k-th smallest element) can be done in O(log n) by walking down powers of two, where n is the tree size. Binary searching over `prefix` instead costs O(log² n), meaning (log n) squared: about log n prefix queries of about log n steps each.

### Two dimensions

Nest the loops (`t[i][j]`, each loop using lowbit) for 2D prefix sums with point updates on an n-by-m grid in O(log n · log m): about log n steps in one direction, each doing about log m steps in the other.

## Fenwick tree vs segment tree

In this table n is the number of array elements.

| | Fenwick | Segment tree |
|---|---|---|
| Memory | One extra slot beyond array length | About two to four times array length |
| Code | ~10 lines | ~40+ lines |
| Operations | Commutative group (sum, XOR) | Any associative |
| Range min/max | Awkward | Natural |
| Range updates | Difference-array methods | Lazy tags |

The key limitation: range queries come from `prefix(r) - prefix(l - 1)`, which needs an **inverse element**. For the standard point-delta update shown here, combining must also be associative and commutative, with an identity: an abelian group. Sum has subtraction, XOR is its own inverse, but **min and max have no inverse**: knowing the minimum of `a[1..r]` and of `a[1..l-1]` tells you nothing about the minimum of `a[l..r]`. A Fenwick tree can maintain *prefix* minima if values only decrease, but for general range min with updates, use a segment tree.

Fenwick trees are also fast in practice: the loops are tight, the array is compact, and there is no recursion.

## Pitfalls

- **zero-based indexing**: an infinite loop on index 0, or off-by-one errors at the ends. Keep the shift in one place.
- Assigning instead of adding: `add` adds a delta. To *set* `a[i] = x`, keep a copy of the array and add `x - a[i]`.
- **Using it for min/max range queries**: subtraction does not work for them.
- **Overflow** in fixed-width languages: prefix sums of many large values can exceed 32 bits. Choose a width justified by the maximum total, or use arbitrary-precision integers; even 64 bits can overflow. A quick check:

A million values of up to ten thousand can total ten billion, beyond a signed 32-bit integer. A signed 64-bit integer fits that example, but choose the type from the actual input bounds, including possible negative totals.

## Key takeaways

- Order-statistic walks require non-negative counts so prefixes are monotone.
- General range sums need an inverse; min and max require different restrictions or a segment tree.

## Further reading
- [Fenwick trees — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
