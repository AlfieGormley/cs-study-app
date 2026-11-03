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

For `horse` → `ros`, the first nonempty prefixes are "h" and "r". They differ, so the cell takes one edit plus the cheapest neighbour: deleting or inserting would leave a distance of 1 to fix, while substituting h → r leaves the empty pair at 0. So that cell is 1.

> [!analogy] Real-world analogy: fixing a typo with the fewest keystrokes
> You typed "horse" but meant "ros". With a keyboard you can delete a character, type a missing one, or overtype one character with another, and you want the fewest keystrokes.
>
> **How it maps:** deleting is a deletion, typing a missing letter is an insertion and overtyping is a substitution, each costing 1. The edit distance is the smallest keystroke count. The table records the best count for every pair of "first i letters typed" and "first j letters wanted", so each correction builds on smaller ones.
>
> **Where it stops:** on a real keyboard, moving the cursor, selecting a word or pasting also costs effort or saves it. Levenshtein distance ignores position entirely and charges exactly 1 for each single-character edit, wherever it happens.

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

**Complexity**: for strings of lengths m and n, the table has a cell for every pair of prefix lengths, and each cell takes a fixed amount of work: O(mn) time and, for the full table, O(mn) slots. Two 1,000-character strings need about 1,000,000 cells. If you only need the distance, keeping two rows cuts the memory to the shorter length (a later unit shows how).

> [!note] Why "matching characters → take the diagonal" is safe
> When the last characters match, there's always an optimal alignment that pairs them. You might worry that deleting or inserting could be better, but any such solution can be rearranged into one that pairs the matching ends at no extra cost. Many implementations still take `min` over all three for safety; it gives the same answer.

## Check basic distance bounds

Three sanity checks catch many table bugs. The distance is the same in both directions, because every edit can be reversed. It is at least the difference in lengths, because only insertions and deletions change the length. And it is at most the longer length, because you can always substitute along the shorter string and then insert or delete the rest.

```formula reference
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
In words: the distance is symmetric, is at least the difference in lengths, and is at most the longer length.
```

These bounds permit substitutions. The separate LCS identity later applies only when substitutions are forbidden.

## Key takeaways
- The table compares pairs of prefix lengths.
- Matching ends cost nothing; otherwise try insertion, deletion and substitution.
- Empty-prefix costs provide the first row and column.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
