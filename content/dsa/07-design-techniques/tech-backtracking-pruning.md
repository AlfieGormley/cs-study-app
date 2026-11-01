---
id: tech-backtracking-pruning
title: Pruning combination-sum search
level: intermediate
minutes: 4
sourceLesson: tech-backtracking
summary: Reject a partial search state only when its whole subtree is impossible or cannot improve a bound.
---

## Pruning: the point of backtracking

Without pruning, backtracking is just brute force with neat bookkeeping. Its real power is abandoning a partial path the moment it can't lead to a valid answer, which skips the **entire subtree** below it.

Two kinds of prune:

- **Feasibility pruning**: the partial solution already breaks a rule (two queens attack each other, the sum exceeds the target).
- **Bound pruning**: the partial solution can't possibly beat the best answer found so far (branch and bound).

### Example: combination sum

Find all combinations of distinct positive integer candidate values (each reusable) that add up to a non-negative integer target. The implementation deduplicates repeated candidate values.

```python
def combination_sum(cands, target):
    cands = list(cands)
    if (type(target) is not int
            or target < 0
            or any(type(c) is not int
                   or c <= 0
                   for c in cands)):
        raise ValueError("candidates")
    # Deduplicate values and permit early
    # stopping.
    cands = sorted(set(cands))
    res, path = [], []
    def bt(start, remaining):
        if remaining == 0:
            # Store a snapshot, not the
            # shared path.
            res.append(path[:])
            return
        for i in range(start, len(cands)):
            c = cands[i]
            if c > remaining:
                break            # prune
            path.append(c)
            # Keep this index available for
            # repeated use.
            bt(i, remaining - c)  # reuse
            # Restore the path for the next
            # sibling.
            path.pop()
    bt(0, target)
    return res

# [2,3,5], 8 -> [2,2,2,2] [2,3,3] [3,5]
```

Sorting first turns a `continue` into a `break`: once one candidate is too big, every later one is too, so the rest of the loop is skipped. Passing `i` (not `i + 1`) allows reuse; restricting the next loop to indices at least i stops `[3, 2, 3]` duplicating `[2, 3, 3]`.

> [!analogy] Real-world analogy: shopping with a budget
> You have £8 left and a shelf of snacks arranged from cheapest to dearest. As soon as you reach one that costs more than £8, you stop looking along the shelf: everything after it costs even more.
>
> **How it maps:** the money left is `remaining`, the sorted shelf is the sorted list of candidates, and walking away at the first unaffordable item is the `break`. Each skipped item would have started a whole subtree of further choices, so one comparison saves all of them.
>
> **Where it stops:** the shortcut depends on the shelf being sorted and on prices being positive. With unsorted candidates you can only skip one item at a time, and with negative values a later choice could bring the total back down, so the prune would lose answers.

## Complexity at a glance

Here n is the number of input elements and k the size of each combination, with k between zero and n. The earlier enumeration units derived the result counts below; copying each result costs its own length.

| Problem | Results | Time |
|---|---|---|
| Subsets | Exponential | O(n·2ⁿ) |
| Permutations | Factorial | O(n·n!) |
| Size-k combinations | Binomial | O(1 + k·C(n,k)) |
| With pruning | varies | often far less |

For subsets, permutations and combinations, working space is O(n), excluding output. With reusable candidates, the path can be much longer than the number of candidates: the deepest path uses the smallest candidate over and over, so its length is the target divided by the smallest candidate, rounded down. For target 8 with smallest candidate 2 that is [2, 2, 2, 2], four selections deep (plus one frame for the root call).

In general count path, frames and constraint state separately. Counting can omit stored outputs but normally still explores all relevant branches; finding one solution can stop at the first success.

## Key takeaways
- Reject a partial search state only when its whole subtree is impossible or cannot improve a bound.
- Sorted positive candidates allow early break; reuse keeps the same candidate index.

## Further reading
- [Backtracking — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
- [Python itertools](https://docs.python.org/3/library/itertools.html)
