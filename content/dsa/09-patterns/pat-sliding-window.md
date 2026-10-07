---
id: pat-sliding-window
title: Sliding window
level: intermediate
minutes: 13
summary: Maintaining a contiguous window incrementally instead of recomputing it, with fixed and variable windows, longest substring without repeats, minimum window substring and the at-most-k counting trick.
---

A sliding window is two pointers that bound a **contiguous** range `a[lo..hi]`. Instead of recomputing something about every subarray from scratch (O(n²) subarrays, often O(n) work each), you **update** the window's summary as the edges move: add the element entering on the right, remove the one leaving on the left.

It is a candidate when a problem says *subarray* or *substring* (contiguous) and asks for the longest, shortest, maximum or count of windows satisfying some condition.

```
 a:  3  1  4  1  5  9  2  6
        [lo ------ hi]
          window state:
          sum, counts, distinct...
```

The code uses random-access sequences. Arithmetic, equality and hashing costs are treated as constant; dictionary bounds are expected/amortised, not adversarial worst-case guarantees. Python string elements are Unicode code points, which need not be complete displayed characters.

## Fixed-size windows

**Problem.** Find the maximum sum of any `k` consecutive elements.

Brute force sums each window: O(nk). But consecutive windows share k − 1 elements. Slide by adding the new element and subtracting the one that fell off.

```python
def max_sum_k(a, k):
    if (type(k) is not int
            or not 1 <= k <= len(a)):
        raise ValueError("1 <= k <= len(a)")
    s = sum(a[i] for i in range(k))
    best = s
    for r in range(k, len(a)):
        s += a[r] - a[r - k]
        best = max(best, s)
    return best
```

For `a = [2, 1, 5, 1, 3, 2]`, `k = 3`:

```
window      sum
[2,1,5]     8
[1,5,1]     8 - 2 + 1 = 7
[5,1,3]     7 - 1 + 3 = 9   best
[1,3,2]     9 - 5 + 2 = 6
```

O(n) time, O(1) space. The same idea handles "average of every window", "count anagrams of `p` in `s`" (a window of length `len(p)` with a character count) and rolling hashes (Rabin–Karp).

## Variable-size windows

Here the window grows and shrinks. The template:

```python
lo = 0
for hi in range(len(a)):
    add(a[hi])                 # grow right
    while not valid():
        remove(a[lo])          # shrink left
        lo += 1
    record(hi - lo + 1)    # valid now
```

If the empty window is valid and add/remove/valid/record each cost O(1), both pointers only move forwards, so each element is added once and removed at most once: **O(n) total**, even with the inner `while`. That amortised argument is the reason the pattern is fast.

> [!warning] The precondition: monotonicity
> These variable-window templates need **monotonic** validity: every subwindow of a valid window stays valid for the longest/shrink-when-invalid template; every superwindow of a valid window stays valid for the shortest/shrink-while-valid template. Merely being able to make some invalid window valid by growing is insufficient. "Sum ≤ k with non-negative numbers and k ≥ 0" qualifies. With **negative numbers**, removing an element can *increase* the sum, so the window can't tell which way to move. Use prefix sums instead (lesson 4).

## Longest substring without repeating characters

**Problem.** Return the length of the longest substring of `s` with all distinct characters.

Window condition: no character appears twice. When `s[hi]` is already in the window, move `lo` just past its previous occurrence. Storing each character's last index lets `lo` jump instead of stepping.

```python
def longest_unique(s):
    last = {}       # char -> last index
    lo = best = 0
    for hi, ch in enumerate(s):
        if last.get(ch, -1) >= lo:
            lo = last[ch] + 1
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

Answer 3. O(n) time; O(min(n, alphabet)) space.

> [!example] Why `>= lo` matters
> For `"abba"`: at the final `a`, `last['a'] = 0`, but `lo` is already 2 (moved by the second `b`). The old `a` is *outside* the window, so `lo` must not move backwards to 1. Without the `>= lo` check, the code returns 3 instead of 2.

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
        need[ch] -= 1
        while missing == 0:      # valid
            if hi - lo < best[1] - best[0]:
                best = (lo, hi)
            left = s[lo]
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

Each character enters and leaves once: Expected O(|s| + |t|) time, O(alphabet) auxiliary space plus the returned substring. The `missing` counter is what keeps the validity check O(1); comparing two full count maps each step would cost O(alphabet) per move.

## Counting windows: the at-most trick

"Count subarrays with **exactly** k distinct values" is awkward for a window: removing an element can keep the count at k or drop it, so there's no single clean shrink rule. But "**at most** k" is monotonic. For each `hi`, after shrinking, every window ending at `hi` and starting anywhere in `[lo, hi]` qualifies: that's `hi - lo + 1` windows.

```python
def at_most(a, k):
    if type(k) is not int:
        raise ValueError("integer k")
    if k < 0:
        return 0
    count = {}
    lo = total = 0
    for hi, x in enumerate(a):
        count[x] = count.get(x, 0) + 1
        while len(count) > k:
            count[a[lo]] -= 1
            if count[a[lo]] == 0:
                del count[a[lo]]
            lo += 1
        total += hi - lo + 1
    return total

def exactly(a, k):
    return at_most(a, k) - at_most(a, k - 1)
```

These functions count nonempty subarrays; a negative distinct budget gives 0, and `exactly(a, 0)` gives 0. Values must be hashable.

For `[1, 2, 1, 2, 3]` with k = 2, `at_most(2) = 12` and `at_most(1) = 5`, so exactly 7 subarrays have exactly two distinct values.

## Recognising the pattern

| Cue | Window type |
|---|---|
| "every k consecutive" | Fixed |
| "longest ... such that" | Variable, shrink when invalid |
| "shortest ... containing" | Variable, shrink while valid |
| "count subarrays at most k" | Variable, add `hi-lo+1` |
| "exactly k" | at_most(k) − at_most(k−1) |
| Max/min of each window | Monotonic deque (lesson 5) |
| Sum = k, negatives allowed | Not a window: prefix sums |

## Pitfalls

- **Non-contiguous problems.** "Subsequence" means elements need not be adjacent; a contiguous window alone does not enumerate arbitrary subsequences. DP, greedy or other methods may apply.
- **Negative numbers** break sum-based windows, as above.
- **Recording at the wrong time.** For "longest", record after shrinking (window valid). For "shortest", record *inside* the shrink loop before removing.
- **Expensive validity checks.** Keep a counter (`missing`, `len(count)`) so each check is O(1).
- **Stale map entries.** Delete keys whose count hits 0, or `len(count)` overstates the distinct count.

## Key takeaways
- A sliding window maintains a contiguous range's summary incrementally, turning O(n²) or O(nk) into O(n).
- Each element enters and leaves the window at most once, so the inner `while` doesn't make it quadratic.
- Variable windows need monotonic validity; negative numbers usually break sum conditions.
- "Longest" shrinks until valid then records; "shortest" records while shrinking a valid window.
- Count "exactly k" as at_most(k) − at_most(k − 1).

## Further reading
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [String cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/string/)
- [Two pointers — USACO Guide](https://usaco.guide/silver/two-pointers)
