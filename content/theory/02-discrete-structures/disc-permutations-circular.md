---
id: disc-permutations-circular
title: "Permutations and circular arrangements"
level: intermediate
minutes: 2
summary: "Permutations count ordered selections without replacement."
sourceLesson: disc-counting
---

## Permutations: order matters

A **permutation** is an ordering. Choose the first item, then one of the remaining items, and keep going. Multiplying those shrinking choices gives the **factorial** count:

```formula essential
n! = n × (n − 1) × … × 2 × 1   for n ≥ 1
0! = 1
where
n: the number of distinct items being put in order, a whole number 0 or more
!: factorial: multiply every whole number from n down to 1. By convention 0! = 1 (there is exactly one way to order nothing)
…: and so on: the pattern continues through every whole number in between
≥: is greater than or equal to
In words: A factorial counts orderings of distinct items: choose the first item, then a remaining item, and keep going. There is one ordering of no items.
```

For an ordered selection filling only some positions, stop choosing when those positions are filled. No item may be reused; asking for more distinct items than exist is impossible.

```formula reference
P(n, k) = n! / (n − k)!
where
P(n, k): the number of permutations of k items from n: ordered selections with no item used twice
n: the number of distinct items available
k: how many places are filled, from 0 up to n
!: factorial: the product of every whole number from that number down to 1, with 0! = 1
In words: An ordered selection without repeats chooses a new item for each successive position. Stop after filling the requested number of positions.
```

Each extra item creates more possible insertion positions. This makes factorial growth eventually exceed every fixed-base exponential, explaining why enumerating all orders quickly becomes impractical.

That is why brute-forcing the travelling salesman problem (trying every ordering of cities) quickly becomes impractical as the number of cities grows (the cutoff depends on the implementation and hardware).

A comparison sort must distinguish every possible ordering of distinct items. Each yes/no comparison supplies at most one binary decision, which gives the familiar worst-case lower bound of linear-times-logarithmic comparisons.

## Circular arrangements

When rotations count as the same seating, divide out the rotational overcounting.

Fix one person’s position and arrange the others relative to them. This removes rotational duplicates. A reflection reverses clockwise order and remains distinct unless the problem explicitly identifies mirror images; with at least three distinct people, identifying reflections halves the count again.

## Key takeaways

- Permutations count ordered selections without replacement.
- Circular seatings of distinct people identify rotations; identifying reflections requires a further adjustment.

## Further reading

- [Permutation — Wikipedia](https://en.wikipedia.org/wiki/Permutation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
