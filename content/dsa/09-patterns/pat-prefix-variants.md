---
id: pat-prefix-variants
title: Use first indices and normalised remainders
level: intermediate
minutes: 3
sourceLesson: pat-prefix-sums
summary: Store the first occurrence to maximise the length of a matching subarray.
---

Different prefix problems retain different information: counts for counting, earliest positions for longest ranges, or normalised remainders for divisibility. Here n is the number of elements.

## Prefix summaries for different questions

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

## Remainder and update caveats

- **Negative modulo**: in Python `-1 % 5 == 4`, which is what you want; in C, Java and JavaScript, `-1 % 5 == -1`, for positive k. In fixed-width code, the extra `+ k` can itself overflow: compute `r = x % k`, then add k only if r is negative; ensure the preceding sum fits too. Java also provides `Math.floorMod`.
- **Mutable data**: prefix sums go stale after an update; rebuilding is O(n). Use a Fenwick tree if updates are frequent.

## Remainder frequencies

For a positive modulus, reduce each running prefix sum to its canonical remainder between zero and one less than the modulus. Two prefixes in the same remainder class differ by a multiple of the modulus, so the subarray between them has divisible sum. Keep a frequency map, seeded with one empty prefix at remainder zero, and look up a remainder before inserting it.

Python’s remainder has the positive divisor’s sign. Java’s remainder follows the dividend’s sign, so a negative running total can produce a negative key for the same class. With positive Java `int` modulus and `int` input values, widen the sum to `long` before `Math.floorMod`; merely normalising after an overflowing `int` addition does not repair that lost value.

## Key takeaways
- Store the first occurrence to maximise the length of a matching subarray.
- Equal normalised prefix remainders identify sums divisible by a positive modulus.
- Widen before Java addition and normalise remainders consistently.

## Further reading
- [Prefix sums — USACO Guide](https://usaco.guide/silver/prefix-sums)
- [More on prefix sums (2-D, difference arrays) — USACO Guide](https://usaco.guide/silver/more-prefix-sums)
- [Prefix sum — Wikipedia](https://en.wikipedia.org/wiki/Prefix_sum)
- [Summed-area table — Wikipedia](https://en.wikipedia.org/wiki/Summed-area_table)
