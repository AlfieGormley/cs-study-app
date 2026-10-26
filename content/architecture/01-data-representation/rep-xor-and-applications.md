---
id: rep-xor-and-applications
title: XOR identities and practical bit masks
level: intermediate
minutes: 4
summary: XOR cancels matching pairs and can reconstruct parity-protected data.
sourceLesson: rep-bitwise
---

XOR toggles the positions selected by another pattern. Applying the same toggle twice restores the original, which explains cancellation and parity.

### XOR's algebra

XOR has properties that make it unusually useful:

```formula essential
(a ⊕ k) ⊕ k = a
where
⊕: bitwise exclusive OR; a result bit is one when the input bits differ
a: the original integer bit pattern
k: the integer bit pattern used to toggle selected positions, applied twice at the same width
In words: applying the same XOR mask twice restores every original bit.
```

- A value XOR itself is 0, and XOR with 0 leaves a value alone.
- It is commutative and associative, so order does not matter.
- It is its own inverse: XOR-ing with the same key twice gets the original back.

Consequences:

- **Find the odd one out.** XOR every element of a list where every value appears twice except one. The pairs cancel and the single value is left. For a list of n fixed-width values that takes O(n) word operations (work growing in proportion to n) and O(1) auxiliary words (a fixed amount of extra memory); arbitrary-precision integer costs depend on bit length.
- **Parity.** XOR-ing all the bits gives 1 if the count of 1s is odd. RAID 5 stores the XOR of the data blocks so any one lost block can be rebuilt by XOR-ing the rest.
- **Toggle with a key.** A one-time pad XORs with a secret uniformly random message-length pad used only once. A stream cipher such as ChaCha20 XORs plaintext with a generated keystream, not directly with its short secret key. Repeating the same XOR recovers the input; that identity alone does not provide secure encryption.

```python
# Repeated values cancel, leaving 2.
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
- XOR cancels matching pairs and can reconstruct parity-protected data.
- Remainder becomes a mask only for a nonzero power-of-two size.
- An XOR identity alone does not provide secure encryption.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [Python bitwise integer operations](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)
- [Bitwise operation — Wikipedia](https://en.wikipedia.org/wiki/Bitwise_operation)
- [GCC bit-operation builtins](https://gcc.gnu.org/onlinedocs/gcc/Bit-Operation-Builtins.html)
- [Bitwise shift operators — cppreference (C)](https://en.cppreference.com/w/c/language/operator_arithmetic)
- [Bitwise operations on integer types — Python docs](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)
- [Bitboard — Chess Programming Wiki](https://www.chessprogramming.org/Bitboards)
