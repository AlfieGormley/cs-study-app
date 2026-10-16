---
id: elec-divider-loading
sourceLesson: elec-dividers
title: "Loading, source resistance and divider limits"
level: basic
minutes: 4
summary: "Combine a resistive load with the bottom resistor first."
---

Combine a resistive load with the bottom resistor first.

## Loading: the divider's output changes when you use it
The divider formula assumes nothing draws current from the output. Anything you connect there is a **load** (an electrical load), and it sits in parallel with the bottom resistor. That lowers the effective bottom resistance, so the output falls. To find the loaded output, combine the load with the bottom resistor first, then use the divider formula as before:

```formula
R2_eff = R2 ∥ R_load
Vout = Vin R2_eff / (R1 + R2_eff)
where
R2_eff: the effective bottom resistance with the load attached, in ohms (Ω)
R2: the bottom resistor, in ohms
R_load: the resistance of whatever is connected to the output, in ohms
∥: "in parallel with", worked out as (a × b) / (a + b)
Vout: the loaded output voltage, in volts (V)
Vin: the input voltage, in volts
R1: the top resistor, in ohms
In words: a load in parallel with the bottom resistor makes it look smaller, so the output voltage falls.
```

For a 10 kΩ/10 kΩ divider from 3.3 V with a 10 kΩ load:

```formula
R2_eff = 10 kΩ ∥ 10 kΩ = 5 kΩ
Vout = 3.3 V × 5 kΩ / (10 kΩ + 5 kΩ)
Vout = 1.1 V
where
R2_eff: the bottom resistor with the load in parallel
Vout: the loaded output voltage
∥: "in parallel with"
kΩ: kilohms; 1 kΩ = 1000 ohms
V: volts, the unit of voltage
In words: a load equal to the bottom resistor drags the output from 1.65 V down to 1.1 V, a third lower.
```

The script below repeats this for several loads:

```python
# Both input resistances are in ohms.
def par(a, b):
    return a * b / (a + b)

def divider(vin, r1, r2):
    return vin * r2 / (r1 + r2)

vin, r1, r2 = 3.3, 10e3, 10e3
v0 = divider(vin, r1, r2)
print(f"unloaded: {v0:.3f} V")
for load in (1e6, 100e3, 10e3, 1e3):
    # The load shunts the lower resistor.
    v = divider(vin, r1, par(r2, load))
    k = load / 1e3
    print(f"load {k:>6.0f}k: {v:.3f} V")
```

```
unloaded: 1.650 V
load   1000k: 1.642 V
load    100k: 1.571 V
load     10k: 1.100 V
load      1k: 0.275 V
```

For a resistive load, compare it with the divider’s output resistance and your allowed error: a load ten times that resistance causes about 9.1% sag, while a hundred times causes about 1% sag. These are trade-offs, not universal pass/fail limits. A 1 MΩ load barely moves a 10 kΩ divider. A 10 kΩ load drags it from 1.65 V to 1.10 V.

The divider's **output resistance** (its source impedance) tells you how easily a load can pull it around. Seen from the output, the supply acts like a short for changes, so the two resistors appear in parallel:

```formula
R_out = R1 ∥ R2 = (R1 R2) / (R1 + R2)
R_out = (10 kΩ × 10 kΩ) / 20 kΩ = 5 kΩ
where
R_out: the divider's output resistance, in ohms (Ω)
R1: the top resistor, here 10 kΩ
R2: the bottom resistor, here 10 kΩ
∥: "in parallel with"
kΩ: kilohms; 1 kΩ = 1000 ohms (Ω)
In words: the divider behaves like a perfect voltage source with 5 kΩ in series. Loads much larger than 5 kΩ barely move it.
```

The lower the output resistance, the less a load disturbs it, but the more **divider standing current** (the current that flows through the divider all the time) it wastes.

> [!note] Why this matters for ADCs
> A microcontroller's ADC input isn't a pure open circuit. Many ADCs briefly connect a small sampling capacitor that has to charge through the source's resistance. If the source impedance is too high, the sampling capacitor may not settle to the new input voltage; the error can have either sign depending on its previous charge, and noise can also matter. The chip's datasheet or reference manual states the maximum source impedance for a given sampling time. Check it for your board rather than assuming a value.

### Dividers are not power supplies

A divider can make a reference voltage for a high-impedance input. It can't power anything that draws significant or varying current. Feed a 5 V-to-3.3 V divider into a board's power pin and the voltage collapses as soon as the board draws current. Use a voltage regulator for power.

## Key takeaways

- Combine a resistive load with the bottom resistor first.
- Output resistance and allowed error determine acceptable loading.

## Further reading

- [TI: linear-regulator fundamentals](https://www.ti.com/video/series/power-fundamentals-linear-regulator-fundamentals.html)

- [SparkFun: voltage dividers](https://learn.sparkfun.com/tutorials/voltage-dividers/all)
- [OpenStax: series and parallel resistors](https://openstax.org/books/university-physics-volume-2/pages/10-2-resistors-in-series-and-parallel)
