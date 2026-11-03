---
id: adv-sparse-overlap-queries
title: Constant-time queries with overlapping blocks
level: advanced
minutes: 4
summary: Two largest-fitting blocks cover any range.
sourceLesson: adv-sparse-tables
---

Here n is the array length, tree size or text length specified in the section. Big-O costs assume fixed-size summaries and constant-time word operations. This index assumes a non-empty array and valid inclusive query endpoints.

### The O(1) query: overlap is fine

Any range can be covered by two blocks of the same power-of-two length: the largest power of two that fits inside the range. One block starts at the left end and one ends at the right end. They may overlap in the middle.

For `query(2, 6)` on the example array, the range contains five elements. The largest fitting power-of-two block has length four. Use indices 2–5 and 3–6; together they cover the requested range, and their overlap is harmless for a minimum.

The two blocks overlap at indices three through five:

```
query(2, 6), length 5, k = 2 (len 4):

index:  0 1 2 3 4 5 6 7
a:      5 2 4 7 1 3 6 8
            [-------]        a[2..5]
              [-------]      a[3..6]
min(1, 1) = 1
```

```python
def query(table, l, r):
    # min of a[l..r], inclusive
    # Choose the largest fitting block size.
    k = (r - l + 1).bit_length() - 1
    return min(table[k][l],
               table[k][r - (1 << k) + 1])
```

Overlap does not matter for min, because counting an element twice does not change a minimum. The overlap query needs an associative combine that is also an **idempotent operation**: combining a value with itself gives the value back.

An associative operation is **idempotent** when combining a value with itself leaves it unchanged. Repeating an overlapping minimum is harmless; repeating a sum counts the shared elements again.

Min, max, gcd (greatest common divisor), bitwise AND and bitwise OR all qualify.

> [!warning] Sums are not idempotent
> Overlapping blocks would double-count the middle for a sum. You can still answer range sums from a sparse table in O(log n), with n the array length, by decomposing the range into **disjoint** power-of-two blocks (like a Fenwick prefix), but a prefix-sum array does that job in O(1) with O(n) memory. A **disjoint sparse table** stores the table differently to give O(1) queries for any associative operation.

In the Python, `bit_length() - 1` computes k, the base-2 logarithm of the range length rounded down: 5 is `101` in binary, 3 bits long, so k is 2. C++ code often uses `__builtin_clz` or precomputes a `log` array.

## Key takeaways

- Two largest-fitting blocks cover any range.
- Overlap requires an associative idempotent combine; summation double-counts.

## Further reading
- [Sparse tables — cp-algorithms](https://cp-algorithms.com/data_structures/sparse-table.html)
