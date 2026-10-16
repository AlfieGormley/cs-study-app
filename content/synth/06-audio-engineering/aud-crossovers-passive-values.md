---
id: aud-crossovers-passive-values
title: Calculate passive values and recognise their limits
level: advanced
minutes: 5
summary: The textbook values assume fixed resistive driver loads.
sourceLesson: aud-crossovers
---

## A first-order passive crossover, worked

The textbook calculation treats each driver as a plain resistor equal to its nominal impedance. An inductor's opposition to current (its reactance) rises with frequency, and a capacitor's falls. A first-order filter's corner is where the part's reactance equals the driver's resistance, which gives:

```formula
X_L = 2πf L
X_C = 1 / (2πf C)
L = R / (2πf_c)
C = 1 / (2πf_c R)
where
X_L: the inductor's reactance (its opposition to alternating current), in ohms (Ω); it rises with frequency, so a series inductor attenuates treble into a suitable load
X_C: the capacitor's reactance, in ohms (Ω); it falls with frequency, so a series capacitor attenuates bass into a suitable load
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
L = R / (2πf_c)
L = 8 Ω / (2π × 3000 Hz)
L ≈ 0.000424 H = 0.424 mH
C = 1 / (2πf_c R)
C = 1 / (2π × 3000 Hz × 8 Ω)
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

The formula assumes a constant 8 Ω resistor. The loudspeaker-driver units showed real drivers aren't:

- **The impedance varies with frequency.** If the tweeter can be approximated by a constant 6 Ω resistance throughout this region, the high-pass corner moves to about **4 kHz** (calculated below). A single impedance measurement at 3 kHz cannot establish the real corner. The woofer's impedance *rises* through the crossover region because of coil inductance, so its inductor filters less than intended.
- **The tweeter's resonance.** Near its Fs (for a dome tweeter typically somewhere around 0.5–1.5 kHz; check the datasheet) the tweeter's impedance peaks and it can't handle much power. A gentle 6 dB/octave filter still feeds it a lot of energy there.
- **The drivers' own roll-offs add to the filter's.** What matters is the *acoustic* slope: electrical filter × driver response. A woofer that's already falling off adds its own slope and phase.
- **Sensitivity differences.** Tweeters are often more sensitive than woofers, so a resistor network (L-pad) is needed to bring the tweeter down.

Here is the tweeter corner with the 6.63 µF capacitor from the 8 Ω design, when the tweeter is really closer to 6 Ω:

```formula
f_c = 1 / (2πRC)
f_c = 1 / (2π × 6 Ω × 6.63 µF)
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
> Passive crossovers sit after the power amplifier, at speaker-level voltages and currents. High-power speaker outputs can themselves present hazardous voltages and currents. Never open the amplifier; switch it off before changing speaker wiring and follow its discharge and connection instructions (the power-amplifier units).

## Key takeaways
- The textbook values assume fixed resistive driver loads.
- Real impedance, driver roll-off, sensitivity and acoustic-centre offsets change the result.
- Design from measurements and follow the amplifier’s safe connection guidance.

## Further reading
- [Crossovers — Linkwitz Lab](https://www.linkwitzlab.com/crossovers.htm)
- [Linkwitz–Riley crossover primer — Rane](https://www.ranecommercial.com/legacy/note160.html)
- [Filter circuits — Linkwitz Lab](https://linkwitzlab.com/filters.htm)
