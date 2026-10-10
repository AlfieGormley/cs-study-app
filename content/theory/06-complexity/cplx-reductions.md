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

An arrow from A down to B means A reduces to B, written with the symbol ≤_p:

```formula
A ≤_p B
x ∈ A  iff  f(x) ∈ B
where
A: the problem we already know is hard (higher up the map), e.g. 3-SAT
B: the problem we want to show is hard (lower down the map), e.g. IS
≤_p: "polynomial-time reduces to": a polynomial-time translation maps every instance of A to an instance of B with the same yes/no answer, so B is at least as hard as A
x: any instance (input) of problem A
f: the reduction: an algorithm that turns an instance of A into an instance of B, running in polynomial time (at most about n^k steps for an input of n bits and some fixed k)
f(x): the instance of B that f builds from x
∈: "is a yes-instance of": x ∈ A means x is an input whose answer for problem A is yes
In words: A reduces to B when a fast translation turns every A-question into a B-question with exactly the same answer. Then a fast algorithm for B would give one for A, so B is at least as hard as A.
```

So once A is NP-hard, every problem below it on the map is NP-hard too. For example, 3-SAT reduces to IS (Independent Set), and IS reduces to VC (Vertex Cover), so VC is NP-hard.

## 3-SAT to Independent Set

**Independent Set (IS)**: given a graph G and integer k, is there a set of k vertices with no edge between any two of them? Written out with symbols:

```formula
S ⊆ V   and   |S| = k
{u, v} ∉ E   for all u, v ∈ S
where
G: the input graph, made of a vertex set V and an edge set E
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
N_pairs = k × (k − 1) / 2 = O(k^2)
N_pairs = 3 × 2 / 2 = 3   for k = 3
where
N_pairs: the number of vertex pairs the verifier must look up in E
k: the size of the claimed independent set
O(k^2): Big O: grows at most as fast as a constant times k squared, for large k
In words: checking a claimed independent set of k vertices takes about k squared over 2 edge look-ups, which is polynomial, so IS is in NP.
```

Now the reduction. It starts from a **3-CNF formula** φ: an AND of m clauses, where each clause is an OR of exactly 3 **literals** (a variable such as x or its negation ¬x). Given φ:

1. **Clause gadget.** For each clause, create 3 vertices, one per literal, joined in a **triangle**. An independent set can take at most one vertex per triangle: it "picks the literal that satisfies this clause".
2. **Consistency edges.** Join every vertex labelled x to every vertex labelled ¬x, in any clause. You can't pick x in one clause and ¬x in another.
3. Set the target size **k** equal to the number of clauses **m**.

The output instance, in symbols:

```formula
|V| = 3 × m
k = m
where
|V|: the number of vertices in the graph the reduction builds
m: the number of clauses in the 3-CNF formula φ
φ: phi, the input 3-CNF formula (an AND of clauses, each an OR of 3 literals)
k: the independent-set size the reduction asks for
In words: three vertices per clause, and we ask for an independent set with one vertex per clause.
```

### A worked instance

Here is a formula with m = 3 clauses over 4 variables:

```formula
φ = (x1 ∨ x2 ∨ ¬x3)
  ∧ (¬x1 ∨ x3 ∨ x4)
  ∧ (¬x2 ∨ ¬x3 ∨ ¬x4)
where
φ: phi, the whole 3-CNF formula; it is true when every bracketed clause is true
x1, x2, x3, x4: Boolean variables, each set to true or false
¬: NOT: ¬x3 is true exactly when x3 is false
∨: OR: a clause is true when at least one of its 3 literals is true
∧: AND: joins the clauses; φ is true only when all of them are true
In words: three clauses, C1, C2 and C3 in order; φ is satisfiable if some true/false setting of x1 to x4 makes at least one literal true in every clause.
```

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

Counting the graph:

```formula
|V| = 3 × m = 3 × 3 = 9
|E| = 3 × m + 5 = 9 + 5 = 14
k = m = 3
where
|V|: the number of vertices
m: the number of clauses, here 3
|E|: the number of edges: 3 triangle edges per clause plus the 5 consistency edges drawn above
k: the independent-set size asked for
In words: 9 vertices, 14 edges, and we ask for an independent set of size 3, one vertex per clause.
```

Take the assignment x1 = true, x2 = false, x3 = true (x4 can be anything). Each clause then has a true literal:

```formula
C1 = x1 ∨ x2 ∨ ¬x3 = T ∨ F ∨ F = T
C2 = ¬x1 ∨ x3 ∨ x4 = F ∨ T ∨ x4 = T
C3 = ¬x2 ∨ ¬x3 ∨ ¬x4 = T ∨ F ∨ ¬x4 = T
where
C1, C2, C3: the three clauses of φ
x1, x2, x3, x4: Boolean variables; here x1 = T, x2 = F, x3 = T, x4 either
T: true
F: false
¬: NOT: flips true and false
∨: OR: true when at least one part is true
In words: with x1 true, x2 false and x3 true, every clause contains a true literal whatever x4 is, so φ is satisfied.
```

Pick one true literal from each clause: x1 from C1, x3 from C2, ¬x2 from C3. These three vertices are in different triangles, and no two are complementary, so they form an independent set of size 3.

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

For a no-instance, take all 8 clauses over x1, x2, x3 (each one rules out one assignment, so φ is unsatisfiable). Each variable appears plain in 4 clauses and negated in the other 4, which fixes the size of the graph:

```formula
|V| = 3 × m = 3 × 8 = 24
E_tri = 3 × m = 24
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

Running `has_is(V, E, 8)` on that graph returns `None`. I also ran 300 random 3-CNF formulas on 3 to 5 variables through both checks; `satisfiable` and `has_is` agreed every time.

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
|V| = 3 × m
|E| ≤ 3 × m × (3 × m − 1) / 2 = O(m^2)
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

## Independent Set, Vertex Cover and Clique

A **vertex cover** is a set C of vertices touching every edge: every edge has at least one end in C. The key observation links it to independent sets:

```formula
S ∈ I(G)  iff  (V ∖ S) ∈ C(G)
f(G, k) = (G, n − k)
where
S: any set of vertices of the graph G
I(G): the collection of all independent sets of G (vertex sets with no edge inside them)
C(G): the collection of all vertex covers of G (vertex sets touching every edge)
∈: "is a member of"
G: the input graph, with vertex set V
V: the set of all vertices of G
∖: set difference: V ∖ S is every vertex of V that is not in S
n: the number of vertices in G
k: the independent-set size asked for
f: the reduction from Independent Set to Vertex Cover
f(G, k): the Vertex Cover instance it outputs: the same graph, with target size n − k
In words: a set is independent exactly when the vertices left over touch every edge, so asking for an independent set of size k is the same as asking for a vertex cover of size n − k.
```

Why the first line holds: if no edge has both ends in S, every edge has at least one end outside S, and vice versa. So the reduction doesn't even change the graph; it only changes the number. For example, a 10-vertex graph with an independent set of size 4 has a vertex cover of size 10 − 4 = 6.

A **clique** is a set of vertices all joined to each other. S is independent in G exactly when S is a clique in the **complement** graph Ḡ (same vertices, edges exactly where G has none):

```formula
f(G, k) = (Ḡ, k)
t_build = O(n^2)
where
G: the input graph
Ḡ: "G-bar", the complement graph: the same vertices as G, with an edge between two vertices exactly when G has no edge there
k: the target size, unchanged
f: the reduction from Independent Set to Clique
n: the number of vertices in G
t_build: the number of steps needed to build Ḡ
O(n^2): Big O: grows at most as fast as a constant times n squared, because Ḡ is built by checking each of the about n²/2 vertex pairs once
In words: to ask for an independent set of size k, ask for a clique of size k in the complement graph. Building the complement means visiting every pair of vertices, about n squared over 2 steps.
```

```
 G: 1-2, 2-3        complement: 1-3
 {1,3} independent  {1,3} a clique
 {2} covers both edges of G
```

I checked the IS/VC equivalence by brute force on a 5-vertex graph, over every one of the 32 vertex subsets.

These three problems are the same problem viewed three ways. Yet they behave very differently once you approximate (lesson 4). Vertex cover has a simple factor-2 approximation, while clique has a much worse limit:

```formula
ρ_VC ≤ 2
ρ_CLIQUE > n^(1 − ε)   if P ≠ NP
ρ_CLIQUE > 1000^0.99 ≈ 933   for n = 1000
where
ρ_VC: the best approximation ratio known for vertex cover in polynomial time: the returned cover is at most 2 times the smallest
ρ_CLIQUE: the approximation ratio any polynomial-time clique algorithm can promise: how many times smaller than the largest clique its answer might be
n: the number of vertices in the graph
ε: epsilon, any fixed positive number, however small; the third line uses ε = 0.01
≈: approximately equal to
≠: is not equal to
≤: is at most
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps for some fixed k)
NP: the class NP (nondeterministic polynomial time): decision problems whose yes-answers have a short certificate checkable in polynomial time
In words: vertex cover can always be solved to within a factor of 2, but unless P equals NP no polynomial-time algorithm can promise a clique within a factor of n to the power 0.99 (or any power below 1) of the largest one. On a 1,000-vertex graph that is a factor of about 933.
```

A guarantee that weak is almost useless. The exact reductions above preserve yes/no answers, not approximation ratios.

## Vertex Cover to Set Cover

**Set Cover**: given a universe U, a family of subsets, and k, can k of the subsets cover all of U?

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
k_SC: the number of sets the Set Cover instance may use
In words: the elements to cover are the edges, and each vertex becomes the set of edges it touches. Choosing k vertices that touch every edge is exactly choosing k sets that cover every element.
```

Set Cover is therefore NP-complete, and Vertex Cover is the special case where every element (edge) is in exactly two sets. For a star with centre 0 and leaves 1 to 4, U holds the 4 edges, there are 5 sets, and the centre's set alone covers U, matching the vertex cover {0}.

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

## Pitfalls that invalidate a reduction

1. **Wrong direction.** To show X is hard, map *from* the known hard problem *to* X.
2. **Only one direction proved.** You need both directions: every yes-instance must map to a yes-instance, *and* every instance that maps to a yes-instance must itself be a yes-instance (equivalently, no-instances map to no-instances). Many broken proofs show only that satisfying assignments give solutions.
3. **Using the answer.** The reduction can't "first find a satisfying assignment". It must run in polynomial time without solving the problem.
4. **Exponential blow-up.** Encoding every possible assignment, or writing numbers in unary, breaks polynomial time.
5. **Forgetting membership.** Hardness plus a reduction gives NP-hard; you still need to show X is in NP to claim NP-complete.

> [!note] Karp versus Cook reductions
> Everything here is a **many-one (Karp)** reduction: one call to B, answer passed through unchanged. A **Turing (Cook)** reduction may call B many times and post-process. Turing reductions are more powerful; for example, they make SAT and UNSAT reduce to each other trivially, which blurs NP versus coNP. NP-completeness is standardly defined with Karp reductions.

## Key takeaways
- A reduction is a polynomial-time map preserving yes/no answers, proved correct in both directions.
- 3-SAT reduces to IS: one triangle per clause, edges between complementary literals, target size = number of clauses.
- A set of vertices is independent exactly when the other vertices form a vertex cover, and exactly when it is a clique in the complement graph.
- Vertex Cover reduces to Set Cover: elements are edges, sets are the edges at each vertex.
- Check small reductions by brute force: build the instance, solve both sides exhaustively, and compare on random inputs.

## Further reading
- [Polynomial-time reduction — Wikipedia](https://en.wikipedia.org/wiki/Polynomial-time_reduction)
- [Independent set (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Independent_set_(graph_theory))
- [Vertex cover — Wikipedia](https://en.wikipedia.org/wiki/Vertex_cover)
- [Clique problem — Wikipedia](https://en.wikipedia.org/wiki/Clique_problem)
- [Set cover problem — Wikipedia](https://en.wikipedia.org/wiki/Set_cover_problem)
- [Karp's 21 NP-complete problems — Wikipedia](https://en.wikipedia.org/wiki/Karp%27s_21_NP-complete_problems)
