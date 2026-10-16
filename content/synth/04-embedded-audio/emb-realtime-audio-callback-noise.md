---
id: emb-realtime-audio-callback-noise
sourceLesson: emb-realtime-audio
title: "Investigate a block-rate noise tone"
level: advanced
minutes: 2
summary: "A repeatable power transient can produce a tone at the callback rate."
---

A block contains a fixed number of samples per channel. At a fixed sample rate, dividing that rate by the block size gives callback calls per second.

> [!example] A real block-rate artefact
> Electro-Smith's "Avoiding callback noise" guide explains that a long-running callback creates a current transient each time it exits, which can disturb ground on your PCB. That repeats at the callback rate: 1 kHz for 48-sample blocks at 48 kHz, squarely audible. One suggested fix is a 2-sample block, pushing the artefact to 24 kHz. Good layout and power filtering are the others.

## Key takeaways
- A repeatable power transient can produce a tone at the callback rate.
- A smaller block changes the disturbance rate and overhead; it does not fix every noise mechanism.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Getting started: audio (callback rules, CpuLoadMeter) — Electro-Smith](https://docs.daisy.audio/tutorials/_a3_Getting-Started-Audio/)
- [Avoiding callback noise — Electro-Smith](https://docs.daisy.audio/tutorials/eliminating-callback-noise/)
- [Audio library processor usage — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
- [libDaisy source (daisy_seed.cpp defaults)](https://github.com/electro-smith/libDaisy)
- [Teensy 4 AudioStream.cpp (software interrupt, cycle counting) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/AudioStream.cpp)
- [PCM3060 datasheet (group delay) — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm3060.pdf)
