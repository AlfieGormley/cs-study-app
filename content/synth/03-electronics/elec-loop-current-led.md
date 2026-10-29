---
id: elec-loop-current-led
sourceLesson: elec-ohms-law
title: "Complete loops and LED current"
level: basic
minutes: 2
summary: "A steady current needs a complete current return path."
---

A steady current needs a complete current return path.

## Complete circuits
In the steady low-voltage DC model, sustained conduction current flows around a **closed electrical loop** (a complete circuit): from the supply's positive terminal, through the load, and back to the supply's negative terminal. Break the loop anywhere (an open switch, a loose jumper, a cracked solder joint) and the current everywhere in that loop drops to zero.

```diagram
 +5V ---[ R 330 ]---[ LED >| ]---+
  |                              |
 supply                          |
  |                              |
 0V -----------------------------+
          return path (ground)
```

Two consequences:

- **The current return path is part of the circuit.** A signal that leaves your synth board on one wire must come back on another. In ordinary unbalanced audio wiring, the sleeve or shield is that return; balanced audio uses a pair of signal conductors.
- **Current is the same everywhere in a single loop.** If 10 mA flows through the resistor, 10 mA flows through the LED. This is Kirchhoff's current law in its simplest form.

Kirchhoff's voltage law is the other half: around any closed loop, the voltage rises equal the drops. It's how you work out what is left for the LED once the resistor has taken its share.

For example, a steady 5 V supply with 3.3 V across the resistor leaves 1.7 V across the LED. Voltage is shared; current is not used up by the first component.

In this lumped, steady-DC model, include any significant wire resistance as another component. Kirchhoff’s laws do not require zero wire resistance. At high frequencies or with changing magnetic flux, the simple lumped model needs additional care.

A bare LED connected to a voltage source has no dependable current control: its current rises steeply with forward voltage. Use a suitable series resistor or specified current driver, and respect both the LED and any GPIO pin’s current limits.

## Conventional current and electron flow
Circuit diagrams and textbooks use **conventional current**: current flows from + to −. That convention predates the discovery of the electron. In a metal wire the charge carriers are actually electrons, which are negative and drift the opposite way, from − to +.

Both descriptions predict the same voltages, currents and power. Every formula, datasheet and schematic symbol uses conventional current. A forward-biased diode carries conventional current from anode to cathode (the bar). An LED's outward arrows indicate light, not current. Use conventional current and treat electron flow as a physics detail.

## Key takeaways

- A steady current needs a complete current return path.
- Use conventional current from anode to cathode through a forward-biased LED.

## Further reading

- [OpenStax: Kirchhoff’s rules](https://openstax.org/books/university-physics-volume-2/pages/10-3-kirchhoffs-rules)
- [OpenStax: electric current](https://openstax.org/books/university-physics-volume-2/pages/9-1-electrical-current)
- [SparkFun: LED current limiting](https://learn.sparkfun.com/tutorials/light-emitting-diodes-leds/all)
