---
id: pat-bits
title: Bit manipulation
level: advanced
minutes: 14
summary: The handful of bit tricks that keep coming up, such as x & (x-1), x & -x and XOR cancellation, plus bitmasks for subsets and DP, counting set bits, and the traps of Python's unbounded integers.
---

A fixed-width machine word is a row of bits. Many CPUs provide AND, OR, XOR and shifts on a native word with one instruction; width, latency and available instructions depend on the architecture. Python integers can span many machine words, so their bitwise operations are not constant-time for arbitrarily large values. Bit manipulation problems exploit that: they treat a number as a tiny set or a packed array of booleans, and use identities that turn loops into one-liners.

In interviews the cues are "without extra space", "every element appears twice except one", "n ≤ 20" (subsets as masks), "power of two" or "count the 1 bits". In production the same tricks show up in permission flags, Bloom filters, bitmap indexes, chess engines and network masks.

## The operators

```
op      meaning          4-bit example
a & b   1 if both 1      1100 & 1010 = 1000
a | b   1 if either 1    1100 | 1010 = 1110
a ^ b   1 if different   1100 ^ 1010 = 0110
~a      flip all bits    ~x == -x - 1
a << k  times 2^k        0011 << 2 = 1100
a >> k  floor div 2^k    1100 >> 2 = 0011
```

Python bitwise operations behave **as if** integers had infinitely many two’s-complement sign bits: `-x == ~x + 1`. This specifies the result, not Python’s internal storage representation. In Python, `>>` on a negative number is arithmetic (it rounds towards −∞): `-5 >> 1 == -3`.

## Single-bit operations

For a nonnegative integer bit index `i`, treat bit `i` of integer `x` as a boolean flag:

```python
x >> i & 1        # test bit i
x | (1 << i)      # set bit i
x & ~(1 << i)     # clear bit i
x ^ (1 << i)      # toggle bit i
```

This is how flag sets work in practice: Unix file permissions (`0o755` is `rwxr-xr-x`), Linux `open()` flags (`O_CREAT | O_TRUNC`), and feature flags packed into one integer column.

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
        x &= x - 1
        count += 1
    return count
```

Python provides `x.bit_count()` (3.10+), which counts the ones in `abs(x)`; the lesson loop instead rejects negative input. GCC provides width-specific extensions such as `__builtin_popcount` for unsigned int and `__builtin_popcountll` for unsigned long long; C++20 also has `std::popcount` for unsigned types. Whether the compiler emits a hardware popcount instruction depends on the target and compiler settings.

### `x & -x` isolates the lowest set bit

Since `-x == ~x + 1`, the bits above the lowest 1 are flipped and the bits from there down match. AND keeps only that one bit.

```
x      = 0110 1000   (104)
-x     = 1001 1000
x & -x = 0000 1000   (8)
```

That is the step a **Fenwick tree** uses to advance update indices (`i += i & -i`, with i > 0); prefix queries subtract it. In C/C++, use unsigned arithmetic for such fixed-width tricks: negating the minimum signed value can overflow.

## XOR: the cancelling operator

XOR has three properties that make it look like magic:

```
x ^ x == 0          (self-inverse)
x ^ 0 == x          (identity)
order doesn't matter (commutative,
                      associative)
```

So XOR-ing a list together **cancels every value that appears an even number of times**.

**Single number.** Every element appears twice except one. Find it in O(n) time, O(1) space:

```python
from functools import reduce
from operator import xor

def single(nums):
    return reduce(xor, nums, 0)

# [4, 1, 2, 1, 2] -> 4
```

**Missing number.** `nums` contains n distinct values from `0..n` with one missing. XOR all indices `0..n` with all values; everything present cancels, leaving the missing one. No overflow risk, unlike summing.

### Two single numbers

Assume a reusable sequence of integers in which every value appears twice except **two distinct singles**, `x` and `y`. XOR-ing everything gives `x ^ y`, which is non-zero because `x != y`. Any set bit in it is a position where `x` and `y` differ, so split the numbers into two groups by that bit; each group contains exactly one of them, and duplicates stay together.

```python
def two_singles(nums):
    xy = 0
    for n in nums:
        xy ^= n
    low = xy & -xy     # a differing bit
    x = 0
    for n in nums:
        if n & low:
            x ^= n
    return x, xy ^ x
```

For `[1, 2, 1, 3, 2, 5]`: `xy = 3 ^ 5 = 0b110`, `low = 0b010`. Numbers with that bit: 2, 3, 2 → XOR is 3. The other is `6 ^ 3 = 5`.

### Every element thrice except one

For this code, input is a reusable sequence of signed 32-bit integers, with every value occurring three times except one occurring once. XOR does not cancel triples. Instead, count each bit position modulo 3: the bits of the tripled values contribute multiples of 3, so the remainder is the single number's bit.

```python
def single_thrice(nums):
    res = 0
    for b in range(32):
        cnt = sum(n >> b & 1 for n in nums)
        if cnt % 3:
            res |= 1 << b
    if res >= 1 << 31:   # sign bit set
        res -= 1 << 32
    return res
```

O(32n) time, O(1) space. The last two lines convert the 32-bit pattern back to a negative Python int.

## Bitmasks as subsets

With n items, an integer `mask` from `0` to `2ⁿ − 1` represents a subset: bit `i` set means item `i` is in. This enumerates all subsets of item positions with no recursion (equal item values can therefore produce equal-looking lists). The returned nested lists take Θ(n·2ⁿ) element references for n ≥ 1; enumeration also takes Θ(n·2ⁿ) tests in the unit-cost mask model:

```python
def subsets(items):
    n = len(items)
    out = []
    for mask in range(1 << n):
        out.append([items[i]
                    for i in range(n)
                    if mask >> i & 1])
    return out
```

Union is `a | b`, intersection `a & b`, "is `a` a subset of `b`?" is `a & b == a`.

**Bitmask DP** uses the mask as a DP state. The Held–Karp travelling-salesman algorithm stores `dp[mask][last]` = shortest path from a fixed start visiting exactly the cities in `mask`, ending at `last` (add the edge back to the start to complete a tour): O(2ⁿ · n²) time instead of O(n!). For n = 20, n²2ⁿ ≈ 4.2 × 10⁸ is an upper-work expression, not an exact transition count; fixing the start also reduces naive tour permutations to (n − 1)!.

> [!note] Content gap
> A C++ feasibility promise and universal practical size limit are omitted because no implementation, hardware, deadline or benchmark supports them.

For nonnegative `mask`, iterate over every **nonzero submask**:

```python
s = mask
while s:
    ...           # use submask s
    s = (s - 1) & mask
```

Over all n-bit masks, there are 3ⁿ pairs including zero submasks, since each element is in the submask, in the mask only, or in neither. This loop omits one zero submask per mask, so it executes 3ⁿ − 2ⁿ visits: O(3ⁿ) in the unit-cost mask model.

## Counting bits for 0..n

**Problem.** Return the number of 1 bits in every integer from 0 to n.

Calling a bit-at-a-time or set-bit-clearing routine on every integer through n takes O(n log n) word operations overall; a constant-time native-word popcount changes that comparison. The following DP uses O(n) table operations and O(n) entries: `i >> 1` is `i` with its last bit dropped, and we've already computed it.

```python
def count_bits(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative int")
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        bits[i] = bits[i >> 1] + (i & 1)
    return bits

# count_bits(8)
# [0, 1, 1, 2, 1, 2, 2, 3, 1]
```

The alternative recurrence `bits[i] = bits[i & (i - 1)] + 1` reuses the lowest-bit trick.

## Language traps

- **Python ints are unbounded.** `~5` is `-6`, not `4294967290`, and there's no overflow to rely on. To emulate 32-bit unsigned results, mask with `& 0xFFFFFFFF`.
- **Operator precedence differs.** In Python, comparisons bind *looser* than `&`, so `x & 1 == 0` means `(x & 1) == 0`. In C, C++ and Java, `==` binds *tighter*, so the same text means `x & (1 == 0)`, which yields 0 in C/C++ but is a type error for integer `x` in Java (`int & boolean`). Always parenthesise.
- **Shifts and arithmetic.** In both Python and C, `+` and `-` bind tighter than `<<`, so `1 << n - 1` is `1 << (n - 1)`.
- **Fixed-width overflow.** In Java, `1 << 31` is negative and `1 << 32 == 1` (the shift count is taken mod 32). `1L << k` uses 64-bit long, but its shift distance is still masked modulo 64 and its sign bit is bit 63.

## Recognising the pattern

| Cue | Trick |
|---|---|
| "appears twice except one" | XOR everything |
| "power of two" | `x > 0 and (x & (x - 1)) == 0` |
| "count 1 bits" | Kernighan / DP |
| Lowest set bit | `x & -x` |
| n ≤ 20, choose a subset | Masks 0..2ⁿ−1 |
| Visit all of n ≤ 20 nodes | Bitmask DP |
| Many boolean flags | Pack into an int |

## Key takeaways
- `x & (x - 1)` clears the lowest set bit (powers of two, popcount); `x & -x` isolates it (Fenwick trees).
- XOR cancels pairs: single number and missing number in O(n) time and O(1) space; split by a differing bit for two singles.
- An n-bit mask is a subset: enumerate all 2ⁿ, use it as a DP state, or walk submasks in O(3ⁿ) total.
- `bits[i] = bits[i >> 1] + (i & 1)` counts bits for 0..n in O(n).
- Mind the language: Python ints are unbounded, and `&` vs `==` precedence differs between Python and C-family languages.

## Further reading
- [Bit manipulation — cp-algorithms](https://cp-algorithms.com/algebra/bit-manipulation.html)
- [Enumerating submasks — cp-algorithms](https://cp-algorithms.com/algebra/all-submasks.html)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford](https://graphics.stanford.edu/~seander/bithacks.html)
- [Hamming weight — Wikipedia](https://en.wikipedia.org/wiki/Hamming_weight)
- [Binary cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/binary/)
