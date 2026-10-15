---
id: rep-converting-bases
title: Converting binary and hexadecimal
level: basic
minutes: 4
summary: Repeated division records digits from least to most significant.
sourceLesson: rep-number-systems
---

This unit continues the preceding material on binary place values.

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

## Key takeaways
- Repeated division records digits from least to most significant.
- Group binary digits in fours to read hexadecimal.

## Further reading
- [Python integer conversion functions](https://docs.python.org/3/library/functions.html)
- [NIST binary prefixes](https://physics.nist.gov/cuu/Units/binary.html)
