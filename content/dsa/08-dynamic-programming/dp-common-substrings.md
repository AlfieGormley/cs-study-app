---
id: dp-common-substrings
title: Common subsequence versus common substring
level: intermediate
minutes: 2
summary: A substring must be unbroken, so a mismatch resets its matching run.
sourceLesson: dp-2d
---

A subsequence can skip characters, whereas a substring must form one uninterrupted run. That difference changes the state, the mismatch rule and the answer location.

### Subsequence vs substring

The **longest common substring** (one unbroken run of characters) is a different DP:

```formula
S[i][j] = S[i − 1][j − 1] + 1   if A_i = B_j
S[i][j] = 0   otherwise
answer = max of S[i][j] for all i, j
where
S[i][j]: the length of the longest common suffix (matching run that ends at both positions) of the first i characters of A and the first j characters of B
A_i, B_j: the ith character of A and the jth character of B, counting from 1
i, j: positive prefix lengths of A and B; an empty prefix has matching-run length zero
answer: the length of the longest common substring
max: the largest value
In words: a matching character extends the run that ended just before it in both strings; a mismatch breaks the run back to zero, and the best run can end anywhere.
```

The **0** on a mismatch is the difference from LCS, and it is why the answer is the maximum cell anywhere in the table, not the bottom-right.

## Key takeaways
- A substring must be unbroken, so a mismatch resets its matching run.
- The longest matching run can end at any table cell.

## Further reading
- [Longest common subsequence](https://en.wikipedia.org/wiki/Longest_common_subsequence)
- [Longest common substring](https://en.wikipedia.org/wiki/Longest_common_substring)
