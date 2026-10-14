---
id: hash-pattern-distinct-window
title: A sliding window with at most k distinct keys
level: intermediate
minutes: 3
sourceLesson: hash-patterns
summary: The count map describes only the current window.
---

The count map describes only the current window. Removing a zero-count key is part of maintaining that description, not merely a memory optimisation.

## Counting keys inside a sliding window

### Longest substring with at most k distinct characters

Here the map holds counts of characters in the window, and its size is the number of distinct characters.

```python
def longest_k_distinct(s, k):
    if type(k) is not int or k < 0:
        raise ValueError("nonnegative k")
    counts = {}
    left = best = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        while len(counts) > k:
            out = s[left]
            counts[out] -= 1
            if counts[out] == 0:
                # No copies remain in the
                # window.
                del counts[out]
            left += 1
        best = max(best, right - left + 1)
    return best

longest_k_distinct("eceba", 2)  # 3 ("ece")
```

Deleting keys whose count hits zero is essential: otherwise `len(counts)` overstates the number of distinct characters. Each character enters and leaves the window at most once, so for a string of n characters the inner `while` loop does O(n) work in total, not per step. Total: O(n).

The same skeleton solves "minimum window containing all characters of t" (track how many required characters are satisfied) and "find all anagrams of p in s" (a fixed-size window compared with `Counter(p)`).

## Why the nested loop is linear overall

Imagine the right boundary walking along aabbcc with a limit of two distinct characters. The map initially counts a, then a and b. When the first c arrives, it records three distinct keys and the left boundary must advance until a disappears entirely. Removing only one a is insufficient: its second copy still belongs to the window. The key is removed only after its count becomes zero.

The left boundary never moves backwards. Although one right-boundary step can trigger several iterations of the while loop, every such iteration consumes a different earlier input position. Across the whole input there are no more left-boundary advances than characters. This is an amortised argument about loop work, separate from the expected cost of each hash-map operation.

A zero limit permits only an empty window, so every new character is removed before best is updated and the result is zero. A negative limit or a non-integer is rejected explicitly. With a limit at least as large as the input’s number of distinct characters, the whole string is valid.

For n input characters, expected time is O(n). The count map stores only keys inside the current valid window, apart from the brief violation before shrinking. Zero-count deletion makes the map size a correct distinct-key count. Returning the substring would also require storing the best boundaries rather than only its length.

## Key takeaways
- The count map must describe characters currently in the window.
- Delete zero-count keys before using map size as the distinct count.
- The nested shrinking loop is linear overall because the left boundary only advances.

## Further reading
- [Time complexity of Python operations — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [Hash table — Wikipedia](https://en.wikipedia.org/wiki/Hash_table)
