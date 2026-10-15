---
id: pat-prefix-range
title: Subtract prefixes to answer static range sums
level: intermediate
minutes: 5
sourceLesson: pat-prefix-sums
summary: The padded prefix table starts with zero and totals elements before each position.
---

If you'll ask "what's the sum of `a[l..r]`?" many times, adding up the range each time costs O(n) per query. Here `a[l..r]` means the elements from index l to index r, both included, and n is the length of the array. A **prefix sum** array costs O(n) once and then answers every range query in O(1).

The idea underpins far more than range queries: subarray-sum counting, difference arrays for batched updates, 2-D summed-area tables and cumulative frequency tables all reuse it.

Examples use exact integer arithmetic. The O(1) arithmetic/hash model assumes values fit the chosen word size; Python arbitrary-precision costs grow with bit length. Floating-point prefix subtraction can lose accuracy through rounding and cancellation.

## The prefix array

Build the prefix array one running total at a time:

```formula
P[0] = 0
P[i + 1] = P[i] + a[i]
P[3] = P[2] + a[2] = 4 + 4 = 8
where
P[i]: the prefix sum, the total of the first i elements a[0] to a[i − 1]
a[i]: the element at index i, counting from 0
i: an index from 0 to n − 1
n: the length of the array a
In words: each prefix sum is the previous one plus the next element, starting from 0 for the empty prefix; for a = [3, 1, 4, 1, 5], the first three elements sum to 8.
```

The prefix at an index totals that many earlier elements. The table has one more entry than the input because it includes the empty prefix.

```
index i:   0  1  2  3  4
a:         3  1  4  1  5
P:      0  3  4  8  9  14
```

```python
def build_prefix(a):
    p = [0] * (len(a) + 1)
    for i, x in enumerate(a):
        # The next prefix includes this
        # element.
        p[i + 1] = p[i] + x
    return p

# sum of a[l..r] inclusive:
#   p[r + 1] - p[l]
```

Any range sum is then one subtraction:

```formula
S(l, r) = P[r + 1] − P[l]
S(1, 3) = P[4] − P[1] = 9 − 3 = 6
S(0, 2) = P[3] − P[0] = 8 − 0 = 8
where
S(l, r): the sum of a[l..r], the elements from index l to index r inclusive
P[i]: the prefix sum, the total of the elements before index i
l: the first index of the range
r: the last index of the range, with l ≤ r
≤: "is less than or equal to"
In words: everything before r + 1, minus everything before l, leaves exactly the range; a[1..3] = 1 + 4 + 1 = 6.
```

The leading zero, `P[0] = 0` in the implementation, is what makes ranges starting at index 0 work without a special case. This relies on subtraction undoing addition exactly, so it holds for integers but only approximately for floating-point numbers, and it does not work for operations like max that can't be undone.

> [!tip] Off-by-one insurance
> Use the length-`n + 1` array with `P[0] = 0`. Think of `P[i]` as the sum of the elements *before* index `i`. Then "sum of `a[l..r]`" is always "everything before `r + 1` minus everything before `l`".

Python provides these values as an iterator: `itertools.accumulate(a, initial=0)`. Materialise it with `list(...)` for indexed range queries.

## Integer width and numeric limits

- **Forgetting the leading zero:** misses ranges that start at index 0. In frequency-counting variants, seed `seen = {0: 1}` for the same reason.
- **Integer overflow** in fixed-width languages: a prefix sum can be as large as the count times the largest value, which blows past a 32-bit integer:

```formula
P_max = n v_max
P_max = 10^5 × 10^9 = 10^14
I_32 = 2^31 − 1 ≈ 2.1 × 10^9
I_64 = 2^63 − 1 ≈ 9.2 × 10^18
where
P_max: the largest possible prefix sum
n: the number of values; here 10^5
v_max: the largest possible value; here 10^9
I_32: the largest signed 32-bit integer, 2,147,483,647
I_64: the largest signed 64-bit integer, about 9.2 × 10^18
≈: approximately equal to
In words: 100,000 values of up to a billion can total 100 trillion, far beyond a 32-bit integer but well inside a 64-bit one, so use 64-bit integers. (Python integers grow as needed, subject to available memory.)
```



## Key takeaways
- The padded prefix table starts with zero and totals elements before each position.
- Inclusive range queries subtract the prefix before the left edge from the prefix after the right edge.
- Use a suitable integer width and account for floating-point cancellation.

## Further reading
- [Prefix sums — USACO Guide](https://usaco.guide/silver/prefix-sums)
- [More on prefix sums (2-D, difference arrays) — USACO Guide](https://usaco.guide/silver/more-prefix-sums)
- [Prefix sum — Wikipedia](https://en.wikipedia.org/wiki/Prefix_sum)
- [Summed-area table — Wikipedia](https://en.wikipedia.org/wiki/Summed-area_table)
