---
id: pat-prefix-variants
title: Use first indices and normalised remainders
level: intermediate
minutes: 3
sourceLesson: pat-prefix-sums
summary: Store the first occurrence to maximise the length of a matching subarray.
---

Different prefix problems retain different information: counts for counting, earliest positions for longest ranges, or normalised remainders for divisibility. Here n is the number of elements. The Hash Tables & Hashing module's "Prefix-sum indices and remainder keys" unit introduces these maps; this unit compares them as one pattern.

## Prefix summaries for different questions

The same "complement in a hash map" trick, borrowed from two sum, solves several variations:

| Problem | Store in map |
|---|---|
| Count sum equals k | prefix → count |
| Longest sum equals k | prefix → first index |
| Sum divisible by positive k | prefix % k → count |
| Equal 0s and 1s | map 0→−1, find sum 0 |

## Longest: keep the first index

For "longest", seed `first = {0: -1}` and store the *first* ending index at which each running total appears; never overwrite it. When the running total at index `j` is `run`, a stored entry for `run - k` means a matching subarray starts just after `first[run - k]`, so its length is `j - first[run - k]`. Keeping the earliest index makes that gap as large as possible.

For `a = [1, 2, 3]` with target 3: at index 1 the running total is 3, the needed earlier total is 0, and the empty prefix records 0 at index −1. So `[1, 2]` has length 1 − (−1) = 2.

## Divisible: compare remainders

For a positive modulus, reduce each running prefix sum to its canonical remainder between zero and one less than the modulus. Two prefixes in the same remainder class differ by a multiple of the modulus, so the subarray between them has a divisible sum. Keep a frequency map, seeded with one empty prefix at remainder zero, and look up a remainder before inserting it.

Languages disagree about negative remainders. Python's remainder takes the positive divisor's sign: `-1 % 5 == 4`, which is what you want. In C, C++, Java and JavaScript it takes the dividend's sign, so `-1 % 5 == -1`, and prefixes in the same class can land under different keys. Java provides `Math.floorMod`. With an `int` modulus and `int` input values, widen the sum to `long` before calling it: normalising after an overflowing `int` addition cannot recover the lost value. If you normalise by hand, add the modulus only when the remainder is negative, because adding it unconditionally can itself overflow.

## When the data changes

Prefix sums go stale after an update, and rebuilding them is O(n). If updates are frequent, use a Fenwick tree, which keeps prefix sums current with logarithmic-time updates and queries (Advanced Structures & Algorithms module).

## Key takeaways
- Store the first occurrence to maximise the length of a matching subarray.
- Equal normalised prefix remainders identify sums divisible by a positive modulus.
- Widen before Java addition and normalise remainders consistently.

## Further reading
- [Prefix sums — USACO Guide](https://usaco.guide/silver/prefix-sums)
- [More on prefix sums (2-D, difference arrays) — USACO Guide](https://usaco.guide/silver/more-prefix-sums)
- [Prefix sum — Wikipedia](https://en.wikipedia.org/wiki/Prefix_sum)
- [Summed-area table — Wikipedia](https://en.wikipedia.org/wiki/Summed-area_table)
