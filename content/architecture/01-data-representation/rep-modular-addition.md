---
id: rep-modular-addition
title: One adder, two integer interpretations
level: basic
minutes: 3
summary: Fixed-width hardware addition retains the low bits.
sourceLesson: rep-integers
---

This unit continues the preceding material on fixed-width integer representations.

## Why two's complement won

The real prize is that **addition is the same circuit for signed and unsigned**. You add the bits, drop any carry out of the top, and the answer is correct in both interpretations (as long as it fits).

```
  1111 1011   (-5, or 251)
+ 0000 0111   ( 7)
-----------
1 0000 0010   drop the carry
  0000 0010   = 2  (and 251+7-256 = 2)
```

This works because fixed-width arithmetic is **modular arithmetic**: it wraps around, like a clock, once it runs out of bit patterns. Numbers that differ by a whole multiple of the pattern count (256 for 8 bits) end up as the same bit pattern:

```formula
a ≡ b (mod 2^n)
−5 ≡ 251 (mod 256)
251 − (−5) = 256
where
≡: "is congruent to": the two numbers leave the same remainder when divided by the modulus, so n-bit hardware stores them as the same bit pattern
mod: modulo: arithmetic that wraps around after reaching the modulus; here the modulus is 2^n
a: any integer
b: any integer that differs from a by a whole multiple of 2^n
n: the number of bits (8 in the example, so 2^n = 256)
In words: with eight retained bits, −5 and 251 have the same residue and bit pattern, because they differ by exactly 256; they remain different mathematical integers.
```

Two's complement simply chooses to label the upper half of the circle as negative:

```
bits:     00 .. 7F | 80 .. FF
unsigned:  0 .. 127|128 .. 255
signed:    0 .. 127|-128 .. -1

wrap: 0x7F + 1 = 0x80
  unsigned 127 + 1 = 128  (fine)
  signed   127 + 1 = -128 (overflow)
```

Subtraction is addition of the negation:

```formula
a − b = a + (−b)
a − b = a + ~b + 1
where
a: the number being subtracted from
b: the number being subtracted
~b: b with every bit inverted (bitwise NOT)
In words: to subtract, invert b, add 1 to make −b, then add; hardware typically feeds the +1 in as a carry into the lowest bit, so no separate subtractor is needed.
```

So one adder handles `+`, `−`, signed and unsigned. For a fixed retained width, multiplication's low bits are also identical for both. Division, comparison, widening, high multiplication bits and arithmetic flags can depend on signedness.

> [!note] Now it is the law
> C23 and C++20 finally require signed integers to use two's complement. Earlier standards also allowed sign-magnitude and ones' complement, although two's complement was already the norm on common general-purpose targets. Representation does not change the rule that signed arithmetic overflow is undefined.

## Key takeaways
- Fixed-width hardware addition retains the low bits.
- Signed interpretation and language overflow rules are separate questions.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [GCC implementation-defined integers](https://gcc.gnu.org/onlinedocs/gcc/Integers-implementation.html)
