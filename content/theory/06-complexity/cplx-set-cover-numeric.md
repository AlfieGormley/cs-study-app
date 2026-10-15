---
id: cplx-set-cover-numeric
title: "Edges as elements and numeric reductions"
level: intermediate
minutes: 4
summary: "Vertex Cover reduces to Set Cover with edges as elements."
sourceLesson: cplx-reductions
---

## Vertex Cover to Set Cover

**Set Cover**: given a universe U, a family of subsets, and k, can at most k of the subsets cover all of U?

From a Vertex Cover instance (G, k), build a Set Cover instance:

```formula
U = E
S_v = { {v, w} ∈ E }
k_SC = k
where
U: the universe: the set of elements that must all be covered
E: the set of edges of the graph G
G: the input graph of the Vertex Cover instance
v: any vertex of G; there is one set per vertex
S_v: the set of edges that touch vertex v (the edges incident to v)
w: any other vertex joined to v by an edge, so {v, w} is an edge with v at one end
∈: "is a member of"
k: the vertex cover size asked for
k_SC: the count of subsets in the family the Set Cover instance may use
In words: the elements to cover are the edges, and each vertex becomes the set of edges it touches. Choosing k vertices that touch every edge is exactly choosing k sets that cover every element.
```

Set Cover is in NP because a chosen family can be checked by taking its union. Combined with this reduction, Set Cover is therefore NP-complete, and Vertex Cover is the special case where every element (edge) is in exactly two sets. For a star with centre 0 and leaves 1 to 4, U holds the 4 edges, there are 5 sets, and the centre's set alone covers U, matching the vertex cover {0}.

## Other classic reductions, briefly

- **3-SAT to 3-colouring.** A "palette" triangle with colours TRUE, FALSE, BASE; each variable is an edge x–¬x joined to BASE (so one is TRUE, one FALSE); each clause is a small OR-gadget that can be properly coloured only if at least one of its literals is TRUE.
- **3-SAT to Subset Sum.** Each literal and clause becomes a large decimal number with one digit column per variable and per clause, so that hitting the target forces one choice per variable and at least one true literal per clause. The numbers have one digit per variable and per clause (sized below), which is why the problem is only weakly NP-complete.
- **Hamiltonian cycle to TSP.** Edges weight 1, non-edges weight 2, and a tour-length budget equal to the number of vertices.

The Subset Sum numbers are short to write but huge in value:

```formula
d = n + m
N < 10^d
b ≈ d × log_2(10) ≈ 3.32 × d
d = 4 + 5 = 9   for n = 4, m = 5
N < 10^9
b ≈ 3.32 × 9 ≈ 30
where
d: the number of decimal digits in each number the reduction builds
n: the number of variables in the 3-SAT formula
m: the number of clauses in the 3-SAT formula
N: the value of any one of those numbers
b: the number of bits needed to write N down
log_2(10): log base 2 of 10, about 3.32: the number of bits one decimal digit is worth
≈: approximately equal to
In words: each number has one digit per variable and per clause, so writing it takes only a polynomial number of bits, but its value grows exponentially with the formula size.
```

For a formula with 4 variables and 5 clauses, each number has 9 digits: values up to a billion, written in about 30 bits. The reduction is polynomial because it writes the numbers in binary or decimal. Subset Sum's dynamic program runs in time proportional to the target's value, which here is exponential in the number of variables plus clauses, so the reduction does not contradict Subset Sum being solvable in pseudo-polynomial time. Problems hard only when their numbers are huge are called **weakly NP-complete**.

## Key takeaways

- Vertex Cover reduces to Set Cover with edges as elements.
- Literal and clause gadgets also encode colouring and subset sum.
- Huge numeric values are compatible with polynomial-size binary encodings.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
