---
id: midi-audio-levels-sine-headroom
title: Distinguish RMS, peaks and headroom
level: intermediate
minutes: 3
sourceLesson: midi-audio-levels
summary: Use the square-root-of-two factor only for a sine wave and leave room above the nominal operating level.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Sine-wave peaks and operating level

Level figures such as +4 dBu describe an RMS (root mean square) voltage: a kind of effective average. The circuit, though, has to survive the signal's *peaks*. For a pure sine wave the two are linked by a fixed factor:

```formula essential
V_peak = V_rms √2
where
V_peak: the highest voltage the sine wave reaches, measured from 0 V, in volts (V)
V_rms: the RMS (root mean square) voltage, the "effective" value that level figures quote, in volts
√2: the square root of 2, about 1.414
V: volt
In words: a sine wave's peaks are about 1.41 times its RMS value, so +4 dBu (about 1.228 V RMS) swings to about ±1.74 V.
```

The factor of about 1.414 holds only for a pure sine wave. Other waveforms and music can have a different, including higher, ratio of peak to RMS, which is one reason equipment needs headroom.

Two cautions:

- **Nominal is not maximum.** The nominal level is the design's operating level; real signals have peaks well above it, and equipment leaves **headroom** for them. Elektron, for example, specifies the Digitakt II's main outputs and inputs at +18 dBu peak, and the original Digitakt's main outputs at +22 dBu peak. Analogue-to-digital alignment is equipment-dependent; −18 and −20 dBFS are examples used in some systems, not a universal correspondence to a particular dBu voltage.
- **Interfaces differ.** Many line inputs are switchable or have enough gain range to handle both conventions. Read your interface manual for its *maximum* input level (often in dBu) and compare it with your synth's maximum output.

Elektron labels these published maximum ratings “dBu peak”. The standard dBu voltage reference is RMS-based; the manufacturer label is quoted here rather than silently converted into waveform peak volts. Confirm the test/measurement convention and permitted input voltage when comparing equipment.

## Key takeaways
- Nominal level figures such as +4 dBu describe RMS voltages; circuits must also survive the peaks.
- The square-root-of-two factor between peak and RMS holds only for a pure sine wave; music and other waveforms can peak higher.
- Nominal level is an operating point, not a maximum: compare published maximum levels, and their measurement conventions, before connecting.

## Further reading
- [RMS references and the misleading phrase “peak dBu” — Rane](https://www.ranecommercial.com/legacy/pdf/ranenotes/No_Such_Thing_as_Peak_Volts_dBu.pdf)
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
