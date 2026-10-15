---
id: pat-fixed-window
title: Maintain the sum of a fixed-size window
level: intermediate
minutes: 4
sourceLesson: pat-sliding-window
summary: A fixed window updates its sum by adding the entering value and subtracting the leaving value.
---

A sliding window is two pointers that bound a **contiguous range** `a[lo..hi]`. Instead of recomputing something about every subarray from scratch (an array of n elements has O(n²) subarrays, often with O(n) work each), you **update** the window's summary as the edges move: add the element entering on the right, remove the one leaving on the left.

It is a candidate when a problem says *subarray* or *substring* (consecutive) and asks for the longest, shortest, maximum or count of windows satisfying some condition.

```
 a:  3  1  4  1  5  9  2  6
        [lo ------ hi]
          window state:
          sum, counts, distinct...
```

The code uses random-access sequences. Arithmetic, equality and hashing costs are treated as constant; dictionary bounds are expected/amortised, not adversarial worst-case guarantees. Python string elements are Unicode code points, which need not be complete displayed characters.

## Fixed-size windows

**Problem.** Find the maximum sum of any `k` consecutive elements.

Brute force sums each window from scratch: about n windows of k elements each, so O(n × k) work, where n is the array length. But consecutive windows share all but one of their elements. Slide by adding the new element and subtracting the one that fell off:

```formula
S_r = S_{r−1} + a[r] − a[r − k]
S_3 = 8 + 1 − 2 = 7
where
S_r: the sum of the window that ends at index r (the k elements a[r − k + 1] to a[r])
S_{r−1}: the sum of the previous window, one step to the left
a[r]: the element entering the window on the right
a[r − k]: the element leaving the window on the left
r: the index of the window's right edge, counting from 0
k: the window size, a whole number from 1 to n
S_3: the sum of the window ending at index 3, [1, 5, 1]
n: the array length
In words: the new window's sum is the old sum plus what came in minus what fell out, two operations instead of k.
```

The worked line uses the example below: the window [2, 1, 5] sums to 8; sliding one step brings in `a[3]`, whose value is 1, and drops `a[0]`, whose value is 2. This only works because addition can be undone by subtraction; a window maximum can't be "un-added" like this (the monotonic stack and deque units handles that with a deque).

```python
def max_sum_k(a, k):
    if (type(k) is not int
            or not 1 <= k <= len(a)):
        raise ValueError("1 <= k <= len(a)")
    s = sum(a[i] for i in range(k))
    best = s
    for r in range(k, len(a)):
        # Add the entrant and subtract the
        # leaver.
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

Each slide costs a constant amount of work, so the whole scan is O(n) time, O(1) space. The same idea handles "average of every window", "count anagrams of `p` in `s`" (a window of length `len(p)` with a character count) and rolling hashes (Rabin–Karp).

## Counts that update with the window

For distinct values, keep a map from value to occurrence count. Increment the entrant, decrement the leaver and delete a key when its count becomes zero. The number of remaining keys is the current distinct count, read in constant time.

For anagrams, compare counts against the pattern’s required counts. Maintain how many character counts currently disagree: when one count changes, update that mismatch count from its old and new equality status. This avoids scanning the whole alphabet on every slide. Build the target counts once and update a bounded number of keys per slide, assuming expected constant-time hashing. Account for both source and pattern lengths in the total cost.

## Key takeaways
- A fixed window updates its sum by adding the entering value and subtracting the leaving value.
- Maintain counts and a constant-time mismatch counter for anagram windows.
- A median needs order information; a running total alone does not suffice.

## Further reading
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [String cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/string/)
- [Two pointers — USACO Guide](https://usaco.guide/silver/two-pointers)
