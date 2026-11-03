---
id: pat-mask-subsets
title: Represent subsets and dynamic-programming states
level: advanced
minutes: 4
sourceLesson: pat-bits
summary: An item-position mask describes one of all possible subsets.
---

Here n is the number of item positions, or the number of cities when explicitly stated. Mask complexity assumes unit-cost word operations; Python arbitrary-precision masks add bit-length costs.

## Bitmasks as subsets

With n items, an integer `mask` ranging from zero through the largest n-bit pattern represents a subset: bit `i` set means item `i` is in. Each item is either in or out, so n items give 2ⁿ subsets, one for each mask. Three items give 8 subsets, masks 0 to 7, and mask 5 (binary 101) means items 0 and 2. The Dynamic Programming module's "Represent a small set with bits" unit uses the same encoding.

This enumerates all subsets of item positions with no recursion (equal item values can therefore produce equal-looking lists). The returned nested lists take Θ(n·2ⁿ) element references for n of at least 1, and enumeration also takes Θ(n·2ⁿ) tests in the unit-cost mask model. Θ (big-Theta) means the cost grows exactly at that rate, up to constant factors: here n bit tests for each of the 2ⁿ masks.

```python
def subsets(items):
    n = len(items)
    out = []
    # Visit every subset of item positions.
    for mask in range(1 << n):
        out.append([items[i]
                    for i in range(n)
                    if mask >> i & 1])
    return out
```

Union is `a | b`, intersection `a & b`, "is `a` a subset of `b`?" is `a & b == a`.

**Bitmask DP** uses the mask as a DP state. The Held–Karp algorithm for the travelling salesman problem stores `dp[mask][last]` = shortest path from a fixed start visiting exactly the cities in `mask`, ending at `last` (add the edge back to the start to complete a tour). Its work grows as O(2ⁿ · n²), where n is the number of cities: 2ⁿ subsets, times n choices of last city, times n choices of the city before it. Trying every tour order instead grows factorially.

The difference is large, but neither is polynomial: the DP grows exponentially and the order count factorially, which is faster still. For 20 cities, the subset DP's growth figure is about 420 million, while the orders from a fixed start number about 120 million billion. Going from 20 to 21 cities multiplies the DP's figure by about 2.2 but the number of orders by 20. The Dynamic Programming module's "A visited-set state for travelling salesman" unit develops the recurrence.

## Key takeaways
- An item-position mask describes one of all possible subsets.
- Materialising all subsets counts both bit tests and returned element references.
- Held–Karp also stores an endpoint and closes the tour back to its fixed start.

## Further reading
- [Bit manipulation — cp-algorithms](https://cp-algorithms.com/algebra/bit-manipulation.html)
- [Enumerating submasks — cp-algorithms](https://cp-algorithms.com/algebra/all-submasks.html)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford (archived copy)](https://web.archive.org/web/20250605031917/https://graphics.stanford.edu/~seander/bithacks.html)
- [Hamming weight — Wikipedia](https://en.wikipedia.org/wiki/Hamming_weight)
- [Binary cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/binary/)
