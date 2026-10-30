---
id: graph-directed-dfs-colours
title: DFS colours and directed cycles
level: intermediate
minutes: 3
sourceLesson: graph-dfs-applications
summary: Grey vertices remain on the active recursion path.
---

The traversal units used DFS just to visit things. Its real power is the **structure** it leaves behind: which vertices are still "open" on the stack, and the order in which vertices finish. That structure answers questions such as "is there a circular dependency?", "in what order should I build these modules?" and "which pages all link to each other?".

Throughout this lesson, n is the number of vertices and m the number of edges, and O(…) is Big O notation: how the running time grows with the graph's size, ignoring constant factors. Every algorithm here runs in O(n + m), the same as one traversal.

## The three colours

Give every vertex a colour during DFS:

- **White**: not yet discovered.
- **Grey**: discovered, still on the recursion stack (we are somewhere inside its subtree).
- **Black**: finished; all its outgoing edges have been examined and all recursive calls it made have returned.

When DFS at u looks at an edge u→v, the colour of v classifies the edge:

| v is | Edge type | Meaning |
|---|---|---|
| White | Tree edge | DFS goes to v |
| Grey | Back edge | v is u or an ancestor of u |
| Black | Forward or cross | Already done |

A back edge points from a vertex to one of its own ancestors, closing a loop. That gives the key theorem: **a directed graph has a cycle if and only if a DFS covering all vertices finds a back edge.**

> [!analogy] Real-world analogy: following "see also" references with your fingers in the pages
> You look something up in a printed encyclopaedia, follow a "see also" reference, then another, keeping a finger in every page you have not finished with. When you finish a page you take your finger out.
>
> **How it maps:** a page you have never opened is white, a page holding a finger is grey (on the current recursion path), and a finished page is black. A reference to a page that still holds a finger means you have come round in a circle: a back edge. A reference to a finished page just means two trails met.
>
> **Where it stops:** you might happily reread a finished page. DFS never re-enters a black vertex, and it explores every reference on a page before finishing it, so the colours record exactly where the search is, not what you happen to remember.

## Cycle detection in directed graphs

```python
def has_cycle(n, adj):
    WHITE, GREY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def visit(u):
        # Keep u open until descendants
        # finish.
        color[u] = GREY
        for v in adj[u]:
            if color[v] == GREY:
                return True  # back edge
            if color[v] == WHITE:
                if visit(v):
                    return True
        # The active path no longer contains
        # u.
        color[u] = BLACK
        return False

    for u in range(n):
        if color[u] == WHITE and visit(u):
            return True
    return False
```

### Why "visited" is not enough

A plain visited set reports a cycle in this DAG, which has none:

```
    0
   / \
  v   v
  1   2
   \ /
    v
    3
```

DFS goes 0→1→3, finishes, then 0→2 finds 3 already visited. But 3 is black (finished), not grey. It is a cross edge, not a loop.

> [!warning] Grey, not visited
> Only grey means "on my current path". Checking `v in visited` instead of `color[v] == GREY` gives false positives on any DAG where two paths reconverge, such as the diamond above.

## Key takeaways
- Grey vertices remain on the active recursion path.
- A black reconvergence is not a directed cycle.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.2 Directed graphs](https://algs4.cs.princeton.edu/42digraph/)
- [Depth-first search — Wikipedia](https://en.wikipedia.org/wiki/Depth-first_search)
