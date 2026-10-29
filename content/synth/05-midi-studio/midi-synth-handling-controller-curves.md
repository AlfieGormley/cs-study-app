---
id: midi-synth-handling-controller-curves
title: Map controller steps onto useful ranges
level: intermediate
minutes: 4
sourceLesson: midi-synth-handling
summary: Choose a curve for the parameter; exponential frequency mapping spreads ratios evenly but does not add MIDI resolution.
---

## Mapping CC values to parameters

A CC gives you 0–127. Your synth parameter has a real range and a natural scale, so the first design decision is the curve that connects them. (The next unit covers adding resolution and smoothing.)

## Frequencies and times: use an exponential curve

People hear pitch by *ratio*: going from 100 Hz to 200 Hz sounds like the same step as 1 kHz to 2 kHz. A filter cutoff is also a frequency, and synth designers usually treat cutoffs and envelope times the same way, because equal ratios tend to feel like roughly equal changes there too. That is a widely used design rule of thumb rather than an exact perceptual law. So for these parameters each knob step should *multiply* the value by a fixed ratio rather than add a fixed number of hertz (or milliseconds). Then equal knob movements give equal musical intervals.

```formula reference
f = f_lo (f_hi / f_lo)^{v / 127}
where
f: the parameter value the knob position maps to, here a filter cutoff in hertz (Hz)
f_lo: the value at CC 0, the bottom of the range, in hertz; must be above zero
f_hi: the value at CC 127, the top of the range, in hertz
v: the received CC value, 0 to 127
127: the largest CC value, so v / 127 runs from 0 to 1
Hz: hertz, cycles per second
x^{…}: raising to the power in braces
In words: the knob position chooses how far along the ratio from the bottom to the top of the range you are, so equal knob steps give equal frequency ratios.
```

Compare the two curves over a 20 Hz to 20 kHz cutoff range:

| CC | Exponential | Linear |
|---|---|---|
| 0 | 20 Hz | 20 Hz |
| 1 | about 21 Hz | about 177 Hz |
| 32 | about 114 Hz | about 5.05 kHz |
| 64 | about 650 Hz | about 10.1 kHz |
| 96 | about 3.7 kHz | about 15.1 kHz |
| 127 | 20 kHz | 20 kHz |

The linear map adds about 157 Hz per step. Its very first step jumps from 20 Hz to about 177 Hz, more than three octaves, and half the knob is spent above 10 kHz, where turning it changes little that you can hear. The exponential map shares the range's roughly 10 octaves evenly: just under a semitone per step, with the midpoint near the *geometric* middle (about 650 Hz).

Two limits to keep in mind. An exponential map can never reach 0 Hz, so its bottom value must be above zero. And it rearranges the 128 steps; it does not add resolution, so each step is still an audible jump that the next unit smooths.

> [!analogy] Real-world analogy: a piano keyboard
> On a piano, moving up one key, white or black, always raises the pitch by the same musical step, a semitone, not by the same number of hertz. The top octave spans thousands of hertz; the bottom octave spans a few tens.
>
> **How it maps:** the CC value is the key position, and an exponential cutoff map lays its 128 steps out like piano keys: each step up is the same frequency *ratio*. A linear map is like a keyboard whose keys add 157 Hz each, so the bass is skipped in a few keys and most keys play near-identical treble.
>
> **Where it stops:** a piano's steps are fixed semitones, while a cutoff map's step size depends on the chosen range (just under a semitone for 20 Hz to 20 kHz). And a filter cutoff is not a pitch you play; the analogy only explains why ratio spacing feels even.

## Other parameter types

The exponential argument applies only where perception is roughly on a ratio scale, as it is for pitch and, approximately, for cutoff and time settings. A linear mapping can suit a control *position*. A pan control's audible gain law is a separate design choice, so equal position steps need not mean linear channel gains.

A decibel-style curve can be useful for **mix levels**; choose its range and mute behaviour explicitly. For MIDI controllers defined as **switches**, use the documented convention: values up to 63 are off, and values from 64 are on.

## Key takeaways
- Choose a curve that matches how the parameter is perceived; frequencies and times usually suit an exponential map.
- An exponential map gives equal ratios per step (just under a semitone each for 20 Hz to 20 kHz); a linear map wastes most of the knob in the treble.
- Curves redistribute the 128 steps but do not add resolution; switches use 0–63 off and 64–127 on.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1, including the running status appendix (CCRMA copy)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Polyphony and monophony in instruments: note priority — Wikipedia](https://en.wikipedia.org/wiki/Polyphony_and_monophony_in_instruments)
- [MIDI library for Teensy (serial MIDI) — PJRC](https://www.pjrc.com/teensy/td_libs_MIDI.html)
