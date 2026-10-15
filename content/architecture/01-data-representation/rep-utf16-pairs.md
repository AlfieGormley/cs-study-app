---
id: rep-utf16-pairs
title: UTF-16 units and surrogate pairs
level: intermediate
minutes: 3
summary: Supplementary scalar values use a high/low surrogate pair.
sourceLesson: rep-text-encoding
---

This unit continues the preceding material on Unicode scalar values and their encodings.

## UTF-16 and surrogate pairs

**UTF-16** uses 16-bit **code units**. BMP scalar values (excluding D800–DFFF) take one unit. Code points above U+FFFF take two, called a **surrogate pair**, built from a range of the BMP (U+D800 to U+DFFF) reserved so that no character uses it.

To encode a code point above U+FFFF:

1. Subtract 0x10000, leaving a 20-bit number.
2. The top 10 bits plus 0xD800 give the **high surrogate**.
3. The low 10 bits plus 0xDC00 give the **low surrogate**.

As a formula:

```formula
v = c − 0x10000
H = 0xD800 + ⌊v / 0x400⌋
L = 0xDC00 + (v mod 0x400)
where
c: the code point, from 0x10000 up to 0x10FFFF
v: c minus 0x10000, a 20-bit number from 0 to 0xFFFFF
H: the high surrogate code unit, 0xD800 to 0xDBFF: 0xD800 plus the top 10 bits of v
L: the low surrogate code unit, 0xDC00 to 0xDFFF: 0xDC00 plus the low 10 bits of v
0x400: 1,024, which is 2 to the power 10
⌊ ⌋: floor: round down to a whole number; dividing by 0x400 and rounding down keeps the top 10 bits
mod: modulo, the remainder after division; v mod 0x400 is the low 10 bits
In words: split the 20-bit offset into a top half and a bottom half of 10 bits each, and add each half to the start of its reserved surrogate range.
```

For 😀 (U+1F600):

```
0x1F600 - 0x10000 = 0x0F600
= 0000 1111 01 | 10 0000 0000
top 10:  0x03D  -> D800 + 03D = D83D
low 10:  0x200  -> DC00 + 200 = DE00
```

So 😀 in UTF-16 is `D83D DE00`. Because of the reserved surrogate block, those 2,048 values can never be characters, leaving 1,112,064 valid **scalar values**.

UTF-16 extends an earlier 16-bit design with surrogate pairs. Java, JavaScript, Windows W APIs, .NET and Qt use 16-bit code units in their string interfaces; their adoption histories differ, so they cannot all be described as pre-1996 adopters. UTF-16 also has byte-order variants (UTF-16LE and UTF-16BE), often signalled by a **byte order mark** (BOM), U+FEFF, at the start of the file.

## Key takeaways
- Supplementary scalar values use a high/low surrogate pair.
- UTF-16 serialisation needs a byte-order convention.

## Further reading
- [Unicode 17 conformance and encoding forms](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)
- [RFC 3629: UTF-8](https://www.rfc-editor.org/rfc/rfc3629)
