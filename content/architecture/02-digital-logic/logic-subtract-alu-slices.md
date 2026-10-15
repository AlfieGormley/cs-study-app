---
id: logic-subtract-alu-slices
title: Subtraction and ALU slices
level: intermediate
minutes: 3
sourceLesson: logic-adders-alu
summary: Invert the second operand and assert carry-in to subtract.
---

## Subtraction with the same adder

In two's complement, negating a number means inverting every bit and adding one. So subtraction is addition of the inverted bits plus one:

```formula
−B ≡ (B′ + 1) mod 2^n
A − B ≡ (A + B′ + 1) mod 2^n
0101 + 1100 + 1 = 1 0010
(0101 − 0011) mod 16 = 0010
(1 0010) mod 16 = 0010
where
A, B: n-bit values; arithmetic is reduced modulo the number of representable unsigned bit patterns
n: the fixed width in bits
mod: remainder after division
B′: B with every bit inverted (bitwise NOT)
+, −: ordinary binary addition and subtraction here, not OR
≡: congruent, meaning the same low n bits
16: the number of distinct four-bit patterns; taking the remainder keeps the low four bits
In words: to compute A − B, add A to the inverted B and add one more. The example is 5 − 3: 0101 + 1100 + 1 is 1 0010, and the low four bits 0010 are 2.
```

The adder already has a carry input. Put an XOR on each B input controlled by a `sub` signal, and feed `sub` into c0 (the adder's carry in) as well:

```formula
B_i ⊕ 1 = B_i′
B_i ⊕ 0 = B_i
where
B_i: bit i of the B input
B_i′: NOT B_i
⊕: XOR: 1 when the two sides differ
In words: XOR with sub = 1 inverts each B bit; XOR with sub = 0 passes it unchanged.
```

One circuit now adds and subtracts.

## Building an ALU

An ALU computes several operations in parallel on the same operands and uses a mux to pick one. A 1-bit **ALU slice**:

```
          +-------+
 a --+----|  AND  |------+
     | +--|       |      |  +-----+
     | |  +-------+      +--|0    |
     | |  +-------+         |     |
     +----|  OR   |---------|1 MUX|-- r
     | +--|       |         |     |
     | |  +-------+      +--|2    |
     | |  +-------+      |  +-----+
     +----| FULL  |------+     |
       +--| ADDER |            op
 b* ---+  +-------+
           ^     |
          cin   cout
```

`b*` is b XOR sub: b itself when adding, NOT b when subtracting. Put n slices side by side, chain the carries, and you have an n-bit ALU that can AND, OR, add and subtract. Real ALUs add XOR, shifts (via a **barrel shifter**, a tree of muxes whose depth is the base-2 logarithm of the width: 6 levels for 64 bits), comparisons and more.

## Key takeaways
- Invert the second operand and assert carry-in to subtract.
- Parallel logic results feed a mux that chooses the requested ALU operation.

## Further reading
- [MIT — Arithmetic structures](https://web.mit.edu/6.111/www/f2017/handouts/L08.pdf)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Adder (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Adder_(electronics))
- [Carry-lookahead adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-lookahead_adder)
- [Kogge–Stone adder — Wikipedia](https://en.wikipedia.org/wiki/Kogge%E2%80%93Stone_adder)
- [Arithmetic logic unit — Wikipedia](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Multiplexer — Wikipedia](https://en.wikipedia.org/wiki/Multiplexer)
- [Carry-save adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-save_adder)
