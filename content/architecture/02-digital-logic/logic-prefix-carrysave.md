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

```formula
(G, P) ∘ (G′, P′) = (G + P·G′, P·P′)
where
G, P: the generate and propagate signals of the more significant span of bits
G′, P′: the generate and propagate signals of the adjacent less significant span. Here the prime means "the other span", not NOT
∘: the prefix combine operator: it merges two adjacent spans into one span covering both
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the combined span generates a carry if the upper part generates one, or the upper part propagates one that the lower part generated; it propagates only if both parts propagate.
```

Because the operator is associative (the grouping does not matter), the carries for all positions are a **parallel prefix** computation (like a prefix sum), which can be done in a tree whose depth grows with the logarithm of the width:

```formula
L = ⌈log_2(n)⌉
L = ⌈log_2(64)⌉ = 6
where
L: the number of binary prefix-tree levels (Kogge–Stone), excluding input and final-sum logic
⌈ ⌉: ceiling, rounding up to a whole number
n: the adder width in bits
log_2: logarithm base 2: how many times you must double 1 to reach n, since 2^6 = 64
In words: each level doubles the span each carry covers, so 64 bits need 6 levels instead of a 64-stage ripple, and doubling the width adds just one level.
```

The classic designs trade depth against area and wiring:

| Adder | 64-bit topology model | Trade-off |
|---|---|---|
| Ripple-carry | 64 carry stages | Simple linear chain |
| Kogge–Stone | 6 prefix levels | Shallow tree, substantial wiring |
| Brent–Kung | 11 scheduled rows | Fewer cells, deeper |
| Han–Carlson | 7 | A hybrid |

These counts exclude input generate/propagate and final-sum logic. The Brent–Kung count uses the original buffered layout: its scheduled rows include forwarding stages. Counting only combining cells on the longest unbuffered path instead gives ten at 64 bits. Keep the counting convention explicit when comparing drawings. Cell delay, fan-out, routing and design variants determine actual speed and area.

## Beyond addition

- **Multiplication** is many additions. Hardware multipliers generate all partial products at once and sum them with trees of **carry-save adders**, which add three numbers into two without propagating carries, so only one real carry-propagate add is needed at the end.
- **Division** commonly uses iterative hardware, but algorithms, latency, throughput and operand dependence vary by processor.

> [!note] Evidence gap
> Universal modern-CPU multiplication/division cycle counts are omitted because no target processor, instruction or measurement was supplied.

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
