---
id: rep-lowest-set-bit
title: Clearing and isolating the lowest set bit
level: intermediate
minutes: 3
summary: Subtracting one lets AND clear the lowest set bit.
sourceLesson: rep-bitwise
---

This unit continues the preceding material on unsigned bit patterns and masks.

## Classic bit tricks

The following identities assume non-negative Python integers or unsigned fixed-width C arithmetic as appropriate. Signed C `x - 1` or `-x` can overflow at the minimum value; narrow unsigned operands can also undergo integer promotion.

### Clear the lowest set bit: `x & (x - 1)`

Subtracting 1 turns the lowest 1 into 0 and every 0 below it into 1. AND-ing with the original clears exactly that bit:

```
x       0010 1100   (44)
x - 1   0010 1011
x&(x-1) 0010 1000   (40)
```

Uses:

- **Power-of-two test**: `x != 0 && (x & (x - 1)) == 0`. A power of two has exactly one bit set to 1, so clearing it leaves 0.
- **Counting bits** (Kernighan's method): repeat until zero; the number of steps is the number of 1s. It loops once per set bit, not once per position.

```python
# Clear one set bit on each iteration.
def popcount(x):
    if x < 0:
        raise ValueError("negative input")
    n = 0
    while x:
        # Remove the lowest one bit.
        x &= x - 1
        n += 1
    return n

popcount(0xB5)   # 10110101 -> 5
```

Prefer supported library/compiler operations: GCC/Clang `__builtin_popcount` (and width-appropriate variants), C23 `stdc_count_ones`, or Python 3.10+ `int.bit_count()`. They may use hardware such as x86 POPCNT or suitable ARM instructions, but lowering depends on the target. Python bit_count counts ones in the absolute value, unlike this non-negative-only loop; arbitrary-precision cost grows with integer size.

### Isolate the lowest set bit: `x & -x`

In two's complement, `-x` is `~x + 1`. That flips everything above the lowest 1 and keeps the lowest 1 itself, so AND-ing leaves only that bit:

```
x       0010 1100
-x      1101 0100
x & -x  0000 0100   (4)
```

Fenwick trees (binary indexed trees) are built on this trick. For nonzero unsigned x, the position of that bit is "count trailing zeros" (`__builtin_ctz(0x2C)` is 2). GCC's traditional `__builtin_ctz(0)` is undefined; handle zero explicitly.

## Key takeaways
- Subtracting one lets AND clear the lowest set bit.
- AND with unsigned negation isolates that bit.
- Kernighan's loop runs once per set bit.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [Python bitwise integer operations](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)
