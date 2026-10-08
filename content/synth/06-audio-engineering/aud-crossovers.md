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

The table follows one simple rule. Each order (each "pole" of the filter) adds 6 dB/octave of slope and 90° of phase rotation, so you can work out any row from the order alone:

```formula
slope = n × 6 dB/octave
φ_total = n × 90°
slope = 4 × 6 dB/octave = 24 dB/octave
φ_total = 4 × 90° = 360°
where
slope: how fast the output falls in the stopband, far from the corner, in decibels per octave
n: the filter order (1, 2, 3, 4 ...); higher means steeper and more complex
dB: decibel, a logarithmic measure of level ratio; −6 dB is about half the voltage
octave: a doubling (or halving) of frequency, for example 1 kHz to 2 kHz
φ_total: phi, the total phase rotation the filter adds across the whole band, in degrees (°)
In words: every extra order makes the filter fall another 6 dB per octave, and twists the phase another quarter turn.
```

Why 6 dB? Far above its corner, a first-order low-pass halves its output voltage every time the frequency doubles, and halving the voltage is −6 dB (20 dB per *decade*, a tenfold change in frequency, says the same thing). A 4th-order filter at 24 dB/octave is down about 24 dB one octave into its stopband, and 48 dB two octaves in. These are asymptotes: near the corner the real curve is gentler.

Steeper slopes protect drivers better (a tweeter crossed with 24 dB/octave sees much less energy at its resonance than with 6 dB/octave) and reduce the overlap where both drivers play. The cost: more phase rotation, more complex circuits and, passively, more expensive parts.

## Making the outputs add up

The low-pass and high-pass outputs have to sum to a flat response. Magnitude alone isn't enough: at the crossover frequency both drivers contribute, so their **phase** relationship decides whether they add or cancel.

Crossover levels are quoted in decibels, which come from the voltage (amplitude) ratio. These are the numbers you'll meet below:

```formula
L = 20 × log_10(A)
20 × log_10(0.707) ≈ −3 dB
20 × log_10(0.5) ≈ −6 dB
20 × log_10(1) = 0 dB
20 × log_10(1.414) ≈ +3 dB
where
L: the level change, in decibels (dB); negative means quieter
A: the amplitude ratio, output voltage divided by input voltage (no unit); 1 means unchanged, 0.5 means half
log_10: the base-10 logarithm, which asks "10 to what power gives this number?"
≈: approximately equal to (rounded)
dB: decibel, the unit of level ratio
In words: half the voltage is −6 dB, about 71 % of it (1/√2) is −3 dB, and 1.414 times (√2) is +3 dB.
```

### First order

A first-order low-pass and high-pass at the same frequency are each −3 dB at the crossover, and they sum *exactly* to the input. Filter designers write a filter as a fraction of the input using the variable *s*:

```formula
LP = 1 / (1 + s)
HP = s / (1 + s)
LP + HP = (1 + s) / (1 + s) = 1
where
LP: the low-pass output as a fraction of the input (its transfer function); no unit
HP: the high-pass output as a fraction of the input; no unit
s: the normalised complex frequency (the Laplace variable). For a steady sine wave it equals j times the frequency divided by the crossover frequency, where j is the imaginary unit (the square root of −1) that tracks phase. At the crossover, s = j
In words: the low-pass and high-pass pieces share the same bottom line, so their tops add up to that bottom line and the sum is exactly the input, at every frequency.
```

At the crossover, each output's size is about 0.707 of the input (−3 dB), but the two are 90° apart in phase, which is why two 0.707s can still add up to exactly 1. The catch: the two outputs are 90° apart at the crossover, the 6 dB/octave slopes give the drivers a lot of out-of-band signal to handle, and the perfect sum only holds on one axis with ideal drivers.

### Butterworth

A Butterworth filter is maximally flat in its passband and −3 dB at its corner. For a **second-order Butterworth** crossover, the low-pass and high-pass outputs are 180° apart at the crossover, so:

- Wired with the same polarity, they **cancel**: a deep notch at the crossover.
- With one driver's polarity reversed, they sum with a **+3 dB peak** at the crossover (two −3 dB outputs adding in phase).

```formula
A_sum = A_LP + A_HP
A_sum = 0.707 + 0.707 = 1.414
L_sum = 20 × log_10(1.414) ≈ +3 dB
where
A_sum: the size of the summed output at the crossover, as a fraction of the input (no unit)
A_LP: the low-pass output's size at the crossover; 0.707 (−3 dB) for a Butterworth
A_HP: the high-pass output's size at the crossover; also 0.707
L_sum: the summed level, in decibels (dB)
log_10: the base-10 logarithm
≈: approximately equal to
dB: decibel, the unit of level ratio
In words: two outputs that are each 71 % of the input, added in step, give 141 % of the input: a 3 dB bump.
```

This simple addition only works because, with one polarity flipped, the two outputs are exactly in step at the crossover.

### Linkwitz–Riley

Siegfried Linkwitz and Russ Riley's fix (1976) was to cascade **two Butterworth filters** of the same order on each side. Each output is then **−6 dB** at the crossover, half the voltage, and the two halves add to exactly 0 dB:

```formula
A_LR = A_BW × A_BW
A_LR = 0.707 × 0.707 = 0.5
A_sum = 0.5 + 0.5 = 1
L_sum = 20 × log_10(1) = 0 dB
where
A_LR: the size of one Linkwitz–Riley output at the crossover, as a fraction of the input (no unit)
A_BW: the size of one Butterworth section's output at the crossover: 0.707 (−3 dB)
A_sum: the size of the summed output (in-phase outputs), as a fraction of the input
L_sum: the summed level, in decibels (dB)
log_10: the base-10 logarithm
dB: decibel, the unit of level ratio
In words: putting two −3 dB filters in a row gives −6 dB (half the voltage), and two halves added in step make exactly the original level.
```

- **LR2** (two first-order sections): 12 dB/octave, outputs 180° apart, so one driver is reversed in polarity. Sums flat.
- **LR4** (two second-order Butterworths): 24 dB/octave. At the crossover the low-pass is at −180° and the high-pass at +180°, which is a **360° difference: the outputs are in phase at every frequency**. They sum to a flat magnitude, and the total behaves as an **all-pass** filter: flat amplitude with smoothly changing phase.

Why does LR4 sum flat at *every* frequency, not just at the crossover? Write each output as a transfer function, using the same normalised frequency variable as the first-order example, and compare the sizes of the top and bottom of the sum:

```formula
D = s^2 + √2 × s + 1
LP = 1 / D^2
HP = s^4 / D^2
LP + HP = (1 + s^4) / D^2
s = j × ω
|1 + s^4| = 1 + ω^4
|D|^2 = (1 − ω^2)^2 + 2 × ω^2
|D|^2 = 1 + ω^4
|LP + HP| = (1 + ω^4) / (1 + ω^4) = 1
where
D: the denominator (bottom line) of a second-order Butterworth filter; no unit
s: the normalised complex frequency (the Laplace variable); for a steady sine it equals j × ω
LP: the LR4 low-pass output as a fraction of the input (two Butterworth low-passes in a row, so D is squared)
HP: the LR4 high-pass output as a fraction of the input
j: the imaginary unit, the square root of −1; it keeps track of phase. j^4 = 1, so s^4 = ω^4
ω: omega, the normalised frequency: the actual frequency divided by the crossover frequency (no unit); ω = 1 at the crossover
√: square root
| |: the magnitude (size) of a complex number, ignoring its phase
In words: the top and the bottom of the summed transfer function always have the same size, so the sum's size is exactly 1 (0 dB) at every frequency; only its phase changes.
```

The top and bottom are not the same polynomial (D² has odd powers of *s* that 1 + s⁴ lacks), so the sum's phase still rotates. That's exactly what an all-pass filter is.

| Crossover | Each output at crossover | Sum at crossover |
|---|---|---|
| BW2, one driver inverted | −3 dB | +3 dB peak |
| LR2, one driver inverted | −6 dB | 0 dB |
| LR4 | −6 dB | 0 dB, in phase |

LR4 is a very common choice in active and DSP crossovers, including PA processors.

## Driver offset and phase

All the sums above assume both drivers' sound starts from the same point. Real drivers don't: a woofer's **acoustic centre** usually sits further back than a tweeter's on a flat baffle. A path difference becomes a time delay, and a time delay becomes a frequency-dependent phase shift that ruins the neat summation:

```formula
t = d / c
φ = 360° × f × t
t = 0.02 m / (343 m/s) ≈ 58 µs
t = 0.08 m / (343 m/s) ≈ 233 µs
φ = 360° × 2000 Hz × 233 µs ≈ 168°
where
t: the time delay between the two drivers' sound, in seconds (s) or microseconds (µs, millionths of a second)
d: the path difference: how much further one acoustic centre is from the listener, in metres (m)
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
φ: phi, the phase error the delay causes, in degrees (°); 360° is one whole cycle
f: the frequency in question, here the 2 kHz crossover, in hertz (Hz)
m: metres
s: seconds
µs: microseconds
Hz: hertz, cycles per second
≈: approximately equal to
In words: sound covers about 3.4 mm every 10 µs, and a fixed delay is a bigger slice of a cycle at higher frequencies; 233 µs is almost half a 2 kHz cycle (500 µs).
```

The script below adds that delay to the woofer of an ideal 2 kHz LR4 crossover and prints the on-axis sum in dB.

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

The textbook calculation treats each driver as a plain resistor equal to its nominal impedance. An inductor's opposition to current (its reactance) rises with frequency, and a capacitor's falls. A first-order filter's corner is where the part's reactance equals the driver's resistance, which gives:

```formula
X_L = 2 × π × f × L
X_C = 1 / (2 × π × f × C)
L = R / (2 × π × f_c)
C = 1 / (2 × π × f_c × R)
where
X_L: the inductor's reactance (its opposition to alternating current), in ohms (Ω); it rises with frequency, so the inductor blocks treble
X_C: the capacitor's reactance, in ohms (Ω); it falls with frequency, so the capacitor blocks bass
f: any frequency, in hertz (Hz)
L: the inductance of the series inductor feeding the woofer (low-pass), in henries (H); a few tenths of a millihenry (mH) is typical
C: the capacitance of the series capacitor feeding the tweeter (high-pass), in farads (F); a few microfarads (µF) is typical
R: the driver's impedance treated as a fixed resistance, in ohms (Ω); usually the nominal 4 Ω or 8 Ω
f_c: the crossover (corner) frequency, in hertz (Hz), where X_L or X_C equals R
π: pi, about 3.14159
In words: set the inductor's or capacitor's reactance equal to the driver's resistance at the crossover frequency and solve; a higher crossover or a lower driver impedance needs a smaller inductor, while a higher crossover or higher impedance needs a smaller capacitor.
```

```diagram
 amp+ --+--L------ woofer ------+
        |                      |
        +--C------ tweeter -----+-- amp-
```

Worked example: crossover at 3 kHz, 8 Ω drivers.

```formula
L = R / (2 × π × f_c)
L = 8 Ω / (2 × π × 3000 Hz)
L ≈ 0.000424 H = 0.424 mH
C = 1 / (2 × π × f_c × R)
C = 1 / (2 × π × 3000 Hz × 8 Ω)
C ≈ 0.00000663 F = 6.63 µF
where
L: the woofer's series inductor, in henries (H)
C: the tweeter's series capacitor, in farads (F)
R: the driver impedance, taken as a fixed 8 ohms (Ω)
f_c: the crossover frequency, 3000 hertz (Hz)
π: pi, about 3.14159
≈: approximately equal to
H: henry, the unit of inductance
mH: millihenry, a thousandth of a henry
F: farad, the unit of capacitance
µF: microfarad, a millionth of a farad
Hz: hertz, cycles per second
Ω: ohm, the unit of resistance and impedance
In words: for a 3 kHz crossover on 8 Ω drivers, the woofer needs about 0.42 mH in series and the tweeter about 6.6 µF.
```

So a 0.42 mH inductor in series with the woofer and a 6.6 µF capacitor in series with the tweeter (nearest standard values in practice).

### Why it won't behave as calculated

The formula assumes a constant 8 Ω resistor. Lesson 4 showed real drivers aren't:

- **The impedance varies with frequency.** If the tweeter can be approximated by a constant 6 Ω resistance throughout this region, the high-pass corner moves to about **4 kHz** (calculated below). A single impedance measurement at 3 kHz cannot establish the real corner. The woofer's impedance *rises* through the crossover region because of coil inductance, so its inductor filters less than intended.
- **The tweeter's resonance.** Near its Fs (for a dome tweeter typically somewhere around 0.5–1.5 kHz; check the datasheet) the tweeter's impedance peaks and it can't handle much power. A gentle 6 dB/octave filter still feeds it a lot of energy there.
- **The drivers' own roll-offs add to the filter's.** What matters is the *acoustic* slope: electrical filter × driver response. A woofer that's already falling off adds its own slope and phase.
- **Sensitivity differences.** Tweeters are often more sensitive than woofers, so a resistor network (L-pad) is needed to bring the tweeter down.

Here is the tweeter corner with the 6.63 µF capacitor from the 8 Ω design, when the tweeter is really closer to 6 Ω:

```formula
f_c = 1 / (2 × π × R × C)
f_c = 1 / (2 × π × 6 Ω × 6.63 µF)
f_c ≈ 4000 Hz = 4 kHz
where
f_c: the high-pass corner frequency, in hertz (Hz) and kilohertz (kHz, thousands of hertz)
R: the tweeter's actual resistance in this region, 6 ohms (Ω)
C: the series capacitor, 6.63 microfarads (µF), i.e. 0.00000663 farads (F)
π: pi, about 3.14159
≈: approximately equal to
Ω: ohms, the unit of resistance
µF: microfarads, millionths of a farad
Hz: hertz, cycles per second
kHz: kilohertz, thousands of hertz
In words: the corner frequency scales inversely with resistance, so 6 Ω instead of 8 Ω pushes the 3 kHz corner up by 8/6 to about 4 kHz.
```

This still assumes a constant resistance; a real driver's impedance is complex and changes with frequency, so only the full measured curve gives the true corner.

Designers fix some of this with impedance-compensation networks (a **Zobel** network across the woofer flattens the rising impedance) and by designing from *measured* driver impedance and frequency response in simulation software, then measuring the built speaker. For a DIY project, using published, tested crossover designs, or a DSP crossover where everything can be measured and adjusted, is far more forgiving than calculating a passive one from nominal values.

> [!note] Passive crossover safety
> Passive crossovers sit after the power amplifier, at speaker-level voltages and currents. High-power speaker outputs can themselves present hazardous voltages and currents. Never open the amplifier; switch it off before changing speaker wiring and follow its discharge and connection instructions (lesson 7).

## Key takeaways
- Crossovers split the band so each driver plays where it works well; passive ones sit after the amp, active and DSP ones before separate amps.
- For the conventional filter families shown, each order adds about 6 dB/octave of asymptotic roll-off and 90° total phase change.
- Second-order Butterworth crossovers are −3 dB each at the crossover frequency and sum to a +3 dB bump (with one driver inverted) or a notch.
- Linkwitz–Riley filters are cascaded Butterworths, −6 dB at the crossover frequency; LR4's outputs are in phase at all frequencies and sum flat (an all-pass).
- Acoustic centre offsets turn into phase errors near the crossover: fix with delay or physical alignment, and measure.
- First-order passive values come from setting each part's reactance equal to the driver's nominal impedance at the crossover frequency, but real driver impedance shifts the corners, so design from measurements.

## Further reading
- [Linkwitz–Riley crossovers: a primer (RaneNote 160) — Rane](https://www.ranecommercial.com/legacy/note160.html)
- [Crossovers — Linkwitz Lab](https://www.linkwitzlab.com/crossovers.htm)
- [Linkwitz–Riley filter — Wikipedia](https://en.wikipedia.org/wiki/Linkwitz%E2%80%93Riley_filter)
- [Audio crossover — Wikipedia](https://en.wikipedia.org/wiki/Audio_crossover)
- [Butterworth filter — Wikipedia](https://en.wikipedia.org/wiki/Butterworth_filter)
- [Zobel network — Wikipedia](https://en.wikipedia.org/wiki/Zobel_network)
