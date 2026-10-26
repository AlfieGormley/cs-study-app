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

```formula essential
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
- "Happened-before" on events in a distributed system (Lamport's relation, as a strict order).

Divisibility is a useful example of an order that is not total.

For positive integers, “a divides b” means b is a whole-number multiple of a. Three divides twelve. Neither two nor three divides the other, so not every pair is comparable.

Two elements are incomparable when neither precedes the other. The singleton sets containing 1 and 2 are incomparable under subset inclusion.

If every pair is comparable, it is a **total order** (or linear order), like ≤ on integers or alphabetical order on strings.

A **strict partial order** is irreflexive (nothing relates to itself) and transitive.

Removing all self-pairs turns a partial order into its strict version: strictly before, rather than before-or-equal.

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

Useful vocabulary for reading order relationships:

- **Minimal element**: nothing is strictly below it. **Maximal element** means nothing is strictly above it. **Least element** (minimum): below everything; **greatest element** means above everything. A poset can have several minimal elements but at most one least element.
- A **chain in a poset** is a set of pairwise comparable elements. **Antichain**: pairwise incomparable.
- An **upper bound (order theory)** is an element at or above both chosen elements. Their **least upper bound (join)** is below or equal to every upper bound (order theory). The **greatest lower bound (meet)** is defined dually: it lies below both and above or equal to every lower bound (order theory). In the subset order, the join of two sets is their union. Posets where every pair has a join and a meet are **lattices**; state-based CRDTs use a join operation on a join-semilattice of states; operation-based CRDTs use different delivery and commutativity conditions.

> [!analogy] Real-world analogy: Getting dressed
> Socks must precede shoes, but putting on a hat need not be ordered relative to either.
>
> **How it maps:** Dependencies produce a partial order: some pairs are constrained and others incomparable. A full dressing sequence is one linear extension.
>
> **Where it stops:** This ignores duration, shared resources and personal preferences; ordering constraints alone do not solve scheduling with those extra limits.

## Key takeaways

- Partial orders allow incomparable pairs; total orders compare every pair.
- Hasse diagrams remove self-pairs and transitive edges, leaving the immediate ordering constraints.

## Further reading

- [Partially ordered set — Wikipedia](https://en.wikipedia.org/wiki/Partially_ordered_set)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
