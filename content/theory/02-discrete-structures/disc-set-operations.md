---
id: disc-set-operations
title: "Set operations and De Morgan’s laws"
level: basic
minutes: 4
summary: "Union keeps either set; intersection keeps shared elements; symmetric difference keeps exactly one."
sourceLesson: disc-sets-functions
---

## Set operations

These operations build new sets from old ones. The **universe** U is the set of everything under discussion (all users, all integers), which a complement needs so it knows what "not in A" ranges over.

```formula
A ∪ B = { x : x ∈ A or x ∈ B }
A ∩ B = { x : x ∈ A and x ∈ B }
A \ B = { x : x ∈ A and x ∉ B }
A ⊕ B = (A ∪ B) \ (A ∩ B)
Aᶜ = U \ A
where
A, B: any two sets
x: a stand-in for an element
U: the universe: the set of everything under discussion
∪: union: in A or B (or both)
∩: intersection: in both A and B
\: set difference: in A but not in B (some books write A − B)
⊕: symmetric difference: in exactly one of the two sets (some books write A △ B)
ᶜ: complement: everything in the universe U that is not in A
∈: is an element of
∉: is not an element of
{ x : … }: the set of all x that make the condition after the colon true
In words: union keeps anything in either set, intersection keeps what they share, difference keeps A's elements that B lacks, symmetric difference keeps what is in exactly one, and the complement is everything in the universe that is not in A.
```

The picture shows how the three regions of two overlapping sets line up with these operations:

```
+---------+---------+---------+
| A only  |  both   | B only  |
| A \ B   | A ∩ B   | B \ A   |
+---------+---------+---------+
```

A worked example, with a universe of the numbers 1 to 6:

```formula
A = {1, 2, 3, 4}   B = {3, 4, 5}
A ∪ B = {1, 2, 3, 4, 5}
A ∩ B = {3, 4}
A \ B = {1, 2}
A ⊕ B = {1, 2, 5}
Aᶜ = {5, 6}   for U = {1, 2, 3, 4, 5, 6}
where
A, B: the two example sets
U: the universe, here the numbers 1 to 6
∪: union: in A or B (or both)
∩: intersection: in both
\: difference: in A but not in B
⊕: symmetric difference: in exactly one of A and B
ᶜ: complement: in the universe but not in A
In words: the union has every number from either set, the intersection only the shared 3 and 4, the difference A's numbers that B lacks, the symmetric difference everything except the shared 3 and 4, and the complement the numbers in U that A misses.
```

Python's built-in set supports union, intersection, difference and symmetric difference; complement needs an explicit universe, `U - a`. They are the bread and butter of practical code (deduplicating, finding common users, permission checks):

```python
a = {1, 2, 3, 4}
b = {3, 4, 5}
# Set results below ignore display order.
a | b   # {1, 2, 3, 4, 5}
a & b   # {3, 4}
a - b   # {1, 2}
a ^ b   # {1, 2, 5}
a <= b  # False: is a a subset of b?
```

Two laws worth memorising are **De Morgan's laws**, which mirror the logic versions. They say how a complement passes through a union or an intersection:

```formula
(A ∪ B)ᶜ = Aᶜ ∩ Bᶜ
(A ∩ B)ᶜ = Aᶜ ∪ Bᶜ
where
A, B: any two sets inside a universe U
ᶜ: complement: everything in the universe U that is not in the set
∪: union: in either set
∩: intersection: in both sets
In words: "not in (A or B)" is the same as "not in A and not in B", and "not in (A and B)" is the same as "not in A or not in B". The complement flips union into intersection and back.
```

Check the first law with the example sets from above:

```formula
A = {1, 2, 3, 4}   B = {3, 4, 5}
(A ∪ B)ᶜ = {1, 2, 3, 4, 5}ᶜ = {6}
Aᶜ ∩ Bᶜ = {5, 6} ∩ {1, 2, 6} = {6}
where
A, B: the two example sets, inside the universe U = {1, 2, 3, 4, 5, 6}
U: the universe: everything under discussion, here the numbers 1 to 6
ᶜ: complement: the elements of U that are not in the set
∪: union: in either set
∩: intersection: in both sets
In words: only 6 is outside both sets, and computing it either way gives {6}, so the two sides of the law agree.
```

This is the same rewrite you do when you push a `NOT` through an SQL WHERE clause.

## Key takeaways

- Union keeps either set; intersection keeps shared elements; symmetric difference keeps exactly one.
- Complements depend on a fixed universe, and De Morgan’s laws exchange union and intersection.

## Further reading

- [Set (mathematics) — Wikipedia](https://en.wikipedia.org/wiki/Set_(mathematics))
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
