---
id: tech-backtracking
title: Backtracking
level: intermediate
minutes: 13
summary: The choose, explore, unchoose template for searching every possibility, applied to subsets, permutations and combinations, and how pruning cuts the search down.
---

Some problems don't have a clever formula. You simply have to try possibilities: every subset, every ordering, every placement. **Backtracking** is the disciplined way to do that.

Picture walking a maze with a piece of chalk. At each junction you pick a corridor and mark it. If you reach a dead end, you walk back to the last junction, rub out the mark and try the next corridor. With systematic choice enumeration and a mark for every cell on the current path, you can enumerate simple routes without following a cycle forever. The path is working state; access to the maze and any extra constraints still requires storage.

## The decision tree

Every backtracking problem is a walk over an implicit **decision tree**. Each level is one decision; each edge is one choice; each leaf is a complete candidate.

Generating subsets of `[1, 2, 3]`: at each level decide "include this element or not".

```
                  []
          +1 /         \ skip
          [1]           []
       +2/   \       +2/  \
     [1,2]   [1]    [2]    []
     /  \    / \    / \    / \
 [123][12][13][1][23][2] [3] []
```

The tree has 2³ = 8 leaves, one per subset. Backtracking is a **depth-first** traversal of this tree that builds the current path incrementally and undoes it on the way back.

## The template: choose, explore, unchoose

Almost every backtracking solution has this shape:

```python
def backtrack(state):
    if is_complete(state):
        record(state)
        return
    for choice in choices(state):
        if not is_valid(state, choice):
            continue          # prune
        make(state, choice)   # choose
        backtrack(state)      # explore
        undo(state, choice)   # unchoose
```

- **Choose** modifies one shared piece of state (append to a path, mark a cell used).
- **Explore** recurses with that choice in place.
- **Unchoose** restores the state *exactly* so that the next choice starts from the same position.

Simple path append/pop updates cost amortised O(1), avoiding a full path copy at each node. Constraint checks and richer updates can cost more; shared mutation alone does not make them constant-time. The abstract helpers in this template are problem-specific.

## Subsets

The include/skip version maps directly onto the tree above:

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
        res.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            bt(i + 1)
            path.pop()
    bt(0)
    return res

# [[], [1], [1,2], [1,2,3], [1,3],
#  [2], [2,3], [3]]
```

For n distinct elements (or n distinguished positions), there are 2ⁿ subsets, and copying each costs up to n, so the total is **O(n · 2ⁿ)**. At n = 20 that's about a million subsets; at n = 40 it exceeds a trillion, making full materialisation expensive. Feasibility depends on the representation and resources.

> [!warning] Append a copy, not the path
> `res.append(path)` stores a reference to the one shared list. After the search finishes, every unchoose has run, `path` is empty, and `res` is a list of identical empty lists: `[[], [], [], []]`. Always append `path[:]` or `list(path)`.

## Permutations

For orderings, every unused element is a possible next choice. A `used` array tracks what's already on the path:

```python
def permutations(nums):
    res, path = [], []
    used = [False] * len(nums)
    def bt():
        if len(path) == len(nums):
            res.append(path[:])
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True        # choose
            path.append(x)
            bt()                  # explore
            path.pop()            # unchoose
            used[i] = False
    bt()
    return res

# [1,2,3] -> 123 132 213 231 312 321
```

For n distinct values, the tree has n choices at the root, n − 1 below that, and so on: **n!** leaves. Repeated input values produce duplicate value sequences unless separately handled. With O(n) to copy each, it's **O(n · n!)**. 10! is about 3.6 million; 13! is over 6 billion.

## Combinations

Choosing k of n items without regard to order is subsets with a size limit. Using `start` again prevents `[2, 1]` from appearing after `[1, 2]`:

```python
def combine(n, k):
    if (type(n) is not int or n < 0
            or type(k) is not int or k < 0):
        raise ValueError("nonnegative n, k")
    res, path = [], []
    def bt(start):
        if len(path) == k:
            res.append(path[:])
            return
        need = k - len(path)
        # stop if too few numbers remain
        for i in range(start, n - need + 2):
            path.append(i)
            bt(i + 1)
            path.pop()
    bt(1)
    return res

# combine(4, 2) -> [1,2] [1,3] [1,4]
#                  [2,3] [2,4] [3,4]
```

There are C(n, k) = n! / (k!(n − k)!) results. The loop bound `n - need + 2` is already a small piece of **pruning**: if you need 2 more numbers, there's no point starting at n.

## Pruning: the point of backtracking

Without pruning, backtracking is just brute force with neat bookkeeping. Its real power is abandoning a partial path the moment it can't lead to a valid answer, which skips the **entire subtree** below it.

Two kinds of prune:

- **Feasibility**: the partial solution already breaks a rule (two queens attack each other, the sum exceeds the target).
- **Bound**: the partial solution can't possibly beat the best answer found so far (branch and bound).

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
    cands = sorted(set(cands))
    res, path = [], []
    def bt(start, remaining):
        if remaining == 0:
            res.append(path[:])
            return
        for i in range(start, len(cands)):
            c = cands[i]
            if c > remaining:
                break            # prune
            path.append(c)
            bt(i, remaining - c)  # reuse
            path.pop()
    bt(0, target)
    return res

# [2,3,5], 8 -> [2,2,2,2] [2,3,3] [3,5]
```

Sorting first turns a `continue` into a `break`: once one candidate is too big, every later one is too, so the rest of the loop is skipped. Passing `i` (not `i + 1`) allows reuse; restricting the next loop to indices at least i stops `[3, 2, 3]` duplicating `[2, 3, 3]`.

### Handling duplicate inputs

For `[1, 2, 2]`, the plain subsets code produces `[2]` twice and `[1, 2]` twice. Sort, then skip a value that equals its left neighbour **at the same depth**:

```python
nums.sort()
for i in range(start, len(nums)):
    if i > start and nums[i] == nums[i-1]:
        continue
```

The `i > start` condition is key: it allows `[2, 2]` (the second 2 chosen at a *deeper* level) but forbids starting two sibling branches with equal values. `[1, 2, 2]` then gives 6 distinct subsets instead of 8.

## Complexity at a glance

| Problem | Results | Time |
|---|---|---|
| Subsets | 2ⁿ | O(n·2ⁿ) |
| Permutations | n! | O(n·n!) |
| Combinations (0 ≤ k ≤ n) | C(n,k) | O(1 + k·C(n,k)) |
| With pruning | varies | often far less |

For subsets, permutations and combinations, working space is O(n), excluding output. With reusable candidates, path depth can instead reach target/min(candidate). In general count path, frames and constraint state separately. Counting can omit stored outputs but normally still explores all relevant branches; finding one solution can stop at the first success.

## Where backtracking shows up

- **Regular expression engines.** Backtracking engines such as Python’s `re` can explore exponentially many alternatives for `(a+)+$` on `"aaaa…ab"`. This can cause **regular-expression denial of service (ReDoS)**. Cloudflare’s 2 July 2019 outage involved a different pattern with super-linear backtracking; it is not evidence that this exact pattern was deployed. RE2 and Rust’s `regex` bound a single search by O(mn) in regex size m and input length n, hence linear in n for a fixed regex; repeated-search APIs can have different bounds.

> [!note] Content gap
> Per-length regex timings are omitted because no pinned interpreter, machine and benchmark support the original measurements.
- **Dependency resolvers.** pip's resolver backtracks: it picks candidate versions and, on conflict, undoes choices and tries alternative compatible versions; those need not always be older.
- **SAT and constraint solvers** (next lesson), Prolog's execution model, parsers with alternatives, and puzzle solvers.

## Pitfalls

- **Forgetting to unchoose**, or undoing in the wrong order, so later branches start from corrupted state.
- **Appending the shared path** instead of a copy.
- **Generating duplicates** because the loop restarts from 0 instead of `start`.
- **Not pruning early enough**: checking validity only at the leaves turns backtracking back into brute force.
- **Exploding output.** No pruning helps if the answer itself has n! entries.

## Key takeaways
- Backtracking is a depth-first walk over a decision tree, building one partial solution in shared state.
- Template: check for a complete solution, then for each valid choice: choose, explore, unchoose.
- Subsets O(n·2ⁿ), permutations O(n·n!), combinations O(1 + k·C(n,k)) for 0 ≤ k ≤ n.
- Use a `start` index to avoid reordered duplicates; sort and skip equal siblings for duplicate inputs.
- Pruning abandons whole subtrees; sorted inputs often turn `continue` into `break`.

## Further reading
- [Backtracking — Wikipedia](https://en.wikipedia.org/wiki/Backtracking)
- [Jeff Erickson, Algorithms, chapter 2: Backtracking (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
- [itertools: combinations and permutations — Python docs](https://docs.python.org/3/library/itertools.html)
- [ReDoS — Wikipedia](https://en.wikipedia.org/wiki/ReDoS)
- [Details of the Cloudflare outage on July 2, 2019](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/)
- [Dependency resolution — pip docs](https://pip.pypa.io/en/stable/topics/dependency-resolution/)
