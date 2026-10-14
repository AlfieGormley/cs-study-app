---
id: hash-pattern-unique-window
title: A sliding window without repeated characters
level: intermediate
minutes: 3
sourceLesson: hash-patterns
summary: The left boundary must move only forwards.
---

The left boundary must move only forwards. Last-seen positions let it skip directly past an offending character, but an occurrence already outside the window must be ignored.

## 5. Sliding window with a map

When the question is about a substring or subarray occupying adjacent sequence positions and a condition on its contents ("no repeats", "at most k distinct", "contains all of these"), move a window `[left, right]` along the input and keep a map describing what is inside it.

### Longest substring without repeating characters

Store each character's last index. When you meet a character already inside the window, jump the left edge past its previous occurrence.

```python
def longest_unique(s):
    last = {}  # char -> last index
    start = best = 0
    for i, ch in enumerate(s):
        # Ignore repeats outside the window.
        if last.get(ch, -1) >= start:
            start = last[ch] + 1
        last[ch] = i
        best = max(best, i - start + 1)
    return best

longest_unique("abcabcbb")  # 3 ("abc")
longest_unique("abba")      # 2
```

The `>= start` check matters. In `"abba"`, when the final `a` arrives, its last index (0) is to the left of the current window (which starts at 2, after the second `b`). Without the check, `start` would jump *backwards* to 1 and the answer would wrongly be 3.

## Trace a boundary that must not retreat

Read abba from left to right. The first a starts a one-character window, and b extends it to two. The second b has an earlier occurrence inside the current window, so the left boundary jumps past that occurrence. The valid window now contains only the newest b.

The final a was last seen before the current left boundary. That old occurrence is no longer in the window, so it creates no conflict. The guard prevents moving the boundary backwards to include both b characters again. After storing the new last-seen position, the best valid length remains two.

last records the latest position globally, not only characters in the current window. Keeping old positions is safe because the boundary check interprets them correctly. The answer records a length; returning the substring itself would require remembering the best pair of boundaries as well.

For a string of n code points, the loop visits each position once and performs expected constant-time map work per visit, giving expected O(n) time and O(n) extra space in the unrestricted alphabet case. Empty input returns zero. Repeated copies of one character give one. Python string indexing and iteration here concern Unicode code points, which need not equal user-perceived grapheme clusters.

## Key takeaways
- Only occurrences inside the current window move its left boundary.
- The left boundary must never retreat.
- A last-position map and one input pass give expected linear work.

## Further reading
- [Time complexity of Python operations — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [Hash table — Wikipedia](https://en.wikipedia.org/wiki/Hash_table)
