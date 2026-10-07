---
id: elec-ohms-law
title: Voltage, current, resistance and power
level: basic
minutes: 12
summary: The four quantities behind every circuit, Ohm's law and P = VI, unit prefixes, ground as a reference, complete circuits, and which way current "flows".
---

Every circuit in a synth, from an LED on the front panel to the board's audio output, obeys a few simple rules. Learn them well now and the rest of this module is mostly applying them.

> [!warning] Low voltage only
> This module covers low-voltage DC work only: USB power, bench supplies of a few volts, and batteries. It does **not** cover mains wiring or mains power supplies. Use a ready-made, certified supply (a USB charger or a bench supply) and never open or modify anything that plugs into the wall.

## Four quantities

**Voltage** (V, measured in volts) is the difference in electrical potential between two points. It is the "push". A voltage is always *between* two points. "This pin is at 3.3 V" really means "3.3 V higher than ground".

**Current** (I, measured in amperes or amps, A) is the rate at which charge flows past a point. One amp is one coulomb per second. Current flows *through* things.

**Resistance** (R, measured in ohms, Ω) is how strongly something opposes current. A resistor is a part made to have a known resistance.

**Power** (P, measured in watts, W) is the rate at which energy is transferred, for example turned into heat in a resistor or into light in an LED.

A water analogy helps at first: voltage is pressure, current is flow rate, and resistance is a narrow pipe. Don't push it too far. It breaks down for capacitors and for anything at audio or radio frequencies.

## Ohm's law

For a resistor, the voltage across it is proportional to the current through it:

```
V = I × R
I = V / R
R = V / I
```

If you know any two, you can find the third. A 1 kΩ resistor with 5 V across it carries 5 / 1000 = 5 mA.

Ohm's law describes resistors (and wires). It does not describe LEDs and diodes. Their current rises steeply once the voltage passes a threshold, so you can't use "V / R" on an LED directly. You use it on the resistor in series with the LED, as in the worked example below.

## Power: P = VI

Power is voltage times current. Substituting Ohm's law gives two more forms that are useful for resistors:

```
P = V × I
P = I² × R
P = V² / R
```

Power matters because resistors, regulators and chips all have a maximum they can dissipate before they overheat. A typical small through-hole resistor is rated at 0.25 W (check the actual part's datasheet).

> [!example] An LED's resistor
> A 5 V supply drives an LED through a 330 Ω resistor, and you measure 10 mA. The resistor drops 10 mA × 330 Ω = 3.3 V and dissipates 3.3 V × 10 mA = 33 mW. That is well inside a 0.25 W (250 mW) rating. The remaining 1.7 V is across the LED.

```python
# LED budget on a 5 V supply
V_supply = 5.0
I = 0.010          # 10 mA
R = 330.0          # ohms

V_R = I * R        # Ohm's law
P_R = V_R * I      # P = VI
print(f"V across R: {V_R:.2f} V")
print(f"Power in R: {P_R*1000:.1f} mW")
V_led = V_supply - V_R  # KVL
print(f"Left for LED: {V_led:.2f} V")
```

```
V across R: 3.30 V
Power in R: 33.0 mW
Left for LED: 1.70 V
```

## Units and prefixes

Electronics spans huge ranges, so SI prefixes are everywhere. Get them wrong and you're off by a factor of a thousand.

| Prefix | Symbol | Factor |
|---|---|---|
| mega | M | 10⁶ |
| kilo | k | 10³ |
| milli | m | 10⁻³ |
| micro | µ (or u) | 10⁻⁶ |
| nano | n | 10⁻⁹ |
| pico | p | 10⁻¹² |

Tips:

- Note the case: **m** (milli) and **M** (mega) differ by 10⁹.
- Schematics often put the prefix where the decimal point would be: `4k7` = 4.7 kΩ, `2R2` = 2.2 Ω, `100n` = 100 nF.
- A handy pairing: volts ÷ kilohms = milliamps. 3.3 V across 1 kΩ is 3.3 mA.

## Complete circuits

Current only flows around a **closed loop**: from the supply's positive terminal, through the load, and back to the supply's negative terminal. Break the loop anywhere (an open switch, a loose jumper, a cracked solder joint) and the current everywhere in that loop drops to zero.

```diagram
 +5V ---[ R 330 ]---[ LED >| ]---+
  |                              |
 supply                          |
  |                              |
 0V -----------------------------+
          return path (ground)
```

Two consequences:

- **The return path is part of the circuit.** A signal that leaves your synth board on one wire must come back on another. With audio cables, the sleeve or shield is that return.
- **Current is the same everywhere in a single loop.** If 10 mA flows through the resistor, 10 mA flows through the LED. This is Kirchhoff's current law in its simplest form.

Kirchhoff's voltage law is the other half: around any closed loop, the voltage rises equal the drops. In the LED circuit, 5 V = 3.3 V (resistor) + 1.7 V (LED).

## Ground is a reference

**Ground** (GND, 0 V) is the point you choose to measure every other voltage against. In a battery- or USB-powered synth it's usually the supply's negative terminal. It doesn't have to connect to the earth in the soil.

Three meanings of "ground" get mixed up:

- **Signal or circuit ground:** the 0 V reference and return path inside your circuit. This is what "GND" on a microcontroller board means.
- **Chassis ground:** the conductive case or chassis reference; whether it connects to circuit 0 V depends on the equipment design.
- **Protective earth:** the mains safety earth in a wall socket. It belongs to mains equipment and is not something to modify. Lesson 7 returns to this.

Two practical rules follow:

1. **Direct, non-isolated single-ended signals need a shared reference.** For ordinary GPIO/UART links, connect the boards' GND pins. Isolated links such as DIN MIDI deliberately avoid a direct ground connection. A voltage only means something relative to a reference both sides agree on.
2. **"0 V" isn't the same everywhere.** Ground wires have small resistances. When current flows through them, two "ground" points can differ by a few millivolts. For audio that's enough to hear (lesson 7).

## Conventional current and electron flow

Circuit diagrams and textbooks use **conventional current**: current flows from + to −. That convention predates the discovery of the electron. In a metal wire the charge carriers are actually electrons, which are negative and drift the opposite way, from − to +.

Both descriptions predict the same voltages, currents and power. Every formula, datasheet and schematic symbol uses conventional current. A forward-biased diode carries conventional current from anode to cathode (the bar). An LED's outward arrows indicate light, not current. Use conventional current and treat electron flow as a physics detail.

## Pitfalls

- **Measuring a voltage "at a point" without a reference.** Always know which two points you mean. Usually one of them is ground.
- **Forgetting the return path.** A direct single-ended GPIO signal needs its reference/return; isolated interfaces use a different return arrangement.
- **Ignoring power.** A resistor that's correct by Ohm's law can still cook if P = I²R exceeds its rating.
- **Prefix slips.** 1 MΩ instead of 1 kΩ is a thousand-fold error. Write values with their units every time.

## Key takeaways

- Voltage is between two points, current flows through a component, resistance opposes current, and power is energy per second.
- Ohm's law V = IR applies to resistors. Use it on the resistor, not on an LED or diode.
- P = VI = I²R = V²/R. Check every resistor against its power rating.
- Current needs a complete loop, and the return path is part of the circuit.
- Ground is the reference you measure against. Connected devices must share it.
- Use conventional current (+ to −). Electron flow is the physical reality in wires but gives the same answers.
- This module stays at low voltage. Never work on mains.

## Further reading

- [Ohm's law (Wikipedia)](https://en.wikipedia.org/wiki/Ohm%27s_law)
- [Electric power (Wikipedia)](https://en.wikipedia.org/wiki/Electric_power)
- [Electric current: conventional current (Wikipedia)](https://en.wikipedia.org/wiki/Electric_current)
- [Kirchhoff's circuit laws (Wikipedia)](https://en.wikipedia.org/wiki/Kirchhoff%27s_circuit_laws)
- [Ground (electricity) (Wikipedia)](https://en.wikipedia.org/wiki/Ground_(electricity))
- [Metric prefix (Wikipedia)](https://en.wikipedia.org/wiki/Metric_prefix)
- [Voltage, current, resistance and Ohm's law (SparkFun)](https://learn.sparkfun.com/tutorials/voltage-current-resistance-and-ohms-law/all)
