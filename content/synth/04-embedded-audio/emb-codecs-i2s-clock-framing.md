---
id: emb-codecs-i2s-clock-framing
sourceLesson: emb-codecs-i2s
title: "Read serial audio clocks and format"
level: intermediate
minutes: 4
summary: "One stereo frame uses one word-clock period; slot widths set the bit clock."
---

## I2S: the digital audio link

The MCU sends samples to the codec over a synchronous serial link, usually **I2S** (Inter-IC Sound, defined by Philips) or a close relative. On STM32 parts the peripheral is called **SAI** (serial audio interface); on Teensy it is the I2S port.

Four signals are typical:

| Signal | Also called | Job |
|---|---|---|
| BCLK | SCK, bit clock | One pulse per data bit |
| LRCLK | WS, FS, word clock | Left/right frame |
| SD | DIN / DOUT | The sample bits |
| MCLK | SCKI, master clock | Codec's internal clock |

```
LRCLK ___________|‾‾‾‾‾‾‾‾‾‾‾‾‾|_____
      left word    right word
BCLK  |‾|_|‾|_|‾|_|‾|_|‾|_|‾|_|‾|_|‾|
SD     x M . . . L x M . . . L x
         ^MSB first  ^LSB
```

- **LRCLK** runs at the sample rate. One full period carries one left and one right sample (a **frame**). In standard I2S, LRCLK low means left.
- **BCLK** clocks each bit. Bits go MSB first.
- **Standard I2S** puts the MSB one BCLK *after* the LRCLK edge. **Left-justified** puts it *on* the edge. Get the format wrong and you hear loud distorted garbage, or audio shifted by one bit.
- **MCLK** is a faster clock (a fixed multiple of the sample rate, such as 256×) that many codecs need to run their converters.

The **audio clock master** generates BCLK and LRCLK; the **audio clock follower** accepts them. Manufacturer manuals also call these master and slave. Normally the MCU is master and the codec is slave.

### Worked numbers: Teensy audio adaptor

PJRC documents the SGTL5000 link: LRCLK 44.1 kHz, BCLK 2.82 MHz (64 bits per LRCLK cycle, of which the upper 16 bits of each 32-bit slot carry data), and MCLK 11.29 MHz. All three clocks come from the Teensy; the SGTL5000's clock pins are inputs.

The **slot width**, not just the number of meaningful sample bits, determines the bit-clock requirement. Two 32-bit slots still need 64 bit clocks per stereo frame when only 16 bits in each slot carry sample data. At 44.1 kHz that is about 2.82 MHz. The documented master clock is about 11.29 MHz.

A format with two 16-bit slots uses half as many bit clocks per frame. Changing sample precision without changing the slots does not change the bit clock. Read the permitted slot widths and master-clock ratios from the codec and peripheral documentation; they are not universal constants.

### Worked example: Daisy Seed Rev 7

The datasheet's codec page says the PCM3060 is in hardware mode, using **24-bit left-justified** format for both ADC and DAC, with both sides as slave. The STM32's SAI1 drives MCLK, bit clock and frame sync. Note: left-justified, not standard I2S. The two formats are close enough that people call both "I2S", which is exactly why you check.

PJRC also warns that I2S wires must be short. These are fast clocks with sharp edges, so long jumper wires cause errors.

## Key takeaways
- One stereo frame uses one word-clock period; slot widths set the bit clock.
- Standard I2S delays the MSB one bit clock; left-justified does not.

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
