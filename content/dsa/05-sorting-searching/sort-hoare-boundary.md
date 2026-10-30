---
id: sort-hoare-boundary
title: Hoare partition and recursion bounds
level: intermediate
minutes: 3
sourceLesson: sort-quicksort
summary: Hoare returns a split boundary, not the final pivot index.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Hoare partition

Hoare's original 1961 scheme uses two pointers moving towards each other, swapping pairs that are on the wrong side.

```python
def hoare(a, lo, hi):
    # A copied pivot value guides both
    # scans.
    pivot = a[(lo + hi) // 2]
    i, j = lo - 1, hi + 1
    while True:
        i += 1
        while a[i] < pivot:
            i += 1
        j -= 1
        while a[j] > pivot:
            j -= 1
        # Crossing returns a boundary, not a
        # pivot.
        if i >= j:
            return j
        a[i], a[j] = a[j], a[i]

def quicksort(a, lo, hi):
    if lo < hi:
        p = hoare(a, lo, hi)
        quicksort(a, lo, p)      # note: p
        quicksort(a, p + 1, hi)
```

Same input, pivot `a[3] = 6`:

```
swap a[0],a[7] [4,2,1,6,8,5,3,7]
swap a[3],a[6] [4,2,1,3,8,5,6,7]
swap a[4],a[5] [4,2,1,3,5,8,6,7]
pointers cross: return j 4
left [4,2,1,3,5]   right [8,6,7]
```

> [!analogy] Real-world analogy: two people tidying a shelf from both ends
> Two people stand at opposite ends of a bookshelf, agreeing that short books belong on the left and tall ones on the right, compared with one reference book. Each walks inwards until they find a book on the wrong side, then they swap those two books and carry on. When they meet, the shelf is split into a short side and a tall side.
>
> **How it maps:** the two people are the pointers `i` and `j`, the reference book's height is the pivot value, stopping at a misplaced book is the inner `while` loop ending, and the meeting point is the boundary Hoare returns.
>
> **Where it stops:** the reference book itself is not set aside in a special place; it can end up anywhere on its correct side. That is why Hoare's caller recurses on `[lo, p]` and `[p+1, hi]` rather than excluding a fixed pivot position.

Two differences matter:

- Under a uniformly random permutation of distinct keys, these classical schemes give Hoare roughly one-third of Lomuto's expected swaps; this is not a bound for every input.
- Hoare does **not** put the pivot in its final place. It only guarantees that everything in the left part is no bigger than the pivot and everything in the right part is no smaller. So the recursion is on `[lo, p]` and `[p+1, hi]`, not `p-1`. Using Lomuto bounds with Hoare can leave an unsorted boundary element out of recursion. Choosing `hi` as the pivot index in this Hoare variant can instead fail to shrink a partition and cause infinite recursion.

### Duplicates

On an array where every element is equal, Lomuto with `<` finds nothing smaller, so every partition is zero keys on one side and every non-pivot key on the other: **O(n²)**. Hoare's pointers stop on equal elements (`<` and `>` are strict), swap them, and meet in the middle: balanced splits, O(n log n). Stopping on equal keys looks wasteful but is exactly what saves it.

## Key takeaways
- Hoare returns a split boundary, not the final pivot index.
- Strict scans stop on equal keys and balanced duplicate splits avoid Lomuto’s all-equal degeneration.

## Further reading
- [Quicksort and partitioning — Princeton Algorithms](https://algs4.cs.princeton.edu/23quicksort/)
