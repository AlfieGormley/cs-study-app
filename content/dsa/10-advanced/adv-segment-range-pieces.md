---
id: adv-segment-range-pieces
title: Answering ranges from stored tree pieces
level: advanced
minutes: 3
summary: Each node summarises one contiguous range.
sourceLesson: adv-segment-trees
---

Here n is the non-empty input array’s length. Big-O bounds count constant-time combines of constant-size summaries on word-sized values.

Suppose you have an array and two kinds of request arriving in any order: "what is the sum (or minimum, or maximum) of `a[l..r]`?" and "change `a[i]`".

Throughout this lesson n is the number of elements in the array, and O(f) means "the work grows at most in proportion to f". `a[l..r]` means the elements from index l to index r, both included.

- A plain array makes updates O(1) (a fixed amount of work) but queries O(n).
- A prefix-sum array makes sum queries O(1) but every update O(n), because every later prefix changes.

On large arrays, many linear-time operations become expensive. A **segment tree** balances the trade-off: point updates and range queries each take O(log n), provided each summary has constant size and combining two summaries takes constant time. It works for associative operations, including sums, minima and maxima.

## The idea: store answers for halves, quarters, eighths...

Each node of a segment tree is responsible for a contiguous range of the array and stores the answer for that range. The root covers everything; each node splits its range in half between its two children; the leaves are single elements.

For `a = [5, 2, 8, 1, 9, 3, 7, 4]` with sums:

```
              [0,7]=39
         /              \
    [0,3]=16          [4,7]=23
    /      \          /      \
 [0,1]=7 [2,3]=9  [4,5]=12 [6,7]=11
  / \     / \      / \      / \
 5   2   8   1    9   3    7   4
```

A query for indices 2 through 5 uses the stored nodes for 2 through 3 and 4 through 5. Their totals, 9 and 12, give 21. The query stops at those nodes because each is fully covered; it need not visit their leaves.

Only the two ends of a requested range can cut through nodes at each level. Everything between them uses fully covered pieces, which is why a query needs only logarithmically many nodes.

> [!analogy] Real-world analogy: Totals by district
> A delivery service keeps parcel totals for regions, districts and streets.
>
> **How it maps:** A request covering a whole district uses its stored total; only partly covered districts need smaller pieces. Segment-tree nodes similarly summarise nested contiguous ranges.
>
> **Where it stops:** The tree uses fixed binary splits, and its combine must be associative. Geographic districts need not satisfy either rule.

## Key takeaways

- Each node summarises one contiguous range.
- Fully covered pieces combine into the requested range without scanning all elements.

## Further reading
- [Segment trees — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
