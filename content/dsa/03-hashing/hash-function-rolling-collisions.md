---
id: hash-function-rolling-collisions
title: Rolling string hashes and collision risk
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: A rolling hash reuses a previous window hash rather than rescanning every character.
---

A rolling hash reuses a previous window hash rather than rescanning every character. Here the base is 31 and the window contains three characters. The outgoing code is ninety-seven, the incoming code one hundred, and the old hash ninety-six thousand three hundred and fifty-four, corresponding to abc. Fixed-width arithmetic is assumed in the constant-time update claim.

## Rolling a fixed-length window

Polynomial hashes also **roll**: you can slide a fixed-length window along a string, removing the leftmost character and adding a new one with a constant number of arithmetic operations. With fixed-width arithmetic and the outgoing weight precomputed, this is O(1), independent of the window length:

```formula
h_new = (h_old − c_out p^{n − 1}) × p
        + c_in
h_new = (96354 − 97 × 961) × 31 + 100
h_new = 3137 × 31 + 100 = 97347
where
h_new: the hash of the window after sliding one place right, here "bcd"
h_old: the hash of the window before sliding, here h("abc") = 96,354
c_out: the code of the character leaving on the left, here a = 97
c_in: the code of the character entering on the right, here d = 100
p: the base, here 31
n: the window length in characters, here 3, so p^(n−1) = 31^2 = 961
^: "to the power of"
In words: subtract the leaving character's contribution, multiply everything by the base to shift each remaining character up one power, then add the new character with weight 1; "abc" rolls to "bcd" with hash 97,347.
```

With a modulus M, every step is also reduced mod M (adding M first if the subtraction went negative). That is the idea behind the Rabin–Karp substring search, which compares a pattern's hash with every window of a text in expected linear time.

> [!warning] Small moduli collide sooner than you think
> With a 10⁹-sized modulus, 100,000 strings almost certainly contain a collision. If you compare strings by hash alone, use a 64-bit modulus or two independent hashes, and confirm matches with a real comparison.

The estimate comes from the **birthday paradox**: the number of *pairs* of strings grows with the square of the number of strings, so collisions appear long before the hash values run out. Assuming each string's hash behaves like an independent, uniformly random value:

```formula
P ≈ 1 − e^(−n^2 / (2 × M))
P ≈ 1 − e^(−100000^2 / (2 × 10^9))
P ≈ 1 − e^(−5) ≈ 1 − 0.0067 ≈ 0.993
where
P: the probability that at least two of the strings share a hash, from 0 (never) to 1 (certain)
n: the number of distinct strings hashed, here 100,000
M: the number of possible hash values (the modulus), here about 10⁹
e: Euler's number, about 2.718, the base of natural logarithms; e^(−5) ≈ 0.0067
^: "to the power of"
≈: approximately equal to
In words: with 100,000 strings and about a billion possible hashes, the chance of at least one shared hash is about 99%; the chance reaches about fifty per cent at roughly 1.18 times the square root of the hash-space size.
```

The approximation is good when n is much smaller than M. Real hashes are not perfectly random, and patterned inputs can do worse.

## Key takeaways
- A rolling update removes the outgoing weight, shifts remaining weights and adds the incoming code.
- Constant update cost assumes fixed-width arithmetic and a precomputed outgoing weight.
- Collision risk grows with the number of pairs; confirm matching hashes with real comparisons.

## Further reading
- [String hashing — cp-algorithms](https://cp-algorithms.com/string/string-hashing.html)
