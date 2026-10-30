---
id: tree-binary-counts
title: Binary nodes and counting bounds
level: basic
minutes: 4
sourceLesson: tree-basics
summary: Left and right child positions are distinct, even with only one child.
---

Use the rooted-tree vocabulary from the earlier unit. The linked examples below assume a finite acyclic tree without shared child nodes. Count height and depth in edges, not nodes. A path ends at a leaf only when that node has no children. When an example uses n, it means the number of stored nodes.

## Binary trees

A **binary tree** is a tree where every node has at most two children, called **left** and **right**. The order matters: a node with only a left child is a different tree from one with only a right child.

Binary trees are the workhorse of this module. Binary search trees, AVL trees, red-black trees and binary heaps have binary shape. Other priority queue structures, such as d-ary heaps, allow higher arity, and expression trees can have unary or many-operand nodes.

Use the Node representation from the depth-and-height unit; the four-node example there also illustrates these child-slot counts.


Two useful counting facts.

### Empty child slots

Every node has two child slots, and every edge fills exactly one of them. A tree with n nodes has n − 1 edges, so the remaining slots, one more than the number of nodes, are empty (None):

```formula reference
S = 2n − (n − 1) = n + 1
where
S: the number of empty (None) child slots in a nonempty binary tree
n: the number of nodes
In words: a binary tree always has one more empty child slot than it has nodes.
```

In the four-node sample from the depth-and-height unit, node 4 has two empty slots, node 3 has two and node 2 has one: 5 in total. This is why serialising a tree with a marker for every empty child writes one more marker than nodes (the common-problem units).

### How short a tree can be

Each level can hold at most twice as many nodes as the level above it: 1 root, then at most 2, 4, 8 and so on. So every extra level roughly doubles how many nodes can fit, and the shortest possible tree grows only logarithmically. At the other extreme, nothing stops a badly shaped tree from being a single chain, one node per level:

```formula essential
h_min = ⌊log_2(n)⌋
h_max = n − 1
where
n: the number of nodes in the tree, at least 1
h_min: the smallest possible height, in edges, reached when every level except the last is full
h_max: the largest possible height, in edges, reached by a chain where every node has at most one child
log_2(n): the base-2 logarithm of n: how many times you can halve n before reaching 1, so log_2(8) = 3
⌊ ⌋: floor: round down to a whole number
In words: n nodes can be packed into a height of about log_2(n) edges, or strung out to a height of n − 1 edges; the shape decides which.
```

For a million nodes, that is a height somewhere between 19 and 999,999. Height 3 fits at most 15 nodes, height 9 up to 1,023, height 19 just over a million. Doubling the node count adds only one level to the shortest possible tree.

That gap is why "O(log n)" keeps appearing in this module. Operations that walk one root-to-leaf path take time proportional to the height, so a well-shaped tree reaches any node in about 20 steps per million nodes, while a chain behaves like a linked list.

> [!analogy] Real-world analogy: a phone tree for news
> A club spreads news by phone. The organiser calls two people, each of them calls two more, and so on. With everyone passing it on, about 20 rounds of calls reach a million members. If instead each member calls just one other person, a million members need almost a million rounds.
>
> **How it maps:** each member is a node, each call is an edge and each round is one level. The two-calls-each scheme is a well-filled binary tree with logarithmic height; the one-call-each scheme is a chain with height one less than the number of nodes.
>
> **Where it stops:** a phone tree's job is to reach every member, so every call gets made. A tree lookup follows a single path from the root, one node per level, and skips everything else, so its cost is the height, not the total number of calls. Real callers also phone people one after another, so rounds are never perfectly simultaneous.

## Key takeaways
- Left and right child positions are distinct, even with only one child.
- Count empty slots by subtracting occupied edges from child positions.
- Doubling each level gives the shortest possible height for a node count: about log₂ n levels.
- A chain is the tallest possible shape, so shape, not node count, decides whether paths are short.

## Further reading
- [Binary tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_tree)
