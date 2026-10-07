---
id: elec-components
title: "Components: resistors, capacitors, LEDs, diodes, switches and connectors"
level: intermediate
minutes: 16
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

Colours are easy to misread under poor light. Brown, red and orange look alike, and so do violet and grey. **Measure with a multimeter before fitting** (out of circuit) whenever you're unsure.

### Preferred values

Resistors come in E-series values. E12 (for ±10%) has 12 values per decade: 10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82. E24 adds more in between. You calculate an ideal value, then choose the nearest standard value in the safe direction.

### Tolerance and power rating

- **Tolerance:** a 10 kΩ ±5% part may be anywhere from 9.5 to 10.5 kΩ. For a divider that sets a precise level, use 1% parts.
- **Power rating:** common small through-hole resistors are rated around 0.25 W. Check the datasheet. Calculate P = I²R and leave margin. Running at half the rating or less is a common conservative practice.

## Capacitors

A capacitor stores charge between two plates separated by an insulator (the dielectric). Capacitance C is measured in farads (F). Practical values run from pF to thousands of µF.

### Behaviour

- It **blocks steady DC** once charged, because no current flows through the insulator.
- It **passes changes**, since current flows while its voltage is changing. This is why it can remove a DC offset from an audio signal or short fast noise to ground.
- Its voltage **can't jump instantly**. It changes at a rate set by the current.

### The RC time constant

Charge a capacitor C through a resistor R from a fixed voltage and it follows an exponential curve. The **time constant** is:

```
τ = R × C      (ohms × farads = seconds)
```

After one τ the capacitor reaches about 63.2% of the applied voltage. After 5τ it's within 1% of it.

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

RC circuits show up across synth hardware. They give a simple low-pass filter (its −3 dB cutoff is f = 1 / (2πRC)). They smooth a noisy knob, and they slow a bouncing switch.

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
- **Ceramic DC bias.** Many high-value ceramics (X7R, X5R and similar Class 2 dielectrics) lose a significant share of their capacitance when a DC voltage is applied, sometimes well over half near the rated voltage. The effect is documented in manufacturers' DC-bias curves. The "X7R" code itself only describes temperature behaviour (±15% from −55 to +125 °C); it says nothing about voltage. C0G/NP0 ceramics are stable but only come in small values.
- **Markings.** Small ceramics often use three digits: `104` = 10 × 10⁴ pF = 100 nF.

## LEDs and the current-limiting resistor

An LED is a diode that emits light. It conducts in one direction only. Above its **forward voltage** V_f the current rises very steeply, so an LED always needs something to limit its current, usually a series resistor.

V_f depends on colour and current. For a typical red indicator LED it's around 1.8–2.2 V at 20 mA, and for blue and white around 3–3.5 V. Datasheet maximums are higher: Kingbright's 5 mm parts, for example, list a red at 1.85 V typical, 2.5 V maximum, and a blue at 3.3 V typical, 4.0 V maximum. Use the figures from your LED's datasheet. Small 3 mm and 5 mm indicator LEDs are usually characterised at 20 mA, with an absolute-maximum continuous current often in the 20–30 mA range. Treat 20 mA as a ceiling, not a target: they're usually bright enough at a few milliamps.

```
R = (V_supply − V_f) / I_LED
```

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

Round **up** to the next standard value. That gives slightly less current, which is the safe direction. Then check the resistor's power, (1.3 V × 4.8 mA ≈ 6 mW), and the source's limits. When a microcontroller pin drives the LED, the pin's maximum output current from the board's datasheet also applies.

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

Switches are described by **poles** (independent circuits switched) and **throws** (positions each pole can connect to):

- **SPST:** single pole, single throw. A simple on/off.
- **SPDT:** single pole, double throw. A common terminal switches between two others.
- **DPDT:** two SPDT switches moved together.

**Momentary** buttons only connect while pressed. **Latching** (toggle) switches stay put. Tactile buttons often have four legs that are internally connected in pairs. Check which pairs with a continuity tester before wiring.

Mechanical contacts **bounce**: for a few milliseconds a press looks like several rapid presses. A microcontroller reading a button also needs a defined idle level from a pull-up or pull-down resistor. Debouncing and pull-ups are covered with the embedded topics.

## Connectors and pinouts

Connectors are where parts are most often wired wrong.

- **Pin headers** are commonly on a 2.54 mm (0.1 in) pitch. Pin 1 is marked by a square pad, a triangle or a dot.
- **Pinout diagrams can be drawn from either side.** "Looking into the socket" and "looking at the solder side" are mirror images. Check which view the diagram shows.
- **Audio jacks:** on a 3.5 mm or 6.35 mm TRS stereo jack, tip = left, ring = right, sleeve = ground. On a mono TS jack, tip = signal and sleeve = ground.
- **Keying:** keyed connectors only fit one way. Unkeyed headers fit both ways, including the wrong one.
- **Product-specific connectors** (power inputs, MIDI DIN, board edge headers) have pinouts defined by the product or standard. Take them from that documentation, never from memory. DIN MIDI isn't a direct GPIO connection; it needs the interface circuit from the MIDI specification, covered in a later module.

> [!warning] Polarity and pinout mistakes destroy parts
> Before power-up, check every polarised part (electrolytics, diodes, LEDs, chips) and every connector orientation against the schematic. It takes a minute and catches the most common fatal mistakes.

## Key takeaways

- Read resistor bands from the bunched end. Brown-red-gold-silver tolerance is 1%, 2%, 5%, 10%. Measure when unsure.
- Choose standard E-series values. Check power with P = I²R and leave margin.
- τ = RC: 63.2% after one τ, about 99% after 5τ.
- Electrolytic and tantalum capacitors are polarised. Respect polarity and choose a voltage rating with margin.
- LED resistor: R = (V_supply − V_f) / I, rounded up. Respect pin and LED current limits.
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
