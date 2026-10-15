---
id: adv-lazy-range-tags
title: Lazy range updates and deferred tags
level: advanced
minutes: 2
summary: A fully covered node updates its summary immediately.
sourceLesson: adv-segment-trees
---

Here n is the non-empty input array’s length. Big-O bounds count constant-time combines of constant-size summaries on word-sized values.

## Lazy propagation: updating whole ranges

Now add a third request: "add `x` to every element of `a[l..r]`". Doing it as one point update per element is slow for a big range:

```formula
c_naive ≤ (r − l + 1)(⌈log_2(n)⌉ + 1)
c_naive ≤ 10^6 × 21 = 21,000,000
where
c_naive: an upper bound on the number of nodes touched when a range add is done as separate point updates
l, r: the first and last index of the range, inclusive
r − l + 1: the number of elements in the range
n: the number of elements in the array; the example uses a whole-array add with n = 10^6
log_2(n): the base-2 logarithm of n
≤: is at most
⌈ ⌉: ceiling: round up to the nearest whole number
In words: each element in the range costs a full root-to-leaf update, so a range covering most of the array costs O(n log n).
```

**Lazy propagation** applies a range update the same way a query reads a range: stop at fully covered nodes. At such a node, update its stored sum and leave a **pending tag** saying "my children still owe `+x`":

```formula
S_new = S_old + x(hi − lo + 1)
z_new = z_old + x
S_new = 0 + 5 × (3 − 0 + 1) = 20
where
lo, hi: the first and last array index covered by a node whose whole range lies inside the update range
S_old: that node's stored sum before the update
S_new: that node's stored sum after the update
z_old: the node's pending tag (the amount its children still owe) before the update
z_new: the node's pending tag after the update
x: the amount added to every element of the range
In words: adding x to every element of a node's range raises its sum by x times the number of elements, and the tag remembers to pass x on to the children later.
```

The third line describes a fully covered node spanning indices zero through three, initially holding zeros. The next unit traces the complete tree update. The tag is pushed down to the children only when some later operation needs to go below that node.

## Key takeaways

- A fully covered node updates its summary immediately.
- A pending tag records work still owed to the children.

## Further reading
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
- [Segment tree, the interval-stabbing version — Wikipedia](https://en.wikipedia.org/wiki/Segment_tree)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
