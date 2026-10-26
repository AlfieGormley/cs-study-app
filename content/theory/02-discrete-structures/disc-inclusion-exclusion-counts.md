---
id: disc-inclusion-exclusion-counts
title: "Inclusion–exclusion and divisibility counts"
level: intermediate
minutes: 3
summary: "Alternating intersection counts count each element of a union exactly once."
sourceLesson: disc-inclusion-recurrences
---

When cases overlap, adding their counts double-counts shared members. **Inclusion–exclusion** corrects that overcount by tracking how many times each member appears.

## Inclusion–exclusion

When two groups overlap, adding their sizes counts everyone in the overlap twice, so subtract the overlap once:

```formula essential
|A ∪ B| = |A| + |B| − |A ∩ B|
where
A, B: two finite sets (collections of distinct items)
| |: the size of a set: how many elements it has
∪: union: the elements in at least one of the two sets
∩: intersection: the elements in both sets
In words: Adding two overlapping groups counts shared members twice. Subtract the overlap once to count everyone in at least one group exactly once.
```

> [!example] Two sets
> In a team of 30 engineers, 18 know Python, 15 know Java and 8 know both. Those who know at least one: 18 + 15 − 8 = 25. So 30 − 25 = 5 know neither.

With three sets, pairwise corrections themselves overlap.

An item in all three sets is added three times and removed once for each of the three pairwise overlaps. At that point it has vanished from the count, so add the triple overlap back once.

The general pattern alternates: add singles, subtract pairs, add triples, subtract quadruples, and so on.

Track one element through the overlap corrections: the goal is a final contribution of one whenever it belongs to the union. This element-by-element reasoning explains the alternating signs.

### Divisibility as overlapping sets

To count integers divisible by any of several divisors, treat each divisor’s multiples as one set.

Multiples shared by 2 and 3 are multiples of 6; multiples shared by 2, 3 and 5 are multiples of 30. In general use the least common multiple for an intersection. The product works here because the divisors are pairwise coprime.

To count integers divisible by none of the divisors, subtract the union from the size of the whole range. This is the same complement reasoning used for codes with at least one digit.

## Key takeaways

- Alternating intersection counts count each element of a union exactly once.
- Multiples shared by coprime divisors are multiples of their product.

## Further reading

- [Inclusion–exclusion principle — Wikipedia](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
