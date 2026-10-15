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

With n items, an integer `mask` ranging from zero through the largest n-bit pattern represents a subset: bit `i` set means item `i` is in.

```formula
N_sub = 2^n
0 ≤ mask ≤ 2^n − 1
N_sub = 2^3 = 8
where
N_sub: the number of subsets of n items
n: the number of items
mask: an integer whose bit i says whether item i is in the subset
≤: "is less than or equal to"
In words: each item is either in or out, two choices per item, so n items give 2^n subsets, numbered by the integers 0 to 2^n − 1; 3 items give 8 subsets, masks 0 to 7, and mask 5 = 101 in binary means items 0 and 2.
```

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

**Bitmask DP** uses the mask as a DP state. The Held–Karp algorithm for the travelling salesman problem stores `dp[mask][last]` = shortest path from a fixed start visiting exactly the cities in `mask`, ending at `last` (add the edge back to the start to complete a tour): O(2ⁿ · n²) time instead of O(n!), where n is the number of cities:

```formula
W_HK = 2^n n^2
W_HK = 2^20 × 20^2 ≈ 4.2 × 10^8
(n − 1)! = 19! ≈ 1.2 × 10^17
where
W_HK: the upper-work expression for Held–Karp: 2^n subsets, times n choices of last city, times n choices of the city before it
n: the number of cities; here 20
2^n: the number of subsets of the n cities
n^2: n squared, n × n
(n − 1)!: the number of tour orders with a fixed start city, (n − 1) × (n − 2) × … × 1
!: factorial, the product of all whole numbers from 1 up to the given one
…: "and so on", continuing the pattern
≈: approximately equal to
In words: for 20 cities, dynamic programming over subsets faces about 420 million units of work, while trying every tour order from a fixed start faces about 120 million billion.
```

The 4.2 × 10⁸ figure is an upper-work expression, not an exact transition count.

> [!note] Content gap
> A C++ promise that this runs in time and a universal practical size limit are omitted because no implementation, hardware, deadline or benchmark supports them.

## Key takeaways
- An item-position mask describes one of all possible subsets.
- Materialising all subsets counts both bit tests and returned element references.
- Held–Karp also stores an endpoint and closes the tour back to its fixed start.

## Further reading
- [Bit manipulation — cp-algorithms](https://cp-algorithms.com/algebra/bit-manipulation.html)
- [Enumerating submasks — cp-algorithms](https://cp-algorithms.com/algebra/all-submasks.html)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford](https://graphics.stanford.edu/~seander/bithacks.html)
- [Hamming weight — Wikipedia](https://en.wikipedia.org/wiki/Hamming_weight)
- [Binary cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/binary/)
