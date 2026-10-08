---
id: elec-ohms-law
title: Voltage, current, resistance and power
level: basic
minutes: 15
summary: The four quantities behind every circuit, Ohm's law, electrical power, unit prefixes, ground as a reference, complete circuits, and which way current "flows".
---

Every circuit in a synth, from an LED on the front panel to the board's audio output, obeys a few simple rules. Learn them well now and the rest of this module is mostly applying them.

> [!warning] Low voltage only
> This module covers low-voltage DC work only: USB power, bench supplies of a few volts, and batteries. It does **not** cover mains wiring or mains power supplies. Use a ready-made, certified supply (a USB charger or a bench supply) and never open or modify anything that plugs into the wall.

## Four quantities

**Voltage** (written V, measured in volts, also V) is the difference in electrical potential between two points. It is the "push". A voltage is always *between* two points. "This pin is at 3.3 V" really means "3.3 V higher than ground".

**Current** (electric current, written I, measured in amperes or amps, A) is the rate at which charge flows past a point. One amp is one coulomb per second. Current flows *through* things.

**Resistance** (electrical resistance, written R, measured in ohms, Ω) is how strongly something opposes current. A resistor is a part made to have a known resistance.

**Power** (electrical power, written P, measured in watts, W) is the rate at which energy is transferred, for example turned into heat in a resistor or into light in an LED.

A water analogy helps at first: voltage is pressure, current is flow rate, and resistance is a narrow pipe. Don't push it too far. It breaks down for capacitors and for anything at audio or radio frequencies.

## Ohm's law

Ohm's law is the rule you use most: it links the voltage across a resistor to the current through it. For a resistor, the two are proportional. Double the voltage and the current doubles. The resistance is the fixed ratio between them:

```formula
V = I × R
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

Ohm's law describes resistors (and wires). It does not describe LEDs and diodes. Their current rises steeply once the voltage passes a threshold, so dividing the LED's voltage by some "resistance" gives a meaningless answer. You apply Ohm's law to the resistor in series with the LED instead, as in the worked example below.

## Power: voltage times current

Power tells you how fast a part turns electrical energy into heat (or light). It's what decides whether a resistor survives. Power is voltage times current, for any part:

```formula
P = V × I
where
P: the power, in watts (W); 1 W is 1 joule of energy per second
V: the voltage across the part, in volts (V)
I: the current through the part, in amperes (A)
W: watts, the unit of power
In words: power is voltage times current. 1 volt driving 1 amp is 1 watt. This holds for any component, not just resistors.
```

For a resistor only, you can substitute Ohm's law into it. Replace V with I × R to get the second line, or replace I with V / R to get the third:

```formula
P = V × I
P = (I × R) × I = I^2 × R
P = V × (V / R) = V^2 / R
where
P: the power the resistor turns into heat, in watts (W)
V: the voltage across the resistor, in volts (V)
I: the current through the resistor, in amperes (A)
R: the resistance, in ohms (Ω)
I^2: the current squared (multiplied by itself)
V^2: the voltage squared
W: watts, the unit of power
In words: all three lines give the same answer for a resistor. Use whichever matches the two quantities you know. Because current and voltage are squared, doubling either one quadruples the heat.
```

The squared forms only work for resistors, because they rely on Ohm's law. For an LED or a chip, multiply its measured voltage by its measured current instead.

Power matters because resistors, regulators and chips all have a maximum they can dissipate before they overheat. A typical small through-hole resistor is rated at 0.25 W (check the actual part's datasheet).

> [!example] An LED's resistor
> A 5 V supply drives an LED through a 330 Ω resistor, and you measure 10 mA. How much voltage does the resistor take, how hot does it get, and what is left for the LED?

```formula
V_R = I × R
V_R = 0.010 A × 330 Ω = 3.3 V
P_R = V_R × I
P_R = 3.3 V × 0.010 A = 0.033 W = 33 mW
V_LED = V_supply − V_R = 5 V − 3.3 V = 1.7 V
where
V_R: the voltage across the resistor, in volts (V)
I: the current in the loop, here 10 mA = 0.010 amperes (A)
R: the resistor's resistance, here 330 ohms (Ω)
P_R: the power the resistor turns into heat, in watts (W)
V_LED: the voltage left across the LED, in volts (V)
V_supply: the supply voltage, here 5 V
V: volts, the unit of voltage
A: amperes, the unit of current
Ω: ohms, the unit of resistance
W: watts, the unit of power
mW: milliwatts; 1 mW = 0.001 W
In words: the resistor takes 3.3 V and makes 33 mW of heat, well inside a typical 0.25 W (250 mW) rating, and the remaining 1.7 V is across the LED.
```

The same sum as a short Python script:

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
- Schematics often put the prefix where the decimal point would be (the RKM code, part of IEC 60062): `4k7` means 4.7 kΩ, `2R2` means 2.2 Ω, and `100n` means 100 nF.
- A handy pairing: volts ÷ kilohms = milliamps. 3.3 V across 1 kΩ is 3.3 mA.

## Complete circuits

Current only flows around a **closed loop** (a complete circuit): from the supply's positive terminal, through the load, and back to the supply's negative terminal. Break the loop anywhere (an open switch, a loose jumper, a cracked solder joint) and the current everywhere in that loop drops to zero.

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

Kirchhoff's voltage law is the other half: around any closed loop, the voltage rises equal the drops. It's how you work out what is left for the LED once the resistor has taken its share:

```formula
V_supply = V_R + V_LED
5 V = 3.3 V + 1.7 V
where
V_supply: the voltage the supply raises, in volts (V)
V_R: the voltage dropped across the resistor, in volts
V_LED: the voltage dropped across the LED, in volts
V: volts, the unit of voltage
In words: going once round the loop, the voltage the supply provides is used up exactly by the parts in the loop. Nothing is left over and nothing is missing.
```

Both laws assume the wires themselves are ideal. Real wires have a tiny resistance, which is why "ground" isn't exactly the same voltage everywhere (see below).

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
- **Ignoring power.** A resistor that's correct by Ohm's law can still cook if its power (current squared times resistance) exceeds its rating.
- **Prefix slips.** 1 MΩ instead of 1 kΩ is a thousand-fold error. Write values with their units every time.

## Key takeaways

- Voltage is between two points, current flows through a component, resistance opposes current, and power is energy per second.
- Ohm's law (voltage equals current times resistance) applies to resistors. Use it on the resistor, not on an LED or diode.
- Power is voltage times current. For a resistor that also equals current squared times resistance, or voltage squared divided by resistance. Check every resistor against its power rating.
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
