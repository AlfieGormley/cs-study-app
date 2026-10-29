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

Both describe the same thing. dBV/Pa is a voltage ratio in decibels, so every factor of 10 in mV/Pa is 20 dB, and a less negative dBV/Pa figure means more output.

```formula reference
S_dBV = 20 log_10(S / (1 V/Pa))
where
S_dBV: the sensitivity in decibels relative to 1 volt per pascal (dBV/Pa); negative for typical passive and studio microphones, and less negative means more output
S: the sensitivity as a voltage ratio, in volts per pascal (V/Pa); for example 28 mV/Pa = 0.028 V/Pa
log_10: the base-10 logarithm
V: volt, the unit of voltage
Pa: pascal, the unit of pressure; 1 Pa is about 94 dB SPL
dBV: decibels relative to 1 volt
In words: dBV/Pa expresses a microphone's output per pascal as a voltage ratio against one volt per pascal, so 28 millivolts per pascal is about −31 dBV/Pa and 1.6 millivolts per pascal is about −56 dBV/Pa.
```

| Mic (manufacturer's figures) | mV/Pa | dBV/Pa |
|---|---|---|
| Shure SM58 (dynamic) | 1.6 | −56.0 |
| Neumann U 87 Ai, cardioid | 28 | ≈ −31 |

(The SM58 figures follow Shure’s user guide version 6.4 (2024-F), checked October 2026; the −56.0 dBV/Pa figure corresponds to about 1.585 mV/Pa, rounded to 1.6 mV/Pa. The U 87 Ai figures are Neumann's published technical data. Older specifications quote different values, so confirm the revision for the microphone being used.)

The condenser puts out about 17.5 times the voltage of the dynamic, which is about **25 dB**. So for the same recorded level, the dynamic needs about 25 dB more preamp gain. That gain raises the preamp's own input noise along with the signal, so on a quiet source a low-output microphone can leave audible hiss even though the microphone itself is quiet. For quiet sources, compare microphone sensitivity, its own noise and the preamp’s equivalent input noise together; a low-noise condenser often performs well. On a loud source the difference rarely matters: there is plenty of signal above the preamp's noise.

### Self-noise

A condenser's electronics produce some noise even in a silent room. **Self-noise** (or "equivalent noise level") is quoted as the SPL that would produce the same output, usually A-weighted (dB-A). Neumann specifies the U 87 Ai's self-noise as **12 dB-A** in cardioid. Below about 10 dB-A is very quiet; above about 20 dB-A can become audible on quiet sources.

Passive dynamics and ribbons have no active electronics, but their winding and transformer resistance still generate thermal noise. That noise and the preamp’s input noise both contribute to the recorded noise floor.

### Maximum SPL and dynamic range

Max SPL is the level at which distortion reaches a stated figure (often 0.5% or 1% THD). Neumann gives **117 dB SPL** for the U 87 Ai at 0.5 % THD (127 dB with its pre-attenuation pad).

The **dynamic range** is the gap between the self-noise and the max SPL. Both are already decibel levels on the same SPL scale, so the range is simply their difference: about 117 − 12 = 105 dB for the U 87 Ai in cardioid. Because the self-noise figure is A-weighted, this is an approximate, A-weighted range. The pad raises the top end to 127 dB SPL so that very loud sources do not overload the microphone's electronics.

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
