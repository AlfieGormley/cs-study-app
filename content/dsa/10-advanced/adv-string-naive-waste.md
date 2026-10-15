---
id: adv-string-naive-waste
title: Why naive string search repeats work
level: advanced
minutes: 3
summary: Repeated prefixes make naive matching retry the same successful comparisons.
sourceLesson: adv-string-algorithms
---

Here n is the text or indexed-string length, m is the pattern length, and positions count from zero. Costs count constant-time character and word operations unless noted.

The naive way to find a pattern p (length m) in a text t (length n) tries every start position and compares character by character. In the worst case every start position compares the whole pattern:

```formula
C_naive ≤ (n − m + 1)m
T_naive = O(nm)   for 1 ≤ m ≤ n
C_naive ≈ (10^6 − 5 + 1) × 5 ≈ 5 × 10^6
where
C_naive: the number of character comparisons naive matching makes
T_naive: the total naive matching work for a non-empty pattern that fits in the text
n: the length of the text t, in characters
m: the length of the pattern p, in characters
n − m + 1: the number of places the pattern can start inside the text
O(f): "grows at most in proportion to f", ignoring constant factors
≤: is at most
≈: approximately equal to
In words: naive matching can compare up to m characters at each of about n start positions, so its cost grows with the product of the two lengths.
```

The second line is the classic bad case: searching for `aaaab` (five characters) in a million `a`s matches four `a`s and fails on the `b` at every start, about five million comparisons, and finds nothing. When mismatches come early (typical English text), naive matching is much closer to n comparisons.

The algorithms in this lesson avoid that waste in different ways. **KMP** and the **Z-function** reuse previous matches instead of restarting the search at every position. **Rabin–Karp** compares hashes instead of strings. **Suffix arrays** pre-process the text once so that many later queries are fast.

## The waste in naive matching

Suppose we search for `abab` and have matched `aba` before a mismatch:

```
text:    a b a c ...
pattern: a b a b
               ^ mismatch
```

Naive matching slides the pattern one place and starts again from scratch. But we already know the last three text characters were `aba`. The end of what we matched (`a`) is also a start of the pattern, so the next possible match can begin there, with one character already matched. Nothing before it can work.

KMP precomputes, for every prefix of the pattern, exactly this "how much can I keep?" number.

## Key takeaways

- Repeated prefixes make naive matching retry the same successful comparisons.
- A border tells a matcher which already-matched characters it can retain.

## Further reading
- [Prefix function and Knuth–Morris–Pratt — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Rabin–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
- [Suffix Array — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix array — Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
