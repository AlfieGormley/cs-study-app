---
id: disc-partial-orders-hasse
title: "Partial orders and Hasse diagrams"
level: basic
minutes: 4
summary: "Partial orders allow incomparable pairs; total orders compare every pair."
sourceLesson: disc-relations
---

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

- **Minimal element**: nothing is strictly below it. **Maximal element** means nothing is strictly above it. **Least element** (minimum): below everything; **greatest element** means above everything. A poset can have several minimal elements but at most one least element.
- A **chain in a poset** is a set of pairwise comparable elements. **Antichain**: pairwise incomparable.
- An **upper bound (order theory)** is an element at or above both chosen elements. Their **least upper bound (join)** is below or equal to every upper bound (order theory). The **greatest lower bound (meet)** is defined dually: it lies below both and above or equal to every lower bound (order theory). In the subset order, the join of two sets is their union. Posets where every pair has a join and a meet are **lattices**; state-based CRDTs use a join operation on a semilattice of states; operation-based CRDTs use different delivery and commutativity conditions.

## Key takeaways

- Partial orders allow incomparable pairs; total orders compare every pair.
- Hasse diagrams remove self-pairs and transitive edges, leaving the immediate ordering constraints.

## Further reading

- [Partially ordered set — Wikipedia](https://en.wikipedia.org/wiki/Partially_ordered_set)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
