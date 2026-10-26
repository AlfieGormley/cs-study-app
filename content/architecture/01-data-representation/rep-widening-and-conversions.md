---
id: rep-widening-and-conversions
title: Widening and signed/unsigned conversions
level: basic
minutes: 3
summary: Sign extension preserves a negative signed value when widening.
sourceLesson: rep-integers
---

Widening should preserve a value, but preserving its old bits is not enough: the new upper bits must match the source interpretation.

## Sign extension

When you widen a value (a **widening conversion**), say from 8 to 32 bits, the new upper bits must preserve its value.

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
/* The source type chooses extension. */
int8_t  s = -3;
uint8_t u = 0xFD;  /* same bits */
int32_t a = s;     /* -3  */
int32_t b = u;     /* 253 */
```

### Signed meets unsigned

When C compares a signed `int` with an `unsigned int`, the signed value is converted to unsigned first. A negative number becomes a huge positive one.

```c
/* The comparison converts x to unsigned. */
int x = -1;
unsigned y = 1;
if (x < y) puts("less");
else       puts("not less");
/* prints: not less */
```

For 32-bit unsigned int, −1 becomes 4,294,967,295, which is greater than 1. On common platforms where `size_t` does not promote to signed `int`, the same trap catches countdown loops:

```c
/* Unsafe example: the test stays true. */
/* condition cannot stop unsigned i */
for (size_t i = n - 1; i >= 0; i--)
    use(a[i]);
```

`i >= 0` is always true, so the condition cannot stop the loop. After unsigned wrap (or immediately when `n` is 0), indexing is out of bounds: this is undefined behaviour, not a guaranteed infinite loop. GCC warnings such as `-Wsign-compare` and `-Wtype-limits` can help; flags and diagnostics differ between compilers. A safe reverse traversal is `for (size_t i = n; i > 0; ) use(a[--i]);`.

## Key takeaways
- Sign extension preserves a negative signed value when widening.
- For int versus unsigned int, C converts the signed side to unsigned.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [GCC implementation-defined integers](https://gcc.gnu.org/onlinedocs/gcc/Integers-implementation.html)
