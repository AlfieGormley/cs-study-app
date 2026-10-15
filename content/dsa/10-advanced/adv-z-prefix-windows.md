---
id: adv-z-prefix-windows
title: Reusing prefix matches with the Z-function
level: advanced
minutes: 3
summary: A Z-value measures agreement with the whole string prefix.
sourceLesson: adv-string-algorithms
---

Here n is the text or indexed-string length, m is the pattern length, and positions count from zero. Costs count constant-time character and word operations unless noted.

## The Z-function

`z[i]` is the length of the longest substring starting at i that is also a **prefix** of the whole string. By convention `z[0] = 0`.

```formula
z[i] = max L   such that 0 ≤ L ≤ n − i
  s[0..L−1] = s[i..i+L−1]
z[4] = 3   as s[0..2] = "aab" = s[4..6]
where
s: the string, with characters numbered from 0
n: the length of s
i: a position in s, from 1 to n − 1
z[i]: the Z-value at position i, a whole number of characters
L: a candidate match length
max: the largest value that satisfies the condition
s[a..b]: the characters of s from position a to position b, both included
In words: z[i] counts how many characters, starting at i, agree with the start of the string.
```

```
s:  a a b x a a b
z:  0 1 0 0 3 1 0
```

In the table, the value 3 at position 4 is because `aab` starting at 4 matches the prefix `aab`, then the suffix reaches the end of the string.

The algorithm keeps the rightmost window `[l, r)` known to match a prefix. For a new i inside that window, the character run from i mirrors the run from i − l, so it can reuse the earlier value, capped at the window's edge:

```formula
z[i] ≥ min(r − i, z[i − l])   if i < r
z[5] ≥ min(7 − 5, z[1]) = min(2, 1) = 1
where
i: the position being computed
l, r: the start (included) and end (excluded) of the rightmost known window, so s[l..r−1] equals s[0..r−l−1]
z[i]: the Z-value at position i
z[i − l]: the Z-value at the mirrored position inside the prefix, already computed
min: the smaller of the two values
≥: is at least
In words: inside a known matching window, position i agrees with the prefix at least as far as its mirror image did, but no further than the window's edge without checking.
```

The last line is the worked example for `aabxaab`: after position 4 the window runs from 4 up to 7, so position 5 mirrors position 1 and starts at 1. One more comparison (`a` against `b`) fails, so the value stays 1, with no wasted comparisons.

```python
def z_function(s):
    n = len(s)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i < r:
            # Reuse only the known matching
            # window.
            z[i] = min(r - i, z[i - l])
        while (i + z[i] < n
               and s[z[i]] == s[i + z[i]]):
            z[i] += 1
        if i + z[i] > r:
            # Keep the furthest verified
            # right edge.
            l, r = i, i + z[i]
    return z
```

Each successful comparison in the inner loop pushes r to the right, and r never moves left, so the total work is O(n), where n is the length of s.

To search, compute z of `p + "$" + t`, choosing `$` absent from both strings: every position with `z[i] == m` is a match. The Z-function is often the simplest tool for "which suffixes match a prefix?" questions, such as finding a string's period.

## Key takeaways

- A Z-value measures agreement with the whole string prefix.
- Reuse an earlier mirrored Z-value only within the already-known matching window.

## Further reading
- [Prefix function and Knuth–Morris–Pratt — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Rabin–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
- [Suffix Array — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix array — Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
