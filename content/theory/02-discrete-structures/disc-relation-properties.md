---
id: disc-relation-properties
title: "Relations and their four properties"
level: basic
minutes: 5
summary: "A binary relation chooses ordered pairs and can be represented by a matrix or directed graph."
sourceLesson: disc-relations
---

A function links each input to exactly one output. A **binary relation** is the looser idea: any collection of links between things. "Follows" on a social network, "depends on" between packages, "is congruent to mod 7" between integers and "happened before" between events in a distributed system are all relations.

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

Test them on “less than or equal to” over the numbers 1, 2 and 3:

```formula
2 ≤ 2
1 ≤ 2
not 2 ≤ 1
1 ≤ 2 and 2 ≤ 3   ⇒   1 ≤ 3
where
≤: is less than or equal to
⇒: implies
In words: Every number is at most itself, reverse links need not hold, and two comparisons in the same direction chain. These show reflexivity, failure of symmetry, and the transitive pattern.
```

In the matrix: reflexive means the diagonal is all 1s, symmetric means the matrix equals its transpose. In the graph: reflexive means a self-loop on every node, symmetric means every edge has a reverse edge, transitive means every two-step path has a shortcut edge.

> [!warning] Antisymmetric is not "not symmetric"
> Antisymmetric only forbids two-way links between *different* elements. Equality (=) is both symmetric and antisymmetric. The relation {(1, 2), (2, 1), (1, 3)} is neither: (1, 2) has a reverse, but (1, 3) doesn't.

Some everyday examples:

- **≤ on integers**: reflexive, antisymmetric, transitive. Not symmetric.
- **< on integers**: not reflexive (irreflexive), antisymmetric (vacuously), transitive.
- **"Is a friend of"**: symmetric, usually not transitive.
- **"Follows" on a social network**: none of the four in general.

## Key takeaways

- A binary relation chooses ordered pairs and can be represented by a matrix or directed graph.
- Reflexivity, symmetry, antisymmetry and transitivity describe different constraints on those pairs.

## Further reading

- [Binary relation — Wikipedia](https://en.wikipedia.org/wiki/Binary_relation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
