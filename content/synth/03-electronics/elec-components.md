---
id: elec-components
title: "Components: resistors, capacitors, LEDs, diodes, switches and connectors"
level: intermediate
minutes: 22
summary: The parts in every synth build. How to read their values and ratings, size an LED resistor, use the RC time constant, respect polarity, and check connector pinouts.
---

A synth build uses a small set of passive parts over and over. Each one has a **value** (what it does) and **ratings** (what it survives). Most beginner damage comes from ignoring the ratings or the polarity, not from getting the value slightly wrong.

## Resistors

### Reading the value

Through-hole resistors use colour bands defined by IEC 60062. Read from the end where the bands bunch together. The gold or silver tolerance band is usually at the other end, often slightly separated.

| Colour | Digit | Multiplier |
|---|---|---|
| Black | 0 | ×1 |
| Brown | 1 | ×10 |
| Red | 2 | ×100 |
| Orange | 3 | ×1k |
| Yellow | 4 | ×10k |
| Green | 5 | ×100k |
| Blue | 6 | ×1M |
| Violet | 7 | ×10M |
| Grey | 8 | ×100M |
| White | 9 | ×1G |
| Gold | | ×0.1 |
| Silver | | ×0.01 |

- **Four-band:** digit, digit, multiplier, tolerance. Yellow-violet-red-gold = 4, 7, ×100 = 4.7 kΩ ±5%.
- **Five-band** (precision): digit, digit, digit, multiplier, tolerance. Brown-black-black-red-brown = 1, 0, 0, ×100 = 10 kΩ ±1%.
- **Tolerance band:** brown ±1%, red ±2%, gold ±5%, silver ±10%.

The digit bands form a whole number, and the multiplier band scales it:

```formula
R = (10 × d_1 + d_2) × m
R = (10 × 4 + 7) × 100 Ω = 4700 Ω
where
R: the resistor's nominal value, in ohms (Ω)
d_1: the first digit band's number (yellow = 4)
d_2: the second digit band's number (violet = 7)
m: the multiplier band's factor (red = ×100)
Ω: ohms, the unit of resistance
In words: read the digit bands as a two-digit number, then multiply by the multiplier band. Yellow-violet-red gives 47 × 100 = 4700 Ω = 4.7 kΩ.
```

A five-band resistor works the same way with three digits: (100 × first + 10 × second + third) × multiplier. Brown-black-black-red gives 100 × 100 = 10 kΩ.

Colours are easy to misread under poor light. Brown, red and orange look alike, and so do violet and grey. **Measure with a multimeter before fitting** (out of circuit) whenever you're unsure.

### Preferred values

Resistors come in E-series values. E12 (for ±10%) has 12 values per decade (each tenfold range, such as 10 to 100): 10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82. E24 adds more in between. You calculate an ideal value, then choose the nearest standard value in the safe direction.

The values aren't arbitrary. They are spaced by a constant ratio, so neighbouring values are always about the same *percentage* apart:

```formula
v_n ≈ 10 × 10^{n/12}
v_4 ≈ 10 × 10^{4/12} ≈ 21.5 → 22
where
v_n: the n-th E12 value in the 10 to 100 decade (scale by 10, 100, 1000 … for other decades)
v_4: the value at step 4
n: the step number, 0 to 11 for the twelve values
10^{n/12}: ten raised to the power n ÷ 12; each step multiplies by about 1.21
≈: approximately equal to (the standard rounds each value to two digits)
→: rounds to
In words: each E12 value is about 21% above the one before, so the ±10% ranges of neighbouring values roughly touch and every resistance is covered. Five E12 values don't match plain rounding of the formula: 27, 33, 39, 47 and 82, where it gives 26.1, 31.6, 38.3, 46.4 and 82.5. They are older established values the standard kept, so take values from the table, not the formula.
```

E24 uses the same idea with 24 steps per decade (n ÷ 24), each about 10% apart.

### Tolerance and power rating

- **Tolerance** (component tolerance): how far a real part may be from its marked value. A 10 kΩ ±5% part may be anywhere from 9.5 to 10.5 kΩ. For a divider that sets a precise level, use 1% parts.
- **Power rating:** the most power the part can turn into heat continuously. Common small through-hole resistors are rated around 0.25 W. Check the datasheet. Calculate the power and leave margin. Running at half the rating or less is a common conservative practice.

```formula
R_min = R_nom × (1 − t)
R_max = R_nom × (1 + t)
R_min = 10 kΩ × 0.95 = 9.5 kΩ
R_max = 10 kΩ × 1.05 = 10.5 kΩ
where
R_nom: the nominal (marked) resistance, here 10 kΩ
t: the tolerance as a fraction, here ±5% = 0.05
R_min: the lowest value the part may really have
R_max: the highest value the part may really have
kΩ: kilohms; 1 kΩ = 1000 ohms (Ω)
In words: a ±5% part can be up to 5% below or above its marked value.
```

For the power check, use the resistor form of the power law from lesson 1:

```formula
P = I^2 × R
P = (0.010 A)^2 × 330 Ω = 0.033 W
where
P: the power the resistor turns into heat, in watts (W)
I: the current through it, here 10 mA = 0.010 amperes (A)
I^2: the current squared
R: the resistance, here 330 ohms (Ω)
A: amperes, the unit of current
Ω: ohms, the unit of resistance
W: watts, the unit of power
In words: 10 mA through 330 Ω makes 33 mW of heat, about an eighth of a 0.25 W rating, so a small resistor is comfortable.
```

## Capacitors

A capacitor stores charge between two plates separated by an insulator (the dielectric). Capacitance C is measured in farads (F). Practical values run from pF to thousands of µF.

### Behaviour

- It **blocks steady DC** once charged, because no current flows through the insulator.
- It **passes changes**, since current flows while its voltage is changing. This is why it can remove a DC offset from an audio signal or short fast noise to ground.
- Its voltage **can't jump instantly**. It changes at a rate set by the current:

```formula
ΔV / Δt = I / C
ΔV / Δt = 0.001 A / 0.000001 F
ΔV / Δt = 1000 V/s = 1 V/ms
where
ΔV: the change in the capacitor's voltage, in volts (V)
Δt: the time over which that change happens, in seconds (s)
Δ: delta, "the change in"
I: the current flowing into the capacitor, in amperes (A)
C: the capacitance, in farads (F)
A: amperes, the unit of current
F: farads, the unit of capacitance
V/s: volts per second
V/ms: volts per millisecond; 1 ms = 0.001 s
In words: the voltage rises faster with more current and slower with a bigger capacitor. 1 mA into 1 µF raises it by 1 V every millisecond. An instant jump would need infinite current, which is why it can't happen.
```

### The RC time constant

Charge a capacitor through a resistor from a fixed voltage and it follows an exponential charging curve: fast at first, then slower and slower as it nears the supply. The **RC time constant** sets how long that takes:

```formula
τ = R × C
τ = 10,000 Ω × 0.0000001 F = 0.001 s
where
τ: tau, the time constant, in seconds (s)
R: the resistance the capacitor charges through, here 10 kΩ = 10,000 ohms (Ω)
C: the capacitance, here 100 nF = 0.0000001 farads (F)
Ω: ohms, the unit of resistance
F: farads, the unit of capacitance
s: seconds; ohms × farads comes out in seconds
In words: a 10 kΩ resistor charging a 100 nF capacitor has a time constant of 1 millisecond. A bigger resistor or a bigger capacitor makes it slower.
```

The time constant is the unit of time for the charging curve:

```formula
V_C(t) = V_final × (1 − e^{−t/τ})
V_C(τ) = V_final × (1 − e^{−1})
V_C(τ) ≈ V_final × 0.632
where
V_C(t): the capacitor's voltage at time t, in volts (V)
t: the time since charging started, in seconds (s)
V_final: the voltage it is charging towards, in volts
e: Euler's number, about 2.718, the base of natural exponential growth and decay
e^{−t/τ}: e raised to the power minus t ÷ τ; it starts at 1 and falls towards 0
τ: tau, the time constant R × C, in seconds
≈: approximately equal to
In words: after one time constant the capacitor has covered about 63.2% of the way to its final voltage. Each further time constant covers 63.2% of what is left.
```

After five time constants it's within 1% of the final voltage (99.3%). The curve assumes an ideal capacitor and a steady source. The same shape, run backwards, describes discharging.

```python
import math

tau = 10e3 * 100e-9    # 10 kΩ, 100 nF
for n in (1, 2, 3, 5):
    pct = 100 * (1 - math.exp(-n))
    ms = n * tau * 1e3
    t = f"{n} tau = {ms:.1f} ms"
    print(f"{t}: {pct:.1f}%")
```

```
1 tau = 1.0 ms: 63.2%
2 tau = 2.0 ms: 86.5%
3 tau = 3.0 ms: 95.0%
5 tau = 5.0 ms: 99.3%
```

RC circuits show up across synth hardware. They smooth a noisy knob and slow a bouncing switch. A resistor followed by a capacitor to ground is also the simplest low-pass filter (an RC low-pass filter): it passes slow changes and shorts fast ones to ground. Its cut-off frequency is:

```formula
f_c = 1 / (2 × π × R × C)
f_c = 1 / (2 × π × 10,000 × 0.0000001)
f_c ≈ 159 Hz
where
f_c: the cut-off frequency, in hertz (Hz): where the output has fallen to about 71% of the input (−3 dB)
π: pi, about 3.14159
R: the resistance, here 10 kΩ = 10,000 ohms (Ω)
C: the capacitance, here 100 nF = 0.0000001 farads (F)
Hz: hertz, cycles per second
≈: approximately equal to (rounded)
In words: the same 10 kΩ and 100 nF that give a 1 ms time constant start cutting frequencies above about 159 Hz. Bigger R or C gives a lower cut-off.
```

This assumes whatever reads the capacitor draws almost no current. A load across the capacitor changes the cut-off, just as it loads a divider.

### Types

| Type | Polarised? | Typical use |
|---|---|---|
| Ceramic (MLCC) | No | Decoupling (100 nF), small values |
| Film | No | Audio signal paths, filters |
| Aluminium electrolytic | **Yes** | Bulk supply filtering, large µF |
| Tantalum | **Yes** | Compact bulk capacitance |

Things to watch:

- **Polarity.** Electrolytic and tantalum capacitors must have their + lead at the higher voltage. On aluminium electrolytics a stripe marks the **negative** lead, and the negative lead is usually the shorter one. On tantalum capacitors the marking works the other way: a stripe or bar usually marks the **positive** lead. Check the datasheet. Reverse them and they can overheat, vent or burst; tantalums can fail short and catch fire. Don't use a polarised capacitor where the voltage across it can reverse, such as a plain AC audio signal with no DC bias.
- **Voltage rating.** Every capacitor has a maximum working voltage. Choose one comfortably above the highest voltage it will see. A 6.3 V capacitor on a 5 V rail leaves little margin, so 10 V or 16 V is more comfortable. Margin is a design rule of thumb; check the manufacturer's guidance for the part.
- **Ceramic DC bias.** Many high-value ceramics (X7R, X5R and similar Class 2 dielectrics) lose a significant share of their capacitance when a DC voltage is applied, sometimes well over half near the rated voltage. The effect is documented in manufacturers' DC-bias curves. The "X7R" code itself only describes temperature behaviour (±15% from −55 to +125 °C); it says nothing about voltage. C0G/NP0 (Class 1) ceramics barely change with voltage or temperature, but come in much smaller values than Class 2 types of the same size.
- **Markings.** Small ceramics often use a three-digit code: two digits, then the number of zeros, in picofarads. `104` means 10 followed by four zeros:

```formula
C = (10 × d_1 + d_2) × 10^{d_3} pF
C = 10 × 10^4 pF = 100,000 pF = 100 nF
where
C: the capacitance
d_1: the first digit (1)
d_2: the second digit (0)
d_3: the third digit, the power of ten (4)
10^4: ten to the power 4, which is 10,000
pF: picofarads; 1 pF = 10^{-12} farads
nF: nanofarads; 1 nF = 1000 pF
In words: 104 is 10 with four zeros after it, in picofarads: 100,000 pF, which is 100 nF.
```

## LEDs and the current-limiting resistor

An LED is a diode that emits light. It conducts in one direction only. Above its **forward voltage** (written V_f) the current rises very steeply, so an LED always needs something to limit its current, usually a series resistor.

The forward voltage depends on colour and current. For a typical red indicator LED it's around 1.8–2.2 V at 20 mA, and for blue and white around 3–3.5 V. Datasheet maximums are higher: Kingbright's 5 mm parts, for example, list a red at 1.85 V typical, 2.5 V maximum, and a blue at 3.3 V typical, 4.0 V maximum. Use the figures from your LED's datasheet. Small 3 mm and 5 mm indicator LEDs are usually characterised at 20 mA, with an absolute-maximum continuous current often in the 20–30 mA range. Treat 20 mA as a ceiling, not a target: they're usually bright enough at a few milliamps.

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

260 Ω isn't a standard value, so pick the next E12 value up, 270 Ω, and recalculate what you actually get:

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

The forward voltage is only approximately constant, so the real current will differ a little. The same calculation in Python, including the rounding to E12:

```python
import math

def led_resistor(vs, vf, i):
    return (vs - vf) / i

E12 = [10, 12, 15, 18, 22, 27,
       33, 39, 47, 56, 68, 82]

def next_e12_up(r):
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

**LED polarity:** the longer leg is usually the anode (+). The cathode (−) is often marked by a flat on the rim. Check the datasheet. Reversed, it just stays dark at these voltages, but don't rely on reverse-voltage tolerance. LED reverse ratings are often only a few volts.

## Diodes

A diode lets conventional current flow from **anode** to **cathode** (towards the bar in its schematic symbol; an LED's outward arrows represent emitted light) and blocks it the other way. The cathode is marked with a band.

| Type | Forward drop (approx.) | Common use |
|---|---|---|
| Silicon (e.g. 1N4148) | ~0.6–0.75 V at a few mA | Small-signal, clamping |
| Silicon rectifier (e.g. 1N400x) | ~0.7 V small current, up to ~1 V at 1 A | Reverse-polarity protection |
| Schottky | ~0.2–0.4 V small current, ~0.45–0.6 V at 1 A | Low-drop protection |

The forward drops are approximate, and they rise with current and fall with temperature. Datasheets guarantee a maximum at a stated current (the 1N4148's is 1 V at 10 mA; the 1N5817 Schottky's is 0.45 V at 1 A) and show the typical curve.

Uses in a synth:

- **Reverse-polarity protection:** a series diode in the supply line blocks current if the supply is connected backwards, at the cost of its forward drop.
- **Clamping:** diodes to the supply rails catch input overvoltage (lesson 4).
- **Flyback:** a diode across a relay or motor coil absorbs the voltage spike when the coil switches off.

## Switches and buttons

Switches are described by their poles and throws: **poles** are the independent circuits switched, and **throws** are the positions each pole can connect to.

- **SPST:** single pole, single throw. A simple on/off.
- **SPDT:** single pole, double throw. A common terminal switches between two others.
- **DPDT:** two SPDT switches moved together.

**Momentary** buttons only connect while pressed. **Latching** switches (toggle switches) stay put. Tactile buttons often have four legs that are internally connected in pairs. Check which pairs with a continuity tester before wiring.

Mechanical contacts **bounce** (contact bounce): for a few milliseconds a press looks like several rapid presses. A microcontroller reading a button also needs a defined idle level from a pull-up or pull-down resistor. Debouncing and pull-ups are covered with the embedded topics.

## Connectors and pinouts

Connectors are where parts are most often wired wrong.

- **Pin headers** are commonly on a 2.54 mm (0.1 in) pitch. Pin 1 is marked by a square pad, a triangle or a dot.
- **Pinout diagrams can be drawn from either side.** "Looking into the socket" and "looking at the solder side" are mirror images. Check which view the diagram shows.
- **Audio jacks:** on a 3.5 mm or 6.35 mm TRS stereo jack, the tip carries left, the ring carries right and the sleeve is ground. On a mono TS jack, the tip carries the signal and the sleeve is ground.
- **Keying:** keyed connectors only fit one way. Unkeyed headers fit both ways, including the wrong one.
- **Product-specific connectors** (power inputs, MIDI DIN, board edge headers) have pinouts defined by the product or standard. Take them from that documentation, never from memory. DIN MIDI isn't a direct GPIO connection; it needs the interface circuit from the MIDI specification, covered in a later module.

> [!warning] Polarity and pinout mistakes destroy parts
> Before power-up, check every polarised part (electrolytics, diodes, LEDs, chips) and every connector orientation against the schematic. It takes a minute and catches the most common fatal mistakes.

## Key takeaways

- Read resistor bands from the bunched end. Brown-red-gold-silver tolerance is 1%, 2%, 5%, 10%. Measure when unsure.
- Choose standard E-series values. Check power (current squared × resistance) and leave margin.
- The RC time constant is resistance × capacitance: 63.2% of the way after one time constant, about 99% after five.
- Electrolytic and tantalum capacitors are polarised. Respect polarity and choose a voltage rating with margin.
- LED resistor: (supply voltage − forward voltage) ÷ wanted current, rounded up to a standard value. Respect pin and LED current limits.
- Diodes conduct anode to cathode (banded end) with a forward drop of roughly 0.6–0.7 V for silicon at small currents, rising towards 1 V at amps.
- Switch types: poles and throws, momentary or latching. Contacts bounce.
- Take pinouts from documentation and note which side the diagram is drawn from.

## Further reading

- [Electronic color code, IEC 60062 (Wikipedia)](https://en.wikipedia.org/wiki/Electronic_color_code)
- [E series of preferred numbers (Wikipedia)](https://en.wikipedia.org/wiki/E_series_of_preferred_numbers)
- [RC time constant (Wikipedia)](https://en.wikipedia.org/wiki/RC_time_constant)
- [Electrolytic capacitor: polarity and failure (Wikipedia)](https://en.wikipedia.org/wiki/Electrolytic_capacitor)
- [Ceramic capacitor, including voltage dependence (Wikipedia)](https://en.wikipedia.org/wiki/Ceramic_capacitor)
- [Diode (Wikipedia)](https://en.wikipedia.org/wiki/Diode)
- [Light-emitting diodes (SparkFun)](https://learn.sparkfun.com/tutorials/light-emitting-diodes-leds/all)
- [Phone connector (audio): TRS wiring (Wikipedia)](https://en.wikipedia.org/wiki/Phone_connector_(audio))
- [Flyback diode (Wikipedia)](https://en.wikipedia.org/wiki/Flyback_diode)
