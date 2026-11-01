---
id: tech-greedy-fails-whole-items
title: Why whole-item knapsack resists ratio greedy
level: advanced
minutes: 3
sourceLesson: tech-greedy-fails
summary: Whole items can fit together better after a locally best item is omitted.
---

The previous unit proved ratio-greedy when arbitrary fractions are available. Now each item can be included only once and must be taken whole. The examples retain positive integer weights, non-negative values and non-negative integer capacity.

### 0/1: greedy fails

If each item is taken whole or not at all, ratio-greedy breaks. The classic example (from CLRS), capacity 50:

| Item | Weight | Value | Ratio |
|---|---|---|---|
| A | 10 | 60 | 6 |
| B | 20 | 100 | 5 |
| C | 30 | 120 | 4 |

```
fractional: A + B + 2/3 of C
          = 60 + 100 + 80   = 240
0/1 greedy: A + B (C won't fit)
          = 160, 20 kg wasted
0/1 best:   B + C           = 220
```

Greedy's high-ratio choice, A, wastes capacity that couldn't be filled afterwards. With whole items, *how well the pieces fit together* matters, and the value/weight rule does not capture that interaction.

> [!analogy] Real-world analogy: packing a car boot
> Packing for a holiday, you load the bag that is most useful for its size first, then the next. Soon a gap is left that none of the remaining bags will fit, although a different combination of bags would have filled the boot completely.
>
> **How it maps:** the boot is the capacity, each bag is an item that must go in whole, and "most useful for its size" is ratio greedy. The leftover gap is the 20 kg greedy wastes in the table above; the better combination is the 0/1 optimum.
>
> **Where it stops:** a real boot has shape as well as volume, so even a combination with the right total size might not fit. The knapsack model only tracks one number, total weight, which is why an exact DP over that number is possible at all.

### How hard is 0/1 knapsack?

No algorithm is known that solves every 0/1 knapsack instance in time polynomial in the size of the input. Precisely:

- The **decision version**, "can a value of at least V be reached without exceeding capacity W?", is **NP-complete**. A knapsack problem is one of **Karp's 21 NP-complete problems** (1972); his version asks for a subset of numbers with an exact total, what is now usually called subset sum.
- Finding the best value, the **optimisation problem**, is **NP-hard**: a fast optimiser would answer the decision version just by comparing its best value with V.
- Hardness is shown by a **polynomial-time reduction** from a known NP-complete problem *to* knapsack: a fast knapsack solver would then give a fast solver for that problem too. A reduction in the other direction, from knapsack to some other problem, would prove nothing about knapsack's difficulty.
- The chain starts with the **Cook–Levin theorem**: Stephen Cook (1971) and, independently, Leonid Levin (published 1973, framed in terms of search problems) showed that the Boolean satisfiability problem (SAT) is NP-complete. Karp then built a tree of reductions outward from SAT; his knapsack proof reduces exact cover to knapsack.
- Whether P = NP is still unresolved. So "NP-hard" means "no polynomial-time algorithm unless P = NP", not "proved impossible".

### Why the DP doesn't contradict this

The standard DP updates one table entry per whole-number capacity for each item, so its work is the number of items times the capacity. A hundred items with capacity 50 take about 5,000 updates; the same items with a capacity of five billion take about half a trillion.

That makes it **pseudo-polynomial**: its storage and work depend on the capacity's numeric value, while the input only needs about 33 bits to write that capacity down. The running time is exponential in the length of the capacity's binary representation, so it does not count as polynomial time. Problems like this, hard in general but solvable in time polynomial in the numeric values, are called **weakly NP-hard**. Whether the DP is practical depends on the number of items, the capacity and the available resources.

```python
def knapsack01(items, cap):
    items = list(items)
    if (type(cap) is not int or cap < 0
            or any(type(w) is not int
                   or w <= 0
                   or type(v) is not int
                   or v < 0
                   for w, v in items)):
        raise ValueError("item domain")
    best = [0] * (cap + 1)
    for w, v in items:
        # go downwards so each item is
        # used at most once
        for c in range(cap, w - 1, -1):
            # The downward pass uses the
            # previous item state.
            best[c] = max(best[c],
                          best[c - w] + v)
    return best[cap]
```

## Key takeaways
- Whole items can fit together better after a locally best item is omitted.
- The capacity-indexed DP is pseudo-polynomial because it depends on the numeric capacity.

## Further reading
- [Greedy algorithms — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
- [Dynamic programming — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
