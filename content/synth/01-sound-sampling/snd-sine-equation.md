---
id: snd-sine-equation
title: Build a sine from its parameters
level: basic
minutes: 4
summary: Read the sine equation from the inside out and calculate a waveform value.
sourceLesson: snd-waves
---

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
> A sine contains exactly one frequency. An ideal periodic waveform (a sawtooth, a square, or a repeating approximation to a sustained violin tone) can be built by adding sines at whole-number multiples of its fundamental frequency. A real recorded note also changes over time and can contain noise. These are its **harmonics**, and the recipe of harmonic amplitudes is a big part of its **timbre**. The synthesis module builds on this.

## Pitfalls

- **Forgetting the 2π.** `sin(f·t)` produces a tone 2π times too low (440 Hz becomes about 70 Hz).

## Key takeaways

- Frequency and elapsed time determine the number of cycles completed.
- Convert cycles to radians, add starting phase, then take the sine and scale its amplitude.
- Angular frequency measures radians per second; harmonics build richer periodic waveforms.

## Further reading

- [Sinusoids — Julius O. Smith, Mathematics of the DFT (CCRMA)](https://ccrma.stanford.edu/~jos/mdft/Sinusoids.html)
- [Sine wave — Wikipedia](https://en.wikipedia.org/wiki/Sine_wave)
- [Python sine and angle functions — Python documentation](https://docs.python.org/3/library/math.html)
