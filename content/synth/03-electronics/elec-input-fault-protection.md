---
id: elec-input-fault-protection
sourceLesson: elec-logic-levels
title: "Level conversion, input clamps and back-powering"
level: intermediate
minutes: 3
summary: "Use proper level conversion during normal operation."
---

Use proper level conversion during normal operation.

## Protecting inputs
Inputs that connect to the outside world (jacks, long wires, other equipment) see accidents: wrong voltages, static discharge, hot-plugging.

Many CMOS inputs, including the SN74HC00, have internal **clamp diodes** from each input to the supply pin (V_CC) and to GND. When an input goes beyond a rail by a diode drop, the diode conducts and dumps the excess current into the rail.

```diagram
        VCC
         |
        ─┴─ clamp diode
  in ─[ R ]─┬──── chip input
        ─┬─ clamp diode
         |
        GND
```

A **series resistor** limits the current that flows into those clamps during a fault. TI permits particular over-rail cases only when its specified pin-current limits are observed; that exception belongs to this exact device, not every microcontroller. During a fault the clamp holds the pin about one diode drop above the rail, so the resistor takes the rest of the fault voltage:

```formula
I_clamp = (V_fault − V_CC − V_D) / R
I_clamp ≈ (5 V − 3.3 V − 0.5 V) / 10 kΩ
I_clamp ≈ 1.2 V / 10 kΩ ≈ 0.12 mA
where
I_clamp: the current pushed through the clamp diode into the supply rail, in milliamps (mA)
V_fault: the wrong voltage applied to the input, here 5 volts (V)
V_CC: the chip's supply rail, here 3.3 V
V_D: the clamp diode's forward drop, assumed about 0.5 V
R: the series resistor, here 10 kΩ
V: volts
kΩ: kilohms; 1 kΩ = 1000 ohms
mA: milliamperes; 1 mA = 0.001 amperes
≈: approximately equal to
In words: a 5 V mistake on a 3.3 V input pushes only about 0.12 mA through the clamp when a 10 kΩ resistor is in the way.
```

The 0.5 V clamp drop is an assumption: the real drop depends on the chip and the current, and like any silicon junction it is usually somewhat higher at milliamp currents. A lower actual drop would increase the current, so 0.5 V is only an illustrative assumption, not a guaranteed current bound. A real protection design needs the diode curve, resistor tolerance, rail behaviour and chip injection limits.

Be conservative:

- **Clamps are fault protection, not a level shifter.** Some manufacturers, such as PJRC for Teensy 4.1, say plainly not to drive pins above 3.3 V. Use proper level conversion for normal operation.
- **Microcontrollers specify their own injected-current limits.** Check the chip's datasheet rather than borrowing a 74HC figure.
- **Back-powering:** a signal driven into an unpowered chip can power it partly through the clamp diodes, causing strange behaviour or damage. Power boards up together, or make sure signals can't arrive before the supply.
- **External Schottky clamps** (with a lower forward drop than the internal diodes) are often added on exposed inputs, so they conduct before the chip's internal diodes do.

## Key takeaways

- Use proper level conversion during normal operation.
- Clamp current and supply-rail injection must both remain within documented limits.

## Further reading

- [TI SN74HC00, SCLS181H](https://www.ti.com/lit/ds/symlink/sn74hc00.pdf)
- [TI: interpreting standard-logic datasheets, SZZA036C](https://www.ti.com/lit/an/szza036c/szza036c.pdf)
- [PJRC: Teensy 4.1 signal-voltage limits](https://www.pjrc.com/store/teensy41.html)
