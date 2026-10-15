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

The rank rule for merging two roots fits in two lines:

```formula
r_new = r + 1   if r_a = r_b = r
r_new = max(r_a, r_b)   otherwise
where
r_a: the rank of the first root being merged, a whole number starting at 0
r_b: the rank of the second root being merged
r: the shared rank, when the two Union-Find ranks coincide
r_new: the rank of the merged tree's root
max(r_a, r_b): the larger of the two ranks
In words: two trees of equal rank make a tree one rank higher; otherwise the lower-rank root goes under the higher one and no rank changes.
```

So two rank-2 trees make a rank-3 tree, while a rank-1 tree hung under a rank-3 root leaves the rank at 3.

For union by size, an element only gets deeper when its tree is merged under a tree at least as big. Each time that happens, the size of the tree containing it at least doubles. A tree can never hold more than all n elements, which caps how many doublings there can be:

```formula
2^d ≤ n
d ≤ log_2(n)
d ≤ log_2(1,000,000) ≈ 19.9
where
d: the depth of an element: how many parent steps it is below its root
n: the total number of elements in the structure
2^d: d copies of 2 multiplied together; the smallest its tree's size can be after it has been pushed down d times
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
≤: is at most
≈: approximately equal to
In words: every step deeper at least doubles the element's tree, and a tree cannot outgrow n elements, so no element is ever more than log_2(n) levels deep.
```

With a million elements, no `find` walks more than 19 parent steps. That makes `find` O(log n) in the worst case: its cost grows in proportion to the logarithm of n. The bound assumes every union goes through the size rule; a single careless `parent[b] = a` breaks it.

For union by rank, a separate induction (a proof that the claim holds for rank 0 and stays true after every merge) bounds the tree size by its rank. Rank rises only when two equal-rank roots merge, which at least doubles the smaller one:

```formula
s(x) ≥ 2^{r(x)}
r(x) ≤ ⌊log_2(n)⌋
h(x) ≤ r(x)
r(x) ≤ ⌊log_2(1000)⌋ = 9
where
x: any root in the forest
r(x): the rank of root x, a whole number starting at 0
s(x): the number of elements in x's tree
2^{r(x)}: 2 multiplied by itself r(x) times
h(x): the height of x's tree: the longest path of parent steps from an element up to x
n: the total number of elements
log_2(n): the base-2 logarithm of n
⌊ ⌋: floor: round down to the nearest whole number
≥: is at least
≤: is at most
In words: a root of rank r holds at least 2^r elements, so with n elements no rank, and so no tree height, can exceed log_2(n) rounded down.
```

For a thousand elements, the base-two logarithm is about 9.97, so the card’s floor bound limits every rank to nine. Parent ranks strictly increase on every path up the tree, which is why the height can be no larger than the root's rank.

Size is often more useful in practice, because you get the group sizes for free ("how big is the largest friend circle?").

## Key takeaways

- Attach smaller trees under larger ones to limit depth.
- Rank grows only when equal-rank roots merge and remains an upper bound after compression.

## Further reading
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [Disjoint Set Union — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Ackermann function — Wikipedia](https://en.wikipedia.org/wiki/Ackermann_function)
