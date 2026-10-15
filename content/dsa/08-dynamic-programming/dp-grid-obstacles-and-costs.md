---
id: dp-grid-obstacles-and-costs
title: Grid obstacles and rolling path costs
level: intermediate
minutes: 3
summary: Blocked cells reset their path count to zero.
sourceLesson: dp-2d
---

The empty-grid path count adds the answers from above and left. Preserve that dependency shape while adding blocked cells or cell costs.

The DP earns its keep once the closed form stops working, for instance with **obstacles**:

```python
def paths(grid):  # 1 = blocked
    if not grid:
        return 0
    n = len(grid[0])
    if any(len(r) != n for r in grid):
        raise ValueError("rectangular grid")
    if any(x not in (0, 1)
           for r in grid for x in r):
        raise ValueError("binary grid")
    # No columns means no start or end cell.
    if n == 0:
        return 0
    row = [0] * n
    # Seed the start before obstacle
    # handling.
    row[0] = 1
    for r in grid:
        for c in range(n):
            # No path can pass through a
            # blocked cell.
            if r[c] == 1:
                row[c] = 0
            elif c > 0:
                # Old value is above;
                # updated neighbour left.
                row[c] += row[c - 1]
    return row[-1]
```

For a 3 × 3 grid with the centre blocked, this returns 2 (around the top-right or around the bottom-left).

Notice the single `row` array. Before the update, `row[c]` still holds the value from the row above; `row[c-1]` has already been updated to the current row. So `row[c] += row[c-1]` is exactly `above + left`. That's the **rolling array** trick, and it takes memory from O(m·n) to O(n).

**Minimum path sum** (each cell has a cost; find the cheapest right/down path) uses the same shape with `min` instead of `+`:

```formula
D[0][0] = g[0][0]
D[r][c] = g[r][c]
  + min(D[r − 1][c], D[r][c − 1])
where
D[r][c]: the smallest total cost of any right/down path from the top-left to the cell in row r, column c, including both end cells
g[r][c]: the cost written in that cell (grid[r][c] in code)
r: the row number, 0 at the top; the recurrence applies to cells other than the separately initialised start
c: the column number, 0 at the left
min: the smaller of the two values
In words: the cheapest way into a cell is its own cost plus the cheaper of the two cells you could have come from.
```

A neighbour that doesn't exist (above the top row or left of the first column) counts as +∞ (positive infinity), so it is never chosen. Path counts use integer slots whose bit sizes can grow; the usual grid time bounds count additions as unit cost.

## Key takeaways
- Blocked cells reset their path count to zero.
- A rolling row holds above before update and left after update.
- Minimum-cost paths use the same dependency shape with min.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming)
