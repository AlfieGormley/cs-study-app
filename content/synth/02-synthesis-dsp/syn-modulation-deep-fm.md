---
id: syn-modulation-deep-fm
title: Deep exponential modulation and mean frequency
level: intermediate
minutes: 3
summary: Deep exponential modulation and mean frequency.
sourceLesson: syn-modulation
---

> [!note] Exponential versus linear FM
> Applying an oscillator to pitch *in octaves* (exponential FM, as you would for vibrato) is not symmetric in hertz. In a quick numpy check, a 5 Hz LFO at ±1 octave on 440 Hz gave an average frequency of 494.5 Hz, roughly 2 semitones sharp. At vibrato depths (±1 semitone) the average was about 440.37 Hz, a small but non-zero mean-frequency shift. For deep FM with an audible-frequency modulator, synths use **linear** FM (or phase modulation), which can keep the mean instantaneous frequency at the carrier (for zero-mean linear modulation). Perceived pitch and tuner readings depend on the resulting spectrum and analysis method; they are not guaranteed by that arithmetic mean.

The ±1-octave check computed this instantaneous frequency:

```formula
f(t) = f_0 × 2^{D sin(2πrt)}
f(t) = 440 Hz × 2^{sin(2π × 5 × t)}
where
f(t): the instantaneous frequency at time t, in hertz (Hz)
f_0: the unmodulated frequency, 440 Hz
D: the depth in octaves: 1 for ±1 octave, 1/12 for ±1 semitone
sin: the sine function, taking an angle in radians
π: pi, about 3.14159
r: the LFO rate, 5 Hz; the substituted numeric 5 also has units of hertz
t: time, in seconds
Hz: hertz
In words: the frequency swings between 220 Hz (half) and 880 Hz (double); the upper half-swing adds 440 Hz but the lower one removes only 220 Hz, so the average sits above 440 Hz, at about 494.5 Hz.
```

## Key takeaways

- Symmetry in octaves is asymmetric in hertz.
- Average instantaneous frequency and perceived pitch are different measurements.
- Zero-mean linear FM preserves mean instantaneous frequency; periodic PM can too.

## Further reading

- [Sinusoidal FM and PM — Julius O. Smith](https://ccrma.stanford.edu/~jos/mdft/Sinusoidal_Frequency_Modulation_FM.html)
- [Frequency modulation synthesis — CMU](https://www.cs.cmu.edu/~music/icm-online/readings/fm-synthesis/index.html)
