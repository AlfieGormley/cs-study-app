---
id: tech-backtracking-combinations
title: Choosing fixed-size combinations
level: intermediate
minutes: 2
sourceLesson: tech-backtracking
summary: A start index prevents reordered copies of the same combination.
---

## Combinations

Choosing k items from n without regard to order is subsets with a size limit. Using `start` again prevents `[2, 1]` from appearing after `[1, 2]`:

```python
def combine(n, k):
    if (type(n) is not int or n < 0
            or type(k) is not int or k < 0):
        raise ValueError("nonnegative n, k")
    res, path = [], []
    def bt(start):
        if len(path) == k:
            # Store a snapshot, not the
            # shared path.
            res.append(path[:])
            return
        need = k - len(path)
        # stop if too few numbers remain
        # Leave enough later values to
        # finish a result.
        for i in range(start, n - need + 2):
            path.append(i)
            bt(i + 1)
            # Restore the path for the next
            # sibling.
            path.pop()
    bt(1)
    return res

# combine(4, 2) -> [1,2] [1,3] [1,4]
#                  [2,3] [2,4] [3,4]
```

The number of results is the **binomial coefficient**, "n choose k":

```formula
C(n, k) = n! / (k! (n − k)!)
C(4, 2) = 24 / (2 × 2) = 6
where
C(n, k): the number of ways to choose k items from n distinct items when order doesn't matter
n: the number of items to choose from
k: how many items each combination contains, from 0 to n
n!: n factorial, n × (n − 1) × … × 1 (and 0! = 1)
k!: k factorial, the number of orderings of the k chosen items
(n − k)!: the factorial of the number of items left out
In words: count the orderings of all n items, then divide out the orderings inside the chosen group and inside the left-out group, because they don't make a different combination.
```

That matches the six pairs returned by `combine(4, 2)`; the comment shows the result without printing it. The loop bound `n - need + 2` is already a small piece of **pruning**: if you need 2 more numbers, there's no point starting at n.

## Key takeaways
- A start index prevents reordered copies of the same combination.
- The remaining-needed bound avoids branches with too few items left.

## Further reading
- [Backtracking — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
- [Python itertools](https://docs.python.org/3/library/itertools.html)
