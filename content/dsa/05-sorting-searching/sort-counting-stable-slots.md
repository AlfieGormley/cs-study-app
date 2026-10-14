---
id: sort-counting-stable-slots
title: Counting sort and stable output slots
level: intermediate
minutes: 4
sourceLesson: sort-linear-time
summary: Prefix counts locate each key’s output block.
---

The last lesson proved that any sort which only *compares* elements needs Ω(n log n) comparisons, where n is the number of elements and Ω (Big Omega) means "at least this growth rate, up to a constant factor". The way around that is to stop comparing. If keys are small integers, or can be broken into small integer digits, you can use them directly as **array indices**. An index lookup answers "which of k buckets does this go in?" in one step, which is far more information than a yes/no comparison.

That is the whole trick behind counting sort, radix sort and bucket sort. The catch is that they only work when the keys have the right shape.

## Counting sort

**Assumption:** keys are integers in a known range `0..k−1`: k is the number of possible key values, and n is the number of elements.

Count how many times each key occurs, then use running totals to work out where each key's block starts in the output.

```python
def counting_sort(a, key, k):
    count = [0] * k
    for x in a:
        # Count the frequency of each
        # integer key.
        count[key(x)] += 1
    # prefix sums: end of each key's slot
    for v in range(1, k):
        # Convert frequencies into block
        # endpoints.
        count[v] += count[v - 1]
    out = [None] * len(a)
    for x in reversed(a):  # keeps it stable
        # Fill each block from its last free
        # slot.
        count[key(x)] -= 1
        # Reverse input traversal preserves
        # ties.
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
- 1,000 arbitrary 32-bit integers: about 4.3 billion possible values, so about 4.3 billion counters, whatever n is. The counts alone need 16 GiB (formula below); Python lists have different, larger overhead. Hopeless.

```formula
k = 2^32 ≈ 4.3 × 10^9
M = k × 4 B = 2^34 B
M = 16 GiB ≈ 17.2 GB
where
k: the number of possible key values: a 32-bit integer can take 2^32 values
M: the memory the counter array needs
2^32: 32 copies of 2 multiplied together, 4,294,967,296
B: bytes; each counter here is a 4-byte integer
GiB: gibibyte, 2^30 = 1,073,741,824 bytes
GB: gigabyte, 1,000,000,000 bytes
≈: approximately equal to
In words: one 4-byte counter for each of the 4.3 billion possible values needs 16 GiB, even to sort only 1,000 numbers.
```

The rule: counting sort is great when **k is O(n)** or smaller. When k is much larger than n, use radix sort.

## Key takeaways
- Prefix counts locate each key’s output block.
- Reverse placement preserves ties; the key range controls counter memory.

## Further reading
- [LSD and MSD radix sorting — Princeton Algorithms](https://algs4.cs.princeton.edu/51radix/)
