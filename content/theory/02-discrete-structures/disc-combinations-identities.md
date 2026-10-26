---
id: disc-combinations-identities
title: "Combinations and binomial identities"
level: intermediate
minutes: 3
summary: "Divide ordered selections by the permutations of each chosen group."
sourceLesson: disc-counting
---

## Combinations: order doesn't matter

A **combination** is a subset: a choice where order is irrelevant. Its count is a **binomial coefficient**. Count ordered selections, then divide by the number of orders of each group. This works because every selected group has the same number of distinct members.

```formula reference
C(n, k) = n! / (k! × (n − k)!)
where
C(n, k): the binomial coefficient, read "n choose k": the number of ways to choose k items from n distinct items when order doesn't matter. Books also write it as n over k in tall brackets
n: the number of distinct items available
k: how many are chosen, from 0 up to n
!: factorial: the product of every whole number from that number down to 1, with 0! = 1
In words: Count ordered selections and divide by the number of orders of each chosen group. This is valid because every group has the same number of distinct members.
```

This "count ordered, then divide out the overcounting" move is one of the most useful in counting.

Three facts about binomial coefficients, each with a one-line counting argument:

- **Binomial symmetry.** Choosing who's in is the same as choosing who's out.
- **Pascal's rule.** Pick one particular item: either it is in the subset or it isn't, and those two cases are disjoint.
- **Binomial row sum.** Adding the counts for every possible subset size gives the total number of subsets, and each item is independently in or out.

These three arguments describe the same subsets from different viewpoints.

Pascal's rule is exactly how each number in Pascal's triangle is the sum of the two above it:

```
Pascal's triangle
          1
         1 1
        1 2 1
       1 3 3 1
      1 4 6 4 1
    1 5 10 10 5 1
```

## Choosing a chair

Choosing a committee is a combination, because its members have the same role. Choosing a president, secretary and treasurer is a permutation, because swapping their roles changes the outcome.

A committee of three with a chair can be counted in two ways: choose the group then its chair, or the chair then the remaining members.

Every committee-with-chair is counted once by either method. Picking the chair changes the outcome; merely reordering the ordinary members does not.

## Check by brute force

A small enumeration can expose overcounting. Python offers the corresponding operations:

```python
from itertools import (permutations,
    combinations, product)
from math import comb, perm

# Ordered pairs distinguish ab and ba.
len(list(permutations('abcd', 2)))  # 12
perm(4, 2)                          # 12
# Unordered pairs count ab once.
len(list(combinations('abcd', 2)))  # 6
comb(4, 2)                          # 6
# Deduplicate swaps of identical letters.
len(set(permutations('BANANA')))    # 60
```

Brute force on small instances can catch off-by-one and overcounting mistakes. It supplies evidence for those instances; the counting argument or an induction establishes the general formula.

## Key takeaways

- Divide ordered selections by the permutations of each chosen group.
- Symmetry, Pascal’s rule and the row sum each follow from a counting argument.

## Further reading

- [Combination — Wikipedia](https://en.wikipedia.org/wiki/Combination)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [itertools — Python docs](https://docs.python.org/3/library/itertools.html)
