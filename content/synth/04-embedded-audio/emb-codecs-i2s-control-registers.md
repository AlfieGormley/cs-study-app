---
id: emb-codecs-i2s-control-registers
sourceLesson: emb-codecs-i2s
title: "Configure the codec before audio"
level: intermediate
minutes: 2
summary: "The sample link and configuration link do different jobs."
---

## Configuring a codec over I2C

A software-controlled codec may need explicit power-up and routing configuration. On the SGTL5000, firmware writes a sequence of registers over **I2C** (the serial-bus units) to power up the analogue blocks, choose the digital format and sample rate, route the DAC to the outputs, set volume and unmute.

On the Teensy audio adaptor, the SGTL5000's control pins are SDA and SCL on Teensy pins 18 and 19; the Teensy Audio Library's control object performs the register sequence when you call its enable function.

```
codec_init():
  i2c_write(CODEC, POWER, analog_on)
  i2c_write(CODEC, FORMAT, i2s_16bit)
  i2c_write(CODEC, ROUTE, dac_to_lineout)
  i2c_write(CODEC, VOLUME, safe_level)
  i2c_write(CODEC, MUTE, off)
```

(Register names are illustrative; real ones come from the codec datasheet.)

Common failure: the I2S clocks run and the DMA moves data, yet there is silence, because one configuration write failed or used the wrong I2C address. Check the write's acknowledgement (the serial-bus units) and read registers back when bringing up a new codec.

Hardware-mode codecs such as the Daisy Rev 7's PCM3060 skip this: their configuration is set by pin levels on the board.

## Key takeaways
- The sample link and configuration link do different jobs.
- Check addresses, acknowledgements and documented readback when clocks run but sound is absent.

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
