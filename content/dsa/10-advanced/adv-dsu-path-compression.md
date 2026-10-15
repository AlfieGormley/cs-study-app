---
id: adv-dsu-path-compression
title: Path compression and the DSU implementation
level: intermediate
minutes: 2
summary: Find the root, then repoint the visited path at it.
sourceLesson: adv-union-find
---

## Fix 2: path compression

`find` already walks from `x` to the root. While doing so, **repoint every node on the path directly at the root**. Without an intervening union, the next `find` on a non-root node on that path takes one parent step.

```
before find(4)        after find(4)
     0                     0
     |                  / | | \
     1                 1  2 3  4
     |
     2
     |
     3
     |
     4
```

Variants such as **path halving** (point each node at its grandparent as you go) achieve the same bounds in a single pass.

## The full structure

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.count = n   # number of sets

    def find(self, x):
        root = x
        while self.parent[root] != root:
            # Follow ancestors to the
            # representative.
            root = self.parent[root]
        # second pass: compress the path
        while self.parent[x] != root:
            # Save the old link before
            # overwriting it.
            nxt = self.parent[x]
            self.parent[x] = root
            x = nxt
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False   # already joined
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        # smaller tree goes under bigger
        # Join roots; never detach a non-
        # root.
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.count -= 1
        return True
```

> [!tip] Iterative find in Python
> The textbook recursive `find` (`parent[x] = find(parent[x])`) is elegant, but an unbalanced variant can create a chain exceeding the interpreter's recursion limit. Union by size or rank already prevents such linear-depth chains. The two-pass loop above has no such limit.

Note that `union` returns whether a merge actually happened. That boolean is what most applications use.

## Key takeaways

- Find the root, then repoint the visited path at it.
- Union returns false when its two arguments already share a root.

## Further reading
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [Disjoint Set Union — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Ackermann function — Wikipedia](https://en.wikipedia.org/wiki/Ackermann_function)
