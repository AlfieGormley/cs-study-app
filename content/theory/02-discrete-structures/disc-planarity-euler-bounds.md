---
id: disc-planarity-euler-bounds
title: "Planarity, Euler’s formula and edge bounds"
level: intermediate
minutes: 3
summary: "Euler’s formula counts faces in a connected plane drawing, including the outside face."
sourceLesson: disc-graphs
---

## Planarity

A graph is **planar** if it can be drawn in the plane with no edges crossing. For a connected planar drawing, **Euler's formula** relates vertices, edges and the faces of a drawing (regions, including the outside one):

```formula essential
V − E + F = 2
where
V: the number of vertices
E: the number of edges
F: the number of faces: the regions the drawing cuts the plane into, counting the unbounded outside region
In words: In a connected drawing without crossings, vertices minus edges plus faces is two. Faces include the unbounded outside region.
```

In this unit the capital letters denote counts rather than vertex and edge sets. Connectedness is required for the constant two; for several components the constant becomes one plus the component count. Adding a crossing-free edge between already-connected vertices splits one face into two, keeping the relationship balanced.

For a connected simple plane graph with at least three vertices, every face boundary walk uses at least three edge sides. Every edge contributes two sides, counting a bridge twice on the same face. Combining that counting argument with Euler’s relationship gives an edge limit:

```formula reference
E ≤ 3 × V − 6
where
E: the number of edges
V: the number of vertices, at least 3
≤: is less than or equal to
In words: A finite simple planar graph with at least three vertices has an edge limit that grows linearly with its vertex count. Exceeding the limit disproves planarity; satisfying it is inconclusive.
```

Without triangles, face boundaries need at least four sides under the same assumptions, producing a stricter edge limit:

```formula reference
E ≤ 2 × V − 4
where
E: the number of edges
V: the number of vertices, at least 3
≤: is less than or equal to
In words: A finite simple triangle-free planar graph with at least three vertices has a stricter linear edge limit. Bipartite graphs have no triangles, so this test also applies to them.
```

These inequalities give quick proofs of non-planarity. **K₅** is the complete graph on 5 vertices; **K₃,₃** (the "three houses, three utilities" puzzle) joins each of 3 vertices to each of 3 others and is bipartite, so it has no triangles.

The complete five-vertex graph has ten edges, exceeding the planar limit of nine. The complete bipartite graph with three vertices per side has nine edges, exceeding its triangle-free planar limit of eight. Both are non-planar.

**Kuratowski's theorem** says these two are the only obstacles: a graph is planar if and only if it contains no subdivision of K₅ or K₃,₃. Planarity can be tested in linear time (the Hopcroft–Tarjan planarity test, 1974). It matters in chip and PCB layout, where crossing wires need extra layers, and in graph drawing tools.

The inequalities only work one way: satisfying the general planar edge bound does **not** prove planarity. K₃,₃ has 9 edges, within the general six-vertex limit of 12, yet it is not planar; only the triangle-free bound catches it.

## Key takeaways

- Euler’s formula counts faces in a connected plane drawing, including the outside face.
- Planar edge bounds can disprove planarity; satisfying a bound does not establish planarity.

## Further reading

- [Planar graph — Wikipedia](https://en.wikipedia.org/wiki/Planar_graph)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
