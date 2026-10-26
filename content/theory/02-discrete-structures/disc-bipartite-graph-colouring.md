---
id: disc-bipartite-graph-colouring
title: "Bipartite graphs and proper colouring"
level: intermediate
minutes: 3
summary: "A graph is bipartite exactly when it has no odd cycle."
sourceLesson: disc-graphs
---

## Bipartite graphs and colouring

Here graphs are finite, simple and undirected. A **proper colouring** assigns a colour to each vertex so that adjacent vertices differ. The **chromatic number** is the fewest colours needed. Two bounds pin it down for many graphs:

```formula reference
χ(K_n) = n
χ(G) ≤ Δ(G) + 1
where
χ(G): chi of G, the chromatic number of graph G: the fewest colours in a proper colouring
G: a finite simple undirected graph; the empty graph has chromatic number zero, and the maximum-degree bound assumes at least one vertex
K_n: the complete graph on n vertices, every pair joined
n: the number of vertices
Δ(G): delta of G, the maximum degree: the largest number of edges touching any one vertex of G
≤: is less than or equal to
In words: A complete graph needs a different colour for every vertex. Any nonempty finite simple undirected graph can be greedily coloured with at most one more colour than its maximum degree, though this need not be optimal.
```

The complete graph on four vertices needs four colours because every pair conflicts. A five-cycle needs three: two colours clash when they meet round the odd cycle, and a third resolves that clash. A high-degree star still needs only two colours, showing that the maximum-degree bound can be loose.

- A graph is **2-colourable (bipartite)** if and only if it has **no odd cycle**. Even cycles need 2 colours; odd cycles need 3.
- BFS checks bipartiteness in O(n + m), where n counts vertices and m counts edges: colour by distance parity and look for an edge joining the same parity.
- Deciding 3-colourability is NP-complete.
- **Greedy colouring** gives each vertex the first colour unused by its already-coloured neighbours. At most as many colours as its degree are blocked, so one additional colour always suffices. Vertex order can make this use more colours than optimal.

```python
from collections import deque

def is_bipartite(adj):
    side = {}
    # Restart BFS in each unseen component.
    for s in adj:
        if s in side:
            continue
        side[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in side:
                    # Use the opposite side.
                    side[v] = 1 - side[u]
                    q.append(v)
                # Same-side edges conflict.
                elif side[v] == side[u]:
                    return False
    return True
```

Colouring shows up wherever conflicting things must be kept apart:

- **Register allocation.** Compilers build an **interference graph** with a vertex per variable and an edge between variables that are live at the same time. Colours are CPU registers. If the fixed graph needs more colours than there are registers, it cannot be allocated as-is. An allocator can **spill** values to memory or transform live ranges, for example by splitting or rematerialising values. Chaitin and colleagues described an implemented graph-colouring allocator in their 1981 paper Register allocation via coloring.
- **Scheduling.** Exams that share a student can't be at the same time: colours are time slots.
- **Frequency assignment.** Nearby transmitters need different frequencies.

The **four colour theorem** says every finite simple planar graph can be properly vertex-coloured with at most 4 colours. For maps, this corresponds to connected regions sharing a boundary segment; meeting at one point does not require different colours. Its 1976 proof by Appel and Haken was among the first major proofs to rely on a computer check.

## Key takeaways

- A graph is bipartite exactly when it has no odd cycle.
- Colouring models conflicts in scheduling and register allocation; greedy choices need not be optimal.

## Further reading

- [Graph coloring — Wikipedia](https://en.wikipedia.org/wiki/Graph_coloring)
- [Register allocation — Wikipedia](https://en.wikipedia.org/wiki/Register_allocation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Register allocation via coloring — IBM Research](https://research.ibm.com/publications/register-allocation-via-coloring)
