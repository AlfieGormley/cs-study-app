---
id: midi-audio-levels-voltage-references
title: Compare dBu and dBV line levels
level: intermediate
minutes: 3
sourceLesson: midi-audio-levels
summary: dBu and dBV use different reference voltages, so convert to a common reference before comparing line levels.
---

## Decibels with a reference: dBV and dBu

A decibel figure on its own is a *ratio*. To describe an absolute voltage it needs a reference, shown by the letter after "dB":

- **dBV**: relative to **1 V RMS**.
- **dBu**: relative to **0.7746 V RMS**. That odd number is a holdover from 600 Ω telephone practice: it is the voltage that delivers 1 milliwatt into 600 Ω. Today the 600 Ω load is history, and 0 dBu simply means 0.7746 V RMS, whatever the actual load.

The two nominal line levels use different references:

- **Professional: +4 dBu**, about **1.228 V RMS**.
- **Consumer: −10 dBV**, about **0.316 V RMS**.

Converting a level back to volts undoes the decibel scale, on which every 20 dB multiplies the voltage by 10 (and about 6 dB doubles it):

```formula reference
V_L = V_ref 10^{L / 20}
where
V_L: the RMS voltage the level L describes, in volts (V)
V_ref: the level reference voltage: 0.7746 V for dBu, 1 V for dBV
L: the level in decibels relative to that reference (dBu or dBV)
10^{…}: 10 raised to the power in braces; it undoes a base-10 logarithm
V: volt, the unit of voltage
In words: start from the reference voltage and multiply by 10 for every 20 dB above it (or divide for every 20 dB below); +4 dBu works out at about 1.228 V RMS.
```

## The subtraction trap

How far apart are the two line levels? It is tempting to say 4 − (−10) = 14 dB, but the numbers are measured from different starting points, so they cannot be subtracted directly.

Put both on the same reference first. 1 V is about 2.2 dB above 0.7746 V, so −10 dBV is about −7.8 dBu. Now the subtraction is fair: +4 dBu is about **11.8 dB** above consumer level, a voltage ratio of nearly four. Converting both levels to volts first and comparing them gives the same answer.

The general rule: before adding, subtracting or comparing decibel figures, check that they share a reference. A level that says only "dB" is a gain or a difference, not an absolute voltage.

These are RMS voltages. For a pure sine wave the peak is about 1.414 times the RMS value, so +4 dBu swings to about ±1.74 V. The next unit explains why that factor does not hold for an arbitrary waveform.

## Key takeaways
- dBu is relative to 0.7746 V RMS and dBV to 1 V RMS; the suffix tells you the reference.
- Professional +4 dBu is about 1.228 V RMS and consumer −10 dBV about 0.316 V RMS.
- Convert to a common reference before comparing: the gap is about 11.8 dB, not 14 dB.

## Further reading
- [Signal processing fundamentals and level references — Rane](https://www.ranecommercial.com/legacy/pdf/ranenotes/Signal_Processing_Fundamentals.pdf)
- [Line level — Wikipedia](https://en.wikipedia.org/wiki/Line_level)
- [Nominal level — Wikipedia](https://en.wikipedia.org/wiki/Nominal_level)
- [Impedance bridging — Wikipedia](https://en.wikipedia.org/wiki/Impedance_bridging)
- [Balanced audio — Wikipedia](https://en.wikipedia.org/wiki/Balanced_audio)
- [Capacitive coupling (coupling capacitors and their high-pass effect) — Wikipedia](https://en.wikipedia.org/wiki/Capacitive_coupling)
- [Phantom power — Wikipedia](https://en.wikipedia.org/wiki/Phantom_power)
- [Single-supply biasing (op amps biased at half supply, coupling capacitors) — LibreTexts, from J. Fiore's op amp textbook](https://eng.libretexts.org/Workbench/Introduction_to_Circuit_Analysis/05%3A_Advanced_Topic-_Operational_Amplifiers/5.10%3A_Basic_Op_Amp_Circuits/5.10.03%3A_Single_Supply_Biasing)
- [Single-Supply Op Amp Design Techniques (SLOA030) — Texas Instruments](https://www.ti.com/lit/an/sloa030a/sloa030a.pdf)
- [PCM5102A data sheet (ground-centred 2.1 V RMS output) — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm5102a.pdf)
- [Digitakt II user manual, technical information — Elektron](https://www.elektron.se/wp-content/uploads/2026/10/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf)
