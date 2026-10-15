---
id: pat-prefix-count-target
title: Count earlier prefix complements
level: intermediate
minutes: 3
sourceLesson: pat-prefix-sums
summary: Count frequencies of earlier running totals, including one empty prefix.
---

Here n is the array length and k is a target sum. The preceding padded prefix convention represents the empty prefix with total zero.

## Subarray sum equals k

**Problem.** Count the nonempty contiguous subarrays whose sum is exactly `k`. Values may be negative.

A sliding window fails because of the negatives (the sliding-window units). Prefix sums turn the question around:

```formula
S(i, j) = k
P[j + 1] − P[i] = k
P[i] = P[j + 1] − k
where
S(i, j): the sum of the subarray a[i..j], from index i to index j inclusive
P[m]: the prefix sum, the total of the first m elements (P[0] = 0)
i: the start index of the subarray
j: the end index of the subarray, with i ≤ j
k: the target sum
≤: "is less than or equal to"
In words: a subarray ending at j sums to k exactly when some earlier prefix sum equals the current prefix sum minus k, so you only need to look up one value.
```

So as we scan, for each running total `run`, the number of subarrays ending here with sum `k` equals the number of **earlier** prefix values equal to `run − k`. Keep a hash map counting prefix values seen so far.

```python
def subarray_sum(a, k):
    seen = {0: 1}   # prefix value -> count
    run = count = 0
    for x in a:
        run += x
        # Count earlier matching prefix
        # positions.
        count += seen.get(run - k, 0)
        # Insert afterward to exclude empty
        # ranges.
        seen[run] = seen.get(run, 0) + 1
    return count
```

Trace for `a = [1, 2, 3]`, `k = 3`:

```
x  run  need run-k  seen before   count
1  1    -2          {0:1}         0
2  3    0           {0:1,1:1}     1
3  6    3           {0,1,3}       2
```

The two subarrays are `[1, 2]` and `[3]`. Expected O(n) time with well-behaved constant-cost hashing, O(n) space.

> [!warning] Why `seen = {0: 1}`?
> It represents the empty prefix `P[0] = 0`. Without it, subarrays that start at index 0 (like `[1, 2]` above, where the required earlier prefix is zero) are never counted.

## Key takeaways
- Count frequencies of earlier running totals, including one empty prefix.
- Query before inserting the current prefix so empty subarrays are excluded.
- Prefix-frequency counting handles signed values under expected constant-cost hashing.

## Further reading
- [Prefix sums — USACO Guide](https://usaco.guide/silver/prefix-sums)
- [More on prefix sums (2-D, difference arrays) — USACO Guide](https://usaco.guide/silver/more-prefix-sums)
- [Prefix sum — Wikipedia](https://en.wikipedia.org/wiki/Prefix_sum)
- [Summed-area table — Wikipedia](https://en.wikipedia.org/wiki/Summed-area_table)
