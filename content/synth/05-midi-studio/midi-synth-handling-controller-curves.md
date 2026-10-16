---
id: midi-synth-handling-controller-curves
title: Map controller steps onto useful ranges
level: intermediate
minutes: 5
sourceLesson: midi-synth-handling
summary: Choose a curve for the parameter; exponential frequency mapping spreads ratios evenly but does not add MIDI resolution.
---

## Mapping CC values to parameters

A CC gives you 0–127. Your synth parameter has a real range and a natural scale. Mapping has three parts.

### 1. Choose the curve

For **frequencies and times**, use an exponential curve, so that equal knob movements give equal musical intervals. The idea: instead of adding a fixed number of hertz per step, *multiply* by a fixed ratio per step, so every step is the same musical interval.

```formula
f = f_lo (f_hi / f_lo)^{v / 127}
f = 20 Hz × (20000 / 20)^{64 / 127}
f ≈ 20 Hz × 1000^{0.504}
f ≈ 649.9 Hz
where
f: the parameter value the knob position maps to, here a filter cutoff in hertz (Hz)
f_lo: the value at CC 0, the bottom of the range; 20 Hz here
f_hi: the value at CC 127, the top of the range; 20,000 Hz (20 kHz) here
v: the received CC value, 0 to 127; 64 is the knob's midpoint
127: the largest CC value, so v / 127 runs from 0 to 1
Hz: hertz, cycles per second
x^{…}: raising to the power in braces
≈: approximately equal to (rounded)
In words: the knob's position chooses how far along the ratio from 20 Hz to 20 kHz you are; the midpoint lands near the geometric middle (about 650 Hz), not the arithmetic middle (about 10 kHz).
```

The same mapping in Python, with its values across the knob:

```python
def cc_to_cutoff(v, lo=20.0, hi=20000.0):
    # exponential: equal steps = equal
    # musical intervals
    return lo * (hi / lo) ** (v / 127)

# Output: controller value then cutoff in
# Hz.
for v in (0, 32, 64, 96, 127):
    print(v, round(cc_to_cutoff(v), 1))
```

```output
0 20.0
32 114.0
64 649.9
96 3704.6
127 20000.0
```

Compare a linear map over the same range, which adds a fixed number of hertz per step:

```formula
f = f_lo + ((f_hi − f_lo)v / 127)
f = 20 Hz + 19980 Hz × 1 / 127
f ≈ 177 Hz
where
f: the cutoff the knob position maps to, in hertz (Hz)
f_lo: the value at CC 0; 20 Hz
f_hi: the value at CC 127; 20,000 Hz
v: the CC value; 1 here, the first step above zero
Hz: hertz, cycles per second
≈: approximately equal to (rounded)
In words: a linear map adds about 157 Hz per step, which is a huge musical jump at the bottom and an inaudible one at the top.
```

So the step from 0 to 1 jumps from 20 Hz to about 177 Hz (more than three octaves), and half the knob covers 10–20 kHz where little changes audibly. How evenly does the exponential map spread its steps? Count the octaves in the range, then divide them between the 127 steps:

```formula
N_oct = log_2(f_hi / f_lo)
N_oct = log_2(20000 / 20)
N_oct = log_2(1000) ≈ 9.97
Δ = (12 N_oct) / 127
Δ = 12 × 9.97 / 127 ≈ 0.94
where
N_oct: the number of octaves (doublings) between the bottom and top of the range
log_2: logarithm base 2, which counts how many times you must double to get from 1 to the number; log_2(8) = 3
f_hi: the top of the range, 20,000 Hz
f_lo: the bottom of the range, 20 Hz
Δ: the interval covered by one CC step, in semitones (there are 12 semitones in an octave)
≈: approximately equal to (rounded)
In words: 20 Hz to 20 kHz is about 10 octaves, or 120 semitones, so 127 equal steps are just under a semitone each.
```

These formulas assume f_lo is above zero (an exponential map can never reach 0 Hz) and that the parameter really is perceived on a ratio scale, as pitch and time are. A linear mapping can suit a control position. A pan control's audible gain law is a separate design choice, so equal position steps need not mean linear channel gains.

A decibel-style curve can be useful for **mix levels**; choose its range and mute behaviour explicitly. For MIDI controllers defined as **switches**, use the documented convention: values up to 63 are off, and values from 64 are on.

## Key takeaways
- Choose a curve for the parameter; exponential frequency mapping spreads ratios evenly but does not add MIDI resolution.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1, including the running status appendix (CCRMA copy)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Polyphony and monophony in instruments: note priority — Wikipedia](https://en.wikipedia.org/wiki/Polyphony_and_monophony_in_instruments)
- [MIDI library for Teensy (serial MIDI) — PJRC](https://www.pjrc.com/teensy/td_libs_MIDI.html)
