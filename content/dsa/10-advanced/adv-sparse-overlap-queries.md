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

```formula
L = r − l + 1
k = ⌊log_2(L)⌋
q = min(T[k][l], T[k][r − 2^k + 1])
L = 6 − 2 + 1 = 5
k = ⌊log_2(5)⌋ = 2
q = min(T[2][2], T[2][3]) = min(1, 1) = 1
where
l: the left end of the query range (an index, inclusive)
r: the right end of the query range (an index, inclusive)
L: the length of the range, in elements
k: the row to use: the largest whole number with 2^k ≤ L
2^k: k copies of 2 multiplied together, the length of each of the two blocks
T[k][i]: the sparse-table entry: the minimum of the length-2^k block starting at index i
q: the answer, the minimum of a[l] through a[r]
log_2(L): the base-2 logarithm of L
⌊ ⌋: floor: round down to the nearest whole number
min(x, y): the smaller of x and y
≤: is at most
In words: pick the biggest power-of-two block that fits in the range, take one starting at the left end and one ending at the right end, and the smaller of their two minima is the range minimum.
```

The worked lines are `query(2, 6)` on the example array: two length-4 blocks, a[2..5] and a[3..6], overlapping at indices 3 to 5:

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

```formula
f(x, x) = x
min(7, 7) = 7
7 + 7 = 14
where
f: the combining operation (min, max, gcd, AND, OR, +, …)
x: any value
min(x, y): the smaller of x and y
In words: an operation is idempotent when applying it to two copies of the same value just gives that value; min is, addition is not.
```

Min, max, gcd (greatest common divisor), bitwise AND and bitwise OR all qualify.

> [!warning] Sums are not idempotent
> Overlapping blocks would double-count the middle for a sum. You can still answer range sums from a sparse table in O(log n), with n the array length, by decomposing the range into **disjoint** power-of-two blocks (like a Fenwick prefix), but a prefix-sum array does that job in O(1) with O(n) memory. A **disjoint sparse table** stores the table differently to give O(1) queries for any associative operation.

In the Python, `bit_length() - 1` computes k, the base-2 logarithm of the range length rounded down: 5 is `101` in binary, 3 bits long, so k is 2. C++ code often uses `__builtin_clz` or precomputes a `log` array.

## Key takeaways

- Two largest-fitting blocks cover any range.
- Overlap requires an associative idempotent combine; summation double-counts.

## Further reading
- [Sparse Table — cp-algorithms](https://cp-algorithms.com/data_structures/sparse-table.html)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
- [Persistent data structure — Wikipedia](https://en.wikipedia.org/wiki/Persistent_data_structure)
- [Rope (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Rope_(data_structure))
- [Text Buffer Reimplementation — VS Code blog](https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation)
