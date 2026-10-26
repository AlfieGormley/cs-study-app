---
id: logic-carry-lookahead
title: Generate, propagate and carry lookahead
level: intermediate
minutes: 4
sourceLesson: logic-adders-alu
summary: Generate creates a carry; propagate passes one from below.
---

## Carry-lookahead: compute carries in parallel

The insight is that each bit position can say, *before* knowing its carry in, what it will do with one:

- **Generate signal**: this column produces a carry regardless of its carry in (both bits are 1).
- **Propagate signal**: this column passes a carry in through to its carry out (exactly one bit is 1).

Written as equations, with the carry rule that follows from them:

```formula essential
G_i = A_i·B_i
P_i = A_i ⊕ B_i
C_{i+1} = G_i + P_i·C_i
where
i: the bit position, counting from 0 at the least significant bit
A_i, B_i: bit i of the two numbers being added
G_i: generate for bit i (Gi in the text): 1 when this column makes a carry by itself
P_i: propagate for bit i (Pi in the text): 1 when this column passes an incoming carry on
C_i: the carry into bit i; C_0 is the adder's carry in
C_{i+1}: the carry out of bit i, which is the carry into bit i + 1
⊕: XOR: 1 when the two bits differ
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: a carry leaves column i if the column generates one, or if it propagates a carry that arrived from below.
```

A carry can originate at any lower bit, but it reaches the target only if every intervening bit propagates it. Lookahead tests these possible routes in parallel, using input-derived signals rather than waiting for a carry to ripple through each column. The expanded equations are a reference for wiring a four-bit block:

```formula reference
C_1 = G_0 + P_0·C_0
C_2 = G_1 + P_1·G_0 + P_1·P_0·C_0
C_3 = G_2 + P_2·G_1 + P_2·P_1·G_0
    + P_2·P_1·P_0·C_0
C_4 = G_3 + P_3·G_2 + P_3·P_2·G_1
    + P_3·P_2·P_1·G_0
    + P_3·P_2·P_1·P_0·C_0
where
C_0: the adder's carry in
C_1, C_2, C_3, C_4: the carries into bits 1, 2 and 3, and the carry out of bit 3 (the adder's carry out)
G_0, G_1, G_2, G_3: generate signals of bits 0 to 3: G_i = A_i·B_i
P_0, P_1, P_2, P_3: propagate signals of bits 0 to 3: P_i = A_i ⊕ B_i
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: each term is one way for a carry to arrive: generated at some bit and then propagated by every bit above it, or the original carry in propagated by every bit.
```

For example, add binary 1011 (decimal 11) and binary 0110 (decimal 6) with no carry in, writing every 4-bit value with bit 3 on the left:

Bit 1 has two high operand bits and generates a carry. Bits 2 and 3 have unequal operand bits, so both propagate it to the output. The carry therefore reaches the top even though the top bit does not generate one.

Each carry is a two-level sum of products of G and P. In an ideal unit-delay model with arbitrary required fan-in and one-level G/P generation, this gives about three levels. Real XORs, wide gates, fan-out and wiring do not share one universal delay. Read `C2` in words: "a carry arrives at bit 2 if bit 1 generates one, or bit 1 propagates one that bit 0 generated, or both propagate the original carry in."

The cost is that the terms get wider and more numerous as you go. As width grows, the expanded gates and interconnect become costly, so designers build **hierarchical** lookahead: 4-bit blocks each produce a block-level G and P, and a second lookahead unit combines those.

## Key takeaways
- Generate creates a carry; propagate passes one from below.
- Expanded lookahead computes each carry from input generate/propagate signals.

## Further reading
- [MIT — Arithmetic structures](https://web.mit.edu/6.111/www/f2017/handouts/L08.pdf)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Adder (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Adder_(electronics))
- [Carry-lookahead adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-lookahead_adder)
- [Kogge–Stone adder — Wikipedia](https://en.wikipedia.org/wiki/Kogge%E2%80%93Stone_adder)
- [Arithmetic logic unit — Wikipedia](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Multiplexer — Wikipedia](https://en.wikipedia.org/wiki/Multiplexer)
- [Carry-save adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-save_adder)
