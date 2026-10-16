---
id: elec-resistor-power-budget
sourceLesson: elec-ohms-law
title: "Resistor heat and an LED power budget"
level: basic
minutes: 3
summary: "Check resistor heat as well as current."
---

Check resistor heat as well as current.

## Power: voltage times current
Power tells you how fast a part turns electrical energy into heat (or light). It's what decides whether a resistor survives. For a two-terminal part, instantaneous absorbed power is voltage times current when positive current enters the terminal labelled positive. In steady DC that is also the time-averaged electrical power. With changing signals, average the instantaneous product; multiplying arbitrary RMS voltages and currents is not a universal power rule:

```formula
P = VI
where
P: the power, in watts (W); 1 W is 1 joule of energy per second
V: the voltage across the part, in volts (V)
I: the current through the part, in amperes (A)
W: watts, the unit of power
In words: with the passive sign convention, voltage times current gives absorbed power. In this steady-DC example, 1 volt and 1 amp mean 1 watt; a negative result means the part supplies power.
```

For a resistor only, you can substitute Ohm's law into it. Replace V with I × R to get the second line, or replace I with V / R to get the third:

```formula
P = VI
P = (IR)I = I^2 R
P = V(V / R) = V^2 / R
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

The squared forms only work for resistors, because they rely on Ohm's law. For a steady-DC LED, multiply its voltage by its current. A chip can have several supply and signal terminals; budget the relevant power flows rather than assuming one pair describes every path.

Power matters because resistors, regulators and chips all have a maximum they can dissipate before they overheat. A typical small through-hole resistor is rated at 0.25 W (check the actual part's datasheet).

> [!example] An LED's resistor
> A 5 V supply drives an LED through a 330 Ω resistor, and you measure 10 mA. How much voltage does the resistor take, how hot does it get, and what is left for the LED?

```formula
V_R = IR
V_R = 0.010 A × 330 Ω = 3.3 V
P_R = V_R I
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

# Resistor drop; all current is in amps.
V_R = I * R        # Ohm's law
# Convert watts to mW only for display.
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

## Key takeaways

- Check resistor heat as well as current.
- The squared power formulas assume an ohmic resistor with a fixed resistance.

## Further reading

- [OpenStax: electrical energy and power](https://openstax.org/books/university-physics-volume-2/pages/9-5-electrical-energy-and-power)
- [SparkFun: LED current limiting](https://learn.sparkfun.com/tutorials/light-emitting-diodes-leds/all)
