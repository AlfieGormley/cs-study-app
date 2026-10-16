---
id: aud-microphones-specifications
title: Microphone sensitivity, noise and overload
level: intermediate
minutes: 5
summary: Sensitivity relates output voltage to acoustic pressure, commonly at one kilohertz and one pascal.
sourceLesson: aud-microphones
---

## Reading the specifications

### Sensitivity

The output voltage for a given sound pressure, normally at 1 kHz and **1 Pa (94 dB SPL)**:

- **mV/Pa**: millivolts of output per pascal of sound pressure, or
- **dBV/Pa**: the same figure in decibels relative to 1 volt per pascal.

Converting between the two is a voltage-ratio decibel calculation:

```formula
S_dBV = 20 log_10(S / (1 V/Pa))
S_dBV = 20 log_10((0.028 V/Pa) / (1 V/Pa))
S_dBV ≈ −31.1 dBV/Pa
where
S_dBV: the sensitivity in decibels relative to 1 volt per pascal (dBV/Pa); negative for these two microphones; a less negative value means greater output, and sufficiently sensitive active designs need not be negative
S: the sensitivity as a voltage ratio, in volts per pascal (V/Pa); here 28 mV/Pa = 0.028 V/Pa (a Neumann U 87 Ai)
log_10: the base-10 logarithm
V: volt, the unit of voltage
Pa: pascal, the unit of pressure; 1 Pa is about 94 dB SPL
dBV: decibels relative to 1 volt
≈: approximately equal to (the result is rounded)
In words: sensitivity in dBV/Pa is 20 times the base-10 log of the output voltage per pascal; 28 mV/Pa comes out at about −31 dBV/Pa.
```

| Mic (manufacturer's figures) | mV/Pa | dBV/Pa |
|---|---|---|
| Shure SM58 (dynamic) | 1.6 | −56.0 |
| Neumann U 87 Ai, cardioid | 28 | ≈ −31 |

(The SM58 figures follow Shure’s user guide version 6.4 (2024-F), checked October 2026; the −56.0 dBV/Pa figure corresponds to about 1.585 mV/Pa, rounded to 1.6 mV/Pa. Older specifications quote different values, so confirm the revision for the microphone being used. Supercardioid definitions also vary a little between sources; an omni share of 0.366 is one common choice.)

How much more preamp gain does the less sensitive mic need for the same output? Take the ratio of the two sensitivities and convert it to decibels:

```formula
G = 20 log_10(S_A / S_B)
G = 20 log_10((28 mV/Pa) / (1.6 mV/Pa))
G = 20 log_10(17.5)
G ≈ 24.9 dB
where
G: the extra preamp gain mic B needs to match mic A's output, in decibels (dB)
S_A: the sensitivity of the more sensitive mic (here the U 87 Ai), in millivolts per pascal (mV/Pa)
S_B: the sensitivity of the less sensitive mic (here the SM58), in mV/Pa
log_10: the base-10 logarithm; 20 × log_10 because these are voltage ratios
mV: millivolt, a thousandth of a volt
Pa: pascal, the unit of pressure
dB: decibel
≈: approximately equal to (the result is rounded)
In words: the condenser puts out about 17.5 times the voltage, which is about 24.9 dB, so the dynamic needs about 25 dB more preamp gain.
```

So the dynamic needs about **25 dB** more preamp gain for the same output. Gain raises signal and input noise together. For quiet sources, compare microphone sensitivity, its own noise and the preamp’s equivalent input noise; a low-noise condenser often performs well.

### Self-noise

A condenser's electronics produce some noise even in a silent room. **Self-noise** (or "equivalent noise level") is quoted as the SPL that would produce the same output, usually A-weighted (dB-A). Neumann specifies the U 87 Ai's self-noise as **12 dB-A** in cardioid. Below about 10 dB-A is very quiet; above about 20 dB-A can become audible on quiet sources.

Passive dynamics and ribbons have no active electronics, but their winding and transformer resistance still generate thermal noise. That noise and the preamp’s input noise both contribute to the recorded noise floor.

### Maximum SPL and dynamic range

Max SPL is the level at which distortion reaches a stated figure (often 0.5% or 1% THD). Neumann gives **117 dB SPL** for the U 87 Ai (127 dB with its pre-attenuation pad). The dynamic range is the gap between self-noise and max SPL:

```formula
DR = L_max − L_noise
DR = 117 dB SPL − 12 dB SPL = 105 dB
where
DR: the microphone's dynamic range, in decibels (dB): how far the loudest clean sound is above its own noise
L_max: the maximum SPL, the sound level at which distortion reaches the stated limit, in dB SPL
L_noise: the self-noise expressed as an equivalent sound level, in dB SPL (A-weighted here)
dB: decibel
SPL: sound pressure level, measured relative to 20 µPa
In words: subtract the noise floor from the overload point; both are already in decibels, so subtraction gives the range.
```

Because the self-noise figure is A-weighted, this is an approximate, A-weighted range; with the pad engaged the top end rises to 127 dB SPL.

## Key takeaways
- Sensitivity relates output voltage to acoustic pressure, commonly at one kilohertz and one pascal.
- Compare microphone noise and preamp noise together.
- Dynamic range requires both a noise reference and a stated overload criterion.

## Further reading
- [Microphone technology — DPA](https://www.dpamicrophones.com/mic-university/technology/microphone-technology-the-essentials/)
- [U 87 Ai technical data — Neumann](https://www.neumann.com/en-en/products/microphones/u-87-ai/)
- [Phantom power — Schoeps](https://schoeps.de/en/knowledge/knowledge-base/technical-basics/phantom-power-p48p12.html)
- [Three-to-one rule — DPA](https://www.dpamicrophones.com/dict/3-1-rule/)
- [SM58 manufacturer specifications — Shure](https://pubs.shure.com/view/guide/SM58/en-US.pdf)
