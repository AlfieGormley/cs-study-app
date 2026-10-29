---
id: elec-led-resistor-choice
sourceLesson: elec-components
title: "Choosing an LED’s current-limiting resistor"
level: intermediate
minutes: 3
summary: "Subtract the LED drop before sizing the resistor."
---

Subtract the LED drop before sizing the resistor.

## LEDs and the current-limiting resistor
An LED is a diode that emits light. It normally conducts strongly under forward bias and carries much less reverse current within its reverse-voltage limits. Its current rises steeply with forward voltage; the quoted **forward voltage** (written V_f) is measured at a stated current rather than being a fixed switching threshold, so an LED always needs something to limit its current, usually a series resistor.

The forward voltage depends on the exact device, current and temperature. For example, Kingbright WP7113ID revision V.14A (8 January 2026) lists 1.9 V typical and 2.3 V maximum at 10 mA (checked 29 October 2026). Those are test conditions, not a recommended drive current or a universal red-LED voltage. Many indicators are useful at only a few milliamps; check the actual LED’s current and thermal limits.

The resistor's job is to take whatever voltage the LED doesn't. Kirchhoff's voltage law gives that leftover voltage, and Ohm's law on the resistor turns it into a resistance:

```formula reference
R = (V_supply − V_f) / I_LED
where
R: nominal series resistance, in ohms (Ω)
V_supply: supply or loaded pin voltage, in volts (V)
V_f: assumed LED forward voltage at the chosen current, in volts
I_LED: desired LED current, in amperes (A)
In words: The resistor takes the voltage left after the LED’s forward drop. A larger resistance gives less current for the same assumed voltage difference; the LED’s drop is not a fixed threshold.
```

With assumed 3.3 V drive and 2.0 V LED drop, a nominal 5 mA target calls for 260 Ω. The next E12 value up, 270 Ω, gives about 4.81 mA and 6.26 mW resistor heat under those same assumptions. Choosing a larger preferred value reduces nominal current; it does not by itself prove a worst-case safe design.

For a hardware bound, use maximum supply, minimum LED drop and minimum resistance allowed by tolerance. Check resistor heat, LED thermal/current limits and the source’s loaded output voltage. A GPIO also has per-pin and combined pin-current limits; a nominal estimate below one limit is not enough if variation can exceed it.

**LED orientation:** the longer leg is usually the anode (+). The cathode (−) is often marked by a flat on the rim. Check the datasheet. Reversed, it may stay dark but may also exceed its allowed reverse voltage. Do not apply a reverse voltage beyond the exact LED’s rating. LED reverse ratings are often only a few volts.

## Key takeaways

- Subtract the LED drop before sizing the resistor.
- Use worst-case supply, forward voltage and resistor tolerance for hardware.

## Further reading

- [Kingbright WP7113ID, revision V.14A](https://www.kingbrightusa.com/images/catalog/spec/wp7113id.pdf)
- [Kingbright WP7113QBC/D, revision V.18B](https://www.kingbrightusa.com/images/catalog/spec/wp7113qbc-d.pdf)
- [SparkFun: LED current limiting](https://learn.sparkfun.com/tutorials/light-emitting-diodes-leds/all)
