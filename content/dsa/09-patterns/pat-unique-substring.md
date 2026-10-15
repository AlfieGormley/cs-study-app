---
id: pat-unique-substring
title: Jump past an in-window duplicate
level: intermediate
minutes: 2
sourceLesson: pat-sliding-window
summary: Store each character’s last position to jump past a duplicate.
---

The earlier variable-window rule now tracks unique characters. Here n is the string length measured in Python code points; dictionary operations use the expected constant-cost hash model.

## Longest substring without repeating characters

**Problem.** Return the length of the longest substring of `s` with all distinct characters.

Window condition: no character appears twice. When `s[hi]` is already in the window, move `lo` just past its previous occurrence. Storing each character's last index lets `lo` jump instead of stepping.

```python
def longest_unique(s):
    last = {}       # char -> last index
    lo = best = 0
    for hi, ch in enumerate(s):
        if last.get(ch, -1) >= lo:
            # Jump beyond the duplicate
            # inside window.
            lo = last[ch] + 1
        # Remember the newest occurrence.
        last[ch] = hi
        best = max(best, hi - lo + 1)
    return best
```

Trace for `"abcabcbb"`:

```
hi ch  last[ch]  lo  window  best
0  a   -         0   a       1
1  b   -         0   ab      2
2  c   -         0   abc     3
3  a   0         1   bca     3
4  b   1         2   cab     3
5  c   2         3   abc     3
6  b   4         5   cb      3
7  b   6         7   b       3
```

Answer 3. O(n) time; O(min(n, alphabet)) space, where n is the length of `s`, alphabet is the number of different characters that can occur, and min picks the smaller of the two: the map never holds more keys than either.

> [!example] Why `>= lo` matters
> For `"abba"`: at the final `a`, `last['a'] = 0`, but `lo` is already 2 (moved by the second `b`). The old `a` is *outside* the window, so `lo` may never move backwards to 1. Without the `>= lo` check, the code returns 3 instead of 2.

## Key takeaways
- Store each character’s last position to jump past a duplicate.
- Ignore occurrences before the left edge so the edge never moves backwards.
- Python strings are scanned by code point, which can differ from displayed characters.

## Further reading
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [String cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/string/)
- [Two pointers — USACO Guide](https://usaco.guide/silver/two-pointers)
