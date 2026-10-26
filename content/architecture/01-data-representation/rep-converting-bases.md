---
id: rep-converting-bases
title: Converting binary and hexadecimal
level: basic
minutes: 3
summary: Repeated division records digits from least to most significant.
sourceLesson: rep-number-systems
---

Hexadecimal makes long bit patterns easier to read without changing their value. Use it for memory dumps, masks and encoded fields; use decimal when the number's everyday magnitude matters.

## One hex digit represents four bits

**Hexadecimal** is base 16. Its digits run from 0 to 9, then A to F for ten through fifteen. A **nibble** is four bits, so it has exactly the sixteen patterns needed for one hex digit.

| Hex | Bits | Decimal |
|---|---|---|
| 0 | 0000 | 0 |
| 5 | 0101 | 5 |
| A | 1010 | 10 |
| B | 1011 | 11 |
| C | 1100 | 12 |
| F | 1111 | 15 |

Group binary digits in fours from the right. Keep four positions for each hex digit, including zeros inside the complete number:

```
1011 0101
   B    5     -> 0xB5
```

`0x` marks a hex integer literal in C and Python. Two hex digits represent an eight-bit byte. For example, bytes `C0 A8 01 0A` keep their boundaries only if the `01` and `0A` retain both digits. Dropping their zeros before joining the digits changes the value.

## Conversion changes the spelling

The same integer can be displayed in different bases:

```python
# Each conversion describes the same value.
value = 181
bin(value)       # '0b10110101'
hex(value)       # '0xb5'
int('b5', 16)    # 181
```

Hexadecimal is still positional: its rightmost position counts ones, the next counts sixteens and the next counts groups of 256. There is no special hexadecimal arithmetic inside the integer after parsing.

## Why repeated division works

To convert a non-negative integer by hand, divide by the target base and record the remainder. The remainder is the lowest digit: everything in the quotient belongs to higher positions. Repeat on the quotient, then read the recorded digits in reverse order.

For decimal 200, division by sixteen leaves twelve groups and eight left over. The eight is the low digit; twelve is written C as a single hex digit. The result is `0xC8`. Writing `0x8C` reverses the position weights.

This explains the conversion mechanism; a language's conversion functions are preferable for routine work. When inspecting a dump, preserving digit grouping and knowing the field's meaning is more useful than repeatedly calculating its decimal value.

## Key takeaways
- One hex digit represents exactly four bits.
- Keep internal zeros so bit and byte boundaries survive.
- Repeated division discovers the lowest digit first.

## Further reading
- [Python integer conversion functions](https://docs.python.org/3/library/functions.html)
- [NIST binary prefixes](https://physics.nist.gov/cuu/Units/binary.html)
