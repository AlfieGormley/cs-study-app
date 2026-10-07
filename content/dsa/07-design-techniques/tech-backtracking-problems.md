---
id: tech-backtracking-problems
title: Backtracking problems in depth
level: advanced
minutes: 15
summary: N-Queens, Sudoku and word search worked through properly, then the techniques real solvers use to tame exponential search: smart variable ordering, forward checking and constraint propagation.
---

The previous lesson's template enumerates everything. Real backtracking problems are about **search**: the tree is astronomically large, and the craft lies in rejecting bad branches as early and cheaply as possible.

Three ideas do most of the work:

1. **Model the problem well**, so the tree is small to begin with.
2. **Make constraint checks inexpensive**, using incremental bookkeeping where possible.
3. **Propagate consequences** of each choice, so dead ends are spotted before you walk into them.

## N-Queens

Place n queens on an n × n board so that no two share a row, column or diagonal.

### Modelling shrinks the tree

For n = 8, compare three ways of framing the search:

| Model | Candidates |
|---|---|
| Any 8 of 64 squares | 4,426,165,368 |
| One queen per row | 8⁸ = 16,777,216 |
| One per row and column | 8! = 40,320 |

Backtracking row by row, rejecting a column the moment it's attacked, makes only **2,057** calls to find all **92** solutions. Each layer of reasoning (rows, then columns, then diagonals checked early) cuts orders of magnitude.

### O(1) attack checks

Every square on the same down-right diagonal has the same `row − col`; every square on the same down-left (anti-) diagonal has the same `row + col`.

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
            cols.add(c)
            diag.add(r - c)
            anti.add(r + c)
            queens.append(c)
            place(r + 1)
            cols.remove(c)
            diag.remove(r - c)
            anti.remove(r + c)
            queens.pop()
    place(0)
    return out

# n=4 -> [[1, 3, 0, 2], [2, 0, 3, 1]]
```

Solution counts grow quickly: 2 for n = 4, 10 for n = 5, 4 for n = 6, 40 for n = 7, 92 for n = 8, 724 for n = 10, 14,200 for n = 12.

### Bitmasks for speed

An alternative uses integer bitmasks instead of sets. Bit i of `cols` means column i is taken. The diagonal masks shift by one each row because a diagonal moves one column per row.

```python
def count_queens(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    full = (1 << n) - 1
    def go(cols, d1, d2):
        if cols == full:
            return 1
        total = 0
        free = full & ~(cols | d1 | d2)
        while free:
            bit = free & -free   # lowest 1
            free -= bit
            total += go(
                cols | bit,
                ((d1 | bit) << 1) & full,
                (d2 | bit) >> 1)
        return total
    return go(0, 0, 0)
```

`free & -free` isolates the lowest set bit (two's complement trick), so each loop iteration jumps straight to the next legal column. The count for n = 12 is 14,200. Python integer bit operations scale with the number of machine words needed to hold the masks.

> [!note] Content gap
> The original tenth-of-a-second runtime is omitted: no pinned machine and interpreter benchmark establishes it.

> [!note] N-Queens has a direct construction
> For n = 1 and every n ≥ 4, direct constructions can place one solution in O(n) output operations without backtracking; n = 2 and n = 3 have no solution. Backtracking matters when you need all solutions, or for variants with extra constraints.

## Sudoku

Fill a 9 × 9 grid so each row, column and 3 × 3 box contains 1–9 once. Each empty cell is a **variable** with **domain** {1..9}, and the rules are **constraints** between cells: Sudoku is a textbook **constraint satisfaction problem (CSP)**.

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
                empty.append((r, c))

    def cands(r, c):
        b = r//3*3 + c//3
        used = rows[r] | cols[c] | boxes[b]
        return [d for d in range(1, 10)
                if d not in used]

    def bt():
        if not empty:
            return True
        i = min(range(len(empty)),
                key=lambda i:
                    len(cands(*empty[i])))
        r, c = empty.pop(i)
        b = r//3*3 + c//3
        for d in cands(r, c):
            grid[r][c] = d
            rows[r].add(d)
            cols[c].add(d)
            boxes[b].add(d)
            if bt():
                return True
            rows[r].remove(d)
            cols[c].remove(d)
            boxes[b].remove(d)
        grid[r][c] = 0
        empty.insert(i, (r, c))
        return False

    return bt()
```

> [!note] Content gap
> The claimed 4,209-versus-52 call comparison is omitted because the original test did not provide an exact puzzle, baseline solver and counting convention. MRV can reduce search, but the improvement is instance-dependent.

### Constraint propagation

MRV picks good cells; **propagation** goes further by deducing values before guessing. Peter Norvig's well-known solver keeps a set of possible digits for every cell and applies two rules repeatedly:

1. **Naked single**: if a cell has only one possible digit, assign it and remove that digit from all its 20 peers.
2. **Hidden single**: if a digit has only one possible cell in a row, column or box, it must go there.

Each assignment can trigger more eliminations, which trigger more assignments. Many easy puzzles are solved by propagation alone, with no search at all. When propagation stalls, the solver picks the MRV cell, guesses, propagates again, and backtracks if any cell's set becomes empty.

## Word search

Given a rectangular grid of single-character strings, is a word spelled by a path of horizontally or vertically adjacent cells, using each cell at most once? The empty word is accepted; a non-empty word on an empty board is rejected.

```python
def exist(board, word):
    if not word:
        return True
    if not board or not board[0]:
        return False
    R, C = len(board), len(board[0])
    if any(len(row) != C for row in board):
        raise ValueError("ragged board")
    if len(word) > R * C:
        return False
    used = object()  # cannot equal a letter
    def dfs(r, c, k):
        if k == len(word):
            return True
        if not (0 <= r < R and 0 <= c < C):
            return False
        if board[r][c] != word[k]:
            return False
        ch, board[r][c] = board[r][c], used
        found = (dfs(r+1, c, k+1) or
                 dfs(r-1, c, k+1) or
                 dfs(r, c+1, k+1) or
                 dfs(r, c-1, k+1))
        board[r][c] = ch          # restore
        return found
    return any(dfs(r, c, 0)
               for r in range(R)
               for c in range(C))
```

- **Choose** = temporarily replace the cell with a unique object, which cannot equal a string character. This avoids a separate visited set; relative speed requires measurement.
- **Unchoose** = restore the letter. Forget this and a failed path permanently blocks cells that a later path needs.
- **Prune** = the letter mismatch check, which can reject a branch immediately; its effectiveness depends on the grid and word.

Complexity: R·C starting cells; the first step has 4 directions and every later step at most 3 (you can't go back), so the worst case is **O(R·C·3ᴸ)** for a word of length L. Mismatches and boundaries can reduce this upper bound, but no reduction is guaranteed for every input.

### Many words at once

To find which of thousands of words appear in the grid, don't run `exist` per word. Put all words in a **trie** and do one DFS from each cell that walks the grid and the trie together. You stop as soon as the current path isn't a prefix of any word, and you clear a found word’s terminal marker and optionally delete exhausted branches, preserving nodes still needed by longer words.

## Constraint propagation in general

All of this generalises to CSPs: variables, domains and constraints. Solvers combine backtracking with:

| Technique | Idea |
|---|---|
| MRV | Branch on the smallest domain |
| Degree heuristic | Tie-break by most constraints |
| Least constraining value | Try values that leave neighbours most options |
| Forward checking | After assigning, prune neighbours' domains; fail if one empties |
| Arc consistency (AC-3) | For binary constraints, retain a value only if it has support in each constrained neighbour |

**Forward checking** looks one step ahead. **Arc consistency** propagates further: removing a value from one domain can remove values from others, and so on, until nothing changes. Propagation has a per-node cost and can reduce the search tree; whether it improves runtime depends on the instance and implementation.

**Exact cover.** A 9 × 9 Sudoku has 729 potential candidate rows (cell × digit) and 324 exactly-once constraint columns before givens remove candidates. Knuth’s **Algorithm X** can be implemented with **dancing links** (DLX): restoring an individual removed link/node takes O(1), while undoing a whole choice may restore many nodes. N-Queens uses exactly-one row/column constraints and **at-most-one diagonal** constraints, so the direct formulation needs optional secondary columns (generalised exact cover) or another encoding.

**SAT solvers.** The DPLL algorithm is backtracking plus **unit propagation** (an unsatisfied clause with one unassigned literal and all others false forces it). Modern CDCL solvers add clause learning and non-chronological backjumping, and can solve substantial structured instances; size alone does not determine difficulty. They power hardware verification, scheduling and package managers: libsolv (used by DNF and by conda's libmamba solver) resolves dependencies with SAT techniques, while pip's resolver backtracks over candidate versions.

## Pitfalls

- **Expensive validity checks.** Scanning units costs their length; fixed 9 × 9 Sudoku has constant-size units. Incremental sets give expected constant-time membership, and bitmask cost depends on the represented width.
- **Incomplete undo.** Every structure updated in "choose" (grid, sets, masks, the empty list) must be restored in "unchoose".
- **Continuing after success.** If you need one solution, propagate a `True` back up and stop.
- **Symmetry.** N-Queens solutions come in groups of up to 8 under rotation and reflection (8-Queens has 12 fundamentally different solutions). Breaking symmetry, for example searching mirrored first-row branches only once, can reduce work. For odd n, handle the centre column separately; enumerating all solutions requires restoring omitted symmetric solutions.

## Key takeaways
- A good model (one queen per row) can shrink the search space by orders of magnitude before any pruning.
- Make constraint checks inexpensive with expected constant-time set membership or appropriately sized bitmasks: `r - c` and `r + c` identify diagonals.
- Branch on the most constrained variable; it exposes forced moves and dead ends early.
- Constraint propagation (naked and hidden singles, forward checking, arc consistency) deduces values instead of guessing.
- Word search marks cells in place and must restore them; many words at once call for a trie.

## Further reading
- [Eight queens puzzle — Wikipedia](https://en.wikipedia.org/wiki/Eight_queens_puzzle)
- [Peter Norvig: Solving Every Sudoku Puzzle](https://norvig.com/sudoku.html)
- [Sudoku solving algorithms — Wikipedia](https://en.wikipedia.org/wiki/Sudoku_solving_algorithms)
- [Constraint satisfaction problem — Wikipedia](https://en.wikipedia.org/wiki/Constraint_satisfaction_problem)
- [AC-3 algorithm — Wikipedia](https://en.wikipedia.org/wiki/AC-3_algorithm)
- [Dancing Links — Wikipedia](https://en.wikipedia.org/wiki/Dancing_Links)
- [DPLL algorithm — Wikipedia](https://en.wikipedia.org/wiki/DPLL_algorithm)
