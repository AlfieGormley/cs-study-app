---
id: dp-equal-partition
title: Split totals into equal or near-equal groups
level: intermediate
minutes: 3
summary: An equal partition needs an even total and a reachable half-total.
sourceLesson: dp-knapsack
---

Subset sum answers whether a chosen group can reach an exact total. Partition uses that answer to balance two groups without changing the input domain.

## Partition

> Can `nums` be split into two groups with equal sums?

If the total is odd, equal integer sums are impossible. Otherwise use subset sum with half the total as the target: if one group reaches exactly half, the numbers left over make up the other half automatically.

```python
def can_partition(nums):
    nums = tuple(nums)
    if any(type(x) is not int or x < 0
           for x in nums):
        raise ValueError("nonnegative nums")
    # Equal groups must each take half the
    # total.
    S = sum(nums)
    return S % 2 == 0 and \
        subset_sum(nums, S // 2)
```

For `[1, 5, 11, 5]`, the total is 22 and selecting the single 11 reaches half, so the answer is `True`. For `[1, 2, 3, 5]`, the total is odd at 11, so the answer is `False`.

**Minimum difference partition** (split into two groups as evenly as possible): compute every reachable subset sum up to half the total and take the largest one. That group is the smaller side, and the gap is the total minus twice its sum.

For `[1, 5, 11, 5]`, the reachable half-total gives difference zero. For `[1, 2, 3, 5]`, the best smaller group has sum 5 (5 alone, or 2 plus 3); the other group has sum 6, so the difference is 1.

## Key takeaways
- An equal partition needs an even total and a reachable half-total.
- The largest reachable sum at most half the total gives the smallest gap.

## Further reading
- [Knapsack recurrences](https://cp-algorithms.com/dynamic_programming/knapsack.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
