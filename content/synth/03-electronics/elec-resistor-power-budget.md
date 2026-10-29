---
id: elec-resistor-power-budget
sourceLesson: elec-ohms-law
title: "Resistor heat and an LED power budget"
level: basic
minutes: 3
summary: "Check resistor heat as well as current."
---

A resistor can have the right resistance and still overheat. Check how much electrical energy it turns into heat each second, then compare that power with the part’s rating under the actual mounting and temperature conditions.

## Current alone does not tell you the heat
For a two-terminal part, power depends on both the voltage across it and the current through it:

```formula essential
P = VI
where
P: instantaneous absorbed power, in watts (W)
V: voltage across the part, in volts (V), using the labelled positive terminal
I: current entering that positive terminal, in amperes (A)
In words: Voltage times current gives the rate of energy transfer. Positive absorbed power means the part receives energy; negative means it supplies energy.
```

For steady DC this also gives average power. With changing signals, average the instantaneous product; multiplying arbitrary RMS voltages and currents is not a universal power rule. A chip with multiple terminals may need several power paths included.

For a fixed ohmic resistor, doubling the voltage also doubles the current, so it produces four times as much heat. At fixed voltage, increasing resistance reduces current and heat. At fixed current, increasing resistance requires more voltage and increases heat. Always say what stays fixed.

```formula reference
P = I^2 R
P = V^2 / R
where
P: resistor heat dissipation, in watts (W)
I: current through the resistor, in amperes (A)
R: the fixed resistance, in ohms (Ω)
V: voltage across the resistor, in volts (V)
In words: For a fixed resistor, heat rises with the square of voltage or current. These alternative forms use Ohm’s law and do not model an LED as a fixed resistor.
```

## Leave a thermal margin
An illustrative 100 Ω resistor directly across 5 V dissipates 0.25 W. A part rated for 0.25 W would be at its stated limit only under the specified thermal conditions; it need not feel cool. Choose a suitable higher-rated part, or reduce current if the circuit permits. Check the manufacturer’s derating curve, ambient temperature and mounting rather than treating a fixed safety factor as universal.

An LED and its resistor share the supply voltage. If a 330 Ω resistor carries a measured steady 10 mA from a 5 V supply, it drops 3.3 V and dissipates 33 mW; the LED has the remaining 1.7 V. That is an illustrative budget, not a claim about an arbitrary LED’s forward voltage. The resistor and LED carry the same series current, but their different voltage drops mean different powers.

## Key takeaways

- Resistance and wattage answer different questions: current control and allowed heat.
- Check voltage and current together, then the real part’s thermal conditions.
- Low voltage does not prevent a low-resistance path from overheating.

## Further reading

- [OpenStax: electrical energy and power](https://openstax.org/books/university-physics-volume-2/pages/9-5-electrical-energy-and-power)
- [SparkFun: LED current limiting](https://learn.sparkfun.com/tutorials/light-emitting-diodes-leds/all)
- [Vishay MRS16/MRS25: thermal conditions and derating](https://www.vishay.com/docs/28724/mrs16m25.pdf)
