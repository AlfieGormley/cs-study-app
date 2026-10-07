---
id: emb-realtime-audio
title: The real-time audio model
level: advanced
minutes: 16
summary: How interrupts drive the audio callback, how block size sets the processing budget (with worked numbers), why that budget is not the same as end-to-end latency, what must never happen inside the callback and why, and how to measure CPU load with cycle counters and a scope.
---

Every audio platform, from a Daisy to a laptop running Ableton, works the same way underneath: hardware asks for a block of samples at fixed intervals, and your code must deliver it in time. Miss once and you hear a click. Miss often and the instrument is unusable. This lesson is the contract your audio code signs.

## Interrupts and the audio callback

An **interrupt** is a hardware signal that makes the CPU pause what it is doing, save its place, run a short **interrupt service routine** (ISR), then resume. Interrupts have **priorities**: a higher-priority interrupt can preempt a lower-priority one, and any interrupt preempts the main loop.

On an MCU audio platform, the chain is:

```flow
Codec clocks samples in and out via I2S/SAI
DMA moves them to and from a RAM buffer
DMA reaches the half or end of the buffer
DMA interrupt fires
Library converts formats, calls callback
Callback computes the next block and returns
```

The **audio callback** is the function you write. libDaisy calls it from the DMA half-complete and complete callbacks (lesson 4). The Teensy Audio Library is organised slightly differently. In its source, the I2S output's DMA interrupt calls `update_all()`, which only sets a *software* interrupt pending; that software interrupt, configured at a low priority (208, where 255 is lowest), then runs every audio object's update. The short DMA interrupt stays responsive while the long DSP work runs at lower priority.

The **main loop** (foreground) runs whenever no interrupt is active. That is where knobs, displays, MIDI parsing and logging belong.

```
time ->
main  ===   =====   ====   =====
cb       ##      ##     ##      ##
         ^ DMA interrupt, every block
```

## Block size and the processing budget

The callback processes **N samples per channel per call** (the **block size**). New blocks are due every N / fs seconds, so that is your **budget**: all the work for one block must finish within it, every time.

| Platform default | Block | fs | Budget |
|---|---|---|---|
| libDaisy (Seed) | 48 | 48 kHz | 1.000 ms |
| Teensy Audio Library | 128 | 44.1 kHz | 2.902 ms |
| Small block | 4 | 48 kHz | 0.083 ms |
| Large block | 256 | 48 kHz | 5.333 ms |

The libDaisy and Teensy defaults are from their source code (`audio_config.blocksize = 48` at 48 kHz in `daisy_seed.cpp`; `AUDIO_BLOCK_SAMPLES 128` and 44,100 Hz in Teensy's `AudioStream.h`). Electro-Smith's audio guide says Daisy's block size "can be any number up to 256".

```python
for n, fs in [(48, 48000), (128, 44100),
              (4, 48000), (256, 48000)]:
    ms = n / fs * 1000
    print(f"{n:>4} @ {fs}: {ms:.3f} ms")
```

```
  48 @ 48000: 1.000 ms
 128 @ 44100: 2.902 ms
   4 @ 48000: 0.083 ms
 256 @ 48000: 5.333 ms
```

### In CPU cycles

Time is easier to reason about as cycles. A 480 MHz Cortex-M7 (Daisy Seed) at 48 kHz:

```python
f_cpu = 480_000_000
fs = 48_000
n = 48
per_block = f_cpu * n // fs
per_sample = f_cpu // fs
print(per_block, per_sample)
```

```
480000 10000
```

So 480,000 cycles per block, or 10,000 cycles per stereo sample frame. That sounds like a lot until you count a polyphonic synth: 8 voices × (2 oscillators + filter + 2 envelopes + LFO) each sample, plus effects. The budget is shared by *everything* in the callback, including the library's own format conversion.

### Choosing a block size

Smaller blocks mean the callback runs more often, with fixed per-call overhead (interrupt entry, DMA bookkeeping, function calls) paid more times per second. Teensy's source comments say reducing the block size achieves lower latency "at the expense of higher interrupt and DMA setup overhead". Larger blocks are more efficient but delay everything by more.

> [!example] A real block-rate artefact
> Electro-Smith's "Avoiding callback noise" guide explains that a long-running callback creates a current transient each time it exits, which can disturb ground on your PCB. That repeats at the callback rate: 1 kHz for 48-sample blocks at 48 kHz, squarely audible. One suggested fix is a 2-sample block, pushing the artefact to 24 kHz. Good layout and power filtering are the others.

## Budget is not latency

The budget answers "how long do I have to compute a block?". **End-to-end latency** answers "how long from a key press to sound coming out?". They are related but not equal, and the project roadmap asks you to keep them distinct.

For a MIDI-triggered note on a Daisy-style setup (48 samples, 48 kHz), the delays stack up:

```python
fs = 48_000
block = 48
blk_ms = block / fs * 1000
parts = {
    "MIDI note-on (3 bytes)": 0.96,
    "wait for block (worst)": blk_ms,
    "compute + queue (1 blk)": blk_ms,
    "DAC filter (20/fs)": 20 / fs * 1000,
}
for name, ms in parts.items():
    print(f"{name:<24}{ms:5.2f} ms")
print(f"{'total':<24}"
      f"{sum(parts.values()):5.2f} ms")
```

```
MIDI note-on (3 bytes)   0.96 ms
wait for block (worst)   1.00 ms
compute + queue (1 blk)  1.00 ms
DAC filter (20/fs)       0.42 ms
total                    3.38 ms
```

- **MIDI transmission:** 960 µs for a three-byte note-on (lesson 5).
- **Waiting for the next block:** an event arriving just after a callback started is not seen until the next one, up to one block later.
- **Queue:** with double buffering, a block computed now starts playing about one block later.
- **Converter delay:** the PCM3060 datasheet gives a DAC digital-filter group delay of 20/fs (0.42 ms at 48 kHz). Codec ADCs add their own on the input path (17.4/fs for the PCM3060's ADC).

This is an *estimate* for the synth's own part. If the main loop polls MIDI less often than every block, add that. Then the audio interface adds its ADC delay and its driver buffer, and Ableton adds its own buffer if you monitor through it. Measure the total with a loopback recording rather than trusting a sum.

## What must never happen in the callback

The callback must have a **bounded, predictable** run time. Anything whose duration is unknown, or that may wait for something else, breaks that. Ross Bencina's essay *Time waits for nothing* is the classic statement; Electro-Smith's audio guide says the same for Daisy: avoid dynamic allocation like `malloc` and blocking peripheral calls, and use flags to defer such work to the main loop.

| Never in the callback | Why |
|---|---|
| Memory allocation | Unbounded time; can fail; fragments |
| Locks, waits, sleeps | May wait on lower-priority code |
| Logging / printf | Formatting and I/O take long, variable time |
| File, SD, flash I/O | Milliseconds, and may block |
| Bus I/O (I2C display) | Blocks for ms (lesson 5) |
| Unbounded loops | No worst-case time |

Two subtle ones:

- **Locks and priority inversion.** If the callback waits for a lock held by the main loop, it cannot proceed until the main loop runs again. But on a bare-metal single-core MCU the main loop cannot run while the callback's interrupt is executing, so a callback that spins on that lock never gets it: a deadlock, and the audio stops. On an RTOS or a general-purpose OS, a high-priority audio thread blocked on a lock held by a low-priority thread is classic **priority inversion**: the holder may be descheduled for far longer than your budget. This is why lesson 7 uses lock-free techniques.
- **Logging.** Even a short `print` may format numbers, copy into a USB or UART buffer, and block when that buffer is full. Set a flag or write a counter, and print from the main loop.

The working pattern:

```
callback(in, out, n):
  read latest params (lock-free)
  pop pending events (lock-free queue)
  for i in 0..n-1:
    out[i] = synth.next_sample()
  if peak > 1.0: clip_flag = true

main loop:
  if clip_flag: log("clipped")
```

## Measuring CPU load

**CPU load** is the fraction of the budget the callback uses: callback time / block period. Measure the **maximum**, not just the average: one slow block is one click.

### Cycle counters

Most Cortex-M3, M4 and M7 chips include a cycle counter (`CYCCNT`, in the DWT debug unit) that counts CPU clock cycles. It is optional in the Armv7-M architecture (the `NOCYCCNT` bit in `DWT_CTRL` says whether it exists), and Cortex-M0/M0+ parts do not have it, so confirm your part has it. It is also off after reset: firmware must set `TRCENA` in `DEMCR` and `CYCCNTENA` in `DWT_CTRL`. Teensy 4's start-up code does both, and its audio library reads the counter as `ARM_DWT_CYCCNT`; PJRC's page notes it counts at the CPU clock (600 MHz). The 32-bit counter wraps every few seconds at these clocks, which unsigned subtraction handles for short intervals. Read it at the start and end of the callback:

```
callback(in, out, n):
  t0 = cycle_count()
  ... process ...
  used = cycle_count() - t0
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

- Pulse **width** = callback time; **period** = block period; width / period = load.
- You see **jitter** and occasional long blocks directly, using persistence or a trigger on pulse width.
- Overhead is one pin write at each end, which is tiny.

### Know the limits of your measurement

- The callback's time varies with what the synth is doing. Measure with the worst realistic case: all voices sounding, every effect on, knobs moving.
- Caches and memory location (lesson 1) change timing; code that is fast in one build may be slower after an unrelated change moves it.
- Library code outside your callback (format conversion, interrupt entry) also uses the budget. Library meters may or may not include it; a GPIO toggle only measures what lies between the toggles.
- Decide a margin, record the measured maximum and the conditions, and re-measure after significant changes.

## Key takeaways
- A DMA interrupt (or a software interrupt it triggers) runs your callback once per block; the main loop runs in the gaps.
- Budget = block size / sample rate: 1 ms for 48 samples at 48 kHz (480,000 cycles at 480 MHz), 2.9 ms for 128 at 44.1 kHz.
- End-to-end latency adds MIDI transmission, waiting for a block, buffering and converter delay, then the interface and DAW. Estimate it, then measure it.
- Never allocate, lock, log, do file or bus I/O, or run unbounded loops in the callback.
- Measure maximum load with a cycle counter or a GPIO toggle on a scope, under worst-case conditions.

## Further reading
- [Real-time audio programming 101: time waits for nothing — Ross Bencina](http://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Getting started: audio (callback rules, CpuLoadMeter) — Electro-Smith](https://docs.daisy.audio/tutorials/_a3_Getting-Started-Audio/)
- [Avoiding callback noise — Electro-Smith](https://docs.daisy.audio/tutorials/eliminating-callback-noise/)
- [Audio library processor usage — PJRC](https://www.pjrc.com/teensy/td_libs_AudioProcessorUsage.html)
- [libDaisy source (daisy_seed.cpp defaults)](https://github.com/electro-smith/libDaisy)
- [Teensy 4 AudioStream.cpp (software interrupt, cycle counting) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/AudioStream.cpp)
- [PCM3060 datasheet (group delay) — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm3060.pdf)
