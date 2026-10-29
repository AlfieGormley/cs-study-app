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
- **Filter cutoff:** similar, and smooth it in a perceptual unit (octaves) rather than hertz so its motion is even in musical terms. Only a constant-rate ramp in octaves gives every octave equal time; an exponential smoother still slows near its target.
- **Pitch:** small smoothing for knob jitter; deliberate glide is a separate musical control.
- **Noisy ADC knobs:** combine smoothing with a small dead-band or hysteresis so a stationary knob doesn't wobble the parameter.

Smoothing in the right domain matters. Gain heard in decibels, and frequency heard in octaves, are perceptually logarithmic. A linear ramp in hertz from 100 Hz to 10 kHz spends most of its time in the top octaves.

For example, a linear-in-hertz sweep from 100 Hz to 10 kHz spends only about 1% of its duration between 100 and 200 Hz, but about half between 5 and 10 kHz. Both intervals are one octave.

A sweep that is linear in octaves instead gives each octave an equal share of the time, rather than allocating most of the duration to the largest hertz spans. JUCE’s `SmoothedValue` offers linear and multiplicative smoothing. The multiplicative form moves in equal ratios and cannot reach zero: use an appropriate finite fade or explicit threshold for silence.

> [!note] Where this fits on hardware
> On a microcontroller, the main loop or a timer reads knobs and MIDI and writes *targets*; the audio callback runs the smoothers per sample. That split keeps slow, irregular work out of the audio path. Embedded lessons later cover how to pass those values safely.

> [!analogy] Real-world analogy: Equal steps on a musical staircase
> Treat each octave as one stair, regardless of which note you started on.
>
> **How it maps:** A ramp in octaves gives equal musical intervals equal time; a ramp in hertz allocates more time to the much wider hertz spans at the top.
>
> **Where it stops:** This is a choice of control mapping, not a claim that perceived loudness or every timbre follows a simple octave scale.

## Key takeaways

- Balance responsiveness against unwanted steps.
- A linear ramp in log frequency gives equal musical intervals equal time.
- Dead-band or hysteresis can complement smoothing for noisy controls.

## Further reading

- [SmoothedValue — JUCE](https://docs.juce.com/master/classSmoothedValue.html)
- [Notes, octaves and frequency — UNSW Acoustics](https://newt.phys.unsw.edu.au/jw/notes.html)
