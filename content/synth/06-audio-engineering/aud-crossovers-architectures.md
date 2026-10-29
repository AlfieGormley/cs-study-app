---
id: aud-crossovers-architectures
title: Crossover architectures, order and slope
level: advanced
minutes: 4
summary: Passive networks filter speaker-level signals; active filters precede driver amplifiers.
sourceLesson: aud-crossovers
---

A single driver faces substantial trade-offs in covering 20 Hz to 20 kHz at useful levels and with controlled dispersion. A woofer big enough for bass beams and breaks up in the treble (the loudspeaker-driver units); a tweeter small enough to disperse treble widely would be destroyed by bass excursion. So most speakers use two or more drivers, and a **crossover** sends each one only the frequencies it handles well.

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

- **Passive crossovers** are inductors, capacitors and resistors between one power amplifier and the drivers. They carry full speaker-level current, so parts are large and the filter's behaviour depends on the drivers' impedance. Most hi-fi speakers use them.
- **Active crossovers** filter at line level (op-amp circuits), *before* a separate amplifier for each driver. Filter behaviour is predictable, each amp sees one driver, and a clipping woofer amp can't send its distortion to the tweeter.
- **DSP** crossovers are active crossovers done in software, as in most powered studio monitor loudspeakers and PA processors. They add delay, EQ and limiters per driver at little extra cost, and you can even use linear-phase (FIR) filters, with delay and latency determined by the design.

## Order and slope

For the conventional analogue all-pole low-pass and corresponding high-pass families below, order sets the **asymptotic** stopband slope and total phase change. Arbitrary filters with additional zeros, delays or FIR structures need separate analysis:

| Order | Slope | Total phase rotation |
|---|---|---|
| 1st | 6 dB/octave | 90° |
| 2nd | 12 dB/octave | 180° |
| 3rd | 18 dB/octave | 270° |
| 4th | 24 dB/octave | 360° |

The table follows one simple rule: each order (each "pole" of the filter) adds 6 dB/octave of slope and 90° of phase rotation, so you can work out any row from the order alone.

Why 6 dB? Far above its corner, a first-order low-pass halves its output voltage every time the frequency doubles, and halving the voltage is −6 dB (20 dB per *decade*, a tenfold change in frequency, says the same thing). A fourth-order filter approaches another 24 dB of attenuation per octave far into its stopband. Its absolute level one octave from the corner depends on the filter family. These are asymptotes: near the corner the real curve is gentler.

Steeper slopes protect drivers better (a tweeter crossed with 24 dB/octave sees much less energy at its resonance than with 6 dB/octave) and reduce the overlap where both drivers play. The cost: more phase rotation, more complex circuits and, passively, more expensive parts.

## Key takeaways
- Passive networks filter speaker-level signals; active filters precede driver amplifiers.
- For the conventional families discussed, each order contributes roughly six decibels per octave asymptotically.
- Electrical filter response and actual driver response jointly determine the acoustic result.

## Further reading
- [Crossovers — Linkwitz Lab](https://www.linkwitzlab.com/crossovers.htm)
- [Linkwitz–Riley crossover primer — Rane](https://www.ranecommercial.com/legacy/note160.html)
- [Filter circuits — Linkwitz Lab](https://linkwitzlab.com/filters.htm)
