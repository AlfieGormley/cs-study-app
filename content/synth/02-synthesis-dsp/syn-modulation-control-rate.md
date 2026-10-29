---
id: syn-modulation-control-rate
title: Control-rate and per-sample modulation
level: intermediate
minutes: 3
summary: Control-rate and per-sample modulation.
sourceLesson: syn-modulation
---

## Control rate versus audio rate

Not every signal needs updating 48,000 times a second. Many synths compute modulation at a **control rate**, once per block, and only the audio path per sample.

The important comparison is updates per event. A slow LFO gets many updates within one cycle, while a millisecond attack may span only one or two blocks. Holding one value for each block can make the fast event a handful of abrupt steps.

At 48 kHz with 32-sample blocks the control rate is 1.5 kHz, and each block lasts 0.67 ms. That's plenty for a 5 Hz LFO (300 updates per cycle). It's not enough for:

- **Fast envelopes:** a 1 ms attack would be about 1.5 control steps, a staircase that can cause a click or buzz, depending on the signal and playback level.
- **Fast or stepped modulation of gain and cutoff:** the block-rate staircase is the zipper noise from the envelopes lesson.
- **Audible-frequency pitch modulation:** varying oscillator frequency with an audible-frequency modulator is FM (covered in the neighbouring synthesis units). It creates sidebands (below) and needs sufficient update bandwidth; in this voice, compute it per sample.

For the sideband example, assume a sine carrier with constant-depth sinusoidal **linear FM**. This is not the deep exponential pitch mapping discussed next:

For constant-depth sinusoidal linear FM of a sine carrier, sidebands are spaced at whole multiples of the modulator frequency on either side of the carrier. Their levels depend on modulation depth, and components can cancel.

With modest pitch depth, a 5 Hz LFO is commonly heard as vibrato. Its sidebands are spaced by 5 Hz; perception depends on carrier, depth and listening conditions rather than a universal boundary between “wobble” and “separate tones”. A 220 Hz modulator on a 440 Hz carrier puts them at 220, 660, 880 Hz and so on: new tones, which a block-rate staircase cannot produce correctly.

Common compromise: compute modulation sources at control rate, then **linearly interpolate** the result across the block (or feed it into per-sample smoothers), and run anything fast or audible (amp envelope, audible-frequency FM) per sample.

## Putting it together

A complete basic voice now looks like this, with the per-sample and control-rate parts marked:

```diagram
per block (control rate):
  LFO, mod wheel, matrix sums
     |  interpolate / smooth
     v
per sample (audio rate):
  osc(pitch) -> filter(cutoff, res)
     -> amp(amp env * velocity)
```

That's a playable monophonic subtractive synth. The roadmap's suggested exercise for this lesson is to apply an LFO to amplitude or pitch, then explain what you hear in terms of rate, depth and units.

## Key takeaways

- Compare the update rate with the fastest relevant event.
- Interpolate slow controls; fast envelopes and audible-frequency modulation generally belong in the sample loop.

## Further reading

- [Sinusoidal FM and PM — Julius O. Smith](https://ccrma.stanford.edu/~jos/mdft/Sinusoidal_Frequency_Modulation_FM.html)
- [SmoothedValue — JUCE](https://docs.juce.com/master/classSmoothedValue.html)
- [Real FFT — NumPy](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
