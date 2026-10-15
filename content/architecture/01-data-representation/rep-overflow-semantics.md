---
id: rep-overflow-semantics
title: Overflow flags and C arithmetic rules
level: basic
minutes: 3
summary: Carry and signed overflow detect different out-of-range results.
sourceLesson: rep-integers
---

This unit continues the preceding material on fixed-width integer representations.

## Overflow

**Integer overflow** means the true mathematical result does not fit in the type. The hardware still produces *n* bits; what those bits mean, and what your language promises, varies.

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

- Arithmetic whose resulting type is unsigned is defined to wrap around: results are reduced modulo 2 to the power of the type's width in bits (modulo 4,294,967,296 for a 32-bit `unsigned int`). Narrow unsigned operands may first promote to signed int; their expressions follow the promoted type, not an automatic wrap at the original width. `UINT_MAX + 1` is 0, and `0u - 1` is `UINT_MAX` (4,294,967,295 for 32 bits).
- **Signed overflow** is **undefined behaviour**. The C standard imposes no requirements on an execution with undefined behaviour; consequences need not be confined to the point of overflow. Optimisers may assume defined executions do not overflow.

That assumption has visible effects:

```c
/* Defined inputs cannot make this true. */
int will_overflow(int x) {
    return x + 1 < x;
}
```

You might expect this to return 1 for `INT_MAX`. GCC and Clang at `-O2` compile it to `return 0`, because for any `x` where the addition is defined, `x + 1 < x` is false. The same reasoning lets compilers widen loop counters and remove "impossible" checks, which is often good for speed and occasionally deletes a security check.

Safe alternatives:

```c
/* Detect overflow before using r. */
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

## Key takeaways
- Carry and signed overflow detect different out-of-range results.
- Unsigned resulting types wrap; signed C overflow is undefined.
- Check before overflowing, or use checked arithmetic.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [GCC implementation-defined integers](https://gcc.gnu.org/onlinedocs/gcc/Integers-implementation.html)
