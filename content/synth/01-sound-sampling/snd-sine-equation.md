---
id: snd-sine-equation
title: Build a sine from its parameters
level: basic
minutes: 3
summary: Explain how frequency, elapsed time, phase and amplitude determine a sine’s value.
sourceLesson: snd-waves
---

## The sine wave formula

The purest tone is a sine wave. This formula gives its value at any moment, and it is the starting point for every oscillator in the project:

```formula essential
x(t) = A × sin(2 × π × f × t + φ)
where
x(t): the value of the wave at time t: a pressure, a voltage or a sample value, depending on where the wave lives
t: the time since the wave started, in seconds (s)
A: the amplitude, the largest value the wave reaches; in software usually at most 1.0
sin: the sine function, which turns an angle in radians into a value that swings smoothly between −1 and +1 and repeats every 2π
π: pi, about 3.14159
f: the frequency, in hertz (Hz), cycles per second
φ: phi, the starting phase, in radians (rad): where in the cycle the wave is at t = 0
In words: To generate a sine, advance through cycles at the desired frequency, convert to radians, add the starting phase, take the sine and scale by amplitude.
```

Read it from the inside out:

1. **f·t** is the number of cycles completed after t seconds. At 440 Hz, after 0.01 s you've done 4.4 cycles.
2. **2π·f·t** converts cycles to radians, because `sin` wants radians.
3. **φ** (phi) is the starting phase, in radians. A starting phase of π/2 turns a sine into a cosine.
4. **A** scales the result, which otherwise swings between −1 and +1.

For a sine starting at zero, a quarter-cycle reaches the positive peak, a half-cycle returns to zero and three quarters reaches the negative peak. An amplitude of 0.5 makes those peaks +0.5 and −0.5, whatever the frequency. Frequency determines how quickly you reach them.

The formula describes an ideal, never-ending tone; real notes start, stop and change, which is what the rest of the module deals with.

Frequency can also be measured in radians per second, called **angular frequency**. One cycle contains two pi radians, so angular frequency is about 6.283 times the cycles-per-second value.

> [!note] Why the sine is special
> A sine contains exactly one frequency. An ideal periodic waveform (a sawtooth, a square, or a repeating approximation to a sustained violin tone) can be built by adding sines at whole-number multiples of its fundamental frequency. Those whole-number components are its **harmonics**, and their amplitude recipe is a big part of its **timbre**. A real recorded note also changes over time and can contain noise. The synthesis module builds on this.

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
