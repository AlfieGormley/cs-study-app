---
id: syn-envelopes-smoothing-domain
title: Choosing smoothing time and musical units
level: intermediate
minutes: 3
summary: Choosing smoothing time and musical units.
sourceLesson: syn-envelopes
---

### Choosing smoothing times

There's no universal value; listen and measure. Useful starting points:

- **Gain and mix levels:** a few milliseconds to a few tens of milliseconds. Too short and zipper noise returns; too long and the control feels laggy.
- **Filter cutoff:** similar, and smooth it in a perceptual unit (octaves) rather than hertz so sweeps sound even.
- **Pitch:** small smoothing for knob jitter; deliberate glide is a separate musical control.
- **Noisy ADC knobs:** combine smoothing with a small dead-band or hysteresis so a stationary knob doesn't wobble the parameter.

Smoothing in the right domain matters. Gain heard in decibels, and frequency heard in octaves, are perceptually logarithmic. Smoothing a frequency linearly from 100 Hz to 10 kHz spends most of its time in the top octaves:

```formula
O = log_2(f_2 / f_1)
O = log_2(10000 Hz / 100 Hz) ≈ 6.64
r_1 = (200 − 100) / (10000 − 100) ≈ 0.01
where
O: the number of octaves between two frequencies
log_2: the base-2 logarithm: how many doublings get from one number to the other
f_1, f_2: the start and end frequencies, in hertz (Hz)
r_1: the share of a linear-in-hertz sweep's time spent in the first octave, 100 to 200 Hz
Hz: hertz, per second
≈: approximately equal to
In words: the sweep covers about 6.6 octaves, but a straight line in hertz spends only about 1% of its time in the first one and about half in the last.
```

A sweep that is linear in octaves instead gives each octave an equal share of the time, which sounds even. JUCE’s `SmoothedValue` offers linear and multiplicative smoothing. The multiplicative form moves in equal ratios and cannot reach zero: use an appropriate finite fade or explicit threshold for silence.

> [!note] Where this fits on hardware
> On a microcontroller, the main loop or a timer reads knobs and MIDI and writes *targets*; the audio callback runs the smoothers per sample. That split keeps slow, irregular work out of the audio path. Embedded lessons later cover how to pass those values safely.

## Key takeaways

- Balance responsiveness against unwanted steps.
- Log-frequency smoothing gives equal musical intervals equal time.
- Dead-band or hysteresis can complement smoothing for noisy controls.

## Further reading

- [SmoothedValue — JUCE](https://docs.juce.com/master/classSmoothedValue.html)
- [Notes, octaves and frequency — UNSW Acoustics](https://newt.phys.unsw.edu.au/jw/notes.html)
