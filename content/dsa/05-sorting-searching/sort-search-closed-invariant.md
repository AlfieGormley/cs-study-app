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

Each step halves the range. The search ends when one or zero elements remain, so the question is how many halvings that takes:

```formula
r_k ≈ n / 2^k
n / 2^k = 1  ⇒  k = log_2(n)
log_2(10^9) ≈ 29.9
where
r_k: how many elements are still in range after k steps
n: the number of elements in the sorted array; a billion (10^9) in the last line
k: the number of steps (probes) taken so far
2^k: k copies of 2 multiplied together
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n, which is how many halvings take n down to 1
⇒: "which happens when"
≈: approximately equal to
In words: halving a billion items about 30 times leaves one, so binary search needs about 30 probes.
```

| n | max comparisons |
|---|---|
| 1,000 | 10 |
| 1,000,000 | 20 |
| 1,000,000,000 | 30 |

Exactly:

```formula
c_max = ⌊log_2(n)⌋ + 1
c_max = ⌊log_2(1000)⌋ + 1 = 9 + 1 = 10
where
c_max: the most three-way comparisons (less, equal or greater) a successful search can need
n: the number of elements; here 1,000
log_2(n): the base-2 logarithm of n; log_2(1000) ≈ 9.97
⌊ ⌋: the floor: round down to a whole number
In words: binary search over n elements never needs more than one probe per halving plus one, which is 10 for a thousand elements and 30 for a billion.
```

That is where the table comes from. The decision-tree argument from the relevant unit in this module shows no comparison-based search can do better in the worst case.

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
