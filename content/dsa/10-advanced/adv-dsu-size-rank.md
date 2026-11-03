---
id: adv-dsu-size-rank
title: Balancing Union-Find by size and rank
level: intermediate
minutes: 4
summary: Attach smaller trees under larger ones to limit depth.
sourceLesson: adv-union-find
---

## Fix 1: union by size or by rank

When merging, **hang the smaller tree under the larger one**. "Smaller" can mean:

- size: number of elements in the tree, or
- **rank**: an upper bound on the tree's height. Every element starts with rank 0.

For rank, attach the lower-rank root under the higher-rank root. If the ranks are equal, choose either root and increase its rank by one. Two rank-two roots therefore produce rank three; adding a singleton to a rank-three root leaves its rank unchanged.

For union by size, an element only gets deeper when its tree joins one at least as big. Its containing tree therefore at least doubles each time it gets deeper. It cannot double indefinitely inside a fixed population: this bounds the depth logarithmically in the number of elements n.

Union by rank has a similar guarantee. A rank increase requires two roots of the same rank, so high ranks require many elements. Parent ranks strictly increase along a path. Rank is an upper bound on height, even after path compression shortens paths without changing ranks.

Both strategies give O(log n) worst-case `find` before compression. The guarantee relies on always joining roots using the chosen rule; linking arbitrary nodes can detach part of a component.

Size is often more useful in practice, because you get the group sizes for free ("how big is the largest friend circle?").

## Key takeaways

- Attach smaller trees under larger ones to limit depth.
- Rank grows only when equal-rank roots merge and remains an upper bound after compression.

## Further reading
- [Disjoint-set unions — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
