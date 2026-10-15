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

```formula
T_clk ≥ t_{cq,max} + t_{pd,max} + t_su
f_max = 1 / T_{clk,min}
where
T_clk: the clock period, the time between rising edges, in picoseconds (ps)
T_{clk,min}: the smallest period that meets the constraint
t_{cq,max}: the longest clock-to-Q delay of FF1: the time from the clock edge until FF1's output changes
t_{pd,max}: the longest propagation delay through the logic between FF1 and FF2
t_su: the setup time of FF2: how long before the edge its input must be stable
f_max: the highest clock frequency allowed, in hertz (Hz); 1 GHz is 10^9 cycles per second
≥: greater than or equal to
ps: picoseconds, 10^-12 seconds
Hz: hertz, cycles per second
In words: one clock period must be long enough for data to leave the first flip-flop, cross the slowest logic, and settle before the second flip-flop samples it.
```

For example, with t_cq = 50 ps, t_pd = 400 ps and t_su = 30 ps:

```formula
T_clk ≥ 50 ps + 400 ps + 30 ps = 480 ps
f_max = 1 / (480 × 10^{-12} s)
f_max ≈ 2.08 × 10^9 Hz = 2.08 GHz
where
T_clk: the clock period
f_max: the highest allowed clock frequency
ps: picoseconds, 10^-12 seconds
s: seconds
Hz: hertz, cycles per second
GHz: gigahertz, 10^9 Hz
≥: greater than or equal to
≈: approximately equal to
In words: the period must be at least 480 ps, so the clock can run at about 2.08 GHz at most.
```

The constraint assumes an ideal clock that reaches both flip-flops at the same moment, with no jitter. The slowest such path on the chip is the **critical path**, and it sets the clock rate. (Clock skew, the difference in clock arrival time between FF1 and FF2, shifts this budget: if FF2's clock arrives earlier than FF1's, the logic has that much less time. If it arrives later, setup gets easier but hold, below, gets harder.)

There is a second, sneakier constraint. The *new* value from FF1 must never reach FF2 so fast that it corrupts what FF2 is capturing on the same edge. This is the **hold constraint**, shown here with an example path whose fastest clock-to-Q delay is 20 ps, fastest logic path 5 ps and hold time 40 ps:

```formula
t_{cq,min} + t_{pd,min} ≥ t_h
20 ps + 5 ps = 25 ps < 40 ps
where
t_{cq,min}: the shortest clock-to-Q delay of FF1
t_{pd,min}: the shortest propagation delay through the logic (the fastest path)
t_h: the hold time of FF2: how long after the edge its input must stay stable
≥: greater than or equal to; <: less than
ps: picoseconds, 10^-12 seconds
In words: the earliest new data must never arrive before FF2's hold window has closed. In the example numbers, the new data arrives after 25 ps but FF2 needs its input steady for 40 ps, so the path fails by 15 ps.
```

A **hold violation** cannot be fixed by slowing the clock, because the clock period does not appear in it. The fix is to add delay (buffers) to the short path. Static timing analysis tools check both constraints on every path.

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
