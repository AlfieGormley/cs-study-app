---
id: tech-backtracking-duplicates
title: Skipping equal sibling choices
level: intermediate
minutes: 1
sourceLesson: tech-backtracking
summary: Skip equal values at the same depth, while allowing them at deeper levels.
---

The earlier subsets unit recorded a path at every node and recursed only to later indices. Distinct positions are useful for distinct elements, but repeated values make identical result lists. We now keep the increasing-index search while eliminating equal sibling branches.

### Handling duplicate inputs

For `[1, 2, 2]`, the plain subsets code produces `[2]` twice and `[1, 2]` twice. Sort, then skip a value that equals its left neighbour **at the same depth**:

```python
# Equal siblings become adjacent after
# sorting.
nums.sort()
for i in range(start, len(nums)):
    # Skip siblings, not equal values deeper
    # down.
    if i > start and nums[i] == nums[i-1]:
        continue
```

The `i > start` condition is key: it allows `[2, 2]` (the second 2 chosen at a *deeper* level) but forbids starting two sibling branches with equal values. `[1, 2, 2]` then gives 6 distinct subsets instead of 8.

## Key takeaways
- Skip equal values at the same depth, while allowing them at deeper levels.
- A sibling-only test preserves combinations that use repeated values.

## Further reading
- [Backtracking — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
- [Python itertools](https://docs.python.org/3/library/itertools.html)
