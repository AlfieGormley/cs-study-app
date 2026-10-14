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

For n distinct values, the tree has n choices at the root, n − 1 below that, and so on down to 1. Multiplying those choices together gives the number of leaves, **n factorial**:

```formula
n! = n × (n − 1) × … × 2 × 1
W = O(n^2!)
10! = 3,628,800
13! = 6,227,020,800
where
n: the number of distinct values to order
n!: n factorial, the product of every whole number from 1 to n; the number of orderings of n distinct items (0! = 1)
…: and so on, one less each time
W: the total work to generate and copy every permutation (each copy costs up to n)
O: Big-O, grows no faster than this up to a constant factor
In words: n choices for the first position, n − 1 for the second, and so on, multiply to n factorial orderings: about 3.6 million for 10 values and over 6 billion for 13.
```

Repeated input values produce duplicate value sequences unless separately handled.

## Key takeaways
- Track used positions to generate each ordering of distinct values.
- Factorial output growth dominates even with careful working-state bookkeeping.

## Further reading
- [Backtracking — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
- [Python itertools](https://docs.python.org/3/library/itertools.html)
