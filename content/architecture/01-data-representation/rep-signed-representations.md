---
id: rep-signed-representations
title: Why signed representations differ
level: basic
minutes: 3
summary: A bit pattern acquires meaning from its interpretation.
sourceLesson: rep-integers
---

The preceding binary units read a row of bits as a non-negative number. That is an **unsigned integer**. Its range follows from counting patterns:

```formula
0 ≤ x ≤ 2^n − 1
0 ≤ x ≤ 2^8 − 1 = 255
where
x: a value an n-bit unsigned integer can hold
n: the number of bits, here 8
2^n: n copies of 2 multiplied together: the number of different bit patterns
≤: less than or equal to
In words: the smallest unsigned value is 0 (all bits 0) and the largest is one less than the number of patterns (all bits 1), because one pattern is used up by zero.
```

So an 8-bit unsigned value runs from 0 to 255, and a 32-bit one from 0 to 4,294,967,295.

Programs also need negative numbers. There is no minus sign in hardware, only bits, so some bit patterns have to be set aside to mean negative values. Several schemes have been tried. Mainstream present-day processors use **two's complement** for signed integers. This lesson explains how it works, why it won, and what goes wrong when a result does not fit.

## Two schemes that lost

### Sign-magnitude

The obvious idea: use the top bit as a sign (0 = positive, 1 = negative) and the rest as the size.

```
+5 = 0000 0101
-5 = 1000 0101
```

It is easy for humans to read but awkward for hardware:

- There are two zeros, `0000 0000` (+0) and `1000 0000` (−0), so equality checks need a special case.
- Adding a positive and a negative number needs different circuitry from adding two positives (you have to compare sizes and subtract).

Sign-magnitude survives in one important place: the sign bit of floating-point numbers (the floating-point units).

### Ones' complement

To negate, invert every bit:

```
+5 = 0000 0101
-5 = 1111 1010
```

Addition is nearly uniform, but you must add any carry out of the top bit back in at the bottom ("end-around carry"), and there are still two zeros (`0000 0000` and `1111 1111`). Some early machines such as the CDC 6600 used it. Today you meet it mainly in the **Internet checksum** used by IPv4, TCP and UDP, which is a ones' complement sum.

## Key takeaways
- A bit pattern acquires meaning from its interpretation.
- Sign-magnitude and ones' complement have two zero patterns.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [GCC implementation-defined integers](https://gcc.gnu.org/onlinedocs/gcc/Integers-implementation.html)
