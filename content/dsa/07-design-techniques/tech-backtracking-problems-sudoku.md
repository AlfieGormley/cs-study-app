---
id: tech-backtracking-problems-sudoku
title: Sudoku search with MRV
level: advanced
minutes: 3
sourceLesson: tech-backtracking-problems
summary: Choose the empty cell with the fewest candidates to expose forced moves or failure.
---

Unlike queens, Sudoku has one variable per empty cell. We will keep its constraints in row, column and box sets, then search for one completion. Zero marks an empty cell; the displayed solver mutates a list of nine row lists.

## Sudoku

Fill a 9 × 9 grid so each row, column and 3 × 3 box contains 1–9 once. Each empty cell is a **CSP variable** with **CSP domain** {1..9}, and the rules are **CSP constraints** between cells: Sudoku is a textbook **constraint satisfaction problem (CSP)**.

### Plain backtracking

Take the first empty cell, try each digit that doesn't clash with its row, column or box, recurse, undo on failure. It works, but it is blind: it may pick a cell with seven options when another cell has only one.

### Most constrained variable first (MRV)

Choose the empty cell with the **fewest remaining candidates**. Two reasons this helps:

- A cell with one candidate is a forced move: no branching at all.
- A cell with zero candidates proves the current branch is dead, immediately.

```python
def solve(grid):
    if (len(grid) != 9
            or any(len(row) != 9
                   for row in grid)):
        raise ValueError("expected 9 by 9")
    if any(type(d) is not int
           or not 0 <= d <= 9
           for row in grid for d in row):
        raise ValueError("digits 0..9")
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empty = []
    for r in range(9):
        for c in range(9):
            if d := grid[r][c]:
                b = r//3*3 + c//3
                if (d in rows[r]
                        or d in cols[c]
                        or d in boxes[b]):
                    return False
                rows[r].add(d)
                cols[c].add(d)
                boxes[r//3*3 + c//3].add(d)
            else:
                # Record empty cells for
                # variable selection.
                empty.append((r, c))

    def cands(r, c):
        b = r//3*3 + c//3
        # Any unit can exclude a candidate
        # digit.
        used = rows[r] | cols[c] | boxes[b]
        return [d for d in range(1, 10)
                if d not in used]

    def bt():
        if not empty:
            return True
        i = min(range(len(empty)),
                key=lambda i:
                    len(cands(*empty[i])))
        # Remove the most constrained empty
        # cell.
        r, c = empty.pop(i)
        b = r//3*3 + c//3
        for d in cands(r, c):
            grid[r][c] = d
            rows[r].add(d)
            cols[c].add(d)
            boxes[b].add(d)
            # Return on the first complete
            # solution.
            if bt():
                return True
            rows[r].remove(d)
            cols[c].remove(d)
            boxes[b].remove(d)
        grid[r][c] = 0
        # Restore this cell at its former
        # position.
        empty.insert(i, (r, c))
        return False

    return bt()
```

> [!note] Heuristics depend on the puzzle
> MRV can reduce search, but its improvement is instance-dependent. Compare an exact puzzle and baseline solver with the same call-counting convention before drawing a numerical conclusion.

## Key takeaways
- Choose the empty cell with the fewest candidates to expose forced moves or failure.
- Restore grid, unit sets and the empty-cell list together when a branch fails.

## Further reading
- [Peter Norvig: Solving Every Sudoku Puzzle](https://norvig.com/sudoku.html)
