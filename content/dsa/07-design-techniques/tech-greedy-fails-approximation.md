---
id: tech-greedy-fails-approximation
title: A half-optimum knapsack guarantee
level: advanced
minutes: 3
sourceLesson: tech-greedy-fails
summary: Ratio greedy alone can be arbitrarily poor on whole items.
---

The previous unit showed that whole-item ratio-greedy can miss the optimum. We now quantify how poor it can be, then recover a guarantee by comparing two feasible candidate solutions. We assume positive weights and non-negative values throughout.

> [!tip] Greedy as an approximation
> Ratio-greedy alone can be arbitrarily bad: with a large capacity, a small item with a high ratio can block one big item that fills the whole knapsack. A small fix gives a guarantee of at least half the optimum.

For example:

```formula
w_1 = 1, v_1 = 2;   w_2 = M, v_2 = M
G = 2,   OPT = M,   M > 2
where
w_1: the weight of the small item
v_1: the value of the small item (ratio 2)
w_2: the weight of the big item, equal to the capacity
v_2: the value of the big item (ratio 1)
M: the capacity, any number greater than 2
G: the value ratio-greedy collects (it takes the small item, then the big one no longer fits)
OPT: the best possible value (the big item alone)
In words: greedy gets 2 while the optimum is M, so the gap can be made as large as you like.
```

The fix: for positive weights and non-negative values, first discard items heavier than capacity. Take the ratio-ordered whole-item prefix up to the first item that does not fit, and compare its value with the best single feasible item:

```formula
OPT ≤ G + v_next
max(G, v_max) ≥ (G + v_next) / 2
max(G, v_max) ≥ OPT / 2
where
OPT: the best possible 0/1 value
G: the value of the ratio-ordered prefix of whole items
v_next: the value of the first item that didn't fit
v_max: the value of the best single item that fits on its own (at least v_next)
max: the larger of its inputs
≤: at most
≥: at least
In words: the fractional optimum, which beats any 0/1 answer, is at most the prefix plus the whole next item; the larger of two numbers is at least their average, so the better of the prefix and the best single item gets at least half the optimum.
```

Continuing to fit later items can only improve that prefix value.

## Key takeaways
- Ratio greedy alone can be arbitrarily poor on whole items.
- Compare the feasible ratio-prefix value with the best single item after discarding overweight items.

## Further reading
- [Knapsack approximation proof — Cornell notes](https://www.cs.cornell.edu/courses/cs4820/2019fa/lectures/approx-knapsack.pdf)
