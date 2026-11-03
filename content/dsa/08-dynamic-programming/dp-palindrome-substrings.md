---
id: dp-palindrome-substrings
title: Count contiguous palindromes
level: advanced
minutes: 3
summary: Matching ends enclose a smaller palindrome.
sourceLesson: dp-interval-tree
---

A palindrome reads the same forwards and backwards. First require an unbroken range; the next unit will allow gaps between retained characters.

### Counting palindromic substrings

`P[i][j]` records True if `s[i..j]` (characters i to j inclusive) is a palindrome, a string that reads the same backwards. It is exactly when the ends match and the inside `s[i+1..j-1]` is a palindrome, or there is no inside (the range has one or two characters):

```python
def count_palindromes(s):
    n = len(s)
    P = [[False] * n for _ in range(n)]
    count = 0
    # Larger starting indices are ready
    # first.
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            # Singletons and pairs need no
            # inner read.
            inner = j - i < 2 or P[i+1][j-1]
            if s[i] == s[j] and inner:
                P[i][j] = True
                # Count this occurrence,
                # including repeats.
                count += 1
    return count
```

`"aaa"` has 6 (three `a`s, two `aa`s, one `aaa`); `"abc"` has 3; `"racecar"` has 10. For a string of n characters this is O(n²) time and space.

Note the loop order: `i` descending, `j` ascending, because `P[i][j]` reads `P[i+1][j-1]` (next row down). Looping by length works too. Looping `i` upwards is a silent bug: the inner cell hasn't been filled yet, still reads False, and every palindrome longer than two characters is missed.

**Expand around centre** gets the same O(n²) time in O(1) space. A palindrome is centred either on a character (odd length) or on the gap between two characters (even length), so a string of n characters has 2n − 1 possible centres. For each one, grow outwards while the ends match. **Manacher's algorithm** computes a compact array of palindrome radii in O(n), reusing mirror information. That suffices to find a longest palindrome or count occurrences; explicitly listing all occurrences can require Θ(n²) output.

## Key takeaways
- Matching ends enclose a smaller palindrome.
- Single characters and matching pairs are base cases.
- Compact palindrome radii can be linear-sized even when occurrences are quadratic.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Longest palindromic substring](https://en.wikipedia.org/wiki/Longest_palindromic_substring)
