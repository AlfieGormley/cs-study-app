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

For example, a length-two block starting at index three in `[5, 2, 4, 7, 1, 3, 6, 8]` covers seven and one. Its minimum is one, obtained by combining the two length-one entries. Larger blocks apply the same rule to their adjacent halves.

The code builds rows in increasing block length, using the completed preceding row:

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

There is one row per power-of-two block length that fits, and at most n entries in each row. Build time and storage are O(n log n). This extra memory buys constant-time minimum queries on unchanged data; Python object overhead can be substantial.

The eight-element example has four rows and twenty-one entries. Rows get shorter as block length grows because only fitting start positions are stored.

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
- [Sparse tables — cp-algorithms](https://cp-algorithms.com/data_structures/sparse-table.html)
