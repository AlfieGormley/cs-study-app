---
id: logic-alu-flags-model
title: ALU flags and comparisons
level: intermediate
minutes: 3
sourceLesson: logic-adders-alu
summary: Carry and signed overflow answer different questions.
---

### The flags

Our teaching ALU reports N/Z/C/V-style condition flags. Architectures such as ARM use these; other ISAs, including base RISC-V, use different comparison mechanisms without such an architectural flag register:

| Flag | Meaning | Computed as |
|---|---|---|
| N | Negative | MSB of result |
| Z | Zero | NOR of all result bits |
| C | Carry | carry out of MSB |
| V | Signed overflow | carry into MSB ⊕ carry out of MSB |

For an n-bit result, the four flags are:

```formula
N = r_{n−1}
Z = (r_{n−1} + … + r_1 + r_0)′
C = c_n
V = c_{n−1} ⊕ c_n
where
n: the width in bits; bits are numbered 0 (least significant) to n − 1 (the MSB, the sign bit)
r_0, r_1, r_{n−1}: bits of the result
…: the bits in between
c_n: the carry out of the MSB
c_{n−1}: the carry into the MSB
N, Z, C, V: the negative, zero, carry and overflow flags, each 0 or 1
+: OR
( )′: NOT of the whole bracket, so OR then NOT is a NOR
⊕: XOR: 1 when the two sides differ
In words: N copies the sign bit, Z is 1 only when every result bit is 0, C is the carry out of the top bit, and V is 1 when the carry into the top bit differs from the carry out of it.
```

The **V** rule deserves a moment. Signed overflow happens when two numbers of the same sign produce a result of the other sign, such as 7 + 1 in 4 bits giving `1000`, which is -8. That happens exactly when the carry into the sign bit differs from the carry out of it: in 0111 + 0001, a carry of 1 enters bit 3 but none leaves it, so V = 1 XOR 0 = 1.

### Comparisons come free

A compare instruction (`cmp` on x86 and ARM) is a subtraction that keeps only the flags. After computing A − B:

```formula
A = B       if Z = 1
A <_u B     if C = 0
A <_s B     if N ≠ V
where
A, B: the two operands being compared
Z: the zero flag: 1 when A − B is 0
C: the carry flag, using the ARM convention: the adder's real carry out of A + B′ + 1. C = 0 means a borrow occurred, so A was smaller as an unsigned number. (x86 inverts this: its CF = 1 means a borrow.)
<_u: less than, treating both as unsigned numbers
<_s: less than, treating both as signed two's-complement numbers
N: the negative flag (sign bit of A − B)
V: the signed overflow flag
≠: is not equal to
In words: equal if the difference is zero; unsigned-less if the subtraction borrowed; signed-less if the sign flag and overflow flag disagree. N alone is wrong when the subtraction overflowed, because overflow flips the sign bit.
```

> [!warning] The carry flag's meaning after subtraction differs by ISA
> Arm-style subtraction sets carry when there is **no borrow**; x86 subtraction sets CF when there **is a borrow**. Both describe unsigned comparison, with opposite polarity. These rules concern subtraction instructions that update the relevant flags; consult the ISA for the selected instruction.

## Key takeaways
- Carry and signed overflow answer different questions.
- Unsigned subtraction uses borrow conventions; signed less-than accounts for overflow.

## Further reading
- [MIT — Arithmetic structures](https://web.mit.edu/6.111/www/f2017/handouts/L08.pdf)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Adder (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Adder_(electronics))
- [Carry-lookahead adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-lookahead_adder)
- [Kogge–Stone adder — Wikipedia](https://en.wikipedia.org/wiki/Kogge%E2%80%93Stone_adder)
- [Arithmetic logic unit — Wikipedia](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Multiplexer — Wikipedia](https://en.wikipedia.org/wiki/Multiplexer)
- [Carry-save adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-save_adder)
