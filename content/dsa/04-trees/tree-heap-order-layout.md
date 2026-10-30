---
id: tree-heap-order-layout
title: Heap order and implicit array layout
level: intermediate
minutes: 4
sourceLesson: tree-heaps
summary: A binary heap combines complete shape with parent-child priority order.
---

Many problems only ever need the **smallest** (or largest) item: the next job to run, the nearest unvisited city in Dijkstra's algorithm, the earliest timer to fire, the next event in a simulation. A BST can do that, but it keeps far more order than you need.

A **priority queue** is the abstract data type for this job: `push(item)`, `pop_min()` and `peek()`. The standard implementation is the **binary heap**. For a binary heap of n items it gives O(log n) push and pop (work growing with the logarithm of n, about 20 steps for a million items) and O(1) peek (a fixed cost), stored with implicit parent/child indices rather than tree-link pointers. Python lists still store references to their elements. Costs assume constant-time comparisons; dynamic-array resizing makes push/pop bounds amortized when allocation costs are included.

## The binary heap property

A binary **min-heap** is a binary tree with two rules:

1. **Shape:** it is a **complete binary tree** (every level full except possibly the last, which fills from the left).
2. **Order:** every parent is **less than or equal to** its children.

So the minimum is always at the root. A **max-heap** flips the order rule.

```
          1
        /   \
       3     2
      / \   / \
     4   8 7   6
    /
   9
```

Notice how much weaker this is than a BST. Siblings are unordered (3 is left of 2), and 4 sits deep on the left while 2 is near the top on the right. The binary heap only promises that every path from the root downward is sorted. That weaker promise is what makes it cheap to maintain.

> [!analogy] Real-world analogy: a chain of command
> In a strict chain of command, every officer outranks the people directly under them, so the most senior person is always at the top. But two officers in different units are never compared, and someone low down in one unit may hold a higher rank than someone near the top of another.
>
> **How it maps:** "outranks" is the heap order (for a min-heap, "smaller key ranks higher"), the top officer is the root and the minimum, and units are subtrees. Only each chain from the top downwards is ordered; siblings and cousins are not.
>
> **Where it stops:** a real chain of command rarely changes shape. A heap reshuffles on every push and pop, and it must always stay a complete tree, filling each level from the left.

## The array layout

Because the tree is complete, it packs into an array in level order with no gaps (the tree-structure units):

```
idx:  0  1  2  3  4  5  6  7
val: [1, 3, 2, 4, 8, 7, 6, 9]
```

The parent and children of any slot are found by arithmetic on its index:

```formula essential
i_parent = ⌊(i − 1) / 2⌋
i_left = 2i + 1
i_right = 2i + 2
where
i: the index (0-based position) of an item in the array; i_parent applies only when i > 0
i_parent: the index of that item's parent
i_left: the index of its left child, if that index is less than the heap size
i_right: the index of its right child, if that index is less than the heap size
⌊ ⌋: floor: round down to a whole number, so ⌊2.5⌋ = 2
In words: the children of slot i are at 2i + 1 and 2i + 2, and the parent is at (i − 1) halved and rounded down.
```

So the 3 at index 1 has children at indices 3 and 4 (4 and 8), and the 9 at index 7 has its parent at index 3 (the 4). In the Python code below, the parent index is `(i - 1) // 2`, where `//` divides and rounds down.

Avoiding explicit tree links saves their storage. The array of slots is contiguous, though referenced payload objects need not be; actual cache behaviour depends on layout and access patterns.

The second half of the array, rounded up, is all **leaves**. A slot has a child only if its left-child index is still inside the array, and that stops being true halfway along. In the 8-item example, indices 4 to 7 (values 8, 7, 6 and 9) are leaves: index 4's left child would be at 9, past the end. This fact matters later: building a heap only needs to repair the first half of the array, and with distinct keys the largest key in a min-heap must be somewhere in the leaf half.

```formula reference
⌊n / 2⌋ ≤ i ≤ n − 1
where
n: the number of items in the heap (at least 1)
i: the index of a leaf; every index in this range is a leaf, and no other index is
⌊ ⌋: floor: round down to a whole number
≤: is at most
In words: in an array heap, the leaves start halfway along (rounded down) and run to the end.
```

## Key takeaways
- A binary heap combines complete shape with parent-child priority order.
- Array indices replace explicit links.
- Binary heap order does not sort siblings or the entire array.

## Further reading
- [Binary heap — Wikipedia](https://en.wikipedia.org/wiki/Binary_heap)
- [Priority Queues — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/24pq/)
