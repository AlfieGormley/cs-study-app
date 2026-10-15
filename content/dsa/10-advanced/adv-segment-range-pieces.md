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

On large arrays, many O(n) operations can become expensive. A **segment tree** makes both operations O(log n). For a million elements the difference is stark:

```formula
c_scan = n = 1,000,000
c_tree ≈ log_2(n) ≈ 20
where
n: the number of elements in the array, a million here
c_scan: roughly how many elements one O(n) query or update touches
c_tree: roughly how many tree levels one segment-tree operation walks through
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
≈: approximately equal to
In words: scanning touches every element, while a segment tree only walks down about 20 levels for a million elements.
```

A segment tree does a few nodes of work per level, so the real count is a small multiple of 20, still tens of thousands of times less than a scan. It works for any operation that combines associatively, not just sums.

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

Any range can be assembled from a handful of these precomputed pieces. Writing S(l, r) for the sum of `a[l..r]`:

```formula
S(2, 5) = S(2, 3) + S(4, 5)
S(2, 5) = 9 + 12 = 21
where
S(l, r): the sum of the array elements from index l to index r, both included; the label [l,r]=value in the drawing is S(l, r)
l: the first index of a range
r: the last index of a range
In words: the range 2 to 5 splits into two stored nodes, 2 to 3 and 4 to 5, so adding their two stored sums gives the answer.
```

That is two nodes instead of four elements. For long ranges the saving is enormous: any range needs at most about two nodes per level of the tree.

## Key takeaways

- Each node summarises one contiguous range.
- Fully covered pieces combine into the requested range without scanning all elements.

## Further reading
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
- [Segment tree, the interval-stabbing version — Wikipedia](https://en.wikipedia.org/wiki/Segment_tree)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
