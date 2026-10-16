---
id: emb-control-to-audio-receive-smoothing
sourceLesson: emb-control-to-audio
title: "Smooth on the audio side"
level: advanced
minutes: 4
summary: "Audio-rate smoothing reduces abrupt parameter steps after a safe data transfer."
---

## Pattern 4: smooth on the receiving side

The callback now receives correct values, but they arrive in steps: knob scans at around 1 kHz, MIDI CCs in 128 coarse steps. Jumping a gain or cutoff by a step at a block boundary makes **zipper noise**. Smooth again, at audio rate, inside the callback:

**Per-sample one-pole** towards the latest target. This is the same smoother as the knob-reading units', now updated once per audio sample instead of once per knob reading:

```formula
a = 1 − e^(−1 / (τ f_s))
a = 1 − e^(−1 / (0.005 s × 48000 Hz))
a = 1 − e^(−1 / 240) ≈ 0.004158
c_n = c_{n−1} + a(g − c_{n−1})
where
a: the smoothing coefficient per sample, between 0 and 1, no unit
e: Euler's number, about 2.71828
τ: tau, the time constant, in seconds (s): the time to cover about 63% of a jump; here 5 ms = 0.005 s
f_s: the sample rate, in hertz (Hz); here 48 kHz
c_n: the smoothed parameter value used for sample n
c_{n−1}: the smoothed value used for the previous sample
g: the target, the latest value received from the foreground
n: the sample number
s: second
Hz: hertz, samples per second
≈: approximately equal to
In words: a 5 ms time constant spans 240 samples at 48 kHz, so each sample closes about 0.42% of the gap to the target; a jump becomes a smooth curve lasting a few milliseconds.
```

For a 20 ms time constant, the same formula gives a coefficient of about 0.001041. Compute `a` once at start-up, not per sample, because the exponential is expensive. In code:

```
a = 1 - exp(-1 / (tau * fs))   # at init
per sample:
  cur = cur + a * (target - cur)
```

**Linear ramp per block:** step from the old value to the new across the block, adding the same increment each sample:

```formula
Δ = (v_new − v_old) / N
Δ = (1000 Hz − 520 Hz) / 48 = 10 Hz
where
Δ: the amount added to the parameter on every sample of the block, in the parameter's own unit
v_new: the value received for this block; here a cutoff of 1,000 Hz
v_old: the value at the end of the previous block; here 520 Hz
N: the block size, samples per channel; here 48
Hz: hertz, the unit of this example parameter
In words: spread the change evenly over the block, so a 480 Hz jump becomes 48 steps of 10 Hz.
```

In the mathematical version, apply the increment before each of the 48 output samples: the last parameter value reaches the target. Real code must choose that endpoint convention, retain state across blocks and account for rounding; assigning the exact target after the last step avoids cumulative endpoint error. Other ramp durations can span several blocks. Sample-rate steps can still be audible for large or sensitive changes, so listen and measure rather than promising silence.

Why smooth here and not only in the foreground? The foreground can only deliver values as often as it runs. The receiving side knows the sample rate, so it is the only place that can reduce the size and spacing of parameter steps; digital samples remain discrete. The foreground smoothing from the knob-reading units is about rejecting knob noise; this smoothing is about removing steps.
## Choosing a pattern

| Data | Pattern |
|---|---|
| Single knob value | Atomic, smooth in callback |
| Grouped parameter change | One message or double buffer |
| Note on/off, program change | SPSC event queue |
| Meters, clip flag (back) | Atomic or SPSC queue |
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
