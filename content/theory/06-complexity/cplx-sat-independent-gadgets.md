---
id: cplx-sat-independent-gadgets
title: "Building clause and consistency gadgets"
level: intermediate
minutes: 4
summary: "Independent sets have no internal edges and are easy to verify."
sourceLesson: cplx-reductions
---

## 3-SAT to Independent Set

**Independent Set (IS)**: given a graph G and integer k, is there a set of k vertices with no edge between any two of them? Written out with symbols:

```formula
S ⊆ V   and   |S| = k
{u, v} ∉ E   for all u, v ∈ S
where
G: a finite simple undirected input graph, made of a vertex set V and an edge set E
V: the set of vertices (dots) of G
E: the set of edges (lines) of G; an edge {u, v} joins vertices u and v
k: the target size, a whole number given as part of the input
S: the proposed independent set: a collection of vertices of G
⊆: "is a subset of": every vertex in S is also in V
|S|: the number of vertices in S
u, v: any two different vertices of S
∈: "is a member of"
∉: "is not a member of": {u, v} is not an edge of G
In words: an independent set of size k is a group of k vertices where no two are joined by an edge. The IS question asks whether one exists.
```

IS is in NP: the certificate is the set S itself. To check it, look up every pair of its vertices in the edge set:

```formula
N_pairs = k(k − 1) / 2 = O(k^2)
N_pairs = 3 × 2 / 2 = 3   for k = 3
where
N_pairs: the number of vertex pairs the verifier must look up in E
k: the size of the claimed independent set
O(k^2): Big O: grows at most as fast as a constant times k squared, for large k
In words: checking a claimed independent set of k vertices takes about k squared over 2 edge look-ups, which is polynomial, so IS is in NP.
```

Now the reduction. It starts from a **3-CNF formula** φ: an AND of m clauses, where each clause is an OR of exactly 3 **literals** (a variable such as x or its negation ¬x). Given φ:

1. **Clause gadget.** For each clause, create 3 vertices, one per literal, joined in a **graph triangle**. An independent set can take at most one vertex per triangle: it "picks the literal that satisfies this clause".
2. **Consistency edges.** Join every vertex labelled x to every vertex labelled ¬x, in any clause. You can't pick x in one clause and ¬x in another.
3. Set the target size **k** equal to the number of clauses **m**.

The output instance, in symbols:

```formula
|V| = 3m
k = m
where
|V|: the number of vertices in the graph the reduction builds
m: the number of clauses in the 3-CNF formula φ
φ: phi, the input 3-CNF formula (an AND of clauses, each an OR of 3 literals)
k: the independent-set size the reduction asks for
In words: three vertices per clause, and we ask for an independent set with one vertex per clause.
```

## Key takeaways

- Independent sets have no internal edges and are easy to verify.
- Each clause becomes a triangle of literal occurrences.
- Consistency edges forbid complementary literals; the target equals the clause count.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
