---
id: dp-edit-distance-table
title: Build an edit-distance table
level: intermediate
minutes: 5
summary: The table compares pairs of prefix lengths.
sourceLesson: dp-2d
---

## Edit distance (Levenshtein)

> The minimum number of unit-cost insertions, deletions and substitutions to turn A into B. Python strings are sequences of Unicode code points here; user-perceived characters may contain several code points.

`kitten` → `sitting` is 3: substitute k→s, substitute e→i, insert g.

**State**: `D[i][j]` records edit distance between `A[:i]` and `B[:j]`.

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
i: how many characters of A are in the prefix, 0 to m; character-reading recurrence lines require both prefixes to be nonempty
j: how many characters of B are in the prefix, 0 to n
m: the length of A
n: the length of B
min: the smallest of the three values
In words: if the last characters match, keep them for free; otherwise pay one edit for whichever of delete, insert or substitute leaves the cheapest smaller problem.
```

For `horse` → `ros`, the first nonempty prefixes have different letters, h and r:

```formula
D[1][1] = 1 + min(1, 1, 0) = 1
where
D[i][j]: the edit distance between the first i letters of "horse" and first j letters of "ros"
i, j: prefix lengths
min: the smallest candidate
In words: Substituting the first letter is cheaper than inserting or deleting it.
```

```python
def edit_distance(a, b):
    m, n = len(a), len(b)
    D = [[0] * (n+1) for _ in range(m+1)]
    for i in range(m + 1):
        # Turning this prefix into empty
        # deletes it.
        D[i][0] = i
    for j in range(n + 1):
        # Building this prefix from empty
        # inserts it.
        D[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # Matching final characters cost
            # no edit.
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
T = O((m + 1) × (n + 1)) = O(mn)
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

## Check basic distance bounds

Useful sanity checks follow directly from reversible edits, required length changes, and substituting the shared-length portion:

```formula
D(A, B) = D(B, A)
|m − n| ≤ D(A, B) ≤ max(m, n)
D(A, A) = 0
where
D(A, B): the unit-cost Levenshtein distance between strings A and B
A, B: the input strings
m, n: their lengths in code points
|m − n|: the absolute difference between the lengths
max: the larger input length
≤: less than or equal to
In words: Distance is symmetric, needs enough insertions or deletions to fix the length, and never exceeds substituting a common-length portion plus the remaining insertions or deletions.
```

These bounds permit substitutions. The separate LCS identity later applies only when substitutions are forbidden.

## Key takeaways
- The table compares pairs of prefix lengths.
- Matching ends cost nothing; otherwise try insertion, deletion and substitution.
- Empty-prefix costs provide the first row and column.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
