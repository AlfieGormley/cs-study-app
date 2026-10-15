---
id: pat-difference-updates
title: Record starts and stops for batched updates
level: intermediate
minutes: 4
sourceLesson: pat-prefix-sums
summary: An inclusive update switches on at its first index and off just after its last index.
---

Here n is the array length and u is the number of updates. The batch starts with zeros; updates are applied before the final array is read.

## Difference arrays: batched range updates

Prefix sums make **range queries** cheap. The inverse trick makes **range updates** cheap.

**Problem.** Start with `n` zeros. Apply many updates "add `v` to every element in `[l, r]`", then report the final array.

Doing each update directly is O(r − l + 1). Instead, record only where each update *starts* and *stops*:

```python
def apply_updates(n, updates):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    d = [0] * (n + 1)
    for l, r, v in updates:  # inclusive
        if (type(l) is not int
                or type(r) is not int
                or not 0 <= l <= r < n):
            raise ValueError("bad range")
        # Switch the range increment on.
        d[l] += v
        # Switch it off after the included
        # end.
        d[r + 1] -= v
    out, run = [], 0
    for i in range(n):
        # Recover all increments active
        # here.
        run += d[i]
        out.append(run)
    return out
```

Each update touches two cells of the difference array:

```formula
d_new[l] = d_old[l] + v
d_new[r + 1] = d_old[r + 1] − v
x[i] = d[0] + d[1] + … + d[i]
where
d_old: the difference array before this update
d_new: the difference array after this update
d: the accumulated difference array after all updates, with one more cell than the output; the extra cell at index n catches updates ending at the last element
l: the first index the update covers
r: the last index the update covers (inclusive)
v: the amount added to every element in [l, r]
x[i]: the final value of element i, the prefix sum of d up to i
i: an index from 0 to n − 1
n: the number of elements
…: "and so on", continuing the same pattern
In words: +v at l switches the update on, −v just after r switches it off, and a running total carries the switched-on amounts across the range.
```

Each update is O(1); one prefix-sum pass at the end rebuilds the array. Total O(n + u) for u updates instead of O(n × u).

```
n = 5, updates (1,3,+2), (0,1,+5), (2,4,-1)

d after:  [5, 2, -6, 0, -2, 1]
          (index 5 is the spill slot)
prefix:   [5, 7, 1, 1, -1]
```

Check index 2: covered by `+2` and `-1`, so 1. Correct.

> [!example] Where you see this
> "Car pooling" (can a car with C seats take every trip?) and "flight bookings" are difference arrays over time or flight number. For positive-duration start-inclusive, end-exclusive bookings `[start,end)`, mark +1 at the start and −1 at the end, then sweep. Inclusive discrete ranges instead cancel just after the last included index. The interval units calls this a **sweep line**.

The efficient batch use applies updates before rebuilding the values. Interleaved queries are possible but a plain difference array may need O(n) work per read. A Fenwick tree over differences supports range-add/point-query in O(log n); two Fenwick trees or an appropriately lazy segment tree support range-add/range-sum.

## Key takeaways
- An inclusive update switches on at its first index and off just after its last index.
- One final prefix pass reconstructs all batch-updated values.
- Efficient interleaved updates and queries need an appropriate tree rather than repeated rebuilding.

## Further reading
- [Prefix sums — USACO Guide](https://usaco.guide/silver/prefix-sums)
- [More on prefix sums (2-D, difference arrays) — USACO Guide](https://usaco.guide/silver/more-prefix-sums)
- [Prefix sum — Wikipedia](https://en.wikipedia.org/wiki/Prefix_sum)
- [Summed-area table — Wikipedia](https://en.wikipedia.org/wiki/Summed-area_table)
