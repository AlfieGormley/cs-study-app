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

Each element is either in or out, independently, so the number of subsets **doubles with every extra element**: 2ⁿ subsets for n distinct elements, counting the empty set and the whole set. Twenty elements give about a million subsets; forty give over a trillion. Copying each finished subset into the result costs up to n steps, so generating them all is O(n·2ⁿ) work.

With forty elements full materialisation is very expensive. Whether it is practical depends on the representation and resources.

> [!analogy] Real-world analogy: a row of light switches
> A panel of light switches, each on or off, can be set in many patterns. One switch gives 2 patterns, two give 4, three give 8: every switch you add doubles the number of patterns.
>
> **How it maps:** each switch is one element, "on" means the element is in the subset, and each pattern of switches is one subset. The include/skip recursion flips through the patterns one switch at a time, which is why the tree has one level per element and two branches at each node.
>
> **Where it stops:** flipping a switch costs nothing extra. The program also stores each subset as its own list, so every pattern costs memory and copying time proportional to its size.

> [!warning] Append a copy, not the path
> `res.append(path)` stores a reference to the one shared list. After the search finishes, every unchoose has run, `path` is empty, and `res` is a list of identical empty lists: `[[], [], [], []]`. Always append `path[:]` or `list(path)`.

## Key takeaways
- Include/skip and increasing-index loops both enumerate subsets.
- Store a copy of the current path, and count output storage separately from working search state.

## Further reading
- [Backtracking — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
- [Python itertools](https://docs.python.org/3/library/itertools.html)
