---
id: rep-twos-complement-values
title: Reading and negating two's complement
level: basic
minutes: 4
summary: The highest two's-complement bit has a negative weight.
sourceLesson: rep-integers
---

This unit continues the preceding material on fixed-width integer representations.

## Two's complement

Two's complement makes one small change to the weights. The most significant bit is worth **minus** its usual weight instead of plus. All other bits keep their usual positive weights:

```formula
x = −d_{n−1} 2^{n−1} + Σ d_i 2^i
where
x: the signed value that the n bits represent
n: the number of bits (8 for an 8-bit integer)
d_{n−1}: the top bit, also called the sign bit: 0 or 1
2^{n−1}: the weight of the top bit, n − 1 copies of 2 multiplied together; 128 for 8 bits, but subtracted instead of added
Σ: "add up" the term after it for every bit position i from 0 to n − 2, that is, every bit except the top one
d_i: the bit (0 or 1) in position i
i: the bit position, counted from 0 at the right
2^i: the ordinary positive weight of position i
In words: read the bits exactly as for unsigned numbers, except that the top bit subtracts its weight instead of adding it.
```

For 8 bits the weights are:

```
bit:      7   6   5   4  3  2  1  0
weight: -128  64  32  16  8  4  2  1
```

So `1111 1011` is:

```
-128 + 64 + 32 + 16 + 8 + 2 + 1 = -5
```

And `1000 0000` is −128 on its own, the most negative 8-bit value.

| Bits | Unsigned | Two's complement |
|---|---|---|
| 0000 0000 | 0 | 0 |
| 0111 1111 | 127 | 127 |
| 1000 0000 | 128 | −128 |
| 1111 1011 | 251 | −5 |
| 1111 1111 | 255 | −1 |

Notice that the same bit pattern means different things. `1111 1111` is 255 if you call it unsigned and −1 if you call it signed. The bits do not know; the **type** decides.

### Range

The most negative value has only the top bit set; the most positive has every bit set except the top one:

```formula
−2^{n−1} ≤ x ≤ 2^{n−1} − 1
−2^7 ≤ x ≤ 2^7 − 1   for n = 8
−128 ≤ x ≤ 127
where
x: a value an n-bit two's complement integer can hold
n: the number of bits
2^{n−1}: n − 1 copies of 2 multiplied together: half the number of bit patterns (128 for 8 bits)
≤: less than or equal to
In words: half of the patterns are negative and the other half are zero and the positive numbers, so the range runs from minus half the pattern count up to one less than half.
```

| Width | Min | Max |
|---|---|---|
| 8 | −128 | 127 |
| 16 | −32,768 | 32,767 |
| 32 | −2,147,483,648 | 2,147,483,647 |
| 64 | about −9.22 × 10^18 | about 9.22 × 10^18 |

The range is lopsided: there is one more negative value than positive, because zero takes one of the "non-negative" patterns. This asymmetry causes real bugs, as you will see below.

### Negating: invert and add one

To find −x, flip every bit and add 1:

```
 +5 = 0000 0101
flip  1111 1010
 +1   1111 1011   = -5
```

It works in both directions. Negate −5 the same way and you get +5 back. Here is why:

```formula
x + ~x = −1
~x = −x − 1
~x + 1 = −x
where
x: any n-bit two's complement value
~x: x with every bit inverted, 0s becoming 1s and 1s becoming 0s; ~ is the bitwise NOT operator in C and Python
−1: in two's complement, the all-ones pattern (1111 1111 in 8 bits)
In words: a number plus its inverted copy has a 1 in every position, which is −1; move x to the other side and add 1, and "flip and add one" is exactly negation.
```

For example, complementing the value five gives `1111 1010` (−6), and adding 1 gives `1111 1011`, which is −5.

A quick shortcut for doing it by hand: copy bits from the right up to and including the first `1`, then flip everything to the left of it.

> [!warning] A bit pattern is not a C overflow guarantee
> Flip-and-add-one works as an identity on the retained bits. The mathematical negation of the minimum signed value does not fit in the same signed type. Its wrapped bit pattern is unchanged; evaluating that overflowing negation in C is undefined behaviour. The later overflow unit explains the language rule.

## Key takeaways
- The highest two's-complement bit has a negative weight.
- There is one more negative value than positive.
- Flip and add one gives the negated bit pattern, subject to representability.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [GCC implementation-defined integers](https://gcc.gnu.org/onlinedocs/gcc/Integers-implementation.html)
