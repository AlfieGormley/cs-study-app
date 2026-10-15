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

When the state needs to know **which items from a small set have been used**, encode that set as the bits of an integer (a **bitmask**): bit j is 1 if item j is in the set. Each item is either in or out, so:

```formula
subsets = 2^n
2^20 = 1,048,576 ≈ 10^6
where
subsets: the number of different sets (bitmasks) that can be formed from the items
n: the number of items
2^n: n copies of 2 multiplied together
≈: approximately equal to
In words: every item doubles the number of possible sets, because each existing set can either include it or not.
```

With n items there are 2ⁿ subsets, so practical limits depend on the number of dimensions, transitions, representation and available resources; the following table shows growth, not a hardware guarantee.

| Items | Subsets | Endpoint slots | Work proxy |
|---|---|---|---|
| 10 | 1,024 | ~10⁴ | ~10⁵ |
| 16 | 65,536 | ~10⁶ | ~1.7 × 10⁷ |
| 20 | ~10⁶ | ~2 × 10⁷ | ~4 × 10⁸ |
| 25 | ~3.4 × 10⁷ | ~8 × 10⁸ | ~2 × 10¹⁰ |

```formula
slots = n 2^n
work = n^2 2^n
where
slots: the allocated entries when a DP also records one of n possible endpoints
work: a rough upper-work expression with up to n transitions per entry
n: the number of items
In words: Adding an endpoint and transition choice multiplies subset growth by one factor of the item count each.
```

For example, start with cities zero, one and three included. Setting the bit for city two adds it; testing that bit before adding it reports absence. The following expression fragment assumes `mask` holds decimal 11, `j` is 2 and `n` is 5. It shows operations rather than printing their results.

The bit operations you need:

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
