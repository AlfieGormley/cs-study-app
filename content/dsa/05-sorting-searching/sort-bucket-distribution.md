---
id: sort-bucket-distribution
title: Bucket sort and distribution assumptions
level: intermediate
minutes: 4
sourceLesson: sort-linear-time
summary: Expected bucket performance depends on independent, roughly uniform keys.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Bucket sort

**Assumption:** keys are roughly **uniformly distributed** over a known range, for example floats in `[0, 1)`.

Create n buckets (one per element), each covering an equal slice of the range. Drop each element into its bucket, sort each bucket (with insertion sort), then concatenate. The bucket for a value is found by arithmetic, not comparison: multiply the value by the number of buckets and round down (`int(x * n)` in the code). With 6 buckets, 0.78 goes into bucket 4, which covers 0.667 up to 0.833.

```python
def bucket_sort(a):  # floats in [0, 1)
    n = len(a)
    buckets = [[] for _ in range(n)]
    for x in a:
        # Map the value to its equal-width
        # slice.
        buckets[int(x * n)].append(x)
    out = []
    for b in buckets:
        # Sort within a slice, then
        # concatenate.
        out.extend(sorted(b))
    return out
```

```
[0.78, 0.17, 0.39, 0.26, 0.72, 0.94]
6 buckets, width about 0.167
b0: []        b1: [0.17, 0.26]
b2: [0.39]    b3: []
b4: [0.78, 0.72]   b5: [0.94]
sort each, concat:
[0.17, 0.26, 0.39, 0.72, 0.78, 0.94]
```

With independent uniform input, each bucket has expected occupancy one, and the **expected** time is O(n). But it is only as good as the distribution assumption. If all values fall in one interval whose width is the reciprocal of the bucket count aligned with a bucket, one bucket receives all n values. Insertion sort there can cost O(n²); the shown Python version uses sorted(), so its worst-case bound is O(n log n). A fixed-width interval such as [0.50, 0.51) spans many buckets when n is large.

> [!analogy] Real-world analogy: sorting post by the first letter of the surname
> A village post office sorts letters into 26 wall slots by the first letter of the surname, then tidies each slot by hand. When surnames are spread across the alphabet, every slot holds only a few letters and the tidying is quick. If half the village is called Smith, the S slot overflows and tidying it takes most of the morning.
>
> **How it maps:** the slots are buckets, choosing a slot from the first letter is computing the bucket from the value, tidying a slot is the inner sort, and the Smith problem is skewed data piling into one bucket.
>
> **Where it stops:** a postmaster who knows the village would make more slots for common letters. Plain bucket sort uses equal-width slices fixed in advance; choosing boundaries from a sample of the data is a separate technique (sample sort).

Bucket sort ideas show up in **histogram-based** and **sample sort** algorithms: sample the data to choose bucket boundaries that split it evenly. Distributed sorts (MapReduce's TeraSort, Spark's `sortBy`) do exactly this to divide data across machines.

## When to use which

| Situation | Choice |
|---|---|
| Small integer range (k not much above n) | Counting sort |
| Fixed-width ints, large n | LSD radix sort |
| Strings, variable length | MSD radix sort |
| Uniform real values | Bucket sort |
| Arbitrary comparator | Comparison sort |

In real systems:

- **NumPy:** `np.sort(kind='stable')` picks its algorithm by dtype. The NumPy 1.17 release notes, which introduced it, say radix sort is used for small integer types of **16 bits or less** and Timsort for the remaining types, including 32- and 64-bit integers. (The default `kind='quicksort'` is actually introsort.)
- **GPUs:** NVIDIA CUB offers radix sorting for supported keys; histogram, scan and scatter operations parallelize well. GPU libraries also support comparison-based sorting.
- **Databases:** some analytic engines radix-sort fixed-width encoded keys (such as normalised sort keys) instead of calling a comparator per pair.

## Pitfalls

1. **Memory.** Counting and LSD radix sorts need an O(n) output buffer plus O(k) or O(b) counters. They are not in place.
2. **Small n.** Passes and buffers can outweigh radix benefits for small inputs. There is no universal crossover size: it depends on the implementation, data type and hardware, so measure.
3. **Wide or complex keys.** A composite key (last name, then first name, then date) or a locale-aware string collation requires an appropriate order-preserving encoding; ICU collation keys, for example, are byte sequences that can themselves be radix-sorted. Total key length and encoding cost matter. A comparison sort with a key function is simpler and often fast enough.
4. **Skewed data in bucket sort.** Real data is rarely uniform. Without sampling, buckets can be badly unbalanced.

## Key takeaways
- Expected bucket performance depends on independent, roughly uniform keys.
- Skew shifts work into the inner sort; library algorithms also depend on key type and implementation.

## Further reading
- [LSD and MSD radix sorting — Princeton Algorithms](https://algs4.cs.princeton.edu/51radix/)
- [NumPy sorting contracts](https://numpy.org/doc/stable/reference/generated/numpy.sort.html)
- [NumPy 1.17 historical dtype mapping](https://numpy.org/doc/1.17/release.html)
