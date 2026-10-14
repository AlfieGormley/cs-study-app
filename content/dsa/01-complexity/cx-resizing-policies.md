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
copies = 10 + 20 + … + (n − 10)
copies = 10 × (1 + 2 + … + (n/10 − 1))
copies ≈ 10 × (n / 10)^2 / 2 = n^2 / 20
n = 10^6:  copies ≈ 10^12 / 20 = 5 × 10^10
where
copies: the total number of element copies over n appends
n: the number of appends, a multiple of 10 of at least 20 here, starting with capacity 10; filling the last block does not yet trigger another resize
…: "and so on"
≈: approximately equal to (lower-order terms dropped)
In words: the copy sizes grow in a straight line rather than doubling, so they add up to a quadratic total, about n squared over 20.
```

That is about 5 × 10^10 copies for a million appends, and the amortised cost per append is Θ(n), growing in proportion to n. Growing by a constant *factor* is what makes the series geometric and the amortised cost O(1).

The factor doesn't have to be 2. Suppose each resize multiplies the capacity by a growth factor g, starting from capacity 1. Ignoring integer rounding:

```formula
copies = 1 + g + g^2 + … + C / g
copies = (C − 1) / (g − 1)
n ≤ C < g n
copies < gn / (g − 1)
copies ≈ n / (g − 1) when C ≈ n
g = 2: copies ≈ n
g = 1.5: copies ≈ 2n
where
copies: the total number of element copies over all resizes
g: the growth factor, any fixed number greater than 1 (2 for doubling, 1.5, 1.125, …)
C: the final capacity after n appends
n: the number of appends
…: "and so on"
≤: less than or equal to
≈: approximately, near full final capacity and ignoring rounding
In words: each resize copies the old capacity, those capacities form a geometric series, and the series adds up to a constant multiple of the final capacity, which is itself within a factor g of n.
```

The bound in terms of an arbitrary append count needs the growth-factor multiplier because final capacity may exceed current size. Near a full final capacity, the smaller estimate applies. Doubling gives roughly one copy per stored element, while growth by one-half gives roughly two, as the card shows. Real implementations differ:

| Implementation | Growth |
|---|---|
| CPython `list` | ~1.125x + small constant |
| OpenJDK `ArrayList` single-item growth | preferred ~1.5x; implementation detail |
| C++ libstdc++ `vector` single-item growth | commonly ~2x; implementation detail |
| Rust `Vec` | amortised O(1) push; no particular growth factor guaranteed |

CPython's comment in `listobject.c` gives the capacities as 0, 4, 8, 16, 24, 32, 40, 52, 64, 76, ... A smaller factor wastes less memory on empty slots but copies more often. Any factor above 1 keeps appends O(1) amortised.

## Shrinking without thrashing

If the array also supports `pop`, you may want to free memory as it empties. The obvious rule, "halve the capacity when it becomes half full", has a nasty failure.

Suppose the array is exactly full. Append doubles its capacity, copying the old contents. Pop makes it half full, triggering a shrink back to the original capacity and another full copy. Append again doubles it once more. Alternating push and pop at that boundary makes **every operation cost Θ(n)**, where n is the element count, close to the original capacity.

```formula
C_before = k, C_grow = 2k
C_shrink = k
W_grow = k, W_shrink = k
where
C_before, C_grow, C_shrink: the capacities before append, after growth and after the following shrink, in element slots
k: the original full capacity, in slots
W_grow, W_shrink: the element-copy counts for those two resizes
In words: Alternating append and pop repeatedly copies the whole original array, because the growth and shrink thresholds meet at the same boundary.
```

The fix is **hysteresis**: grow when full, but shrink only when the array is a **quarter** full, and then halve. After any resize the array is half full, so at least Θ(capacity) cheap operations must happen before the next resize. Both push and pop are then O(1) amortised.

## Key takeaways
- A fixed multiplicative growth factor preserves constant amortised append cost in the copy-on-resize model.
- Adding a fixed number of slots leads to a quadratic total copy cost.
- Separated growth and shrink thresholds prevent alternating operations from forcing a resize each time.

## Further reading
- [Dynamic array — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_array)
- [CPython listobject.c (list growth policy)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
