---
id: sort-search-closed-invariant
title: Binary search from a closed invariant
level: intermediate
minutes: 4
sourceLesson: sort-binary-search
summary: Each probe shrinks the candidate range by roughly half.
---

Binary search is the payoff for sorting. Throughout this lesson, n is the number of elements in the sorted array, and costs use Big O notation (O(log n) grows with the base-2 logarithm of n: how many times n can be halved before reaching 1). In a sorted array of a billion items, it finds any key in at most 30 middle-element probes. The Python code may perform both equality and order tests per probe. The idea fits in a sentence: compare with the middle element and discard the half that cannot contain the answer.

And yet it is notoriously easy to get wrong. Jon Bentley reported that when he asked professional programmers to write it, around 90% of their versions had bugs. The fix is not to memorise a template, but to write every binary search from an explicit **invariant**.

## Why it is fast

Each probe halves the range of candidates. The search ends when one or zero candidates remain, so the number of probes is the number of times n can be halved before reaching 1:

```formula essential
r_k ≈ n / 2^k
r_k ≈ 1  when  k ≈ log_2(n)
where
r_k: how many elements are still in range after k probes
n: the number of elements in the sorted array
k: the number of probes taken so far
2^k: 2 multiplied by itself k times
log_2(n): the base-2 logarithm of n: how many halvings take n down to 1
≈: approximately equal to
In words: every probe halves what is left, so the number of probes grows with the logarithm of the array size: doubling the array adds only one probe.
```

| n | max comparisons |
|---|---|
| 1,000 | 10 |
| 1,000,000 | 20 |
| 1,000,000,000 | 30 |

Precisely, a successful search needs at most one probe per halving plus one for the last remaining element. The decision-tree argument from the lower-bound units in this module shows no comparison-based search can do better in the worst case.

> [!analogy] Real-world analogy: finding a word in a printed dictionary
> To find "otter" in a dictionary, open it near the middle. If the page shows words starting with "m", every page before it is ruled out, so you only ever look in the back half. Open the middle of that half, and so on. A thousand-page dictionary takes only about ten openings.
>
> **How it maps:** the pages still in play are the range `[lo, hi]`, opening the middle page is probing `mid`, and discarding the half that cannot contain the word is moving `lo` or `hi` past `mid`.
>
> **Where it stops:** people open a dictionary near where they expect the word ("o" is past the middle), which is interpolation search rather than binary search. And it only works because the dictionary is in alphabetical order; binary search on data that is not sorted by the same rule returns nonsense without any warning.

## Think in invariants

Write down what is true about `lo` and `hi` before every iteration, and make sure each update keeps it true. The loop condition and the return value then follow.

### Version 1: find any index of x (closed interval)

Here `a` is the sorted array, n its length, x the value we are looking for, and `lo` and `hi` the indices bounding the part of the array still in play.

**Invariant:** if x is in the array, it is in `a[lo..hi]` (inclusive).

```python
def search(a, x):
    lo, hi = 0, len(a) - 1
    while lo <= hi:      # range non-empty
        mid = (lo + hi) // 2
        # A matching midpoint ends this
        # search.
        if a[mid] == x:
            return mid
        # All keys through mid are too
        # small.
        if a[mid] < x:
            lo = mid + 1  # x right of mid
        else:
            hi = mid - 1  # x is left of mid
    return -1
```

Every choice follows from the invariant. The range `[lo, hi]` is empty when `lo > hi`, so loop while `lo <= hi`. When `a[mid] < x`, mid itself is ruled out, so `lo = mid + 1`, not `mid`.

## Key takeaways
- Each probe shrinks the candidate range by roughly half.
- Closed intervals require an inclusive loop and updates strictly beyond a rejected midpoint.

## Further reading
- [Insertion-bound searches — Python bisect](https://docs.python.org/3/library/bisect.html)
