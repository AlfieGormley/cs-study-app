---
id: dp-lcs-reconstruction
title: Find and reconstruct common subsequences
level: intermediate
minutes: 4
summary: Matching ends extend the diagonal subsequence; mismatches drop one end.
sourceLesson: dp-2d
---

## Longest common subsequence

> The longest sequence of characters that appears, in order but not necessarily next to each other, in both strings.

The LCS of "ABCBDAB" and "BDCABA" has length four, for example "BCBA".

**State**: `L[i][j]` records LCS length of `A[:i]` and `B[:j]`.

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
i: the prefix length of A, 0 to m; the character-reading rules apply only when both prefixes are nonempty
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
            # Matching ends extend the LCS.
            if a[i - 1] == b[j - 1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i - 1][j],
                              L[i][j - 1])
    out, i, j = [], m, n
    while i and j:
        # Matching ends belong to the LCS.
        if a[i - 1] == b[j - 1]:
            # Collect matching characters
            # backwards.
            out.append(a[i - 1])
            i, j = i - 1, j - 1
        # Drop one unmatched end; ties go
        # upwards.
        elif L[i - 1][j] >= L[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return ''.join(reversed(out))
```

LCS and edit distance are cousins. If only insertions and deletions (indels) are allowed (no substitutions), every character not in the LCS must be deleted from A or inserted from B:

```formula
D_id = (m − ℓ) + (n − ℓ) = m + n − 2ℓ
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

The example compares "ABCB" with "BDCAB" from the table above, with LCS length 3.

## Key takeaways
- Matching ends extend the diagonal subsequence; mismatches drop one end.
- Trace back through the full table to recover characters in reverse order.
- Insert/delete-only distance is determined by the LCS length.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
- [Hirschberg’s algorithm](https://en.wikipedia.org/wiki/Hirschberg%27s_algorithm)
