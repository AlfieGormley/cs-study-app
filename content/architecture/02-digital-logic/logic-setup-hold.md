---
id: logic-setup-hold
title: Setup, hold and clock skew
level: intermediate
minutes: 4
sourceLesson: logic-sequential
summary: Setup constrains the slowest path to the next capture edge.
---

## Flip-flop timing

A real flip-flop needs D to be stable for a short window around the edge:

- **Setup time** (t_su): D must be stable this long *before* the edge.
- **Hold time** (t_h): D must stay stable this long *after* the edge.
- **Clock-to-Q** (t_cq): Q changes this long after the edge.

```
CLK    ________/-----------
D      XXX=========XXXXXXXX
          |<su>|<h>|
               |<cq>|
Q      =============XX=====

= stable value, X may change
```

These numbers set the speed of the whole chip. Consider two registers with combinational logic between them:

```
+-----+                    +-----+
| FF1 |--> logic, t_pd --->| FF2 |
+-----+                    +-----+
   ^                          ^
   +----------- CLK ----------+
```

Data leaves FF1 at t_cq after an edge, takes up to t_pd to get through the logic, and must arrive t_su before the *next* edge. That gives the **setup constraint** on the clock period, and from it the fastest allowed clock:

```formula reference
T_clk ≥ t_{cq,max} + t_{pd,max} + t_su
where
T_clk: the clock period, the time between rising edges, in picoseconds (ps)
t_{cq,max}: the longest clock-to-Q delay of FF1, in ps: the time from the clock edge until FF1's output changes
t_{pd,max}: the longest propagation delay through the logic between FF1 and FF2, in ps
t_su: the setup time of FF2, in ps: how long before the edge its input must be stable
≥: greater than or equal to
ps: picoseconds, 10^-12 seconds
In words: With aligned clocks and no jitter, one period must fit the slowest launch delay, the slowest logic path and the receiving register's setup allowance.
```

A longer logic path leaves less setup margin. Slowing the clock can help a setup failure by moving the next capture edge later, provided the other constraints remain satisfied.

The constraint assumes an ideal clock that reaches both flip-flops at the same moment, with no jitter. The slowest such path on the chip is the **critical path**, and it sets the clock rate. (Clock skew, the difference in clock arrival time between FF1 and FF2, shifts this budget: if FF2's clock arrives earlier than FF1's, the logic has that much less time. If it arrives later, setup gets easier but hold, below, gets harder.)

There is a second, sneakier constraint. The *new* value from FF1 must never reach FF2 so fast that it corrupts what FF2 is capturing on the same edge. This is the **hold constraint**: even the fastest new data must arrive after the receiving register's hold window closes. The reference below assumes aligned clocks without jitter:

```formula reference
t_{cq,min} + t_{pd,min} ≥ t_h
where
t_{cq,min}: the shortest clock-to-Q delay of FF1, in ps
t_{pd,min}: the shortest propagation delay through the logic (the fastest path), in ps
t_h: the hold time of FF2, in ps: how long after the edge its input must stay stable
≥: greater than or equal to
ps: picoseconds, 10^-12 seconds
In words: the fastest launch and logic path must still delay new data until the receiving register has finished holding its old input stable.
```

A **hold violation** in this same-edge model cannot be fixed by slowing the clock: moving the next edge does not change the current capture window. Adding delay buffers to the short path is a common fix. Recheck setup and hold across the required operating conditions afterwards; clock skew and constraints also matter. Static timing analysis tools check the constrained paths.

## Key takeaways
- Setup constrains the slowest path to the next capture edge.
- Hold constrains the fastest same-edge path and cannot be repaired by a slower clock.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/sequential_logic/notes.html)
- [Flip-flop (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Flip-flop_(electronics))
- [Latch (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Latch_(electronics))
- [Metastability (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Metastability_(electronics))
- [Static timing analysis — Wikipedia](https://en.wikipedia.org/wiki/Static_timing_analysis)
- [Finite-state machine — Wikipedia](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Clock domain crossing — Wikipedia](https://en.wikipedia.org/wiki/Clock_domain_crossing)
