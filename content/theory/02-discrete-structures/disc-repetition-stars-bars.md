---
id: disc-repetition-stars-bars
title: "Repetition, stars and bars, and repeated letters"
level: intermediate
minutes: 2
summary: "Stars and bars distributes identical items among distinct bins."
sourceLesson: disc-counting
---

## Repetition allowed

The table distinguishes the four selection models.

| Order? | Repeats? | Count |
|---|---|---|
| Yes | No | Partial permutation |
| Yes | Yes | Independent choices |
| No | No | Combination |
| No | Yes | Multiset |

The categories differ in what counts as the same outcome. Swapping two choices matters for an ordered selection; selecting the same kind twice is allowed only in the repeat cases.

A no-repeat selection cannot choose more items than exist. A **multiset** allows repeated kinds but ignores order. **Stars and bars** represents identical items by stars and separates the distinct bins with bars, using one fewer bar than bins. Bins may be empty:

```
10 identical jobs, 4 workers:
**|****||****   -> 2, 4, 0, 4
```

Every such line is fixed by choosing which positions hold bars:

```formula reference
M(n, k) = C(n + k − 1, n − 1)
where
M(n, k): the number of ways to put k identical items into n distinct bins (bins may stay empty), which is also the number of multisets of size k from n kinds
n: the number of bins (kinds), at least 1
k: the number of identical items, 0 or more
C(a, b): "a choose b", the number of ways to choose b positions out of a
In words: For identical items in distinct bins with empty bins allowed, a row of stars separated by one fewer bars than bins represents exactly one distribution.
```

If every worker must get at least one job, satisfy that constraint before placing the bars.

Preassigning one job to each worker leaves six identical jobs to distribute. Empty bins are allowed for these remaining jobs; the initial allocation already satisfies the minimum. If there are fewer jobs than workers, the original constraint is impossible.

### Arrangements with repeated letters

The number of distinct arrangements of a word with repeated letters is the **multinomial coefficient**: arrange all the letters as if they were distinct, then divide by the orderings of each group of identical letters, which don't change the word.

Swapping two As or two Ns in BANANA does not change the visible string. Count labelled arrangements, then divide out exactly those invisible swaps. A different word requires its own repeated-letter groups.

## Key takeaways

- Stars and bars distributes identical items among distinct bins.
- Repeated-letter arrangements divide out the orderings of indistinguishable letters.

## Further reading

- [Stars and bars — Wikipedia](https://en.wikipedia.org/wiki/Stars_and_bars_(combinatorics))
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
