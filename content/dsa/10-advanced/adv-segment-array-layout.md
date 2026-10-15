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

Like a binary heap, the tree lives in a flat array, with the root at index 1. The children of a node are found by arithmetic, so no pointers are stored:

```formula
left(v) = 2v
right(v) = 2v + 1
left(3) = 6,   right(3) = 7
where
v: the array index of a node; the root is 1
left(v): the index of v's left child
right(v): the index of v's right child
In words: double a node's index to find its left child, and add one more for its right child.
```

How big must the array be? Each level can hold twice as many nodes as the one above, and the leaves must fit on the bottom level:

```formula
h = ⌈log_2(n)⌉
slots ≤ 2 × 2^h < 4n   for n ≥ 1
n = 5:  h = 3,  2 × 2^3 = 16 < 20
where
n: the number of elements in the array
h: the height of the tree: the number of levels below the root
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
⌈ ⌉: ceiling: round up to the nearest whole number
2^h: h copies of 2 multiplied together, the number of slots on the bottom level
slots: the highest array index a node can use, plus one
≤: is at most
<: is less than
In words: rounding n up to the next power of two at most doubles it, and a full tree on that many leaves needs twice as many slots, so 4n is always enough.
```

That is why implementations allocate `4 * n`. When n is already a power of two, the bottom level holds exactly n leaves and 2n slots are enough.

## Key takeaways

- Use one-based child indices in a flat array.
- Round the leaf capacity up to a power of two when bounding allocated slots.

## Further reading
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
- [Segment tree, the interval-stabbing version — Wikipedia](https://en.wikipedia.org/wiki/Segment_tree)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
