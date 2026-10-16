---
id: aud-sound-systems-gain-plan
title: Plan gain across the whole system
level: advanced
minutes: 4
summary: Set input gain with representative source peaks and leave headroom.
sourceLesson: aud-sound-systems
---

## Gain staging across the system

Module 1 covered gain staging inside a digital synth. In a system, the same idea applies at every box:

1. **Set the preamp gain first**, with the performer at their loudest. Aim for healthy levels with headroom to spare: on a digital desk, nominal levels around −18 to −20 dBFS leave room for peaks (module 1); on an analogue desk, follow its meter calibration and overload-warning guidance, allowing headroom for unexpectedly loud peaks rather than deliberately clipping. The system's signal-to-noise ratio is largely fixed here: noise added at the mic preamp is amplified by everything after it.
2. **Keep faders near their unity (0 dB) mark** for normal levels, so there's travel in both directions.
3. **Set outboard gear to unity** where possible, passing the full signal without clipping.
4. **Set amplifier input sensitivity** as part of the system’s gain and protection plan. One approach maps the maximum clean system output to the required amplifier output; that output must also respect speaker and audience limits. Amp input controls are attenuators that set sensitivity, not "power" controls.

To work out how much preamp gain a mic needs, start from its sensitivity (its output voltage at a reference sound pressure of 1 pascal, which is 94 dB SPL), add however far the real source is above that reference, convert to dBu, and subtract from the level the console wants. Example: an SM58 (sensitivity −56.0 dBV/Pa) picks up a singer at 104 dB SPL, which is 10 dB above 1 Pa:

```formula
V_v = S + (L_p − 94)
V_v = −56.0 + (104 − 94) = −46.0 dBV
V_u = V_v + 20 log_10(1 / 0.7746)
V_u ≈ −46.0 + 2.2 = −43.8 dBu
G = L_nom − V_u
G = 4 − (−43.8) = 47.8 dB
where
V_v: the mic's output level, in dBV (decibels relative to 1 volt)
S: the mic's sensitivity, in dBV per pascal (dBV/Pa): its output at 94 dB SPL; −56.0 dBV/Pa for an SM58, about 1.6 millivolts
L_p: the sound pressure level at the mic, in dB SPL; here 104 dB SPL
94: the sound pressure level of 1 pascal (Pa), in dB SPL: the reference at which sensitivity is measured
V_u: the same output level expressed in dBu (decibels relative to 0.7746 volts)
log_10: the base-10 logarithm: the power you raise 10 to in order to get the number
0.7746: the voltage used as the dBu reference, 0.7746 volts (V); 20 × log_10(1 / 0.7746) ≈ 2.2 dB is the fixed gap between dBV and dBu
G: the preamp gain needed, in decibels (dB)
L_nom: the console's nominal operating level, here +4 dBu
dB: decibels, a logarithmic ratio; every 20 dB is a factor of 10 in voltage
dBV: decibels relative to 1 volt
dBu: decibels relative to 0.7746 volts
In words: the singer is 10 dB louder than the sensitivity reference, so the mic puts out 10 dB more than its rated sensitivity; the preamp must make up the gap between that and the console's +4 dBu working level.
```

About 48 dB of preamp gain. A condenser about 25 dB more sensitive (the microphone units) would need only around 23 dB.

> [!warning] Two common mistakes
> - Low preamp gain "made up" with faders pushed to the top: the console's noise is amplified as much as the signal.
> - Preamp gain set with the singer warming up quietly: the first chorus clips the input, and no fader can undo clipping that happened upstream.

## Key takeaways
- Set input gain with representative source peaks and leave headroom.
- A fader cannot repair clipping at an earlier stage.
- Coordinate amplifier sensitivity, limiter settings and speaker and audience limits.

## Further reading
- [Setting system level controls — Rane](https://www.ranecommercial.com/legacy/note135.html)
- [Acoustic feedback — Rane](https://www.ranecommercial.com/legacy/note158.html)
- [Keyboard stage connections — Radial](https://www.radialeng.com/blog/how-to-manage-any-keyboard-setup-on-stage)
