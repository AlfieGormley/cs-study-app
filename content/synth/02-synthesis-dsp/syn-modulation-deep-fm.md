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

The ±1-octave result follows from the mapping’s asymmetry:

One octave below 440 Hz is 220 Hz; one octave above is 880 Hz. Equal time at paired positive and negative octave offsets adds more hertz on the upper side than it removes on the lower side. Over complete cycles, the arithmetic mean frequency therefore rises even though the sine control itself has zero mean.

## Key takeaways

- Symmetry in octaves is asymmetric in hertz.
- Average instantaneous frequency and perceived pitch are different measurements.
- Zero-mean linear FM preserves mean instantaneous frequency; periodic PM can too.

## Further reading

- [Sinusoidal FM and PM — Julius O. Smith](https://ccrma.stanford.edu/~jos/mdft/Sinusoidal_Frequency_Modulation_FM.html)
- [Frequency modulation synthesis — CMU](https://www.cs.cmu.edu/~music/icm-online/readings/fm-synthesis/index.html)
