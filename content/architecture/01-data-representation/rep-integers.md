---
id: rep-integers
title: Two's complement and overflow
level: basic
minutes: 13
summary: How negative integers are stored, why two's complement won, sign extension, and what happens (and what C allows the compiler to assume) when arithmetic overflows.
---

Lesson 1 read a row of bits as a non-negative number. That is an **unsigned** integer. With *n* bits it covers 0 to 2^n − 1, so an 8-bit unsigned value runs from 0 to 255.

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

Sign-magnitude survives in one important place: the sign bit of floating-point numbers (lesson 4).

### Ones' complement

To negate, invert every bit:

```
+5 = 0000 0101
-5 = 1111 1010
```

Addition is nearly uniform, but you must add any carry out of the top bit back in at the bottom ("end-around carry"), and there are still two zeros (`0000 0000` and `1111 1111`). Some early machines such as the CDC 6600 used it. Today you meet it mainly in the **Internet checksum** used by IPv4, TCP and UDP, which is a ones' complement sum.

## Two's complement

Two's complement makes one small change to the weights. The most significant bit is worth **minus** 2^(n−1) instead of plus. All other bits keep their usual positive weights.

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

With *n* bits, two's complement covers −2^(n−1) to 2^(n−1) − 1.

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

It works in both directions. Negate −5 the same way and you get +5 back. The reason: x + ~x is all ones, which is −1, so ~x = −x − 1, and therefore ~x + 1 = −x.

A quick shortcut for doing it by hand: copy bits from the right up to and including the first `1`, then flip everything to the left of it.

## Why two's complement won

The real prize is that **addition is the same circuit for signed and unsigned**. You add the bits, drop any carry out of the top, and the answer is correct in both interpretations (as long as it fits).

```
  1111 1011   (-5, or 251)
+ 0000 0111   ( 7)
-----------
1 0000 0010   drop the carry
  0000 0010   = 2  (and 251+7-256 = 2)
```

This works because *n*-bit arithmetic is arithmetic **modulo 2^n**. In mod 256, −5 and 251 are the same number. Two's complement simply chooses to label the top half of the circle as negative:

```
bits:     00 .. 7F | 80 .. FF
unsigned:  0 .. 127|128 .. 255
signed:    0 .. 127|-128 .. -1

wrap: 0x7F + 1 = 0x80
  unsigned 127 + 1 = 128  (fine)
  signed   127 + 1 = -128 (overflow)
```

Subtraction is addition of the negation (a − b = a + ~b + 1), so one adder handles `+`, `−`, signed and unsigned. Multiplication's low *n* bits are also identical for both. Division, comparison, widening, high multiplication bits and arithmetic flags can depend on signedness.

> [!note] Now it is the law
> C23 and C++20 finally require signed integers to use two's complement. Earlier standards also allowed sign-magnitude and ones' complement, although two's complement was already the norm on common general-purpose targets. Representation does not change the rule that signed arithmetic overflow is undefined.

## Sign extension

When you widen a value, say from 8 to 32 bits, the new upper bits must preserve its value.

- **Unsigned** values are **zero-extended**: fill with 0s.
- **Signed** values are **sign-extended**: fill with copies of the sign bit.

```
-3 as 8 bits:            1111 1101
sign-extended to 16: 1111 1111 1111 1101
zero-extended to 16: 0000 0000 1111 1101
                     (= 253, wrong for -3)
```

x86 has separate instructions for each (`movsx` and `movzx`), and ARM has `sxtb` and `uxtb`. The compiler picks one based on the C type, which is why the type of a variable matters even when the bits look the same.

```c
int8_t  s = -3;
uint8_t u = 0xFD;  /* same bits */
int32_t a = s;     /* -3  */
int32_t b = u;     /* 253 */
```

## Overflow

Overflow means the true mathematical result does not fit in the type. The hardware still produces *n* bits; what those bits mean, and what your language promises, varies.

### The two flags

Architectures such as x86, and flag-setting ARM add instructions, distinguish two kinds of overflow. Not all ISAs have these flags:

- **Carry flag**: there was a carry out of the top bit. This means **unsigned** overflow. 200 + 100 in 8 bits gives 44 with carry set.
- **Overflow flag**: the signed result has the wrong sign. This happens only when adding two numbers of the **same** sign gives a result of the opposite sign.

```
  0110 0100  (100)
+ 0110 0100  (100)
-----------
  1100 1000  = -56 signed, 200 unsigned
```

Here the carry flag is clear (200 fits in unsigned 8 bits) but the overflow flag is set (+100 + +100 cannot be negative). Adding a positive and a negative number can never overflow.

### What C does

C treats the two cases very differently.

- Arithmetic whose resulting type is unsigned is defined to wrap modulo 2^n. Narrow unsigned operands may first promote to signed int; their expressions follow the promoted type, not an automatic wrap at the original width. `UINT_MAX + 1` is 0, and `0u - 1` is `UINT_MAX` (4,294,967,295 for 32 bits).
- **Signed** overflow is **undefined behaviour**. The C standard imposes no requirements on an execution with undefined behaviour; consequences need not be confined to the point of overflow. Optimisers may assume defined executions do not overflow.

That assumption has visible effects:

```c
int will_overflow(int x) {
    return x + 1 < x;
}
```

You might expect this to return 1 for `INT_MAX`. GCC and Clang at `-O2` compile it to `return 0`, because for any `x` where the addition is defined, `x + 1 < x` is false. The same reasoning lets compilers widen loop counters and remove "impossible" checks, which is often good for speed and occasionally deletes a security check.

Safe alternatives:

```c
int r;
if (__builtin_add_overflow(a, b, &r))
    handle_error();
/* C23 standard version: */
/* #include <stdckdint.h>  */
/* if (ckd_add(&r, a, b))  */
```

Or check both directions before adding `int` operands: `if ((b > 0 && a > INT_MAX - b) || (b < 0 && a < INT_MIN - b))` detects overflow without first overflowing. Compiler flags also help: GCC's `-fwrapv` specifies wrapping for signed addition, subtraction and multiplication, and `-ftrapv` requests traps for those operations; neither is a blanket fix for every undefined integer operation, and `-fsanitize=signed-integer-overflow` (UBSan) reports it at run time in testing.

### The asymmetry bug

Because the range has one extra negative value, some operations on the minimum cannot be represented:

- `-INT_MIN` should be +2,147,483,648, which does not fit. It is undefined in C; a wrapping hardware instruction may produce `INT_MIN` again, but the compiler need not preserve that result.
- `abs(INT_MIN)` is undefined for the same reason.
- `INT_MIN / -1` is undefined, and on x86 the `idiv` instruction raises a hardware exception that usually kills the process.

> [!warning] Hash bucket indices
> A classic Java bug: `Math.abs(key.hashCode()) % n`. For positive n, when the hash is `Integer.MIN_VALUE`, `Math.abs` returns it unchanged. Its remainder is negative unless n divides it exactly; a negative index throws. Use `Math.floorMod(h, n)` or mask the sign bit off.

### Signed meets unsigned

When C compares a signed `int` with an `unsigned int`, the signed value is converted to unsigned first. A negative number becomes a huge positive one.

```c
int x = -1;
unsigned y = 1;
if (x < y) puts("less");
else       puts("not less");
/* prints: not less */
```

For 32-bit unsigned int, −1 becomes 4,294,967,295, which is greater than 1. The same trap catches `size_t` loops:

```c
/* condition cannot stop unsigned i */
for (size_t i = n - 1; i >= 0; i--)
    use(a[i]);
```

`i >= 0` is always true, so the condition cannot stop the loop. After unsigned wrap (or immediately for n = 0), indexing is out of bounds: this is undefined behaviour, not a guaranteed infinite loop. GCC warnings such as `-Wsign-compare` and `-Wtype-limits` can help; flags and diagnostics differ between compilers. A safe reverse traversal is `for (size_t i = n; i > 0; ) use(a[--i]);`.

## Python: no overflow, but you can fake it

Python's `int` has arbitrary precision. Arithmetic has no fixed-width wraparound, so `2**100` is exact. Storage and implementation limits still apply; a computation can fail for lack of resources. Python models a negative number as if it had an infinite row of 1s to the left, which is why bitwise operations on negatives behave like two's complement.

To see the *n*-bit pattern, or to emulate a fixed-width type, mask it:

```python
def to_u8(x):
    return x & 0xFF

def to_s8(x):
    x &= 0xFF
    return x - 256 if x >= 128 else x

to_u8(-3)       # 253
bin(-3 & 0xFF)  # '0b11111101'
to_s8(100+100)  # -56
to_s8(0xB5)     # -75
```

NumPy, however, uses fixed-width types, so `np.int8(100) + np.int8(100)` wraps to −56 (under the usual NumPy error settings scalar arithmetic warns, while integer array arithmetic generally wraps without that warning).

## Overflow in the real world

- **Ariane 5, 1996.** A conversion of the horizontal-bias alignment result (related to horizontal velocity) from 64-bit floating point to a 16-bit signed integer raised an exception. Both inertial reference systems failed through the same software path; the inquiry identified reuse of assumptions from Ariane 4 and inadequate protection/testing, not just a number being too large.
- **Boeing 787, 2015.** The US FAA warned that a counter in the generator control units would overflow after 248 days of continuous power, potentially losing all AC electrical power if the units entered failsafe together. The FAA directive states the counter-overflow interval; it does not specify a 32-bit centisecond representation. That implementation claim is omitted because it could not be verified from the directive.
> [!note] Evidence gap
> The YouTube/Gangnam Style migration anecdote is omitted: the original engineering account of counter type and migration timing was not available for reliable primary-source verification. A hypothetical signed 32-bit view counter still has the demonstrable limit 2,147,483,647.

- **The year 2038 problem.** A signed 32-bit `time_t` counting seconds from 1970 runs out at 03:14:07 UTC on 19 January 2038, and a wrapping interpretation of the next bit pattern corresponds to December 1901. Actual software may fail differently; signed overflow in C is not guaranteed to wrap. Common current 64-bit Unix ABIs use a 64-bit `time_t`, but embedded devices and old file formats remain at risk.

## Key takeaways
- Unsigned *n*-bit integers cover 0 to 2^n − 1; two's complement covers −2^(n−1) to 2^(n−1) − 1.
- In two's complement the top bit weighs −2^(n−1); negate by inverting and adding 1.
- The same adder works for signed and unsigned because both are arithmetic mod 2^n. The type, not the bits, decides the meaning.
- Widening uses sign extension for signed types and zero extension for unsigned.
- The carry flag signals unsigned overflow; the overflow flag signals signed overflow (same-sign inputs, different-sign result).
- In C, arithmetic in an unsigned resulting type wraps (check narrow-operand promotions), but signed overflow is undefined behaviour that the optimiser exploits. Use `__builtin_add_overflow` or C23 `ckd_add`.
- `INT_MIN` has no positive counterpart: `-INT_MIN`, `abs(INT_MIN)` and `INT_MIN / -1` all break.
- Mixing int and unsigned int converts the signed side to unsigned. Other signed/unsigned combinations follow ranks and representable ranges, not a universal unsigned-wins rule.

## Further reading
- [Two's complement — Wikipedia](https://en.wikipedia.org/wiki/Two%27s_complement)
- [Integer overflow — Wikipedia](https://en.wikipedia.org/wiki/Integer_overflow)
- [Arithmetic operators and overflow — cppreference (C)](https://en.cppreference.com/w/c/language/operator_arithmetic)
- [Standard library header stdckdint.h — cppreference](https://en.cppreference.com/w/c/header/stdckdint)
- [Year 2038 problem — Wikipedia](https://en.wikipedia.org/wiki/Year_2038_problem)
- [Ariane flight V88 — Wikipedia](https://en.wikipedia.org/wiki/Ariane_flight_V88)

- [FAA 2015 Boeing 787 directive](https://www.govinfo.gov/content/pkg/FR-2015-05-01/pdf/2015-10066.pdf)
- [GCC code generation options](https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html)

- [Ariane 501 inquiry board report (university-hosted copy)](https://www-users.cse.umn.edu/~arnold/disasters/ariane5rep.html)
