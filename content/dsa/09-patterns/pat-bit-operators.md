---
id: pat-bit-operators
title: Read shifts and manipulate individual flags
level: advanced
minutes: 4
sourceLesson: pat-bits
summary: Bitwise operators combine bit patterns rather than treating values as logical conditions.
---

A fixed-width machine word is a row of bits. Many CPUs provide bitwise AND, bitwise OR, XOR and shifts on a native word with one instruction; width, latency and available instructions depend on the architecture. Python integers can span many machine words, so their bitwise operations are not constant-time for arbitrarily large values. Bit manipulation problems exploit that: they treat a number as a tiny set or a packed array of booleans, and use identities that turn loops into one-liners.

In interviews the cues are "without extra space", "every element appears twice except one", "at most 20 items" (so item positions can be represented by bits in a mask), "power of two" or "count the 1 bits". In production the same tricks show up in permission flags, Bloom filters, bitmap indexes, chess engines and network masks.

## The operators

```
op      meaning          4-bit example
a & b   1 if both 1      1100 & 1010 = 1000
a | b   1 if either 1    1100 | 1010 = 1110
a ^ b   1 if different   1100 ^ 1010 = 0110
~a      flip all bits    ~x == -x - 1
a << k  left shift      0011 << 2 = 1100
a >> k  right shift     1100 >> 2 = 0011
```

The two shift rows are arithmetic in disguise. For a nonnegative integer:

```formula
a << k = a 2^k
a >> k = ⌊a / (2^k)⌋
3 << 2 = 3 × 4 = 12
12 >> 2 = ⌊12 / 4⌋ = 3
where
a: a nonnegative integer
k: the shift distance, a nonnegative whole number of bit positions
<<: left shift: move every bit k places towards the high end, filling with zeros
>>: right shift: move every bit k places towards the low end, dropping the bits that fall off
2^k: k copies of 2 multiplied together
⌊ ⌋: floor, rounding down to the nearest whole number
In words: shifting left by k multiplies by 2 to the k, and shifting right by k divides by 2 to the k and throws away the remainder, just as moving a decimal number one place multiplies or divides by 10; 0011 shifted left 2 is 1100.
```

The `~` row is two's complement, explained next:

```formula
~x = −x − 1
−x = ~x + 1
~5 = −6
where
x: an integer
~: bitwise NOT, flipping every bit of x
In words: flipping all the bits of x gives minus x minus one in two's complement, so negating a number is "flip every bit, then add 1"; flipping 5 gives −6.
```

Python bitwise operations behave **as if** integers had infinitely many two’s-complement sign bits: `-x == ~x + 1`. This specifies the result, not Python’s internal storage representation. In Python, `>>` on a negative number is arithmetic (it rounds down, towards minus infinity): `-5 >> 1 == -3`.

## Single-bit operations

For a nonnegative integer bit index `i`, treat bit `i` of integer `x` as a boolean flag:

```python
x >> i & 1        # test bit i
x | (1 << i)      # set bit i
x & ~(1 << i)     # clear bit i
x ^ (1 << i)      # toggle bit i
```

This is how flag sets work in practice: Unix file permissions (`0o755` is `rwxr-xr-x`), Linux `open()` flags (`O_CREAT | O_TRUNC`), and feature flags packed into one integer column.

## Key takeaways
- Bitwise operators combine bit patterns rather than treating values as logical conditions.
- Python shifts have exact integer semantics and nonnegative shift distances.
- Test, set, clear or toggle one position with a single-bit mask.

## Further reading
- [Bit manipulation — cp-algorithms](https://cp-algorithms.com/algebra/bit-manipulation.html)
- [Enumerating submasks — cp-algorithms](https://cp-algorithms.com/algebra/all-submasks.html)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford](https://graphics.stanford.edu/~seander/bithacks.html)
- [Hamming weight — Wikipedia](https://en.wikipedia.org/wiki/Hamming_weight)
- [Binary cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/binary/)
- [Python integer bitwise semantics](https://docs.python.org/3.14/library/stdtypes.html#bitwise-operations-on-integer-types)
