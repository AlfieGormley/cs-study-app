---
id: logic-ripple-carry
title: Trace the ripple-carry chain
level: intermediate
minutes: 3
sourceLesson: logic-adders-alu
summary: Each carry feeds the next bit in a ripple chain.
---

## Ripple-carry adder

Chain one full adder per bit, each carry out feeding the next carry in:

```
  a3 b3     a2 b2     a1 b1     a0 b0
   | |       | |       | |       | |
 +-----+   +-----+   +-----+   +-----+
 | FA  |<--| FA  |<--| FA  |<--| FA  |<-c0
 +-----+ c3+-----+ c2+-----+ c1+-----+
  |   |      |         |         |
 c4  s3     s2        s1        s0
```

It is small and simple: one full adder per bit. Its weakness is the dependence between neighbouring carry stages. A generate or kill at an intermediate bit can stop an incoming carry from mattering for particular input data, but the longest permitted propagation path still limits timing.

With the same delay per carry stage, doubling the width doubles the worst-case chain depth. Actual delay depends on cells and wiring; counting stages is a structural comparison, not a measured clock speed.

Whether that fits a clock target depends on actual cells and interconnect; high-performance designs commonly use lookahead, prefix, carry-select or hybrid structures.

## Follow an example carry

For an 8-bit example, add binary `01111111` and `00000001`. The least significant column adds two ones, producing a zero result bit and a carry. Each of the following six columns adds a one from the first operand to that incoming carry, producing another zero and passing the carry onwards. The top column adds zero to that carry and produces one. The result is `10000000`.

This describes logical dependence, not eight simultaneous stages with independent carry inputs. In a ripple implementation the upper columns cannot know their final carry contribution until the lower chain has settled. For different input data, a column that generates or kills its own carry can cut the dependence. Timing closure nevertheless has to accommodate the longest permitted path under the specified delay model.

## Key takeaways
- Each carry feeds the next bit in a ripple chain.
- Worst-case chain depth grows with width under the stated delay model.

## Further reading
- [MIT — Arithmetic structures](https://web.mit.edu/6.111/www/f2017/handouts/L08.pdf)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Adder (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Adder_(electronics))
- [Carry-lookahead adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-lookahead_adder)
- [Kogge–Stone adder — Wikipedia](https://en.wikipedia.org/wiki/Kogge%E2%80%93Stone_adder)
- [Arithmetic logic unit — Wikipedia](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Multiplexer — Wikipedia](https://en.wikipedia.org/wiki/Multiplexer)
- [Carry-save adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-save_adder)
