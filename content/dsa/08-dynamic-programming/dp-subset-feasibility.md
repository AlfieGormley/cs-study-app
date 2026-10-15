---
id: dp-subset-feasibility
title: Subset sum, counts and bitsets
level: intermediate
minutes: 2
summary: A Boolean table records exactly reachable sums.
sourceLesson: dp-knapsack
---

Knapsack can ask whether a total is possible rather than what its best value is. Each input position remains available at most once, including repeated equal values.

## Subset sum

> For nonnegative integer `nums` and target T, is there a subset of positions that sums exactly to T?

It's 0/1 knapsack where each item's value equals its weight and we only ask about feasibility.

```python
def subset_sum(nums, T):
    nums = tuple(nums)
    if (type(T) is not int or T < 0
            or any(type(x) is not int
                   or x < 0 for x in nums)):
        raise ValueError("nonnegative sums")
    # The empty subset reaches exactly zero.
    can = [True] + [False] * T
    for x in nums:
        # Each position contributes at most
        # once.
        for s in range(T, x - 1, -1):
            can[s] = can[s] or can[s - x]
    return can[T]
```

`subset_sum([3, 34, 4, 12, 5, 2], 9)` is True (4 + 5). For target 30 it is `False`.

Variants change only the combiner:

- **Count** subsets summing to T: `cnt[s] += cnt[s - x]`, with `cnt[0] = 1`.
- **Minimum items** to reach T: `+∞` sentinel value and `min(..., dp[s - x] + 1)`.

> [!tip] Bitset trick
> A Python integer can encode reachable sums. Start with `mask = 1` and `limit = (1 << (T + 1)) - 1`; for each nonnegative input not exceeding the target, update `mask = (mask | (mask << x)) & limit`. Skip inputs greater than the target, then test `(mask >> T) & 1`. Masking bounds retained and temporary lengths by O(T + 1) bits. Without masking, storage instead grows with the sum of all inputs. Packed word operations can improve constants, but a shift is not constant-time on arbitrary-size integers.
>
> Content gap: fixed 64× or Python speedup claims are omitted because no pinned benchmark supports them.

## Key takeaways
- A Boolean table records exactly reachable sums.
- Descending sums keep each position available at most once.
- Bitsets pack reachability, but arbitrary-sized shifts still cost work.

## Further reading
- [Knapsack recurrences](https://cp-algorithms.com/dynamic_programming/knapsack.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
