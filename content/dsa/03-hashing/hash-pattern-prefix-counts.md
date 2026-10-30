---
id: hash-pattern-prefix-counts
title: Counting subarrays with prefix sums
level: intermediate
minutes: 3
sourceLesson: hash-patterns
summary: A subarray's sum is a difference of running totals, so a map of earlier totals counts matching subarrays in one pass, even with negative values.
---

A map can remember how many earlier running totals would complete the current range. It must store counts, because several different earlier positions can share the same running total.

## 4. Prefix sum plus hash map

> Count the subarrays of `nums` whose sum equals `k`. Values may be negative.

A **prefix sum** is a running total: the sum of the first so-many elements. The sum of any subarray is then the difference of two prefix sums: the total up to its end minus the total before its start. So we want pairs of boundaries, an earlier start and a later end, whose running totals differ by exactly k:

```formula essential
P[j] − P[i] = k
⇒ P[i] = P[j] − k
where
P[j]: the prefix sum, the total of the first j elements of nums (P[0] = 0, the empty prefix)
P[i]: the prefix total at the earlier start boundary
i: the start index of the subarray, counting from 0
j: one past the end index, so the subarray is nums[i] up to nums[j − 1]
k: the target sum
⇒: "which means"; rearranging the first line gives the second
In words: a subarray sums to k exactly when an earlier running total equals the current running total minus k. For nums = [1, 2, 1, −1, 2], the running totals are 0, 1, 3, 4, 3, 5, and 3 − 0 = 3 picks out the subarray [1, 2].
```

> [!analogy] Real-world analogy: milestones on a long walk
> On a long walk you note the distance shown on your pedometer at every landmark. To know how far it is between any two landmarks, you subtract the two readings; you never re-measure the path.
>
> **How it maps:** the readings are prefix sums and a stretch between landmarks is a subarray. Asking "is there an earlier landmark exactly k kilometres back?" is the map lookup for the current total minus k.
>
> **Where it stops:** a pedometer only ever counts up. Prefix sums can go down when values are negative, so the same reading can recur at several landmarks, which is why the map stores how many times each total has appeared.

That is two-sum again, on prefix sums. Walk once, keeping a count of each prefix sum seen so far:

```python
def count_subarrays(nums, k):
    count = p = 0
    seen = {0: 1}  # prefix sum -> times
    for x in nums:
        p += x
        # Count starts ending before this
        # point.
        count += seen.get(p - k, 0)
        # Only then record this ending
        # prefix.
        seen[p] = seen.get(p, 0) + 1
    return count
```

Trace `nums = [1, 2, 1, -1, 2]`, `k = 3`:

```
x   p   need p-3  found  count
1   1   -2        0      0
2   3    0        1      1
1   4    1        1      2
-1  3    0        1      3
2   5    2        0      3
```

The answer is 3: `[1, 2]`, `[2, 1]` and `[1, 2, 1, -1]`.

The **`{0: 1}` seed** represents the empty prefix before the array starts. Without it, subarrays that begin at index 0 (like `[1, 2]`) are missed.

## State the loop invariant

Before processing an element, seen holds counts of all prefix sums that end before that element, including the empty prefix. After updating the running total, the lookup asks how many earlier starting boundaries would make the current ending boundary valid. Only then is the current prefix added to seen.

This order matters for a target of zero. If the current prefix were added before querying, it could match itself and count an empty range as a subarray. Repeated earlier prefixes, however, are real different starting boundaries and must all contribute to the answer. The empty-prefix seed is one such boundary, not an arbitrary special-case count.

An empty input returns zero. Negative values do not break the invariant because it uses equality between prefix sums rather than an assumption that extending a window always increases its sum.

## Key takeaways
- A matching range is the difference between current and earlier prefix totals.
- Seed the empty prefix to count ranges beginning at the first element.
- Query before recording the current prefix to avoid counting an empty range.

## Further reading
- [Prefix sum — Wikipedia](https://en.wikipedia.org/wiki/Prefix_sum)
