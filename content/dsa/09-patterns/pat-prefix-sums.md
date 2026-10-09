---
id: pat-prefix-sums
title: Prefix sums and difference arrays
level: intermediate
minutes: 13
summary: Precomputing running totals to answer range sums in O(1), counting subarrays that sum to k with a hash map, applying range updates with difference arrays, and extending it all to 2-D grids.
---

If you'll ask "what's the sum of `a[l..r]`?" many times, adding up the range each time costs O(n) per query. Here `a[l..r]` means the elements from index l to index r, both included, and n is the length of the array. A **prefix sum** array costs O(n) once and then answers every range query in O(1).

The idea underpins far more than range queries: subarray-sum counting, difference arrays for batched updates, 2-D image integrals and cumulative frequency tables all reuse it.

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

So `P[i]` is the sum of the first `i` elements, and P has n + 1 entries.

```
index i:   0  1  2  3  4
a:         3  1  4  1  5
P:      0  3  4  8  9  14
```

```python
def build_prefix(a):
    p = [0] * (len(a) + 1)
    for i, x in enumerate(a):
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

The leading zero, P[0] = 0, is what makes ranges starting at index 0 work without a special case. This relies on subtraction undoing addition exactly, so it holds for integers but only approximately for floating-point numbers, and it does not work for operations like max that can't be undone.

> [!tip] Off-by-one insurance
> Use the length-`n + 1` array with `P[0] = 0`. Think of `P[i]` as the sum of the elements *before* index `i`. Then "sum of `a[l..r]`" is always "everything before `r + 1` minus everything before `l`".

Python provides these values as an iterator: `itertools.accumulate(a, initial=0)`. Materialise it with `list(...)` for indexed range queries.

## Subarray sum equals k

**Problem.** Count the nonempty contiguous subarrays whose sum is exactly `k`. Values may be negative.

A sliding window fails because of the negatives (lesson 3). Prefix sums turn the question around:

```formula
S(i, j) = k
P[j + 1] − P[i] = k
P[i] = P[j + 1] − k
where
S(i, j): the sum of the subarray a[i..j], from index i to index j inclusive
P[m]: the prefix sum, the total of the first m elements (P[0] = 0)
i: the start index of the subarray
j: the end index of the subarray, with i ≤ j
k: the target sum
≤: "is less than or equal to"
In words: a subarray ending at j sums to k exactly when some earlier prefix sum equals the current prefix sum minus k, so you only need to look up one value.
```

So as we scan, for each running total `run`, the number of subarrays ending here with sum `k` equals the number of **earlier** prefix values equal to `run − k`. Keep a hash map counting prefix values seen so far.

```python
def subarray_sum(a, k):
    seen = {0: 1}   # prefix value -> count
    run = count = 0
    for x in a:
        run += x
        count += seen.get(run - k, 0)
        seen[run] = seen.get(run, 0) + 1
    return count
```

Trace for `a = [1, 2, 3]`, `k = 3`:

```
x  run  need run-k  seen before   count
1  1    -2          {0:1}         0
2  3    0           {0:1,1:1}     1
3  6    3           {0,1,3}       2
```

The two subarrays are `[1, 2]` and `[3]`. Expected O(n) time with well-behaved constant-cost hashing, O(n) space.

> [!warning] Why `seen = {0: 1}`?
> It represents the empty prefix `P[0] = 0`. Without it, subarrays that start at index 0 (like `[1, 2]` above, where `run − k = 0`) are never counted.

The same "complement in a hash map" trick, borrowed from two sum, solves several variations:

| Problem | Store in map |
|---|---|
| Count sum equals k | prefix → count |
| Longest sum equals k | prefix → first index |
| Sum divisible by positive k | prefix % k → count |
| Equal 0s and 1s | map 0→−1, find sum 0 |

For "longest", seed `first = {0: -1}` and store the *first ending index* at which each running total appears (do not overwrite it). At ending index `j`, a match gives the length:

```formula
L = j − first[run − k]
L = 1 − first[3 − 3]
L = 1 − (−1) = 2
where
L: the length of the subarray found
j: the index of the current element, where the subarray ends; here 1
first[x]: the first ending index at which the running total was x; first[0] = −1 stands for the empty prefix
run: the running total up to and including index j; here 1 + 2 = 3
k: the target sum; here 3
In words: the subarray starts just after the earliest point where the running total was run − k, so its length is the gap between the two indices. For a = [1, 2, 3] and k = 3, the subarray [1, 2] ending at index 1 has length 2.
```

## Difference arrays: batched range updates

Prefix sums make **range queries** cheap. The inverse trick makes **range updates** cheap.

**Problem.** Start with `n` zeros. Apply many updates "add `v` to every element in `[l, r]`", then report the final array.

Doing each update directly is O(r − l + 1). Instead, record only where each update *starts* and *stops*:

```python
def apply_updates(n, updates):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    d = [0] * (n + 1)
    for l, r, v in updates:  # inclusive
        if (type(l) is not int
                or type(r) is not int
                or not 0 <= l <= r < n):
            raise ValueError("bad range")
        d[l] += v
        d[r + 1] -= v
    out, run = [], 0
    for i in range(n):
        run += d[i]
        out.append(run)
    return out
```

Each update touches two cells of the difference array:

```formula
d[l] = d[l] + v
d[r + 1] = d[r + 1] − v
x[i] = d[0] + d[1] + … + d[i]
where
d: the difference array, n + 1 cells starting at 0; the extra cell at index n catches updates that end at the last element
l: the first index the update covers
r: the last index the update covers (inclusive)
v: the amount added to every element in [l, r]
x[i]: the final value of element i, the prefix sum of d up to i
i: an index from 0 to n − 1
n: the number of elements
…: "and so on", continuing the same pattern
In words: +v at l switches the update on, −v just after r switches it off, and a running total carries the switched-on amounts across the range.
```

Each update is O(1); one prefix-sum pass at the end rebuilds the array. Total O(n + u) for u updates instead of O(n × u).

```
n = 5, updates (1,3,+2), (0,1,+5), (2,4,-1)

d after:  [5, 2, -6, 0, -2, 1]
          (index 5 is the spill slot)
prefix:   [5, 7, 1, 1, -1]
```

Check index 2: covered by `+2` and `-1`, so 1. Correct.

> [!example] Where you see this
> "Car pooling" (can a car with C seats take every trip?) and "flight bookings" are difference arrays over time or flight number. For positive-duration half-open bookings `[start,end)`, mark +1 at the start and −1 at the end, then sweep. Inclusive discrete ranges instead cancel just after the last included index. Lesson 5 calls this a **sweep line**.

The efficient batch use applies updates before rebuilding the values. Interleaved queries are possible but a plain difference array may need O(n) work per read. A Fenwick tree over differences supports range-add/point-query in O(log n); two Fenwick trees or an appropriately lazy segment tree support range-add/range-sum.

## 2-D prefix sums

For a grid, let `P[r][c]` be the sum of the rectangle from `(0, 0)` up to but not including row `r` and column `c`. Build it with inclusion–exclusion:

```formula
P[r+1][c+1] = g[r][c]
  + P[r][c+1]
  + P[r+1][c]
  − P[r][c]
where
P[r][c]: the sum of the rectangle of cells above row r and left of column c (rows 0 to r − 1, columns 0 to c − 1); row 0 and column 0 of P are all zero
g[r][c]: the value in the grid at row r, column c, counting from 0
r: a row index of the grid
c: a column index of the grid
In words: the new corner total is the new cell, plus the rectangle above it, plus the rectangle to its left, minus the top-left rectangle that both of those included.
```

```python
def build_2d(g):
    R = len(g)
    C = len(g[0]) if R else 0
    if any(len(row) != C for row in g):
        raise ValueError("rectangular grid")
    P = [[0] * (C + 1)
         for _ in range(R + 1)]
    for r in range(R):
        for c in range(C):
            P[r+1][c+1] = (
                g[r][c] + P[r][c+1]
                + P[r+1][c] - P[r][c])
    return P

def rect(P, r1, c1, r2, c2):  # inclusive
    # Requires a valid nonempty rectangle.
    return (P[r2+1][c2+1] - P[r1][c2+1]
            - P[r2+1][c1] + P[r1][c1])
```

The query subtracts the strip above and the strip to the left, then adds back the corner that was subtracted twice:

```
  +-----+-------+
  |  D  |   B   |      want = A
  +-----+-------+      total(A+B+C+D)
  |  C  |   A   |      - (B+D) - (C+D)
  +-----+-------+      + D
```

For the grid

```
3 0 1 4
5 6 3 2
1 2 0 1
```

the prefix table is

```
P = 0  0  0  0  0
    0  3  3  4  8
    0  8 14 18 24
    0  9 17 21 28
```

and the rectangle rows 1–2, columns 1–2 (the cells 6, 3, 2, 0) comes from four lookups:

```formula
A = P[r2+1][c2+1] − P[r1][c2+1]
  − P[r2+1][c1] + P[r1][c1]
A = P[3][3] − P[1][3] − P[3][1] + P[1][1]
A = 21 − 4 − 9 + 3 = 11
where
A: the sum of the rectangle from row r1 to row r2 and column c1 to column c2, all inclusive
P[r][c]: the sum of all cells above row r and left of column c
r1: the top row of the rectangle; here 1
r2: the bottom row; here 2
c1: the left column; here 1
c2: the right column; here 2
In words: take everything up to the bottom-right corner, remove the strip above and the strip to the left, then add back the top-left block that was removed twice; 6 + 3 + 2 + 0 = 11 checks it.
```

This is the **summed-area table** from computer graphics, introduced for texture mapping in 1984. The Viola–Jones face detector used it (as the "integral image") to evaluate rectangular features in constant time, which helped make real-time face detection practical in the early 2000s.

## Recognising the pattern

- Many **range-sum queries** on a static array or grid.
- "Subarray sum **equals** / is **divisible by** k", especially with negatives.
- "Equal number of X and Y in a subarray" (map one to −1, look for sum 0).
- Many **range updates** followed by reads: difference array.
- Products work too (prefix products, or "product of array except self" with prefix and suffix passes), but watch out for zeros.

## Pitfalls

- **Forgetting `P[0] = 0`** (or `seen = {0: 1}`): misses ranges that start at index 0.
- **Integer overflow** in fixed-width languages: a prefix sum can be as large as the count times the largest value, which blows past a 32-bit integer:

```formula
P_max = n × v_max
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

- **Negative modulo**: in Python `-1 % 5 == 4`, which is what you want; in C, Java and JavaScript, `-1 % 5 == -1`, for positive k. In fixed-width code, the extra `+ k` can itself overflow: compute `r = x % k`, then add k only if r is negative; ensure the preceding sum fits too. Java also provides `Math.floorMod`.
- **Mutable data**: prefix sums go stale after an update; rebuilding is O(n). Use a Fenwick tree if updates are frequent.

## Key takeaways
- `P[i]` is the sum of elements before index `i`; range sum `a[l..r]` is `P[r+1] − P[l]`.
- "Subarray sum equals k" becomes "count earlier prefixes equal to run − k", O(n) with a hash map and safe with negatives.
- Difference arrays make each range update O(1); one prefix pass recovers the final values.
- 2-D prefix sums answer any rectangle sum in O(1) with inclusion–exclusion.
- For interleaved updates and queries, move to a Fenwick or segment tree.

## Further reading
- [Prefix sums — USACO Guide](https://usaco.guide/silver/prefix-sums)
- [More on prefix sums (2-D, difference arrays) — USACO Guide](https://usaco.guide/silver/more-prefix-sums)
- [Prefix sum — Wikipedia](https://en.wikipedia.org/wiki/Prefix_sum)
- [Summed-area table — Wikipedia](https://en.wikipedia.org/wiki/Summed-area_table)
