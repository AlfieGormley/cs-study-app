---
id: cplx-sat-independent-proof
title: "Executing and proving the graph reduction"
level: intermediate
minutes: 5
summary: "The executable construction uses a vertex per occurrence."
sourceLesson: cplx-reductions
---

Use the same construction as the preceding units: one triangle per three-literal clause, consistency edges between complementary occurrences, and a target equal to the number of clauses. In the code, a positive integer represents a variable and a negative integer its negation.

### Checking it in Python

```python
from itertools import combinations, product

def sat_to_is(phi):
    # vertex = (clause, position, literal)
    V = [(i, j, l)
         for i, c in enumerate(phi)
         for j, l in enumerate(c)]
    # Edges forbid same-clause or opposite
    # picks.
    E = set()
    for u, v in combinations(V, 2):
        same = u[0] == v[0]
        clash = u[2] == -v[2]
        if same or clash:
            E.add((u, v))
    return V, E, len(phi)

def has_is(V, E, k):
    # Exhaustive search is only for tiny
    # audits.
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

For a no-instance, take all 8 clauses over x1, x2, x3 (each one rules out one assignment, so φ is unsatisfiable). Each variable appears plain in 4 clauses and negated in the other 4, which fixes the size of the graph:

```formula
|V| = 3m = 3 × 8 = 24
E_tri = 3m = 24
E_con = n × 4 × 4 = 3 × 16 = 48
|E| = 24 + 48 = 72
where
|V|: the number of vertices
m: the number of clauses, here 8
n: the number of variables, here 3 (x1, x2, x3)
E_tri: the number of triangle edges, 3 per clause
E_con: the number of consistency edges: each of the 4 plain copies of a variable is joined to each of its 4 negated copies
|E|: the total number of edges
In words: 24 vertices and 72 edges, and since φ is unsatisfiable there is no independent set of size 8.
```

Running `has_is(V, E, 8)` on that graph returns `None`. A reproducible audit also compares both checks on 300 seeded random 3-CNF formulas over three to five variables. Finite agreement supports the implementation; the proof below establishes the reduction for every instance.

### Why it's correct (both directions)

The claim to prove is an "if and only if":

```formula
φ ∈ 3-SAT  iff  (G, m) ∈ IS
where
φ: phi, the input 3-CNF formula, with m clauses
3-SAT: the set of satisfiable 3-CNF formulas; φ ∈ 3-SAT means φ is satisfiable
G: the graph the reduction builds from φ
m: the number of clauses, used as the target size k
IS: the set of yes-instances of Independent Set: pairs (graph, k) whose graph has an independent set of size k
∈: "is a yes-instance of"
In words: the formula is satisfiable exactly when the graph built from it has an independent set with one vertex per clause.
```

Each direction, and the running time:

- **If φ is satisfiable, there is an independent set of size m.** Fix a satisfying assignment. Each clause has a true literal; pick its vertex. One per triangle, so no triangle edges. All picked literals are true, so none is the negation of another, so no consistency edges. Size m.
- **If there is an independent set of size m, φ is satisfiable.** At most one vertex per triangle, and there are m triangles, so exactly one per clause. No consistency edge is inside the set, so the picked literals never include both x and ¬x. Set those literals true (others arbitrarily). Every clause has a true literal.
- **Polynomial.** The graph is small compared with φ:

```formula
|V| = 3m
|E| ≤ 3m × (3m − 1) / 2 = O(m^2)
where
|V|: the number of vertices built
|E|: the number of edges built; at most every pair of vertices
m: the number of clauses in φ
O(m^2): Big O: grows at most as fast as a constant times m squared
≤: is at most
In words: the graph has 3 vertices per clause and at most about m squared edges, so building it takes polynomial time.
```

> [!tip] Gadget pattern
> Triangles enforce "choose exactly one" (given a budget of one vertex per clause). Edges between conflicting choices enforce consistency. You'll see this pattern again and again.

More generally, an assignment satisfying a given number of clauses provides an independent set of that size by choosing one true occurrence per satisfied clause. Conversely, any independent set extends to a consistent assignment satisfying every clause represented by a picked vertex. Thus the maximum independent-set size equals the maximum number of simultaneously satisfiable clauses; for all eight sign patterns on three variables, that number is seven.

## Key takeaways

- The executable construction uses a vertex per occurrence.
- Both directions of the proof are necessary for a valid reduction.
- Exhaustive checks illustrate the result on finite examples; the proof covers all instances.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
