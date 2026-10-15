---
id: pat-lowest-bit
title: Clear or isolate the lowest set bit
level: advanced
minutes: 3
sourceLesson: pat-bits
summary: Clearing the lowest set bit gives one popcount loop visit per set bit.
---

These examples use nonnegative Python integers and nonnegative bit positions. Python integers can span multiple machine words; bit-operation costs grow with bit length.

## The two workhorse tricks

### `x & (x - 1)` clears the lowest set bit

Subtracting 1 flips the lowest 1 to 0 and every 0 below it to 1. ANDing with the original wipes all of those out.

```
x       = 1011 0100
x - 1   = 1011 0011
x&(x-1) = 1011 0000
```

Uses:

- **Power of two:** a power of two has exactly one set bit, so `x > 0 and x & (x - 1) == 0`.
- **Counting set bits** (Kernighan's method): clear the lowest bit until zero; the loop runs once per *set* bit, not once per bit position.

```python
def popcount(x):
    if type(x) is not int or x < 0:
        raise ValueError("nonnegative int")
    count = 0
    while x:
        # Clear one set bit on every
        # iteration.
        x &= x - 1
        count += 1
    return count
```

Python provides `x.bit_count()` (3.10+), which counts the ones in `abs(x)`; the lesson loop instead rejects negative input. GCC provides width-specific extensions such as `__builtin_popcount` for unsigned int and `__builtin_popcountll` for unsigned long long; C++20 also has `std::popcount` for unsigned types. Whether the compiler emits a hardware popcount instruction depends on the target and compiler settings.

### `x & -x` isolates the lowest set bit

Since `-x == ~x + 1`, the bits above the lowest 1 are flipped and the bits from there down match. Bitwise AND keeps only that one bit.

```
x      = 0110 1000   (104)
-x     = 1001 1000
x & -x = 0000 1000   (8)
```

That is the step a **Fenwick tree** uses to advance update indices (`i += i & -i`, with i > 0); prefix queries subtract it. In C/C++, use unsigned arithmetic for such fixed-width tricks: negating the minimum signed value can overflow.

## Key takeaways
- Clearing the lowest set bit gives one popcount loop visit per set bit.
- A positive power of two has exactly one set bit; zero requires a separate guard.
- The isolated lowest bit advances a positive Fenwick update index.

## Further reading
- [Bit manipulation — cp-algorithms](https://cp-algorithms.com/algebra/bit-manipulation.html)
- [Enumerating submasks — cp-algorithms](https://cp-algorithms.com/algebra/all-submasks.html)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford](https://graphics.stanford.edu/~seander/bithacks.html)
- [Hamming weight — Wikipedia](https://en.wikipedia.org/wiki/Hamming_weight)
- [Binary cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/binary/)
- [GCC bit-operation builtins](https://gcc.gnu.org/onlinedocs/gcc/Bit-Operation-Builtins.html)
