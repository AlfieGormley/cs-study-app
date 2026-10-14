---
id: tech-backtracking-problems-queens
title: Modelling N-Queens and attack checks
level: advanced
minutes: 4
sourceLesson: tech-backtracking-problems
summary: One queen per row removes impossible placements before search begins.
---

The previous lesson's template enumerates everything. Real backtracking problems are about **search**: the tree is astronomically large, and the craft lies in rejecting bad branches as early and cheaply as possible.

Three ideas do most of the work:

1. **Model the problem well**, so the tree is small to begin with.
2. **Make constraint checks inexpensive**, using incremental bookkeeping where possible.
3. **Propagate consequences** of each choice, so dead ends are spotted before you walk into them.

## N-Queens

Place n queens on an n × n board so that no two share a row, column or diagonal.

### Modelling shrinks the tree

For an eight-by-eight board, compare three ways of framing the search. Each extra piece of structure you build into the model shrinks the number of candidate placements:

```formula
N_any = C(64, 8) = 4,426,165,368
N_row = 8^8 = 16,777,216
N_perm = 8! = 40,320
where
N_any: placements choosing any 8 of the 64 squares
C(64, 8): "64 choose 8", the number of ways to pick 8 squares from 64 when order doesn't matter
N_row: placements with exactly one queen in each row (8 column choices for each of 8 rows)
8^8: 8 copies of 8 multiplied together
N_perm: placements with one queen per row and per column (each row takes a different column)
8!: 8 factorial, 8 × 7 × … × 1
In words: one queen per row cuts 4.4 billion candidates to 16.8 million, and one per column as well cuts them to 40,320.
```

| Model | Candidates |
|---|---|
| Any 8 of 64 squares | 4,426,165,368 |
| One queen per row | 16,777,216 |
| One per row and column | 40,320 |

Backtracking row by row, rejecting a column the moment it's attacked, makes only **2,057** calls to find all **92** solutions. Each layer of reasoning (rows, then columns, then diagonals checked early) cuts orders of magnitude.

### O(1) attack checks

Every square on the same down-right diagonal has the same `row − col`; every square on the same down-left (anti-) diagonal has the same `row + col`. Moving one step down-right adds 1 to both row and column, so their difference stays the same; moving down-left adds 1 to the row and takes 1 from the column, so their sum stays the same:

```formula
r_1 − c_1 = r_2 − c_2
r_1 + c_1 = r_2 + c_2
1 + 2 = 3 + 0 = 3
where
r_1: the row number of the first square, counting from 0 at the top
c_1: the column number of the first square, counting from 0 at the left
r_2: the row number of the second square
c_2: the column number of the second square
In words: the first line holds exactly when two squares share a down-right diagonal (row minus column matches); the second holds exactly when they share an anti-diagonal (row plus column matches); squares (1, 2) and (3, 0) both have sum 3.
```

```
row-col on a 4x4      row+col on a 4x4
  0 -1 -2 -3            0  1  2  3
  1  0 -1 -2            1  2  3  4
  2  1  0 -1            2  3  4  5
  3  2  1  0            3  4  5  6
```

Three sets support expected O(1) lookup per square in the usual hash-table/word-cost model:

```python
def solve_n_queens(n):
    # Reject inputs outside the stated
    # domain.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    cols, diag, anti = set(), set(), set()
    queens, out = [], []
    def place(r):
        if r == n:
            out.append(queens[:])
            return
        for c in range(n):
            if (c in cols or r - c in diag
                    or r + c in anti):
                continue          # attacked
            # Register the column and both
            # diagonals.
            cols.add(c)
            diag.add(r - c)
            anti.add(r + c)
            queens.append(c)
            place(r + 1)
            cols.remove(c)
            diag.remove(r - c)
            anti.remove(r + c)
            # Undo every attack marker and
            # this placement.
            queens.pop()
    place(0)
    return out

# n=4 -> [[1, 3, 0, 2], [2, 0, 3, 1]]
```

For board sides four, five, six, seven, eight, ten and twelve respectively, the solution counts are 2, 10, 4, 40, 92, 724 and 14,200.

## Key takeaways
- One queen per row removes impossible placements before search begins.
- Columns and diagonal identities support incremental attack checks and complete undo.

## Further reading
- [N-Queens construction and modelling](https://warwick.ac.uk/fac/sci/maths/general/outreach/urss/n-queens-urss-workbook_16.pdf)
