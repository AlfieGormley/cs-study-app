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

Length 4. Here n is the number of input elements. Each costs one binary search on `tails`, plus an amortised O(1) append or O(1) replacement:

```formula
T = O(n log_2(n + 1))
T(10^5) ≈ 10^5 × 17 = 1.7 × 10^6
where
T: an upper bound on the comparison work for lis_fast; the numeric line is a rough full-length binary-search work estimate, not the actual count for a particular input
n: the number of elements in the input array, positive
log_2(n): the base-2 logarithm of n, the number of halvings a binary search needs on n items (about 17 for 100,000)
log: logarithm; the base only changes a constant factor
O(...): Big-O, growing at most in proportion to the expression inside
≈: approximately equal to
In words: n binary searches on a list of at most n items, each taking about log_2(n) comparisons.
```

The memory is O(n) slots for `tails`.

> [!warning] tails is not the LIS
> On `[3, 1, 4, 1, 5, 9, 2, 6]` the final `tails` is `[1, 2, 5, 6]`. That isn't a subsequence at all: the 2 comes *after* the 5 in the input. The *length* is right (4, e.g. `[3, 4, 5, 9]`), but the contents of `tails` mix different subsequences. To reconstruct, store for each element the index of the element before it in the subsequence (the tail at position k − 1 when it was placed).

**Non-strict** (non-decreasing) LIS: use `bisect_right` instead, so equal elements extend rather than replace. With `bisect_left`, `[2, 2, 2]` gives 1; with `bisect_right` it gives 3.

## Real-world use

- **LIS** underlies patience diff (used by Bazaar and available in Git as `git diff --patience`), which matches unique lines between files and keeps a longest increasing subsequence of unique-line matches, not necessarily an unbroken run.

## A return-value pitfall

The LIS can end before the final input position: return the largest ending length, not merely the final entry.

## Key takeaways
- Sorted minimum tails allow binary search for each new value.
- Replacing a tail improves future extension opportunities without changing that length.
- The tails array need not itself be an input subsequence.

## Further reading
- [Python bisect](https://docs.python.org/3/library/bisect.html)
- [Longest increasing subsequence](https://cp-algorithms.com/sequences/longest_increasing_subsequence.html)
