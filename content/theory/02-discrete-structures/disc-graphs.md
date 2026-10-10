---
id: disc-graphs
title: Graph theory essentials
level: intermediate
minutes: 15
summary: Degrees and the handshaking lemma, trees, Euler and Hamilton paths, bipartite graphs and colouring, and planarity with Euler's formula, plus where each shows up in real systems.
---

A **graph** is a set of things and the connections between them. Road networks, the web, social networks, package dependencies, chip layouts, the call graph of a program and the interference between variables in a compiler are all graphs. The DSA subject covers graph *algorithms* (BFS, Dijkstra, and so on). This lesson is about the *theory*: the facts that tell you what is possible before you write any code, and which problems have efficient general algorithms and which have no known polynomial-time solution.

## Vocabulary

A graph is made of **vertices** (the things, also called nodes) and **edges** (the connections). In an **undirected** graph an edge just joins two vertices, with no direction; in a **directed** graph it points from one vertex to another. A **simple** graph has no self-loops (an edge from a vertex to itself) and no repeated edges. Unless stated otherwise, "graph" here means simple and undirected. Textbooks write all this in a compact notation that the rest of the lesson uses:

```formula
G = (V, E)
{u, v} ∈ E
(u, v) ∈ E
n = |V|
m = |E|
where
G: the graph, a pair made of a vertex set and an edge set
V: the set of vertices
E: the set of edges
u, v: two vertices of the graph
{u, v}: an undirected edge: an unordered pair, so {u, v} and {v, u} are the same edge
(u, v): a directed edge: an ordered pair, pointing from u to v, so (u, v) and (v, u) are different edges
∈: "is an element of", so {u, v} ∈ E says that this edge is one of the graph's edges
|V|, |E|: the size of a set: how many elements it has
n: the number of vertices
m: the number of edges
In words: a graph G is a set of vertices V plus a set of edges E; an undirected edge is an unordered pair of vertices, a directed edge an ordered pair, and n and m count the vertices and edges.
```

For example, a triangle on vertices a, b and c has V = {a, b, c} and E = {{a, b}, {b, c}, {a, c}}, so n = 3 and m = 3.

- The **degree** of a vertex v, written deg(v), is the number of edges touching it. In the triangle every vertex has degree 2.
- A walk is a sequence of vertices joined by edges. A simple path repeats no vertex; a cycle closes a path by returning to its start, with no other repeated vertices. An Euler trail may revisit vertices but never edges.
- A graph is **connected** if there is a path between every pair of vertices.
- The **complete graph** Kₙ has an edge between every pair of its n vertices.

The number of edges in a complete graph is the number of ways to pick an unordered pair of vertices:

```formula
m = n × (n − 1) / 2
m = 4 × 3 / 2 = 6   for n = 4
where
m: the number of edges in the complete graph K_n
n: the number of vertices
K_n: the complete graph on n vertices, with every pair joined
In words: each of the n vertices joins the n − 1 others, which counts every edge twice (once from each end), so halve it. Four vertices give 6 edges.
```

This grows with the square of n: a full mesh of 100 servers needs 100 × 99 / 2 = 4,950 links.

### The handshaking lemma

Every edge has two ends, so if you add up the degrees of all the vertices, each edge is counted exactly twice. This holds for every undirected graph:

```formula
Σ deg(v) = 2 × m
2 + 2 + 2 = 2 × 3
where
Σ: "sum of": add up the expression after it once for every vertex v of the graph
deg(v): the degree of vertex v: how many edges touch it
v: a vertex of the graph
m: the number of edges
In words: the degrees add up to twice the number of edges. A triangle has three vertices of degree 2 and three edges, and 6 = 2 × 3.
```

Consequences you can use immediately:

- The degree sum is even, so the number of vertices with **odd degree is always even**.
- There is no graph on 7 vertices where every vertex has degree 3: the degree sum would be 7 × 3 = 21, which is odd, and the edge count would be 21 / 2 = 10.5.
- Dividing both sides by the number of vertices links edges to the average degree:

```formula
m = n × d / 2
m = 10^9 × 200 / 2 = 10^11
where
m: the number of edges
n: the number of vertices
d: the average degree: the degree sum divided by n
In words: a graph's edge count is half of (vertices × average degree). A social network of a billion users averaging 200 friends has 100 billion friendship edges.
```

The handshaking lemma is about undirected edges. In a directed graph the same counting gives: the in-degrees add up to m, and so do the out-degrees.

### Representations

| | Adjacency list | Adjacency matrix |
|---|---|---|
| Space | O(n + m) | O(n²) |
| Is u–v an edge? | O(deg u) | O(1) |
| List neighbours | O(deg u) | O(n) |
| Good for | Sparse graphs | Dense graphs |

In the table, n is the number of vertices, m the number of edges and deg u the degree of vertex u. For sparse graphs (far fewer edges than the roughly n²/2 a complete graph would have), adjacency lists save space. The table assumes unsorted neighbor lists; hash-set or sorted representations change membership costs.

## Trees

A **tree** is a connected graph with no cycles. Its edge count is fixed by its vertex count, and the same idea extends to a **forest** (a graph with no cycles that need not be connected, so it is a collection of separate trees):

```formula
m = n − 1
c = n − m
where
m: the number of edges
n: the number of vertices
c: the number of components: separate connected pieces of the forest
In words: a tree on n vertices always has n − 1 edges, and a forest with n vertices and m edges falls into exactly n − m separate pieces. A tree is the forest with exactly one piece.
```

Why: start with n isolated vertices, which is n separate pieces. Adding an edge between two different pieces (which never creates a cycle) merges them, so the count drops by exactly one per edge. A 10-vertex tree therefore has 9 edges, and a 10-vertex forest with 7 edges has 3 components. This only holds when there are no cycles: an edge added inside a piece makes a cycle and does not reduce the count.

For a nonempty finite simple undirected graph with n vertices, these are equivalent:

1. It is connected and acyclic.
2. It is connected and has exactly n − 1 edges.
3. It is acyclic and has exactly n − 1 edges.
4. There is exactly one simple path between every pair of distinct vertices.

These equivalences are surprisingly handy. Adding an edge between previously nonadjacent vertices of a tree creates exactly one cycle; removing any edge disconnects it. The forest count is what Kruskal's algorithm and union-find exploit: each edge that joins two different components reduces the count by one.

A **spanning tree** of a connected graph is a tree that uses all its vertices. Network protocols (the Spanning Tree Protocol in Ethernet switching) build one to avoid broadcast loops. How many different trees can be built on a fixed set of labelled vertices is given by **Cayley's formula**:

```formula
T(n) = n^{n − 2}   for n ≥ 2
T(4) = 4^2 = 16
where
T(n): the number of different trees whose vertices are exactly the n labelled vertices (two trees differ if some pair is joined in one but not the other)
n: the number of vertices, at least 2
n^{n − 2}: n multiplied by itself n − 2 times
≥: is greater than or equal to
In words: there are n to the power n − 2 labelled trees on n vertices, so 4 labelled vertices can be joined into 16 different trees.
```

The 16 for n = 4 splits into 4 stars (pick the centre) and 12 paths (the 24 orderings of the 4 vertices, halved because a path read backwards is the same tree). The count grows very fast: 10 vertices already allow 10⁸ trees. It counts labelled trees; if you ignore labels, 4 vertices only make 2 shapes (the star and the path).

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

Checking the condition takes O(n + m), and **Hierholzer's algorithm** finds the Euler circuit in O(m).

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

A **Hamiltonian cycle** visits every vertex once and only once and returns home. It looks like a small change from Euler, but it's a completely different world:

- There is **no known efficient test**. Deciding whether a Hamiltonian cycle exists is NP-complete, as is the decision version of travelling salesman (is there a tour whose total cost is at most a given budget?). Finding a cheapest tour is an NP-hard optimization problem.
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

For example, K₃,₃ (two groups of 3, every vertex joined to all 3 in the other group) has n = 6 and every degree 3, which is 6 / 2, so Dirac guarantees a Hamiltonian cycle; one is a1, b1, a2, b2, a3, b3, back to a1. The condition is not necessary: a plain cycle on 10 vertices has every degree 2, far below 10 / 2 = 5, and is itself a Hamiltonian cycle.

Euler and Hamilton are independent. Two triangles sharing one vertex (a "bowtie") has all degrees even, so it has an Euler circuit, but any cycle through all 5 vertices would have to pass through the shared vertex twice, so there is no Hamiltonian cycle.

> [!tip] Spot the trap
> "Visit every edge once" is linear-time. "Visit every vertex once" is NP-complete. When a problem lands on your desk, figure out which one it really is before reaching for an algorithm.

## Bipartite graphs and colouring

A **proper colouring** assigns a colour to each vertex so that adjacent vertices differ. The **chromatic number** is the fewest colours needed. Two bounds pin it down for many graphs:

```formula
χ(K_n) = n
χ(G) ≤ Δ(G) + 1
where
χ(G): chi of G, the chromatic number of graph G: the fewest colours in a proper colouring
G: any graph
K_n: the complete graph on n vertices, every pair joined
n: the number of vertices
Δ(G): delta of G, the maximum degree: the largest number of edges touching any one vertex of G
≤: is less than or equal to
In words: a complete graph needs one colour per vertex, because every vertex clashes with every other; and no graph ever needs more than one colour above its highest degree.
```

For example, K₄ needs 4 colours, and a cycle on 5 vertices has maximum degree 2, so it needs at most 3 colours (it needs exactly 3, as the list below explains). The second bound is often loose: a star with 100 leaves has maximum degree 100 but needs only 2 colours.

- A graph is **2-colourable (bipartite)** if and only if it has **no odd cycle**. Even cycles need 2 colours; odd cycles need 3.
- BFS checks bipartiteness in O(n + m), where m is the number of edges: colour by distance parity and look for an edge between two vertices of the same parity.
- Deciding 3-colourability is NP-complete.
- **Greedy colouring** (go through vertices, give each the smallest colour not used by its neighbours) uses at most Δ + 1 colours, which is where the bound above comes from: when a vertex is coloured, at most Δ neighbours already hold a colour, so one of Δ + 1 colours is always free. It can be far from optimal depending on the order.

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

A graph is **planar** if it can be drawn in the plane with no edges crossing. For a connected planar drawing, **Euler's formula** relates vertices, edges and the faces of a drawing (regions, including the outside one):

```formula
V − E + F = 2
8 − 12 + F = 2
F = 2 − 8 + 12 = 6
where
V: the number of vertices
E: the number of edges
F: the number of faces: the regions the drawing cuts the plane into, counting the unbounded outside region
In words: in any connected drawing without crossings, vertices minus edges plus faces is always 2. A cube drawn flat (a square inside a square, corners joined) has 8 vertices and 12 edges, so it must have 6 faces: 5 inside plus the outside.
```

Note that this lesson switches here from n and m to V and E for the counts (earlier, V and E named the sets themselves), because that is how Euler's formula is always written. The formula needs the drawing to be connected; for a drawing in several separate pieces, the 2 becomes 1 plus the number of pieces.

Euler's formula also limits how many edges a planar graph can have. For a connected simple plane graph with at least 3 vertices, each face boundary walk has length at least 3. Counting edge sides with multiplicity (a bridge is traversed twice on the same face) gives total boundary length 2E, hence 3F ≤ 2E. Substitute F = 2 − V + E from Euler's formula:

```formula
3 × F ≤ 2 × E
3 × (2 − V + E) ≤ 2 × E
6 − 3 × V + 3 × E ≤ 2 × E
E ≤ 3 × V − 6
where
F: the number of faces, including the outside one
E: the number of edges
V: the number of vertices, at least 3
≤: is less than or equal to
In words: every face is surrounded by at least 3 edge sides and every edge has only 2 sides, which forces a simple planar graph with at least 3 vertices to have at most 3V − 6 edges.
```

If the graph has no triangles (no cycle of length 3), every face boundary has length at least 4. The same steps give a tighter bound:

```formula
4 × F ≤ 2 × E
4 × (2 − V + E) ≤ 2 × E
E ≤ 2 × V − 4
where
F: the number of faces, including the outside one
E: the number of edges
V: the number of vertices, at least 3
≤: is less than or equal to
In words: a simple planar graph with no triangles has at most 2V − 4 edges.
```

These inequalities give quick proofs of non-planarity. **K₅** is the complete graph on 5 vertices; **K₃,₃** (the "three houses, three utilities" puzzle) joins each of 3 vertices to each of 3 others and is bipartite, so it has no triangles:

```formula
E(K_5) = 10 > 3 × 5 − 6 = 9
E(K_{3,3}) = 9 > 2 × 6 − 4 = 8
where
K_5: the complete graph on 5 vertices, with 5 × 4 / 2 = 10 edges
K_{3,3}: the complete bipartite graph with 3 vertices on each side, every left vertex joined to every right one: 6 vertices and 3 × 3 = 9 edges
E( ): the number of edges of the graph in brackets
>: is greater than
In words: K5 has one edge too many for a 5-vertex planar graph, and K3,3 has one edge too many for a 6-vertex planar graph without triangles, so neither can be drawn without a crossing.
```

**Kuratowski's theorem** says these two are the only obstacles: a graph is planar if and only if it contains no subdivision of K₅ or K₃,₃. Planarity can be tested in linear time (the Hopcroft–Tarjan planarity test, 1974). It matters in chip and PCB layout, where crossing wires need extra layers, and in graph drawing tools.

The inequalities only work one way: satisfying E ≤ 3V − 6 does **not** prove a graph is planar. K₃,₃ has 9 edges, within the general limit 3 × 6 − 6 = 12, yet it is not planar; only the triangle-free bound catches it.

## Key takeaways
- The degrees add up to twice the number of edges, so the number of odd-degree vertices is always even.
- A tree has one fewer edge than vertices and a unique path between any two vertices; a forest's number of components is its vertex count minus its edge count.
- When all edge-bearing vertices are connected, an undirected Euler circuit exists exactly when all degrees are even; an Euler trail needs 0 or 2 odd vertices. Construction is linear; deciding Hamiltonian-cycle existence is NP-complete.
- A graph is bipartite exactly when it has no odd cycle; general colouring is NP-hard but models register allocation and scheduling.
- In a connected crossing-free drawing, vertices − edges + faces = 2 (Euler's formula). A simple planar graph with at least 3 vertices has at most 3 × vertices − 6 edges; the triangle-free limit of 2 × vertices − 4 is what rules out K₃,₃.

## Further reading
- [Eulerian path — Wikipedia](https://en.wikipedia.org/wiki/Eulerian_path)
- [Hamiltonian path — Wikipedia](https://en.wikipedia.org/wiki/Hamiltonian_path)
- [Graph coloring — Wikipedia](https://en.wikipedia.org/wiki/Graph_coloring)
- [Planar graph — Wikipedia](https://en.wikipedia.org/wiki/Planar_graph)
- [Tree (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Tree_(graph_theory))
- [Register allocation — Wikipedia](https://en.wikipedia.org/wiki/Register_allocation)
