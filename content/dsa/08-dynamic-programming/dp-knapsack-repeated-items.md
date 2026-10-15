---
id: dp-knapsack-repeated-items
title: Unbounded and bounded item supplies
level: intermediate
minutes: 3
summary: Ascending capacities deliberately allow repeated copies.
sourceLesson: dp-knapsack
---

## Unbounded knapsack

Unlimited copies of each item. Same array, loop the weight limit **upwards**:

```python
def knapsack_unbounded(items, W):
    items = tuple(items)
    if (type(W) is not int or W < 0
            or any(type(w) is not int
                   or type(v) is not int
                   or w <= 0 or v < 0
                   for w, v in items)):
        raise ValueError("knapsack domain")
    best = [0] * (W + 1)
    for w, v in items:
        # Updated smaller capacities allow
        # reuse.
        for c in range(w, W + 1):
            best[c] = max(best[c],
                          best[c - w] + v)
    return best[W]
```

Now `best[c - w]` may already contain copies of this item, which is exactly what we want. Example: items (3 kg, 4), (4 kg, 5), (5 kg, 6), weight limit 10 kg. 0/1 gives 11 (4 + 5 kg); unbounded gives 13 (3 + 3 + 4 kg).

The earlier coin-change problem is unbounded knapsack: "minimum coins" is min-count knapsack, "number of ways" is counting knapsack.

**Bounded knapsack** (item i available up to a limited number of times) can be solved by splitting each item into bundles of 1, 2, 4, ... copies, plus a final remainder, so that every count from 0 to the limit is a sum of distinct bundles:

```formula
k_i = 1 + 2 + 4 + ... + 2^{t − 1} + r
bundles = O(log_2(k_i + 1))
k_i = 13 = 1 + 2 + 4 + 6
where
k_i: how many copies of item i are available
t: how many power-of-two bundles fit (1, 2, 4, ... up to 2^{t − 1})
2^{t − 1}: t − 1 copies of 2 multiplied together, the largest power-of-two bundle
r: the remainder bundle, whatever is left after the powers of two (0 up to 2^t − 1)
bundles: the number of 0/1 items produced for item i
log_2(k_i + 1): the base-2 logarithm of k_i + 1, roughly how many times you can halve it
O(...): Big-O, growing at most in proportion to the expression inside
In words: split k_i copies into doubling bundles plus a leftover; any count up to k_i can be made by picking some bundles, and there are only about log_2(k_i) of them.
```

With 13 copies, bundles of 1, 2, 4 and 6 replace 13 separate items with 4; any count from 0 to 13 is a sum of distinct bundles (for example 9 = 1 + 2 + 6). A limit of 0 contributes no items.

## Key takeaways
- Ascending capacities deliberately allow repeated copies.
- A bounded supply can be represented by doubling bundles and a remainder.

## Further reading
- [Knapsack recurrences](https://cp-algorithms.com/dynamic_programming/knapsack.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
