---
id: pat-prefix-sums
title: Prefix sums and difference arrays
level: intermediate
minutes: 13
summary: Precomputing running totals to answer range sums in O(1), counting subarrays that sum to k with a hash map, applying range updates with difference arrays, and extending it all to 2-D grids.
---

If you'll ask "what's the sum of `a[l..r]`?" many times, adding up the range each time costs O(n) per query. A **prefix sum** array costs O(n) once and then answers every range query in O(1).

The idea underpins far more than range queries: subarray-sum counting, difference arrays for batched updates, 2-D image integrals and cumulative frequency tables all reuse it.

Examples use exact integer arithmetic. The O(1) arithmetic/hash model assumes values fit the chosen word size; Python arbitrary-precision costs grow with bit length. Floating-point prefix subtraction can lose accuracy through rounding and cancellation.

## The prefix array

Define `P[0] = 0` and `P[i + 1] = P[i] + a[i]`. So `P[i]` is the sum of the first `i` elements.

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

Sum of `a[1..3]` = `P[4] − P[1]` = 9 − 3 = 6 = 1 + 4 + 1. The leading zero is what makes ranges starting at index 0 work without a special case: `a[0..2]` = `P[3] − P[0]` = 8.

> [!tip] Off-by-one insurance
> Use the length-`n + 1` array with `P[0] = 0`. Think of `P[i]` as the sum of the elements *before* index `i`. Then "sum of `a[l..r]`" is always "everything before `r + 1` minus everything before `l`".

Python provides these values as an iterator: `itertools.accumulate(a, initial=0)`. Materialise it with `list(...)` for indexed range queries.

## Subarray sum equals k

**Problem.** Count the nonempty contiguous subarrays whose sum is exactly `k`. Values may be negative.

A sliding window fails because of the negatives (lesson 3). Prefix sums turn the question around:

```
sum(a[i..j]) == k
P[j + 1] - P[i] == k
P[i] == P[j + 1] - k
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
| Count sum = k | prefix → count |
| Longest sum = k | prefix → first index |
| Sum divisible by positive k | prefix % k → count |
| Equal 0s and 1s | map 0→−1, find sum 0 |

For "longest", seed `first = {0: -1}` and store the *first ending index* at which each running total appears (do not overwrite it). At ending index `j`, a match gives length `j − first[run − k]`.

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

Each update is O(1); one prefix-sum pass at the end rebuilds the array. Total O(n + u) for u updates instead of O(n·u).

```
n = 5, updates (1,3,+2), (0,1,+5), (2,4,-1)

d after:  [5, 2, -6, 0, -2, 1]
          (index 5 is the spill slot)
prefix:   [5, 7, 1, 1, -1]
```

Check index 2: covered by `+2` and `-1`, so 1. Correct.

> [!example] Where you see this
> "Car pooling" (can a car of capacity C take every trip?) and "flight bookings" are difference arrays over time or flight number. For positive-duration half-open bookings `[start,end)`, mark +1 at the start and −1 at the end, then sweep. Inclusive discrete ranges instead cancel just after the last included index. Lesson 6 calls this a **sweep line**.

The efficient batch use applies updates before rebuilding the values. Interleaved queries are possible but a plain difference array may need O(n) work per read. A Fenwick tree over differences supports range-add/point-query in O(log n); two Fenwick trees or an appropriately lazy segment tree support range-add/range-sum.

## 2-D prefix sums

For a grid, let `P[r][c]` be the sum of the rectangle from `(0, 0)` up to but not including row `r` and column `c`. Build it with inclusion–exclusion:

```
P[r+1][c+1] = g[r][c]
            + P[r][c+1]   (above)
            + P[r+1][c]   (left)
            - P[r][c]     (counted twice)
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

the rectangle rows 1–2, columns 1–2 is 6 + 3 + 2 + 0 = 11, from four lookups.

This is the **summed-area table** from computer graphics, introduced for texture mapping in 1984. The Viola–Jones face detector used it (as the "integral image") to evaluate rectangular features in constant time, which helped make real-time face detection practical in the early 2000s.

## Recognising the pattern

- Many **range-sum queries** on a static array or grid.
- "Subarray sum **equals** / is **divisible by** k", especially with negatives.
- "Equal number of X and Y in a subarray" (map one to −1, look for sum 0).
- Many **range updates** followed by reads: difference array.
- Products work too (prefix products, or "product of array except self" with prefix and suffix passes), but watch out for zeros.

## Pitfalls

- **Forgetting `P[0] = 0`** (or `seen = {0: 1}`): misses ranges that start at index 0.
- **Overflow** in fixed-width languages: prefix sums of 10⁵ values up to 10⁹ reach 10¹⁴; use 64-bit integers. (Python integers grow as needed, subject to available memory.)
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
