---
id: dp-knapsack-backward-loop
title: Use each item once with a backward loop
level: intermediate
minutes: 2
summary: Descending capacities read the previous item row.
sourceLesson: dp-knapsack
---

The previous table used one row per item. Compressing it to one row is correct only when each read still represents the earlier item row.

### One row, iterated backwards

Each row only reads the previous row, at the same or a smaller weight limit. So use a single array and loop the weight limit **downwards**:

```python
def knapsack_01(items, W):
    items = tuple(items)
    if (type(W) is not int or W < 0
            or any(type(w) is not int
                   or type(v) is not int
                   or w <= 0 or v < 0
                   for w, v in items)):
        raise ValueError("knapsack domain")
    best = [0] * (W + 1)
    for w, v in items:
        # Read earlier-item values before
        # reuse.
        for c in range(W, w - 1, -1):
            best[c] = max(best[c],
                          best[c - w] + v)
    return best[W]
```

Why downwards? When you update `best[c]`, you read `best[c - w]`. Going downwards, `best[c - w]` hasn't been touched yet in this round, so it still holds the "previous row" value: item i hasn't been used. Going upwards, `best[c - w]` may already include item i, so you'd use it twice.

> [!warning] The one-character bug
> Loop direction is the only difference between 0/1 and unbounded knapsack in the 1-D form. With one item of weight 2 and value 3 and weight limit 6, the downward loop gives 3 (one copy), and the upward loop gives 9 (three copies). Get the direction wrong and your 0/1 solution silently becomes unbounded.

## Key takeaways
- Descending capacities read the previous item row.
- Ascending capacities can reuse the same item and change the problem.

## Further reading
- [Knapsack recurrences](https://cp-algorithms.com/dynamic_programming/knapsack.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
