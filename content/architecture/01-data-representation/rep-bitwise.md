---
id: rep-bitwise
title: Bitwise operations
level: intermediate
minutes: 13
summary: AND, OR, XOR, NOT and shifts, the mask idioms built from them, the classic bit tricks, and the C and Python rules that trip people up.
---

Arithmetic treats a word as one number. **Bitwise** operations treat it as a row of independent bits and work on every position at once. A 64-bit bitwise operation can manipulate up to 64 flag bits at once, which is why bitwise code appears everywhere from device drivers and network stacks to chess engines, compression and database bitmap indexes.

## The operators

| Op | C / Python | Result bit is 1 when |
|---|---|---|
| AND | `a & b` | both bits are 1 |
| OR | `a \| b` | either bit is 1 |
| XOR | `a ^ b` | the bits differ |
| NOT | `~a` | the bit was 0 |

Each operates column by column, with no carries between positions:

```
  1100 1010      1100 1010      1100 1010
& 1010 0110    | 1010 0110    ^ 1010 0110
-----------    -----------    -----------
  1000 0010      1110 1110      0110 1100
```

Three intuitions are worth memorising:

- AND with 1 **keeps** a bit; AND with 0 **clears** it.
- OR with 1 **sets** a bit; OR with 0 leaves it alone.
- XOR with 1 **flips** a bit; XOR with 0 leaves it alone.

A **mask** is a constant whose 1s pick out the positions you care about. Choosing the operator decides what happens to those positions.

> [!warning] Bitwise is not logical
> `&&` and `||` in C (and `and` / `or` in Python) are **logical** operators. They treat each whole operand as true or false and short-circuit. `2 & 1` is 0, but `2 && 1` is 1.

## The four mask idioms

For unsigned int x and 0 ≤ k < its width, build the mask `1u << k`. A wider x needs a correspondingly wide unsigned mask; complementing a 32-bit mask before widening it would clear the upper bits of a 64-bit x.

```c
x |=  (1u << k);   /* set bit k    */
x &= ~(1u << k);   /* clear bit k  */
x ^=  (1u << k);   /* toggle bit k */
if (x & (1u << k)) { /* bit is set */ }
```

Applying each one separately to `x = 0x2C` (`0010 1100`):

```
x            0010 1100
set bit 0    0010 1101   (x | 0x01)
clear bit 3  0010 0100   (x & ~0x08)
toggle bit 7 1010 1100   (x ^ 0x80)
test bit 2   0000 0100   nonzero: set
```

### Flags

Packing booleans into one integer is the most common use. POSIX `open()` takes flags OR-ed together:

```c
int fd = open("log.txt",
    O_WRONLY | O_CREAT | O_APPEND, 0644);
```

Many open options are independent bit flags, but **not every O_ constant is one bit**. Access modes are alternatives selected with O_ACCMODE; O_RDONLY is commonly zero. Test a mode with `(flags & O_ACCMODE) == O_RDONLY`, not a simple AND with O_RDONLY. Creation mode 0644 is also filtered by the process umask when a file is created. The same pattern appears in Python's `re.IGNORECASE | re.MULTILINE` and the `enum.Flag` class.

### Extracting fields

Many formats pack several small numbers into one word. To pull one out, **shift it down, then mask it**:

```python
colour = 0x1E90FF   # RRGGBB
r = (colour >> 16) & 0xFF   # 0x1E = 30
g = (colour >> 8)  & 0xFF   # 0x90 = 144
b =  colour        & 0xFF   # 0xFF = 255
```

To pack, shift each field up and OR them together: `(r << 16) | (g << 8) | b`. CPU instruction encodings, IPv4 headers, Unix file modes and UUIDs are all decoded this way.

In Python, for non-negative n, a mask of the low *n* bits is `(1 << n) - 1`. In C, the operand type, promotions and shift-count limit matter; use an appropriately wide unsigned mask and handle n equal to the width separately. For *n* = 5 that is `0b11111` = 31.

## Shifts

`x << k` moves every bit *k* places left and fills with zeros. For unsigned values that do not lose any 1s off the top, it multiplies by 2^k:

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

An arithmetic shift by *k* divides by 2^k, but it rounds **towards negative infinity**, while C's `/` rounds **towards zero**. On C implementations with arithmetic right shift, `-17 >> 1` is −9 while C99-and-later `-17 / 2` is −8. A compiler may implement signed division using a corrected shift, unless it proves a correction unnecessary; a bare arithmetic shift is not generally equivalent.

### The C shift rules

C leaves several cases to the implementation or makes them undefined:

- Shifting by a negative amount, or by **at least the width** of the promoted left operand, is undefined. `x << 32` on a 32-bit `int` is UB. For ordinary 32-bit x86 shifts the hardware masks the count to 5 bits (6 bits for 64-bit shifts), so it often behaves like `x << 0`, but the optimiser may do anything.
- Under C23 and earlier ISO C rules, left shift of a negative signed value is undefined, even by zero; for a non-negative signed value, the multiplied result must be representable in the promoted type. `1 << 31` with 32-bit `int` is UB; write `1u << 31`.
- Right-shifting a negative signed value is **implementation-defined**. GCC, Clang and MSVC all do an arithmetic shift.

Use suitably wide **unsigned** operands and masks, check shift counts, and account for integer promotions. A plain `1u` has unsigned-int width; use a wider constant when needed. These are C rules, not a statement of the differing modern C++ shift rules.

### Python's shifts

Python ints have no fixed width, so `1 << 100` is fine, and `>>` on negatives is always arithmetic (it floors: `-17 >> 1` is −9). `~x` is always `-x - 1`. To emulate a fixed width, mask the result: `(x << 3) & 0xFFFFFFFF`.

## Precedence traps

In C, `&`, `^` and `|` bind **more loosely** than `==`. This is a historical leftover from before C had `&&`.

```c
if (x & 1 == 0)    /* x & (1 == 0) */
                   /* = x & 0 = 0   */
if ((x & 1) == 0)  /* what you meant */
```

Python fixed this: its bitwise operators bind tighter than comparisons, so `x & 1 == 0` means `(x & 1) == 0`. Code ported between the two languages can therefore change meaning silently. Shifts also bind looser than `+` in both languages: `1 << n - 1` is `1 << (n - 1)`. When in doubt, add brackets.

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

- **Power-of-two test**: `x != 0 && (x & (x - 1)) == 0`. A power of two has exactly one 1-bit, so clearing it leaves 0.
- **Counting bits** (Kernighan's method): repeat until zero; the number of steps is the number of 1s. It loops once per set bit, not once per position.

```python
def popcount(x):
    if x < 0:
        raise ValueError("negative input")
    n = 0
    while x:
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

### XOR's algebra

XOR has properties that make it unusually useful:

- `a ^ a = 0` and `a ^ 0 = a`.
- It is commutative and associative, so order does not matter.
- It is its own inverse: `(a ^ k) ^ k = a`.

Consequences:

- **Find the odd one out.** XOR every element of a list where every value appears twice except one. The pairs cancel and the single value is left, in O(n) word operations and O(1) auxiliary words for fixed-width values; arbitrary-precision integer costs depend on bit length.
- **Parity.** XOR-ing all the bits gives 1 if the count of 1s is odd. RAID 5 stores the XOR of the data blocks so any one lost block can be rebuilt by XOR-ing the rest.
- **Toggle with a key.** A one-time pad XORs with a secret uniformly random message-length pad used only once. A stream cipher such as ChaCha20 XORs plaintext with a generated keystream, not directly with its short secret key. Repeating the same XOR recovers the input; that identity alone does not provide secure encryption.

```python
from functools import reduce
from operator import xor

reduce(xor, [4, 7, 2, 7, 4])   # 2
```

The **XOR swap** (`a ^= b; b ^= a; a ^= b;`) swaps without a temporary, but do not use it. It introduces dependencies and can lose to a plain swap, but performance depends on compilation and target. It fails for aliased a and b (the shared value becomes 0). Prefer a clear temporary or language swap; no compiler universally guarantees optimal code.

## Bitwise in the real world

- **Subnet masks.** A /24 network has mask `255.255.255.0` = `0xFFFFFF00`. A host is on the network if `(ip & mask) == (net & mask)`. Actual routing lookup uses longest-prefix matching and implementation-specific data structures. No universal throughput rate is implied.
- **Bitboards.** Chess engines such as Stockfish store each piece type as a 64-bit integer, one bit per square, and compute attacks with shifts and masks.
- **Bitmap indexes and Bloom filters.** Databases answer `WHERE a AND b` by AND-ing bitmaps of matching rows. Roaring Bitmaps (used by Lucene, Druid and others) compress them.
- **Hash tables.** For non-negative or unsigned hashes and a nonzero power-of-two table size, `hash & (size - 1)` equals `hash % size`. Compilers can already optimise remainder by a known power of two; a speedup is not guaranteed. Java's `HashMap` does this, and also XORs the hash's top 16 bits into its bottom 16 so high bits influence the bucket.
- **Permission bits.** `mode & 0o022` tests whether a file is group- or world-writable.

## Key takeaways
- AND keeps or clears, OR sets, XOR flips; a mask selects which bits are affected.
- Set, clear, toggle and test bit *k* with `|=`, `&= ~`, `^=` and `&` using `1u << k`.
- Extract a field by shifting down then masking; pack by shifting up then OR-ing.
- Logical right shift fills with 0; arithmetic fills with the sign bit and rounds towards −∞, unlike C's `/`.
- In C, shifting by the promoted left operand's width or more is UB; `1 << 31` is UB for 32-bit int, and right shift of negative signed values is implementation-defined. Use appropriately wide unsigned types.
- C's `&` binds looser than `==`; always bracket `(x & m) == v`.
- `x & (x - 1)` clears the lowest set bit; `x & -x` isolates it; XOR cancels pairs.

## Further reading
- [Bitwise operation — Wikipedia](https://en.wikipedia.org/wiki/Bitwise_operation)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford](https://graphics.stanford.edu/~seander/bithacks.html)
- [Bitwise shift operators — cppreference (C)](https://en.cppreference.com/w/c/language/operator_arithmetic)
- [Bitwise operations on integer types — Python docs](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)
- [Bitboard — Chess Programming Wiki](https://www.chessprogramming.org/Bitboards)
