---
id: disc-combinations-identities
title: "Combinations and binomial identities"
level: intermediate
minutes: 4
summary: "Divide ordered selections by the permutations of each chosen group."
sourceLesson: disc-counting
---

## Combinations: order doesn't matter

A **combination** is a subset: a choice of items where order is irrelevant. The number of k-element subsets of an n-element set is the **binomial coefficient**. Count the ordered selections, then divide out the overcounting: each unordered group of k items appears k! times among the ordered ones.

```formula
C(n, k) = n! / (k! × (n − k)!)
C(n, k) = P(n, k) / k!
C(8, 3) = 336 / 6 = 56
where
C(n, k): the binomial coefficient, read "n choose k": the number of ways to choose k items from n distinct items when order doesn't matter. Books also write it as n over k in tall brackets
P(n, k): the number of ordered selections of k items from n (no repeats), n! / (n − k)!
n: the number of distinct items available
k: how many are chosen, from 0 up to n
!: factorial: the product of every whole number from that number down to 1, with 0! = 1
In words: choosing a team of 3 from 8 people: there are 336 ordered ways to pick 3, and each team turns up 3! = 6 times among them, so there are 56 teams.
```

This "count ordered, then divide out the overcounting" move is one of the most useful in counting.

Three facts about binomial coefficients, each with a one-line counting argument:

- **Binomial symmetry.** Choosing who's in is the same as choosing who's out.
- **Pascal's rule.** Pick one particular item: either it is in the subset or it isn't, and those two cases are disjoint.
- **Binomial row sum.** Adding the counts for every possible subset size gives the total number of subsets, and each item is independently in or out.

```formula
C(n, k) = C(n, n − k)
C(n, k) = C(n − 1, k − 1) + C(n − 1, k)
C(n, 0) + C(n, 1) + … + C(n, n) = 2^n
C(5, 2) = C(5, 3) = 10
C(5, 2) = C(4, 1) + C(4, 2) = 4 + 6
1 + 5 + 10 + 10 + 5 + 1 = 32 = 2^5
where
C(n, k): the number of ways to choose k items from n when order doesn't matter ("n choose k")
n: the number of distinct items, at least 1 for Pascal's rule
k: the size of the subset, from 0 to n (for Pascal's rule, 1 to n − 1 so both terms make sense)
…: and so on, through every subset size from 0 to n
2^n: n copies of 2 multiplied together: each of the n items is either in or out
In words: line 1 is symmetry, line 2 is Pascal's rule, line 3 is the row sum. The last three lines check each fact with n = 5.
```

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

```formula
3 × C(10, 3) = 3 × 120 = 360
10 × C(9, 2) = 10 × 36 = 360
where
C(10, 3): "10 choose 3": the number of 3-person committees from 10 people, 120
C(9, 2): "9 choose 2": the number of ways to pick the 2 ordinary members from the 9 people left once the chair is chosen, 36
In words: choose the committee then which of its 3 is chair, or choose the chair first then 2 more: both give 360.
```

## Check by brute force

When in doubt, write the dumbest possible enumeration for a small case. Python's `itertools` and `math` make this one line each:

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
