---
id: snd-sampling-time-memory
title: Sample timing, block deadlines and memory
level: intermediate
minutes: 5
summary: Interpret sample instants and budget processing time, buffer memory and audio data rate.
sourceLesson: snd-sampling
---

A digital synth never handles a continuous wave. It handles a stream of numbers, one every 1/48,000 of a second or so, and a converter turns them into a voltage. This lesson is about what those numbers are, how precise they need to be, and what goes wrong at the edges.

Two separate settings decide the quality of a digital signal. **Sample rate** sets how *often* you measure. **Bit depth** sets how *finely* each measurement is recorded. Neither of them is the playback volume, which is decided by the numbers' size relative to full scale and by whatever amplifier follows the converter.



## Discrete-time signals

**Sampling a signal** means measuring a continuous signal at evenly spaced instants. The spacing between instants is the sample period, and sample number n is simply the signal's value at n sample periods:

```formula
T = 1 / fs
x[n] = x(n × T)
T = 1 / 48000 s ≈ 20.8 µs
where
T: the sample period, the time between one sample and the next, in seconds (s)
fs: the sample rate, in samples per second (equivalently hertz, Hz); here 48,000
x(t): the continuous signal: its value at any time t, in seconds
x[n]: sample number n, a single number; square brackets mean "the sample with index n"
n: the sample index, a whole number 0, 1, 2, …
s: seconds
µs: microseconds, millionths of a second
≈: approximately equal to (rounded)
In words: take the continuous signal's value every T seconds; the nth sample is its value at time n × T. At 48 kHz the samples are about 20.8 microseconds apart.
```

Picture each sample as a lollipop: a value at an instant, with nothing defined in between.

```diagram
  |   o
  |   |  o
  | o |  |
  | | |  |     time ->
--+-+-+--+--+--+--
  |          |  |
  |          |  o
  |          o
```

A sample is *not* a little rectangle of constant value. The DAC's job (explained in the reconstruction unit) is to rebuild a smooth signal that passes through every lollipop.

Common sample rates:

| Rate | Typical use |
|---|---|
| 44.1 kHz | CD audio |
| 48 kHz | Video, most pro audio and audio hardware |
| 96 kHz | High-resolution recording; some synth internals |

The sample rate fixes the **highest frequency** you can represent: half the sample rate, as the Nyquist-limit unit explains. 48 kHz covers up to 24 kHz, above the roughly 20 kHz limit of hearing. Higher rates mostly buy room for processing that creates high frequencies (distortion, sharp waveforms), not extra audible treble.

It also sets your **time budget**. Synths process audio in blocks (a fixed number of samples handled in one go), and the hardware plays a block in a fixed time:

```formula
t_b = N_b / fs
t_b = 48 / 48000 s
t_b = 0.001 s = 1 ms
where
t_b: the duration of one block, in seconds (s)
N_b: the block size, in samples; here 48
fs: the sample rate, in samples per second; here 48,000
s: seconds
ms: milliseconds, thousandths of a second
In words: a block lasts its number of samples divided by the sample rate, so 48 samples at 48 kHz is 1 ms.
```

All the work for a block must finish in less time than that, every time. If it doesn't, the hardware runs out of samples and you hear a click or dropout.

## How much data is that?

The numbers add up quickly, which matters on a microcontroller:

```formula
M = fs × t × B × C
M = 48000 × 1 × 4 × 1 = 192000 bytes
R = fs × b × C
R = 48000 × 24 × 2 = 2304000 bit/s
where
M: the memory needed, in bytes
R: the data rate, in bits per second (bit/s)
fs: the sample rate, in samples per second; here 48,000
t: the length of audio, in seconds; here 1
B: bytes per sample; 4 for float32
b: bits per sample; here 24
C: the number of channels; 1 for mono, 2 for stereo
bytes: units of 8 bits
bit/s: bits per second
In words: multiply samples per second by seconds, by the size of each sample, by the number of channels.
```

- One second of mono float32 at 48 kHz is 192,000 bytes, about 192 kB (kilobytes).
- Stereo 24-bit audio data at 48 kHz is 2.304 Mbit/s (megabits per second). On an I²S bus, 24-bit samples often travel in 32-bit slots, so the bit clock runs at 48,000 × 32 × 2 = 3.072 MHz.

A delay effect with a two-second buffer needs 48,000 × 2 × 4 = 384,000 bytes (384 kB) per channel in float32. Check this against your board's RAM before designing features.

## Pitfalls

- **Confusing the three settings.** Sample rate (how often), bit depth (how finely), level (how big relative to full scale). Turning a synth down in software doesn't change its bit depth, but very quiet *integer* signals do use fewer effective bits.

## Key takeaways

- Sample rate determines the spacing of sample instants and the duration of each processing block.
- Finish each block before the hardware consumes it or audio can drop out.
- Buffer memory scales with duration, sample rate, bytes per sample and channel count.

## Further reading

- [Sampling (signal processing) — Wikipedia](https://en.wikipedia.org/wiki/Sampling_(signal_processing))
