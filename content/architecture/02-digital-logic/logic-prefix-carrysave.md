---
id: logic-prefix-carrysave
title: Prefix trees and carry-save arithmetic
level: intermediate
minutes: 3
sourceLesson: logic-adders-alu
summary: Associative span combination enables logarithmic prefix depth.
---

## Prefix adders: lookahead taken to its conclusion

Generate and propagate pairs for neighbouring spans of bits combine with an associative operator:

```formula reference
(G, P) ∘ (G′, P′) = (G + P·G′, P·P′)
where
G, P: the generate and propagate signals of the more significant span of bits
G′, P′: the generate and propagate signals of the adjacent less significant span. Here the prime means "the other span", not NOT
∘: the prefix combine operator: it merges two adjacent spans into one span covering both
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the combined span generates a carry if the upper part generates one, or the upper part propagates one that the lower part generated; it propagates only if both parts propagate.
```

Because the operator is associative (the grouping does not matter), the carries for all positions are a **parallel prefix** computation (like a prefix sum), which can be done in a tree whose depth grows with the logarithm of the width.

Each binary prefix level combines neighbouring spans and doubles the reach of a carry calculation. Doubling the adder width adds one such combining level, instead of doubling a serial carry chain.

The classic designs trade depth against area and wiring:

| Adder | Structure | Trade-off |
|---|---|---|
| Ripple-carry | Serial carry chain | Simple, depth grows with width |
| Kogge–Stone | Broad prefix tree | Shallow tree, substantial wiring |
| Brent–Kung | More selective prefix tree | Fewer combining cells, deeper paths |
| Han–Carlson | Hybrid prefix structure | Balances depth and wiring |

These comparisons concern topology. Input logic, final-sum logic, cell delay, fan-out and routing also affect actual speed and area.

## Beyond addition

- **Multiplication** is many additions. Hardware multipliers generate all partial products at once and sum them with trees of **carry-save adders**, which add three numbers into two without propagating carries, so only one real carry-propagate add is needed at the end.
- **Division** commonly uses iterative hardware, but algorithms, latency, throughput and operand dependence vary by processor.

Instruction latency is a property of a particular processor and instruction, not a consequence of the word “multiply” or “divide” alone.

## Key takeaways
- Associative span combination enables logarithmic prefix depth.
- Carry-save trees reduce many operands before a final carry-propagating sum.

## Further reading
- [MIT — Arithmetic structures](https://web.mit.edu/6.111/www/f2017/handouts/L08.pdf)
- [Brent and Kung — A regular layout for parallel adders](https://maths-people.anu.edu.au/~brent/pd/rpb060.pdf)
- [Prefix-algorithm implementations and wiring trade-offs](https://www.cse.chalmers.se/~ms/PP/KoggeStone.pdf)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Adder (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Adder_(electronics))
- [Carry-lookahead adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-lookahead_adder)
- [Kogge–Stone adder — Wikipedia](https://en.wikipedia.org/wiki/Kogge%E2%80%93Stone_adder)
- [Arithmetic logic unit — Wikipedia](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Multiplexer — Wikipedia](https://en.wikipedia.org/wiki/Multiplexer)
- [Carry-save adder — Wikipedia](https://en.wikipedia.org/wiki/Carry-save_adder)
