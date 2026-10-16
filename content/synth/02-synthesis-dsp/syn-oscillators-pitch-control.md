---
id: syn-oscillators-pitch-control
title: Musical pitch and frequency control
level: basic
minutes: 2
summary: Musical pitch and frequency control.
sourceLesson: syn-oscillators
---

## Frequency control

Musical pitch is exponential: each octave doubles the frequency. MIDI note numbers convert to hertz with the twelve-tone equal temperament formula (from module 1):

```formula
f = 440 Hz × 2^{(m − 69)/12}
f = 440 Hz × 2^{(60 − 69)/12}
f = 440 Hz × 2^{−0.75} ≈ 261.63 Hz
where
f: the note's frequency, in hertz (Hz)
m: the MIDI note number (called `note` in code), a whole number from 0 to 127; 69 is the A above middle C and 60 is middle C
440 Hz: the reference pitch given to note 69 (A4)
12: the number of semitones in an octave; one semitone multiplies the frequency by 2^{1/12}, about 1.0595
2^{x}: 2 raised to the power x; adding 12 to m doubles f, subtracting 12 halves it
≈: approximately equal to
Hz: hertz, cycles per second
In words: count semitones away from note 69 (440 Hz) and multiply by 2 for every 12 of them.
```

So note 60 (middle C) is 261.63 Hz, and note 81 (an octave above note 69) is 880 Hz. Pitch modulation, pitch bend and detune are added in *semitones* or *cents* before this conversion, then the increment is recomputed. Because the increment is just the frequency divided by the sample rate, it can change each sample while phase stays continuous. A sudden frequency step can still make an audible transient or unwanted modulation; smoothing and a suitable band-limited oscillator remain necessary.

## Key takeaways

- Equal-tempered note numbers map exponentially to frequency.
- Changing increment preserves phase continuity, while abrupt frequency changes can still need smoothing.

## Further reading

- [Tuning and reference note — MIDI Association](https://midi.org/microtuning-and-alternative-intonation-systems)
- [Notes, octaves and frequency — UNSW Acoustics](https://newt.phys.unsw.edu.au/jw/notes.html)
