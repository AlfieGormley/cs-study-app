---
id: logic-edge-registers
title: Edge-triggered storage and registers
level: intermediate
minutes: 3
sourceLesson: logic-sequential
summary: Opposite-phase master and slave latches implement edge-triggered sampling.
---

## The edge-triggered D flip-flop

The solution is to make storage happen at an **instant**, not over an interval. Put two D latches in series with opposite enables:

```
         +---------+     +---------+
D -------| master  |-----|  slave  |--- Q
         | latch   |     |  latch  |
         | E = CLK'|     | E = CLK |
         +---------+     +---------+
```

- While the clock is low the master is transparent and follows D; the slave is closed and holds Q.
- When CLK rises, the master closes, capturing D at that instant, and the slave opens, passing the captured value to Q.
- While CLK = 1 the master is closed, so changes on D cannot reach Q.

The result is a **positive-edge-triggered D flip-flop**: Q takes the value D had at the rising edge of the clock and holds it until the next rising edge. Here is the difference from a latch (enabled while CLK is high) in a timing diagram:

```
event              D   latch Q   FF Q
initial CLK=0      0      0        0
rising edge        0      0        0
D rises, CLK=1     1      1        0
D falls, CLK=1     0      0        0
falling edge       0      0        0
next rising edge   0      0        0
```

The latch passes the short pulse on D because the clock happens to be high. The flip-flop ignores it, because D was 0 at both surrounding edges. In the ideal single-clock model, registers sample at the same edge. Real clock skew, clock-to-Q, setup/hold and wire delays reduce or shift the available budget; synchronous designs can also use carefully timed latches.

## Building blocks from flip-flops

- **Register**: n flip-flops sharing one clock. To make it hold its value unless `load` is asserted, put a 2-to-1 mux in front of each D:

```formula
D = L′·Q + L·D_new
where
D: the flip-flop's data input, sampled at the next clock edge
Q: the flip-flop's current output (its stored value)
L: the load signal (`load` in the text): 1 to load a new value
L′: NOT L
D_new: the new value to load
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: when load is 0 the flip-flop is fed its own output and keeps its value; when load is 1 it is fed the new value. In code this is `D = load ? new : Q`.
```

This avoids naive combinational clock gating. Proper integrated clock-gating cells or dedicated FPGA clock-enable resources can safely save power when used with their timing rules.
- **Shift register**: each flip-flop's Q feeds the next one's D; data moves one place per clock. Used for serial links and delay lines.
- **Counter circuit**: a register plus an incrementer, `Q <= Q + 1`. The program counter is a fancy version.
- **Reset**: a **synchronous** reset only takes effect at a clock edge; an **asynchronous** reset can assert independently of the clock, but its release must satisfy recovery/removal timing, commonly using synchronised deassertion.

## Key takeaways
- Opposite-phase master and slave latches implement edge-triggered sampling.
- Load muxes, shift chains and incrementers build useful register structures.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/sequential_logic/notes.html)
- [Flip-flop (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Flip-flop_(electronics))
- [Latch (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Latch_(electronics))
- [Metastability (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Metastability_(electronics))
- [Static timing analysis — Wikipedia](https://en.wikipedia.org/wiki/Static_timing_analysis)
- [Finite-state machine — Wikipedia](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Clock domain crossing — Wikipedia](https://en.wikipedia.org/wiki/Clock_domain_crossing)
