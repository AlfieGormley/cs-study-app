---
id: cx-resizing-policies
sourceLesson: cx-amortised-analysis
title: Growth policies and safe shrinking
level: advanced
minutes: 4
summary: Choose growth and shrink thresholds that avoid repeated full-array copying.
---

Here n is the number of stored elements or appends. Amortised bounds depend on the resizing policy as well as the data structure.

## Why the growth must be geometric

Suppose instead the array grows by a **fixed amount**, say 10 slots each time. Resizes happen at sizes 10, 20, 30, ..., and each copies the whole array:

```formula
copies = 10 + 20 + 30 + … + n
copies = 10 × (1 + 2 + … + n / 10)
copies ≈ 10 × (n / 10)^2 / 2 = n^2 / 20
n = 10^6:  copies ≈ 10^12 / 20 = 5 × 10^10
where
copies: the total number of element copies over n appends
n: the number of appends (a multiple of 10 here)
n^2: n squared, n × n
…: "and so on"
≈: approximately equal to (lower-order terms dropped)
In words: the copy sizes grow in a straight line rather than doubling, so they add up to a quadratic total, about n squared over 20.
```

That is about 5 × 10^10 copies for a million appends, and the amortised cost per append is Θ(n), growing in proportion to n. Growing by a constant *factor* is what makes the series geometric and the amortised cost O(1).

The factor doesn't have to be 2. Suppose each resize multiplies the capacity by a growth factor g, starting from capacity 1. Ignoring integer rounding:

```formula
copies = 1 + g + g^2 + … + C / g
copies = (C − 1) / (g − 1)
n ≤ C < g × n
where
copies: the total number of element copies over all resizes
g: the growth factor, any fixed number greater than 1 (2 for doubling, 1.5, 1.125, …)
g^2: g × g
C: the final capacity after n appends
n: the number of appends
…: "and so on"
≤: less than or equal to
In words: each resize copies the old capacity, those capacities form a geometric series, and the series adds up to a constant multiple of the final capacity, which is itself within a factor g of n.
```

So the copying is at most about g × n / (g − 1), a constant times n. Since n ≤ C < g × n, a bound in terms of arbitrary n needs the extra factor g. The smaller estimate n / (g − 1) applies near a full final capacity. With g = 2 it gives about n copies; with g = 1.5 about 2n. Real implementations differ:

| Implementation | Growth |
|---|---|
| CPython `list` | ~1.125x + small constant |
| OpenJDK `ArrayList` single-item growth | preferred ~1.5x; implementation detail |
| C++ libstdc++ `vector` single-item growth | commonly ~2x; implementation detail |
| Rust `Vec` | amortised O(1) push; no particular growth factor guaranteed |

CPython's comment in `listobject.c` gives the capacities as 0, 4, 8, 16, 24, 32, 40, 52, 64, 76, ... A smaller factor wastes less memory on empty slots but copies more often. Any factor above 1 keeps appends O(1) amortised.

## Shrinking without thrashing

If the array also supports `pop`, you may want to free memory as it empties. The obvious rule, "halve the capacity when it becomes half full", has a nasty failure.

Suppose the array is exactly full at capacity k. Append: double to 2k (k copies). Pop: now half full, halve back to k (k copies). Append again: full, double again. Alternating push and pop at that boundary makes **every operation cost Θ(n)**, proportional to the number of elements n (which is about k).

The fix is **hysteresis**: grow when full, but shrink only when the array is a **quarter** full, and then halve. After any resize the array is half full, so at least Θ(capacity) cheap operations must happen before the next resize. Both push and pop are then O(1) amortised.

## Key takeaways
- A fixed multiplicative growth factor preserves constant amortised append cost in the copy-on-resize model.
- Adding a fixed number of slots leads to a quadratic total copy cost.
- Separated growth and shrink thresholds prevent alternating operations from forcing a resize each time.

## Further reading
- [Dynamic array — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_array)
- [CPython listobject.c (list growth policy)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
