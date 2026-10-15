---
id: disc-inclusion-exclusion-counts
title: "Inclusion–exclusion and divisibility counts"
level: intermediate
minutes: 5
summary: "Alternating intersection counts count each element of a union exactly once."
sourceLesson: disc-inclusion-recurrences
---

The basic counting rules break down in two common situations. When cases **overlap**, the sum rule double-counts. When a problem is easiest to describe **in terms of smaller versions of itself**, a direct formula is hard to see. Inclusion–exclusion fixes the first; recurrences fix the second. Generating functions are a power tool that packages a whole sequence into one object, so that counting problems become algebra.

These are also the tools you need to analyse algorithms: recurrences describe the running time of recursive code, and the same "count the ways" reasoning is what dynamic programming computes.

## Inclusion–exclusion

When two groups overlap, adding their sizes counts everyone in the overlap twice, so subtract the overlap once:

```formula
|A ∪ B| = |A| + |B| − |A ∩ B|
|P ∪ J| = 18 + 15 − 8 = 25
where
A, B: two finite sets (collections of distinct items), here P and J
P, J: the engineers who know Python and the engineers who know Java
| |: the size of a set: how many elements it has
∪: union: the elements in at least one of the two sets
∩: intersection: the elements in both sets
In words: everyone in at least one group = the first group + the second group − those counted in both. With 18 Python, 15 Java and 8 who know both, 25 engineers know at least one.
```

> [!example] Two sets
> In a team of 30 engineers, 18 know Python, 15 know Java and 8 know both. Those who know at least one: 18 + 15 − 8 = 25. So 30 − 25 = 5 know neither.

For three sets, subtracting the pairwise overlaps removes the triple overlap one time too many, so add it back:

```formula
|A ∪ B ∪ C| = |A| + |B| + |C|
            − |A ∩ B| − |A ∩ C| − |B ∩ C|
            + |A ∩ B ∩ C|
where
A, B, C: three finite sets
| |: the size of a set (its number of elements)
∪: union: elements in at least one of the sets
∩: intersection: elements in all of the sets it joins
In words: add the three groups, subtract each pairwise overlap, then add back the part common to all three.
```

The general pattern alternates: add singles, subtract pairs, add triples, subtract quadruples, and so on. To see why it works, follow one element that lies in exactly m of the sets. It is counted once for every single set it is in, minus once for every pair, plus once for every triple, and so on:

```formula
C(m, 1) − C(m, 2) + C(m, 3)
  − … ± C(m, m) = 1
3 − 3 + 1 = 1   for m = 3
where
m: the number of the sets that contain this particular element, at least 1
C(m, j): "m choose j", the number of ways to pick j of those m sets: the number of j-fold intersections the element lies in
…: and so on, through every size from 1 to m
±: plus or minus: the signs keep alternating, so the last sign is + when m is odd and − when m is even
In words: however many sets an element is in, the alternating sum counts it once and only once. (It follows from the binomial theorem with x = −1 and y = 1.)
```

### Worked example: divisibility

How many integers from 1 to 1000 are divisible by 2, 3 or 5? The multiples of d up to 1000 number ⌊1000 / d⌋. The multiples of both 2 and 3 are the multiples of 6, and so on, because 2, 3 and 5 share no factors.

```formula
|A_d| = ⌊1000 / d⌋
|A_2| = 500  |A_3| = 333  |A_5| = 200
|A_6| = 166  |A_10| = 100  |A_15| = 66
|A_30| = 33
500 + 333 + 200 = 1033
1033 − 166 − 100 − 66 = 701
701 + 33 = 734
where
A_d: the set of integers from 1 to 1000 divisible by d
A_2, A_3, A_5: the singles: the multiples of 2, of 3 and of 5
A_6, A_10, A_15: the pairs: multiples of both 2 and 3 (that is, of 6), of both 2 and 5 (of 10), and of both 3 and 5 (of 15)
A_30: the triple: multiples of 2, 3 and 5 at once, which are the multiples of 30
d: the divisor, here 2, 3, 5, 6, 10, 15 or 30
| |: the size of a set (how many integers it contains)
⌊ ⌋: floor: round down to a whole number, so ⌊1000 / 3⌋ = ⌊333.3⌋ = 333
In words: add the three singles, subtract the three pairs, add back the triple: 734 integers are divisible by at least one of 2, 3 and 5.
```

So 734 are divisible by at least one, and 1000 − 734 = 266 by none. Each term is one integer division (one counted step in a fixed-width arithmetic model), so inclusion–exclusion counts without iterating. The same idea computes Euler's totient function (written with the Greek letter phi), which you'll meet in the number theory lesson.

## Key takeaways

- Alternating intersection counts count each element of a union exactly once.
- Multiples shared by coprime divisors are multiples of their product.

## Further reading

- [Inclusion–exclusion principle — Wikipedia](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
