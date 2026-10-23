---
id: esc-bits-masks
title: Read and change selected bits
level: basic
minutes: 4
summary: Use unsigned masks without assuming every device register permits read modify write.
---

A **bit mask** selects positions within an integer. Number positions from zero at the least-significant bit, the rightmost position in a binary display. Bit zero has the value one, bit one the value two, and bit two the value four. Hexadecimal notation is a compact way to write the same pattern; C writes hexadecimal literals with a `0x` prefix.

## Four useful operations

**Bitwise AND** (`&`) keeps a position set only when both inputs have it set. **Bitwise OR** (`|`) sets a position when either input has it set. **Bitwise XOR** (`^`) sets a position when the inputs differ. **Bitwise NOT** (`~`) flips the bits of its promoted operand. These are integer operations, distinct from C's logical `&&` and `||`, which test truth and short-circuit evaluation.

This complete C11 host program operates on a local integer, not a device register. On the checked host, `uint32_t` and the constant macros used here operate as 32-bit unsigned values. Check the target's promoted operand types before generalising the inverted-mask expression:

```c
#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint32_t value = UINT32_C(0x05);
    const uint32_t bit1 = UINT32_C(1) << 1;
    value |= bit1;       // set: 0x07
    value &= ~UINT32_C(1); // clear: 0x06
    value ^= bit1;       // toggle: 0x04
    printf("%u\n", (unsigned)value);
    return 0;
}
```

It prints `4`. `|=` means update the left object with the OR result; the corresponding compound assignments do the same for the other operations. The comments show the intermediate values. To test a selected bit, use a condition such as `(value & bit1) != 0u`; the parentheses make the intended grouping explicit.

A **left shift** moves a pattern towards higher positions. `UINT32_C(1)` supplies a constant suitable for the corresponding least-width unsigned type; the operand used by the shift can undergo integer promotion. The shift by one here is defined on implementations providing the exact-width types. Never shift by a negative amount or by the width of the promoted left operand or more. General code also needs to avoid invalid signed shifts.

> [!analogy] Real-world analogy: changing labelled switches
> A row of labelled switches lets you change one selected position while keeping the others as they were.
>
> **How it maps:** A mask identifies the selected positions. OR sets them, AND with an inverted mask clears them, and XOR flips them in an ordinary integer value.
>
> **Where it stops:** A peripheral register may not store switches in this simple way. Reads can have effects, writes can use special meanings, and another execution context can change a value between your read and write.

## Ordinary integers and registers have different contracts

Compound assignment is a **read-modify-write** operation. It is not automatically an indivisible hardware update. A write-one-to-clear status register interprets a written one as a request to clear an event, rather than a new stored value. Reading its old bits and writing them back may clear events unintentionally. Some chips provide separate set and clear accessors; the RP2040 is one named example with documented atomic register aliases and exceptions. Use the actual register's contract, not a generic masking recipe.

## Key takeaways
- Masks select positions; bitwise operations differ from logical truth operators.
- Check the promoted operand type and valid shift range.
- Apply register-specific access rules before using read-modify-write on hardware.

## Further reading
- [C11 draft: integer promotions and bitwise operators](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [RP2040 datasheet: atomic register access and register definitions](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
