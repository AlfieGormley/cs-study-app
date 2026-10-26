---
id: rep-finite-binary-fractions
title: Finite and repeating binary fractions
level: basic
minutes: 3
summary: Fractional binary positions have weights one half, one quarter and so on.
sourceLesson: rep-number-systems
---

A decimal fraction can be simple to write and still need infinitely many binary digits. This matters whenever a fixed-size binary format stores measurements or prices.

## The positions continue past the point

To the right of the binary point, the positions are worth one half, one quarter, one eighth and so on. A binary `0.101` includes a half and an eighth, giving decimal 0.625. The zero skips the quarter position.

A fraction terminates in binary only when its denominator, after reducing to lowest terms, is a power of two. For example, three eighths terminates; one tenth does not, because its denominator contains a factor of five.

Decimal has its own limitation: one third repeats forever in base ten. Repetition is a property of the value and chosen base, not a fault in a particular computer.

## What a finite format must do

Binary one tenth starts `0.0001100110011...`, with a repeating tail. More bits improve the approximation but no finite number of binary fraction positions makes one tenth exact.

For a hand conversion, repeatedly double the remaining fraction. The whole-number part gives the next binary digit; continue with the fractional remainder. Reaching a zero remainder means the expansion terminates. Returning to an earlier nonzero remainder means the same digits will repeat. You do not need to carry out the whole expansion to diagnose the representability problem.

A fixed-size floating-point format must also have enough significant bits and exponent range. A terminating binary fraction can still be too large, too small or require more precision than that particular format provides.

For decimal quantities that must remain exact, choose a suitable decimal representation or integer units with an explicit rounding policy. For approximate measurements, binary floating point is often appropriate; later lessons explain its rounding and precision limits.

## Key takeaways
- Binary fraction positions successively halve in weight.
- A reduced denominator containing factors other than two gives a repeating binary expansion.
- Termination alone does not guarantee that a particular fixed-size format can store the value.

## Further reading
- [Python integer conversion functions](https://docs.python.org/3/library/functions.html)
- [NIST binary prefixes](https://physics.nist.gov/cuu/Units/binary.html)
