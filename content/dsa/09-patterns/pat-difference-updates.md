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

Each update touches only two cells of the difference array, `d`, which has one more cell than the output so that an update ending at the last element has somewhere to switch off:

```formula reference
x[i] = d[0] + d[1] + … + d[i]
where
x[i]: the final value of element i
d: the difference array after all updates; each update adds v at index l and subtracts v at index r + 1
i: an index from 0 to n − 1
n: the number of elements
v: the amount one update adds to every element from index l to index r inclusive
l: the first index an update covers
r: the last index an update covers
…: "and so on", continuing the same pattern
In words: each final value is the running total of the difference array up to that index, so every update switched on at or before it and not yet switched off is counted once.
```

Each update is O(1); one prefix-sum pass at the end rebuilds the array. Total O(n + u) for u updates instead of O(n × u).

```
n = 5, updates (1,3,+2), (0,1,+5), (2,4,-1)

d after:  [5, 2, -6, 0, -2, 1]
          (index 5 is the spill slot)
prefix:   [5, 7, 1, 1, -1]
```

Check index 2: covered by `+2` and `-1`, so 1. Correct.

> [!analogy] Real-world analogy: passengers on a bus
> A bus driver doesn't record who is on board between every pair of stops. They note how many people get on and off at each stop, and the number on board between stops is the running total of those changes.
>
> **How it maps:** think of element i as the stretch of road after stop i. A group of v people on board for stretches l to r is a range update: +v at the stop where they board (`d[l] += v`) and −v at the stop where they get off (`d[r + 1] -= v`). The final prefix pass is the driver adding up boardings and alightings as the bus travels.
>
> **Where it stops:** the driver can read the count at any moment, but a plain difference array only gives correct values after the final prefix pass; reading in between needs another pass or a Fenwick tree. Passenger counts change by whole people, while the array accepts any added value, including negative ones.

> [!example] Where you see this
> "Car pooling" (can a car with C seats take every trip?) and "flight bookings" are difference arrays over time or flight number. For positive-duration start-inclusive, end-exclusive bookings `[start,end)`, mark +1 at the start and −1 at the end, then sweep. Inclusive discrete ranges instead cancel just after the last included index. The interval units call this a **sweep line**.

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
