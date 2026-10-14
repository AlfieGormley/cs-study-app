---
id: sort-merge-stable-step
title: Merging sorted lists stably
level: basic
minutes: 3
sourceLesson: sort-merge
summary: Each comparison consumes one front element.
---

The simple sorts are slow because each step makes only a tiny amount of progress: one adjacent swap removes one inversion. Merge sort makes progress in bulk by using **divide and conquer**:

1. **Divide** the array into two halves.
2. **Conquer**: sort each half recursively.
3. **Combine**: merge the two sorted halves into one sorted array.

The magic is that step 3 is cheap. Merging two sorted lists takes linear time, and that is enough to get O(n log n) overall, guaranteed, on every input. Here n is the number of elements, O(...) is Big O notation (how cost grows with n, ignoring constant factors) and the logarithm notation in each card is base two: how many times n can be halved before reaching 1, about 20 for a million.

## The merge step

Picture two sorted piles of cards face up. Repeatedly take the smaller of the two top cards. When one pile empties, append the rest of the other.

```python
def merge(left, right):
    out = []
    # Each cursor tracks an unconsumed head.
    i = j = 0
    while i < len(left) and j < len(right):
        # Take left on ties to retain input
        # order.
        if left[i] <= right[j]:  # stable
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    # Append the tail with no comparisons.
    out.extend(left[i:])
    out.extend(right[j:])
    return out
```

Each comparison outputs one element, and once one list runs out the rest of the other is copied with no comparisons at all. That gives the cost of a merge:

```formula
C_max = a + b − 1
C_min = min(a, b)
C_max = 3 + 3 − 1 = 5
where
C_max: the most comparisons a merge can need, when both lists are nonempty (it is zero if either is empty)
C_min: the fewest comparisons, reached when every element of the shorter list is smaller than every element of the longer one
a: the number of elements in the left list; here 3
b: the number of elements in the right list; here 3
min: the smaller of its two inputs
In words: a merge never needs more comparisons than one fewer than the total number of elements, and never fewer than the length of the shorter list.
```

```
left  [2, 5, 9]     right [3, 4, 10]
2 vs 3 -> 2        out [2]
5 vs 3 -> 3        out [2, 3]
5 vs 4 -> 4        out [2, 3, 4]
5 vs 10 -> 5       out [2, 3, 4, 5]
9 vs 10 -> 9       out [2, 3, 4, 5, 9]
left empty: append [10]
```

Five comparisons for six elements: 3 + 3 − 1, the maximum.

### Why `<=` makes it stable

When the two front elements are equal, we take the one from the **left** half. Everything in the left half came earlier in the original array, so equal keys keep their original order. Write `<` instead and equal elements from the right half jump ahead: the sort is no longer stable. One character decides it.

## Key takeaways
- Each comparison consumes one front element.
- Taking ties from the left keeps earlier equal-key records first.

## Further reading
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
