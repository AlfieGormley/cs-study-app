---
id: syn-harmonics-pulse-spectrum
title: Oscillator pulse width and missing harmonics
level: intermediate
minutes: 2
summary: Oscillator pulse width and missing harmonics.
sourceLesson: syn-harmonics
---

### Pulse waves

A pulse wave's harmonics depend on its width (the fraction of each cycle it spends high):

```formula
A_n ∝ |sin(π n w)| / n
where
A_n: the amplitude of harmonic n
∝: "is proportional to": A_n equals the right-hand side times a fixed scale factor
|x|: the absolute value of x, i.e. x without its sign
sin: the sine function, taking an angle in radians
π: pi, about 3.14159
n: the harmonic number, 1, 2, 3...
w: the oscillator pulse width, a fraction of the cycle between 0 and 1 (0.5 is a square wave)
In words: each harmonic's strength falls roughly as 1/n, but is multiplied by a sine that reaches zero whenever n × w is a whole number.
```

A harmonic vanishes whenever its number times the width is a whole number. At half-cycle width, all even harmonics vanish. At quarter-cycle width, every fourth harmonic vanishes, because the fourth harmonic spans a whole cycle during the high interval. This is why sweeping oscillator pulse width changes the timbre so audibly.

## Key takeaways

- Oscillator pulse width changes the harmonic strengths.
- At one-third duty cycle, every third harmonic vanishes in the ideal series.

## Further reading

- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
- [Alias-free classic waveforms — Stilson and Smith](https://ccrma.stanford.edu/~stilti/papers/blit.pdf)
