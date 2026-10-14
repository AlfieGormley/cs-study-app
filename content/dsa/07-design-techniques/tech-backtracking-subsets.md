---
id: tech-backtracking-subsets
title: Generating subsets without shared-output bugs
level: intermediate
minutes: 2
sourceLesson: tech-backtracking
summary: Include/skip and increasing-index loops both enumerate subsets.
---

## Subsets

The include/skip version maps directly onto the previous unit’s decision tree:

```python
def subsets(nums):
    res, path = [], []
    def bt(i):
        if i == len(nums):
            res.append(path[:])   # copy!
            return
        path.append(nums[i])      # choose
        bt(i + 1)                 # explore
        path.pop()                # unchoose
        bt(i + 1)                 # skip it
    bt(0)
    return res
```

An equally common version records a subset at **every** node and loops over which element to add next. Starting each loop from `start` ensures each subset is generated once, in one order:

```python
def subsets(nums):
    res, path = [], []
    def bt(start):
        # Store a snapshot, not the shared
        # path.
        res.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            bt(i + 1)
            # Restore the path for the next
            # sibling.
            path.pop()
    bt(0)
    return res

# [[], [1], [1,2], [1,2,3], [1,3],
#  [2], [2,3], [3]]
```

Each element is either in or out, independently, so the number of subsets doubles with every extra element. Copying each finished subset into the result costs up to n steps:

```formula
N_sub = 2^n
W = O(n 2^n)
N_sub = 2^20 = 1,048,576
N_sub = 2^40 ≈ 1.1 × 10^12
where
N_sub: the number of subsets of n distinct elements (including the empty set and the whole set)
n: the number of distinct elements (or distinguished positions)
2^n: n copies of 2 multiplied together
W: the total work to generate and copy every subset
O: Big-O, grows no faster than this up to a constant factor
10^12: one trillion (a 1 followed by 12 zeros)
≈: approximately equal to
In words: every extra element doubles the number of subsets; 20 elements give about a million, 40 give over a trillion.
```

With forty elements full materialisation is very expensive. Whether it is practical depends on the representation and resources.

> [!warning] Append a copy, not the path
> `res.append(path)` stores a reference to the one shared list. After the search finishes, every unchoose has run, `path` is empty, and `res` is a list of identical empty lists: `[[], [], [], []]`. Always append `path[:]` or `list(path)`.

## Key takeaways
- Include/skip and increasing-index loops both enumerate subsets.
- Store a copy of the current path, and count output storage separately from working search state.

## Further reading
- [Backtracking — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
- [Python itertools](https://docs.python.org/3/library/itertools.html)
