---
id: elec-dividers
title: Series, parallel and voltage dividers
level: basic
minutes: 13
summary: Combining resistors, the voltage divider formula, why loading a divider changes its output, and how a knob on a synth is just a divider with a moving tap.
---

Every knob on a microcontroller synth is a voltage divider. The board reads the voltage at the knob's middle pin with an ADC and turns it into a number. To wire knobs correctly, and to understand why some readings come out wrong, you need series and parallel resistance and the divider formula.

## Series: one path, resistances add

Components in **series** share a single current path. The same current flows through each one, and their voltages add up to the total.

```
R_total = R1 + R2 + R3 + ...
```

A 1 kΩ and a 2.2 kΩ in series behave like one 3.2 kΩ resistor. The series total is always larger than the largest part.

## Parallel: several paths, conductances add

Components in **parallel** connect across the same two nodes, so they all have the **same voltage**. The currents split between the branches and add up to the total.

```
1/R_total = 1/R1 + 1/R2 + ...

two resistors:
R_total = (R1 × R2) / (R1 + R2)
```

Three facts are worth memorising:

- Two equal resistors in parallel give half the value: 10 kΩ ∥ 10 kΩ = 5 kΩ.
- The parallel total is always **smaller than the smallest** branch.
- A much larger resistor in parallel barely changes anything: 10 kΩ ∥ 1 MΩ ≈ 9.9 kΩ.

The symbol ∥ means "in parallel with".

## The voltage divider

Two resistors in series across a supply split the voltage in proportion to their resistances. The output is taken from the junction:

```diagram
 Vin ──┐
       R1
       ├──── Vout
       R2
 GND ──┘
```

Because the same current I = Vin / (R1 + R2) flows through both resistors, the voltage across R2 is I × R2:

```
Vout = Vin × R2 / (R1 + R2)
```

Examples:

- R1 = R2: Vout = Vin / 2. Two 10 kΩ across 3.3 V give 1.65 V.
- R1 = 20 kΩ, R2 = 10 kΩ from 5 V: Vout = 5 × 10/30 ≈ 1.67 V.
- The ratio sets the output, not the absolute values. 1 kΩ/1 kΩ and 100 kΩ/100 kΩ both halve the voltage when unloaded.

The absolute values still matter in two ways. They set the standing current (and so the wasted power), and they determine how badly the output sags when something draws current from it.

## Loading: the divider's output changes when you use it

The formula assumes nothing draws current from Vout. Anything you connect there is a **load**, and it sits in parallel with R2. That lowers the effective bottom resistance, so Vout falls.

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

The divider's **output resistance** (its source impedance) is R1 ∥ R2. Here that's 10 kΩ ∥ 10 kΩ = 5 kΩ. The lower it is, the less a load disturbs it, but the more standing current the divider wastes.

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

Wire one end to the supply, the other to ground, and the wiper is a divider output. Turn the knob and you move the split point between "R1" and "R2". The total stays fixed, so for a 10 kΩ pot, R1 + R2 = 10 kΩ at every position.

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

- Series resistances add. Parallel resistances combine to less than the smallest branch; for two, (R1·R2)/(R1+R2).
- Vout = Vin × R2 / (R1 + R2). The ratio sets the voltage.
- A load sits in parallel with R2 and pulls Vout down. Keep loads well above the divider's resistance.
- The divider's output resistance is R1 ∥ R2. ADC inputs have a maximum source impedance; check the datasheet.
- A pot is a divider with a moving tap: ends to reference and ground, wiper to the ADC.
- Linear taper suits ADC knobs because curves can be applied in code. Log taper suits analogue volume.

## Further reading

- [Voltage divider (Wikipedia)](https://en.wikipedia.org/wiki/Voltage_divider)
- [Series and parallel circuits (Wikipedia)](https://en.wikipedia.org/wiki/Series_and_parallel_circuits)
- [Potentiometer, including taper markings (Wikipedia)](https://en.wikipedia.org/wiki/Potentiometer)
- [Input impedance (Wikipedia)](https://en.wikipedia.org/wiki/Input_impedance)
- [Voltage dividers (SparkFun)](https://learn.sparkfun.com/tutorials/voltage-dividers/all)
