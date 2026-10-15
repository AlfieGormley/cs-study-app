---
id: adv-sparse-static-build
title: Building sparse tables for static ranges
level: advanced
minutes: 5
summary: Store every fitting power-of-two block summary.
sourceLesson: adv-sparse-tables
---

Here n is the array length, tree size or text length specified in the section. Big-O costs assume fixed-size summaries and constant-time word operations. This index assumes a non-empty array and valid inclusive query endpoints.

This unit builds a static range-minimum index from overlapping power-of-two blocks. Later units separately cover historical versions and editable text.

## Range minimum queries

A **range minimum query** (RMQ) asks for the smallest value in `a[l..r]`, the elements from index l to index r inclusive. The options so far, for an array of n elements (O(n²) means growing with n × n):

| Method | Build | Query | Updates |
|---|---|---|---|
| Scan | none | O(n) | O(1) |
| Every range | O(n²) | O(1) | rebuild |
| Segment tree | O(n) | O(log n) | O(log n) |
| Sparse table | O(n log n) | O(1) | rebuild |

The sparse table is the right choice when the array never changes and there are many queries: for example, LCA queries on a fixed tree, or the LCP array of a suffix array.

## The sparse table

Precompute the minimum of every block whose length is a **power of two** (1, 2, 4, 8, …). Each row holds minima for one block length, twice the previous row’s length. Combine two adjacent half-size blocks from the preceding row to obtain each larger block:

```formula
T[0][i] = a[i]
T[k][i] = min(T[k−1][i], T[k−1][i + h])
h = 2^{k−1}
T[1][3] = min(T[0][3], T[0][4])
T[1][3] = min(7, 1) = 1
where
a: the input array, which never changes
a[i]: the element of a at index i, counting from 0
i: the start index of a block
k: the row number; row k holds blocks of length 2^k
2^k: k copies of 2 multiplied together, the block length in row k (2^0 = 1)
T[k][i]: the table entry for row k, index i: the minimum of a[i] through a[i + 2^k − 1]
h: the half-block length, 2 to the power k − 1
min(x, y): the smaller of x and y
In words: the minimum of a block is the smaller of the minima of its left half and its right half, so each row is built from the row below in one pass.
```

The worked lines use the example array below, `a = [5, 2, 4, 7, 1, 3, 6, 8]`: the length-2 block starting at index 3 covers 7 and 1, so its minimum is 1. The recurrence only works for operations where combining two halves gives the answer for the whole, which holds for min.

The code builds row after row (`table` is T, `j` is k and `half` is h):

```python
def build(a):
    n = len(a)
    table = [a[:]]
    j = 1
    while (1 << j) <= n:
        # Combine two adjacent half-size
        # blocks.
        prev = table[-1]
        half = 1 << (j - 1)
        count = n - (1 << j) + 1
        row = [min(prev[i], prev[i + half])
               for i in range(count)]
        table.append(row)
        j += 1
    return table
```

Each row fits as long as its block length is at most n, which fixes how many rows there are and bounds the size:

```formula
R = ⌊log_2(n)⌋ + 1
S ≤ nR
R = ⌊log_2(8)⌋ + 1 = 4
S = 8 + 7 + 5 + 1 = 21 ≤ 32
R = ⌊log_2(10^6)⌋ + 1 = 20
S ≤ 10^6 × 20 = 2 × 10^7
where
n: the number of elements in the array
R: the number of rows in the sparse table
S: the total number of table entries
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
⌊ ⌋: floor: round down to the nearest whole number
≤: is at most
In words: there is one row for each power of two up to n, and each row holds at most n entries, so the table holds at most n times (log_2(n) + 1) entries.
```

The 8-element example below has 4 rows and 21 entries. A million elements need at most 20 million entries, about 80 MB as 4-byte integers (the exact count, about 18.95 million entries, is about 76 MB), and far more as Python objects. So the build is **O(n log n)** time and memory, and that memory is the main limit on how large an array a sparse table suits.

For `a = [5, 2, 4, 7, 1, 3, 6, 8]`:

```
k=0 (len 1): 5 2 4 7 1 3 6 8
k=1 (len 2): 2 2 4 1 1 3 6
k=2 (len 4): 2 1 1 1 1
k=3 (len 8): 1
```

## Key takeaways

- Store every fitting power-of-two block summary.
- Sparse-table preprocessing is worthwhile for many queries on unchanged data.

## Further reading

- [Sparse Table — cp-algorithms](https://cp-algorithms.com/data_structures/sparse-table.html)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
