---
id: disc-permutations-circular
title: "Permutations and circular arrangements"
level: intermediate
minutes: 4
summary: "Permutations count ordered selections without replacement."
sourceLesson: disc-counting
---

## Permutations: order matters

A **permutation** is an ordering. To put n distinct items in order there are n choices for the first place, n − 1 for the second, and so on down to 1. That product has its own name and symbol, the **factorial**:

```formula
n! = n × (n − 1) × … × 2 × 1
5! = 5 × 4 × 3 × 2 × 1 = 120
where
n: the number of distinct items being put in order, a whole number 0 or more
!: factorial: multiply every whole number from n down to 1. By convention 0! = 1 (there is exactly one way to order nothing)
…: and so on: the pattern continues through every whole number in between
In words: n factorial is the number of different orderings of n distinct things. Five items can be lined up in 120 ways.
```

Often you only fill k places from n items (no item used twice). You stop the product after k factors, which is the same as dividing n! by the (n − k)! orderings of the items you didn't use:

```formula
P(n, k) = n! / (n − k)!
P(n, k) = n × (n − 1) × … × (n − k + 1)
P(8, 3) = 8 × 7 × 6 = 336
where
P(n, k): the number of permutations of k items from n: ordered selections with no item used twice
n: the number of distinct items available
k: how many places are filled, from 0 up to n
!: factorial: the product of every whole number from that number down to 1, with 0! = 1
…: the pattern continues; the second line has exactly k factors
In words: n choices for the first place, one fewer for each later place, k places in total. Choosing a gold, silver and bronze winner from 8 runners gives 336 possible podiums.
```

Factorials grow very fast. 10! is about 3.6 million and 20! is about 2.4 × 10¹⁸. However large a fixed base you pick, the factorial eventually overtakes its powers:

```formula
n! > c^n   for all n ≥ n_0
where
n!: n factorial, the product of every whole number from n down to 1
c: any fixed number greater than 1, for example 2 or 1000
c^n: n copies of c multiplied together (exponential growth)
n_0: a threshold that depends on c; past it the inequality always holds. For c = 2, n_0 = 4 (4! = 24 > 16)
≥: greater than or equal to
In words: factorial growth beats every exponential in the end, because each new factor n keeps getting bigger while c stays fixed.
```

That is why brute-forcing the travelling salesman problem (trying every ordering of cities) quickly becomes impractical as the number of cities grows (the cutoff depends on the implementation and hardware).

It is also where the lower bound for comparison sorting comes from. A sort that only compares items must be able to tell all n! orderings of its input apart, and each yes/no comparison at best halves the possibilities, so it needs about log₂(n!) comparisons in the worst case:

```formula
log_2(n!) ≈ n × log_2(n)
log_2(20!) ≈ 61.1
20 × log_2(20) ≈ 86.4
where
n: the number of distinct items being sorted, at least 1 for this logarithmic comparison
n!: n factorial, the number of possible orderings of n distinct items
log_2: logarithm base 2: log_2(x) is the power you raise 2 to in order to get x, i.e. how many halvings take x down to 1
≈: in the first line, the ratio of the two sides tends to 1 as n grows; the numeric lines give rounded values
In words: the number of comparisons needed grows like n log n. The approximation is rough for small n (at n = 20 the two sides are 61 and 86, a ratio of about 0.71), but the ratio creeps towards 1 as n grows.
```

## Circular arrangements

When rotations count as the same seating, divide out the rotational overcounting.

```formula
R(n) = n! / n = (n − 1)!
R(6) = 5! = 120
where
R(n): the number of ways to seat n distinct people round a table when rotations of a seating count as the same
n: the number of distinct people (and seats), at least 1
!: factorial: the product of every whole number from that number down to 1
In words: the n! straight-line orderings fall into groups of n rotations, so divide by n. For n ≥ 3, if mirror images also count as the same, halve it again (60 for 6 people).
```

## Key takeaways

- Permutations count ordered selections without replacement.
- Circular seatings of distinct people identify rotations; identifying reflections requires a further adjustment.

## Further reading

- [Permutation — Wikipedia](https://en.wikipedia.org/wiki/Permutation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
