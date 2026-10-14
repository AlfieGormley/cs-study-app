---
id: cx-in-place-memory
sourceLesson: cx-space-complexity
title: In-place transformations
level: intermediate
minutes: 3
summary: Mutate an existing list and bound quicksort stack depth by recursing on the smaller side.
---

Here n is the number of input items. In-place transformations save memory by reusing the input itself.

## In-place algorithms

An algorithm is **in-place** if it transforms its input using only O(1) auxiliary space, a constant amount however big the input of n items is (some definitions allow O(log n), to cover a recursion stack). Reversing a list with two pointers is the classic example:

```python
def reverse_in_place(xs):
    i, j = 0, len(xs) - 1
    while i < j:
        # Swap the ends of the same list.
        xs[i], xs[j] = xs[j], xs[i]
        i += 1
        j -= 1
# Changes xs; returns None implicitly.
```

Compare `xs[::-1]`, which is simpler but allocates a whole new list.

In-place algorithms save memory and often run faster (less allocation, better cache use). The costs:

- **They destroy the input.** If the caller still needs the original, it has to copy it first, and the saving vanishes.
- **They can be harder to get right.** Swapping elements around inside one array is fiddlier than building a new one.
- **They don't play well with sharing.** Mutating a list that other code (or another thread) holds a reference to causes surprising bugs.

Sorting is the familiar case. Heapsort sorts in place with O(1) auxiliary space. Quicksort partitions in place, but its recursion needs a stack: O(log n) expected depth, O(n) in the worst case. A standard trick bounds it at O(log n) even in the worst case: **recurse into the smaller partition and loop on the larger one**, because the smaller side is at most half the size. Python's `list.sort()` mutates its input, but is not in-place in the strict O(1)-auxiliary-space sense; it may allocate a temporary buffer of up to half the list (half the items) while merging.

Why does recursing into the smaller side bound the depth? Each recursive call at least halves the size of the part it works on:

```formula
s_{k+1} ≤ s_k / 2
s_k ≤ n / 2^k
depth ≤ ⌊log_2(n)⌋ + 1   for n ≥ 1
where
s_k: the size of the partition handled at recursion depth k
s_{k+1}: the size handled one level deeper
k: the recursion depth (0 for the first call)
n: the number of items being sorted
depth: the maximum number of quicksort frames on the stack at once, including the initial call
⌊x⌋: floor: round x down to the nearest whole number
log_2(n): the base-2 logarithm of n, the number of halvings that take n down to 1
≤: less than or equal to
In words: the smaller partition is at most half the current size, so you can only go about log_2(n) levels deep before reaching a single item.
```

For a million items that is at most 20 frames including the initial call, instead of up to a million.

## Key takeaways
- Strict in-place analysis permits only a constant amount of extra storage.
- Mutating the input can affect other references to the same list.
- Recursing on the smaller quicksort partition bounds stack depth even when partition balance is poor.

## Further reading
- [In-place algorithm — Wikipedia](https://en.wikipedia.org/wiki/In-place_algorithm)
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)
