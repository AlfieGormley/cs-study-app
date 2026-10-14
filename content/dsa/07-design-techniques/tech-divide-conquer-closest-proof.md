---
id: tech-divide-conquer-closest-proof
title: Why closest-pair checks seven neighbours
level: intermediate
minutes: 3
sourceLesson: tech-divide-conquer
summary: Cross-half improvements must lie in a narrow strip.
---

## Closest pair of points

Given n points in the plane, find the two closest. Brute force checks every pair:

```formula
P = (n(n − 1)) / 2
P = 1000 × 999 / 2 = 499,500
where
P: the number of distinct pairs of points
n: the number of points; 1000 in the example line
In words: each of the n points pairs with the n − 1 others, and dividing by 2 stops each pair being counted twice; this grows like n², so brute force is O(n²).
```

Divide and conquer does it in O(n log n) time, where n is still the number of points.

1. Sort the points by x once. Split them with a vertical line at the median x.
2. Recursively find the closest distance on each side, and keep the smaller:

```formula
δ = min(δ_L, δ_R)
where
δ: delta, the smallest distance found so far, in the same units as the coordinates
δ_L: the closest-pair distance among the points left of the line
δ_R: the closest-pair distance among the points right of the line
min: the minimum function, which returns the smaller of its inputs
In words: the best answer so far is whichever half had the closer pair.
```

3. The only pairs left to check are those that **straddle** the line. Both points must lie within δ of it, in a strip of width 2δ (δ on each side).

```
         |<- δ ->|<- δ ->|
   .     |   .   |       |    .
     .   |       |  .    |
  .      |  .    |   .   |  .
         |     strip     |
           mid line
```

4. Maintain y order through the recursion; extract the strip in that order. Compare each point with the next **7** points.

Why only 7? Any point closer than δ must lie in a rectangle δ tall and 2δ wide above it. Split that rectangle into eight small squares, each δ/2 on a side: assign boundary points to their recursive half and apply the four-square packing argument within each half. The key fact is that no two points inside one small square can be δ apart or more (δ is the current same-half distance bound):

```formula
s = δ / 2
g = √(s^2 + s^2) = δ / √(2)
g ≈ 0.707δ < δ
where
s: the side length of each small square
δ: delta, the smallest distance found within either half
g: the length of a small square's diagonal, the furthest apart two points inside it can be
√: the square root
≈: approximately equal to
In words: two points in the same small square are at most about 0.71 δ apart, which is closer than δ.
```

Two points of the same half in one such square would therefore be closer than δ, contradicting that half’s distance bound. So at most one point from the relevant half per small square, eight in total including the point itself, which leaves at most 7 others to compare with.

## Key takeaways
- Cross-half improvements must lie in a narrow strip.
- Within each recursive half, small-square packing bounds the relevant neighbours.

## Further reading
- [Closest pair — Dartmouth notes](https://cs.dartmouth.edu/~deepc/LecNotes/cs31/lec7.pdf)
