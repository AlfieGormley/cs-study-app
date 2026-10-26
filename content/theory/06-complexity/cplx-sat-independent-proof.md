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
from itertools import combinations

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

phi = [[1, 2, -3], [-1, 3, 4], [-2, -3, -4]]
V, E, k = sat_to_is(phi)
print(len(V), len(E), k)   # 9 14 3
print(has_is(V, E, k))
# ((0, 0, 1), (1, 1, 3), (2, 0, -2))
```

Literals are integers: 3 means x3, −3 means ¬x3. The independent set found is exactly x1 from C1, x3 from C2 and ¬x2 from C3.

For a no-instance, take all eight sign patterns over three distinct variables. Every assignment falsifies one clause. The construction therefore cannot have an independent set taking one vertex from every clause. Exhaustive tests can check this small case, but the two-direction proof below establishes correctness for all inputs.

### Why it's correct (both directions)

The claim has two directions: the formula is satisfiable exactly when the graph has an independent set whose size equals the clause count.

Each direction, and the running time:

- **If φ is satisfiable, there is an independent set of size m.** Fix a satisfying assignment. Each clause has a true literal; pick its vertex. One per triangle, so no triangle edges. All picked literals are true, so none is the negation of another, so no consistency edges. Size m.
- **If there is an independent set of size m, φ is satisfiable.** At most one vertex per triangle, and there are m triangles, so exactly one per clause. No consistency edge is inside the set, so the picked literals never include both x and ¬x. Set those literals true (others arbitrarily). Every clause has a true literal.
- **Polynomial.** Each clause creates three vertices. Checking each pair creates at most quadratically many edges in the clause count, so the construction is polynomial.

> [!tip] Gadget pattern
> Triangles enforce "choose exactly one" (given a budget of one vertex per clause). Edges between conflicting choices enforce consistency. You'll see this pattern again and again.

More generally, an assignment satisfying a given number of clauses provides an independent set of that size by choosing one true occurrence per satisfied clause. Conversely, any independent set extends to a consistent assignment satisfying every clause represented by a picked vertex. Thus the maximum independent-set size equals the maximum number of simultaneously satisfiable clauses; for all eight sign patterns on three variables, that number is seven.

## Key takeaways

- The executable construction uses a vertex per occurrence.
- Both directions of the proof are necessary for a valid reduction.
- Exhaustive checks illustrate the result on finite examples; the proof covers all instances.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
