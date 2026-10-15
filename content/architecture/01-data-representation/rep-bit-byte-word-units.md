---
id: rep-bit-byte-word-units
title: Bits, words and storage units
level: basic
minutes: 4
summary: An octet is exactly eight bits; a C byte has at least eight.
sourceLesson: rep-number-systems
---

This unit continues the preceding material on binary place values.

## Bits, bytes and words

- **Bit**: a single 0 or 1.
- **Nibble**: 4 bits, one hex digit.
- **Byte**: today, 8 bits, the smallest addressable unit on common byte-addressed processors; some DSPs and other architectures differ. Standards documents say **octet** when they need to be unambiguous, because some historical machines used 6-, 7- or 9-bit bytes. C's `CHAR_BIT` is the number of bits in a byte (at least 8).
- **Word** (machine word): the natural unit a processor works with, usually the width of its general-purpose registers. A "64-bit CPU" usually has 64-bit general-purpose integer registers. Implemented virtual and physical address widths may be smaller and need not equal each other.

"Word" is overloaded. On x86, for historical reasons dating to the 16-bit 8086, a `WORD` is 16 bits, a `DWORD` 32 and a `QWORD` 64, even on a 64-bit chip. On ARM, a word is 32 bits. Always check which definition a document uses.

| Width | Unsigned range | Typical use |
|---|---|---|
| 8 bits | 0–255 | octets; ASCII fits in seven bits |
| 16 bits | 0–65,535 | ports, UTF-16 |
| 32 bits | 0–~4.29 × 10^9 | IPv4, `int` |
| 64 bits | 0–~1.8 × 10^19 | pointers, `long long` |

### KB or KiB?

Two families of prefixes describe sizes. SI prefixes are powers of ten; the IEC binary prefixes are powers of two:

```formula
1 kB = 10^3 B = 1,000 B
1 MB = 10^6 B = 1,000,000 B
1 GB = 10^9 B
1 KiB = 2^10 B = 1,024 B
1 MiB = 2^20 B = 1,048,576 B
1 GiB = 2^30 B = 1,073,741,824 B
where
B: byte, normally 8 bits
kB: kilobyte; the SI prefix kilo (k) means a thousand
MB: megabyte; mega (M) means a million
GB: gigabyte; giga (G) means a thousand million
KiB: kibibyte ("kilo binary"), 1,024 bytes
MiB: mebibyte, 1,024 KiB
GiB: gibibyte, 1,024 MiB
10^3: ten to the power 3, 10 × 10 × 10
2^10: 2 to the power 10: ten 2s multiplied together
In words: decimal (SI) prefixes step by 1,000 each time; binary (IEC) prefixes step by 1,024, so each binary unit is a little bigger than the decimal unit with the similar name.
```

Drive makers use SI; some operating systems report binary units with SI names. That is why a "1 TB" disk shows up as about 931 "GB" (really GiB):

```formula
1 TB = 10^12 B
(10^12 B) / (2^30 B) ≈ 931.3
where
TB: terabyte, 10^12 bytes (a million million)
B: byte
10^12: ten to the power 12, a 1 followed by 12 zeros
2^30: 1,073,741,824, the number of bytes in one gibibyte (GiB)
≈: approximately equal to (the result is rounded)
In words: a drive sold as 1 TB holds about 931 gibibytes, which some operating systems label "931 GB".
```

The gap grows with each prefix step, because every step multiplies by 1,024 instead of 1,000:

```formula
2^10 / 10^3 = 1.024
2^30 / 10^9 ≈ 1.074
2^40 / 10^12 ≈ 1.0995
10^12 / 2^40 ≈ 0.9095
where
2^10: 1,024, the bytes in one KiB; 10^3 is the 1,000 bytes in one kB
2^30: the bytes in one GiB; 10^9 is the bytes in one GB
2^40: 1,099,511,627,776, the bytes in one tebibyte (TiB); 10^12 is the bytes in one TB
≈: approximately equal to
In words: the binary unit is about 2.4% bigger at kilo, 7.4% at giga and 10.0% at tera; turned the other way round, 1 TB is only about 0.9095 TiB.
```

Those percentages are measured relative to the decimal unit size. The shortfall you see on screen uses a different denominator: 1 TB is about 0.9095 TiB, about 9.05% below the number 1.

## Key takeaways
- An octet is exactly eight bits; a C byte has at least eight.
- Machine word terminology depends on the architecture.
- Decimal and binary storage prefixes count different quantities.

## Further reading
- [Python integer conversion functions](https://docs.python.org/3/library/functions.html)
- [NIST binary prefixes](https://physics.nist.gov/cuu/Units/binary.html)
- [Binary number — Wikipedia](https://en.wikipedia.org/wiki/Binary_number)
- [Hexadecimal — Wikipedia](https://en.wikipedia.org/wiki/Hexadecimal)
- [Octal — Wikipedia](https://en.wikipedia.org/wiki/Octal)
- [Word (computer architecture) — Wikipedia](https://en.wikipedia.org/wiki/Word_(computer_architecture))
- [Binary prefix — Wikipedia](https://en.wikipedia.org/wiki/Binary_prefix)
- [Built-in functions (bin, hex, int) — Python docs](https://docs.python.org/3/library/functions.html)
