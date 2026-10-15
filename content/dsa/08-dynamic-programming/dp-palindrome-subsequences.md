---
id: dp-palindrome-subsequences
title: Palindromes with gaps allowed
level: advanced
minutes: 2
summary: Matching ends contribute two characters around the inner answer.
sourceLesson: dp-interval-tree
---

A palindromic subsequence may skip input characters. Keep an interval state, but compare dropping either end when they cannot both join the palindrome.

### Longest palindromic subsequence

The characters need not be next to each other, so it's a classic interval DP:

```formula
L[i][j] = L[i + 1][j − 1] + 2
  if i < j and s_i = s_j
L[i][j] = max(L[i + 1][j], L[i][j − 1])
  if i < j and s_i ≠ s_j
L[i][i] = 1
where
L[i][j]: the length of the longest palindromic subsequence of the characters from position i to j of s
s_i, s_j: the characters at positions i and j of s
i, j: the first and last positions of the range
max: the larger of the two values
≠: not equal to
In words: matching ends both join the palindrome (adding 2) around the best answer for the inside; otherwise drop one end and keep the better result.
```

An empty range, whose left endpoint is past its right endpoint, counts as zero. For `"bbbab"` the answer is 4 (`"bbbb"`). Its length equals the LCS length of s and its reverse; an arbitrary reconstructed LCS need not itself be palindromic. For `"acbac"` and its reverse `"cabca"`, the maximum common-subsequence length is three. Both `"aba"` and `"abc"` are longest common subsequences, but only the first is a palindrome. The equality of optimal lengths does not make every reconstructed sequence valid.

## Key takeaways
- Matching ends contribute two characters around the inner answer.
- A mismatch drops one end and keeps the better subproblem.
- Empty ranges and single positions need distinct base cases.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Longest palindromic substring](https://en.wikipedia.org/wiki/Longest_palindromic_substring)
