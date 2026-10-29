---
id: aud-crossovers-passive-values
title: Calculate passive values and recognise their limits
level: advanced
minutes: 5
summary: The textbook values assume fixed resistive driver loads.
sourceLesson: aud-crossovers
---

## A first-order passive crossover, worked

The textbook calculation treats each driver as a plain resistor equal to its nominal impedance. An inductor's opposition to alternating current (its **reactance**) rises with frequency, so an inductor in series with the woofer passes bass and increasingly blocks treble. A capacitor's reactance falls with frequency, so a capacitor in series with the tweeter blocks bass. A first-order filter's corner is where the part's reactance equals the driver's resistance:

```formula reference
L = R / (2πf_c)
C = 1 / (2πf_c R)
where
L: the inductance of the series inductor feeding the woofer (low-pass), in henries (H); a few tenths of a millihenry (mH) is typical
C: the capacitance of the series capacitor feeding the tweeter (high-pass), in farads (F); a few microfarads (µF) is typical
R: the driver's impedance treated as a fixed resistance, in ohms (Ω); usually the nominal 4 Ω or 8 Ω
f_c: the crossover (corner) frequency, in hertz (Hz), where the part's reactance equals R
π: pi, about 3.14159
In words: Choose the inductor or capacitor whose reactance equals the driver's resistance at the crossover frequency; a lower-impedance driver needs a smaller inductor but a larger capacitor, and a higher crossover needs smaller parts of both kinds.
```

```diagram
 amp+ --+--L------ woofer ------+
        |                      |
        +--C------ tweeter -----+-- amp-
```

For example, a 3 kHz crossover on 8 Ω drivers works out at about 0.42 mH in series with the woofer and about 6.6 µF in series with the tweeter (rounded to the nearest standard values in practice). Halve the driver impedance to 4 Ω and the inductor halves while the capacitor doubles.

### Why it won't behave as calculated

The calculation assumes a constant 8 Ω resistor. The loudspeaker-driver lessons showed real drivers aren't:

- **The impedance varies with frequency.** If the tweeter can be approximated by a constant 6 Ω resistance throughout this region, the high-pass corner moves to about **4 kHz** (explained below). A single impedance measurement at 3 kHz cannot establish the real corner. The woofer's impedance *rises* through the crossover region because of coil inductance, so its inductor filters less than intended.
- **The tweeter's resonance.** Near its Fs (for a dome tweeter typically somewhere around 0.5–1.5 kHz; check the datasheet) the tweeter's impedance peaks and it can't handle much power. A gentle 6 dB/octave filter still feeds it a lot of energy there.
- **The drivers' own roll-offs add to the filter's.** What matters is the *acoustic* slope: electrical filter × driver response. A woofer that's already falling off adds its own slope and phase.
- **Sensitivity differences.** Tweeters are often more sensitive than woofers, so a resistor network (L-pad) is needed to bring the tweeter down.

The corner moves in inverse proportion to the load's resistance. So the 6.6 µF capacitor chosen for an 8 Ω tweeter puts the corner at about 4 kHz (3 kHz × 8/6) if the tweeter actually looks like 6 Ω across that region. Even that still assumes a constant resistance; a real driver's impedance is complex and changes with frequency, so only the full measured curve gives the true corner.

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
