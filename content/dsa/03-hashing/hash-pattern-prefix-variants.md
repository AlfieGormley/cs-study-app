---
id: hash-pattern-prefix-variants
title: Prefix-sum indices and remainder keys
level: intermediate
minutes: 3
sourceLesson: hash-patterns
summary: The previous unit counted earlier prefix totals.
---

The previous unit counted earlier prefix totals. For a longest range, store the earliest index instead; for divisibility, store a normalised remainder. Choose the map’s values and keys from the requested answer.

## Prefix-sum variants

Variants:

- **Longest subarray with sum k**: store the *first* index at which each prefix sum appears, and maximise `j - first[p - k]`.
- **Subarray sum divisible by k**: for nonzero k, key on `p % k` (the remainder, written mod below); two prefixes with equal remainders bound a divisible subarray.
- **Equal numbers of 0s and 1s**: map 0 to −1, then look for subarrays with sum 0.

The divisible-by-k variant rests on one fact about remainders:

```formula
(P[j] − P[i]) mod k = 0
⇔ P[j] mod k = P[i] mod k
(13 − 3) mod 5 = 10 mod 5 = 0
13 mod 5 = 3 mod 5 = 3
where
P[j]: the prefix sum of the first j elements
P[i]: an earlier prefix sum, i < j
k: the positive divisor, here 5; normalise a negative input divisor to its magnitude
mod: "modulo", the remainder after division, taken from 0 to k − 1
⇔: "exactly when", the statements on either side are both true or both false
In words: a difference is divisible by k exactly when the two numbers leave the same remainder; prefix sums 13 and 3 both leave 3 when divided by 5, so the stretch between them sums to 10, a multiple of 5.
```

So count, for each remainder, how many earlier prefixes had it. (Some languages return negative remainders for negative numbers, so normalise them first.)

> [!warning] Why not a sliding window?
> The usual sum-based two-pointer rule relies on monotonicity, as with nonnegative inputs. Counting all matching windows also needs care with zeros. Arbitrary mixed signs break that monotonicity; prefix sums with a map handle them.

## The map must match the objective

Counting ranges needs a frequency per earlier prefix. Finding the longest range needs the earliest index per earlier prefix, because an earlier starting boundary gives a longer candidate. Overwriting that index loses a valid longer answer. These are two different loop invariants even though both use a hash map.

For the index-based variant, the empty prefix is recorded before index zero at minus one. For the boundary-based notation used in the formulas, the empty prefix is boundary zero. Both conventions work, but mixing them creates an off-by-one error.

For divisibility, use a positive divisor. If a caller supplies a negative divisor, normalise it to its magnitude before using the zero-to-divisor-minus-one remainder interpretation. In Java, Math.floorMod gives consistent nonnegative keys for a positive divisor; plain remainder can keep the dividend’s negative sign. Prefix sums may also need a wider integer type to avoid overflow.

The no-repeated-character problem is a different map pattern: it tracks characters currently in a window, not running numeric sums. Top-frequency queries count whole-input occurrences rather than contiguous ranges. These distinctions explain the distractors in the practice question.

## Key takeaways
- Counting needs frequencies; longest-range queries need earliest indices.
- Divisible ranges use equal normalised remainder keys.
- Keep boundary-based and inclusive-index conventions consistent.

## Further reading
- [Prefix sum — Wikipedia](https://en.wikipedia.org/wiki/Prefix_sum)
