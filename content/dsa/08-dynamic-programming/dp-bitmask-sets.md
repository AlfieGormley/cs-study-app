---
id: dp-bitmask-sets
title: Represent a small set with bits
level: advanced
minutes: 3
summary: Each bit records whether one item is present.
sourceLesson: dp-advanced
---

Every DP so far has had states indexed by positions, lengths or weight limits. The following units cover three less obvious state spaces, then tie everything together with one idea: **a finite, acyclic DP can be evaluated over a DAG of states**. The module ends with a practical checklist for spotting DP in an interview.

## Bitmask DP

When the state needs to know **which items from a small set have been used**, encode that set as the bits of an integer (a **bitmask**): bit j is 1 if item j is in the set. Each item is either in or out, so every extra item doubles the number of possible sets: n items give 2ⁿ subsets, about a million for 20 items.

That doubling is why bitmask DP is only for small sets. Practical limits depend on how many other dimensions the state has, how many transitions each state tries, and the available memory and time. The table shows growth for a state that also records one of n endpoints with up to n transitions each (as in the travelling-salesman DP next), not a hardware guarantee.

| Items | Subsets | Endpoint slots | Work proxy |
|---|---|---|---|
| 10 | 1,024 | ~10⁴ | ~10⁵ |
| 16 | 65,536 | ~10⁶ | ~1.7 × 10⁷ |
| 20 | ~10⁶ | ~2 × 10⁷ | ~4 × 10⁸ |
| 25 | ~3.4 × 10⁷ | ~8 × 10⁸ | ~2 × 10¹⁰ |

Each extra item multiplies the subsets by 2, and the endpoint and transition choices each add another factor of the item count, which is why the work column grows so fast.

The bit operations you need (for example, with `mask` = 11, binary `01011`, meaning items 0, 1 and 3, and `j` = 2, testing gives 0 because item 2 is absent, and adding it gives 15):

```python
mask & (1 << j)     # is j in the set?
mask | (1 << j)     # add j
mask & ~(1 << j)    # remove j
(1 << n) - 1        # the full set
bin(mask).count('1')  # set size
```

## Key takeaways
- Each bit records whether one item is present.
- The number of subsets doubles with every extra item.
- State and transition dimensions determine feasibility.

## Further reading
- [Held–Karp algorithm](https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
