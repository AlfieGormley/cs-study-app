---
id: dp-2d
title: 2-D DP on grids and strings
level: intermediate
minutes: 15
summary: Unique paths, edit distance and longest common subsequence as tables, how to read and reconstruct them, and how to cut memory to one or two rows.
---

When the state needs two numbers, the DP becomes a table. Two shapes dominate:

- **Grids**: the state is a cell `(r, c)`, and moves go right or down.
- **Two strings**: the state is a pair of prefix lengths `(i, j)`, meaning "the first i characters of A and the first j of B".

The second is really the first in disguise. Comparing two strings *is* walking a grid, where a diagonal step means "use a character from both" and a horizontal or vertical step means "use a character from only one".

## Unique paths

> A robot starts in the top-left of an m × n grid and can move only right or down. How many paths reach the bottom-right?

- **State**: `P[r][c]` = number of paths from the start to `(r, c)`.
- **Recurrence**: you arrived from above or from the left: `P[r][c] = P[r-1][c] + P[r][c-1]`.
- **Base**: every cell in the top row and left column has exactly one path.

```
 1   1   1   1   1   1   1
 1   2   3   4   5   6   7
 1   3   6  10  15  21  28
```

A 3 × 7 grid has 28 paths. (That's Pascal's triangle on its side; the closed form is `C(m+n−2, m−1)`, here `C(8, 2) = 28`.)

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

**Minimum path sum** uses `D[0][0] = grid[0][0]` and `D[r][c] = grid[r][c] + min(D[r-1][c], D[r][c-1])`, treating unavailable predecessors as +∞. Path counts use integer slots whose bit sizes can grow; the usual grid time bounds count additions as unit cost.

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

**Complexity**: O((m + 1)(n + 1)) time and table slots, conventionally O(mn) for nonempty strings; O(min(m, n) + 1) slots with appropriately oriented rolling rows.

> [!note] Why "matching characters → take the diagonal" is safe
> When the last characters match, there's always an optimal alignment that pairs them. You might worry that deleting or inserting could be better, but any such solution can be rearranged into one that pairs the matching ends at no extra cost. Many implementations still take `min` over all three for safety; it gives the same answer.

## Longest common subsequence

> The longest sequence of characters that appears, in order but not necessarily contiguously, in both strings.

`LCS("ABCBDAB", "BDCABA") = 4`, for example `"BCBA"`.

**State**: `L[i][j]` = LCS length of `A[:i]` and `B[:j]`.

**Recurrence**:

- If `A[i-1] == B[j-1]`: `L[i][j] = L[i-1][j-1] + 1` (use the character).
- Otherwise: `L[i][j] = max(L[i-1][j], L[i][j-1])` (drop one of the last characters).

**Base**: row 0 and column 0 are all 0.

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

> [!tip] LCS and edit distance are cousins
> If only insertions and deletions are allowed (no substitutions), the edit distance is `m + n − 2·LCS`. Every character not in the LCS must be deleted from A or inserted from B.

### Subsequence vs substring

The **longest common substring** (contiguous) is a different DP: `S[i][j]` = length of the common suffix of `A[:i]` and `B[:j]`, which is `S[i-1][j-1] + 1` on a match and **0** otherwise. The answer is the maximum cell anywhere in the table, not the bottom-right.

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

Memory falls from O(m·n) to O(n). Make the **shorter** string the columns to get O(min(m, n)).

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

- **Line diff** is related to LCS and shortest insertion/deletion scripts. Myers’ algorithm has an O(ND) bound (N is total input length, D is insertion/deletion distance). GNU diff and Git use related algorithms and heuristics; default output need not be minimal. Git offers `--minimal` and alternative algorithms such as `--patience`.
- **Spell checkers and fuzzy search** rank suggestions by edit distance; PostgreSQL's `fuzzystrmatch` extension provides `levenshtein()`.
- **Bioinformatics**: Needleman–Wunsch (global alignment) and Smith–Waterman (local alignment) are sequence-alignment DPs with scores for matches, mismatches and gaps; local alignment also allows restarting at zero. Aligning two 10⁵-base sequences is 10¹⁰ cells, which is why real tools use heuristics (like BLAST) and banding.

> [!warning] Quadratic is real
> Edit distance of two 100,000-character strings is 10¹⁰ cell updates. It's widely believed that no algorithm can do it in strongly subquadratic time: a 2015 result by Backurs and Indyk showed that would refute the Strong Exponential Time Hypothesis. In practice, if you only care whether the distance is at most k, a **banded** unit-cost edit DP can reject |m − n| > k and otherwise fill only |i − j| ≤ k in O((k + 1)·max(m, n)) work. This includes k = 0.

## Pitfalls

1. **Off-by-one between string and table indices.** `D[i][j]` covers `A[:i]`, so the last character is `A[i-1]`. Pad the table with an extra row and column for the empty prefix.
2. **Using `L[m][n]` for longest common substring.** The answer can be anywhere in the table.
3. **Overwriting the diagonal** in a single-row optimisation.
4. **Building `[[0] * n] * m`** in Python: that's m references to the *same* row, so writing one cell writes the whole column. Use a list comprehension.

## Key takeaways
- Two-string DPs are grid DPs over prefix pairs `(i, j)`: diagonal = use both characters, up/left = skip one.
- Edit distance: match → diagonal; otherwise 1 + min(delete, insert, substitute). Base cases are i and j.
- LCS: match → diagonal + 1; otherwise max(up, left). Reconstruct by walking back from the corner.
- Most grid DPs depend only on the previous row, so rolling rows cut memory to O(min(m, n)), but direct traceback needs retained choices or additional computation, such as Hirschberg’s technique.
- The basic edit-distance DP is quadratic for equal nonempty lengths. A truly subquadratic exact algorithm would refute SETH; this is a conditional lower bound, not a proof that every algorithm is Θ(n²). Banding helps with small thresholds.

## Further reading
- [Levenshtein distance — Wikipedia](https://en.wikipedia.org/wiki/Levenshtein_distance)
- [Wagner–Fischer algorithm — Wikipedia](https://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm)
- [Longest common subsequence — Wikipedia](https://en.wikipedia.org/wiki/Longest_common_subsequence)
- [Hirschberg's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Hirschberg%27s_algorithm)
- [Needleman–Wunsch algorithm — Wikipedia](https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm)
- [Diff — Wikipedia](https://en.wikipedia.org/wiki/Diff)
