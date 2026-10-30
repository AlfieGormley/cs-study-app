---
id: graph-strong-components
title: Strong components with Kosaraju and Tarjan
level: intermediate
minutes: 4
sourceLesson: graph-dfs-applications
summary: Strong connectivity requires reachability in both directions.
---

DFS discovery and finish order were established in earlier units. Here n counts vertices and m counts edges. The recursive examples assume their depth fits Python’s configured recursion limit.

## Strongly connected components

In a directed graph, u and v are **strongly connected** if each can reach the other. A **strongly connected component (SCC)** is a maximal set of mutually reachable vertices.

```
{0,1,2}:  0 -> 1 -> 2 -> 0
{3,4,5}:  3 -> 4 -> 5 -> 3
{6,7}:    6 -> 7 -> 6
between:  2 -> 3,  6 -> 5

condensation (a DAG):
[0,1,2] --> [3,4,5] <-- [6,7]
```

Edges: 0→1, 1→2, 2→0, 2→3, 3→4, 4→5, 5→3, 6→5, 6→7, 7→6. SCCs: **{0, 1, 2}**, **{3, 4, 5}**, **{6, 7}**.

Collapse each SCC to a single vertex and discard internal edges; you get the **condensation**, which is always a DAG. That is why SCCs matter: they turn any directed graph into a DAG of "clusters" you can topologically sort.

### Kosaraju's algorithm

1. DFS the whole graph, recording finish order.
2. Reverse every edge.
3. DFS the reversed graph, taking start vertices in **decreasing** finish time. Each tree found is one SCC.

Why it works: the vertex that finishes last lies in a "source" SCC of the condensation. In the reversed graph that SCC becomes a sink, so a DFS from it cannot leak into other components. Two passes, each **O(n + m)** for n vertices and m edges, and simple to get right.

### Tarjan's algorithm

One DFS pass. Each vertex gets an index `idx` (discovery order) and a `low` value: the smallest index reachable from its subtree using tree edges plus at most one edge to a vertex still on the SCC stack. This separate stack can include vertices whose recursive calls have already returned; it is not the grey recursion stack. Vertices are pushed onto a separate stack as discovered. When a vertex finishes with `low[u] == idx[u]`, it is the root of an SCC: pop the stack down to u. In symbols, the code updates `low` like this:

```formula reference
low(u) = min(idx(u), low(c), idx(w))
where
u: the vertex DFS is currently finishing
idx(u): u's discovery number: 0 for the first vertex DFS reaches, 1 for the next, and so on
c: any child of u in the DFS tree (reached by a tree edge)
low(c): the low value already computed for that child
w: any vertex still on the SCC stack that u has a direct edge to
low(u): the smallest discovery number u's subtree can reach this way
min(…): the smallest of the values listed, taken over every child c and every such w
In words: a vertex's low value is the discovery number of the earliest vertex that it or its descendants can jump back to while staying inside an unfinished component.
```

If even that earliest reachable vertex is u itself (the equality tested in the code), nothing in u's subtree escapes to an older open vertex, so u and everything above it on the stack form one SCC.

```python
def tarjan(n, adj):
    idx = [None] * n
    low = [0] * n
    on_stack = [False] * n
    stack, sccs = [], []
    counter = 0

    def visit(u):
        nonlocal counter
        idx[u] = low[u] = counter
        counter += 1
        stack.append(u)
        # SCC membership stays pending on
        # return.
        on_stack[u] = True
        for v in adj[u]:
            if idx[v] is None:
                visit(v)
                # Propagate the child
                # subtree’s escape.
                low[u] = min(low[u], low[v])
            # Only unfinished components can
            # link back.
            elif on_stack[v]:
                # A direct open edge uses
                # discovery index.
                low[u] = min(low[u], idx[v])
        if low[u] == idx[u]:  # root
            comp = []
            while True:
                w = stack.pop()
                # This component has now
                # been finalised.
                on_stack[w] = False
                comp.append(w)
                if w == u:
                    break
            sccs.append(comp)

    for u in range(n):
        if idx[u] is None:
            visit(u)
    return sccs
```

On the example it returns [5, 4, 3], then [2, 1, 0], then [7, 6]. Tarjan emits SCCs in **reverse topological order** of the condensation: sinks first. Also O(n + m) for n vertices and m edges, one pass, no reversed graph, but the `on_stack` check is easy to get wrong.

> [!tip] Uses of SCCs
> **2-SAT** is solved by building an implication graph and checking that no variable sits in the same SCC as its negation. Compilers find mutually recursive functions. Garbage collectors and dependency analysers find reference cycles.

## Key takeaways
- Strong connectivity requires reachability in both directions.
- Condensation contracts mutually reachable groups into a DAG.
- Tarjan’s SCC stack differs from the recursion stack.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.2 Directed graphs](https://algs4.cs.princeton.edu/42digraph/)
- [Strongly connected components — cp-algorithms](https://cp-algorithms.com/graph/strongly-connected-components.html)
- [Strongly connected component — Wikipedia](https://en.wikipedia.org/wiki/Strongly_connected_component)
- [Tarjan's strongly connected components algorithm — Wikipedia](https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm)
