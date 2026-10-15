---
id: disc-euler-hamilton-paths
title: "Euler trails and Hamiltonian cycles"
level: intermediate
minutes: 4
summary: "Euler trails use every edge once and are characterised by degree parity and connectivity."
sourceLesson: disc-graphs
---

## Euler paths: every edge once

The founding problem of graph theory: in 18th-century Königsberg, could you walk across each of the seven bridges once and only once? Euler modelled land masses as vertices and bridges as edges (a multigraph) and noticed that every time a walk passes through a vertex it uses two edges, one in and one out.

> [!note] Euler's theorem on circuits
> A connected graph has an **Euler circuit** (a closed walk using every edge once and only once) if and only if every vertex has even degree. It has an **Euler path** (not necessarily closed) if and only if exactly 0 or 2 vertices have odd degree. With 2, the path must start at one odd vertex and end at the other.

Königsberg's four land masses had degrees 5, 3, 3 and 3: four odd vertices, so no such walk exists. (As a check, 5 + 3 + 3 + 3 = 14, twice the 7 bridges, as the handshaking lemma requires.)

```
bridges (edges):
  A-C, A-C   two bridges
  A-B, A-B   two bridges
  A-D, B-D, C-D

degrees: A = 5, B = 3,
         C = 3, D = 3
```

Checking connectivity and parity takes O(n + m), where n is the number of vertices and m is the number of edges. After locating an edge-bearing start vertex, **Hierholzer's algorithm** traverses the edges in O(m) time using an appropriate adjacency representation.

```python
def euler_kind(adj):
    # Prechecked: edge-bearing vertices
    # form one connected component.
    # Lists count all incident edge ends.
    # Each internal visit uses two edges.
    odd = [v for v in adj
           if len(adj[v]) % 2]
    # No odd endpoints: a closed trail fits.
    if not odd:
        return 'circuit'
    # Two odd endpoints allow an open trail.
    if len(odd) == 2:
        return 'path'
    return 'none'
```

Isolated vertices do not affect a trail that covers edges: connectivity is needed among the edge-bearing vertices. With no edges, a nonempty graph has a length-zero closed trail at any vertex; an empty vertex set depends on the chosen empty-walk convention. The classifier above uses the convention that no odd degrees means “circuit” and assumes connectivity has already been checked.

For a directed Euler circuit with at least one edge, each vertex must have equal in-degree and out-degree, and all non-isolated vertices must belong to one connected component when directions are ignored. Balance alone is insufficient. Euler paths are used in DNA sequence assembly (de Bruijn graphs of overlapping fragments), in route planning for snowploughs and postal delivery (the Chinese postman problem), and in generating de Bruijn sequences. Those give minimal universal strings for a sliding-window code tester; a keypad that requires Enter, resets after failure or locks out attempts needs a different model.

## Hamilton paths: every vertex once

A **Hamiltonian cycle** visits every vertex once and only once and returns home. It looks like a small change from Euler, but it's a completely different world:

- There is **no known efficient test**. Deciding whether a Hamiltonian cycle exists is NP-complete, as is the decision version of travelling salesman (is there a tour whose total cost is at most a given budget?). Finding a cheapest tour is an NP-hard optimisation problem.
- There are useful **sufficient** conditions: if they hold, a Hamiltonian cycle is guaranteed, but a graph can have one without meeting them. The best known is **Dirac's theorem**:

```formula
deg(v) ≥ n / 2   for every v   and n ≥ 3
where
deg(v): the degree of vertex v: how many edges touch it
v: any vertex of the graph
n: the number of vertices in the (simple) graph
≥: is greater than or equal to
In words: if a simple graph has at least 3 vertices and every vertex is joined to at least half of all the vertices, then it has a Hamiltonian cycle.
```

For example, K₃,₃ (two groups of 3, every vertex joined to all 3 in the other group) has six vertices and every degree is three, which is half the vertex count, so Dirac guarantees a Hamiltonian cycle; one is a1, b1, a2, b2, a3, b3, back to a1. The condition is not necessary: a plain cycle on 10 vertices has every degree 2, far below half the vertex count, five, and is itself a Hamiltonian cycle.

Euler and Hamilton are independent. Two triangles sharing one vertex (a "bowtie") has all degrees even, so it has an Euler circuit, but any cycle through all 5 vertices would have to pass through the shared vertex twice, so there is no Hamiltonian cycle.

> [!tip] Spot the trap
> Deciding whether an Euler trail visits every edge once is linear-time. Deciding whether a Hamiltonian path or cycle visits every vertex once is NP-complete. When a problem lands on your desk, figure out which one it really is before reaching for an algorithm.

## Key takeaways

- Euler trails use every edge once and are characterised by degree parity and connectivity.
- Hamiltonian cycles visit every vertex once; Dirac’s condition is sufficient rather than necessary.

## Further reading

- [Eulerian path — Wikipedia](https://en.wikipedia.org/wiki/Eulerian_path)
- [Hamiltonian path — Wikipedia](https://en.wikipedia.org/wiki/Hamiltonian_path)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
