---
id: logic-ripple-carry
title: Trace the ripple-carry chain
level: intermediate
minutes: 3
sourceLesson: logic-adders-alu
summary: Each carry feeds the next bit in a ripple chain.
---

## Ripple-carry adder

Chain n full adders, each carry out feeding the next carry in:

```
  a3 b3     a2 b2     a1 b1     a0 b0
   | |       | |       | |       | |
 +-----+   +-----+   +-----+   +-----+
 | FA  |<--| FA  |<--| FA  |<--| FA  |<-c0
 +-----+ c3+-----+ c2+-----+ c1+-----+
  |   |      |         |         |
 c4  s3     s2        s1        s0
```

It is small (n full adders) and simple. Its weakness is that the worst-case carry dependence grows through the lower stages; a generate or kill at an intermediate bit can cut that dependence for particular inputs. The worst case is a carry that starts at bit 0 and propagates all the way, as in 

```formula
01111111 + 00000001 = 10000000
where
+: ordinary binary addition, not Boolean OR
In words: adding one to this run of seven low-order ones propagates a carry through them into the top bit.
```


If each carry stage costs about two gate delays (an AND then an OR), the carry chain's delay grows in proportion to the width, about **2n gate delays** for n bits:

```formula
t_ripple ≈ 2n t_gate
t_ripple ≈ 2 × 64 × t_gate = 128 × t_gate
where
t_ripple: the worst-case delay of the ripple-carry chain
n: the adder width in bits, here 64
t_gate: the delay of one gate (an AND or an OR), in this simplified model where every gate is equally fast
2: two gate delays per bit: an AND then an OR on the carry path
≈: approximately equal to
In words: in the simplified model, a 64-bit ripple adder's carry passes through about 128 gates in the worst case, and doubling the width doubles the delay.
```

Whether that fits a clock target depends on actual cells and interconnect; high-performance designs commonly use lookahead, prefix, carry-select or hybrid structures.

## Follow an example carry

For an 8-bit example, add binary `01111111` and `00000001`. The least significant column adds two ones, producing a zero result bit and a carry. Each of the following six columns adds a one from the first operand to that incoming carry, producing another zero and forwarding the carry. The top column adds zero to that carry and produces one. The result is `10000000`.

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
