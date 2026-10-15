---
id: disc-planarity-euler-bounds
title: "Planarity, Euler’s formula and edge bounds"
level: intermediate
minutes: 4
summary: "Euler’s formula counts faces in a connected plane drawing, including the outside face."
sourceLesson: disc-graphs
---

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

Note that this unit switches from n and m to V and E for the counts (earlier, V and E named the sets themselves), following a common convention for Euler's formula. The formula needs the drawing to be connected; for a drawing in several separate pieces, the 2 becomes 1 plus the number of pieces.

Euler's formula also limits how many edges a planar graph can have. For a connected simple plane graph with at least 3 vertices, each face boundary walk has length at least 3. Count edge sides with multiplicity: a bridge is traversed twice on the same face. Thus the total boundary length is twice the edge count, and at least three times the face count. Substitute Euler's expression for the face count:

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

If the connected simple plane graph has at least 3 vertices and no triangles (no cycle of length 3), every face boundary walk has length at least 4. The same steps give a smaller edge limit:

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

The inequalities only work one way: satisfying the general planar edge bound does **not** prove planarity. K₃,₃ has 9 edges, within the general six-vertex limit of 12, yet it is not planar; only the triangle-free bound catches it.

## Key takeaways

- Euler’s formula counts faces in a connected plane drawing, including the outside face.
- Planar edge bounds can disprove planarity; satisfying a bound does not establish planarity.

## Further reading

- [Planar graph — Wikipedia](https://en.wikipedia.org/wiki/Planar_graph)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
