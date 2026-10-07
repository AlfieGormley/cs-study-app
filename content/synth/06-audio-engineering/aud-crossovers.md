---
id: aud-crossovers
title: Crossovers
level: advanced
minutes: 18
summary: Why multi-way speakers split the signal, passive vs active vs DSP crossovers, filter order and slope, why Butterworth crossovers bump and Linkwitz–Riley LR4 sums flat, driver offset and phase, and a worked first-order passive crossover with the reasons it doesn't behave as calculated.
---

A single driver faces substantial trade-offs in covering 20 Hz to 20 kHz at useful levels and with controlled dispersion. A woofer big enough for bass beams and breaks up in the treble (lesson 4); a tweeter small enough to disperse treble widely would be destroyed by bass excursion. So most speakers use two or more drivers, and a **crossover** sends each one only the frequencies it handles well.

You already met filters in module 2 (synth filters). Crossovers use the same maths, with one extra demand: the outputs must **add back together** in the air into a smooth response.

## Passive, active and DSP

```diagram
 PASSIVE:
  amp ---> [LC filter] ---> woofer
       \-> [LC filter] ---> tweeter

 ACTIVE / DSP:
  source -> [filter] -> amp -> woofer
         \-> [filter] -> amp -> tweeter
```

- **Passive** crossovers are inductors, capacitors and resistors between one power amplifier and the drivers. They carry full speaker-level current, so parts are large and the filter's behaviour depends on the drivers' impedance. Most hi-fi speakers use them.
- **Active** crossovers filter at line level (op-amp circuits), *before* a separate amplifier for each driver. Filter behaviour is predictable, each amp sees one driver, and a clipping woofer amp can't send its distortion to the tweeter.
- **DSP** crossovers are active crossovers done in software, as in most powered studio monitors and PA processors. They add delay, EQ and limiters per driver at little extra cost, and you can even use linear-phase (FIR) filters, at the cost of latency.

## Order and slope

For the conventional analogue all-pole low-pass and corresponding high-pass families below, order sets the **asymptotic** stopband slope and total phase change. Arbitrary filters with additional zeros, delays or FIR structures need separate analysis:

| Order | Slope | Total phase rotation |
|---|---|---|
| 1st | 6 dB/octave | 90° |
| 2nd | 12 dB/octave | 180° |
| 3rd | 18 dB/octave | 270° |
| 4th | 24 dB/octave | 360° |

Steeper slopes protect drivers better (a tweeter crossed with 24 dB/octave sees much less energy at its resonance than with 6 dB/octave) and reduce the overlap where both drivers play. The cost: more phase rotation, more complex circuits and, passively, more expensive parts.

## Making the outputs add up

The low-pass and high-pass outputs have to sum to a flat response. Magnitude alone isn't enough: at the crossover frequency both drivers contribute, so their **phase** relationship decides whether they add or cancel.

### First order

A first-order low-pass and high-pass at the same frequency, each −3 dB at the crossover, sum *exactly* to the input (1/(1+s) + s/(1+s) = 1). The catch: the two outputs are 90° apart at the crossover, the 6 dB/octave slopes give the drivers a lot of out-of-band signal to handle, and the perfect sum only holds on one axis with ideal drivers.

### Butterworth

A Butterworth filter is maximally flat in its passband and −3 dB at its corner. For a **second-order Butterworth** crossover, the low-pass and high-pass outputs are 180° apart at the crossover, so:

- Wired with the same polarity, they **cancel**: a deep notch at the crossover.
- With one driver's polarity reversed, they sum with a **+3 dB peak** at the crossover (two −3 dB outputs adding in phase).

### Linkwitz–Riley

Siegfried Linkwitz and Russ Riley's fix (1976) was to cascade **two Butterworth filters** of the same order on each side. Each output is then **−6 dB** at the crossover, half the voltage, and the two halves add to exactly 0 dB.

- **LR2** (two first-order sections): 12 dB/octave, outputs 180° apart, so one driver is reversed in polarity. Sums flat.
- **LR4** (two second-order Butterworths): 24 dB/octave. At the crossover the low-pass is at −180° and the high-pass at +180°, which is a **360° difference: the outputs are in phase at every frequency**. They sum to a flat magnitude, and the total behaves as an **all-pass** filter: flat amplitude with smoothly changing phase.

Why LR4 sums flat, in one line: with D = s² + √2·s + 1 (a second-order Butterworth denominator), LP = 1/D² and HP = s⁴/D², so on the frequency axis |1 + s⁴| equals |D²| = 1 + ω⁴ (in normalised frequency). The sum's magnitude is exactly 1.

```
           at fc     sum at fc
BW2 (inv)  -3 dB     +3 dB peak
LR2 (inv)  -6 dB      0 dB
LR4        -6 dB      0 dB, in phase
```

LR4 is a very common choice in active and DSP crossovers, including PA processors.

## Driver offset and phase

All the sums above assume both drivers' sound starts from the same point. Real drivers don't: a woofer's **acoustic centre** usually sits further back than a tweeter's on a flat baffle. A path difference becomes a time delay, and a time delay becomes a frequency-dependent phase shift that ruins the neat summation.

```python
import cmath, math

def lr4(f, fc):
    s = 1j * f / fc
    d = s * s + math.sqrt(2) * s + 1
    return 1 / d**2, s**4 / d**2

def summed_db(f, fc, lag=0.0):
    lp, hp = lr4(f, fc)
    # woofer (low-pass) arrives late
    lp *= cmath.exp(-2j * math.pi * f * lag)
    db = 20 * math.log10(abs(lp + hp))
    return round(db, 1) + 0.0

fc = 2000
print("  f     0cm   2cm   8cm")
for f in (500, 1000, 1500, 2000,
          2500, 4000):
    row = [summed_db(f, fc, cm / 100 / 343)
           for cm in (0, 2, 8)]
    print(f"{f:>5}" + "".join(
        f"{v:6.1f}" for v in row))
```

```
  f     0cm   2cm   8cm
  500   0.0   0.0   0.0
 1000   0.0   0.0  -0.5
 1500   0.0  -0.2  -3.8
 2000   0.0  -0.6 -19.6
 2500   0.0  -0.8  -6.4
 4000   0.0  -0.5   0.0
```

With the woofer 2 cm behind (58 µs), the dip is under 1 dB. At 8 cm (233 µs, almost half a period at 2 kHz) there's a deep on-axis hole at the crossover. Remedies:

- **DSP delay** on the earlier driver (easy in active/DSP systems).
- **Stepped or sloped baffles** to line up acoustic centres physically.
- Choosing the crossover frequency and filter shapes so the *acoustic* responses (filter × driver) hit the target, and checking the result by measurement.

Even when on-axis is perfect, moving up or down changes the path lengths to the two drivers. That's **lobing**: the summed response changes with vertical angle. LR crossovers with aligned drivers keep the main lobe pointing straight ahead, which is one reason they're popular.

## A first-order passive crossover, worked

The textbook calculation treats each driver as a resistor equal to its nominal impedance, R:

```
low-pass, series inductor:
  L = R / (2*pi*f)
high-pass, series capacitor:
  C = 1 / (2*pi*f*R)
```

```diagram
 amp+ --+--L------ woofer ------+
        |                      |
        +--C------ tweeter -----+-- amp-
```

Worked example: crossover at 3 kHz, 8 Ω drivers.

```python
import math

f, r = 3000, 8.0
L = r / (2 * math.pi * f)
C = 1 / (2 * math.pi * f * r)
print(f"L = {L * 1e3:.3f} mH")
print(f"C = {C * 1e6:.2f} uF")

# if the tweeter is really 6 ohm here:
print(round(1 / (2 * math.pi * 6 * C)))
```

```
L = 0.424 mH
C = 6.63 uF
4000
```

So a 0.42 mH inductor in series with the woofer and a 6.6 µF capacitor in series with the tweeter (nearest standard values in practice).

### Why it won't behave as calculated

The formula assumes a constant 8 Ω resistor. Lesson 4 showed real drivers aren't:

- **The impedance varies with frequency.** If the tweeter can be approximated by a constant 6 Ω resistance throughout this region, the high-pass corner moves to about **4 kHz** (the last line above). A single impedance measurement at 3 kHz cannot establish the real corner. The woofer's impedance *rises* through the crossover region because of coil inductance, so its inductor filters less than intended.
- **The tweeter's resonance.** Near its Fs (for a dome tweeter typically somewhere around 0.5–1.5 kHz; check the datasheet) the tweeter's impedance peaks and it can't handle much power. A gentle 6 dB/octave filter still feeds it a lot of energy there.
- **The drivers' own roll-offs add to the filter's.** What matters is the *acoustic* slope: electrical filter × driver response. A woofer that's already falling off adds its own slope and phase.
- **Sensitivity differences.** Tweeters are often more sensitive than woofers, so a resistor network (L-pad) is needed to bring the tweeter down.

Designers fix some of this with impedance-compensation networks (a **Zobel** network across the woofer flattens the rising impedance) and by designing from *measured* driver impedance and frequency response in simulation software, then measuring the built speaker. For a DIY project, using published, tested crossover designs, or a DSP crossover where everything can be measured and adjusted, is far more forgiving than calculating a passive one from nominal values.

> [!note] Passive crossover safety
> Passive crossovers sit after the power amplifier, at speaker-level voltages and currents. High-power speaker outputs can themselves present hazardous voltages and currents. Never open the amplifier; switch it off before changing speaker wiring and follow its discharge and connection instructions (lesson 7).

## Key takeaways
- Crossovers split the band so each driver plays where it works well; passive ones sit after the amp, active and DSP ones before separate amps.
- For the conventional filter families shown, each order adds about 6 dB/octave of asymptotic roll-off and 90° total phase change.
- Second-order Butterworth crossovers are −3 dB each at fc and sum to a +3 dB bump (with one driver inverted) or a notch.
- Linkwitz–Riley filters are cascaded Butterworths, −6 dB at fc; LR4's outputs are in phase at all frequencies and sum flat (an all-pass).
- Acoustic centre offsets turn into phase errors near the crossover: fix with delay or physical alignment, and measure.
- First-order passive values come from L = R/(2πf) and C = 1/(2πfR), but real driver impedance shifts the corners, so design from measurements.

## Further reading
- [Linkwitz–Riley crossovers: a primer (RaneNote 160) — Rane](https://www.ranecommercial.com/legacy/note160.html)
- [Crossovers — Linkwitz Lab](https://www.linkwitzlab.com/crossovers.htm)
- [Linkwitz–Riley filter — Wikipedia](https://en.wikipedia.org/wiki/Linkwitz%E2%80%93Riley_filter)
- [Audio crossover — Wikipedia](https://en.wikipedia.org/wiki/Audio_crossover)
- [Butterworth filter — Wikipedia](https://en.wikipedia.org/wiki/Butterworth_filter)
- [Zobel network — Wikipedia](https://en.wikipedia.org/wiki/Zobel_network)
