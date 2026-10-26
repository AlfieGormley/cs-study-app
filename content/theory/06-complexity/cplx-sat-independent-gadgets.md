---
id: cplx-sat-independent-gadgets
title: "Building clause and consistency gadgets"
level: intermediate
minutes: 4
summary: "Independent sets have no internal edges and are easy to verify."
sourceLesson: cplx-reductions
---

## 3-SAT to Independent Set

**Independent Set (IS)**: given a graph G and integer k, is there a set of k vertices with no edge between any two of them? A larger independent set also contains one of exactly the requested size.

IS is in NP: the certificate lists the selected vertices. Check that they are distinct valid vertices and that no selected pair is an edge. There are only quadratically many pairs, so this is polynomial work.

Now the reduction. It starts from a **3-CNF formula** φ: an AND of m clauses, where each clause is an OR of exactly 3 **literals** (a variable such as x or its negation ¬x). Given φ:

1. **Clause gadget.** For each clause, create 3 vertices, one per literal, joined in a **graph triangle**. An independent set can take at most one vertex per triangle: it "picks the literal that satisfies this clause".
2. **Consistency edges.** Join every vertex labelled x to every vertex labelled ¬x, in any clause. You can't pick x in one clause and ¬x in another.
3. Set the target size **k** equal to the number of clauses **m**.

Every literal occurrence gets its own vertex, even when the same literal appears elsewhere. The target counts clauses, not distinct variables: reaching it forces exactly one choice from each triangle.

## Key takeaways

- Independent sets have no internal edges and are easy to verify.
- Each clause becomes a triangle of literal occurrences.
- Consistency edges forbid complementary literals; the target equals the clause count.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
