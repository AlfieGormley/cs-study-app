---
id: tree-downward-path-sums
title: Root-to-leaf and downward prefix sums
level: advanced
minutes: 4
sourceLesson: tree-problems
summary: A root-to-leaf test must verify that its endpoint is a leaf.
---

Use the binary Node with val, left and right fields introduced earlier. Assume a finite acyclic tree with no shared nodes or concurrent mutation. Throughout this unit n counts nodes and h is the tree height in edges. Recursive examples are limited by Python call depth; arithmetic has unit cost and hash-table operations have expected constant cost. Each example distinguishes working storage from returned output.

## Path sums

Three questions with similar names and different techniques.

### Root-to-leaf sum: pass state down

"Is there a root-to-leaf path summing to target?" Subtract as you descend; check at the leaves.

```python
def has_path_sum(node, target):
    if node is None:
        return False
    # Carry the unmet sum toward the leaves.
    r = target - node.val
    # Only an actual leaf may finish this
    # path.
    if not node.left and not node.right:
        return r == 0
    return (has_path_sum(node.left, r) or
            has_path_sum(node.right, r))
```

The leaf check matters: without it, a node with one child could "succeed" at its empty side, counting a path that does not end at a leaf.

### Any downward path: prefix sums

"How many downward paths (starting anywhere, ending anywhere below) sum to target?" Checking every start node is O(n²) on a chain of n nodes. Instead, borrow the **prefix-sum** trick from arrays. Keep the running total from the root down to each node; a downward segment's sum is then a difference of two running totals:

```formula reference
S = R(v) − R(u)
where
v: the node where the segment ends (the current node)
u: an ancestor of v; the segment runs from just below u down to v
R(v): the running sum: the total of all values from the root down to v, inclusive
R(u): the running sum from the root down to u
S: the sum of the values on the segment below u down to v
In words: the sum of a downward segment is the running total where it ends minus the running total just above where it starts.
```

So a downward segment ending at the current node hits the target exactly when some ancestor's running total equals the current running total minus the target. For example, on the path 10 → 5 → 3 with target 8, the running totals are 10, 15 and 18. At node 3, 18 − 8 = 10 is the running total at the root, so the segment 5 → 3 sums to 8. In the code, `run` is the running total at the current node and `seen` counts the running totals on the current path from the root.

> [!analogy] Real-world analogy: odometer readings on a journey
> On a road trip you note the odometer at every stop. The distance between any two stops is simply the later reading minus the earlier one. To ask "did any stretch of this trip end here and cover exactly 80 km?", you look for an earlier reading that is 80 less than the current one.
>
> **How it maps:** the odometer reading at a stop is the running total from the root, a stretch between stops is a downward segment, and your list of earlier readings is the `seen` map. Turning back to try a different branch means crossing those branch readings off the list, which is the backtrack step.
>
> **Where it stops:** an odometer only goes up. Tree values can be negative or zero, so several ancestors can share the same running total, which is why `seen` counts how many times each total appears rather than just recording it.

```python
from collections import defaultdict

def count_paths(root, target):
    seen = defaultdict(int)
    seen[0] = 1            # empty prefix
    def dfs(node, run):
        if node is None:
            return 0
        run += node.val
        # Matching ancestor prefixes start
        # paths.
        n = seen.get(run - target, 0)
        seen[run] += 1
        n += dfs(node.left, run)
        n += dfs(node.right, run)
        # Remove this prefix
        # before sibling work.
        seen[run] -= 1     # backtrack
        if seen[run] == 0:
            del seen[run]
        return n
    return dfs(root, 0)
```

The **backtrack** line is essential: the map must only contain prefixes on the *current* path, so a node's prefix is removed when the recursion leaves it. Without it, sums from a sibling branch leak in. Removing zero-count entries keeps O(h + 1) distinct active prefixes for a tree of height h; expected time is O(n) for n nodes with constant-cost integer arithmetic and hashing.

## Key takeaways
- A root-to-leaf test must verify that its endpoint is a leaf.
- Prefix differences count segments that start below an ancestor.
- Backtrack prefix counts so sibling branches do not contaminate each other.

## Further reading
- [Tree traversal — Wikipedia](https://en.wikipedia.org/wiki/Tree_traversal)
