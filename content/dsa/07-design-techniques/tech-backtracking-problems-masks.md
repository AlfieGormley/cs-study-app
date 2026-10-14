---
id: tech-backtracking-problems-masks
title: Counting N-Queens with bitmasks
level: advanced
minutes: 2
sourceLesson: tech-backtracking-problems
summary: A mask represents legal columns, and its lowest set bit selects one branch.
---

The previous unit placed one queen per row, tracking occupied columns and diagonals. This version counts solutions rather than storing placements. The non-negative integer n is the board side length; a column is one bit in each mask.

### Bitmasks for speed

An alternative uses integer bitmasks instead of sets. Bit i of `cols` means column i is taken. The diagonal masks shift by one each row because a diagonal moves one column per row.

```python
def count_queens(n):
    # Reject inputs outside the stated
    # domain.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    # Keep exactly n usable column bits.
    full = (1 << n) - 1
    def go(cols, d1, d2):
        if cols == full:
            return 1
        total = 0
        # Only unattacked board columns
        # remain.
        free = full & ~(cols | d1 | d2)
        while free:
            bit = free & -free   # lowest 1
            # Try each legal column once at
            # this depth.
            free -= bit
            total += go(
                cols | bit,
                ((d1 | bit) << 1) & full,
                (d2 | bit) >> 1)
        return total
    return go(0, 0, 0)
```

`free & -free` isolates the lowest set bit (two's complement trick), so each loop iteration jumps straight to the next legal column. A twelve-by-twelve board has 14,200 solutions. Python integer bit operations scale with the number of machine words needed to hold the masks.

> [!note] Counts are not timings
> A count of 14,200 solutions does not predict execution time. Interpreter, machine, mask width and search strategy affect a benchmark.

> [!note] N-Queens has a direct construction
> For a board side n of one or at least four, direct constructions can place one solution in O(n) output operations without backtracking; board sides two and three have no solution. Backtracking matters when you need all solutions, or for variants with extra constraints.

## Key takeaways
- A mask represents legal columns, and its lowest set bit selects one branch.
- Mask operations and enumeration costs depend on board width and the requested outputs.

## Further reading
- [N-Queens construction and modelling](https://warwick.ac.uk/fac/sci/maths/general/outreach/urss/n-queens-urss-workbook_16.pdf)
