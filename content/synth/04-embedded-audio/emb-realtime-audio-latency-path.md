---
id: emb-realtime-audio-latency-path
sourceLesson: emb-realtime-audio
title: "Estimate and measure the latency path"
level: advanced
minutes: 3
summary: "Serial delivery, polling, queueing and converter delay are separate contributions."
---

## Budget is not latency

The budget answers "how long do I have to compute a block?". **End-to-end latency** answers "how long from a key press to sound coming out?". They are related but not equal, and the project roadmap asks you to keep them distinct.

For an illustrative MIDI-triggered setup with 48-sample blocks at 48 kHz, assume the complete message is promptly parsed and handed over, the callback adopts events at its next boundary, and the filled output waits one block for playback. The following is an upper estimate within those assumptions, not a measured worst-case bound on Daisy or the complete instrument:

```formula
L = t_MIDI + T_block + T_block + d_DAC
d_DAC = 20 / f_s = 20 / 48000 Hz ≈ 0.42 ms
L = (0.96 + 1.00 + 1.00 + 0.42) ms
L ≈ 3.38 ms
where
L: the estimated upper delay within the stated model from the MIDI message starting to converter output, in milliseconds (ms); parsing stalls and additional buffering are excluded
t_MIDI: the time to send a three-byte note-on over DIN MIDI, 0.96 ms (the serial-bus units)
T_block: one block period, here 1 ms; it appears twice, once for waiting for the next callback and once for the double-buffer queue
d_DAC: the codec DAC's digital-filter group delay; 20 sample periods for the PCM3060
f_s: the sample rate, in hertz (Hz); here 48 kHz
Hz: hertz, samples per second
ms: millisecond
≈: approximately equal to
In words: the model gives about 3.4 ms for the synth path under its stated assumptions; the block size accounts for two of those milliseconds.
```

The same sum as a Python breakdown:

```python
fs = 48_000
block = 48
blk_ms = block / fs * 1000
# Conditional model, excluding parsing
# stalls.
parts = {
    "MIDI note-on (3 bytes)": 0.96,
    "wait for block (worst)": blk_ms,
    "compute + queue (1 blk)": blk_ms,
    "DAC filter (20/fs)": 20 / fs * 1000,
}
for name, ms in parts.items():
    print(f"{name:<24}{ms:5.2f} ms")
# Sum the same assumed path contributions.
print(f"{'total':<24}"
      f"{sum(parts.values()):5.2f} ms")
```

```output
MIDI note-on (3 bytes)   0.96 ms
wait for block (worst)   1.00 ms
compute + queue (1 blk)  1.00 ms
DAC filter (20/fs)       0.42 ms
total                    3.38 ms
```

- **MIDI transmission:** 960 µs for a three-byte note-on (the serial-bus units).
- **Waiting for the next block:** an event arriving just after a callback started is not seen until the next one, up to one block later.
- **Queue:** with double buffering, a block computed now starts playing about one block later.
- **Converter delay:** the PCM3060 datasheet gives a DAC digital-filter group delay of 20/fs (0.42 ms at 48 kHz). Codec ADCs add their own on the input path (17.4/fs for the PCM3060's ADC).

This is an *estimate* for the synth's own part. If the main loop polls MIDI less often than every block, add that. Then the audio interface adds its ADC delay and its driver buffer, and Ableton adds its own buffer if you monitor through it. Measure the total with a loopback recording rather than trusting a sum.

## Key takeaways
- Serial delivery, polling, queueing and converter delay are separate contributions.
- A conditional timing model is a starting estimate; measure the selected complete path.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Getting started: audio (callback rules, CpuLoadMeter) — Electro-Smith](https://docs.daisy.audio/tutorials/_a3_Getting-Started-Audio/)
- [Avoiding callback noise — Electro-Smith](https://docs.daisy.audio/tutorials/eliminating-callback-noise/)
- [Audio library processor usage — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
- [libDaisy source (daisy_seed.cpp defaults)](https://github.com/electro-smith/libDaisy)
- [Teensy 4 AudioStream.cpp (software interrupt, cycle counting) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/AudioStream.cpp)
- [PCM3060 datasheet (group delay) — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm3060.pdf)
