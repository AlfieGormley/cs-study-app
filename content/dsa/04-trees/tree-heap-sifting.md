---
id: tree-heap-sifting
title: Sift up, sift down and priority removal
level: intermediate
minutes: 4
sourceLesson: tree-heaps
summary: Push appends and moves the new key toward the root.
---

Use the complete-tree array layout introduced earlier. The root is array slot zero; absent child positions lie beyond the occupied prefix. Here n counts binary heap entries and comparisons have constant cost. A valid min-heap makes each parent no greater than its children, without ordering siblings. Array allocation and returned output require their own cost accounting.

## Sift up: push

To push, append the new item at the end (the next free slot in the last level, which keeps the shape) and then **sift up**: while it is smaller than its parent, swap them.

```python
def sift_up(a, i):
    while i > 0:
        p = (i - 1) // 2
        # Stop once this parent-
        # child order holds.
        if a[p] <= a[i]:
            break
        a[p], a[i] = a[i], a[p]
        i = p

def push(a, x):
    a.append(x)
    sift_up(a, len(a) - 1)
```

Pushing 0 into the binary heap `[1, 3, 2, 4, 8, 7, 6, 9]` from the previous unit: it lands at index 8 (child of 4), swaps with 4, then 3, then 1, and becomes the new root. There is at most one swap per level, and because a heap is always a complete tree, it is short: a 9-item heap has height 3, so those 3 swaps are the most possible. A million-item binary heap has height 19, so push is **O(log n)**. Many pushes stop after one comparison, because a new item is often no smaller than its parent.

## Sift down: pop

To pop the minimum, you cannot just remove the root: that would leave a hole at the top. Instead, move the **last** item into the root (keeping the shape), shrink the array, and **sift down**: swap it with its **smaller** child until it is no larger than both children.

```python
def sift_down(a, i, n):
    while True:
        # Choose the smallest of
        # parent/children.
        best = i
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and a[l] < a[best]:
            best = l
        if r < n and a[r] < a[best]:
            best = r
        if best == i:
            return
        a[i], a[best] = a[best], a[i]
        i = best

def pop(a):
    # Move the minimum to the
    # removable last slot.
    a[0], a[-1] = a[-1], a[0]
    top = a.pop()
    if a:
        sift_down(a, 0, len(a))
    return top
```

Swapping with the **smaller** child matters: that child becomes the parent of the other, so it must be the smaller of the two. Pop also makes at most one swap per level, the same height limit as push, so for n items it is also **O(log n)**.

> [!warning] Binary Heaps are not sorted
> Only `a[0]` is guaranteed to be the minimum. `a[1]` is not necessarily the second smallest (in the example it is 3, but 2 is smaller), and iterating over a binary heap list does not give sorted order. Popping repeatedly does.

## Key takeaways
- Push appends and moves the new key toward the root.
- Pop moves the final entry to the root and repairs downward.
- Choose the smaller child to preserve min-heap order.

## Further reading
- [Binary heap — Wikipedia](https://en.wikipedia.org/wiki/Binary_heap)
- [Priority Queues — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/24pq/)
