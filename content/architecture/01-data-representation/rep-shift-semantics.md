---
id: rep-shift-semantics
title: Shifts, rounding and C restrictions
level: intermediate
minutes: 4
summary: Arithmetic right shift floors negative values; C integer division truncates.
sourceLesson: rep-bitwise
---

This unit continues the preceding material on unsigned bit patterns and masks.

## Shifts

`x << k` moves every bit *k* places left and fills with zeros. Each place doubles the value, so for unsigned values that do not lose any 1s off the top it is a multiplication by a power of two:

```formula
x << k = x (2^k)
5 << 3 = 5 × 2^3 = 5 × 8 = 40
where
<<: left shift: move every bit k places towards the top and fill the bottom k places with 0s
x: the unsigned value being shifted
k: the number of places to shift
2^k: k copies of 2 multiplied together
In words: shifting left by k places multiplies by 2 to the power k, as long as no 1 bit falls off the top.
```

In bits:

```
0000 0101  (5)
<< 3
0010 1000  (40 = 5 × 8)
```

`x >> k` moves bits right, discarding the low *k* bits. What fills the top depends on the kind of shift:

- **Logical** right shift fills with 0. Used for unsigned values.
- **Arithmetic** right shift fills with copies of the sign bit, preserving the sign. Used for signed values.

```
1111 0000  (-16 signed, 240 unsigned)
logical    >> 2: 0011 1100  (60)
arithmetic >> 2: 1111 1100  (-4)
```

An arithmetic shift divides by a power of two, but it rounds **towards negative infinity**, while C's `/` rounds **towards zero**:

```formula
x >> k = ⌊x / (2^k)⌋
−17 >> 1 = ⌊−8.5⌋ = −9
trunc(−17 / 2) = trunc(−8.5) = −8
where
>>: arithmetic right shift by k places: move every bit k places down, filling the top with copies of the sign bit
x: a signed integer, here −17
k: the number of places shifted, here 1
2^k: k copies of 2 multiplied together
⌊ ⌋: floor: round down to the next whole number, towards negative infinity, so ⌊−8.5⌋ = −9
trunc: truncation: drop the fractional part, rounding towards zero; this is what C's integer / does (C99 and later)
In words: for negative numbers the shift rounds down (−9) while division rounds towards zero (−8); for non-negative numbers both give the same answer.
```

So on C implementations with arithmetic right shift, `-17 >> 1` is −9 while C99-and-later `-17 / 2` is −8. A compiler may implement signed division using a corrected shift, unless it proves a correction unnecessary; a bare arithmetic shift is not generally equivalent.

### The C shift rules

C leaves several cases to the implementation or makes them undefined:

- Shifting by a negative amount, or by **at least the width** of the promoted left operand, is undefined. `x << 32` on a 32-bit `int` is UB. For ordinary 32-bit x86 shifts the hardware masks the count to 5 bits (6 bits for 64-bit shifts), so it often behaves like `x << 0`, but the optimiser may do anything.
- Under C23 and earlier ISO C rules, left shift of a negative signed value is undefined, even by zero; for a non-negative signed value, the multiplied result must be representable in the promoted type. `1 << 31` with 32-bit `int` is UB; write `1u << 31`.
- Right-shifting a negative signed value is **implementation-defined**. GCC, Clang and MSVC all do an arithmetic shift.

Use suitably wide **unsigned** operands and masks, check shift counts, and account for integer promotions. A plain `1u` has unsigned-int width; use a wider constant when needed. These are C rules, not a statement of the differing modern C++ shift rules.

### Python's shifts

Python ints have no fixed width, so `1 << 100` is fine, and `>>` on negatives is always arithmetic (it floors: `-17 >> 1` is −9). `~x` is always `-x - 1`. To emulate a fixed width, mask the result: `(x << 3) & 0xFFFFFFFF`.

## Key takeaways
- Arithmetic right shift floors negative values; C integer division truncates.
- C shift counts and promoted operand types constrain validity.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [Python bitwise integer operations](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)
