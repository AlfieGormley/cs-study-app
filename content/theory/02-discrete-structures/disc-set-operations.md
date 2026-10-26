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

```formula essential
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

For sets containing 1, 2, 3, 4 and 3, 4, 5, the shared elements are 3 and 4. The symmetric difference keeps 1, 2 and 5. With the universe fixed to 1 through 6, the first set’s complement contains 5 and 6.

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

**De Morgan’s laws** explain how “not” changes a condition: outside a union means outside both sets, while outside an intersection means outside at least one.

```formula essential
(A ∪ B)ᶜ = Aᶜ ∩ Bᶜ
(A ∩ B)ᶜ = Aᶜ ∪ Bᶜ
where
A, B: any two sets inside a universe U
ᶜ: complement: everything in the universe U that is not in the set
∪: union: in either set
∩: intersection: in both sets
In words: "not in (A or B)" is the same as "not in A and not in B", and "not in (A and B)" is the same as "not in A or not in B". The complement flips union into intersection and back.
```

Only 6 is outside both example sets. This tests the meaning of “neither”, without needing separate calculations for both sides.

This is the same rewrite you do when you push a `NOT` through an SQL WHERE clause.

## Key takeaways

- Union keeps either set; intersection keeps shared elements; symmetric difference keeps exactly one.
- Complements depend on a fixed universe, and De Morgan’s laws exchange union and intersection.

## Further reading

- [Set (mathematics) — Wikipedia](https://en.wikipedia.org/wiki/Set_(mathematics))
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
