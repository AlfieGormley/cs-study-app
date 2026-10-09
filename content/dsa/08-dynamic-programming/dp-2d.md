---
id: dp-2d
title: 2-D DP on grids and strings
level: intermediate
minutes: 19
summary: Unique paths, edit distance and longest common subsequence as tables, how to read and reconstruct them, and how to cut memory to one or two rows.
---

When the state needs two numbers, the DP becomes a table. Two shapes dominate:

- **Grids**: the state is a cell `(r, c)`, and moves go right or down.
- **Two strings**: the state is a pair of prefix lengths `(i, j)`, meaning "the first i characters of A and the first j of B".

The second is really the first in disguise. Comparing two strings *is* walking a grid, where a diagonal step means "use a character from both" and a horizontal or vertical step means "use a character from only one".

## Unique paths

> A robot starts in the top-left of an m × n grid and can move only right or down. How many paths reach the bottom-right?

- **State**: `P[r][c]` = number of paths from the start to `(r, c)`.
- **Recurrence**: you arrived from above or from the left.
- **Base**: every cell in the top row and left column has exactly one path.

```formula
P[r][c] = P[r − 1][c] + P[r][c − 1]
P[0][c] = P[r][0] = 1
P[2][2] = P[1][2] + P[2][1] = 3 + 3 = 6
where
P[r][c]: the number of right/down paths from the top-left cell to the cell in row r, column c
r: the row number, 0 at the top, up to m − 1
c: the column number, 0 at the left, up to n − 1
m: the number of rows in the grid
n: the number of columns in the grid
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
paths: the number of right/down paths from the top-left to the bottom-right of an m × n grid
m: the number of rows (3 here)
n: the number of columns (7 here)
C(a, b): "a choose b", the number of ways to choose b items from a distinct items
a, b: whole numbers with b no larger than a
!: factorial, the product of every whole number from 1 up to the number (4! = 24, and 0! = 1)
In words: every path is m + n − 2 moves, of which exactly m − 1 go down, so count the ways to choose which moves are the downward ones.
```

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
    if n == 0:
        return 0
    row = [0] * n
    row[0] = 1
    for r in grid:
        for c in range(n):
            if r[c] == 1:
                row[c] = 0
            elif c > 0:
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
r: the row number, 0 at the top
c: the column number, 0 at the left
min: the smaller of the two values
In words: the cheapest way into a cell is its own cost plus the cheaper of the two cells you could have come from.
```

A neighbour that doesn't exist (above the top row or left of the first column) counts as +∞ (positive infinity), so it is never chosen. Path counts use integer slots whose bit sizes can grow; the usual grid time bounds count additions as unit cost.

## Edit distance (Levenshtein)

> The minimum number of unit-cost insertions, deletions and substitutions to turn A into B. Python strings are sequences of Unicode code points here; user-perceived characters may contain several code points.

`kitten` → `sitting` is 3: substitute k→s, substitute e→i, insert g.

**State**: `D[i][j]` = edit distance between `A[:i]` and `B[:j]`.

**Recurrence**: look at the last characters `A[i-1]` and `B[j-1]`.

- If they're equal, no edit is needed for them: `D[i][j] = D[i-1][j-1]`.
- Otherwise take the cheapest of three edits, each costing 1:
  - **delete** `A[i-1]`: `D[i-1][j] + 1`
  - **insert** `B[j-1]`: `D[i][j-1] + 1`
  - **substitute**: `D[i-1][j-1] + 1`

**Base**: `D[i][0] = i` (delete everything), `D[0][j] = j` (insert everything).

```formula
D[i][j] = D[i − 1][j − 1]   if A_i = B_j
D[i][j] = 1 + min(D[i − 1][j],
  D[i][j − 1], D[i − 1][j − 1])   otherwise
D[i][0] = i
D[0][j] = j
where
D[i][j]: the edit distance between the first i characters of A and the first j characters of B
A, B: the two strings being compared
A_i: the ith character of A, counting from 1 (A[i-1] in Python)
B_j: the jth character of B, counting from 1 (B[j-1] in Python)
i: how many characters of A are in the prefix, 0 to m
j: how many characters of B are in the prefix, 0 to n
m: the length of A
n: the length of B
min: the smallest of the three values
In words: if the last characters match, keep them for free; otherwise pay one edit for whichever of delete, insert or substitute leaves the cheapest smaller problem.
```

For example, the `horse` → `ros` table below has D[1][1] = 1 + min(D[0][1], D[1][0], D[0][0]) = 1 + min(1, 1, 0) = 1, because h and r differ.

```python
def edit_distance(a, b):
    m, n = len(a), len(b)
    D = [[0] * (n+1) for _ in range(m+1)]
    for i in range(m + 1):
        D[i][0] = i
    for j in range(n + 1):
        D[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                D[i][j] = D[i - 1][j - 1]
            else:
                D[i][j] = 1 + min(
                    D[i-1][j],    # delete
                    D[i][j-1],    # insert
                    D[i-1][j-1])  # subst
    return D[m][n]
```

The table for `horse` → `ros`:

```
       ""   r   o   s
 ""     0   1   2   3
 h      1   1   2   3
 o      2   2   1   2
 r      3   2   2   2
 s      4   3   3   2
 e      5   4   4   3
```

Answer `D[5][3] = 3`: horse → rorse (substitute h→r) → rose (delete r) → ros (delete e).

To **reconstruct** the edits, start at the bottom-right and step back to whichever neighbour produced the value: diagonal with equal characters (match), diagonal +1 (substitute), up +1 (delete), left +1 (insert).

**Complexity**: one constant-time step per table cell:

```formula
T = O((m + 1) × (n + 1)) = O(m × n)
M_roll = O(min(m, n) + 1)
where
T: the running time, and also the number of table slots for the full table
m: the length of string A
n: the length of string B
M_roll: the memory needed when only rolling rows are kept (see below)
min: the smaller of the two lengths
O(...): Big-O, growing at most in proportion to the expression inside
In words: the table has a cell for every pair of prefix lengths, and each cell takes a fixed amount of work.
```

Two 1,000-character strings need about 1,000,000 cells. The O(m × n) form is the usual shorthand for nonempty strings.

> [!note] Why "matching characters → take the diagonal" is safe
> When the last characters match, there's always an optimal alignment that pairs them. You might worry that deleting or inserting could be better, but any such solution can be rearranged into one that pairs the matching ends at no extra cost. Many implementations still take `min` over all three for safety; it gives the same answer.

## Longest common subsequence

> The longest sequence of characters that appears, in order but not necessarily next to each other, in both strings.

`LCS("ABCBDAB", "BDCABA") = 4`, for example `"BCBA"`.

**State**: `L[i][j]` = LCS length of `A[:i]` and `B[:j]`.

**Recurrence**:

- If `A[i-1] == B[j-1]`: use the character, and extend the LCS of both shorter prefixes.
- Otherwise: drop one of the last characters and keep the better result.

**Base**: row 0 and column 0 are all 0.

```formula
L[i][j] = L[i − 1][j − 1] + 1   if A_i = B_j
L[i][j] = max(L[i − 1][j], L[i][j − 1])
   otherwise
L[i][0] = L[0][j] = 0
where
L[i][j]: the length of the longest common subsequence of the first i characters of A and the first j characters of B
A, B: the two strings
A_i: the ith character of A, counting from 1 (A[i-1] in Python)
B_j: the jth character of B, counting from 1
i: the prefix length of A, 0 to m
j: the prefix length of B, 0 to n
m, n: the lengths of A and B
max: the larger of the two values
In words: matching last characters add one to the answer for both shorter prefixes; otherwise the answer is the better of dropping A's last character or B's.
```

For `A = "ABCB"`, `B = "BDCAB"`:

```
       ""  B  D  C  A  B
 ""     0  0  0  0  0  0
 A      0  0  0  0  1  1
 B      0  1  1  1  1  2
 C      0  1  1  2  2  2
 B      0  1  1  2  2  3
```

`L[4][5] = 3` ("BCB").

**Reconstruction**: from `(m, n)`, if the characters match, emit the character and go diagonal; otherwise move to whichever of up or left has the larger value. You collect the LCS backwards, so reverse it at the end.

```python
def lcs(a, b):
    m, n = len(a), len(b)
    L = [[0] * (n+1) for _ in range(m+1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i - 1][j],
                              L[i][j - 1])
    out, i, j = [], m, n
    while i and j:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i, j = i - 1, j - 1
        elif L[i - 1][j] >= L[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return ''.join(reversed(out))
```

LCS and edit distance are cousins. If only insertions and deletions (indels) are allowed (no substitutions), every character not in the LCS must be deleted from A or inserted from B:

```formula
D_id = (m − ℓ) + (n − ℓ) = m + n − 2 × ℓ
D_id = 4 + 5 − 2 × 3 = 3
where
D_id: the insert/delete-only edit distance between A and B
m: the length of A
n: the length of B
ℓ: the LCS length of A and B (L[m][n])
m − ℓ: the characters of A to delete
n − ℓ: the characters of B to insert
In words: keep the longest common subsequence, delete the rest of A and insert the rest of B.
```

The example is A = "ABCB", B = "BDCAB" from the table above, with LCS length 3.

### Subsequence vs substring

The **longest common substring** (one unbroken run of characters) is a different DP:

```formula
S[i][j] = S[i − 1][j − 1] + 1   if A_i = B_j
S[i][j] = 0   otherwise
answer = max of S[i][j] for all i, j
where
S[i][j]: the length of the longest common suffix (matching run that ends at both positions) of the first i characters of A and the first j characters of B
A_i, B_j: the ith character of A and the jth character of B, counting from 1
i, j: prefix lengths of A and B
answer: the length of the longest common substring
max: the largest value
In words: a matching character extends the run that ended just before it in both strings; a mismatch breaks the run back to zero, and the best run can end anywhere.
```

The **0** on a mismatch is the difference from LCS, and it is why the answer is the maximum cell anywhere in the table, not the bottom-right.

## Space optimisation: rolling rows

All three recurrences only look at the current row and the previous row. So keep two rows and swap them:

```python
def lcs_length(a, b):
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            if x == y:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j],
                             cur[j - 1])
        prev = cur
    return prev[-1]
```

With m the length of `a` and n the length of `b`, memory falls from O(m·n) to O(n). Make the **shorter** string the columns to get O(min(m, n)), where min picks the smaller length.

You can go down to a **single row**, but recurrences that read the diagonal `[i-1][j-1]` need a saved copy, because by the time you reach column j you've overwritten column j − 1 with the current row:

```python
row = list(range(len(b) + 1))
for i, x in enumerate(a, 1):
    diag, row[0] = row[0], i
    for j, y in enumerate(b, 1):
        up = row[j]          # old row[j]
        if x == y:
            row[j] = diag
        else:
            row[j] = 1 + min(up, row[j-1],
                             diag)
        diag = up  # next cell's diag
```

The catch: with rolling rows you **lose the stored history for a direct traceback**, because the earlier rows are gone. If you need both linear memory and the alignment itself, use **Hirschberg's algorithm**, which finds the midpoint of the optimal path with a forward and a backward pass and recurses. For nonempty strings it retains O(mn) time and O(m + n) space including output; the exact constant depends on the implementation. Repeated full recomputation is another space/time tradeoff.

## In the real world

- **Line diff** is related to LCS and shortest insertion/deletion scripts. Myers’ algorithm has an O(N × D) bound, where N is the total input length and D is the insertion/deletion distance, so it is fast when the files are similar. GNU diff and Git use related algorithms and heuristics; default output need not be minimal. Git offers `--minimal` and alternative algorithms such as `--patience`.
- **Spell checkers and fuzzy search** rank suggestions by edit distance; PostgreSQL's `fuzzystrmatch` extension provides `levenshtein()`.
- **Bioinformatics**: Needleman–Wunsch (global alignment) and Smith–Waterman (local alignment) are sequence-alignment DPs with scores for matches, mismatches and gaps; local alignment also allows restarting at zero. Aligning two 100,000-base sequences is 100,000 × 100,000 = 10¹⁰ (ten billion) cells, which is why real tools use heuristics (like BLAST) and banding.

> [!warning] Quadratic is real
> Edit distance of two 100,000-character strings is 10¹⁰ cell updates. It's widely believed that no algorithm can do it in strongly subquadratic time: a 2015 result by Backurs and Indyk showed that would refute the Strong Exponential Time Hypothesis. In practice, if you only care whether the distance is at most some threshold k, a **banded** DP fills only a narrow band around the diagonal. That works because every step off the diagonal costs at least one insertion or deletion.

```formula
|m − n| > k   gives   D > k
|i − j| ≤ k
T = O((k + 1) × max(m, n))
where
k: the largest distance you care about, a whole number 0 or more
m, n: the lengths of the two strings
D: the true edit distance
i, j: the row and column of a table cell (prefix lengths); the banded DP fills only cells where |i − j| ≤ k
|x|: the absolute value of x, its size ignoring sign (|−3| = 3)
max: the larger of the two lengths
T: the work of the banded DP, in cell updates
O(...): Big-O, growing at most in proportion to the expression inside
In words: if the lengths differ by more than k the answer is "no"; otherwise only cells within k of the diagonal can lie on a path of cost k or less.
```

With k = 20 and two 100,000-character strings, the band is 41 cells wide: about 4 million cells instead of 10 billion. This includes k = 0 (a band one cell wide, an equality check).

## Pitfalls

1. **Off-by-one between string and table indices.** `D[i][j]` covers `A[:i]`, so the last character is `A[i-1]`. Pad the table with an extra row and column for the empty prefix.
2. **Using `L[m][n]` for longest common substring.** The answer can be anywhere in the table.
3. **Overwriting the diagonal** in a single-row optimisation.
4. **Building `[[0] * n] * m`** in Python: that's m references to the *same* row, so writing one cell writes the whole column. Use a list comprehension.

## Key takeaways
- Two-string DPs are grid DPs over prefix pairs `(i, j)`: diagonal = use both characters, up/left = skip one.
- Edit distance: match → diagonal; otherwise 1 + min(delete, insert, substitute). Base cases are i and j.
- LCS: match → diagonal + 1; otherwise max(up, left). Reconstruct by walking back from the corner.
- Most grid DPs depend only on the previous row, so rolling rows cut memory to O(min(m, n)) for strings of lengths m and n, but direct traceback needs retained choices or additional computation, such as Hirschberg’s technique.
- The basic edit-distance DP is quadratic for equal nonempty lengths. A truly subquadratic exact algorithm would refute SETH; this is a conditional lower bound, not a proof that every algorithm on two length-n strings is Θ(n²) (quadratic). Banding helps with small thresholds.

## Further reading
- [Levenshtein distance — Wikipedia](https://en.wikipedia.org/wiki/Levenshtein_distance)
- [Wagner–Fischer algorithm — Wikipedia](https://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm)
- [Longest common subsequence — Wikipedia](https://en.wikipedia.org/wiki/Longest_common_subsequence)
- [Hirschberg's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Hirschberg%27s_algorithm)
- [Needleman–Wunsch algorithm — Wikipedia](https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm)
- [Diff — Wikipedia](https://en.wikipedia.org/wiki/Diff)
