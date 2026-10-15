---
id: adv-rabin-karp-rolling
title: Building and sliding a rolling hash
level: advanced
minutes: 4
summary: Remove the outgoing character contribution before shifting the hash.
sourceLesson: adv-string-algorithms
---

Here n is the text or indexed-string length, m is the pattern length, and positions count from zero. Costs count constant-time character and word operations unless noted.

## Rabin–Karp: compare hashes, not strings

Treat a window of m characters as a number in base B, modulo a large prime M:

```formula
h(s) = (s_0 × B^{m−1} + s_1 × B^{m−2}
  + … + s_{m−1} × B^0) mod M
h("123") = 1 × 10^2 + 2 × 10 + 3 = 123
where
s: the window of m characters being hashed
s_0, s_1, s_{m−1}: the character codes of the window's first, second and last characters (for example `ord('a')` = 97 in Python)
m: the window length, equal to the pattern length, in characters
B: the positive integer base; 256 in the code below and 10 in the digit-only toy. Base 256 is smaller than some Unicode code points; the polynomial still defines a hash but is not a unique positional encoding of arbitrary Unicode.
B^0: B to the power 0, which is 1
M: the modulus, a large prime such as 10^9 + 7
mod: the remainder after dividing by M, so the hash is always 0 to M − 1
h(s): the hash value of the window
…: the terms in between, one per character
In words: read the window as a number written in base B, with the first character as the most significant digit, and keep only the remainder after dividing by M.
```

The last line is a toy example: with base ten, digits as characters and a modulus large enough to ignore, the window `123` hashes to the number 123.

Sliding the window one place removes the leading character and appends one. That is O(1) arithmetic, a **rolling hash**:

```formula
h_new = ((h_old − c_out × B^{m−1}) × B
  + c_in) mod M
h_new = (123 − 1 × 10^2) × 10 + 4 = 234
where
h_old: the hash of the current window
h_new: the hash of the window one place to the right
c_out: the character code leaving on the left
c_in: the character code entering on the right
B: the base
m: the window length
B^{m−1}: the weight of the leading character, precomputed once (`hi` in the code)
M: the prime modulus
mod: the remainder after dividing by M
In words: subtract the leading character's contribution, shift everything up one place by multiplying by B, and add the new character as the lowest digit.
```

In the toy example, sliding from `123` to `234` removes 1 × 100, shifts 23 to 230 and adds 4. Real code does each step modulo M so the numbers never grow, and must keep the subtraction non-negative (see Pitfalls).

```python
def rabin_karp(t, p, B=256, M=10**9 + 7):
    n, m = len(t), len(p)
    if not m:
        return list(range(n + 1))
    if m > n:
        return []
    # weight of the first character
    hi = pow(B, m - 1, M)
    hp = ht = 0
    for i in range(m):
        hp = (hp * B + ord(p[i])) % M
        ht = (ht * B + ord(t[i])) % M
    hits = []
    for i in range(n - m + 1):
        # Confirm hash candidates exactly.
        if hp == ht and t[i:i + m] == p:
            hits.append(i)
        if i + m < n:
            out = ord(t[i])
            inc = ord(t[i + m])
            # Remove the outgoing weighted
            # character.
            ht = (ht - out * hi) % M
            # Shift and append the incoming
            # character.
            ht = (ht * B + inc) % M
    return hits
```

## Key takeaways

- Remove the outgoing character contribution before shifting the hash.
- Hash equality is only a candidate; compare actual characters for exact matching.

## Further reading
- [Prefix function and Knuth–Morris–Pratt — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Rabin–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
- [Suffix Array — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix array — Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
