---
id: emb-realtime-audio-block-budget
sourceLesson: emb-realtime-audio
title: "Understand the block processing budget"
level: advanced
minutes: 3
summary: "Block duration is the deadline interval, not the complete path latency."
---

## A deadline for every block

The **block size** is the number of samples per channel processed in one callback. Hardware consumes those samples at the sample rate. All work needed to prepare the next block must finish before its playback deadline, every time.

```formula essential
T_block = N / f_s
where
T_block: duration of one block, in seconds (s)
N: samples per channel in one block, dimensionless count
f_s: sample rate, in sample frames per second (Hz)
s: second, the unit of time
Hz: hertz, here sample frames per second
In words: block duration is the number of samples per channel divided by how many sample frames play each second. More samples give a longer deadline interval; a higher sample rate shortens it.
```

At 48 kHz, a 48-sample block lasts 1 ms. Double the block size at the same sample rate and the duration doubles. Double the sample rate without changing the block size and the duration halves.

| Example configuration | Block | Sample rate | Duration |
|---|---|---|---|
| libDaisy Seed default | 48 | 48 kHz | 1.00 ms |
| Teensy Audio Library default | 128 | 44.1 kHz | About 2.90 ms |
| Smaller block | 4 | 48 kHz | About 0.083 ms |
| Larger block | 256 | 48 kHz | About 5.33 ms |

Defaults describe the checked source versions, not permanent hardware requirements. Confirm supported sizes and rates in the chosen driver.

## Share the budget and leave margin

CPU clock cycles give another way to measure the same interval, but a cycle is not an instruction count. A nominal 480 MHz CPU has 480,000 clock ticks during 1 ms. DSP, library format conversion, interrupt work and time lost to higher-priority activity all have to fit.

If a meter reports a maximum observed load of 62.5%, the measured work used that fraction of the block interval. The remaining 37.5% is shared by anything the meter did not measure and your safety margin. That is **not a proof of safety**: check what the meter includes and what workloads it exercised.

## Smaller blocks have a cost

Smaller blocks shorten buffering delays but make callbacks more frequent. Fixed work such as interrupt entry and buffer bookkeeping happens more times per second. The same per-sample DSP can therefore use a higher percentage of the CPU after you shrink blocks.

Choose block size by measuring the actual workload, overhead and latency path. A callback finishing early does not remove converter delays or downstream buffers; block duration is a processing interval, not complete end-to-end latency.

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
