---
id: tree-bottom-up-heapify
title: Bottom-up heapify and heapsort
level: intermediate
minutes: 5
sourceLesson: tree-heaps
summary: Build downward from the last internal node.
---

Use the complete-tree array layout introduced earlier. The root is array slot zero; absent child positions lie beyond the occupied prefix. Here n counts binary heap entries and comparisons have constant cost. A valid min-heap makes each parent no greater than its children, without ordering siblings. Array allocation and returned output require their own cost accounting.

## Heapify in O(n)

Given n unsorted items, you could push them one at a time. Each push can climb the full height of the heap, so in the worst case (for example, pushing items in descending order into a min-heap) that is O(n log n): up to about 19 swaps for each of a million items. There is a faster way. Treat the array as a complete tree already, and sift down every **non-leaf** from the bottom up:

Use the sift_down helper from the preceding unit to execute heapify. Both operate in place on a list of comparable values; heapify does not return a new sorted list.

```python
def heapify(a):
    n = len(a)
    # Repair children before their parents.
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
```

Trace on `[9, 4, 7, 1, 8, 2, 6, 3]` (8 items, so start at index 3):

```text-output
i=3 (1): children 3      no swap
i=2 (7): children 2, 6   swap with 2
i=1 (4): children 1, 8   swap with 1,
         then 4 vs 3     swap with 3
i=0 (9): children 1, 2   swap with 1,
         9 vs 3, 8       swap with 3,
         9 vs 4          swap with 4

result: [1, 3, 2, 4, 8, 7, 6, 9]
```

### Why is that O(n)?

The cost of sifting down a node is at most its **node height**, and most nodes have tiny heights. In a complete tree, half the nodes are leaves and never move. Of the rest, about a quarter of all nodes sit just above the leaves and can move down at most one level, an eighth at most two levels, and so on. Lots of short moves at the bottom and a few long ones at the top add up to fewer swaps than there are items:

```formula reference
S < n(1/2 + 1/4 + 1/8 + …) = n
where
S: the total number of swaps bottom-up heapify makes
n: the number of items
1/2, 1/4, 1/8: at most these fractions of the n nodes can move down at least one, two and three levels
…: "and so on": the fractions keep halving
In words: half the nodes can move down at least one level, a quarter at least two, an eighth at least three, and those halving counts add up to less than n swaps.
```

The trace above made 0 + 1 + 2 + 3 = 6 swaps for 8 items. For this sift-down, comparisons are bounded by about twice the item count (at most two child comparisons per level a node can move, including the final level where no swap is needed). Pushing one at a time is slower because new items arrive at the *bottom*, the level with the most nodes, and each may climb the full height.

The intuition: sift-down costs are cheap where nodes are plentiful (the bottom) and expensive only where they are rare (the top). Sift-up is the reverse.

### Heapsort

Heapify, then repeatedly swap the root with the last item and sift down over a shrinking prefix. That is **heapsort**: for n items, O(n log n) worst case (n pops, each sifting down at most the binary heap's height), O(1) extra memory, but not stable and with poor cache locality (child positions roughly double their parent position), which can affect practical performance. One use is the worst-case fallback inside **introsort** (the usual implementation of C++ `std::sort`), which switches to heapsort if quicksort recurses too deeply.

## Key takeaways
- Build downward from the last internal node.
- Most nodes can move only a few levels, making bottom-up heapify linear.
- Heapsort repeatedly repairs a shrinking binary heap and is not stable.

## Further reading
- [Priority Queues — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/24pq/)
