---
id: tech-divide-conquer-closest-code
title: Keeping closest-pair combination linear
level: intermediate
minutes: 2
sourceLesson: tech-divide-conquer
summary: Preserve y order throughout recursion rather than sorting every strip.
---

The previous unit proved that the strip needs at most seven later neighbours per point. Here n is the number of points; px and py hold the same distinct points sorted by x and y. The implementation maintains that ordering so every combine stays linear.

The combine step is O(n), provided you keep a y-sorted list rather than re-sorting the strip at every level. Re-sorting costs O(n log n) per level, which would give O(n log² n) in total, where log is any fixed-base logarithm; the squared logarithm multiplies that logarithm by itself.

The implementation returns the minimum distance (infinity for fewer than two points). Coordinates must be finite real numbers with meaningful subtraction; `hypot` uses floating-point arithmetic, so exact geometric predicates would need a different numeric representation. Hash-based partitioning assumes expected constant-time tuple lookup.

```python
from math import hypot

def dist(p, q):
    return hypot(p[0] - q[0], p[1] - q[1])

def brute_force(points):
    return min((dist(p, q)
                for i, p
                in enumerate(points)
                for q in points[i+1:]),
               default=float("inf"))

def closest(points):
    points = [tuple(p) for p in points]
    # Coincident points make the distance
    # zero.
    if len(set(points)) != len(points):
        return 0.0
    py = sorted(points, key=lambda p: p[1])
    return _closest(sorted(points), py)

def _closest(px, py):    # distinct points
    n = len(px)
    if n <= 3:
        return brute_force(px)
    mid = n // 2
    mx = px[mid][0]
    lx, rx = px[:mid], px[mid:]
    lset = set(lx)
    # Partition while preserving y order.
    ly = [p for p in py if p in lset]
    ry = [p for p in py if p not in lset]
    d = min(_closest(lx, ly),
            _closest(rx, ry))
    strip = [p for p in py
             if abs(p[0] - mx) < d]
    for i, p in enumerate(strip):
        # The packing proof permits seven
        # neighbours.
        for q in strip[i+1:i+8]:
            d = min(d, dist(p, q))
    return d
```

## Key takeaways
- Preserve y order throughout recursion rather than sorting every strip.
- Finite distinct coordinates, floating-point distance and expected hash lookup are explicit implementation assumptions.

## Further reading
- [Closest pair — Dartmouth notes](https://cs.dartmouth.edu/~deepc/LecNotes/cs31/lec7.pdf)
- [Python hypot](https://docs.python.org/3/library/math.html#math.hypot)
