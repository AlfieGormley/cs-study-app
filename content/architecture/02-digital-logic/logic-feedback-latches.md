---
id: logic-feedback-latches
title: Feedback, SR latches and D latches
level: intermediate
minutes: 4
sourceLesson: logic-sequential
summary: Cross-coupled feedback retains one bit while powered.
---

Everything so far has been **combinational**: outputs depend only on current inputs. A computer also needs to **remember**: the program counter, the registers, the contents of memory. Circuits whose outputs depend on past inputs as well are **sequential circuits**.

The trick that makes memory possible is **feedback**: wire a gate's output back into its own input. This lesson goes from the simplest feedback loop to the clocked flip-flops and finite-state machines that every processor is built from.

## Two inverters that remember

Connect two inverters in a ring. If the first outputs 1, the second outputs 0, which keeps the first at 1. The opposite state is equally stable. This **bistable** loop stores one bit for as long as it has power, and it is exactly the core of an SRAM cell (in the memory-array units). The only problem is that there is no way to change the bit. The SR latch adds that.

## The SR latch

Replace the inverters with NOR gates so that each gate gets an extra input:

```
       +-------+
R -----|       |
       |  NOR  |o----+----- Q
   +---|       |     |
   |   +-------+     |
   |                 |
   +--------------+  |
                  |  |
   +-----------------+
   |              |
   |   +-------+  |
   +---|       |  |
       |  NOR  |o-+-------- Q'
S -----|       |
       +-------+
```

Each NOR's output feeds the other's input. Recall that a NOR outputs 1 only when both inputs are 0, so a 1 on any input forces its output to 0.

| S | R | Q next | Meaning |
|---|---|---|---|
| 0 | 0 | Q | Hold |
| 1 | 0 | 1 | Set |
| 0 | 1 | 0 | Reset |
| 1 | 1 | 0 (and Q' = 0) | Invalid |

- **Set** (S = 1): the bottom NOR is forced to Q' = 0, so the top NOR sees R = 0 and Q' = 0 and outputs Q = 1.
- **Hold** (S = R = 0): each NOR just inverts the other's output, so the loop keeps its state.
- **Asserting set and reset together** forces both outputs low, breaking the rule that Q' is the complement of Q. Worse, if S and R then fall together, the final stored bit can be unpredictable and the latch can become metastable. Designs must never do this.

## The D latch

The SR latch has two control inputs and a forbidden combination. The **D latch** (D for data) fixes both. It has a data input D and an enable E, and internally drives the SR latch's inputs like this:

```formula
S = D·E
R = D′·E
S·R = D·D′·E = 0
where
S, R: the set and reset inputs of the internal SR latch
D: the data input, 0 or 1
E: the enable input, 0 or 1
D′: NOT D
·: AND: 1 only when both sides are 1
In words: when E is 1, D = 1 sets the latch and D = 0 resets it; when E is 0 both S and R are 0, so it holds. Because D and NOT D are never both 1, S and R are never both 1.
```

So the ideal Boolean equations never assert both. Physical implementations still need timing constraints; propagation delays do not disappear.

- When **enable is high**, the latch has **latch transparency**: Q follows D.
- When **enable is low**, it is an **opaque latch**: Q holds whatever D was when E fell.

Transparency needs deliberate timing design. Latches are useful storage elements and can support time borrowing, but a naive feedback path can race. In a CPU, a register's output feeds logic that eventually feeds back into the same register (think `pc = pc + 4`). If the register is transparent for the whole time the clock is high, a new value can race round the loop and change again within the same clock phase.

## Key takeaways
- Cross-coupled feedback retains one bit while powered.
- A D latch follows data while enabled and holds when disabled.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/sequential_logic/notes.html)
- [Flip-flop (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Flip-flop_(electronics))
- [Latch (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Latch_(electronics))
- [Metastability (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Metastability_(electronics))
- [Static timing analysis — Wikipedia](https://en.wikipedia.org/wiki/Static_timing_analysis)
- [Finite-state machine — Wikipedia](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Clock domain crossing — Wikipedia](https://en.wikipedia.org/wiki/Clock_domain_crossing)
