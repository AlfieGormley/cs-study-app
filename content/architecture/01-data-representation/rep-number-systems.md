---
id: rep-number-systems
title: Number systems and bases
level: basic
minutes: 11
summary: Binary, hexadecimal and octal, how to convert between them by hand, and what bits, bytes and words really are.
---

Digital computers represent numbers, text, pictures and programs using binary states. These are logical states, implemented by physical storage and signalling technologies rather than necessarily one literal switch per bit. We write those states as `0` and `1`. A single one is a **bit** (binary digit).

Bits on their own are meaningless. The same eight bits `01000001` are the number 65, the letter `A`, part of a pixel or part of a machine instruction, depending on how a program chooses to read them. This module is about those choices. It starts with the most basic one: reading a row of bits as a number.

## Positional notation

You already use a positional system. In decimal, `472` means 4 hundreds, 7 tens and 2 ones. Written with powers of ten (a small raised number says how many tens are multiplied together):

```formula
472 = 4 × 10^2 + 7 × 10^1 + 2 × 10^0
472 = 400 + 70 + 2
where
10^2: ten to the power 2, meaning 10 × 10 = 100: the weight of the hundreds position
10^1: ten to the power 1, which is just 10: the weight of the tens position
10^0: ten to the power 0, which is 1 by definition (any non-zero number to the power 0 is 1): the weight of the ones position
In words: each digit is multiplied by the value of its position, and the results are added: 4 hundreds plus 7 tens plus 2 ones.
```

Each position is worth ten times the one to its right, because there are ten digits (0 to 9). The ten is the **base** (or **radix**).

Every positional system, in any base, follows the same rule. Written generally, it is the formula below; you will use it for binary, hexadecimal and octal in this lesson:

```formula
N = Σ d_i × b^i
where
N: the value of the number
Σ: sigma, meaning "add up": add the term after it once for every digit position i, from the rightmost (i = 0) to the leftmost
d_i: the digit in position i; a whole number from 0 up to one less than the base
i: the position number, counted from 0 at the right-hand end
b: the base (radix): how many different digits the system has; 10 for decimal, 2 for binary, 16 for hexadecimal, 8 for octal
b^i: b to the power i, meaning b multiplied by itself i times; b^0 is 1
In words: multiply every digit by the base raised to the power of its position, then add all the products.
```

For `472` the base *b* is 10 and the digits are *d_2* = 4, *d_1* = 7 and *d_0* = 2, which gives exactly the sum above. The formula only covers whole numbers; fractions come at the end of the lesson.

Nothing is special about ten. In **base 2** there are two digits, 0 and 1, and each position is worth twice the one to its right:

```
bit position:  7   6   5   4  3  2  1  0
weight:      128  64  32  16  8  4  2  1
```

So `10110101` in binary is the same positional formula with base 2. Only the positions holding a 1 contribute:

```formula
N = Σ d_i × 2^i
N = 2^7 + 2^5 + 2^4 + 2^2 + 2^0
N = 128 + 32 + 16 + 4 + 1 = 181
where
N: the value of the bit pattern 10110101 read as an unsigned binary number (no sign)
Σ: "add up" the term after it for every bit position i
d_i: the bit (0 or 1) in position i
i: the bit position, from 0 at the right to 7 at the left
2^i: 2 multiplied by itself i times: the weight of position i, so 2^7 = 128 and 2^0 = 1
In words: add the weights of the positions that hold a 1; positions holding a 0 add nothing.
```

The rightmost bit (weight 1) is the **least significant bit** (LSB). The leftmost is the **most significant bit** (MSB). Positions are numbered from 0 at the right, so a bit's position number is also the power of two it is worth: bit 0 is worth 1 and bit 7 is worth 128.

### Counting values

Each extra bit doubles the number of different patterns, because every existing pattern can be followed by either a 0 or a 1:

```formula
P = 2^n
2^8 = 256
2^16 = 65,536
2^32 = 4,294,967,296
where
P: the number of different bit patterns, and so the number of different values, that n bits can hold
n: the number of bits
2^n: 2 multiplied by itself n times
In words: n bits can be set in 2 to the power n different ways, so 8 bits give 256 patterns and 32 bits about 4.3 billion.
```

64 bits give about 1.8 × 10^19 patterns. That is scientific notation: 1.8 multiplied by ten to the power 19, an 18 followed by 18 zeros.

## Decimal to binary by hand

There are two standard methods. Both give the same answer.

### Method 1: subtract powers of two

Find the largest power of two that fits, subtract it, and repeat. For 181:

```
181 - 128 = 53   bit 7 = 1
 53 -  64 ✗      bit 6 = 0
 53 -  32 = 21   bit 5 = 1
 21 -  16 =  5   bit 4 = 1
  5 -   8 ✗      bit 3 = 0
  5 -   4 =  1   bit 2 = 1
  1 -   2 ✗      bit 1 = 0
  1 -   1 =  0   bit 0 = 1
```

Result: `10110101`.

### Method 2: repeated division by two

Divide by 2, write down the remainder, and repeat with the quotient (the whole-number result) until it reaches 0. The remainders, read **from bottom to top**, are the bits.

```formula
181 ÷ 2 = 90 r 1   ← LSB
90 ÷ 2 = 45 r 0
45 ÷ 2 = 22 r 1
22 ÷ 2 = 11 r 0
11 ÷ 2 = 5 r 1
5 ÷ 2 = 2 r 1
2 ÷ 2 = 1 r 0
1 ÷ 2 = 0 r 1   ← MSB
where
÷: whole-number division: keep only the whole part of the answer (the quotient)
r: remainder: what is left over after the division; when dividing by 2 it is always 0 or 1
LSB: least significant bit, the rightmost bit, worth 1; the first remainder
MSB: most significant bit, the leftmost bit; the last remainder
In words: halve the number again and again, noting the remainder each time; the remainders, read from the last back to the first, are the binary digits.
```

Reading upwards: `10110101` again. This method works for any base: divide by 16 to get hexadecimal digits, by 8 for octal.

## Hexadecimal: binary for humans

Long binary strings are hard to read. **Hexadecimal** (base 16) fixes this. It needs sixteen digits, so after 9 it uses letters:

| Dec | Bin | Hex |
|---|---|---|
| 0–9 | 0000–1001 | 0–9 |
| 10 | 1010 | A |
| 11 | 1011 | B |
| 12 | 1100 | C |
| 13 | 1101 | D |
| 14 | 1110 | E |
| 15 | 1111 | F |

The key fact: 16 is 2 × 2 × 2 × 2 (2 to the power 4), so **one hex digit is exactly four bits** (a **nibble**). Converting between binary and hex needs no arithmetic at all. You just group bits in fours from the right:

```
1011 0101
   B    5     → 0xB5
```

And back again, expanding each hex digit into four bits:

```
0x2F3A
  2    F    3    A
0010 1111 0011 1010
```

Two hex digits represent one eight-bit byte, which is why memory dumps, colours (`#1E90FF`), MAC addresses and hashes are often written in hex.

### Hex to decimal

Use the positional formula with base 16. The weights are powers of 16 (1, 16, 256, 4096, 65536):

```formula
0x2F3A = 2 × 16^3 + 15 × 16^2
       + 3 × 16^1 + 10 × 16^0
0x2F3A = 2 × 4096 + 15 × 256 + 3 × 16 + 10
0x2F3A = 8192 + 3840 + 48 + 10 = 12090
where
0x2F3A: the hexadecimal number 2F3A; the 0x prefix marks base 16 in C and Python. Its digits F and A stand for 15 and 10
16^3: 16 × 16 × 16 = 4096, the weight of the fourth digit from the right
16^2: 16 × 16 = 256, the weight of the third digit
16^1: 16, the weight of the second digit
16^0: 1, the weight of the rightmost digit
In words: multiply each hex digit by its power of 16 and add, exactly as you would with powers of 10 in decimal.
```

The same method works for any base: only the weights change.

## Octal: three bits per digit

**Octal** (base 8) uses digits 0 to 7. Since 8 is 2 × 2 × 2 (2 to the power 3), each octal digit is exactly three bits. Group from the right in threes:

```
10 110 101
 2   6   5   → 0o265  (2×64 + 6×8 + 5 = 181)
```

The `0o` prefix marks octal in Python, and the octal weights are 64, 8 and 1.

Octal was popular on machines with 12-, 18- and 36-bit words, which split evenly into threes. Today you mostly meet it in **Unix file permissions**, where each digit is one `rwx` triple:

```
chmod 755 file
  7 = 111 = rwx  (owner)
  5 = 101 = r-x  (group)
  5 = 101 = r-x  (others)
```

> [!warning] The leading-zero trap in C
> An integer literal such as `010` is octal in C, C++ and Java, and in JavaScript legacy non-strict syntax. Other prefixes and floating literals have separate rules; JavaScript legacy literals containing 8 or 9 may instead be decimal. `int x = 010;` sets `x` to **8**, not 10. Zero-padding numbers to line them up in a table of constants can silently change their values. Python 3 refuses `010` with a `SyntaxError` and makes you write `0o10`.

## Bases in code

Python has built-ins for every direction:

```python
bin(181)          # '0b10110101'
hex(181)          # '0xb5'
oct(181)          # '0o265'
int('b5', 16)     # 181
int('10110101', 2)  # 181
format(181, '08b')  # '10110101'
0b1010 + 0x0F     # 25
```

In C, literals can be written as `181`, `0xB5` or `0265` (octal). `printf` prints hex with `%x` and octal with `%o`. Binary literals (`0b10110101`) and a `%b` conversion were only standardised in **C23**, though GCC and Clang accepted `0b` literals as an extension for years.

```c
printf("%x %o\n", 181u, 181u);
// prints: b5 265
```

## Fractions in binary

Positions to the right of the point have weights 1/2, 1/4, 1/8 and so on: the powers of two continue below 1. So `0.101` in binary is:

```formula
0.101_2 = 1 × 2^−1 + 0 × 2^−2 + 1 × 2^−3
0.101_2 = 1/2 + 0 + 1/8 = 0.625
where
0.101_2: the digits 0.101 read in base 2; the small 2 written below the number names the base
2^−1: 2 to the power −1, which means 1/2 = 0.5; a negative power means "1 divided by" the positive power
2^−2: 1/(2 × 2) = 1/4 = 0.25
2^−3: 1/(2 × 2 × 2) = 1/8 = 0.125
In words: the first place after the binary point is worth a half, the next a quarter, the next an eighth; add the ones that hold a 1.
```

To convert a decimal fraction, **multiply by 2** repeatedly and take the integer parts, reading **top to bottom**:

```
0.625 × 2 = 1.25   → 1
0.25  × 2 = 0.5    → 0
0.5   × 2 = 1.0    → 1   (stop: 0 left)
0.625 = 0.101₂
```

Try 0.1 and something unsettling happens:

```
0.1 × 2 = 0.2 → 0
0.2 × 2 = 0.4 → 0
0.4 × 2 = 0.8 → 0
0.8 × 2 = 1.6 → 1
0.6 × 2 = 1.2 → 1
0.2 × 2 = 0.4 → 0   (repeats from here)
0.1 = 0.0001100110011...₂
```

It never terminates, just as 1/3 never terminates in decimal. A fraction terminates in a given base if and only if, after reducing it to lowest terms, every prime factor of its denominator also divides the base. For example, 3/8 has denominator 8 = 2 × 2 × 2, so it ends in binary (`0.011`). Ten is 2 × 5, so 1/10 has a factor of 5 that base 2 cannot express. This is the root of the floating-point surprises in lesson 4.

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
10^12 B / 2^30 B ≈ 931.3
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
- A positional number weights each position by a power of its base; binary weights are 1, 2, 4, 8, 16...
- Convert decimal to binary by subtracting powers of two, or by repeated division by 2, reading the remainders from bottom to top.
- One hex digit is exactly 4 bits and one octal digit exactly 3 bits, so conversion is just regrouping.
- A leading 0 on an unprefixed C integer literal makes it octal: 010 is 8; hexadecimal, binary and floating literals have different rules.
- Fractions like 0.1 have no finite binary form, which is why floating point is approximate.
- An octet is 8 bits; a C byte contains CHAR_BIT bits (at least 8); a "word" depends on context (16 bits in x86 naming, 32 on ARM, 64 for a modern register).

## Further reading
- [Binary number — Wikipedia](https://en.wikipedia.org/wiki/Binary_number)
- [Hexadecimal — Wikipedia](https://en.wikipedia.org/wiki/Hexadecimal)
- [Octal — Wikipedia](https://en.wikipedia.org/wiki/Octal)
- [Word (computer architecture) — Wikipedia](https://en.wikipedia.org/wiki/Word_(computer_architecture))
- [Binary prefix — Wikipedia](https://en.wikipedia.org/wiki/Binary_prefix)
- [Built-in functions (bin, hex, int) — Python docs](https://docs.python.org/3/library/functions.html)
