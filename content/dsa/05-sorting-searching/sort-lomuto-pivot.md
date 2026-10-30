---
id: sort-lomuto-pivot
title: Lomuto partition and pivot placement
level: intermediate
minutes: 3
sourceLesson: sort-quicksort
summary: Lomuto finishes by placing the pivot at its sorted index.
---

Merge sort does its work on the way **up**: split blindly, then merge carefully. Quicksort does the opposite. It works on the way **down**: partition carefully, then the two halves need no combining at all.

1. Pick a **pivot** element.
2. **Partition**: rearrange the array so everything smaller than the pivot comes before everything larger.
3. Recursively sort the two sides. Done; there is no merge step.

Throughout this lesson, n is the number of elements being sorted, and costs use Big O notation (O, Θ and Ω: at most, exactly and at least this growth rate, ignoring constant factors). Quadratic means growing with n², the input size squared.

Quicksort is in-place, has tiny inner loops and accesses memory sequentially, which can make it fast on arrays; the fastest choice depends on data, comparator and implementation. Its weakness is that a bad pivot makes the split lopsided, and a run of bad pivots makes it quadratic. Most of the engineering around quicksort is about avoiding that.

## Lomuto partition

The simpler scheme, popularised by Programming Pearls and CLRS. Use the last element as the pivot. Keep a boundary `i`: everything left of `i` is smaller than the pivot.

```python
def lomuto(a, lo, hi):
    # This scheme uses the last item as
    # pivot.
    pivot = a[hi]
    i = lo
    # Grow a prefix of keys below the pivot.
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    # Place the pivot at its final index.
    a[i], a[hi] = a[hi], a[i]
    return i   # pivot's final index

def quicksort(a, lo, hi):
    if lo < hi:
        # Partition before choosing the next
        # range.
        p = lomuto(a, lo, hi)
        quicksort(a, lo, p - 1)
        quicksort(a, p + 1, hi)
```

Trace on `[7, 2, 1, 6, 8, 5, 3, 4]`, pivot 4:

```
j 1: 2<4 swap a[0],a[1] [2,7,1,6,8,5,3,4]
j 2: 1<4 swap a[1],a[2] [2,1,7,6,8,5,3,4]
j 6: 3<4 swap a[2],a[6] [2,1,3,6,8,5,7,4]
end: swap a[3],a[7]     [2,1,3,4,8,5,7,6]
                               ^ pivot at 3
```

After partitioning, the pivot is in its **final sorted position**. Recursion handles `[2,1,3]` and `[8,5,7,6]`.

> [!analogy] Real-world analogy: lining a class up around one child's height
> A teacher picks the last child in the line as the reference. Walking along the rest of the line, each child shorter than the reference is sent to join a group at the front; everyone else stays where they are. Finally the reference child steps in just behind the front group. That child is now exactly where they belong in height order, even though neither group is in order yet.
>
> **How it maps:** the reference child is the pivot, the back of the front group is the boundary `i`, sending a child forward is a swap, and the reference child stepping into place is Lomuto's final swap. Lining up each group the same way is the recursion.
>
> **Where it stops:** children can shuffle around freely; Lomuto rearranges one array in place by swapping pairs of positions. Those swaps can carry one child past another of the same height, which is why the partition is not stable.

## Key takeaways
- Lomuto finishes by placing the pivot at its sorted index.
- Partition swaps can reorder equal keys, so this implementation is unstable.

## Further reading
- [Quicksort and partitioning — Princeton Algorithms](https://algs4.cs.princeton.edu/23quicksort/)
