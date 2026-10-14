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

0/1 knapsack is **NP-hard**: at least as hard as every problem in NP, so no algorithm is known that solves every instance in time polynomial in the size of the input (and none exists unless P = NP). The standard DP fills one table entry per capacity value for each item:

```formula
T = O(nW)
T ≈ 100 × 50 = 5,000
T ≈ 100 × 5 × 10^9 = 5 × 10^11
where
T: the number of table updates the DP performs
n: the number of items (100 in the examples)
W: the capacity, as a number (50, then 5 × 10^9 in the examples)
O: Big-O, grows no faster than this up to a constant factor
≈: approximately equal to
10^9: one billion
10^11: one hundred billion
In words: the work grows with the capacity's numeric value, not with the number of digits needed to write it, so a capacity of 5 billion makes the table impractically large.
```

That makes it **pseudo-polynomial**: its storage and work depend on W’s numeric value, so whether it is practical depends on both n and W and the available resources.

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
