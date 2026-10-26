---
id: rep-modular-addition
title: One adder, two integer interpretations
level: basic
minutes: 3
summary: Fixed-width hardware addition retains the low bits.
sourceLesson: rep-integers
---

Signed and unsigned addition can share the same hardware because the retained low bits follow the same wraparound rule. The type determines how to interpret those bits.

## Why two's complement won

The real prize is that **addition is the same circuit for signed and unsigned**. You add the bits, drop any carry out of the top, and the answer is correct in both interpretations (as long as it fits).

```
  1111 1011   (-5, or 251)
+ 0000 0111   ( 7)
-----------
1 0000 0010   drop the carry
  0000 0010   = 2
```

Retaining only the low bits of a fixed-width hardware result implements **modular arithmetic**: the result wraps once it runs out of bit patterns. Numbers that differ by a whole multiple of the pattern count (256 for 8 bits) end up as the same bit pattern.

Two's complement simply chooses to label the upper half of the circle as negative:

```
bits:     00 .. 7F | 80 .. FF
unsigned:  0 .. 127|128 .. 255
signed:    0 .. 127|-128 .. -1

wrap: 0x7F + 1 = 0x80
  unsigned 127 + 1 = 128  (fine)
  signed   127 + 1 = -128 (overflow)
```

To subtract, invert the second operand and add it with an incoming carry of one. This uses the same adder and implements the negation within the retained bit width.

So one adder handles `+`, `−`, signed and unsigned. For a fixed retained width, multiplication's low bits are also identical for both. Division, comparison, widening, high multiplication bits and arithmetic flags can depend on signedness.

> [!note] Now it is the law
> C23 and C++20 finally require signed integers to use two's complement. Earlier standards also allowed sign-magnitude and ones' complement, although two's complement was already the norm on common general-purpose targets. Representation does not change the rule that signed arithmetic overflow is undefined.

> [!analogy] Real-world analogy: An odometer rolls over
> An odometer with a fixed number of wheels returns to zero after its largest reading.
>
> **How it maps:** Keeping a fixed number of result bits similarly discards complete turns through the available patterns. Signed and unsigned interpretations attach different labels to some readings.
>
> **Where it stops:** This explains retained hardware bits, not a language guarantee: signed overflow in C remains undefined.

## Key takeaways
- Fixed-width hardware addition retains the low bits.
- Signed interpretation and language overflow rules are separate questions.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [GCC implementation-defined integers](https://gcc.gnu.org/onlinedocs/gcc/Integers-implementation.html)
