---
id: tech-divide-conquer-closest-proof
title: Why closest-pair checks seven neighbours
level: intermediate
minutes: 3
sourceLesson: tech-divide-conquer
summary: Cross-half improvements must lie in a narrow strip.
---

## Closest pair of points

Given n points in the plane, find the two closest. Brute force checks every pair: for a thousand points that is 499,500 pairs, and the number of pairs grows like n², so brute force is O(n²).

Divide and conquer does it in O(n log n) time, where n is still the number of points.

1. Sort the points by x once. Split them with a vertical line at the median x.
2. Recursively find the closest distance on each side. Call the smaller of the two answers δ (delta): the best distance found so far.
3. The only pairs left to check are those that **straddle** the line. A straddling pair closer than δ must have both points within δ of the line, in a strip of width 2δ (δ on each side).

```
         |<- δ ->|<- δ ->|
   .     |   .   |       |    .
     .   |       |  .    |
  .      |  .    |   .   |  .
         |     strip     |
           mid line
```

4. Maintain y order through the recursion; extract the strip in that order. Compare each point with the next **7** points.

## Why only 7 neighbours?

Fix a point p in the strip. Any partner closer than δ that comes after p in y order lies in a rectangle δ tall and 2δ wide just above p, straddling the line.

Split that rectangle into eight small squares, each δ/2 on a side: four on the left of the line and four on the right. Assign a point that sits exactly on the line to the half it came from, and look at each half's four squares separately.

The key fact is that **two points from the same half can't share a small square**. The furthest apart two points in a square can be is its diagonal, about 0.71δ, which is less than δ. But every pair within one half is at least δ apart, because δ is no bigger than that half's closest distance. So each small square holds at most one point of its half.

```formula reference
g = √(s^2 + s^2) = δ / √(2) ≈ 0.707δ
where
g: the length of a small square's diagonal, the furthest apart two points inside it can be
s: the side length of each small square, δ / 2
δ: delta, the smallest distance found within either half
√: the square root
≈: approximately equal to
In words: two points in the same small square are at most about 0.71 δ apart, which is closer than δ.
```

That allows at most eight points in the rectangle, one of which is p itself, leaving at most **7** others. Any point further along in y order is too far above p to beat δ. The bound is a proof for every input of distinct points, not a heuristic, and it keeps the combine step linear.

> [!analogy] Real-world analogy: socially distanced guests on square tiles
> At a reception where every guest must stand at least two metres from every other, a square tile whose diagonal is shorter than two metres can never hold two guests at once.
>
> **How it maps:** the guests are points from one half, the two-metre rule is "same-half points are at least δ apart", and the tiles are the δ/2 squares. Counting tiles near a guest bounds how many other guests can be close by, which is the "at most 7" bound.
>
> **Where it stops:** the distancing rule only applies within one half of the room, which is why each side's tiles are counted separately; a guest from the other side may stand closer than δ, and finding such a pair is exactly what the strip check is for.

## Key takeaways
- Cross-half improvements must lie in a narrow strip.
- Within each recursive half, small-square packing bounds the relevant neighbours.

## Further reading
- [Closest pair — Dartmouth notes](https://cs.dartmouth.edu/~deepc/LecNotes/cs31/lec7.pdf)
