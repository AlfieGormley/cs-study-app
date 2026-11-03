---
id: dp-lis-binary-search
title: LIS length using minimum tails
level: intermediate
minutes: 3
summary: Sorted minimum tails allow binary search for each new value.
sourceLesson: dp-1d
---

### Minimum tails with binary search

Keep an array `tails` where `tails[k]` is the **smallest possible last element** of an increasing subsequence of length k + 1 seen so far. `tails` is always sorted, so you can binary-search it.

For each x:

- If x is bigger than every tail, append it: you've extended the longest subsequence.
- Otherwise replace the first tail that is not smaller than the new value: you have found a subsequence of that same length with a no-larger ending, making future extension at least as easy.

```python
from bisect import bisect_left

def lis_fast(a):
    tails = []
    for x in a:
        # Find the first tail not smaller
        # than x.
        k = bisect_left(tails, x)
        # A new largest tail extends the
        # length.
        if k == len(tails):
            tails.append(x)
        else:
            # Improve this length's ending
            # value.
            tails[k] = x
    return len(tails)
```

Trace:

```
x     tails
10    [10]
9     [9]
2     [2]
5     [2, 5]
3     [2, 3]
7     [2, 3, 7]
101   [2, 3, 7, 101]
18    [2, 3, 7, 18]
```

Length 4. Here n is the number of input elements. Each one costs a single binary search on `tails` (at most about log₂ n comparisons) plus an O(1) append or replacement, so the total is O(n log n): for 100,000 elements, roughly 1.7 million comparisons rather than the quadratic DP's 5 billion. The memory is O(n) slots for `tails`.

> [!analogy] Real-world analogy: dealing cards into piles
> Deal a shuffled deck one card at a time. Put each card on the leftmost pile whose top card is at least as high as it; if there is no such pile, start a new pile on the right. This is a simplified version of the patience (solitaire) game that gives the algorithm its other name, patience sorting.
>
> **How it maps:** the top cards of the piles, read left to right, are the `tails` array, and they are always in increasing order. Choosing the leftmost allowed pile is the `bisect_left` search, and starting a new pile is the append. The number of piles at the end is the length of the longest increasing subsequence.
>
> **Where it stops:** the visible top cards are not themselves an increasing subsequence of the deal order, just as `tails` isn't. Recovering an actual subsequence needs extra bookkeeping: a link from each card to the top of the pile on its left at the moment it was placed.

> [!warning] tails is not the LIS
> On `[3, 1, 4, 1, 5, 9, 2, 6]` the final `tails` is `[1, 2, 5, 6]`. That isn't a subsequence at all: the 2 comes *after* the 5 in the input. The *length* is right (4, e.g. `[3, 4, 5, 9]`), but the contents of `tails` mix different subsequences. To reconstruct, store for each element the index of the element before it in the subsequence (the tail at position k − 1 when it was placed).

**Non-strict** (non-decreasing) LIS: use `bisect_right` instead, so equal elements extend rather than replace. With `bisect_left`, `[2, 2, 2]` gives 1; with `bisect_right` it gives 3.

## Real-world use

- **LIS** underlies patience diff (used by Bazaar and available in Git as `git diff --patience`), which matches unique lines between files and keeps a longest increasing subsequence of unique-line matches, not necessarily an unbroken run.

## Key takeaways
- Sorted minimum tails allow binary search for each new value.
- Replacing a tail improves future extension opportunities without changing that length.
- The tails array need not itself be an input subsequence.

## Further reading
- [Python bisect](https://docs.python.org/3/library/bisect.html)
- [Longest increasing subsequence](https://cp-algorithms.com/sequences/longest_increasing_subsequence.html)
