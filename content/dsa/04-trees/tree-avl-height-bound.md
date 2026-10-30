---
id: tree-avl-height-bound
title: Minimum AVL nodes and the height bound
level: intermediate
minutes: 4
sourceLesson: tree-balanced
summary: The sparsest allowed children differ in height by one.
---

Start with the distinct-key BST ordering from the previous units. A rotation must keep the same sorted in-order sequence while changing local links. Here n counts stored keys and h measures real-node height in edges; empty subtrees have height minus one unless a NIL-path convention is explicitly given. Height bounds assume constant-cost key comparisons, rather than measuring application latency.

## Why the AVL rule guarantees O(log n)

The AVL rule only says each node's two subtree heights may differ by one. Why does such a local rule stop the whole tree growing tall? Turn the question round: what is the **fewest** nodes an AVL tree of a given height can have?

The sparsest AVL tree of height h is as lopsided as the rule allows at every node: a root, one subtree of height h − 1 and the other of height h − 2, each of those as sparse as possible in turn. So the minimum node count for each height is the previous two minimums added together, plus one for the root:

| Height (edges) | Fewest nodes |
|---|---|
| 0 | 1 |
| 1 | 2 |
| 2 | 4 |
| 3 | 7 |
| 4 | 12 |
| 5 | 20 |
| 6 | 33 |

Adding the previous two terms is how Fibonacci numbers grow, and indeed each count is one less than a Fibonacci number. Fibonacci numbers grow by about 1.618 times per step, so even the sparsest AVL tree needs **exponentially** more nodes for every extra level. Turned round, the height can only grow logarithmically with the node count:

```formula reference
N(h) = N(h − 1) + N(h − 2) + 1
h_max ≈ 1.44 log_2(n)
where
h: the height of the AVL tree, in edges
N(h): the smallest number of nodes an AVL tree of height h can have; N(0) = 1 and N(1) = 2
h_max: the greatest height an AVL tree with n nodes can have, for large n
n: the number of nodes (keys) in the tree
log_2(n): the base-2 logarithm of n: how many times you can halve n before reaching 1
≈: approximately equal to (a leading-term approximation for large n)
In words: the sparsest AVL tree of each height is a root over the two previous sparsest trees, so node counts grow like Fibonacci numbers and the worst-case height is about 1.44 times the best possible.
```

For a million keys, the exact minimum counts show an AVL tree can have height at most 27 edges (height 28 would need 1,346,268 nodes), against 19 for a complete tree. That is the hard guarantee: whatever order a million keys arrive in, a search visits at most 28 nodes, and inserts and deletes repair along a path no longer than that.

The 1.44 factor is a large-tree approximation; for an exact finite limit, use the minimum counts, as above.

## Key takeaways
- The sparsest allowed children differ in height by one.
- Minimum node counts obey a Fibonacci-related recurrence.
- Use exact counts when deciding a finite maximum height.

## Further reading
- [AVL tree — Wikipedia](https://en.wikipedia.org/wiki/AVL_tree)
- [AVL tree visualisation — USF](https://www.cs.usfca.edu/~galles/visualization/AVLtree.html)
