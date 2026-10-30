---
id: sort-heapsort-extraction
title: Heapsort construction and extraction
level: intermediate
minutes: 5
sourceLesson: sort-heapsort-lower-bound
summary: Build a max-heap from the last parent toward the root.
---

Throughout this lesson, n is the number of elements being sorted, and the logarithm notation in each card is base two: how many times n can be halved before reaching 1 (about 20 for a million). O, Θ and Ω are Big O, Big Theta and Big Omega: growth rates of at most, exactly and at least, ignoring constant factors.

So far we have two O(n log n) sorts, each with a catch. Merge sort is guaranteed linear times logarithmic growth but needs O(n) extra memory. Quicksort is in place but can go quadratic. **Heapsort** removes both catches: O(n log n) in the worst case, with O(1) extra space.

Then we will ask a deeper question: could some cleverer algorithm do better than linear times logarithmic growth? The answer is no, for any algorithm that sorts by comparing elements, and the proof is one of the most elegant in computer science.

## Heapsort

Heapsort is selection sort with a better data structure. Selection sort spends O(n) finding the maximum each round. A **binary max-heap** (covered in the trees module) finds and removes the maximum in O(log n).

Recall the array layout. The heap is a tree stored level by level in the array, with no pointers; the position of a node's children is computed from its own index (the code below uses `2*i + 1` and `2*i + 2`). The node at index 1, for example, has children at indices 3 and 4.

```formula reference
c_L(i) = 2i + 1
c_R(i) = 2i + 2
p(i) = ⌊(i − 1) / 2⌋
where
i: the index (position, counting from 0) of a node in the array
c_L: function giving the left-child index from the parent index i
c_R: function giving the right-child index from the parent index i
p: function giving the parent index from the child index i (for any node except the root, which is at index 0)
⌊ ⌋: the floor: round down to a whole number
In words: a node's two children sit just after twice its index, and its parent is found by reversing that step, so the tree needs no pointers.
```

Every parent is at least as large as its children (the **heap property**). So the maximum is always at index 0.

The algorithm has two phases:

1. **Build** a max-heap in place from the array.
2. **Repeatedly** swap the root (the maximum) with the last element of the heap, shrink the heap by one, and sift the new root down to restore the heap property.

The sorted part grows from the right, exactly like selection sort.

```python
def sift_down(a, i, n):
    while True:
        # Find the largest within this heap
        # family.
        big = i
        l, r = 2*i + 1, 2*i + 2
        if l < n and a[l] > a[big]:
            big = l
        if r < n and a[r] > a[big]:
            big = r
        # No larger child means the heap is
        # valid.
        if big == i:
            return
        a[i], a[big] = a[big], a[i]
        # Continue down the displaced item’s
        # path.
        i = big

def heapsort(a):
    n = len(a)
    # phase 1: bottom-up heap build
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
    # phase 2: extract max n-1 times
    # The sorted suffix grows each pass.
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        # Exclude the sorted suffix from the
        # heap.
        sift_down(a, 0, end)
```

### Trace

Input `[4, 10, 3, 5, 1]`.

**Phase 1.** Start at the last node that has a child; every node after it is a leaf, which is already a valid one-element heap. The second half of the array is all leaves, so the loop starts just before the halfway point (`n // 2 - 1`, index 1 for these 5 items) and works back to index 0.


```
i 1: 10 vs children 5, 1 -> fine
i 0: 4 vs children 10, 3 -> swap 10
     [10, 4, 3, 5, 1]
     4 vs children 5, 1 -> swap 5
     [10, 5, 3, 4, 1]   max-heap
```

**Phase 2.** Swap root to the end, sift down, repeat.

```
swap 10<->1, sift: [5, 4, 3, 1 | 10]
swap 5<->1,  sift: [4, 1, 3 | 5, 10]
swap 4<->3,  sift: [3, 1 | 4, 5, 10]
swap 3<->1:        [1 | 3, 4, 5, 10]
```

## Key takeaways
- Build a max-heap from the last parent toward the root.
- Move the root to the sorted suffix and restore the remaining heap by sifting down.

## Further reading
- [Priority queues and heapsort — Princeton Algorithms](https://algs4.cs.princeton.edu/24pq/)
