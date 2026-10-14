---
id: sort-search-rotated-halves
title: Searching rotated arrays
level: intermediate
minutes: 2
sourceLesson: sort-binary-search
summary: With distinct keys, at least one midpoint half is sorted.
---

This unit builds on the preceding search units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Searching a rotated sorted array

A sorted array rotated at an unknown point, like `[15, 18, 22, 3, 6, 9, 12]`, is not sorted, but **at least one half around any mid is sorted**. Check which half is sorted and whether x lies inside its range.

```python
def search_rotated(a, x):  # distinct keys
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        # A matching midpoint ends this
        # search.
        if a[mid] == x:
            return mid
        # Distinct keys reveal a sorted
        # half.
        if a[lo] <= a[mid]:  # left sorted
            if a[lo] <= x < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:  # right half sorted
            if a[mid] < x <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```

This is still O(log n), but only for **distinct** keys. With duplicates, `[2, 2, 2, 3, 2]` makes it impossible to tell which half is sorted when `a[lo] == a[mid] == a[hi]`, and the worst case becomes O(n).

The same idea finds the **rotation point** (the minimum): if `a[mid] > a[hi]`, the drop is to the right of mid; otherwise it is at mid or to its left.

## Key takeaways
- With distinct keys, at least one midpoint half is sorted.
- Equal endpoints can hide the rotation and force linear worst-case work.

## Further reading
- [Insertion-bound searches — Python bisect](https://docs.python.org/3/library/bisect.html)
