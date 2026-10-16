---
id: emb-realtime-audio-bounded-callback
sourceLesson: emb-realtime-audio
title: "Keep callback work bounded"
level: advanced
minutes: 2
summary: "Preallocate and perform bounded work without waiting in the audio callback."
---

## What must never happen in the callback

The callback must have a **bounded, predictable** execution duration. Anything whose duration is unknown, or that may wait for something else, breaks that. Ross Bencina's essay *Time waits for nothing* is the classic statement; Electro-Smith's audio guide says the same for Daisy: avoid dynamic allocation like `malloc` and blocking peripheral calls, and use flags to defer such work to the main loop.

| Never in the callback | Why |
|---|---|
| Memory allocation | Unbounded time; can fail; fragments |
| Locks, waits, sleeps | May wait on lower-priority code |
| Logging / printf | Formatting and I/O take long, variable time |
| File, SD, flash I/O | Milliseconds, and may block |
| Bus I/O (I2C display) | Blocks for ms (the serial-bus units) |
| Unbounded loops | No worst-case time |

Two subtle ones:

- **Locks and priority inversion.** If the callback waits for a lock held by the main loop, it cannot proceed until the main loop runs again. But on a bare-metal single-core MCU the main loop cannot run while the callback's interrupt is executing, so a callback that spins on that lock never gets it: a deadlock, and the audio stops. On an RTOS or a general-purpose OS, a high-priority audio thread blocked on a lock held by a low-priority thread is classic **priority inversion**: the holder may be descheduled for far longer than your budget. This is why the safe-transfer units uses lock-free techniques.
- **Logging.** Even a short `print` may format numbers, copy into a USB or UART buffer, and block when that buffer is full. Set a flag or write a counter, and print from the main loop.

Illustrative pseudocode: `peak` is the measured absolute output peak for this block, the flag uses verified bounded lock-free atomics, and the queue has an explicit per-block event limit. Platform-specific atomic syntax and initialization are omitted.

```
callback(in, out, n):
  read latest params (lock-free)
  apply up to MAX_EVENTS queued events
  for i in 0..n-1:
    out[i] = synth.next_sample()
  if peak > 1.0:
    atomic_clip_flag.store(true)

main loop:
  if atomic_clip_flag.exchange(false):
    log("clipped")
```

## Key takeaways
- Preallocate and perform bounded work without waiting in the audio callback.
- Defer logging and peripheral transfers, and bound queued event processing.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Getting started: audio (callback rules, CpuLoadMeter) — Electro-Smith](https://docs.daisy.audio/tutorials/_a3_Getting-Started-Audio/)
- [Avoiding callback noise — Electro-Smith](https://docs.daisy.audio/tutorials/eliminating-callback-noise/)
- [Audio library processor usage — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
- [libDaisy source (daisy_seed.cpp defaults)](https://github.com/electro-smith/libDaisy)
- [Teensy 4 AudioStream.cpp (software interrupt, cycle counting) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/AudioStream.cpp)
- [PCM3060 datasheet (group delay) — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm3060.pdf)
