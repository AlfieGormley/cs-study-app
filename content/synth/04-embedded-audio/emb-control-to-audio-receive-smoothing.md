---
id: emb-control-to-audio-receive-smoothing
sourceLesson: emb-control-to-audio
title: "Smooth on the audio side"
level: advanced
minutes: 3
summary: "Audio-rate smoothing reduces abrupt parameter steps after a safe data transfer."
---

## Safe transfer can still sound abrupt

An atomic or queue can deliver the correct control value while the sound still clicks. Knobs arrive at control rate, and ordinary 7-bit MIDI CC values have only 128 steps. Applying a new gain or cutoff in one jump can cause **zipper noise**.

Smooth the received target inside the callback at audio rate. This serves a different purpose from foreground smoothing: foreground smoothing reduces noisy readings; receiving-side smoothing spreads each delivered change across audio samples.

## Two useful responses

A **one-pole smoother** moves a fraction of the remaining gap on each sample. It starts quickly and slows as it approaches the target. An exponential time constant of 5 ms means about 63% of a fixed step is covered after 5 ms, not that the transition has finished. Choose and test the time constant for the parameter.

Calculate the fraction from the actual sample rate and desired response at initialisation or when the rate changes. The earlier control-smoother reference provides that relationship with the update rate now set to audio rate. Keep the exponential calculation out of the per-sample path. Illustrative pseudocode:

```
initialise current and coefficient
per sample:
  current += coefficient * (target-current)
  render using current
```

A **linear ramp** uses equal increments over a chosen number of samples and reaches a defined endpoint. It may span one block or several. Retain state between blocks; if the target changes mid-ramp, start the new transition from the current value rather than jumping back to the old start.

For a one-block ramp, decide whether the increment is applied before or after each sample. Applying it before each of 48 samples reaches the target on the last sample in exact arithmetic. Set the exact target at completion to avoid accumulating floating-point endpoint error.

Neither method guarantees an inaudible change for every signal and parameter. Digital samples remain discrete. For frequency, choose whether the ramp should move in hertz or logarithmic frequency; equal hertz steps are not equal pitch steps. Listen and measure for large changes and retriggering.

## Choosing a transfer pattern

| Data | Pattern |
|---|---|
| Single knob value | Atomic, smooth in callback |
| Grouped parameter change | One message or acknowledged buffers |
| Note on/off, program change | SPSC event queue |
| Meters, clip flag back to UI | Atomic or SPSC queue |
| Debug logging | Queue to main loop |

## Key takeaways
- Audio-rate smoothing reduces abrupt parameter steps after a safe data transfer.
- One-pole curves and linear ramps have different endpoint and timing behavior.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Why the "volatile" type class should not be used — Linux kernel documentation](https://github.com/torvalds/linux/blob/master/Documentation/process/volatile-considered-harmful.rst)
- [std::memory_order (acquire/release) — cppreference](https://en.cppreference.com/w/cpp/atomic/memory_order)
- [Circular buffer — Wikipedia](https://en.wikipedia.org/wiki/Circular_buffer)
- [Audio library processor usage and AudioNoInterrupts — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
- [Linear and multiplicative smoothing — JUCE](https://docs.juce.com/master/classSmoothedValue.html)
