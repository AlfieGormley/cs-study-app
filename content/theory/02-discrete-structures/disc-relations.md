---
id: disc-relations
title: Relations, equivalence classes and partial orders
level: basic
minutes: 17
summary: Binary relations and their properties, equivalence relations and the partitions they create, partial orders, Hasse diagrams, topological sorting and closures.
---

A function links each input to exactly one output. A **relation** is the looser idea: any collection of links between things. "Follows" on a social network, "depends on" between packages, "is congruent to mod 7" between integers and "happened before" between events in a distributed system are all relations.

Two special kinds of relation do a huge amount of work in computer science. **Equivalence relations** say when two things count as "the same" and split a set into groups. **Partial orders** say when one thing must come "before" another, and are what a build system or a task scheduler sorts.

## What a relation is

A **binary relation** from a set A to a set B is just a set of ordered pairs: it lists which elements of A are linked to which elements of B. A relation on a single set uses pairs from that set on both sides.

```formula
R ⊆ A × B
a R b   means   (a, b) ∈ R
where
R: the relation, written as the set of linked pairs
A, B: the sets the first and second parts of each pair come from
×: Cartesian product: A × B is the set of every ordered pair whose first part is in A and second part is in B
⊆: is a subset of
a: an element of A
b: an element of B
a R b: infix shorthand, read "a is related to b by R"
( , ): an ordered pair: (a, b) and (b, a) are different
∈: is an element of
In words: a relation is any chosen set of pairs (for a relation on one set A, take B to be A as well). Writing a R b is just a shorter way to say that the pair (a, b) is in the set.
```

For example, "is less than" on {1, 2, 3} is the relation {(1, 2), (1, 3), (2, 3)}: 1 < 2 holds, so (1, 2) is in it, while 2 < 1 fails, so (2, 1) is not.

Three equivalent pictures of the same relation on {1, 2, 3}:

```
pairs:   {(1,1), (1,2), (2,3)}

matrix:      1  2  3
          1  1  1  0
          2  0  0  1
          3  0  0  0

graph:   1 --> 2 --> 3
         plus a self-loop 1 --> 1
```

The matrix view shows how many relations a set has: every cell is independently 0 or 1.

```formula
N_rel = 2^(n^2)
N_rel = 2^(3^2) = 2^9 = 512   for n = 3
where
N_rel: the number of different relations on the set
n: the number of elements in the set
n^2: n × n, the number of cells in the n-by-n matrix (one per ordered pair)
2^(n^2): 2 multiplied by itself n^2 times: two choices (0 or 1) per cell
In words: a 3-element set has 9 possible ordered pairs, each either in or out, so 2^9 = 512 relations.
```

The count explodes quickly: a 4-element set has 16 possible pairs and already 65,536 relations (16 copies of 2 multiplied together). The graph view is why so much of graph theory is really about relations.

## The four key properties

For a relation R on a set A:

| Property | Definition |
|---|---|
| Reflexive | every element is related to itself |
| Symmetric | every link has its reverse link |
| Antisymmetric | two distinct elements are never linked both ways |
| Transitive | links chain: two steps imply a direct link |

In symbols, one line per row of the table:

```formula
a R a   for every a ∈ A
a R b   ⇒   b R a
a R b and b R a   ⇒   a = b
a R b and b R c   ⇒   a R c
where
R: the relation, a set of pairs from A
A: the set the relation is on
a, b, c: any elements of A (each line must hold for every choice)
a R b: a is related to b, that is, (a, b) is in R
∈: is an element of
⇒: implies: whenever the left side holds, the right side must hold too
In words: reflexive means everything relates to itself; symmetric means links go both ways; antisymmetric means the only way to have links both ways is between an element and itself; transitive means a two-step chain always has a direct link.
```

Test them on "less than or equal to" over {1, 2, 3}: 2 ≤ 2 (reflexive holds), 1 ≤ 2 but not 2 ≤ 1 (symmetric fails), and 1 ≤ 2 and 2 ≤ 3 give 1 ≤ 3 (transitive holds).

In the matrix: reflexive means the diagonal is all 1s, symmetric means the matrix equals its transpose. In the graph: reflexive means a self-loop on every node, symmetric means every edge has a reverse edge, transitive means every two-step path has a shortcut edge.

> [!warning] Antisymmetric is not "not symmetric"
> Antisymmetric only forbids two-way links between *different* elements. Equality (=) is both symmetric and antisymmetric. The relation {(1, 2), (2, 1), (1, 3)} is neither: (1, 2) has a reverse, but (1, 3) doesn't.

Some everyday examples:

- **≤ on integers**: reflexive, antisymmetric, transitive. Not symmetric.
- **< on integers**: not reflexive (irreflexive), antisymmetric (vacuously), transitive.
- **"Is a friend of"**: symmetric, usually not transitive.
- **"Follows" on a social network**: none of the four in general.

## Equivalence relations

A relation that is **reflexive, symmetric and transitive** is an **equivalence relation**. It formalises "the same in the way we care about".

Examples:

- **Congruence modulo n**: two integers are related when they leave the same remainder after division by n (see below). Mod 3 groups integers by remainder.
- **Same connected component** in an undirected graph.
- **Case-insensitive equality** of strings: "Hello" and "HELLO" are equivalent.
- **Same hash bucket**: two keys are related when the hash function sends them to the same value. Any relation of the form "same output of some function" is an equivalence relation.

The first and last examples in symbols:

```formula
a ≡ b (mod n)   means   n | (a − b)
17 − 5 = 12 = 4 × 3
so   17 ≡ 5 (mod 3)
x ~ y   means   f(x) = f(y)
where
a, b: integers
n: the modulus, a positive integer (3 in the example)
≡: is congruent to: the two numbers leave the same remainder after division by n
mod: modulo: names the number n we divide by
|: divides: n | m means m is a whole-number multiple of n
x, y: any two elements, such as two hash keys
~: is equivalent to (the relation being defined)
f: any function, such as a hash function h or "birth month"
f(x): the output of f for input x
In words: a and b are congruent mod n when their difference is a multiple of n; 17 and 5 both leave remainder 2 when divided by 3. In general, "x and y give the same output" is always reflexive, symmetric and transitive, because equality of outputs is.
```

The **equivalence class** of an element is everything equivalent to it:

```formula
[a] = { x ∈ A : x ~ a }
where
[a]: the equivalence class of a
a: an element of the set A
A: the set the relation is on
x: a stand-in for each element of A
~: the equivalence relation
∈: is an element of
{ x ∈ A : … }: the set of all x in A that make the condition after the colon true
In words: the class of a collects every element equivalent to a, including a itself.
```

The crucial theorem: **the equivalence classes partition the set**. Every element is in exactly one class, and two classes are either identical or disjoint.

For congruence mod 3, the integers split into three classes:

```formula
[0] = {…, −3, 0, 3, 6, …}
[1] = {…, −2, 1, 4, 7, …}
[2] = {…, −1, 2, 5, 8, …}
where
[0], [1], [2]: the equivalence classes of 0, 1 and 2 under congruence mod 3: the integers leaving remainder 0, 1 and 2 when divided by 3
{ }: the set of the things listed inside
…: and so on without end, in both directions
In words: every integer lands in exactly one of three classes by its remainder mod 3. Negative numbers follow the same pattern: −2 = −1 × 3 + 1, so −2 is in [1].
```

The converse holds too: any partition defines an equivalence relation ("in the same block"). So the number of equivalence relations on an n-element set equals the number of partitions, the **Bell number**: 1, 1, 2, 5, 15, 52, … for sets of 0, 1, 2, 3, 4 and 5 elements. For example, {a, b, c} has 5 partitions: everything together, the three ways to pair two elements and leave one alone, and all three apart.

### Equivalence relations in code

The **union-find** (disjoint-set) data structure maintains an equivalence relation as you add facts like "a ~ b". Each class is a tree with a representative at the root. Because the relation is transitive, merging two classes is all you ever need to do.

```python
parent = {}

def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

def union(a, b):
    parent[find(a)] = find(b)

union('a', 'b'); union('b', 'c')
find('a') == find('c')   # True
```

Union-find tracks components for Kruskal's algorithm and can support type-variable unification. Full type unification also needs to handle type structure and checks such as the occurs check.

Python's own contract relies on this theory. Well-behaved value equality is normally an equivalence relation, but Python does not enforce these laws and NaN is a standard exception. Hashable objects that compare equal must have equal hashes, and their hash must stay stable while used as keys.

> [!warning] "Approximately equal" is not an equivalence
> Calling two numbers equal when they are within a small tolerance of each other breaks transitivity, so it cannot be used to bucket values into consistent groups. The example below shows the chain that fails.

```formula
x ~ y   means   |x − y| < 0.1
|0.0 − 0.08| = 0.08   so 0.0 ~ 0.08
|0.08 − 0.16| = 0.08   so 0.08 ~ 0.16
|0.0 − 0.16| = 0.16   so 0.0 ≁ 0.16
where
x, y: any two real numbers
~: "approximately equal", the relation being tested
≁: is not related by ~
| |: around a number, the absolute value: its size ignoring the sign, so |x − y| is the distance between x and y
<: is less than
In words: 0.0 is close to 0.08, and 0.08 is close to 0.16, but 0.0 is not close to 0.16, so the relation is not transitive.
```

## Partial orders

A relation that is **reflexive, antisymmetric and transitive** is a **partial order**. A set with a partial order is a **poset** (partially ordered set). A generic partial order is written with a curly less-than sign:

```formula
a ≼ a
a ≼ b and b ≼ a   ⇒   a = b
a ≼ b and b ≼ c   ⇒   a ≼ c
where
≼: a partial order, read "precedes or equals" or "is below or equal to"
a, b, c: any elements of the set
⇒: implies: whenever the left side holds, the right side must too
In words: everything is below or equal to itself, two different things can't each be below the other, and "below" chains.
```

Examples:

- ≤ on numbers.
- ⊆ on the subsets of a set.
- "Divides" on positive integers (see below).
- "Must be built before" on build targets (taking the reflexive closure).
- "Happened before" on events in a distributed system (Lamport's relation, as a strict order).

Divisibility is worth writing out, because it is the standard example of an order that is not total:

```formula
a | b   means   b = k × a   for some k ∈ ℤ
12 = 4 × 3   so   3 | 12
2 ∤ 3   and   3 ∤ 2
where
|: divides: a | b means b is a whole-number multiple of a
∤: does not divide
a, b: positive integers
k: a whole number, the multiplier
ℤ: the integers …, −2, −1, 0, 1, 2, …
∈: is an element of
In words: a divides b when b is a whole number of copies of a. 3 divides 12, but neither of 2 and 3 divides the other.
```

"Partial" means some pairs may be **incomparable**:

```formula
a ∥ b   means   not a ≼ b and not b ≼ a
{1} ∥ {2}   with ⊆
2 ∥ 3   with |
where
a, b: elements of a poset
∥: is incomparable with
≼: the partial order (here ⊆ or |)
⊆: is a subset of
|: divides
{ }: the set of the things listed inside
In words: two elements are incomparable when neither is below the other. {1} and {2} are not subsets of each other, and neither of 2 and 3 divides the other.
```

If every pair is comparable, it is a **total order** (or linear order), like ≤ on integers or alphabetical order on strings.

A **strict** partial order is irreflexive (nothing is related to itself) and transitive. You get one from a partial order by removing the diagonal, the pairs of each element with itself:

```formula
a ≺ b   means   a ≼ b and a ≠ b
where
≺: the strict order: "is strictly below"
≼: the partial order: "is below or equal to"
a, b: elements of the set
≠: is not equal to
In words: a is strictly below b when it is below or equal to b but not equal to it, just as < is ≤ without the equal case.
```

An acyclic direct-dependency graph need not itself be transitive; its positive-length reachability relation is a strict partial order.

### Hasse diagrams

A **Hasse diagram** draws a poset without clutter: leave out self-loops and any edge implied by transitivity, and put larger elements higher. Here is "divides" on the divisors of 12:

```
        12
       /  \
      4    6
      |  /  \
      2      3
       \    /
        \  /
         1
```

Read upwards: 2 divides 4, and 4 divides 12, so a path upwards means "divides". 4 and 6 are incomparable (no upward path joins them), as are 4 and 3.

Vocabulary that comes up in interviews and papers:

- **Minimal** element: nothing is strictly below it. **Least** (minimum) element: below everything. A poset can have several minimal elements but at most one least element.
- **Chain**: a set of pairwise comparable elements. **Antichain**: pairwise incomparable.
- **Upper bound (order theory)** and **least upper bound (join)**. In the subset order, the join of two sets is their union. Posets where every pair has a join and a meet are **lattices**; state-based CRDTs use a join operation on a semilattice of states; operation-based CRDTs use different delivery and commutativity conditions.

### Topological sorting

A **linear extension** of a poset is a total order that respects it: a list of all the elements in which everything strictly below another element comes earlier.

```formula
a ≺ b   ⇒   pos(a) < pos(b)
where
a, b: elements of the poset
≺: is strictly below in the partial order (for a build: is a prerequisite of)
⇒: implies
pos: the position of an element in the chosen list (1 for first, 2 for second, …)
<: is less than
In words: a valid order never lists something before one of its prerequisites. Elements with no order between them can go either way round.
```

For a finite DAG, finding one is **topological sorting**, and it exists precisely because there are no cycles (a cycle of distinct vertices conflicts with antisymmetry of reachability, and a self-loop would need a target to come strictly before itself).

```python
from graphlib import TopologicalSorter

# target: its prerequisites
deps = {
    'app': {'lib', 'config'},
    'lib': {'utils'},
    'config': set(),
    'utils': set(),
}
ts = TopologicalSorter(deps)
print(list(ts.static_order()))
# e.g. ['config', 'utils', 'lib', 'app']
```

There are usually many valid orders: the incomparable elements can come in any relative order. Build and dependency tools use dependency ordering when prerequisites form a DAG. Cycle policies vary: pip documents an installation fallback for dependency cycles, so not every such tool rejects them.

> [!example] Vector clocks are a partial order
> In a store that tracks versions with vector clocks, each version carries a list of counters, one for each tracked participant. One version is below another when none of its counters is larger. Two versions where neither is below the other are **concurrent**: incomparable in the partial order. Riak and Dynamo-style stores surface these as siblings for the application to merge.

```formula
V ≤ W   means   V_i ≤ W_i   for every i
[2, 1, 0] ≤ [2, 2, 1]
[2, 1, 0] ∥ [1, 2, 0]
where
V, W: two vector clocks: lists of counters, one per participant
V_i, W_i: counter number i in V and in W
i: a position in the list, one per participant
≤: on the left, the order on whole clocks; on the right, ordinary "less than or equal to" on two counters
∥: is incomparable with (concurrent)
[ ]: a vector clock written as its list of counters
In words: one clock is below another when it is behind or level on every counter. [2, 1, 0] and [1, 2, 0] each lead on one counter, so neither is below the other: the two versions were written concurrently.
```

## Closures

Often you have a relation that is "almost" what you want. The **transitive closure** is the smallest transitive relation containing it: it links a to b whenever a chain of one or more links leads from a to b.

```formula
a R⁺ b   means   a R x_1 R x_2 … R x_k R b
1 R 2 and 2 R 3   so   1 R⁺ 3
where
R: the original relation
R⁺: the transitive closure of R, read "R plus"
a, b: elements of the set
x_1, x_2, x_k: the intermediate elements on the chain
k: the number of intermediate steps, which can be 0 (then a R b directly)
…: and so on along the chain
In words: R⁺ adds a direct link for every path of length one or more in R. If 1 links to 2 and 2 links to 3, the closure links 1 to 3.
```

"Can user A reach user B through follows?" and "does package X depend on Y, directly or indirectly?" are transitive-closure questions.

Two standard ways to compute it, viewing the relation as a directed graph:

```formula
T_W = O(n^3)
T_S = O(n × (n + m))
where
T_W: running time of Warshall's algorithm, which works on the adjacency matrix
T_S: running time of a breadth-first or depth-first search (BFS or DFS) from every vertex, using adjacency lists
n: the number of elements (vertices)
m: the number of related pairs (edges)
O( ): big-O: grows no faster than the expression inside, up to a constant factor
In words: Warshall's algorithm costs about n^3 steps whatever the relation looks like; a search from every vertex costs about n searches of n + m steps each.
```

For a sparse relation with 10,000 vertices and 50,000 edges, cubing 10,000 gives a trillion steps while 10,000 × 60,000 is 600 million, so the searches win on the asymptotic bound. That is not a promise of a fixed wall-clock speedup, since constant factors and memory access patterns differ. SQL computes reachability with a recursive CTE.

The **reflexive closure** adds the diagonal, the **symmetric closure** adds reverse edges. The reflexive, symmetric, transitive closure of any relation is an equivalence relation: it groups vertices into connected components after ignoring any edge directions.

## Pitfalls

- **Inconsistent comparators.** Sorting assumes a total (pre)order. A comparator that isn't transitive (say, rock-paper-scissors, or one that compares floats with NaN) can make sort output depend on the input order, or make Java's `TimSort` throw "Comparison method violates its general contract!".
- **NaN breaks reflexivity.** `float('nan') == float('nan')` is `False`, so IEEE 754 floats are not an equivalence relation under `==`. For ordinary float-NaN lookups, retaining the identical key object permits retrieval even though NaN is not equal to itself; another separately created float NaN does not match it.
- **Assuming a total order where only a partial one exists.** Wall-clock timestamps can tie and need not match causality. Lamport timestamps respect causal order but do not detect concurrency; a process-ID tie-breaker can make them total. Vector clocks can expose concurrency under their model.

## Key takeaways
- A relation on a set is any set of ordered pairs of its elements; matrices and directed graphs are two views of the same thing.
- Equivalence relations (reflexive, symmetric, transitive) partition a set into disjoint classes; union-find maintains them incrementally.
- Partial orders (reflexive, antisymmetric, transitive) allow incomparable elements; total orders don't.
- A topological sort is a linear extension of a partial order, and exists exactly when the dependency graph has no cycles.
- Equality, hashing and sorting in real code silently assume these properties; NaN, tolerances and bad comparators break them.

## Further reading
- [Binary relation — Wikipedia](https://en.wikipedia.org/wiki/Binary_relation)
- [Equivalence relation — Wikipedia](https://en.wikipedia.org/wiki/Equivalence_relation)
- [Partially ordered set — Wikipedia](https://en.wikipedia.org/wiki/Partially_ordered_set)
- [Topological sorting — Wikipedia](https://en.wikipedia.org/wiki/Topological_sorting)
- [graphlib — Python docs](https://docs.python.org/3/library/graphlib.html)
- [Vector clock — Wikipedia](https://en.wikipedia.org/wiki/Vector_clock)
