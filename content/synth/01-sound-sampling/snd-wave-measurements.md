---
id: snd-wave-measurements
title: Amplitude, period and wavelength
level: basic
minutes: 4
summary: Describe a repeating wave and convert between frequency, period and wavelength.
sourceLesson: snd-waves
---

Every sound your synth makes ends up as a speaker cone pushing air back and forth. The air pressure at your ear rises and falls around normal atmospheric pressure, and your ear turns that pattern into what you hear.

Inside the synth there is no air. There is first a sequence of numbers, then a voltage on a wire. The vocabulary is the same at every stage, though. A *wave* is a quantity (pressure, voltage, or a number in memory) that changes over time, and we describe it by how big the change is, how often it repeats and where in its cycle it is.

Start by distinguishing how large a wave is, how often it repeats and how far it travels.



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
- **Wavelength** (λ) is the *distance* one cycle covers as it travels through a medium such as air.

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

## Key takeaways

- Amplitude measures the size of the swing; frequency counts cycles per second.
- Frequency and period are reciprocals: doubling one halves the other.
- Wavelength is a distance in a medium; period is a time. Inside a synth, work with time and frequency.

## Further reading

- [Sine wave — Wikipedia](https://en.wikipedia.org/wiki/Sine_wave)
- [Speed of sound — Wikipedia](https://en.wikipedia.org/wiki/Speed_of_sound)
