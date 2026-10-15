---
id: pat-covering-substring
title: Shrink a covering substring to its minimum
level: intermediate
minutes: 3
sourceLesson: pat-sliding-window
summary: A counter records missing occurrences, including repeated target characters.
---

Find the shortest contiguous substring covering every target occurrence. Hashing and character comparisons are assumed constant-cost, and each Python character is a code point.

## Minimum window substring

**Problem.** Given `s` and `t`, find the shortest substring of `s` containing every character of `t` (with multiplicity). For `s = "ADOBECODEBANC"`, `t = "ABC"`, the answer is `"BANC"`. An empty target has answer `""`; when no covering substring exists the answer is also `""`.

This is a "shortest" problem: grow until the window is valid, then shrink while it *stays* valid, recording the best.

Keep `need[c]`: how many more of `c` the window still needs (negative means surplus), and `missing`: the total number of required characters not yet covered.

```python
from collections import Counter

def min_window(s, t):
    if not t:
        return ""
    need = Counter(t)
    missing = len(t)
    lo = 0
    best = (0, float("inf"))
    for hi, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        # Negative counts represent surplus
        # copies.
        need[ch] -= 1
        # Measure each covering window
        # before drop.
        while missing == 0:      # valid
            if hi - lo < best[1] - best[0]:
                best = (lo, hi)
            left = s[lo]
            # Put the departing occurrence
            # back in need.
            need[left] += 1
            if need[left] > 0:   # now short
                missing += 1
            lo += 1
    a, b = best
    if b == float("inf"):
        return ""
    return s[a:b + 1]
```

How it plays out on the example:

```
hi=5  window ADOBEC     valid, len 6
      shrink: drop A -> invalid
hi=10 window DOBECODEBA valid again
      shrink to CODEBA (len 6)
hi=12 add C: window ...BANC
      shrink to BANC     len 4  best
```

Each character enters and leaves once. Writing |s| for the length of `s` and |t| for the length of `t`, that gives expected O(|s| + |t|) time, O(alphabet) auxiliary space plus the returned substring. The `missing` counter is what keeps the validity check O(1); comparing two full count maps each step would cost O(alphabet) per move.

## Key takeaways
- A counter records missing occurrences, including repeated target characters.
- Record a covering candidate before removing its leftmost character.
- An empty target or absence of a covering substring returns the empty string.

## Further reading
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [String cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/string/)
- [Two pointers — USACO Guide](https://usaco.guide/silver/two-pointers)
