---
id: rep-binary-place-values
title: Reading binary place values
level: basic
minutes: 3
summary: Each position has a weight fixed by the base.
sourceLesson: rep-number-systems
---

Digital computers represent numbers, text, pictures and programs using binary states. These logical states are implemented by storage and signalling hardware; there need not be one literal switch per bit. We write the two states as `0` and `1`. One binary digit is a **bit**.

Bits need an interpretation. The eight bits `01000001` can mean the number 65, the letter `A`, part of a pixel or part of an instruction. The surrounding format or program decides which meaning applies.

## Positions carry the value

In decimal, `472` means four hundreds, seven tens and two ones. Moving a digit one position left makes its contribution ten times larger. Ten is the **number base**, also called the **radix**.

Binary uses two digits, so each position is worth twice the one to its right. For an unsigned eight-bit number:

```
bit position:  7   6   5   4  3  2  1  0
weight:      128  64  32  16  8  4  2  1
```

A `1` includes that position's weight; a `0` contributes nothing. In `0000 0101`, the positions worth four and one are set, so the value is five. Moving that pattern left one place gives ten, provided the storage has room for the shifted bits.

The rightmost bit is the **least significant bit** (LSB). It decides whether an unsigned integer is odd. The leftmost is the **most significant bit** (MSB); in this unsigned interpretation it has the largest positive weight. Signed representations give it a different role, covered later.

> [!analogy] Real-world analogy: Labelled coin trays
> Imagine trays labelled one, two, four and eight, with room for one coin in each.
>
> **How it maps:** An occupied tray contributes its labelled value, just as a set bit contributes its positional weight. The label matters as much as whether the tray is occupied.
>
> **Where it stops:** Hardware stores two logical states rather than coins. The weighting describes unsigned numbers; text and signed numbers use other interpretations.

## More bits mean more choices

Adding one bit doubles the number of possible patterns: each old pattern can now appear with a new leading zero or a new leading one. Eight bits give 256 patterns. An unsigned eight-bit field uses them for zero through 255; zero uses one of the patterns.

When designing an identifier field, count all the states it must distinguish, including any reserved values. A field with 512 patterns cannot distinguish 1,000 identifiers. Adding one bit gives 1,024 patterns and makes that possible. Changing the display from binary to decimal does not create extra capacity.

This relationship is useful when sizing a field:

```formula reference
P = 2^n
where
P: the number of distinct patterns, a dimensionless count
n: the number of independent bits
2^n: two raised to the number of bits; each additional bit doubles the count
In words: each extra bit doubles the available patterns; eight bits provide 256 distinct choices.
```

A larger range does not itself define what happens when an arithmetic result exceeds it. The integer units distinguish hardware results from language rules.

## Key takeaways
- Binary positions double in weight as you move left.
- A bit pattern needs a format or type to give it meaning.
- Each extra bit doubles capacity; reserved states reduce the usable choices.

## Further reading
- [Python integer conversion functions](https://docs.python.org/3/library/functions.html)
- [NIST binary prefixes](https://physics.nist.gov/cuu/Units/binary.html)
