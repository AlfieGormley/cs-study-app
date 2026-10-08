---
id: snd-waves
title: Sound as a wave
level: basic
minutes: 15
summary: Amplitude, frequency, period, wavelength and phase; the sine wave formula; and the two numbers every oscillator needs, samples per period and phase increment.
---

Every sound your synth makes ends up as a speaker cone pushing air back and forth. The air pressure at your ear rises and falls around normal atmospheric pressure, and your ear turns that pattern into what you hear.

Inside the synth there is no air. There is first a sequence of numbers, then a voltage on a wire. The vocabulary is the same at every stage, though. A *wave* is a quantity (pressure, voltage, or a number in memory) that changes over time, and we describe it by how big the change is, how often it repeats and where in its cycle it is.

This lesson sets up that vocabulary and the one formula you'll use constantly: the sine wave.

## The four basic measurements

Picture one repeating cycle of a wave plotted against time:

```diagram
 +A |    .-'''-.
    |  .'       '.
  0 +-'-----------'.-----------.-> t
    |               '.       .'
 -A |                 '-...-'
    |<------- one period T ----->|
```

- **Amplitude (A)** is how far the wave swings from its centre line. In air that's a pressure difference; in a circuit it's volts; in software it's a number, conventionally between −1 and +1. Bigger amplitude sounds louder, though loudness perception is more complicated than amplitude alone.
- **Period (T)** is the time one full cycle takes, in seconds.
- **Frequency (f)** is how many cycles happen per second, in hertz (Hz). It's the reciprocal of the period (one divided by the period).
- **Wavelength (λ)** is the *distance* one cycle covers as it travels through a medium such as air.

Frequency and period are two views of the same thing: if you know how long one cycle takes, you know how many fit in a second.

```formula
f = 1 / T
f = 1 / 0.00227 s
f ≈ 440 Hz
where
f: the frequency, in hertz (Hz): how many complete cycles happen each second
T: the period, the time one complete cycle takes, in seconds (s); here about 0.00227 s (2.27 ms)
s: seconds
Hz: hertz, the unit of frequency: one cycle per second
≈: approximately equal to (the numbers are rounded)
In words: frequency is one divided by the period, so a shorter cycle means a higher frequency. Halve the period and the frequency doubles.
```

Turned round, the period is one divided by the frequency: a 440 Hz wave has a period of 1/440 s, about 2.27 milliseconds (ms). The relationship is exact for any repeating wave; it only stops being meaningful for sounds that don't repeat, such as noise.

Wavelength needs one more ingredient, the speed at which the wave travels. In the time of one period, the wave moves forward by one wavelength:

```formula
λ = c / f
λ = 343 / 440
λ ≈ 0.78 m
where
λ: lambda, the wavelength: the distance one cycle occupies as it travels, in metres (m)
c: the speed of sound in the medium, in metres per second (m/s); about 343 m/s in dry air at 20 °C
f: the frequency of the wave, in hertz (Hz)
m: metres
m/s: metres per second
Hz: hertz, cycles per second
≈: approximately equal to (rounded)
In words: the wavelength is the speed of sound divided by the frequency, so higher notes have shorter wavelengths. A 440 Hz tone in air has a wavelength of about 0.78 m.
```

The speed of sound depends on the medium and its temperature (it is faster in warmer air and much faster in water or steel), so λ is only defined for sound actually travelling through something.

Wavelength matters for room acoustics and speaker design (why bass travels through walls, why rooms have resonances). Inside a synth it barely matters at all: your signals live as samples and voltages, where only time and frequency count. Don't confuse *wavelength* with *period*. One is metres, the other seconds.

Human hearing is usually quoted as roughly 20 Hz to 20 kHz (20,000 Hz). The top end falls with age, and that range is a rule of thumb rather than a hard limit. In air, those frequencies have wavelengths of roughly 17 m down to 1.7 cm.

## Phase and radians

The **phase of a wave** says *where in its cycle* it is at a given moment. You can measure it in fractions of a cycle (0 to 1), degrees (0° to 360°), or **radians** (0 to 2π). Maths libraries use radians, so get comfortable with them.

A radian comes from the unit circle (a circle of radius 1). Walk around it: a full lap is a distance of 2π, so one cycle is 2π radians. Converting is a single multiplication:

```formula
θ = 2 × π × p
θ = 2 × π × 0.25
θ ≈ 1.571 rad
where
θ: theta, the phase as an angle, in radians (rad)
p: the phase as a fraction of a cycle, from 0 up to 1; here a quarter of a cycle, 0.25
π: pi, the ratio of a circle's circumference to its diameter, about 3.14159
rad: radians, the angle unit maths libraries use; 2π rad is one full cycle, the same as 360°
≈: approximately equal to (rounded)
In words: to turn a fraction of a cycle into radians, multiply by 2π. A quarter of a cycle is π/2, about 1.571 radians, which is 90°.
```

| Cycles | Degrees | Radians |
|---|---|---|
| 0.25 | 90° | π/2 ≈ 1.571 |
| 0.5 | 180° | π ≈ 3.142 |
| 1 | 360° | 2π ≈ 6.283 |

Phase matters most when you **combine** waves. Two identical sines in phase add up to double the amplitude. Shift one by half a cycle (π radians, 180°) and they cancel completely. Anywhere in between gives partial reinforcement or partial cancellation. That's why detuned oscillators "beat", and why some layered sounds go thin when a phase relationship shifts.

Phase on its own, for a single steady tone, is mostly inaudible. Your ear can't tell a sine from the same sine starting a quarter-cycle later. What you *can* hear is a sudden phase **jump** in the middle of a tone: the waveform jumps to a new value instantly, and you hear a click.

## The sine wave formula

The purest tone is a sine wave. This formula gives its value at any moment, and it is the starting point for every oscillator in the project:

```formula
x(t) = A × sin(2 × π × f × t + φ)
where
x(t): the value of the wave at time t: a pressure, a voltage or a sample value, depending on where the wave lives
t: the time since the wave started, in seconds (s)
A: the amplitude, the largest value the wave reaches; in software usually at most 1.0
sin: the sine function, which turns an angle in radians into a value that swings smoothly between −1 and +1 and repeats every 2π
π: pi, about 3.14159
f: the frequency, in hertz (Hz), cycles per second
φ: phi, the starting phase, in radians (rad): where in the cycle the wave is at t = 0
In words: count how many cycles have passed (f × t), turn that into an angle (× 2π), add the starting phase, take the sine, and scale it by the amplitude.
```

Read it from the inside out:

1. **f·t** is the number of cycles completed after t seconds. At 440 Hz, after 0.01 s you've done 4.4 cycles.
2. **2π·f·t** converts cycles to radians, because `sin` wants radians.
3. **φ** (phi) is the starting phase, in radians. A starting phase of π/2 turns a sine into a cosine.
4. **A** scales the result, which otherwise swings between −1 and +1.

For example, take an amplitude of 0.5, a frequency of 440 Hz and a starting phase of 0, and ask for the value half a millisecond in:

```formula
x(t) = A × sin(2 × π × f × t + φ)
x = 0.5 × sin(2 × π × 440 × 0.0005 + 0)
x = 0.5 × sin(1.382)
x ≈ 0.491
where
x(t): the value of the wave at time t
x: the same value, written without the (t) once t is fixed
A: the amplitude; here 0.5
sin: the sine function, taking radians
π: pi, about 3.14159
f: the frequency; here 440 Hz
t: the time; here 0.0005 s (half a millisecond), by which point 0.22 cycles have passed
φ: phi, the starting phase; here 0 radians
≈: approximately equal to (rounded)
In words: 0.22 of a cycle is an angle of about 1.382 radians, whose sine is about 0.982, and half of that is about 0.491.
```

The formula describes an ideal, never-ending tone; real notes start, stop and change, which is what the rest of the module deals with.

The term **2πf** comes up so often that it has its own name, **angular frequency**, written ω (omega):

```formula
ω = 2 × π × f
ω = 2 × π × 440
ω ≈ 2764.6 rad/s
where
ω: omega, the angular frequency: how many radians the phase turns through per second, in radians per second (rad/s)
π: pi, about 3.14159
f: the ordinary frequency, in hertz (Hz), cycles per second
rad/s: radians per second
≈: approximately equal to (rounded)
In words: angular frequency is the frequency measured in radians per second instead of cycles per second, so it is 2π times bigger.
```

> [!note] Why the sine is special
> A sine contains exactly one frequency. Any periodic waveform (a sawtooth, a square, a recorded violin note) can be built by adding sines at whole-number multiples of its fundamental frequency. These are its **harmonics**, and the recipe of harmonic amplitudes is a big part of its **timbre**. The synthesis module builds on this.

## From time to samples

A digital synth doesn't compute x(t) for every possible t. It computes the wave at evenly spaced instants, `fs` times per second, where `fs` is the **sample rate** (48,000 per second is typical). Sample number n happens at time n/fs seconds, so the sine formula becomes:

```formula
x[n] = A × sin(2 × π × f × n / fs + φ)
where
x[n]: the value of sample number n (square brackets mean "the sample with this index", not a continuous time)
n: the sample index, a whole number counting up from 0
fs: the sample rate, in samples per second (equivalently hertz, Hz); typically 48,000
A: the amplitude, the largest value the wave reaches
sin: the sine function, taking an angle in radians
π: pi, about 3.14159
f: the frequency of the tone, in hertz (Hz)
φ: phi, the starting phase, in radians
In words: the sampled sine is the same formula with time replaced by "sample number divided by sample rate", which is the time at which that sample is taken.
```

Two derived numbers fall straight out of this, and the roadmap asks you to calculate both.

**Samples per period** tells you how many numbers describe one cycle:

```formula
S = fs / f
S = 48000 / 440
S ≈ 109.09
where
S: the number of samples in one cycle (samples per period); not usually a whole number
fs: the sample rate, in samples per second; here 48,000
f: the frequency of the tone, in hertz (Hz), cycles per second; here 440
≈: approximately equal to (rounded)
In words: divide samples per second by cycles per second to get samples per cycle. A 440 Hz cycle at 48 kHz spans about 109 samples.
```

**Phase increment** is how far round the cycle you move between one sample and the next. It's the reciprocal of samples per period:

```formula
Δp = f / fs
Δp = 440 / 48000
Δp ≈ 0.009167 cycles
Δθ = 2 × π × Δp ≈ 0.05760 rad
where
Δp: delta p, the phase increment in cycles per sample (the Greek letter Δ, delta, means "a step in")
Δθ: delta theta, the same increment measured in radians per sample
f: the frequency of the tone, in hertz (Hz)
fs: the sample rate, in samples per second
π: pi, about 3.14159
cycles: fractions of one full cycle
rad: radians; one full cycle is 2π radians
≈: approximately equal to (rounded)
In words: each sample moves the phase on by the frequency divided by the sample rate, in cycles; multiply by 2π to get radians.
```

The same calculation for several notes, in Python:

```python
import math

fs = 48_000
for f in (55, 440, 1000, 3520):
    spp = fs / f
    inc = f / fs
    rad = 2 * math.pi * inc
    print(f"{f:>4} Hz {spp:7.2f} spp"
          f" {inc:.6f} cyc {rad:.5f} rad")
```

```text
  55 Hz  872.73 spp 0.001146 cyc 0.00720 rad
 440 Hz  109.09 spp 0.009167 cyc 0.05760 rad
1000 Hz   48.00 spp 0.020833 cyc 0.13090 rad
3520 Hz   13.64 spp 0.073333 cyc 0.46077 rad
```

Notice:

- Samples per period is rarely a whole number. A 440 Hz cycle at 48 kHz takes 109.09 samples, so the samples land at slightly different points of each cycle. That's fine; the phase is tracked as a real number.
- Higher pitches get **fewer** samples per cycle. At 3520 Hz you have under 14 points per cycle. Lesson 4 shows where this runs out.
- The phase increment depends on **both** f and fs. Run the same code at 44.1 kHz and every increment changes. If a synth assumes the wrong sample rate, every note comes out at the wrong pitch.

## The phase accumulator

The formula above recomputes the phase from n each time. Real oscillators don't. They keep a running **phase** variable and add the increment each sample, wrapping it back into range after each full cycle:

```python
import math

fs, f = 48_000, 440.0
inc = f / fs
phase = 0.0          # cycles, in [0, 1)
out = []
for n in range(6):
    out.append(math.sin(2*math.pi*phase))
    phase += inc
    if phase >= 1.0:
        phase -= 1.0
print([round(x, 4) for x in out])
```

```text
[0.0, 0.0576, 0.1149, 0.1719, 0.2284, 0.284]
```

This **phase accumulator** is the core of many digital oscillators. It has three advantages over recomputing from n.

**1. Frequency changes are smooth.** If you recompute `sin(2π·f·t)` with a new f, the phase jumps. Switch from 440 Hz to 450 Hz at 0.525 s:

```python
import math
fs = 48_000
t = 25_200 / fs      # 0.525 s
before = math.sin(2*math.pi*440*t)
after  = math.sin(2*math.pi*450*t)
print(f"{before:.3f} -> {after:.3f}")
```

```text
0.000 -> 1.000
```

The output leaps from 0 to full scale in one sample: a click. With an accumulator, you just change `inc` and the phase carries on from where it was. Vibrato, pitch bends and glides all rely on this.

**2. Precision stays bounded.** The phase is always between 0 and 1, so its spacing stays bounded instead of getting coarser with elapsed time. Rounding of the increment and additions can still introduce a small frequency error. A sample counter n only grows. A 32-bit float (common on embedded chips) represents integers exactly only up to 2²⁴ = 16,777,216. At 48 kHz that's about 349.5 seconds, under six minutes. After that, `n + 1 == n` in float32, and an oscillator that computes from n starts to drift and distort.

**3. It's cheap.** One add and a compare per sample, then a waveform lookup. The waveform part can be `sin`, a table, or simple arithmetic for a sawtooth (the phase itself, rescaled, *is* a naive saw).

> [!warning] Keep the state between blocks
> Audio is processed in blocks (say 48 samples at a time). The phase must persist from one block to the next. If you reset it to zero each block, you get a click every block: at 48 samples per block and 48 kHz, that's a 1 kHz buzz.

## Pitfalls

- **Degrees passed to `sin`.** `math.sin(90)` is about 0.894, not 1. The argument is radians.
- **Forgetting the 2π.** `sin(f·t)` produces a tone 2π times too low (440 Hz becomes about 70 Hz).
- **Hard-coding the sample rate.** Compute the increment from the actual rate the audio hardware is running at.
- **Ignoring wrap.** Without the wrap, a float phase eventually loses precision like the counter does.

## Key takeaways
- Frequency is one divided by the period. Wavelength (speed of sound divided by frequency) is a distance in air and irrelevant inside the synth's maths.
- One cycle is 2π radians; `sin` takes radians.
- A sine is amplitude × sin(2π × frequency × time + starting phase); sampled, time becomes sample number divided by sample rate.
- Samples per period is the sample rate divided by the frequency; the phase increment is the frequency divided by the sample rate, in cycles per sample (2π times that in radians). Both depend on the sample rate.
- Oscillators keep a wrapped phase accumulator so that frequency changes preserve phase and numerical spacing stays bounded; abrupt changes can still create transients and rounding error remains. Keep that state across processing blocks.

## Further reading
- [Sinusoids — Julius O. Smith, Mathematics of the DFT (CCRMA)](https://ccrma.stanford.edu/~jos/mdft/Sinusoids.html)
- [Sine wave — Wikipedia](https://en.wikipedia.org/wiki/Sine_wave)
- [Phase (waves) — Wikipedia](https://en.wikipedia.org/wiki/Phase_(waves))
- [Speed of sound — Wikipedia](https://en.wikipedia.org/wiki/Speed_of_sound)
- [Numerically controlled oscillator (phase accumulator) — Wikipedia](https://en.wikipedia.org/wiki/Numerically_controlled_oscillator)
