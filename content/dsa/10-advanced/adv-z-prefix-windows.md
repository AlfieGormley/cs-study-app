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

Unlike the prefix function, which measures a border ending at a position, a Z-value measures a match starting there. The whole string's prefix is always the comparison target.

```
s:  a a b x a a b
z:  0 1 0 0 3 1 0
```

In the table, the value 3 at position 4 is because `aab` starting at 4 matches the prefix `aab`, then the suffix reaches the end of the string.

The algorithm keeps the rightmost window `[l, r)` known to match a prefix. For a new i inside that window, the character run from i mirrors the run from i − l, so it can reuse the earlier value, capped at the window's edge:

Reuse the mirrored Z-value only up to the known window's right edge. If it reaches that edge, compare further characters directly: the old window proves nothing about what lies beyond it.

For `aabxaab`: after position 4 the window runs from 4 up to 7, so position 5 mirrors position 1 and starts at 1. One more comparison (`a` against `b`) fails, so the value stays 1, with no wasted comparisons.

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
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
