---
id: emb-codecs-i2s
title: DACs, codecs and audio I/O
level: intermediate
minutes: 15
summary: How samples leave the MCU and become a line-level signal - DACs versus codecs, I2S framing and clocks, sample formats, configuring a codec over I2C, DMA double buffering, and the output stage at a conceptual level.
---

Your oscillator produces a stream of numbers. Somewhere between that stream and the cable into your audio interface, the numbers must become a smoothly varying voltage at the right level. This lesson follows that path: the converter chip, the digital link that feeds it, the memory trick that keeps it fed, and the analogue stage at the end.

## DAC, ADC and codec

- A **DAC** (digital-to-analogue converter) turns sample values into a voltage.
- An **ADC** does the reverse (lesson 3 used the MCU's own ADC for knobs).
- An audio **codec** (coder/decoder) is one chip containing ADC and DAC functions, often stereo, the digital filters that go with them, and often extras such as volume control, a headphone amplifier and input selection.

Many MCUs have a built-in DAC too. The Daisy Seed exposes two 12-bit DAC outputs; they are useful for control voltages or simple signals, but the audio path uses the separate codec, which is designed for low noise and distortion.

Codecs on the boards in this course (checked 2026-10-04):

| Board | Converter | Control |
|---|---|---|
| Daisy Seed Rev 7 | TI PCM3060 | Pins (no I2C) |
| Daisy Seed Rev 5 | WM8731 | I2C |
| Teensy audio adaptor Rev D/D2 | SGTL5000 | I2C |
| Pi DAC+ HAT | TI PCM5122 | I2C |

The Daisy row shows why the project brief insists on naming revisions: the same product name has used three different codecs.

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

The **master** generates BCLK and LRCLK; the other side follows. Normally the MCU is master and the codec is slave.

### Worked numbers: Teensy audio adaptor

PJRC documents the SGTL5000 link: LRCLK 44.1 kHz, BCLK 2.82 MHz (64 bits per LRCLK cycle, of which the upper 16 bits of each 32-bit slot carry data), and MCLK 11.29 MHz. All three clocks come from the Teensy; the SGTL5000's clock pins are inputs.

```python
fs = 44_100
bclk = fs * 2 * 32   # 2 slots of 32 bits
mclk = fs * 256
print(f"BCLK {bclk/1e6:.4f} MHz")
print(f"MCLK {mclk/1e6:.4f} MHz")
```

```
BCLK 2.8224 MHz
MCLK 11.2896 MHz
```

The figures match PJRC's rounded 2.82 MHz and 11.29 MHz: BCLK = 64 × fs, MCLK = 256 × fs.

### Worked example: Daisy Seed Rev 7

The datasheet's codec page says the PCM3060 is in hardware mode, using **24-bit left-justified** format for both ADC and DAC, with both sides as slave. The STM32's SAI1 drives MCLK, bit clock and frame sync. Note: left-justified, not standard I2S. The two formats are close enough that people call both "I2S", which is exactly why you check.

PJRC also warns that I2S wires must be short. These are fast clocks with sharp edges, so long jumper wires cause errors.

## Sample formats

On the wire, codecs use **two's complement integers, MSB first**. The PCM3060 datasheet lists 24-bit I2S, 24-bit left-justified, 24-bit right-justified and 16-bit right-justified, all MSB-first two's complement.

In your code, samples are usually **floats from −1.0 to +1.0**. A library converts at the boundary. libDaisy, for example, converts the codec's 24-bit integers to floats before your callback and back afterwards. The Teensy Audio Library instead works in 16-bit integer blocks throughout.

| Format | Range | Full scale |
|---|---|---|
| 16-bit int | −32,768 … 32,767 | ±32,768 |
| 24-bit int | −8,388,608 … 8,388,607 | ±8,388,608 |
| float | −1.0 … +1.0 | ±1.0 |

Values beyond full scale **clip** at the conversion, so keep your mix within ±1.0.

## Configuring a codec over I2C

A codec with a control port powers up mostly switched off. Before you hear anything, firmware must write a sequence of registers over **I2C** (lesson 5): power up the analogue blocks, choose the digital format and sample rate, route the DAC to the outputs, set volume and unmute.

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

Common failure: the I2S clocks run and the DMA moves data, yet there is silence, because one configuration write failed or used the wrong I2C address. Check the write's acknowledgement (lesson 5) and read registers back when bringing up a new codec.

Hardware-mode codecs such as the Daisy Rev 7's PCM3060 skip this: their configuration is set by pin levels on the board.

## DMA and double buffering

At 48 kHz stereo, the codec needs a new sample pair every 20.8 µs. Interrupting the CPU for every sample would waste much of its time on overhead. Instead, a **DMA** (direct memory access) controller copies samples between memory and the I2S/SAI peripheral without the CPU.

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

Each interrupt tells the CPU that one half has just finished playing and is free to refill. Your audio callback runs from that interrupt and must fill the half before the DMA comes back round to it: one block period. That is the processing deadline of lesson 6.

libDaisy follows this pattern exactly: the SAI's DMA runs in circular mode, the half-complete and complete DMA callbacks both dispatch your audio callback, and the DMA buffer is `blocksize × 2 × 2` words (two halves, two channels). The input side runs the same way in the other direction.

## The output stage and line level

The codec's DAC output is not always ready to drive a cable. A board's output stage may include a coupling capacitor (to block DC), an op-amp buffer, filtering, and sometimes a headphone amplifier. You do not need to design one to start, but you must know what your board's output is designed for.

Signal levels are often quoted as RMS voltage. Standard references:

| Level | RMS voltage |
|---|---|
| Consumer line, −10 dBV | 0.316 V |
| Professional line, +4 dBu | 1.228 V |

What the boards document (checked 2026-10-04):

- **Daisy Seed:** line-level outputs, 0 dBFS at 1 V RMS, output impedance 100 Ω; inputs AC coupled, 3.6 V peak-to-peak, which the datasheet calls "approx. 1Vrms" (a sine of 3.6 V p-p is actually about 1.27 V RMS, so treat that figure as rough).
- **Teensy audio adaptor:** stereo line out and a headphone output, plus line in or mic in.
- **Raspberry Pi DAC+:** line out 0–2 V RMS on phono sockets, plus a headphone amplifier.

**Line, headphone and speaker outputs are not interchangeable.** A line output expects a high-impedance input (an audio interface's line input). A headphone output can drive tens of ohms. A speaker needs a power amplifier. Plugging a speaker into a line output does not work well and can stress the output stage.

> [!warning] Before connecting to your interface
> Keep to low-voltage, battery or USB-powered setups: no mains wiring. Check the interface manual for its input type and maximum level. Start with the interface gain at minimum and the synth's output low, then raise them. Never connect two outputs together.

## Key takeaways
- A codec combines ADC, DAC and filters; check the exact codec for your board revision (the Daisy Seed has used three).
- I2S-style links use BCLK, LRCLK (one frame per sample period) and data, often plus MCLK. Standard I2S and left-justified differ by one bit clock of delay.
- Teensy audio adaptor: LRCLK 44.1 kHz, BCLK = 64 × fs ≈ 2.82 MHz, MCLK = 256 × fs ≈ 11.29 MHz.
- Codecs with control ports need register configuration over I2C before they make sound.
- DMA with a two-half circular buffer lets the CPU fill one half while the other plays; the callback deadline is one block.
- Know your board's output level and type before connecting it to anything.

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
