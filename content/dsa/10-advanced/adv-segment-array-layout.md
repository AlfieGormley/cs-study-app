---
id: adv-segment-array-layout
title: Laying out a segment tree in an array
level: advanced
minutes: 2
summary: Use one-based child indices in a flat array.
sourceLesson: adv-segment-trees
---

Here n is the non-empty input array’s length. Big-O bounds count constant-time combines of constant-size summaries on word-sized values.

## Storing it in an array

Like a binary heap, the recursive tree lives in a flat array with its root at index one. In code, the children of node `v` are `2 * v` and `2 * v + 1`; no child pointers are stored.

When the element count is a power of two, the tree fills its levels neatly. Other lengths leave gaps in this numbering. Allocating `4 * n` slots is a safe bound for a non-empty input of n elements; it does not mean the tree contains four nodes per element.

To see why the bound is safe, round the leaf capacity up to a power of two. That increases the capacity by less than a factor of two; a full binary tree needs fewer than twice that many nodes. The spare slot at index zero also fits. With eight elements, sixteen slots suffice. With six elements, recursive midpoint splitting reaches index thirteen, so twelve slots would be too few.

## Key takeaways

- Use one-based child indices in a flat array.
- Round the leaf capacity up to a power of two when bounding allocated slots.

## Further reading
- [Segment trees — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
