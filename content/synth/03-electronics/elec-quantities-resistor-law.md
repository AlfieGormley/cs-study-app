---
id: elec-quantities-resistor-law
sourceLesson: elec-ohms-law
title: "Voltage, current and Ohm’s law"
level: basic
minutes: 3
summary: "Voltage is measured between two points; current passes through a component."
---

Every circuit in a synth, from an LED on the front panel to the board's audio output, obeys a few simple rules. Learn them well now and the rest of this module is mostly applying them.

> [!warning] Low voltage only
> This module covers low-voltage DC work only: USB power, bench supplies of a few volts, and batteries. It does **not** cover mains wiring or mains power supplies. Use a ready-made, certified supply (a USB charger or a bench supply) and never open or modify anything that plugs into the wall.

## Four quantities
**Voltage** (written V, measured in volts, also V) is the difference in electrical potential between two points. It is the "push". A voltage is always *between* two points. "This pin is at 3.3 V" really means "3.3 V higher than ground".

**Electric current** ( written I, measured in amperes or amps, A) is the rate at which charge flows past a point. One amp is one coulomb per second. Current flows *through* things.

**Electrical resistance** ( written R, measured in ohms, Ω) is how strongly something opposes current. A resistor is a part made to have a known resistance.

**Electrical power** ( written P, measured in watts, W) is the rate at which energy is transferred, for example turned into heat in a resistor or into light in an LED.

A water analogy helps at first: voltage is pressure, current is flow rate, and resistance is a narrow pipe. Don't push it too far. It breaks down for capacitors and for anything at audio or radio frequencies.

## Ohm's law
Ohm's law is the rule you use most: it links the voltage across a resistor to the current through it. For an ohmic resistor at roughly constant temperature, the two are proportional. Double the voltage and the current doubles. The resistance is the fixed ratio between them:

```formula
V = IR
I = V / R
R = V / I
where
V: the voltage across the resistor, in volts (V); written after a number, V is the unit volt
I: the current through the resistor, in amperes (A)
R: the resistance, in ohms (Ω)
A: amperes (amps), the unit of current
Ω: ohms, the unit of resistance; 1 Ω passes 1 A when 1 V is across it
In words: voltage equals current times resistance. The second and third lines are the same law rearranged, so if you know any two of the three you can find the third.
```

For example, a 1 kΩ resistor (1000 Ω) with 5 V across it:

```formula
I = V / R
I = 5 V / 1000 Ω
I = 0.005 A = 5 mA
where
I: the current through the resistor, in amperes (A)
V: the voltage across the resistor, here 5 volts (V)
R: the resistance, here 1 kΩ = 1000 ohms (Ω)
A: amperes, the unit of current
mA: milliamperes; 1 mA = 0.001 A
Ω: ohms, the unit of resistance
In words: 5 volts across 1000 ohms drives 5 milliamps.
```

Ohm's law models ohmic resistors and the resistive part of wires when temperature and other conditions keep their resistance effectively fixed. It does not describe LEDs and diodes. Their current rises steeply with forward voltage rather than following a fixed resistance. Dividing voltage by current describes an operating point; it does not give a constant resistance that predicts another point. Apply Ohm’s law to the resistor in series with the LED, as in the neighbouring LED units.

## Key takeaways

- Voltage is measured between two points; current passes through a component.
- Use Ohm’s law for resistors at the stated operating conditions, not for LEDs.

## Further reading

- [OpenStax: Ohm’s law](https://openstax.org/books/university-physics-volume-2/pages/9-4-ohms-law)
- [OpenStax: electric current](https://openstax.org/books/university-physics-volume-2/pages/9-1-electrical-current)
