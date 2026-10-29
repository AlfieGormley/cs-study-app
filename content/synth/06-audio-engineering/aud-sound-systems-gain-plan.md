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

> [!analogy] Real-world analogy: photocopying a pencil sketch
> Photocopy a faint pencil sketch, then copy the copy several times, darkening each one to make the lines visible. Every copier adds its own speckle, and darkening a faint copy darkens the speckle just as much. Start with a firm, dark original and the speckle stays insignificant; press so hard that the lines smudge into solid black, though, and no later copy can recover the detail.
>
> **How it maps:** The sketch is the source signal, each copier is a stage in the chain, and the speckle is each stage's noise. Setting a healthy preamp gain is drawing a firm original. Turning a faint signal up later (faders at the top) darkens the speckle too. Smudged solid black is clipping, which no later stage can undo.
>
> **Where it stops:** Digital stages add almost no noise of their own once the signal is converted, and an analogue chain's noise depends on each stage's design. The analogy also hides headroom: a real chain needs space above the normal level for unexpectedly loud peaks.

How much preamp gain does a mic need? Start from its sensitivity (its output at 1 pascal, which is 94 dB SPL), then add one decibel of output for every decibel the real source is above that reference. The preamp makes up the gap to the console's working level. Every decibel louder at the mic means one decibel less preamp gain.

For example, an SM58 (sensitivity −56.0 dBV/Pa) on a singer producing 104 dB SPL, 10 dB above 1 Pa, puts out about −46 dBV, which is about −44 dBu (dBu reads about 2.2 dB higher than dBV for the same voltage). Reaching a +4 dBu working level therefore takes about **48 dB** of preamp gain. A condenser about 25 dB more sensitive (the microphone lessons) would need only around 23 dB.

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
