---
id: logic-gate-delay-power
title: Gate delay and switching power
level: basic
minutes: 3
sourceLesson: logic-gates-cmos
summary: Clock period limits the available logic delay.
---

## Timing and power

### Propagation delay

A gate's output does not change instantly. Its output has to charge or discharge the capacitance of the wires and gate inputs it drives. Propagation delay characterises the input-to-output response under specified thresholds, load, slew, process, voltage and temperature. A timing model may bound the time until a valid output.

A higher clock frequency gives each cycle less time. The logic must settle before the next capture edge, allowing for the registers and clock timing too. Gate delay has no universal value: it depends on the selected cell, load and operating conditions.

How many gate stages fit depends on cell and wire delays and register overhead, which is why the depth of a circuit (the longest chain of gates, the **critical path**) matters as much as its size.

Delay grows with **fan-out**, the number of gate inputs one output drives, because each adds capacitance. Designers insert buffers to split large loads.

### Where the power goes

Each time a gate's output switches from 0 to 1, it charges its load capacitance from the supply; switching back to 0 dumps that charge to ground. This **dynamic power** increases with switching activity, load capacitance and clock frequency. Supply voltage has a squared effect when the other factors stay fixed. The optional relationship is useful for estimates:

```formula reference
P_dynamic ≈ αCV^2 f
where
P_dynamic: the dynamic (switching) power, in watts (W)
α: alpha, the activity factor: the mean number of 0-to-1 output transitions per clock cycle, depending on workload and glitches (0.1 is an illustrative data-logic value here; a clock that rises once per cycle has α = 1). Some books instead count every transition, rising and falling, and write ½ × α × C × V^2 × f; that α is twice this one, so the power is the same
C: the switched capacitance, in farads (F): the wires and gate inputs being charged
V: the supply voltage, in volts (V)
V^2: the supply voltage squared: each 0-to-1 transition draws energy C × V^2 from the supply
f: the clock frequency, in hertz (Hz)
W: watts, joules per second
F: farads, the unit of capacitance
Hz: hertz, cycles per second
≈: approximately equal to
In words: switching power grows in proportion to how often nodes switch, how much capacitance they drive and the clock rate, and with the square of the supply voltage.
```

Reducing supply voltage can substantially reduce capacitive switching power, but it also changes transistor speed and must stay within the device's operating limits. Dynamic voltage and frequency scaling (DVFS) coordinates both settings. **Clock gating** stops unnecessary clock transitions in idle blocks, reducing switching activity. It requires clock-gating cells or dedicated resources used within their timing rules.

There is also **static (leakage) power**: real transistors are not perfect switches and leak a little current even when "off". At modern feature sizes, leakage is a significant share of total power, which is one reason the dream of ever-faster clocks ended in the mid-2000s (lesson 7 of the pipelining module covers the power wall).

## Key takeaways
- Clock period limits the available logic delay.
- Capacitive switching power depends quadratically on supply voltage.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/cmos/notes.html)
- [Logic gate — Wikipedia](https://en.wikipedia.org/wiki/Logic_gate)
- [CMOS — Wikipedia](https://en.wikipedia.org/wiki/CMOS)
- [NAND logic — Wikipedia](https://en.wikipedia.org/wiki/NAND_logic)
- [Functional completeness — Wikipedia](https://en.wikipedia.org/wiki/Functional_completeness)
- [Processor power dissipation — Wikipedia](https://en.wikipedia.org/wiki/Processor_power_dissipation)
- [Nand2Tetris: build a computer from NAND gates](https://www.nand2tetris.org/)
