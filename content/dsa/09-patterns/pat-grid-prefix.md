---
id: pat-grid-prefix
title: Apply inclusion–exclusion to rectangle sums
level: intermediate
minutes: 5
sourceLesson: pat-prefix-sums
summary: A zero row and column simplify rectangle boundaries.
---

The earlier prefix-subtraction idea extends to grids. The example uses exact integer arithmetic with constant-cost operations; returned and auxiliary storage must both be counted.

## 2-D prefix sums

For a grid, let `P[r][c]` be the sum of the rectangle from `(0, 0)` up to but not including row `r` and column `c`. Build it with inclusion–exclusion:

```formula
P[r+1][c+1] = g[r][c]
  + P[r][c+1]
  + P[r+1][c]
  − P[r][c]
where
P[r][c]: the sum of the rectangle of cells above row r and left of column c (rows 0 to r − 1, columns 0 to c − 1); row 0 and column 0 of P are all zero
g[r][c]: the value in the grid at row r, column c, counting from 0
r: a row index of the grid
c: a column index of the grid
In words: the new corner total is the new cell, plus the rectangle above it, plus the rectangle to its left, minus the top-left rectangle that both of those included.
```

```python
def build_2d(g):
    R = len(g)
    C = len(g[0]) if R else 0
    if any(len(row) != C for row in g):
        raise ValueError("rectangular grid")
    P = [[0] * (C + 1)
         for _ in range(R + 1)]
    for r in range(R):
        for c in range(C):
            # Subtract the twice-counted
            # corner.
            P[r+1][c+1] = (
                g[r][c] + P[r][c+1]
                + P[r+1][c] - P[r][c])
    return P

def rect(P, r1, c1, r2, c2):  # inclusive
    # Requires a valid nonempty rectangle.
    return (P[r2+1][c2+1] - P[r1][c2+1]
            - P[r2+1][c1] + P[r1][c1])
```

The query subtracts the strip above and the strip to the left, then adds back the corner that was subtracted twice:

```
  +-----+-------+
  |  D  |   B   |      want = A
  +-----+-------+      total(A+B+C+D)
  |  C  |   A   |      - (B+D) - (C+D)
  +-----+-------+      + D
```

The drawing’s letters identify four regions. In the formula below, each letter denotes that region’s cell sum:

```formula
T = A + B + C + D
S_A = T − (B + D) − (C + D) + D
S_A = A
where
T: the total cell sum over all four regions
A: the cell sum in the selected lower-right region
B: the cell sum in the upper-right region
C: the cell sum in the lower-left region
D: the cell sum in the upper-left region
S_A: the recovered sum in the selected region
In words: remove the upper strip and left strip from the total, then restore their shared corner; only the selected region remains.
```

For the grid

```
3 0 1 4
5 6 3 2
1 2 0 1
```

the prefix table is

```
P = 0  0  0  0  0
    0  3  3  4  8
    0  8 14 18 24
    0  9 17 21 28
```

and the rectangle rows 1–2, columns 1–2 (the cells 6, 3, 2, 0) comes from four lookups:

```formula
A = P[r2+1][c2+1] − P[r1][c2+1]
  − P[r2+1][c1] + P[r1][c1]
A = P[3][3] − P[1][3] − P[3][1] + P[1][1]
A = 21 − 4 − 9 + 3 = 11
where
A: the sum of the rectangle from row r1 to row r2 and column c1 to column c2, all inclusive
P[r][c]: the sum of all cells above row r and left of column c
r1: the top row of the rectangle; here 1
r2: the bottom row; here 2
c1: the left column; here 1
c2: the right column; here 2
In words: take everything up to the bottom-right corner, remove the strip above and the strip to the left, then add back the top-left block that was removed twice; 6 + 3 + 2 + 0 = 11 checks it.
```

This is the **summed-area table** from computer graphics, introduced for texture mapping in 1984. The Viola–Jones face detector used it (as the "integral image") to evaluate rectangular features in constant time, which helped make real-time face detection practical in the early 2000s.

## Recognising the pattern

- Many **range-sum queries** on a static array or grid.
- "Subarray sum **equals** / is **divisible by** k", especially with negatives.
- "Equal number of X and Y in a subarray" (map one to −1, look for sum 0).
- Many **range updates** followed by reads: difference array.
- Products work too (prefix products, or "product of array except self" with prefix and suffix passes), but watch out for zeros.

## Recap of the pattern family
- A padded prefix totals the elements before its index; an inclusive range subtracts the prefix before its start from the prefix just after its end.
- "Subarray sum equals k" becomes "count earlier prefixes equal to run − k", O(n) with a hash map and safe with negatives.
- Difference arrays make each range update O(1); one prefix pass recovers the final values.
- 2-D prefix sums answer any rectangle sum in O(1) with inclusion–exclusion.
- For interleaved updates and queries, move to a Fenwick or segment tree.

## Key takeaways
- A zero row and column simplify rectangle boundaries.
- Remove the upper and left strips, then restore their doubly removed corner.
- Static grid queries take constant arithmetic work after a table build.

## Further reading
- [Prefix sums — USACO Guide](https://usaco.guide/silver/prefix-sums)
- [More on prefix sums (2-D, difference arrays) — USACO Guide](https://usaco.guide/silver/more-prefix-sums)
- [Prefix sum — Wikipedia](https://en.wikipedia.org/wiki/Prefix_sum)
- [Summed-area table — Wikipedia](https://en.wikipedia.org/wiki/Summed-area_table)
