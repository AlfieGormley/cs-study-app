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

You can derive all three from the sample rate. LRCLK completes one cycle per frame, so it runs at the sample rate. BCLK must tick once for every bit in the frame, and MCLK is a fixed multiple the codec asks for:

```formula
LRCLK = f_s = 44100 Hz
BCLK = 2 × 32 × f_s = 64 × f_s
BCLK = 64 × 44100 Hz ≈ 2.8224 MHz
MCLK = 256 × f_s
MCLK = 256 × 44100 Hz ≈ 11.2896 MHz
where
LRCLK: the left/right (word) clock frequency, in hertz (Hz)
BCLK: the bit clock frequency, in hertz (Hz): one pulse per bit sent
MCLK: the master clock frequency the codec uses internally, in hertz (Hz)
f_s: the sample rate, samples per second per channel, in hertz (Hz); here 44.1 kHz
Hz: hertz, cycles per second
MHz: megahertz, one million hertz
≈: approximately equal to
In words: each frame has two 32-bit slots (left and right), so the bit clock runs 64 times faster than the sample rate; this codec's master clock runs 256 times faster.
```

The same numbers from Python:

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

The figures match PJRC's rounded 2.82 MHz and 11.29 MHz. The multipliers depend on the format: a link that sends only 16 bits per slot needs a BCLK of 32 times the sample rate, and some codecs accept other MCLK ratios, so read them from the datasheet.

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

The integer full scale comes from the bit depth. One bit is the sign, so the remaining bits count the size, and the library scales a float by that amount:

```formula
FS = 2^(B − 1)
FS = 2^(24 − 1) = 8388608
s_int = x × FS
s_int = 0.5 × 8388608 = 4194304
where
FS: the integer full scale, the size of the most negative code, with no unit
B: the bit depth of the integer format; here 24 (16 for the Teensy library)
2^(B − 1): 2 raised to the power B − 1
s_int: the integer sample sent to the codec, with no unit
x: the float sample from your code, from −1.0 to +1.0
In words: a 24-bit sample runs from −8,388,608 to 8,388,607, so a float of 0.5 becomes about 4.2 million. A float above 1.0 would need a code that does not exist.
```

The top positive code is one less than full scale (8,388,607), because zero takes one of the non-negative codes; libraries clamp +1.0 to it. Values beyond full scale **clip** at the conversion, so keep your mix within ±1.0.

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
In words: 48,000 frames a second leaves only about 21 millionths of a second for each one.
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

Each interrupt tells the CPU that one half has just finished playing and is free to refill. Your audio callback runs from that interrupt and must fill the half before the DMA comes back round to it: one block period. That is the processing deadline of lesson 6:

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

libDaisy follows this pattern exactly: the SAI's DMA runs in circular mode, the half-complete and complete DMA callbacks both dispatch your audio callback, and the DMA buffer is `blocksize × 2 × 2` words:

```formula
W = N × 2 × 2
W = 48 × 2 × 2 = 192
where
W: the length of the circular DMA buffer, in words (one word holds one sample)
N: the block size (libDaisy's `blocksize`), samples per channel per half; here 48
In words: two halves, each holding two channels of N samples, so 48-sample blocks need a 192-word buffer.
```

The input side runs the same way in the other direction.

## The output stage and line level

The codec's DAC output is not always ready to drive a cable. A board's output stage may include a coupling capacitor (to block DC), an op-amp buffer, filtering, and sometimes a headphone amplifier. You do not need to design one to start, but you must know what your board's output is designed for.

Signal levels are often quoted as RMS voltage, the steady (DC) voltage that would deliver the same power. Standard references:

| Level | RMS voltage |
|---|---|
| Consumer line, −10 dBV | 0.316 V |
| Professional line, +4 dBu | 1.228 V |

Those voltages come from the decibel definition: a level in dB is 20 times the base-10 logarithm of a voltage ratio, measured against a fixed reference voltage. Turned around, it gives the voltage for any level:

```formula
V_rms = V_0 × 10^(L / 20)
V_rms = 1 V × 10^(−10 / 20) ≈ 0.316 V
V_rms = 0.775 V × 10^(4 / 20) ≈ 1.228 V
where
V_rms: the RMS voltage of the signal, in volts (V)
V_0: the reference voltage: 1 V for dBV, 0.775 V (√0.6, more exactly 0.7746 V) for dBu
L: the level in decibels relative to that reference (dBV or dBu); here −10 and +4
10^(L / 20): 10 raised to the power L / 20
V: volt, the unit of voltage
≈: approximately equal to
In words: every 20 dB is a factor of 10 in voltage. Consumer line level is about a third of a volt, professional line level a little over 1.2 V.
```

What the boards document (checked 2026-10-04):

- **Daisy Seed:** line-level outputs, 0 dBFS at 1 V RMS, output impedance 100 Ω; inputs AC coupled, 3.6 V peak-to-peak, which the datasheet calls "approx. 1Vrms" (a sine of 3.6 V p-p is actually about 1.27 V RMS, so treat that figure as rough; see the conversion below).
- **Teensy audio adaptor:** stereo line out and a headphone output, plus line in or mic in.
- **Raspberry Pi DAC+:** line out 0–2 V RMS on phono sockets, plus a headphone amplifier.

For a sine wave, peak-to-peak and RMS voltages are related by a fixed factor, which is how the Daisy figure above was checked:

```formula
V_rms = V_pp / (2 × √2)
V_rms = 3.6 V / (2 × 1.414) ≈ 1.27 V
where
V_rms: the RMS (root-mean-square) voltage of the sine, in volts (V)
V_pp: the peak-to-peak voltage, from the lowest point of the wave to the highest, in volts (V); here 3.6 V
√2: the square root of 2, about 1.414
V: volt, the unit of voltage
≈: approximately equal to
In words: halve the peak-to-peak voltage to get the peak, then divide by about 1.414 to get the RMS value. This holds only for sine waves; other shapes have other ratios.
```

**Line, headphone and speaker outputs are not interchangeable.** A line output expects a high-impedance input (an audio interface's line input). A headphone output can drive tens of ohms. A speaker needs a power amplifier. Plugging a speaker into a line output does not work well and can stress the output stage.

> [!warning] Before connecting to your interface
> Keep to low-voltage, battery or USB-powered setups: no mains wiring. Check the interface manual for its input type and maximum level. Start with the interface gain at minimum and the synth's output low, then raise them. Never connect two outputs together.

## Key takeaways
- A codec combines ADC, DAC and filters; check the exact codec for your board revision (the Daisy Seed has used three).
- I2S-style links use BCLK, LRCLK (one frame per sample period) and data, often plus MCLK. Standard I2S and left-justified differ by one bit clock of delay.
- Teensy audio adaptor: LRCLK at the 44.1 kHz sample rate, BCLK at 64 times that (about 2.82 MHz), MCLK at 256 times (about 11.29 MHz).
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
