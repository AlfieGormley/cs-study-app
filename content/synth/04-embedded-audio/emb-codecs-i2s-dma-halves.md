---
id: emb-codecs-i2s-dma-halves
sourceLesson: emb-codecs-i2s
title: "Keep audio fed with DMA"
level: intermediate
minutes: 3
summary: "The CPU fills a released buffer half while DMA transfers the other."
---

## DMA and double buffering

At 48 kHz stereo, the codec needs a new sample pair every 20.8 µs:

```formula
T_s = 1 / f_s
T_s = 1 / 48000 Hz ≈ 0.0000208 s = 20.8 µs
where
T_s: the sample period, the time between one sample frame and the next, in seconds (s)
f_s: the sample rate, in hertz (Hz); here 48 kHz = 48,000 Hz
Hz: hertz, cycles (here samples) per second
s: second
µs: microsecond, one millionth of a second
≈: approximately equal to
In words: 48,000 stereo sample frames each second leaves only about 21 millionths of a second for each one.
```

Interrupting the CPU for every sample would waste much of its time on overhead. Instead, a **DMA** (direct memory access) controller copies samples between memory and the I2S/SAI peripheral without the CPU.

The standard pattern is a **circular buffer split in two halves** (double buffering, sometimes called ping-pong):

```
      buffer in memory
+---------------+---------------+
|    half A     |    half B     |
+---------------+---------------+
 DMA reads A --> codec
 (CPU is filling B)
 "half complete" interrupt:
   DMA moves on to B,
   CPU now fills A
 "complete" interrupt:
   DMA wraps to A, CPU fills B
```

Each interrupt tells the CPU that one half has just finished playing and is free to refill. Your audio callback runs from that interrupt and must fill the half before the DMA comes back round to it: one block period. That is the processing deadline of the real-time audio units:

```formula
T_block = N / f_s
T_block = 48 / 48000 Hz = 0.001 s = 1 ms
where
T_block: the block period, the time the DMA takes to play one half of the buffer, in seconds (s)
N: the block size, samples per channel in each half; here 48, libDaisy's default
f_s: the sample rate, in hertz (Hz); here 48 kHz
Hz: hertz, samples per second
s: second
ms: millisecond, one thousandth of a second
In words: a half holding 48 samples per channel plays for 1 ms, so the callback has 1 ms to refill the other half.
```

libDaisy follows this pattern exactly: the SAI's DMA runs in circular mode, the half-complete and complete DMA callbacks both dispatch your audio callback, and the circular audio-transfer buffer is `blocksize × 2 × 2` words:

```formula
W = N × 2 × 2
W = 48 × 2 × 2 = 192
where
W: the length of the circular DMA buffer, in words (one word holds one sample)
N: the block size (libDaisy's `blocksize`), samples per channel per half; here 48
In words: two halves, each holding two channels of N samples, so 48-sample blocks need a 192-word buffer.
```

The input side runs the same way in the other direction.

## Key takeaways
- The CPU fills a released buffer half while DMA transfers the other.
- The next reuse supplies the deadline; include conversion and interrupt overhead.

## Further reading
- [Audio adaptor boards for Teensy — PJRC](https://www.pjrc.com/store/teensy3_audio.html)
- [Daisy Seed datasheet v1.2.0 (codec and output pages) — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [PCM3060 datasheet — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm3060.pdf)
- [Getting started: audio — Electro-Smith](https://docs.daisy.audio/tutorials/_a3_Getting-Started-Audio/)
- [Raspberry Pi audio boards overview — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/introduction.adoc)
- [Raspberry Pi DAC+ (PCM5122) — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/dac_plus.adoc)
- [I²S — Wikipedia](https://en.wikipedia.org/wiki/I%C2%B2S)
- [Line level — Wikipedia](https://en.wikipedia.org/wiki/Line_level)
- [Direct memory access — Wikipedia](https://en.wikipedia.org/wiki/Direct_memory_access)
