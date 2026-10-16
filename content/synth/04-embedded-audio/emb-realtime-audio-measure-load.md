---
id: emb-realtime-audio-measure-load
sourceLesson: emb-realtime-audio
title: "Measure maximum audio load"
level: advanced
minutes: 4
summary: "A cycle counter or GPIO pulse measures the work included within its boundaries."
---

## Measuring CPU load

**CPU load** is the fraction of the budget the callback uses:

```formula
load = t_cb / T_block
load = 0.6 ms / 1 ms = 0.6 = 60 %
where
load: the CPU load, a fraction (or percentage) of the budget; above 1 (100 %) the block is late
t_cb: the time one callback takes to run, in milliseconds (ms); here 0.6 ms
T_block: the block period, the budget, in milliseconds (ms); here 1 ms
ms: millisecond
%: percent, hundredths
In words: a callback that takes 0.6 ms out of a 1 ms budget is a 60% load, leaving 40% headroom.
```

Measured in cycles instead, divide the cycles the callback used by the cycles per block; the ratio is the same. Measure observed maxima as well as averages; one slow block can be enough for an audible fault, and a finite run does not prove worst-case timing.

### Cycle counters

Most Cortex-M3, M4 and M7 chips include a cycle counter (`CYCCNT`, in the DWT debug unit) that counts CPU clock cycles. It is optional in the Armv7-M architecture (the `NOCYCCNT` bit in `DWT_CTRL` says whether it exists), and Cortex-M0/M0+ parts do not have it, so confirm your part has it. It is also off after reset: firmware must set `TRCENA` in `DEMCR` and `CYCCNTENA` in `DWT_CTRL`. Teensy 4's start-up code does both, and its audio library reads the counter as `ARM_DWT_CYCCNT`; PJRC's page notes it counts at the CPU clock (600 MHz). The 32-bit counter wraps every few seconds at these clocks, which unsigned subtraction handles for short intervals:

```formula
t_wrap = 2^32 / f_cpu
t_wrap = 4294967296 / 600000000 Hz ≈ 7.2 s
where
t_wrap: the time until the counter overflows back to 0, in seconds (s)
2^32: 2 raised to the power 32, the number of values a 32-bit counter can hold, about 4.29 billion
f_cpu: the CPU clock frequency, in hertz (Hz); here Teensy 4's 600 MHz (at 480 MHz it is about 8.9 s)
Hz: hertz, cycles per second
s: second
≈: approximately equal to
In words: at 600 MHz the cycle counter rolls over about every 7 seconds, far longer than any callback, so same-width unsigned subtraction gives the interval if fewer than one full wrap elapsed. A signed subtraction is not the intended operation.
```

Read it at the start and end of the callback:

```
callback(in, out, n):
  t0 = cycle_count()
  ... process ...
  used = unsigned32(cycle_count() - t0)
  load = used / cycles_per_block
  max_load = max(max_load, load)
```

Libraries wrap this for you:

- **libDaisy `CpuLoadMeter`:** call `OnBlockStart()` and `OnBlockEnd()` in the callback; read average, minimum and maximum load from the main loop. (It times blocks with libDaisy's `System::GetTick()` timer rather than the DWT counter.)
- **Teensy `AudioProcessorUsageMax()`:** an estimate of the maximum percentage of CPU any audio update has used, which PJRC calls "the most useful for assuring the audio processing is operating within acceptable limits". Its implementation uses the cycle counter.

### GPIO toggle and a scope

Set a spare pin high at the start of the callback and low at the end. On an oscilloscope (or a cheap logic analyser):

```
pin  _|‾‾|________|‾‾‾|_______|‾‾|____
      <-> busy     <--- period --->
```

- Pulse **width** is the callback time and the **period** is the block period, so the load is the width divided by the period (0.8 ms wide every 2.9 ms is about 28%).
- You see **jitter** and occasional long blocks directly, using persistence or a trigger on pulse width.
- The two pin writes and the measurement method add overhead; quantify it on the chosen platform.

### Know the limits of your measurement

- The callback's time varies with what the synth is doing. Measure with the worst realistic case: all voices sounding, every effect on, knobs moving.
- Caches and memory location (lesson 1) change timing; code that is fast in one build may be slower after an unrelated change moves it.
- Library code outside your callback (format conversion, interrupt entry) also uses the budget. Library meters may or may not include it; a GPIO toggle only measures what lies between the toggles.
- Decide a margin, record the measured maximum and the conditions, and re-measure after significant changes.

## Key takeaways
- A cycle counter or GPIO pulse measures the work included within its boundaries.
- Record build, workload, maxima and margin; a finite measurement is not a universal timing proof.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Getting started: audio (callback rules, CpuLoadMeter) — Electro-Smith](https://docs.daisy.audio/tutorials/_a3_Getting-Started-Audio/)
- [Avoiding callback noise — Electro-Smith](https://docs.daisy.audio/tutorials/eliminating-callback-noise/)
- [Audio library processor usage — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
- [libDaisy source (daisy_seed.cpp defaults)](https://github.com/electro-smith/libDaisy)
- [Teensy 4 AudioStream.cpp (software interrupt, cycle counting) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/AudioStream.cpp)
- [PCM3060 datasheet (group delay) — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm3060.pdf)
