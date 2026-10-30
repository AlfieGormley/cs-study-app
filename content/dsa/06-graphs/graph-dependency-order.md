---
id: graph-dependency-order
title: Ordering dependencies with Kahn and DFS
level: intermediate
minutes: 3
sourceLesson: graph-dfs-applications
summary: Orient prerequisite edges consistently.
---

A DAG is a directed graph with no cycle. Here n counts vertices and m counts edges. DFS colour-based cycle detection is an earlier prerequisite; recursion-depth limits apply to the DFS implementation below.

## Topological sort

A **topological order** of a DAG lists the vertices so that every edge u→v has u before v. For prerequisites, orient each edge from prerequisite to dependent: socks before shoes, shirt before tie. If edges instead point from a target to its dependencies, use reverse topological order. It exists **if and only if** the graph has no directed cycle, and there may be many valid orders.

Example DAG (A→C, B→C, B→D, C→E, D→E):

```
A ---> C ---> E
      ^      ^
     /      /
B ---> D ---
```

### Kahn's algorithm (BFS-style)

Repeatedly output a vertex with no remaining incoming edges, then delete its outgoing edges.

```python
from collections import deque

def kahn(n, adj):
    indeg = [0] * n
    for u in range(n):
        for v in adj[u]:
            indeg[v] += 1
    q = deque(u for u in range(n)
              if indeg[u] == 0)
    order = []
    while q:
        # FIFO preserves the order in which
        # tasks became ready.
        u = q.popleft()
        # Record actual processing order.
        order.append(u)
        for v in adj[u]:
            # A completed prerequisite is
            # removed.
            indeg[v] -= 1
            # This vertex is ready to be
            # emitted.
            if indeg[v] == 0:
                q.append(v)
    if len(order) < n:
        return None  # cycle
    return order
```

On the example: in-degrees A0, B0, C2, D1, E2. The queue starts [A, B]. Output A (C→1), B (C→0, D→0), C (E→1), D (E→0), E. Order: **A, B, C, D, E**.

If a cycle exists, its vertices never reach in-degree 0, so the output is short. That makes Kahn's a cycle detector for free. Replace the queue with a min-heap to get the lexicographically smallest order.

> [!analogy] Real-world analogy: planning a degree course by prerequisites
> Each term a student may take any course whose prerequisites they have all passed. Passing a course may unlock others, which join the list of courses available next.
>
> **How it maps:** a course is a vertex, "A is a prerequisite of B" is an edge A→B, and a course's number of unpassed prerequisites is its in-degree. The "can take now" list is Kahn's queue, and passing a course is outputting it and decrementing its dependants' counts.
>
> **Where it stops:** a student takes several courses at once and may skip some. Kahn's outputs one vertex at a time and must output every vertex. And if two courses each list the other as a prerequisite, a real university would fix the rules; Kahn's simply never frees either one, which is exactly how it reveals the cycle.

### DFS-based

Run DFS and record each vertex when it **finishes**. A vertex finishes only after everything it points to has finished, so reversing the finish order puts every vertex before every vertex it has an edge to.

```python
def topo_dfs(n, adj):
    seen, post = [False] * n, []

    def visit(u):
        seen[u] = True
        for v in adj[u]:
            if not seen[v]:
                visit(v)
        post.append(u)  # successors done

    for u in range(n):
        if not seen[u]:
            visit(u)
    # Successors finished before their
    # users.
    return post[::-1]
```

On the example (starting from A): finish order E, C, A, D, B. Reversed: **B, D, A, C, E**. Different from Kahn's, and equally valid. (This version assumes a DAG; combine it with the grey check to detect cycles.)

Both run in **O(n + m)** for n vertices and m edges.

| | Kahn's | DFS-based |
|---|---|---|
| Style | Queue, in-degrees | Recursion, finish order |
| Cycle check | Built in | Needs grey check |
| Parallelism | Shows ready tasks | No |
| Recursion | None | Deep on long chains |

> [!example] Where it is used
> GNU Make, Bazel and Gradle order build steps topologically. Package managers order installs. Acyclic spreadsheet formulas can be recalculated in dependency order; circular formulas must be reported as errors or handled by an explicitly supported iterative calculation mode. Python ships `graphlib.TopologicalSorter`, a Kahn-style sorter whose `get_ready()` returns every task that can currently run in parallel.

## Key takeaways
- Orient prerequisite edges consistently.
- Kahn detects a cycle when it cannot output every vertex.
- Reverse DFS finish order is valid only after establishing acyclicity.

## Further reading
- [Python docs: graphlib](https://docs.python.org/3/library/graphlib.html)
- [Topological sorting — Wikipedia](https://en.wikipedia.org/wiki/Topological_sorting)
