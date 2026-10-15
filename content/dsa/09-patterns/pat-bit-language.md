---
id: pat-bit-language
title: Account for integer width and operator precedence
level: advanced
minutes: 3
sourceLesson: pat-bits
summary: Python complement behaves with indefinitely extended sign bits.
---

The preceding bit operators use Python integer semantics. This unit contrasts them with fixed-width Java and C-family expressions; explicit width and sign assumptions are essential.

## Language traps

- **Python ints are unbounded.** `~5` is `-6`, not `4294967290`, and there's no overflow to rely on. To emulate 32-bit unsigned results, mask with `& 0xFFFFFFFF`.
- **Operator precedence differs.** In Python, comparisons bind *looser* than `&`, so `x & 1 == 0` means `(x & 1) == 0`. In C, C++ and Java, `==` binds *tighter*, so the same text means `x & (1 == 0)`, which yields 0 in C/C++ but is a type error for integer `x` in Java (`int & boolean`). Always parenthesise.
- **Shifts and arithmetic.** In both Python and C, `+` and `-` bind tighter than `<<`, so `1 << n - 1` is `1 << (n - 1)`.
- **Fixed-width overflow.** In Java, `1 << 31` is negative and `1 << 32 == 1` (the shift count is taken mod 32). `1L << k` uses 64-bit long, but its shift distance is still masked modulo 64 and its sign bit is bit 63.

## Recap of the pattern family
- `x & (x - 1)` clears the lowest set bit (powers of two, popcount); `x & -x` picks it out (Fenwick trees).
- XOR cancels pairs: single number and missing number in O(n) time and O(1) space; split by a differing bit for two singles.
- An n-bit mask is a subset: enumerate all 2ⁿ, use it as a DP state, or walk submasks in O(3ⁿ) total.
- `bits[i] = bits[i >> 1] + (i & 1)` counts bits for 0..n in O(n), where n is the largest number.
- Mind the language: Python ints are unbounded, and `&` vs `==` precedence differs between Python and C-family languages.

## Key takeaways
- Python complement behaves with indefinitely extended sign bits.
- Parentheses avoid precedence changes between Python and C-family languages.
- Java masks shift distances; a long value changes the width but does not remove the masking rule.

## Further reading
- [Bit manipulation — cp-algorithms](https://cp-algorithms.com/algebra/bit-manipulation.html)
- [Enumerating submasks — cp-algorithms](https://cp-algorithms.com/algebra/all-submasks.html)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford](https://graphics.stanford.edu/~seander/bithacks.html)
- [Hamming weight — Wikipedia](https://en.wikipedia.org/wiki/Hamming_weight)
- [Binary cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/binary/)
- [Python operator precedence](https://docs.python.org/3.14/reference/expressions.html#operator-precedence)
