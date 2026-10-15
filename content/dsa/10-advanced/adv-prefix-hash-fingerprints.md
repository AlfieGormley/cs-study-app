---
id: adv-prefix-hash-fingerprints
title: Prefix fingerprints and rolling-hash applications
level: advanced
minutes: 3
summary: Extract substring fingerprints from two prefix hashes and understand their collision limits.
sourceLesson: adv-string-algorithms
---

Here n is the string length and k is the number of patterns. Hash values are fingerprints, so exact equality still needs verification.

Rabin–Karp's real strengths are elsewhere:

- Many patterns at once: group k equal-length patterns by hash and look up each window in expected O(1), plus verification of candidate patterns.
- Substring equality in O(1): with prefix hashes of a string of length n, any two substrings' fingerprints can be compared after O(n) set-up (formula below). This is probabilistic equality unless verified. Hashing and binary search can give an expected O(n log n) Monte Carlo longest-repeated-substring algorithm under an appropriate random-hash model; collision checks add costs.
- **Content-defined chunking**: backup tools such as restic use rolling fingerprints to choose boundaries. Rsync instead searches at every offset for matches to fixed-size blocks of the basis file.

The prefix-hash trick stores the hash of every prefix, then cuts any substring's hash out of two of them:

```formula
H[0] = 0
H[j + 1] = (H[j] × B + s_j) mod M
h(s[i..j)) = (H[j] − H[i] × B^{j−i}) mod M
h(s[1..4)) = 5123 − 5 × 10^3 = 123
where
s: the string, with characters numbered from 0
s_j: the character code at position j
H[j]: the hash of the first j characters of s
i, j: the start (included) and end (excluded) positions of a substring
s[i..j): the substring from position i up to but not including j
B: the base
B^{j−i}: j − i copies of B multiplied together (precomputed for every power)
M: the prime modulus
mod: the remainder after dividing by M, taken as 0 to M − 1
h: the hash of the substring
In words: a substring's hash is the longer prefix's hash minus the shorter prefix's hash shifted up by the substring's length.
```

The last line is a toy example with base ten, digits as characters and a modulus large enough to ignore: for the string `5123`, the prefix hashes are 5 (first character) and 5123 (all four), so the substring `123` hashes to 123, exactly what hashing it directly gives. Each comparison is O(1) once the H array and powers of B are precomputed in O(n).

> [!warning] Hash collisions can be attacked
> With a fixed, public B and M, an adversary can build inputs that collide on purpose. Randomised fingerprints can reduce collision risk under a stated model, but fixed double hashing is not an adversarial guarantee. Verify candidates; use KMP or Z when deterministic linear bounds matter.

## Key takeaways

- Shift the shorter prefix hash by the substring length before subtracting it.
- Fingerprint equality is probabilistic under a stated hash model and is not an adversarial guarantee.

## Further reading
- [Prefix function and Knuth–Morris–Pratt — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Rabin–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
- [Suffix Array — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix array — Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
