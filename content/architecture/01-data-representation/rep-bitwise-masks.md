---
id: rep-bitwise-masks
title: Bitwise operators and single-bit masks
level: intermediate
minutes: 3
summary: AND keeps selected bits, OR sets them and XOR toggles them.
sourceLesson: rep-bitwise
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

A **bit mask** (often just called a mask) is a bit pattern whose 1s pick out the positions you care about. Choosing the operator decides what happens to those positions.

> [!warning] Bitwise is not logical
> `&&` and `||` in C (and `and` / `or` in Python) are **logical** operators. They treat each whole operand as true or false and short-circuit. `2 & 1` is 0, but `2 && 1` is 1.

## The four mask idioms

For an unsigned int `x` and a bit position `k` (from 0 up to one less than the width of `x` in bits), build the mask `1u << k`, which has a single 1 in position `k`. A wider `x` needs a correspondingly wide unsigned mask; complementing a 32-bit mask before widening it would clear the upper bits of a 64-bit x.

```c
/* Each update selects just bit k. */
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

## Key takeaways
- AND keeps selected bits, OR sets them and XOR toggles them.
- Use an unsigned mask wide enough for the operand.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [Python bitwise integer operations](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)
