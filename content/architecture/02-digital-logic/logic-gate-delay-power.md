---
id: logic-gate-delay-power
title: Gate delay and switching power
level: basic
minutes: 4
sourceLesson: logic-gates-cmos
summary: Clock period limits the available logic delay.
---

## Timing and power

### Propagation delay

A gate's output does not change instantly. Its output has to charge or discharge the capacitance of the wires and gate inputs it drives. Propagation delay characterises the input-to-output response under specified thresholds, load, slew, process, voltage and temperature. A timing model may bound the time until a valid output.

> [!note] Evidence gap
> A universal modern-gate delay is omitted because no process, library cell, load or operating corner was supplied to verify the previous ten-picosecond figure.

That sounds negligible until you do the arithmetic. The time for one clock cycle is one divided by the clock frequency:

```formula
T = 1 / f
T = 1 / (3 × 10^9 Hz)
T ≈ 3.33 × 10^{-10} s ≈ 333 ps
where
T: the clock period, the time for one cycle, in seconds (s) or picoseconds (ps)
f: the clock frequency, in hertz (Hz); here 3 GHz = 3 × 10^9 Hz
Hz: hertz, cycles per second
s: seconds
ps: picoseconds: 1 ps = 10^{-12} s, a millionth of a millionth of a second
≈: approximately equal to (rounded)
In words: a 3 GHz clock ticks every third of a nanosecond, about 333 ps, and the logic between two registers must settle within that.
```

How many gate stages fit depends on cell and wire delays and register overhead, which is why the depth of a circuit (the longest chain of gates, the **critical path**) matters as much as its size.

Delay grows with **fan-out**, the number of gate inputs one output drives, because each adds capacitance. Designers insert buffers to split large loads.

### Where the power goes

Each time a gate's output switches from 0 to 1, it charges its load capacitance from the supply; switching back to 0 dumps that charge to ground. The resulting **dynamic power** is approximately:

```formula
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

For example, with illustrative numbers (not a real chip) α = 0.1, C = 1 nF of total switched capacitance, V = 1.0 V and f = 3 GHz:

```formula
P_dynamic ≈ αCV^2 f
P_dynamic ≈ 0.1 × 10^{-9} F × (1.0 V)^2
            × 3 × 10^9 Hz
P_dynamic ≈ 0.3 W
where
P_dynamic: the dynamic power, in watts (W)
α: the activity factor, here 0.1 transitions per node per cycle
C: the switched capacitance, here 1 nF (nanofarad) = 10^-9 F
V: the supply voltage, here 1.0 V (V is also the symbol for volts, its unit)
f: the clock frequency, here 3 GHz (gigahertz) = 3 × 10^9 Hz
F: farads, the unit of capacitance
Hz: hertz, cycles per second
W: watts: one watt is one joule of energy per second
≈: approximately equal to
In words: these illustrative numbers give about 0.3 watts of switching power. Lowering the voltage to 0.8 V alone would multiply it by 0.8 × 0.8 = 0.64, saving 36 %.
```

The V² term makes voltage reduction powerful at fixed activity and capacitance, but voltage limits and performance requirements constrain it. It is also why phones scale voltage and frequency together (DVFS). **Clock gating**, which stops the clock to idle blocks, attacks α.

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
