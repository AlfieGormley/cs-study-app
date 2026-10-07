---
id: disc-graphs
title: Graph theory essentials
level: intermediate
minutes: 15
summary: Degrees and the handshaking lemma, trees, Euler and Hamilton paths, bipartite graphs and colouring, and planarity with Euler's formula, plus where each shows up in real systems.
---

A **graph** is a set of things and the connections between them. Road networks, the web, social networks, package dependencies, circuit layouts, the call graph of a program and the interference between variables in a compiler are all graphs. The DSA subject covers graph *algorithms* (BFS, Dijkstra, and so on). This lesson is about the *theory*: the facts that tell you what is possible before you write any code, and which problems have efficient general algorithms and which have no known polynomial-time solution.

## Vocabulary

A graph G = (V, E) has a set of **vertices** V and a set of **edges** E. In an **undirected** graph an edge is an unordered pair {u, v}; in a **directed** graph it is an ordered pair (u, v). A **simple** graph has no self-loops and no repeated edges. Unless stated otherwise, "graph" here means simple and undirected, with n = |V| and m = |E|.

- The **degree** of a vertex is the number of edges touching it.
- A walk is a sequence of vertices joined by edges. A simple path repeats no vertex; a cycle closes a path by returning to its start, with no other repeated vertices. An Euler trail may revisit vertices but never edges.
- A graph is **connected** if there is a path between every pair of vertices.
- The **complete graph** Kₙ has an edge between every pair: n(n − 1)/2 edges.

### The handshaking lemma

Every edge has two ends, so summing degrees counts each edge exactly twice:

```
sum of all degrees = 2m
```

Consequences you can use immediately:

- The number of vertices with **odd degree is always even**.
- There is no graph on 7 vertices where every vertex has degree 3 (the sum would be 21, which is odd).
- A graph with average degree d has m = nd/2 edges. A social network of 10⁹ users averaging 200 friends has 10¹¹ edges.

### Representations

| | Adjacency list | Adjacency matrix |
|---|---|---|
| Space | O(n + m) | O(n²) |
| Is u–v an edge? | O(deg u) | O(1) |
| List neighbours | O(deg u) | O(n) |
| Good for | Sparse graphs | Dense graphs |

For sparse graphs (m much smaller than n²), adjacency lists save space. The table assumes unsorted neighbor lists; hash-set or sorted representations change membership costs.

## Trees

A **tree** is a connected graph with no cycles. For a nonempty finite simple undirected graph with n vertices, these are equivalent:

1. It is connected and acyclic.
2. It is connected and has exactly n − 1 edges.
3. It is acyclic and has exactly n − 1 edges.
4. There is exactly one simple path between every pair of distinct vertices.

These equivalences are surprisingly handy. Adding an edge between previously nonadjacent vertices of a tree creates exactly one cycle; removing any edge disconnects it. A **forest** (acyclic, not necessarily connected) with n vertices and m edges has exactly n − m components, which is what Kruskal's algorithm and union-find exploit: each edge that joins two different components reduces the count by one.

A **spanning tree** of a connected graph is a tree that uses all its vertices. Network protocols (the Spanning Tree Protocol in Ethernet switching) build one to avoid broadcast loops. For n ≥ 2, the number of labelled trees on a fixed n-vertex set is nⁿ⁻² (**Cayley's formula**): 16 for n = 4.

## Euler paths: every edge once

The founding problem of graph theory: in 18th-century Königsberg, could you walk across each of the seven bridges exactly once? Euler modelled land masses as vertices and bridges as edges (a multigraph) and noticed that every time a walk passes through a vertex it uses two edges, one in and one out.

> [!note] Euler's theorem
> A connected graph has an **Euler circuit** (a closed walk using every edge exactly once) if and only if every vertex has even degree. It has an **Euler path** (not necessarily closed) if and only if exactly 0 or 2 vertices have odd degree. With 2, the path must start at one odd vertex and end at the other.

Königsberg's four land masses had degrees 5, 3, 3 and 3: four odd vertices, so no such walk exists.

```
bridges (edges):
  A-C, A-C   two bridges
  A-B, A-B   two bridges
  A-D, B-D, C-D

degrees: A = 5, B = 3,
         C = 3, D = 3
```

Checking the condition takes O(n + m), and **Hierholzer's algorithm** finds the circuit in O(m).

```python
def euler_kind(adj):
    # assumes the edges form one
    # connected component
    odd = [v for v in adj
           if len(adj[v]) % 2]
    if not odd:
        return 'circuit'
    if len(odd) == 2:
        return 'path'
    return 'none'
```

For a directed Euler circuit with at least one edge, each vertex must have equal in-degree and out-degree, and all non-isolated vertices must belong to one connected component when directions are ignored. Balance alone is insufficient. Euler paths are used in DNA sequence assembly (de Bruijn graphs of overlapping fragments), in route planning for snowploughs and postal delivery (the Chinese postman problem), and in generating de Bruijn sequences. Those give minimal universal strings for a sliding-window code tester; a keypad that requires Enter, resets after failure or locks out attempts needs a different model.

## Hamilton paths: every vertex once

A **Hamiltonian cycle** visits every vertex exactly once and returns home. It looks like a small change from Euler, but it's a completely different world:

- There is **no known efficient test**. Deciding whether a Hamiltonian cycle exists is NP-complete, as is the decision version of travelling salesman (is there a tour of cost at most B?). Finding a cheapest tour is an NP-hard optimization problem.
- There are useful **sufficient** conditions. **Dirac's theorem**: if n ≥ 3 and every vertex has degree at least n/2, a Hamiltonian cycle exists. But plenty of graphs without that property have one too.

Euler and Hamilton are independent. Two triangles sharing one vertex (a "bowtie") has all degrees even, so it has an Euler circuit, but any cycle through all 5 vertices would have to pass through the shared vertex twice, so there is no Hamiltonian cycle.

> [!tip] Spot the trap
> "Visit every edge once" is linear-time. "Visit every vertex once" is NP-complete. When a problem lands on your desk, figure out which one it really is before reaching for an algorithm.

## Bipartite graphs and colouring

A **proper colouring** assigns a colour to each vertex so that adjacent vertices differ. The **chromatic number** χ(G) is the fewest colours needed.

- χ(Kₙ) = n: every vertex clashes with every other.
- A graph is **2-colourable (bipartite)** if and only if it has **no odd cycle**. Even cycles need 2 colours; odd cycles need 3.
- BFS checks bipartiteness in O(n + m): colour by distance parity and look for an edge between two vertices of the same parity.
- Deciding 3-colourability is NP-complete.
- **Greedy colouring** (go through vertices, give each the smallest colour not used by its neighbours) uses at most Δ + 1 colours, where Δ is the maximum degree, but can be far from optimal depending on the order.

```python
from collections import deque

def is_bipartite(adj):
    side = {}
    for s in adj:
        if s in side:
            continue
        side[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in side:
                    side[v] = 1 - side[u]
                    q.append(v)
                elif side[v] == side[u]:
                    return False
    return True
```

Colouring shows up wherever conflicting things must be kept apart:

- **Register allocation.** Compilers build an **interference graph** with a vertex per variable and an edge between variables that are live at the same time. Colours are CPU registers. If the fixed graph needs more colours than there are registers, it cannot be allocated as-is. An allocator can **spill** values to memory or transform live ranges, for example by splitting or rematerializing values. Chaitin and colleagues described an implemented graph-colouring allocator in their 1981 paper Register allocation via coloring.
- **Scheduling.** Exams that share a student can't be at the same time: colours are time slots.
- **Frequency assignment.** Nearby transmitters need different frequencies.

The **four colour theorem** says every finite simple planar graph can be properly vertex-coloured with at most 4 colours. For maps, this corresponds to connected regions sharing a boundary segment; meeting at one point does not require different colours. Its 1976 proof by Appel and Haken was among the first major proofs to rely on a computer check.

## Planarity

A graph is **planar** if it can be drawn in the plane with no edges crossing. For a connected planar drawing, **Euler's formula** relates vertices, edges and faces (regions, including the outside one):

```
V - E + F = 2

cube:  V = 8, E = 12
       F = 12 - 8 + 2 = 6
```

For a connected simple plane graph with at least 3 vertices, each face boundary walk has length at least 3. Counting edge sides with multiplicity (a bridge is traversed twice on the same face) gives total boundary length 2E, hence 3F ≤ 2E. Substitute into Euler's formula:

```
E ≤ 3V - 6     (simple, planar, V ≥ 3)
E ≤ 2V - 4     (also no triangles)
```

These inequalities give quick proofs of non-planarity:

- **K₅**: V = 5, E = 10, but 3V − 6 = 9. Not planar.
- **K₃,₃** (the "three houses, three utilities" puzzle): bipartite, so no triangles. V = 6, E = 9, but 2V − 4 = 8. Not planar.

**Kuratowski's theorem** says these two are the only obstacles: a graph is planar if and only if it contains no subdivision of K₅ or K₃,₃. Planarity can be tested in linear time (Hopcroft and Tarjan, 1974). It matters in chip and PCB layout, where crossing wires need extra layers, and in graph drawing tools.

The inequalities only work one way: satisfying E ≤ 3V − 6 does **not** prove a graph is planar (K₃,₃ satisfies it).

## Key takeaways
- The sum of degrees is 2m, so the number of odd-degree vertices is always even.
- A tree on n vertices has n − 1 edges and a unique path between any two vertices; a forest has n − m components.
- When all edge-bearing vertices are connected, an undirected Euler circuit exists exactly when all degrees are even; an Euler trail needs 0 or 2 odd vertices. Construction is linear; deciding Hamiltonian-cycle existence is NP-complete.
- A graph is bipartite exactly when it has no odd cycle; general colouring is NP-hard but models register allocation and scheduling.
- A connected plane drawing satisfies V − E + F = 2. Simple planar graphs with V ≥ 3 satisfy E ≤ 3V − 6; the triangle-free bound E ≤ 2V − 4 is what rules out K₃,₃.

## Further reading
- [Eulerian path — Wikipedia](https://en.wikipedia.org/wiki/Eulerian_path)
- [Hamiltonian path — Wikipedia](https://en.wikipedia.org/wiki/Hamiltonian_path)
- [Graph coloring — Wikipedia](https://en.wikipedia.org/wiki/Graph_coloring)
- [Planar graph — Wikipedia](https://en.wikipedia.org/wiki/Planar_graph)
- [Tree (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Tree_(graph_theory))
- [Register allocation — Wikipedia](https://en.wikipedia.org/wiki/Register_allocation)
