---
id: emb-realtime-audio-block-budget
sourceLesson: emb-realtime-audio
title: "Calculate a block processing budget"
level: advanced
minutes: 4
summary: "Block duration is the deadline interval, not the complete path latency."
---

## Block size and the processing budget

The callback processes a fixed number of samples per channel per call (the **block size**). The hardware plays one block in the time those samples last, so a new block is due every block period. That period is your **processing budget**: all the work for one block must finish within it, every time.

```formula
T_block = N / f_s
T_block = 48 / 48000 Hz = 0.001 s = 1 ms
where
T_block: the budget (block period), in seconds (s)
N: the block size, samples per channel per callback; here 48, libDaisy's default
f_s: the sample rate, in hertz (Hz); here 48 kHz = 48,000 Hz
Hz: hertz, samples per second
s: second
ms: millisecond, one thousandth of a second
In words: 48 samples at 48,000 samples a second last exactly 1 ms, so the callback must finish in under 1 ms every time.
```

Double the block size and the budget doubles; double the sample rate and it halves.

| Platform default | Block | fs | Budget |
|---|---|---|---|
| libDaisy (Seed) | 48 | 48 kHz | 1.000 ms |
| Teensy Audio Library | 128 | 44.1 kHz | 2.902 ms |
| Small block | 4 | 48 kHz | 0.083 ms |
| Large block | 256 | 48 kHz | 5.333 ms |

The libDaisy and Teensy defaults are from their source code (`audio_config.blocksize = 48` at 48 kHz in `daisy_seed.cpp`; `AUDIO_BLOCK_SAMPLES 128` and 44,100 Hz in Teensy's `AudioStream.h`). Electro-Smith's audio guide says Daisy's block size "can be any number up to 256".

```python
# Compare deadlines, not end-to-end delay.
for n, fs in [(48, 48000), (128, 44100),
              (4, 48000), (256, 48000)]:
    ms = n / fs * 1000
    print(f"{n:>4} @ {fs}: {ms:.3f} ms")
```

```output
  48 @ 48000: 1.000 ms
 128 @ 44100: 2.902 ms
   4 @ 48000: 0.083 ms
 256 @ 48000: 5.333 ms
```

### In CPU cycles

Time is easier to reason about as cycles: the number of CPU clock ticks that fit in the budget. Multiply the budget by the clock frequency:

```formula
C_block = (f_cpu N) / f_s
C_block = 480000000 Hz × 48 / 48000 Hz
C_block = 480000 cycles
C_sample = f_cpu / f_s = 10000 cycles
where
C_block: CPU clock cycles available per block
C_sample: CPU clock cycles available per sample frame
f_cpu: the CPU clock frequency, in hertz (Hz); here 480 MHz for the Daisy Seed's Cortex-M7
N: the block size, samples per channel; here 48
f_s: the sample rate, in hertz (Hz); here 48 kHz
Hz: hertz, cycles per second
cycles: CPU clock ticks; instruction throughput and latency vary, so a cycle is not a guaranteed instruction count
In words: a 480 MHz CPU gets 480,000 clock ticks for each 1 ms block, or 10,000 per stereo sample frame.
```

The same numbers in Python:

```python
# Nominal CPU clock; no instruction
# guarantee.
f_cpu = 480_000_000
fs = 48_000
n = 48
per_block = f_cpu * n // fs
per_sample = f_cpu // fs
print(per_block, per_sample)
```

```output
480000 10000
```

So 480,000 cycles per block, or 10,000 cycles per stereo sample frame. That sounds like a lot until you count a polyphonic synth: eight voices, each evaluating two oscillators, a filter, two envelopes and an LFO for every sample, plus shared effects. The budget is shared by *everything* in the callback, including the library's own format conversion.

The share used by a measured block is its work divided by this cycle budget. For a hypothetical measured maximum of 300,000 cycles:

```formula
load = C_used / C_block
load = 300000 / 480000 = 62.5 %
where
load: the fraction of this block budget used
C_used: CPU cycles measured for the work, here 300,000
C_block: CPU cycles available in a block, here 480,000
%: percent, hundredths
In words: this observed block uses 62.5 percent of the available cycles, before any overhead outside the measurement.
```

### Choosing a block size

Smaller blocks mean the callback runs more often, with fixed per-callback dispatch overhead (interrupt entry, DMA bookkeeping, function calls) paid more times per second. Teensy's source comments say reducing the block size achieves lower latency "at the expense of higher interrupt and DMA setup overhead". Larger blocks are more efficient but delay everything by more.

## Key takeaways
- Block duration is the deadline interval, not the complete path latency.
- Fixed per-callback dispatch overhead takes a larger share as blocks shrink.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Getting started: audio (callback rules, CpuLoadMeter) — Electro-Smith](https://docs.daisy.audio/tutorials/_a3_Getting-Started-Audio/)
- [Avoiding callback noise — Electro-Smith](https://docs.daisy.audio/tutorials/eliminating-callback-noise/)
- [Audio library processor usage — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
- [libDaisy source (daisy_seed.cpp defaults)](https://github.com/electro-smith/libDaisy)
- [Teensy 4 AudioStream.cpp (software interrupt, cycle counting) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/AudioStream.cpp)
- [PCM3060 datasheet (group delay) — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm3060.pdf)
