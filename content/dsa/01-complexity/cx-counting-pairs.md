---
id: cx-counting-pairs
sourceLesson: cx-growth-rates
title: Comparing every pair
level: basic
minutes: 2
summary: Count the comparisons in a duplicate check that visits each distinct pair once.
---

Comparing each item with every other item creates much more work than scanning once. Here n is the number of list items, and equality comparisons are assumed constant cost.

## Why avoiding repeats still leaves quadratic work

```python
# has_dup([2, 3, 2]) returns True.
def has_dup(xs):
    for i in range(len(xs)):
        # Check each pair only once.
        for j in range(i + 1, len(xs)):
            if xs[i] == xs[j]:
                return True
    return False
```

Starting the inner loop after the outer position avoids comparing an item with itself and avoids checking a pair in both orders. The first item still meets every later item; later passes become progressively shorter. With no duplicates, none can exit early.

Doubling a large list roughly quadruples these comparisons: there are about twice as many items, each with about twice as many possible partners. Checking only half the full square changes the amount of work, but its growth remains quadratic.

The exact pair count is useful when budgeting comparisons, but the growth argument does not require calculating it:

```formula reference
C(n) = n(n − 1) / 2
where
C(n): the number of distinct pairs of positions, and worst-case equality checks in this function
n: the nonnegative number of list items
In words: pair each position with every different position, then halve the result because reversing a pair does not create a new pair.
```

Do not classify code by counting nested loops alone. Two consecutive full passes are linear. A full pass containing a fixed hundred checks is also linear. A nested inner range proportional to the input gives quadratic work.

For large duplicate checks, sorting makes equal values adjacent; an efficient comparison sort followed by a scan takes O(n log n) time. A hash set takes expected O(n) time under suitable hashing assumptions, using extra memory. Neither bound promises a specific runtime.

## Key takeaways
- Avoiding repeated pairs reduces work without removing quadratic growth.
- An early return helps only inputs that reach it early.
- Improving the search structure can matter more than speeding up each comparison.

## Further reading
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
