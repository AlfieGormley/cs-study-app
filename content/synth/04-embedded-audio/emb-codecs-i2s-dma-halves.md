---
id: emb-codecs-i2s-dma-halves
sourceLesson: emb-codecs-i2s
title: "Keep audio fed with DMA"
level: intermediate
minutes: 3
summary: "The CPU fills a released buffer half while DMA transfers the other."
---

## Give the CPU one block at a time

At 48 kHz stereo, the codec consumes a left/right sample pair about every 20.8 microseconds. A **DMA** controller transfers those samples between memory and the I2S/SAI peripheral, saving the CPU from copying each sample individually. The CPU still computes the samples and services block boundaries.

The usual pattern is a circular sample buffer split into two halves:

```diagram
DMA plays half A -> CPU prepares half B
DMA plays half B -> CPU prepares half A
```

A half-complete or complete interrupt identifies the half that DMA has just finished using. The callback fills that released half while the other plays. It must finish before DMA returns to the half: **one block period**, including conversion and interrupt overhead.

For 48 samples per channel at 48 kHz, each half lasts 1 ms. Missing that deadline can make DMA play stale or partially written samples. Double buffering separates ownership for a limited interval; it does not create spare time when computation overruns.

> [!analogy] Real-world analogy: Two serving trays
> While guests take food from one tray, a cook refills the other, then the trays swap roles.
>
> **How it maps:** DMA consumes one buffer half while the CPU prepares the released half. The swap determines when the refill must be ready.
>
> **Where it stops:** Audio hardware cannot politely wait for the cook. A late or conflicting write can corrupt playback, and memory placement and cache rules still require platform-specific handling.

The checked libDaisy source dispatches the callback from both DMA boundary notifications. Its stereo circular buffer contains two halves, each with a left and right value for every sample frame: a 48-frame half therefore gives 192 sample words across the whole buffer. The input side transfers in the opposite direction.

On real hardware, use memory accessible to that DMA engine and follow the library's cache and buffer-placement requirements. A host simulation of alternating halves does not verify those requirements.

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
