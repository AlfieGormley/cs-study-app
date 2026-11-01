---
id: tech-backtracking-permutations
title: Generating permutations
level: intermediate
minutes: 2
sourceLesson: tech-backtracking
summary: Track used positions to generate each ordering of distinct values.
---

## Permutations

For orderings, every unused element is a possible next choice. A `used` array tracks what's already on the path:

```python
def permutations(nums):
    res, path = [], []
    used = [False] * len(nums)
    def bt():
        if len(path) == len(nums):
            # Store a snapshot, not the
            # shared path.
            res.append(path[:])
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True        # choose
            path.append(x)
            bt()                  # explore
            path.pop()            # unchoose
            # Release the position as well
            # as its value.
            used[i] = False
    bt()
    return res

# [1,2,3] -> 123 132 213 231 312 321
```

For n distinct values, the tree has n choices at the root, n − 1 below that, and so on down to 1. Multiplying those choices together gives the number of leaves, **n factorial** (written n!): about 3.6 million orderings for 10 values and over 6 billion for 13. Each finished permutation is copied in up to n steps, so storing them all is O(n·n!) work.

Factorial growth is even steeper than the doubling of subsets: adding one more value multiplies the number of orderings by the new count of values, so going from 10 to 11 values multiplies it by 11.

Repeated input values produce duplicate value sequences unless separately handled.

## Key takeaways
- Track used positions to generate each ordering of distinct values.
- Factorial output growth dominates even with careful working-state bookkeeping.

## Further reading
- [Backtracking — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
- [Python itertools](https://docs.python.org/3/library/itertools.html)
