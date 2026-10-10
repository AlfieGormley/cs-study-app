---
id: snd-sampling
title: Sampling and quantisation
level: intermediate
minutes: 18
summary: How a continuous signal becomes a list of numbers. Sample rate, bit depth, quantisation noise and the 6 dB-per-bit rule, integer vs floating-point samples, and the −1..1 convention.
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

A sample is *not* a little rectangle of constant value. The DAC's job (next lesson) is to rebuild a smooth signal that passes through every lollipop.

Common sample rates:

| Rate | Typical use |
|---|---|
| 44.1 kHz | CD audio |
| 48 kHz | Video, most pro audio and audio hardware |
| 96 kHz | High-resolution recording; some synth internals |

The sample rate fixes the **highest frequency** you can represent: half the sample rate, as lesson 4 explains. 48 kHz covers up to 24 kHz, above the roughly 20 kHz limit of hearing. Higher rates mostly buy room for processing that creates high frequencies (distortion, sharp waveforms), not extra audible treble.

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

## Bit depth and quantisation

Each sample must be stored with finite precision. Every extra bit doubles the number of patterns, so with **N bits** a signed integer sample has this many possible values:

```formula
L = 2^N
L = 2^16 = 65536
where
L: the number of distinct levels (values) a sample can take
N: the bit depth, the number of bits per sample; here 16
2^N: 2 raised to the power N (N copies of 2 multiplied together)
In words: each bit doubles the number of levels, so 16 bits give 65,536 of them.
```

| Bits | Levels | Integer range |
|---|---|---|
| 8 | 256 | −128 to 127 |
| 16 | 65,536 | −32,768 to 32,767 |
| 24 | 16,777,216 | −8,388,608 to 8,388,607 |

Rounding the true value to the nearest level is **quantisation**. The levels are evenly spaced, so the step size is the width of the range divided by the number of levels, and rounding to the nearest level is wrong by at most half a step either way:

```formula
Δ = 2 / 2^N
Δ = 2 / 65536 ≈ 0.0000305
e_max = Δ / 2 ≈ 0.0000153
where
Δ: delta, the quantisation step size: the gap between neighbouring levels, in full-scale units
2: the width of the range from −1 to +1 (full scale)
N: the bit depth, in bits; here 16
e_max: the largest possible rounding error when rounding to the nearest level
≈: approximately equal to (rounded)
In words: 16 bits split the range −1 to +1 into steps of about 0.00003, and rounding is never more than half a step out.
```

This assumes the signal stays inside full scale; a value beyond the top or bottom level is clipped, and its error can be much larger.

For a busy signal much larger than one step, the error behaves like a small random noise added to the signal: **quantisation noise**. How far that noise sits below the signal is the **SQNR**, the signal-to-quantisation-noise ratio, measured in decibels (dB, a logarithmic scale for ratios that lesson 5 explains). The standard result, for a full-scale sine wave, is:

```formula
SQNR ≈ 6.02 × N + 1.76 dB
SQNR ≈ 6.02 × 16 + 1.76 dB
SQNR ≈ 98.1 dB
where
SQNR: signal-to-quantisation-noise ratio: the RMS (average) level of a full-scale sine compared with the RMS level of the rounding noise, in decibels
N: the bit depth, in bits; here 16
dB: decibels; every 6 dB is roughly a factor of 2 in amplitude
≈: approximately equal to (the formula is an approximation, and the result is rounded)
In words: each bit adds about 6 dB of distance between a full-scale sine and the quantisation noise, plus a constant 1.76 dB, so 16 bits give about 98 dB.
```

**Each extra bit adds about 6 dB**, because it halves the step size and halving an amplitude is −6.02 dB. 16 bits gives about 98 dB; 24 bits about 146 dB.

Where do the two numbers come from? The rounding error is spread evenly across one step, which gives it a predictable RMS (root-mean-square, a kind of average size; lesson 5). A full-scale sine spans all the steps, so its peak is half of that span, and a sine's RMS is its peak divided by about 1.414. Putting those together:

```formula
S = (2^N × Δ / 2) / √2
E = Δ / √12
S / E = 2^N × √1.5
SQNR = 20 × log_10(S / E)
SQNR = 20 × N × log_10(2)
     + 20 × log_10(√1.5)
SQNR ≈ 6.02 × N + 1.76 dB
where
S: the RMS size of the full-scale sine, in full-scale units (the same units as Δ)
SQNR: the signal-to-quantisation-noise ratio, in decibels (dB)
E: the RMS size of the quantisation error, in the same units, assuming it is spread evenly within ±Δ/2
Δ: delta, the quantisation step size
N: the bit depth, in bits
√: square root
log_10: the base-10 logarithm, used by the decibel scale; 20 × log_10 of an amplitude ratio gives decibels
dB: decibels
≈: approximately equal to (rounded)
In words: the signal-to-noise ratio is 2^N times a constant; in decibels, the 2^N becomes 6.02 dB per bit and the constant becomes 1.76 dB.
```

The derivation shows the assumptions: a sine that fills full scale without overloading, and an error that is evenly spread and unrelated to the signal. A quieter signal gets proportionally less SQNR, and very coarse quantisation breaks the second assumption.

You can check this in a few lines:

```python
import numpy as np

fs = 48_000
n = np.arange(fs)                 # 1 second
x = 0.999 * np.sin(2*np.pi*997*n/fs)

def quantise(x, bits):
    scale = 2 ** (bits - 1)  # 16 -> 32768
    q = np.round(x * scale)
    q = np.clip(q, -scale, scale - 1)
    return q / scale

for bits in (4, 8, 12, 16):
    err = quantise(x, bits) - x
    snr = 10*np.log10(np.mean(x**2)
                      / np.mean(err**2))
    pred = 6.02*bits + 1.76
    print(f"{bits:>2} bits: {snr:5.1f} dB"
          f" (formula {pred:5.1f})")
```

```text
 4 bits:  23.3 dB (formula  25.8)
 8 bits:  49.3 dB (formula  49.9)
12 bits:  74.0 dB (formula  74.0)
16 bits:  98.1 dB (formula  98.1)
```

At 12 and 16 bits the formula agrees closely. At 4 bits this example also **overloads the positive endpoint**: its largest code is 7/8, below the sine's 0.999 peak. That clipping contributes substantial error. In addition, the uniform, signal-independent error model is only an approximation; low-resolution periodic quantisation can produce distortion rather than a gentle hiss.

> [!note] Why 997 Hz?
> Test tones are often slightly "odd" frequencies like 997 Hz rather than 1000 Hz. With 1000 Hz at 48 kHz, each cycle is exactly 48 samples, so the same few quantisation errors repeat every cycle and pile up at harmonic frequencies. An odd frequency spreads them out.

### Dither

The same problem returns for **very quiet signals**, even at 16 bits. A sine whose amplitude is under half a step rounds to zero every time and vanishes completely. A fade-out turns gritty in its last few bits.

**Dither** fixes this by adding a tiny amount of random noise (about one step in size) *before* quantising. The error becomes truly random and unrelated to the signal: you trade a little extra hiss for no distortion, and quiet details survive inside the noise. Dither matters whenever you **reduce** bit depth, such as when exporting 16-bit files. Inside a 32-bit float synth it's rarely needed.

### Real converters

A "24-bit" converter outputs 24-bit words, but its analogue noise floor is far above the theoretical 146 dB. Datasheet dynamic range for common audio converters is roughly 95–115 dB: for example, 99 dB for TI's PCM1808 ADC and 112 dB for its PCM5102A DAC. Flagship DAC chips quote around 130 dB (127–132 dB for the PCM1792A). A finished board usually does somewhat worse than the chip alone, so check the datasheet and measure. 24 bits gives a comfortable margin so that converter noise, not quantisation, sets the floor.

## The −1..1 convention and floating point

Inside most audio software, samples are **floating-point numbers where ±1.0 means full scale**. The converter's maximum output corresponds to 1.0. This convention lets the same code work whatever bit depth the hardware uses.

Why floats internally?

- **Headroom.** A float can hold 3.7 or −12.0 without trouble. Mixing several voices can exceed 1.0 mid-chain and be scaled down later with nothing lost. Integers would overflow or clip.
- **Resolution where it matters.** A 32-bit float has a 24-bit significand plus an exponent. Quiet signals keep their full relative precision, because the exponent scales with the value.
- **Simple maths.** Gain is a multiply; mixing is an add.

Integer and **fixed-point** formats still matter at the edges: WAV files, converter interfaces, and microcontrollers without a floating-point unit. The conversion at the boundary is where bugs live:

```python
import numpy as np
x = np.array([0.5, -0.25, 1.0, -1.0, 1.7])
r = np.clip(np.round(x * 32767),
            -32768, 32767)
i16 = r.astype(np.int16)
print(i16)
y = i16 / 32768
print(np.round(y, 5).tolist())
```

```text
[ 16384  -8192  32767 -32767  32767]
[0.5, -0.25, 0.99997, -0.99997, 0.99997]
```

Three things to notice:

1. **1.7 was clipped** to 32767. Over-range floats must be clipped at conversion, never cast directly. In C and C++, converting a float to an integer type that can't hold its value is undefined behaviour. In practice you may get a wrapped value or, on x86, the "integer indefinite" value −2,147,483,648: either way, a loud crack. NumPy is no safer: in testing, `np.array([1.7 * 32767]).astype(np.int16)` gave −9833, silently.
2. **Asymmetry.** Integers run from −32768 to +32767, so full scale isn't symmetric. Libraries choose 32767 or 32768 as the scale factor.
3. **Inconsistent scale factors.** Here the code multiplied by 32767 but divided by 32768, so a round trip shrinks the signal very slightly. Pick one convention and use it both ways.

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
- **Casting instead of clipping** at float-to-integer conversion.
- **Truncating instead of rounding.** Truncation toward zero gives sign-dependent error approaching a full step; it need not add DC to a symmetric signal. Rounding downward instead has a negative bias, averaging about half a step under the uniform-error model. Nearest rounding limits error to half a step away from overload.
- **Denormals.** Float values extremely close to zero (subnormals, or denormals) are much slower to process on some processors: on x86, an operation on one can cost around 100 extra clock cycles. Decaying filters and reverbs can produce them. The usual fixes are to switch on the CPU's flush-to-zero (and denormals-are-zero) mode for the audio thread, as many audio frameworks do, or to add a tiny offset or noise so the values never get that small.

## Key takeaways
- A sample is the signal's value at one instant. Sample rate sets the frequency limit and the time budget per block.
- Each bit doubles the number of levels; quantisation noise for a full-scale sine is about 6 dB per bit below it (98 dB at 16 bits, 146 dB at 24).
- The noise model breaks down for very few bits or very quiet signals; dither restores it when reducing bit depth.
- Internally, use floats with ±1.0 = full scale. Clip (don't cast) when converting to integers, and use a consistent scale factor.
- Sample rate, bit depth and playback level are three different things.

## Further reading
- [Quantization (signal processing) — Wikipedia](https://en.wikipedia.org/wiki/Quantization_(signal_processing))
- [Audio bit depth — Wikipedia](https://en.wikipedia.org/wiki/Audio_bit_depth)
- [Sampling (signal processing) — Wikipedia](https://en.wikipedia.org/wiki/Sampling_(signal_processing))
- [Dither — Wikipedia](https://en.wikipedia.org/wiki/Dither)
- [Taking The Mystery Out of the Infamous Formula "SNR = 6.02N + 1.76dB" — Analog Devices MT-001](https://www.analog.com/media/en/training-seminars/tutorials/MT-001.pdf)
- [Single-precision floating-point format — Wikipedia](https://en.wikipedia.org/wiki/Single-precision_floating-point_format)
- [Subnormal number — Wikipedia](https://en.wikipedia.org/wiki/Subnormal_number)
- [PCM5102A audio DAC datasheet — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm5102a.pdf)
