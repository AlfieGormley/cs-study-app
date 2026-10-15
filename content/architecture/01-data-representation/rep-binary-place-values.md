---
id: rep-binary-place-values
title: Reading binary place values
level: basic
minutes: 5
summary: Each position has a weight fixed by the base.
sourceLesson: rep-number-systems
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

Each position is worth ten times the one to its right, because there are ten digits (0 to 9). The ten is the **number base** (or **radix**).

Every positional system, in any base, follows the same rule. Written generally, it is the formula below; you will use it for binary, hexadecimal and octal in this lesson:

```formula
N = Σ d_i b^i
where
N: the value of the number
Σ: sigma, meaning "add up": add the term after it once for every digit position i, from the rightmost (i = 0) to the leftmost
d_i: the digit in position i; a whole number from 0 up to one less than the base
i: the position number, counted from 0 at the right-hand end
b: the base (radix): how many different digits the system has; 10 for decimal, 2 for binary, 16 for hexadecimal, 8 for octal
b^i: b to the power i, meaning i copies of b multiplied together; b^0 is 1
In words: multiply every digit by the base raised to the power of its position, then add all the products.
```

For decimal 472, use base ten and the digits four, seven and two from left to right; that gives exactly the sum above. The formula only covers whole numbers; fractions are covered in a later short unit.

Nothing is special about ten. In **base 2** there are two digits, 0 and 1, and each position is worth twice the one to its right:

```
bit position:  7   6   5   4  3  2  1  0
weight:      128  64  32  16  8  4  2  1
```

So `10110101` in binary is the same positional formula with base 2. Only the positions holding a 1 contribute:

```formula
N = Σ d_i 2^i
N = 2^7 + 2^5 + 2^4 + 2^2 + 2^0
N = 128 + 32 + 16 + 4 + 1 = 181
where
N: the value of the bit pattern 10110101 read as an unsigned binary number (no sign)
Σ: "add up" the term after it for every bit position i
d_i: the bit (0 or 1) in position i
i: the bit position, from 0 at the right to 7 at the left
2^i: i copies of 2 multiplied together: the weight of position i, so 2^7 = 128 and 2^0 = 1
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
2^n: n copies of 2 multiplied together
In words: n bits can be set in 2 to the power n different ways, so 8 bits give 256 patterns and 32 bits about 4.3 billion.
```

For 64 bits, the same rule gives 18,446,744,073,709,551,616 patterns, about eighteen million million million. Scientific notation is a compact way to express this:

```formula
P = 2^64 ≈ 1.8 × 10^19
where
P: the dimensionless count of patterns for 64 independent bits
≈: approximately equal to, after rounding
In words: sixty-four binary choices produce about eighteen million million million patterns.
```

## Key takeaways
- Each position has a weight fixed by the base.
- An extra bit doubles the available patterns.

## Further reading
- [Python integer conversion functions](https://docs.python.org/3/library/functions.html)
- [NIST binary prefixes](https://physics.nist.gov/cuu/Units/binary.html)
