---
id: cplx-reductions
title: Reductions in practice
level: intermediate
minutes: 15
summary: Worked polynomial-time reductions with concrete instances checked in Python, 3-SAT to Independent Set, Independent Set to Vertex Cover and Clique, Vertex Cover to Set Cover, and the mistakes that make a reduction invalid.
---

Cook–Levin gives us one NP-complete problem the hard way. Every other NP-completeness proof is a **reduction**: a recipe that turns instances of a known hard problem into instances of the new one, preserving the yes/no answer.

Designing reductions is a craft. The usual approach is to build **gadgets**: small pieces of the target problem that imitate a variable ("choose true or false") or a constraint ("at least one of these must hold").

## The reduction map

```
        SAT
         |   (CNF + clause splitting)
       3-SAT
      /  |   \
     IS  3-COL SUBSET-SUM
    / \          |
  VC  CLIQUE   KNAPSACK
   |
 SET-COVER   (and many more)
```

An arrow from A down to B means "A ≤p B", so B is NP-hard once A is.

## 3-SAT to Independent Set

**Independent Set (IS)**: given a graph G and integer k, is there a set of k vertices with no edge between any two of them?

IS is in NP: the certificate is the set, checked in O(k²) edge look-ups. Now the reduction. Given a 3-CNF formula φ with m clauses:

1. **Clause gadget.** For each clause, create 3 vertices, one per literal, joined in a **triangle**. An independent set can take at most one vertex per triangle: it "picks the literal that satisfies this clause".
2. **Consistency edges.** Join every vertex labelled x to every vertex labelled ¬x, in any clause. You can't pick x in one clause and ¬x in another.
3. Set **k = m**.

### A worked instance

φ = (x1 ∨ x2 ∨ ¬x3) ∧ (¬x1 ∨ x3 ∨ x4) ∧ (¬x2 ∨ ¬x3 ∨ ¬x4)

```
 C1:   x1 ---- x2       C2:  ¬x1 ---- x3
         \    /                \     /
          ¬x3                    x4

 C3:  ¬x2 ---- ¬x3
         \     /
          ¬x4

 consistency edges (5):
  C1.x1  -- C2.¬x1    C1.x2  -- C3.¬x2
  C1.¬x3 -- C2.x3     C2.x3  -- C3.¬x3
  C2.x4  -- C3.¬x4
```

That's 9 vertices, 9 triangle edges plus 5 consistency edges, and k = 3.

Take the assignment x1 = true, x2 = false, x3 = true (x4 can be anything). Pick a true literal from each clause: x1 from C1, x3 from C2, ¬x2 from C3. These three vertices are in different triangles, and no two are complementary, so they form an independent set of size 3.

### Checking it in Python

```python
from itertools import combinations, product

def sat_to_is(phi):
    # vertex = (clause, position, literal)
    V = [(i, j, l)
         for i, c in enumerate(phi)
         for j, l in enumerate(c)]
    E = set()
    for u, v in combinations(V, 2):
        same = u[0] == v[0]
        clash = u[2] == -v[2]
        if same or clash:
            E.add((u, v))
    return V, E, len(phi)

def has_is(V, E, k):
    for S in combinations(V, k):
        if not any((u, v) in E for u, v
                   in combinations(S, 2)):
            return S
    return None

def true_lit(a, l):
    return a[abs(l) - 1] == (l > 0)

def satisfiable(phi, n):
    for a in product([False, True],
                     repeat=n):
        if all(any(true_lit(a, l)
                   for l in c)
               for c in phi):
            return a
    return None

phi = [[1, 2, -3], [-1, 3, 4], [-2, -3, -4]]
V, E, k = sat_to_is(phi)
print(len(V), len(E), k)   # 9 14 3
print(has_is(V, E, k))
# ((0, 0, 1), (1, 1, 3), (2, 0, -2))
```

Literals are integers: 3 means x3, −3 means ¬x3. The independent set found is exactly x1 from C1, x3 from C2 and ¬x2 from C3.

For a no-instance, take all 8 clauses over x1, x2, x3 (each one rules out one assignment, so φ is unsatisfiable). The construction gives 24 vertices and 72 edges, and `has_is(V, E, 8)` returns `None`. I also ran 300 random 3-CNF formulas on 3 to 5 variables through both checks; `satisfiable` and `has_is` agreed every time.

### Why it's correct (both directions)

- **φ satisfiable ⇒ IS of size m.** Fix a satisfying assignment. Each clause has a true literal; pick its vertex. One per triangle, so no triangle edges. All picked literals are true, so none is the negation of another, so no consistency edges. Size m.
- **IS of size m ⇒ φ satisfiable.** At most one vertex per triangle, and there are m triangles, so exactly one per clause. No consistency edge is inside the set, so the picked literals never include both x and ¬x. Set those literals true (others arbitrarily). Every clause has a true literal.
- **Polynomial.** 3m vertices and at most O(m²) edges.

> [!tip] Gadget pattern
> Triangles enforce "choose exactly one" (given the budget k = m). Edges between conflicting choices enforce consistency. You'll see this pattern again and again.

## Independent Set, Vertex Cover and Clique

A **vertex cover** is a set C of vertices touching every edge. Observe:

**S is independent ⇔ V ∖ S is a vertex cover.**

If no edge has both ends in S, every edge has at least one end outside S, and vice versa. So (G, k) has an independent set of size k iff (G, n − k) has a vertex cover of size n − k. The reduction is f(G, k) = (G, n − k): it doesn't even change the graph.

A **clique** is a set of vertices all joined to each other. S is independent in G iff S is a clique in the **complement** graph Ḡ (same vertices, edges exactly where G has none). So f(G, k) = (Ḡ, k), computed in O(n²).

```
 G: 1-2, 2-3        complement: 1-3
 {1,3} independent  {1,3} a clique
 {2} covers both edges of G
```

I checked the IS/VC equivalence by brute force on a 5-vertex graph, over every one of the 32 vertex subsets.

These three problems are the same problem viewed three ways. Yet they behave very differently once you approximate (lesson 4): vertex cover has a simple factor-2 approximation, while clique cannot be approximated within n^(1−ε) for any ε > 0 unless P = NP.

## Vertex Cover to Set Cover

**Set Cover**: given a universe U, a family of subsets, and k, can k of the subsets cover all of U?

From (G, k): let U be the set of edges, and for each vertex v create the set of edges incident to v. Choosing k vertices that touch every edge is exactly choosing k sets that cover U. Set Cover is therefore NP-complete, and Vertex Cover is the special case where every element (edge) is in exactly two sets.

## Other classic reductions, briefly

- **3-SAT to 3-colouring.** A "palette" triangle with colours TRUE, FALSE, BASE; each variable is an edge x–¬x joined to BASE (so one is TRUE, one FALSE); each clause is a small OR-gadget that can be properly coloured only if at least one of its literals is TRUE.
- **3-SAT to Subset Sum.** Each literal and clause becomes a large decimal number with one digit column per variable and per clause, so that hitting the target forces one choice per variable and at least one true literal per clause. The numbers have O(n + m) digits, which is why the problem is only weakly NP-complete.
- **Hamiltonian cycle to TSP.** Edges weight 1, non-edges weight 2, budget n.

## Pitfalls that invalidate a reduction

1. **Wrong direction.** To show X is hard, map *from* the known hard problem *to* X.
2. **Only one direction proved.** You need yes ⇒ yes *and* yes ⇐ yes (equivalently, no ⇒ no). Many broken proofs show only that satisfying assignments give solutions.
3. **Using the answer.** The reduction can't "first find a satisfying assignment". It must run in polynomial time without solving the problem.
4. **Exponential blow-up.** Encoding every possible assignment, or writing numbers in unary, breaks polynomial time.
5. **Forgetting membership.** Hardness plus a reduction gives NP-hard; you still need X ∈ NP to claim NP-complete.

> [!note] Karp versus Cook reductions
> Everything here is a **many-one (Karp)** reduction: one call to B, answer passed through unchanged. A **Turing (Cook)** reduction may call B many times and post-process. Turing reductions are more powerful; for example, they make SAT and UNSAT reduce to each other trivially, which blurs NP versus coNP. NP-completeness is standardly defined with Karp reductions.

## Key takeaways
- A reduction is a polynomial-time map preserving yes/no answers, proved correct in both directions.
- 3-SAT ≤p IS: one triangle per clause, edges between complementary literals, k = number of clauses.
- S independent ⇔ V ∖ S is a vertex cover ⇔ S is a clique in the complement graph.
- Vertex Cover ≤p Set Cover: elements are edges, sets are the edges at each vertex.
- Check small reductions by brute force: build the instance, solve both sides exhaustively, and compare on random inputs.

## Further reading
- [Polynomial-time reduction — Wikipedia](https://en.wikipedia.org/wiki/Polynomial-time_reduction)
- [Independent set (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Independent_set_(graph_theory))
- [Vertex cover — Wikipedia](https://en.wikipedia.org/wiki/Vertex_cover)
- [Clique problem — Wikipedia](https://en.wikipedia.org/wiki/Clique_problem)
- [Set cover problem — Wikipedia](https://en.wikipedia.org/wiki/Set_cover_problem)
- [Karp's 21 NP-complete problems — Wikipedia](https://en.wikipedia.org/wiki/Karp%27s_21_NP-complete_problems)
