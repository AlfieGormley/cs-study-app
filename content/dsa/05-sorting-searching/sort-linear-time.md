---
id: sort-linear-time
title: Linear-time sorts
level: intermediate
minutes: 13
summary: Counting sort, radix sort and bucket sort escape the n log n bound by using keys as indices; here is how they work, what they really cost, and when they apply.
---

The last lesson proved that any sort which only *compares* elements needs Ω(n log n) comparisons. The way around that is to stop comparing. If keys are small integers, or can be broken into small integer digits, you can use them directly as **array indices**. An index lookup answers "which of k buckets does this go in?" in one step, which is far more information than a yes/no comparison.

That is the whole trick behind counting sort, radix sort and bucket sort. The catch is that they only work when the keys have the right shape.

## Counting sort

**Assumption:** keys are integers in a known range `0..k−1`.

Count how many times each key occurs, then use running totals to work out where each key's block starts in the output.

```python
def counting_sort(a, key, k):
    count = [0] * k
    for x in a:
        count[key(x)] += 1
    # prefix sums: end of each key's slot
    for v in range(1, k):
        count[v] += count[v - 1]
    out = [None] * len(a)
    for x in reversed(a):  # keeps it stable
        count[key(x)] -= 1
        out[count[key(x)]] = x
    return out
```

Trace on `[2, 5, 3, 0, 2, 3, 0, 3]` with k = 6:

```
value:   0  1  2  3  4  5
count:   2  0  2  3  0  1
prefix:  2  2  4  7  7  8
```

The prefix sum says "values ≤ 3 occupy the first 7 slots", so the last 3 goes in slot 6, the next 3 in slot 5, and so on. Output: `[0, 0, 2, 2, 3, 3, 3, 5]`.

- **Time:** O(n + k): one pass to count, one over the k counters, one to place.
- **Space:** O(n + k) for the output and counts.
- **Stable**, because the final pass walks the input **backwards** and fills each block from its end. Walk forwards while decrementing and equal keys come out reversed. Stability is not a nicety here: radix sort depends on it.

If you are sorting bare integers (no attached data), you can skip the output array and just write each value `count[v]` times. The prefix-sum version is needed when the key is attached to a record.

### When counting sort works and when it does not

- Exam scores 0 to 100 for 2 million students: k = 101, n = 2,000,000. Linear and very fast.
- Ages, HTTP status codes, bytes (k = 256), days of the year: all good fits.
- 1,000 arbitrary 32-bit integers: k = 2³² ≈ 4.3 billion. With 4-byte counters the counts alone need 16 GiB (about 17.2 GB); Python lists have different, larger overhead. Hopeless.

The rule: counting sort is great when **k is O(n)** or smaller. When k is much larger than n, use radix sort.

## Radix sort

**Idea:** break each key into digits and sort one digit at a time with a stable counting sort.

**LSD (least significant digit) radix sort** starts with the last digit and works left. Sort `[170, 45, 75, 90, 802, 24, 2, 66]` in base 10:

```
ones:  [170, 90, 802, 2, 24, 45, 75, 66]
tens:  [802, 2, 24, 45, 66, 170, 75, 90]
100s:  [2, 24, 45, 66, 75, 90, 170, 802]
```

Look at the tens pass: 802 and 2 both have tens digit 0. The ones pass had already put 802 before 2, and because the sort is stable, they keep that order. Once a pass is done, ties on the current digit are broken by the lower digits, which were sorted earlier. **Without stability, LSD radix sort gives wrong answers.**

```python
def radix_sort(a, base=256):
    if type(base) is not int or base < 2:
        raise ValueError("base >= 2")
    if any(type(x) is not int or x < 0
           for x in a):
        raise ValueError("nonnegative ints")
    if not a:
        return a
    exp = 1
    while max(a) // exp > 0:
        digit = lambda x: (x // exp) % base
        a = counting_sort(a, digit, base)
        exp *= base
    return a
```

### What radix sort really costs

With d digits in base b, each pass is a counting sort costing O(n + b):

```
T = O(d · (n + b))
```

For 32-bit unsigned integers with base 256 (one byte per digit): d = 4, b = 256. Four passes over the data, each with a 256-entry count table that fits in L1 cache. For n = 10 million, that is 40 million output placements across the digit passes, plus counting reads and other overhead, versus roughly 230 million comparisons for an n log n sort.

> [!warning] Radix sort depends on key width
> The bound is O(d(n + b)) under constant-cost digit operations. Distinct keys require d ≥ ceil(log_b n), but that lower bound on d does not imply an upper bound: keys can be much wider. Fixed 32- or 64-bit keys give a fixed number of passes, with at most 2^32 or 2^64 distinct values. Python arbitrary-size integer division has its own bit cost.

Choosing the base is a trade-off. Base 2¹⁶ means 2 passes for 32-bit keys, but clearing 65,536 counters costs more and the table may exceed the target CPU cache. Base 2⁸ uses a smaller table. The best base depends on counter representation, hardware and workload.

### MSD radix sort and strings

**MSD (most significant digit)** radix sort starts from the first digit, splits into buckets, and recurses into each bucket. It suits variable-length strings: you can stop as soon as a bucket has one element, and you never look at characters beyond the distinguishing prefix. Stability depends on the MSD implementation; in-place variants may be unstable. Many implementations switch to insertion sort for small buckets. Sorting strings this way is the basis of suffix array construction and some fast string-sorting libraries.

### Negative numbers and floats

- **Signed integers:** flip the sign bit before sorting (XOR with `0x80000000` for 32-bit), so negatives come first.
- **IEEE-754 floats:** positive floats already sort correctly as unsigned integers. For negatives, flip all the bits; for positives, flip just the sign bit. For non-NaN IEEE binary values this maps numerical order to unsigned-key order. Specify NaN placement and whether -0.0 and +0.0 must be treated as equivalent; simple bit transforms alone do not establish that policy.

## Bucket sort

**Assumption:** keys are roughly **uniformly distributed** over a known range, for example floats in `[0, 1)`.

Create n buckets, each covering an equal slice of the range. Drop each element into its bucket, sort each bucket (with insertion sort), then concatenate.

```python
def bucket_sort(a):  # floats in [0, 1)
    n = len(a)
    buckets = [[] for _ in range(n)]
    for x in a:
        buckets[int(x * n)].append(x)
    out = []
    for b in buckets:
        out.extend(sorted(b))
    return out
```

```
[0.78, 0.17, 0.39, 0.26, 0.72, 0.94]
n=6 buckets, width 1/6 ≈ 0.167
b0: []        b1: [0.17, 0.26]
b2: [0.39]    b3: []
b4: [0.78, 0.72]   b5: [0.94]
sort each, concat:
[0.17, 0.26, 0.39, 0.72, 0.78, 0.94]
```

With independent uniform input, each bucket has expected occupancy one, and the **expected** time is O(n). But it is only as good as the distribution assumption. If all values fall in one interval of width 1/n aligned with a bucket, one bucket receives all n values. Insertion sort there can cost O(n²); the shown Python version uses sorted(), so its worst-case bound is O(n log n). A fixed-width interval such as [0.50, 0.51) spans many buckets when n is large.

Bucket sort ideas show up in **histogram-based** and **sample sort** algorithms: sample the data to choose bucket boundaries that split it evenly. Distributed sorts (MapReduce's TeraSort, Spark's `sortBy`) do exactly this to divide data across machines.

## When to use which

| Situation | Choice |
|---|---|
| Small integer range (k ≲ n) | Counting sort |
| Fixed-width ints, large n | LSD radix sort |
| Strings, variable length | MSD radix sort |
| Uniform real values | Bucket sort |
| Arbitrary comparator | Comparison sort |

In real systems:

- **NumPy:** `np.sort(kind='stable')` is documented as mapping to radix sort for integer data types and to Timsort for others, chosen by dtype. (The default `kind='quicksort'` is actually introsort.)
- **GPUs:** NVIDIA CUB offers radix sorting for supported keys; histogram, scan and scatter operations parallelize well. GPU libraries also support comparison-based sorting.
- **Databases:** some analytic engines radix-sort fixed-width encoded keys (such as normalised sort keys) instead of calling a comparator per pair.

## Pitfalls

1. **Memory.** Counting and LSD radix sorts need an O(n) output buffer plus O(k) or O(b) counters. They are not in place.
2. **Small n.** Passes and buffers can outweigh radix benefits for small inputs. **Content gap:** universal crossover sizes are omitted because they need measurements for a particular implementation, dtype and hardware.
3. **Wide or complex keys.** A composite key (last name, then first name, then date) or a locale-aware string collation requires an appropriate order-preserving encoding; ICU collation keys, for example, are byte sequences that can themselves be radix-sorted. Total key length and encoding cost matter. A comparison sort with a key function is simpler and often fast enough.
4. **Skewed data in bucket sort.** Real data is rarely uniform. Without sampling, buckets can be badly unbalanced.

## Key takeaways
- Linear-time sorts beat the Ω(n log n) bound by using keys as array indices instead of comparing them.
- Counting sort is O(n + k) and stable when placed backwards using prefix sums; it is only practical when the key range k is not much bigger than n.
- LSD radix sort is d passes of a stable counting sort: O(d(n + b)). Stability of each pass is essential.
- Bucket sort is expected O(n) only for roughly uniform input; skew makes it degrade to the inner sort.
- Use them for integers, fixed-width keys and parallel hardware; use comparison sorts for arbitrary orderings.

## Further reading
- [Counting sort — Wikipedia](https://en.wikipedia.org/wiki/Counting_sort)
- [Radix sort — Wikipedia](https://en.wikipedia.org/wiki/Radix_sort)
- [Radix sorts (LSD and MSD) — Algorithms, 4th ed.](https://algs4.cs.princeton.edu/51radix/)
- [Bucket sort — Wikipedia](https://en.wikipedia.org/wiki/Bucket_sort)
- [numpy.sort — NumPy docs](https://numpy.org/doc/stable/reference/generated/numpy.sort.html)
