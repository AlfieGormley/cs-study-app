---
id: tech-greedy-fails-approximation
title: A half-optimum knapsack guarantee
level: advanced
minutes: 3
sourceLesson: tech-greedy-fails
summary: Ratio greedy alone can be arbitrarily poor on whole items.
---

The previous unit showed that 0/1 knapsack is NP-hard, so no fast exact algorithm is known. An **approximation algorithm** settles for a provable promise instead: it runs in polynomial time and always returns a feasible answer within a known factor of the optimum, its **approximation ratio**. This unit builds one for knapsack from ratio-greedy, then places it among other classic guarantees. We assume positive weights and non-negative values throughout.

## Ratio-greedy alone has no guarantee

Ratio-greedy can be arbitrarily bad on whole items. Take a large capacity, a small item of weight 1 and value 2, and one big item whose weight and value both equal the capacity. The small item has the better ratio (2 against 1), so greedy packs it first, and then the big item no longer fits. Greedy collects 2, while the optimum, the big item alone, is worth the whole capacity. Make the capacity as large as you like and greedy's share of the optimum shrinks towards zero.

The damage comes from a single item: greedy's first refusal can be worth far more than everything it accepted.

## The fix: also try the best single item

First discard items heavier than the capacity; they can never be packed. Then build two feasible candidates and return the better one:

1. the ratio-ordered **prefix**: take items in ratio order until the first one that doesn't fit;
2. the **best single item** that fits on its own.

The better of the two is always worth at least half the optimum, so this is a **2-approximation**. The reasoning:

- The fractional answer is at least as good as any whole-item answer, because packing whole items is one of the options fractions allow.
- The fractional answer is the prefix plus *part* of the first item that didn't fit, so it is at most the prefix plus that whole item.
- So the optimum is at most "prefix + next item". The next item fits on its own, so it is worth no more than the best single item. Each of the two parts is therefore at most the better candidate, and the optimum is at most twice that candidate.

```formula reference
OPT ≤ G + v_next ≤ 2 max(G, v_max)
where
OPT: the best possible whole-item value
G: the value of the ratio-ordered prefix
v_next: the value of the first item in ratio order that didn't fit
v_max: the value of the best single item that fits on its own, which is at least v_next
max: the larger of its inputs
≤: at most
In words: the optimum is at most the prefix plus the next item, and each of those is at most the better of the two candidates, so the better candidate is worth at least half the optimum.
```

On the bad example above, the best single item is the big one, so the fixed algorithm returns the optimum. Continuing to pack later items that still fit can only improve the prefix and keeps the guarantee. Knapsack even allows much tighter guarantees: a **fully polynomial-time approximation scheme (FPTAS)** guarantees any chosen tolerance, such as at least 99 percent of the optimum, with running time polynomial in both the number of items and one over the tolerance. The dynamic programming module shows how.

## Other classic guarantees

Approximation ratios are worst-case promises, and they differ widely between problems:

- **Scheduling on identical machines.** Ron Graham (1966) showed that **list scheduling**, which hands each job in turn to the machine that becomes free first, finishes all jobs within twice the best possible completion time for the last job (the **makespan**). The exact factor is two minus one over the number of machines.
- **Metric TSP.** When distances obey the triangle inequality, the **Christofides algorithm** (Nicos Christofides, 1976) guarantees a tour at most 1.5 times the shortest; Anatoliy Serdyukov found the same algorithm independently. In 2020 Anna Karlin, Nathan Klein and Shayan Oveis Gharan gave the first randomised algorithm with a ratio below 1.5 for general metric TSP, better by a tiny constant (more than 10⁻³⁶): a theoretical breakthrough rather than a practical improvement.
- **Nearest-neighbour TSP.** Always visiting the closest unvisited city has no constant-factor guarantee. Even when distances obey the triangle inequality, its tour can be longer than the shortest by a factor that grows with the logarithm of the number of cities (Rosenkrantz, Stearns and Lewis, 1977). With arbitrary distance tables it is worse still: for every number of cities there are tables on which it produces the worst possible tour.

An approximation ratio says nothing about typical inputs: a heuristic with no guarantee can do well on everyday data, and a guaranteed algorithm can be slower in practice.

## Key takeaways
- Ratio greedy alone can be arbitrarily poor on whole items.
- Compare the feasible ratio-prefix value with the best single item after discarding overweight items.

## Further reading
- [Knapsack approximation proof — Cornell notes](https://www.cs.cornell.edu/courses/cs4820/2019fa/lectures/approx-knapsack.pdf)
- [Karlin, Klein and Oveis Gharan: improved metric TSP approximation](https://arxiv.org/abs/2007.01409)
- [List scheduling](https://en.wikipedia.org/wiki/List_scheduling)
