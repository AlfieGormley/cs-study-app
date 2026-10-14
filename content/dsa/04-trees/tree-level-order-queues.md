---
id: tree-level-order-queues
title: Level order and queue width
level: basic
minutes: 4
sourceLesson: tree-traversals
summary: A deque processes the shallowest pending nodes first.
---

Use the binary Node representation introduced earlier: each node has a value and optional left and right children. Assume finite acyclic trees without shared nodes or concurrent mutation. Here n counts nodes and h is the root height in edges. Constant-cost processing at each visited node is assumed; returned output is separate from working memory.

## Breadth-first: level-order

Level-order visits nodes by depth: the root, then all depth-1 nodes left to right, and so on. It uses a **queue** instead of a stack: first in, first out, so nodes are processed in the order they were discovered.

```python
from collections import deque

def level_order(root):
    if root is None:
        return []
    levels, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):
            node = q.popleft()
            # This round visits one fixed
            # depth.
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        levels.append(level)
    return levels

# [['F'], ['B', 'G'],
#  ['A', 'D', 'I'], ['C', 'E', 'H']]
```

Taking `len(q)` at the start of each round processes exactly one level per round. That is the hook for a whole family of problems: right-side view (last of each level), zigzag order, average per level, minimum depth.

> [!warning] Use a deque, not a list
> `list.pop(0)` shifts every remaining element, so it is O(n) in the n items still in the list, and can make BFS quadratic (work growing with the square of the node count) on wide trees. `deque.popleft()` is O(1), a fixed cost.

### Space for BFS

Here n counts tree nodes, h is height in edges, and w is the maximum number of nodes on any level.


The queue can mix the unprocessed part of one level with discovered nodes of the next; its size grows with the tree's **tree width** (the most nodes on any one level), written O(width). A perfect tree is widest at its last level, which holds just over half of all its nodes:

```formula
W = 2^h = (n + 1) / 2
n = 2^(h+1) − 1
W = (15 + 1) / 2 = 8
where
W: the number of nodes on the last (widest) level of a perfect binary tree
h: the height of the tree in edges; the last level is at depth h
n: the total number of nodes in the perfect tree
2^h: h copies of 2 multiplied together
In words: in a perfect binary tree the bottom level holds (n + 1)/2 nodes, just over half the tree, and BFS's queue fills with all of them.
```

A perfect tree of 15 nodes has 8 leaves; one of 1,048,575 nodes has 524,288. So BFS uses O(n) memory on bushy trees, while DFS needs only O(log n) there. On a degenerate chain it is the other way round: the queue never holds more than one node, but recursive DFS needs O(n) frames. Iterative pre-order can keep only one pending node on a chain.

For n nodes:

| Shape | Recursive DFS stack | BFS queue |
|---|---|---|
| Balanced | O(log n) | O(n) |
| Chain | O(n) | O(1) |

BFS has one big advantage: it reaches shallow nodes first. To find the **minimum depth** of a tree, or the nearest node satisfying a condition, BFS can stop as soon as it finds one, while DFS might explore a huge deep subtree first.

## Key takeaways
- A deque processes the shallowest pending nodes first.
- Snapshot the queue length before processing a level.
- Breadth-first working space can be large on wide trees.

## Further reading
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [collections.deque — Python docs](https://docs.python.org/3/library/collections.html)
