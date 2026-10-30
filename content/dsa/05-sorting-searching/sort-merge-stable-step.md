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

Each comparison outputs one element, and once one list runs out the rest of the other is copied with no comparisons at all. So a merge of two nonempty lists needs **at most one comparison fewer than the total number of elements** (the last element is always copied for free), and **at least as many as the shorter list has elements** (when the shorter list's elements all come first). Either way the cost is linear in the total length.

```
left  [2, 5, 9]     right [3, 4, 10]
2 vs 3 -> 2        out [2]
5 vs 3 -> 3        out [2, 3]
5 vs 4 -> 4        out [2, 3, 4]
5 vs 10 -> 5       out [2, 3, 4, 5]
9 vs 10 -> 9       out [2, 3, 4, 5, 9]
left empty: append [10]
```

Five comparisons for six elements: one fewer than the total, the maximum.

> [!analogy] Real-world analogy: two sorted piles of marked exam scripts
> Two markers each hand you a pile of scripts already sorted by score, lowest on top. You build one sorted pile by repeatedly comparing the two top scripts and taking the lower one. When one pile runs out, you put the rest of the other pile on without looking. On a tie, you always take from the first marker's pile.
>
> **How it maps:** each pile is a sorted half, comparing the two top scripts is one comparison, moving the leftover pile is the free tail copy, and the "first marker wins ties" rule is the `<=` test that keeps equal keys in their original order.
>
> **Where it stops:** on a desk the new pile just grows beside the old ones. An array merge needs a separate output buffer as large as the two halves, which is the main extra memory merge sort needs.

### Why `<=` makes it stable

When the two front elements are equal, we take the one from the **left** half. Everything in the left half came earlier in the original array, so equal keys keep their original order. Write `<` instead and equal elements from the right half jump ahead: the sort is no longer stable. One character decides it.

## Key takeaways
- Each comparison consumes one front element.
- Taking ties from the left keeps earlier equal-key records first.

## Further reading
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
