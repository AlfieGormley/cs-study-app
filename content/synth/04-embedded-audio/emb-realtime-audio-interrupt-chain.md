---
id: emb-realtime-audio-interrupt-chain
sourceLesson: emb-realtime-audio
title: "What triggers an audio callback?"
level: advanced
minutes: 2
summary: "DMA servicing and DSP can run at separate interrupt priorities."
---

Every audio platform, from a Daisy to a laptop running Ableton, works the same way underneath: hardware asks for a block of samples at fixed intervals, and your code must deliver it in time. A missed deadline can produce stale or incomplete audio, clicks or dropouts; whether one is audible depends on the data and buffering. Miss often and the instrument is unusable. This lesson is the contract your audio code signs.

## Interrupts and the audio callback

An **interrupt** is a hardware signal that makes the CPU pause what it is doing, save its place, run a short **interrupt service routine** (ISR), then resume. Interrupts have **priorities**: a higher-priority interrupt can preempt a lower-priority one, and an enabled, unmasked eligible interrupt can preempt the main loop.

> [!analogy] Real-world analogy: An oven timer while you cook
> You are chopping vegetables when the oven timer rings. You stop, take the tray out, then return to the chopping board where you left off. A smoke alarm would take priority over even the oven.
>
> **How it maps:** Chopping is the main loop, the timer is the DMA interrupt and taking the tray out is the short service routine. The smoke alarm is a higher-priority interrupt that can preempt a lower one.
>
> **Where it stops:** The CPU saves and restores its exact state automatically and resumes in microseconds. The audio timer also rings at strict, regular intervals, and being late corrupts the output rather than merely overcooking a tray.

On an MCU audio platform, the chain is:

```flow
Codec clocks samples in and out via I2S/SAI
DMA moves them to and from a RAM buffer
DMA reaches the half or end of the buffer
DMA interrupt fires
Library converts formats, calls callback
Callback computes the next block and returns
```

The **audio callback** is the function you write. libDaisy calls it from the DMA half-complete and complete callbacks (the codec/DMA units). The Teensy Audio Library is organised slightly differently. In its source, the I2S output's DMA interrupt calls `update_all()`, which only sets a *software* interrupt pending; that software interrupt, configured at a low priority (208, where 255 is lowest), then runs every audio object's update. The short DMA interrupt stays responsive while the long DSP work runs at lower priority.

The **main loop** (foreground) runs whenever no interrupt is active. That is where knobs, displays, MIDI parsing and logging belong.

```
time ->
main  ===   =====   ====   =====
cb       ##      ##     ##      ##
         ^ DMA interrupt, every block
```

## Key takeaways
- DMA servicing and DSP can run at separate interrupt priorities.
- Foreground work runs when eligible interrupts are not occupying the core.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Getting started: audio (callback rules, CpuLoadMeter) — Electro-Smith](https://docs.daisy.audio/tutorials/_a3_Getting-Started-Audio/)
- [Avoiding callback noise — Electro-Smith](https://docs.daisy.audio/tutorials/eliminating-callback-noise/)
- [Audio library processor usage — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
- [libDaisy source (daisy_seed.cpp defaults)](https://github.com/electro-smith/libDaisy)
- [Teensy 4 AudioStream.cpp (software interrupt, cycle counting) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/AudioStream.cpp)
- [PCM3060 datasheet (group delay) — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm3060.pdf)
