---
id: hash-function-rolling-collisions
title: Rolling string hashes and collision risk
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: A rolling hash updates a sliding window in constant time, and the birthday paradox makes collisions appear far sooner than the hash range suggests.
---

A rolling hash slides a fixed-length window along a string and updates the window's hash in a few arithmetic steps, instead of rehashing every character. That makes hash-based substring search fast, but it also raises a question this lesson answers: how soon do different strings start sharing a hash?

## Rolling a fixed-length window

Think of decimal digits first. Slide a three-digit window along 12345: going from 123 to 234, you remove the leading 1 (worth 100), shift what is left up one place (23 becomes 230) and add the new digit 4. You never re-read the 2 or the 3.

A polynomial hash rolls the same way, in base p instead of base 10. Remove the outgoing character's contribution, multiply by the base to shift every remaining character up one power, and add the incoming character with weight 1:

```formula essential
h_new = (h_old − c_out p^(n − 1)) × p + c_in
where
h_new: the hash of the window after sliding one place right
h_old: the hash of the window before sliding
c_out: the code of the character leaving on the left
c_in: the code of the character entering on the right
p: the base, such as 31
n: the window length in characters; p^(n − 1) is the weight the leaving character carried
^: "to the power of"
In words: subtract the leaving character's weighted contribution, shift everything up one power of the base, then add the arriving character. With base 31, "abc" (hash 96,354) rolls to "bcd" (hash 97,347).
```

With a modulus M, every step is also reduced mod M (adding M first if the subtraction went negative). With fixed-width arithmetic and the outgoing weight p^(n − 1) computed once in advance, each slide costs O(1), however long the window. That is the idea behind the Rabin–Karp substring search, which compares a pattern's hash with every window of a text in expected linear time and checks the real characters only when hashes match.

## How soon do collisions appear?

> [!warning] Small moduli collide sooner than you think
> With a modulus around 10⁹, 100,000 distinct strings almost certainly contain a pair with the same hash (about a 99% chance). If you compare strings by hash alone, use a 64-bit modulus or two independent hashes, and confirm matches with a real comparison.

The reason is the **birthday paradox**: what matters is the number of *pairs* of strings, which grows with the square of the number of strings. Collisions therefore appear long before the hash values run out: the chance of at least one shared hash reaches about 50% at only about 1.18 times the square root of the number of possible hashes (around 37,000 strings for a 10⁹-sized modulus).

```formula reference
P ≈ 1 − e^(−n^2 / (2M))
where
P: the probability that at least two of the strings share a hash, from 0 (never) to 1 (certain)
n: the number of distinct strings hashed
M: the number of possible hash values (the modulus)
e: Euler's number, about 2.718
^: "to the power of"
≈: approximately equal to; the approximation is good when n is much smaller than M
In words: the collision chance depends on the square of the number of strings compared with the size of the hash space, so it rises steeply long before the number of strings gets anywhere near the number of possible hashes.
```

This treats each string's hash as an independent, uniformly random value. Real hashes are not perfectly random, and patterned or deliberately chosen inputs can do worse.

## Key takeaways
- A rolling update removes the outgoing weight, shifts remaining weights and adds the incoming code.
- Constant update cost assumes fixed-width arithmetic and a precomputed outgoing weight.
- Collision risk grows with the number of pairs; confirm matching hashes with real comparisons.

## Further reading
- [String hashing — cp-algorithms](https://cp-algorithms.com/string/string-hashing.html)
