---
id: cx-in-place-memory
sourceLesson: cx-space-complexity
title: In-place transformations
level: intermediate
minutes: 2
summary: Mutate an existing list and bound quicksort stack depth by recursing on the smaller side.
---

An in-place transformation reuses the input storage. Under the strict convention it uses only constant auxiliary space; some descriptions allow a logarithmic recursion stack. State which convention you mean.

```python
def reverse_in_place(xs):
    i, j = 0, len(xs) - 1
    while i < j:
        xs[i], xs[j] = xs[j], xs[i]
        i += 1
        j -= 1
```

This keeps two positions and swaps within the existing list. It returns `None`. In contrast, `xs[::-1]` allocates a new list. Here n is the list length; the first uses O(1) auxiliary words and the copy uses O(n).

## Mutation has a cost beyond memory

Other references to the same list observe the changes. If the caller needs the original order, copying first removes the storage saving. An in-place algorithm can also be harder to implement correctly. Choose it because its trade-offs fit the caller, not merely because its space label is smaller.

Mutating an input is not proof of constant auxiliary space. CPython's `list.sort()` mutates the list but may allocate a merge buffer proportional to its length. Heapsort can sort an array using constant auxiliary words.

## Bound quicksort's stack separately from its time

Ordinary quicksort that recurses on both partitions can build a linear-depth chain with repeatedly unbalanced pivots. Recurse only on the smaller partition and process the larger partition with a loop. Every additional recursive frame then receives at most half its parent's items, bounding stack depth by O(log n).

Changing the order of two recursive calls is insufficient: the larger side must become a loop. This change fixes stack growth even with a poor pivot rule, but it does not remove quadratic worst-case comparisons. Random pivots improve expected time under the stated randomness model; a fallback such as heapsort can provide a worst-case time bound.

## Key takeaways
- Distinguish mutation from constant auxiliary storage.
- Check whether other code still needs the original input.
- Recursing on the smaller side bounds stack depth without necessarily fixing runtime.

## Further reading
- [CPython 3.14 sorting design](https://github.com/python/cpython/blob/3.14/Objects/listsort.txt)
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
