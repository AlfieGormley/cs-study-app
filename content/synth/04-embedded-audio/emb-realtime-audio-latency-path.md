---
id: emb-realtime-audio-latency-path
sourceLesson: emb-realtime-audio
title: "Estimate and measure the latency path"
level: advanced
minutes: 3
summary: "Serial delivery, polling, queueing and converter delay are separate contributions."
---

## Budget is not latency

The block budget answers “how long can this computation take?”. **End-to-end latency** answers “how long from a key press to audible output?”. Faster computation can leave more headroom while the sound still waits in buffers.

> [!analogy] Real-world analogy: A parcel delivery
> A parcel's delivery time is not just the time to pack it. It also waits for collection, travels, and sits at a depot before the final van.
>
> **How it maps:** Computing a block is the packing. Waiting for the next callback is waiting for collection, the output buffer is the depot and the converter filter is the last journey. Faster packing does not shorten the other stages.
>
> **Where it stops:** Audio stages repeat every block with largely fixed delays, so their contributions can be modelled and measured. The answer also depends on where you start the clock: the first MIDI byte or the physical key press.

Trace each part of the path. This example assumes 48-sample blocks at 48 kHz, prompt parsing of a complete three-byte DIN MIDI note-on, adoption at the next callback boundary, and one block of output queueing:

| Contribution | Example delay |
|---|---|
| Three-byte DIN message | 0.96 ms |
| Wait for next callback | Up to 1 ms |
| Prepared output waiting to play | 1 ms |
| PCM3060 DAC filter | About 0.42 ms |

Together these give an upper estimate of about 3.4 ms **within this model**. It is not a measured worst-case bound for Daisy or a complete instrument. An event arriving just after adoption waits nearly a block; one arriving just before may wait much less.

The PCM3060 DAC's documented digital-filter group delay is 20 sample periods. Its ADC adds 17.4 sample periods on an audio-input path. Those conversion delays differ from the callback's computation time.

Additional foreground parsing delays, a busy queue or another output-buffering arrangement change the model. An audio interface adds input conversion and driver buffers; monitoring through Ableton adds its own configured buffering. The keyboard's sensing delay also matters if your measurement starts at the physical key press rather than the first MIDI byte.

Measure the selected complete path with a suitable loopback recording. Record where the measurement starts and ends, the buffer configuration and whether host monitoring is included. Use the model to decide what to investigate, then compare it with the recording.

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
