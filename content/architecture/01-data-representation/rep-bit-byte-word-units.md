---
id: rep-bit-byte-word-units
title: Bits, words and storage units
level: basic
minutes: 3
summary: An octet is exactly eight bits; a C byte has at least eight.
sourceLesson: rep-number-systems
---

A size is meaningful only with its unit. Bytes, machine words and storage prefixes answer different questions, and some names depend on the platform.

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

Decimal prefixes step by 1,000; binary prefixes step by 1,024. The `i` distinguishes the binary names.

| Decimal unit | Bytes | Binary unit | Bytes |
|---|---|---|---|
| kB | 1,000 | KiB | 1,024 |
| MB | 1,000,000 | MiB | 1,048,576 |
| GB | 1,000,000,000 | GiB | 1,073,741,824 |

Drive makers normally advertise decimal capacity. A drive sold as 1 TB contains a million million bytes, about 931 GiB. Counting the same bytes in larger units produces a smaller displayed number. Some software labels that binary count “GB”, which makes the difference look like missing space.

Check the unit before comparing capacities. Formatting, partitions and reserved storage can reduce usable space separately; a unit conversion alone neither removes bytes nor explains every capacity difference.

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
