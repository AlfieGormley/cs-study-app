---
id: syn-modulation-control-rate
title: Control-rate and per-sample modulation
level: intermediate
minutes: 4
summary: Control-rate and per-sample modulation.
sourceLesson: syn-modulation
---

## Control rate versus audio rate

Not every signal needs updating 48,000 times a second. Many synths compute modulation at a **control rate**, once per block, and only the audio path per sample.

```formula
f_ctl = f_s / B = 48000 Hz / 32 = 1500 Hz
T_B = B / f_s = 32 / 48000 Hz ≈ 0.67 ms
U = T f_ctl = 0.001 s × 1500 Hz = 1.5
where
f_ctl: the control rate, in hertz (Hz): updates per second
f_s: the sample rate, 48,000 Hz
B: the block size, 32 samples
T_B: how long one block lasts, in milliseconds (ms)
U: how many control updates happen during an event of length T
T: the event's duration, here a 1 ms attack, 0.001 s
s: seconds
ms: milliseconds
Hz: hertz, per second
≈: approximately equal to
In words: one update per block gives 1,500 updates a second, so a 5 Hz LFO gets 300 per cycle but a 1 ms attack only 1.5.
```

At 48 kHz with 32-sample blocks the control rate is 1.5 kHz, and each block lasts 0.67 ms. That's plenty for a 5 Hz LFO (300 updates per cycle). It's not enough for:

- **Fast envelopes:** a 1 ms attack would be about 1.5 control steps, a staircase that can cause a click or buzz, depending on the signal and playback level.
- **Fast or stepped modulation of gain and cutoff:** the block-rate staircase is the zipper noise from the envelopes lesson.
- **Audible-frequency pitch modulation:** varying oscillator frequency with an audible-frequency modulator is FM (covered in the neighbouring synthesis units). It creates sidebands (below) and needs sufficient update bandwidth; in this voice, compute it per sample.

For the sideband example, assume a sine carrier with constant-depth sinusoidal **linear FM**. This is not the deep exponential pitch mapping discussed next:

```formula
f_sb = f_car ± k f_mod
where
f_sb: the frequency of one sideband, in hertz (Hz)
f_car: the carrier frequency (the oscillator being modulated), in Hz
f_mod: the modulator frequency, in Hz
k: a whole number 1, 2, 3...; each value gives one pair of sidebands
±: plus or minus: one sideband above the carrier and one below
Hz: hertz
In words: sidebands sit either side of the carrier, spaced at multiples of the modulator frequency.
```

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
