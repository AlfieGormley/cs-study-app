---
id: dp-grid-path-counts
title: Count paths on an empty grid
level: intermediate
minutes: 3
summary: A path into a cell came from above or from the left.
sourceLesson: dp-2d
---

When the state needs two numbers, the DP becomes a table. Two shapes dominate:

- **Grids**: the state is a cell `(r, c)`, and moves go right or down.
- **Two strings**: the state is a pair of prefix lengths `(i, j)`, meaning "the first i characters of A and the first j of B".

The second is really the first in disguise. Comparing two strings *is* walking a grid, where a diagonal step means "use a character from both" and a horizontal or vertical step means "use a character from only one".

## Unique paths

> A robot starts in the top-left of a grid with m rows and n columns and can move only right or down. How many paths reach the bottom-right?

- **State**: `P[r][c]` records number of paths from the start to `(r, c)`.
- **Recurrence**: you arrived from above or from the left.
- **Base**: every cell in the top row and left column has exactly one path.

```formula
P[r][c] = P[r − 1][c] + P[r][c − 1]
  for r ≥ 1 and c ≥ 1
P[0][c] = P[r][0] = 1
P[2][2] = P[1][2] + P[2][1] = 3 + 3 = 6
where
P[r][c]: the number of right/down paths from the top-left cell to the cell in row r, column c
r: the row number, 0 at the top, up to m − 1
c: the column number, 0 at the left, up to n − 1
m: the number of rows in the grid
n: the positive number of columns in the grid
≥: greater than or equal to
In words: the last move into a cell came either from the cell above or from the cell to the left, so add the paths to those two.
```

```
 1   1   1   1   1   1   1
 1   2   3   4   5   6   7
 1   3   6  10  15  21  28
```

A 3 × 7 grid has 28 paths. That's Pascal's triangle on its side, and there is a closed form (a direct formula with no table):

```formula
paths = C(m + n − 2, m − 1)
C(a, b) = a! / (b! × (a − b)!)
paths = C(8, 2) = 8! / (2! × 6!) = 28
where
paths: the number of right/down paths from the top-left to the bottom-right of a grid with m rows and n columns
m: the number of rows (3 here)
n: the number of columns (7 here)
C(a, b): "a choose b", the number of ways to choose b items from a distinct items
a, b: whole numbers with b no larger than a
!: factorial, the product of every whole number from 1 up to the number (4! = 24, and 0! = 1)
In words: every path is m + n − 2 moves, of which exactly m − 1 go down, so count the ways to choose which moves are the downward ones.
```

## Key takeaways
- A path into a cell came from above or from the left.
- On an empty grid, choosing the downward moves gives a binomial closed form.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming)
