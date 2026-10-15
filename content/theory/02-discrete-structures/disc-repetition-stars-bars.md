---
id: disc-repetition-stars-bars
title: "Repetition, stars and bars, and repeated letters"
level: intermediate
minutes: 3
summary: "Stars and bars distributes identical items among distinct bins."
sourceLesson: disc-counting
---

## Repetition allowed

The table distinguishes order and replacement. The following card defines the counts.

| Order? | Repeats? | Count |
|---|---|---|
| Yes | No | Partial permutation |
| Yes | Yes | Independent choices |
| No | No | Combination |
| No | Yes | Multiset |

```formula
N_ord = P(n, k)
N_rep = n^k
N_sub = C(n, k)
N_multi = C(n + k − 1, k)
where
N_ord: ordered selections without repeats
N_rep: ordered selections with repeats
N_sub: unordered selections without repeats
N_multi: unordered selections with repeats
n: the number of available kinds, at least 1
k: the number selected, a non-negative integer
P(n, k): the number of ordered selections of k distinct items from n
C(n, k): the number of k-element subsets of an n-element set
In words: Ordering and repetition determine which formula applies. The no-repeat counts are zero when more items are requested than exist.
```

The factorial forms for the no-repeat counts assume you pick no more items than exist; otherwise the count is zero. The last row, **multisets** (collections where an item may appear more than once), is counted with **stars and bars**. Distributing k identical items into n distinct bins is the same as arranging k stars and n − 1 bars in a line, where the bars separate the bins:

```
10 identical jobs, 4 workers:
**|****||****   -> 2, 4, 0, 4
```

Every such line is fixed by choosing which positions hold bars:

```formula
M(n, k) = C(n + k − 1, n − 1)
        = C(n + k − 1, k)
M(4, 10) = C(13, 3) = 286
where
M(n, k): the number of ways to put k identical items into n distinct bins (bins may stay empty), which is also the number of multisets of size k from n kinds
n: the number of bins (kinds), at least 1
k: the number of identical items, 0 or more
C(a, b): "a choose b", the number of ways to choose b positions out of a
In words: lay out k stars and n − 1 bars, 13 symbols for 10 jobs and 4 workers, and choose which 3 positions are bars: 286 ways. The two forms are equal by symmetry.
```

If every worker must get at least one job, hand one to each first, then distribute the remaining 6 freely: 6 stars and 3 bars.

```formula
M_+ = C(9, 3) = 84
where
M_+: the number of distributions with at least one job per worker
C(9, 3): the number of choices of three bar positions among nine symbols
In words: Giving each of four workers one of the ten jobs leaves six jobs to distribute freely, giving 84 distributions.
```

### Arrangements with repeated letters

The number of distinct arrangements of a word with repeated letters is the **multinomial coefficient**: arrange all the letters as if they were distinct, then divide by the orderings of each group of identical letters, which don't change the word.

```formula
N_arr = n! / (n_1! × n_2! × … × n_m!)
N_arr = 6! / (3! × 2! × 1!)
N_arr = 720 / 12 = 60
where
N_arr: the number of distinct arrangements of the letters
n: the total number of letters (here 6, for BANANA)
n_1, n_2, …, n_m: how many times each of the m different letters appears (here A 3 times, N twice, B once); they add up to n
m: the number of different letters (here 3)
!: factorial: the product of every whole number from that number down to 1
…: and so on, one factor per different letter
In words: BANANA's 720 labelled orderings collapse in groups of 3! × 2! = 12, leaving 60 different words.
```

## Key takeaways

- Stars and bars distributes identical items among distinct bins.
- Repeated-letter arrangements divide out the orderings of indistinguishable letters.

## Further reading

- [Stars and bars — Wikipedia](https://en.wikipedia.org/wiki/Stars_and_bars_(combinatorics))
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
