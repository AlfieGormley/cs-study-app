---
id: elec-dividers
title: Series, parallel and voltage dividers
level: basic
minutes: 17
summary: Combining resistors, the voltage divider formula, why loading a divider changes its output, and how a knob on a synth is just a divider with a moving tap.
---

Every knob on a microcontroller synth is a voltage divider. The board reads the voltage at the knob's middle pin with an ADC and turns it into a number. To wire knobs correctly, and to understand why some readings come out wrong, you need series and parallel resistance and the divider formula.

## Series: one path, resistances add

Components in **series** (a series circuit) share a single current path. The same current flows through each one, and their voltages add up to the total. Because the current has to push through every resistor in turn, their resistances simply add:

```formula
R_total = R1 + R2 + R3 + ...
where
R_total: the single resistance that behaves the same as the whole chain, in ohms (Ω)
R1: the first resistor in the chain, in ohms
R2: the second resistor, in ohms
R3: the third resistor, in ohms
...: and so on, for as many resistors as are in the chain
Ω: ohms, the unit of resistance
In words: resistors in series add up. The total is always larger than the largest one.
```

For example, a 1 kΩ and a 2.2 kΩ in series:

```formula
R_total = R1 + R2
R_total = 1 kΩ + 2.2 kΩ = 3.2 kΩ
where
R_total: the combined resistance, in ohms (Ω)
R1: the first resistor, here 1 kΩ
R2: the second resistor, here 2.2 kΩ
kΩ: kilohms; 1 kΩ = 1000 ohms (Ω)
In words: the pair behaves exactly like one 3.2 kΩ resistor.
```

## Parallel: several paths, conductances add

Components in **parallel** (a parallel circuit) connect across the same two connection points, so they all have the **same voltage**. The currents split between the branches and add up to the total. Each extra branch is another path for current, so the combination conducts *more* easily than any branch alone.

The easy way to add them is by **conductance**, which is one divided by resistance (how easily current flows). Conductances in parallel add:

```formula
1 / R_total = 1 / R1 + 1 / R2 + ...
where
R_total: the single resistance that behaves the same as all the branches together, in ohms (Ω)
R1: the first branch's resistance, in ohms
R2: the second branch's resistance, in ohms
...: and so on, one term per branch
Ω: ohms, the unit of resistance
In words: add up one-over-resistance for every branch, then take one over the answer. Each branch adds a path, so the total always comes out smaller than the smallest branch.
```

For exactly two resistors this rearranges into a handier "product over sum" form. The symbol ∥ is shorthand for "in parallel with":

```formula
R1 ∥ R2 = (R1 × R2) / (R1 + R2)
where
R1 ∥ R2: the combined resistance of R1 and R2 in parallel, in ohms (Ω)
∥: "in parallel with"
R1: the first resistor, in ohms
R2: the second resistor, in ohms
Ω: ohms, the unit of resistance
In words: for two resistors in parallel, multiply them, then divide by their sum.
```

Three facts are worth memorising:

- Two equal resistors in parallel give half the value: 10 kΩ ∥ 10 kΩ = 5 kΩ.
- The parallel total is always **smaller than the smallest** branch.
- A much larger resistor in parallel barely changes anything:

```formula
10 kΩ ∥ 1 MΩ = (10 kΩ × 1000 kΩ) / 1010 kΩ
10 kΩ ∥ 1 MΩ ≈ 9.9 kΩ
where
∥: "in parallel with"
kΩ: kilohms; 1 kΩ = 1000 ohms (Ω)
MΩ: megohms; 1 MΩ = 1000 kΩ = 1,000,000 Ω
≈: approximately equal to (rounded)
In words: putting a 1 MΩ resistor across a 10 kΩ one lowers it by only about 1%, because almost all the current takes the easier 10 kΩ path.
```

## The voltage divider

Two resistors in series across a supply split the voltage in proportion to their resistances. The output is taken from the junction:

```diagram
 Vin ──┐
       R1
       ├──── Vout
       R2
 GND ──┘
```

The formula comes straight from the two laws in lesson 1. The resistors are in series, so one current flows through both, set by their total. Ohm's law on R2 alone then gives the voltage across it:

```formula
I = Vin / (R1 + R2)
Vout = I × R2
Vout = Vin × R2 / (R1 + R2)
where
I: the current flowing down through both resistors, in amperes (A)
Vin: the input (supply) voltage across the whole divider, in volts (V)
Vout: the output voltage, measured from the junction to ground, in volts
R1: the top resistor, between Vin and the output, in ohms (Ω)
R2: the bottom resistor, between the output and ground, in ohms
In words: the output is the input voltage scaled by the bottom resistor's share of the total resistance. This holds only when nothing draws current from the output.
```

Two examples:

```formula
Vout = 3.3 V × 10 kΩ / (10 kΩ + 10 kΩ)
Vout = 3.3 V × 0.5 = 1.65 V
Vout = 5 V × 10 kΩ / (20 kΩ + 10 kΩ)
Vout = 5 V × 1/3 ≈ 1.67 V
where
Vout: the divider's unloaded output, in volts (V)
V: volts, the unit of voltage
kΩ: kilohms; 1 kΩ = 1000 ohms
≈: approximately equal to (rounded)
In words: two equal resistors halve the voltage. With 20 kΩ on top and 10 kΩ below, the bottom resistor is a third of the total, so you get a third of the 5 V.
```

The ratio sets the output, not the absolute values. 1 kΩ/1 kΩ and 100 kΩ/100 kΩ both halve the voltage when unloaded.

The absolute values still matter in two ways. They set the standing current (and so the wasted power), and they determine how badly the output sags when something draws current from it.

## Loading: the divider's output changes when you use it

The divider formula assumes nothing draws current from the output. Anything you connect there is a **load** (an electrical load), and it sits in parallel with the bottom resistor. That lowers the effective bottom resistance, so the output falls. To find the loaded output, combine the load with the bottom resistor first, then use the divider formula as before:

```formula
R2_eff = R2 ∥ R_load
Vout = Vin × R2_eff / (R1 + R2_eff)
where
R2_eff: the effective bottom resistance with the load attached, in ohms (Ω)
R2: the bottom resistor, in ohms
R_load: the resistance of whatever is connected to the output, in ohms
∥: "in parallel with", worked out as (a × b) / (a + b)
Vout: the loaded output voltage, in volts (V)
Vin: the input voltage, in volts
R1: the top resistor, in ohms
In words: a load in parallel with the bottom resistor makes it look smaller, so the output drops.
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
def par(a, b):
    return a * b / (a + b)

def divider(vin, r1, r2):
    return vin * r2 / (r1 + r2)

vin, r1, r2 = 3.3, 10e3, 10e3
v0 = divider(vin, r1, r2)
print(f"unloaded: {v0:.3f} V")
for load in (1e6, 100e3, 10e3, 1e3):
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

The rule of thumb is to make the load at least 10× (better 100×) the divider's resistances. A 1 MΩ load barely moves a 10 kΩ divider. A 10 kΩ load drags it from 1.65 V to 1.10 V.

The divider's **output resistance** (its source impedance) tells you how easily a load can pull it around. Seen from the output, the supply acts like a short for changes, so the two resistors appear in parallel:

```formula
R_out = R1 ∥ R2 = (R1 × R2) / (R1 + R2)
R_out = (10 kΩ × 10 kΩ) / 20 kΩ = 5 kΩ
where
R_out: the divider's output resistance, in ohms (Ω)
R1: the top resistor, here 10 kΩ
R2: the bottom resistor, here 10 kΩ
∥: "in parallel with"
kΩ: kilohms; 1 kΩ = 1000 ohms (Ω)
In words: the divider behaves like a perfect voltage source with 5 kΩ in series. Loads much larger than 5 kΩ barely move it.
```

The lower the output resistance, the less a load disturbs it, but the more **standing current** (the current that flows through the divider all the time) it wastes.

> [!note] Why this matters for ADCs
> A microcontroller's ADC input isn't a pure open circuit. Many ADCs briefly connect a small sampling capacitor that has to charge through the source's resistance. If the source impedance is too high, the reading comes out low or noisy. The chip's datasheet or reference manual states the maximum source impedance for a given sampling time. Check it for your board rather than assuming a value.

### Dividers are not power supplies

A divider can make a reference voltage for a high-impedance input. It can't power anything that draws significant or varying current. Feed a 5 V-to-3.3 V divider into a board's power pin and the voltage collapses as soon as the board draws current. Use a voltage regulator for power.

## The potentiometer: a divider with a moving tap

A **potentiometer** (pot) is a resistive track with a wiper that slides along it. It has three terminals: the two ends of the track and the wiper.

```diagram
  pin 1 ──/\/\/\/\/\/\── pin 3
              ↑
           pin 2 (wiper)
```

Wire one end to the supply, the other to ground, and the wiper is a divider output. Turn the knob and you move the split point between the upper part of the track and the lower part. The total stays fixed:

```formula
R_top + R_bottom = R_pot
V_wiper = Vin × R_bottom / R_pot
where
R_top: the track resistance between the supply end and the wiper, in ohms (Ω)
R_bottom: the track resistance between the wiper and the ground end, in ohms
R_pot: the pot's total (end-to-end) resistance, in ohms, e.g. 10 kΩ
V_wiper: the voltage on the wiper, measured to ground, in volts (V)
Vin: the voltage across the whole track, in volts
In words: the two parts of the track always add up to the pot's value, and the wiper voltage is the input scaled by the lower part's share.
```

For a 10 kΩ pot across 3.3 V with the wiper a quarter of the way up (2.5 kΩ below it), the wiper sits at 3.3 V × 2.5/10 ≈ 0.83 V.

For a microcontroller knob:

```diagram
 3.3V ── pin 3
        pot track ── pin 2 ── ADC pin
 GND ── pin 1
```

Points to watch:

- **Use the board's documented analogue supply for the pot, matching the ADC range.** Do not load an unbuffered VREF pin unless the documentation explicitly allows it. If the pot is fed from a different voltage, the ADC's full range won't match the knob's full range. Feeding it from a higher voltage could also exceed the input's maximum (lesson 4).
- **Swapping pins 1 and 3** reverses the direction of the knob. It's harmless and easily fixed in software.
- **Never wire the wiper straight to a supply rail.** At one extreme the wiper sits at the end connected to ground, and you'd short the supply through a few ohms of track.
- **The pot's resistance** trades standing current against source impedance. Values around 10 kΩ are a common choice for microcontroller knobs, but confirm against the ADC's source-impedance limit.

## Linear and logarithmic (audio) taper

The **taper** (or law) is how resistance changes with rotation.

- **Linear taper:** halfway round, the wiper is at half the total resistance. Output voltage is proportional to angle.
- **Logarithmic or "audio" taper:** the resistance changes slowly at first, then quickly. A common specification is a 10% log taper, meaning the wiper is at 10% of the total at mid-rotation. Hearing is roughly logarithmic, so a log pot makes an analogue volume control feel even.

| Rotation | Linear | 10% log (approx.) |
|---|---|---|
| 0% | 0% | 0% |
| 50% | 50% | 10% |
| 100% | 100% | 100% |

Two practical warnings:

- **Markings aren't standardised.** Many Asian and US pots use "A" for log and "B" for linear, but some European makers use "A" for linear. Read the datasheet.
- **Cheap log pots are approximations,** often two linear segments joined near the middle.

> [!tip] For digital synths, usually choose linear
> When a pot feeds an ADC, you can apply any curve you like in software. A linear pot gives even resolution across the whole rotation, and code can map it to a logarithmic volume or exponential frequency response. A log pot is mostly useful when it directly controls an analogue audio level.

## Pitfalls

- **Forgetting the load.** A divider measured with nothing attached may read differently once connected.
- **Using a divider as a supply.** It can't hold its voltage under a changing load.
- **Pot fed from the wrong voltage.** Use the documented supply matched to the ADC range, never above the input's maximum.
- **Assuming the taper letter.** Check the datasheet.

## Key takeaways

- Series resistances add. Parallel resistances combine to less than the smallest branch; for two, multiply them and divide by their sum.
- A divider's output is the input scaled by the bottom resistor's share of the total. The ratio sets the voltage.
- A load sits in parallel with the bottom resistor and pulls the output down. Keep loads well above the divider's resistance.
- The divider's output resistance is its two resistors in parallel. ADC inputs have a maximum source impedance; check the datasheet.
- A pot is a divider with a moving tap: ends to reference and ground, wiper to the ADC.
- Linear taper suits ADC knobs because curves can be applied in code. Log taper suits analogue volume.

## Further reading

- [Voltage divider (Wikipedia)](https://en.wikipedia.org/wiki/Voltage_divider)
- [Series and parallel circuits (Wikipedia)](https://en.wikipedia.org/wiki/Series_and_parallel_circuits)
- [Potentiometer, including taper markings (Wikipedia)](https://en.wikipedia.org/wiki/Potentiometer)
- [Input impedance (Wikipedia)](https://en.wikipedia.org/wiki/Input_impedance)
- [Voltage dividers (SparkFun)](https://learn.sparkfun.com/tutorials/voltage-dividers/all)
