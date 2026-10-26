---
id: rep-octal-and-literals
title: Octal permissions and code literals
level: basic
minutes: 3
summary: Octal groups bits in threes, matching Unix permission triples.
sourceLesson: rep-number-systems
---

Octal is useful when a field naturally groups bits in threes. In code, choosing the wrong literal prefix can silently change a constant.

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
# Convert the same value between bases.
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
/* Unsigned arguments match %x and %o. */
printf("%x %o\n", 181u, 181u);
// prints: b5 265
```

## Key takeaways
- Octal groups bits in threes, matching Unix permission triples.
- A leading zero changes a C integer literal to octal.

## Further reading
- [Python integer conversion functions](https://docs.python.org/3/library/functions.html)
- [NIST binary prefixes](https://physics.nist.gov/cuu/Units/binary.html)
