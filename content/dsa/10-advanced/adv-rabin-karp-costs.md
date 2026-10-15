---
id: adv-rabin-karp-costs
title: Hash candidates, prefix fingerprints and modulo
level: advanced
minutes: 3
summary: Candidate verification adds a cost per matching window, including genuine matches.
sourceLesson: adv-string-algorithms
---

Here n is the text or indexed-string length, m is the pattern length, and positions count from zero. Costs count constant-time character and word operations unless noted.

## Candidate verification and substring fingerprints

Equal strings always have equal hashes, but different strings can produce a **hash collision**. So a hash match is only a candidate, confirmed by a direct comparison. For this implementation the time is:

```formula
T = O(n + m + mC)
C_max = n − m + 1
T = Θ(nm)   if C = C_max and m ≤ n / 2
mC ≈ 3 × 10^6
where
T: the running time of `rabin_karp`
n: the length of the text, in characters
m: the length of the pattern, in characters
C: the number of windows whose hash equals the pattern's hash, including genuine matches; each costs at most linear slicing/equality work in m. Proper candidate slices copy m characters in CPython; equality may reject early, and a whole-string slice may reuse the original object
C_max: the most candidates possible: one per window position, for a non-empty pattern no longer than the text
≤: is at most
≈: approximately equal to
O(f): grows at most in proportion to f
Θ(f): grows exactly in proportion to f, up to constant factors
In words: hashing is linear, but each candidate performs a slice/equality check that may cost work proportional to m, so many candidates make the algorithm as slow as naive matching.
```

The last line is a worked example: searching `aaa` (a 3-character pattern) in a million `a`s gives about a million genuine matches, so the checks alone cost about three million comparisons. Repeated text and pattern characters can require Θ(nm) verification even without collisions when the pattern is at most half the text length. When the pattern nearly fills the text, use the actual candidate count instead. Linear expected time needs assumptions controlling false positives and genuine matches.

> [!note] Content gap: collision probabilities
> No numeric collision probability is provided for the fixed public B and M above: a prime modulus alone does not justify a 1/M probability for arbitrary inputs.

## Porting negative remainders

- **Negative modulo**: in C or Java, `(h - x) % M` can be negative. For positive M, Python's `%` returns a non-negative result, which hides this bug until you port the code. For this fixed modulus near one billion, a sufficiently wide integer type can safely add the modulus before reducing again. For arbitrary fixed-width values, the intermediate addition must also avoid overflow:

```formula
r = ((a mod M) + M) mod M
r_C = (3 − 10) mod 11 = −7
r = (−7 + 11) mod 11 = 4
where
a: the number being reduced, possibly negative after a subtraction such as h − x
M: the positive modulus, 11 in the example
mod: the remainder after dividing by M; in C and Java it takes the sign of a, so it can be negative
r: the result, always between 0 and M − 1
r_C: the result C or Java's `%` gives for the example, which is negative
In words: if the remainder comes out negative, adding M once moves it into the range 0 to M − 1 without changing which remainder class it is in.
```

Both −7 and 4 leave the same remainder class (they differ by exactly 11), but only 4 equals a correctly computed hash.

## Key takeaways

- Candidate verification adds a cost per matching window, including genuine matches.
- Normalise negative remainders so equivalent hashes compare equal when porting.

## Further reading
- [Prefix function and Knuth–Morris–Pratt — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Rabin–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
- [Suffix Array — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix array — Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
