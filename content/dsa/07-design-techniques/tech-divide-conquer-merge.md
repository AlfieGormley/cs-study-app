---
id: tech-divide-conquer-merge
title: Merge sort as divide and conquer
level: intermediate
minutes: 3
sourceLesson: tech-divide-conquer
summary: Two sorted halves can be merged in linear work per level.
---

For this unit n is the number of items being sorted. Merge sort is a concrete example of two independent half-size problems followed by linear combination.

### Merge sort

Split the list in half, sort each half, and merge the two sorted halves in linear time.

```python
def merge_sort(xs):
    if len(xs) <= 1:
        return xs
    mid = len(xs) // 2
    # Each copied half is sorted
    # independently.
    left = merge_sort(xs[:mid])
    right = merge_sort(xs[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        # Use the left equal key to retain
        # stability.
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    # Only one sorted remainder can be non-
    # empty.
    return out + left[i:] + right[j:]
```

```
level 0:  [ 8 3 5 1 ]          n work
level 1:  [ 8 3 ]  [ 5 1 ]     n work
level 2:  [8] [3]  [5] [1]     n work
          3 levels, all 4 items each
```

Each level does linear work in total (every item is merged once per level), and there are about log₂n + 1 levels. In master-theorem terms, two half-size calls balance a linear merge exactly: the "every level equal" case.

```formula reference
T(n) = 2T(n / 2) + Θ(n)
T(n) = Θ(n log(n))
where
T(n): the running time of merge sort on n items
n: the number of items to sort
Θ(n): work proportional to n, here the merge, which touches every item once
log: logarithm (the base only changes a constant)
Θ: Big-Theta, grows at exactly this rate up to constant factors
In words: two half-size sorts plus a linear merge cost the same on every level, and there are about log n levels, so the total grows like n log n.
```

For a million items, the linear-times-logarithm scale is roughly twenty million. This is neither an exact element-move count nor a timing; copied slices and concatenations also contribute work. The `<=` ensures a **stable sort** (equal keys stay in their original order). The price is O(n) extra memory for merging.

## Key takeaways
- Two sorted halves can be merged in linear work per level.
- Stable merging uses the left element on equal keys, and ordinary merging needs linear extra storage.

## Further reading
- [Recursive sorting — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
