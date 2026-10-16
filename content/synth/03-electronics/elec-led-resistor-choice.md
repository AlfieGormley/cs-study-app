---
id: elec-led-resistor-choice
sourceLesson: elec-components
title: "Choosing an LED’s current-limiting resistor"
level: intermediate
minutes: 4
summary: "Subtract the LED drop before sizing the resistor."
---

Subtract the LED drop before sizing the resistor.

## LEDs and the current-limiting resistor
An LED is a diode that emits light. It normally conducts strongly under forward bias and carries much less reverse current within its reverse-voltage limits. Its current rises steeply with forward voltage; the quoted **forward voltage** (written V_f) is measured at a stated current rather than being a fixed switching threshold, so an LED always needs something to limit its current, usually a series resistor.

The forward voltage depends on colour and current. For a typical red indicator LED it's around 1.8–2.2 V at 20 mA, and for blue and white around 3–3.5 V. Datasheet maximums are higher: For a concrete example, the Kingbright WP7113ID red LED datasheet and WP7113QBC/D blue LED datasheet give their own forward-voltage figures at specified test currents. WP7113ID revision V.14A dated 8 January 2026 lists 1.9 V typical and 2.3 V maximum at 10 mA; WP7113QBC/D revision V.18B dated 26 March 2025 lists 3.3 V typical and 4.0 V maximum at 20 mA (both checked 16 October 2026). Package size or colour alone is not a specification. Use the figures from your LED's datasheet. Small 3 mm and 5 mm indicator LEDs are usually characterised at 20 mA, with an absolute-maximum continuous current often in the 20–30 mA range. A characterization current is not a recommended default drive current. Use the exact LED’s allowed current and thermal derating; many indicators are useful at only a few milliamps.

The resistor's job is to take whatever voltage the LED doesn't. Kirchhoff's voltage law gives that leftover voltage, and Ohm's law on the resistor turns it into a resistance:

```formula
R = (V_supply − V_f) / I_LED
R = (3.3 V − 2.0 V) / 0.005 A = 260 Ω
where
R: the series resistor, in ohms (Ω)
V_supply: the supply or pin voltage, here 3.3 volts (V)
V_f: the LED's forward voltage at the chosen current, here about 2.0 V
I_LED: the LED current you want, here 5 mA = 0.005 amperes (A)
V: volts, the unit of voltage
A: amperes, the unit of current
Ω: ohms, the unit of resistance
In words: subtract the LED's forward voltage from the supply, then divide by the current you want. 1.3 V at 5 mA needs 260 Ω.
```

260 Ω is not an E12 preferred value, so pick the next E12 value up, 270 Ω, and recalculate what you actually get:

```formula
I = (V_supply − V_f) / R
I = 1.3 V / 270 Ω ≈ 0.00481 A = 4.81 mA
P = 1.3 V × 0.00481 A ≈ 0.006 W = 6 mW
where
I: the actual LED current, in amperes (A)
V_supply: the supply, here 3.3 volts (V)
V_f: the forward voltage, here 2.0 V
R: the chosen resistor, here 270 ohms (Ω)
P: the power in the resistor, in watts (W)
V: volts
A: amperes
mA: milliamperes; 1 mA = 0.001 A
Ω: ohms
W: watts, the unit of power
mW: milliwatts; 1 mW = 0.001 W
≈: approximately equal to (rounded)
In words: 270 Ω gives just under 5 mA, and the resistor makes only about 6 mW of heat.
```

Forward voltage varies with device, current and temperature, so this nominal calculation is an estimate. A hardware bound uses maximum supply, minimum LED drop, minimum resistor value and all relevant component and pin limits. The same calculation in Python, including the safe E12 selection:

```python
import math

def led_resistor(vs, vf, i):
    return (vs - vf) / i

E12 = [10, 12, 15, 18, 22, 27,
       33, 39, 47, 56, 68, 82]

def next_e12_up(r):
    # Scale by decade; prefer a larger part.
    dec = 10 ** math.floor(math.log10(r))
    for base in E12 + [100]:
        if base * dec / 10 >= r:
            return base * dec / 10

r = led_resistor(3.3, 2.0, 0.005)
pick = next_e12_up(r)
i = (3.3 - 2.0) / pick
print(f"ideal R = {r:.0f} ohm")
print(f"E12 pick = {pick:.0f} ohm")
print(f"actual I = {i*1000:.2f} mA")
```

```
ideal R = 260 ohm
E12 pick = 270 ohm
actual I = 4.81 mA
```

Round **up** to the next standard value. That gives slightly less current, which is the safe direction. Then check the resistor's power (about 6 mW here) and the source's limits. When a microcontroller pin drives the LED, the pin's maximum output current from the board's datasheet also applies.

**LED orientation:** the longer leg is usually the anode (+). The cathode (−) is often marked by a flat on the rim. Check the datasheet. Reversed, it may stay dark but may also exceed its allowed reverse voltage. Do not apply a reverse voltage beyond the exact LED’s rating. LED reverse ratings are often only a few volts.

## Key takeaways

- Subtract the LED drop before sizing the resistor.
- Use worst-case supply, forward voltage and resistor tolerance for hardware.

## Further reading

- [Kingbright WP7113ID, revision V.14A](https://www.kingbrightusa.com/images/catalog/spec/wp7113id.pdf)
- [Kingbright WP7113QBC/D, revision V.18B](https://www.kingbrightusa.com/images/catalog/spec/wp7113qbc-d.pdf)
- [SparkFun: LED current limiting](https://learn.sparkfun.com/tutorials/light-emitting-diodes-leds/all)
