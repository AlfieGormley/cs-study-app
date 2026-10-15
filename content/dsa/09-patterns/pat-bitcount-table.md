---
id: pat-bitcount-table
title: Reuse smaller bit counts in a dynamic-programming table
level: advanced
minutes: 2
sourceLesson: pat-bits
summary: Dropping the lowest bit reaches an already computed table entry.
---

Here n is a nonnegative integer upper bound. The table stores counts for every value through that bound; arithmetic and indexing use a unit-cost word model.

## Counting bits for 0..n

**Problem.** Return the number of 1 bits in every integer from 0 to n.

Calling a bit-at-a-time or set-bit-clearing routine on every integer through n takes O(n log n) word operations overall; a constant-time native-word popcount changes that comparison. The following DP uses O(n) table operations and O(n) entries: `i >> 1` is `i` with its last bit dropped, and we've already computed it.

```formula
B(i) = B(⌊i / 2⌋) + (i mod 2)
B(7) = B(3) + 1 = 2 + 1 = 3
where
B(i): the number of 1 bits in i (`bits[i]` in the code); B(0) = 0
i: an integer from 1 to n
⌊ ⌋: floor, rounding down; ⌊i / 2⌋ is `i >> 1`
mod: "modulo", the remainder; i mod 2 is the last bit, `i & 1`
In words: i has the same 1 bits as i with its last bit dropped, plus one more if its last bit is 1; 7 is 111, 3 is 11, so 7 has one more 1 bit than 3.
```

```python
def count_bits(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative int")
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        # Reuse the smaller count and add
        # last bit.
        bits[i] = bits[i >> 1] + (i & 1)
    return bits

# count_bits(8)
# [0, 1, 1, 2, 1, 2, 2, 3, 1]
```

The alternative recurrence `bits[i] = bits[i & (i - 1)] + 1` reuses the lowest-bit trick.

## Key takeaways
- Dropping the lowest bit reaches an already computed table entry.
- The last bit adds either zero or one to that smaller count.
- A hardware popcount and a bit-clearing loop have different cost models.

## Further reading
- [Bit manipulation — cp-algorithms](https://cp-algorithms.com/algebra/bit-manipulation.html)
- [Enumerating submasks — cp-algorithms](https://cp-algorithms.com/algebra/all-submasks.html)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford](https://graphics.stanford.edu/~seander/bithacks.html)
- [Hamming weight — Wikipedia](https://en.wikipedia.org/wiki/Hamming_weight)
- [Binary cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/binary/)
