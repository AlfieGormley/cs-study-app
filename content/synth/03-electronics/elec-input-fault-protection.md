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

A **series resistor** limits the current that flows into those clamps during a fault. TI permits particular over-rail cases only when its specified pin-current limits are observed; that exception belongs to this exact device, not every microcontroller. During a fault the clamp holds the pin about one diode drop above the rail, so the resistor takes the rest of the fault voltage.

A larger series resistance reduces fault current for the same voltage difference. But current diverted into a supply rail must go somewhere: a lightly loaded regulator may not absorb it, allowing the rail to rise. An unpowered chip can also be partly powered through this path.

A real protection design needs the diode’s voltage-current behaviour, resistor tolerance, rail behaviour and the exact chip’s voltage and injection-current limits. A small calculated current alone does not establish safety.

Be conservative:

- **Clamps are fault protection, not a level shifter.** Some manufacturers, such as PJRC for Teensy 4.1, say plainly not to drive pins above 3.3 V. Use proper level conversion for normal operation.
- **Microcontrollers specify their own injected-current limits.** Check the chip's datasheet rather than borrowing a 74HC figure.
- **Back-powering:** a signal driven into an unpowered chip can power it partly through the clamp diodes, causing strange behaviour or damage. Power boards up together, or make sure signals can't arrive before the supply.
- **External Schottky clamps** may divert current before internal diodes, but only if their actual drop at the relevant current is low enough. Check leakage, capacitance, fault ratings and where the rail current goes.

## Key takeaways

- Use proper level conversion during normal operation.
- Clamp current and supply-rail injection must both remain within documented limits.

## Further reading

- [TI SN74HC00, SCLS181H](https://www.ti.com/lit/ds/symlink/sn74hc00.pdf)
- [TI: interpreting standard-logic datasheets, SZZA036C](https://www.ti.com/lit/an/szza036c/szza036c.pdf)
- [PJRC: Teensy 4.1 signal-voltage limits](https://www.pjrc.com/store/teensy41.html)
