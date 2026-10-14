---
id: snd-harmonics-timbre
title: Harmonics, timbre and missing fundamentals
level: basic
minutes: 3
summary: Separate pitch from harmonic content and explain beating between equal-tempered notes and harmonics.
sourceLesson: snd-pitch
---

## Pitch vs timbre

Play a sine and a sawtooth at 220 Hz. They have the **same pitch** but sound completely different. The difference is **timbre**, often loosely called "tone colour".

A sawtooth at 220 Hz contains sine components at 220, 440, 660, 880 Hz and so on: the **harmonic series**, every whole-number multiple of the fundamental. In an ideal sawtooth their amplitudes fall off steadily:

```formula
f_k = k × f_0
a_k = 1 / k
where
f_k: the frequency of harmonic number k, in hertz (Hz)
k: the harmonic number, a whole number 1, 2, 3, …; k = 1 is the fundamental
f_0: the fundamental frequency, in hertz (Hz); here 220 Hz
a_k: the amplitude of harmonic k, relative to the fundamental (no unit)
In words: harmonic k sits at k times the fundamental and, in a sawtooth, has 1/k of its amplitude: the 3rd harmonic of 220 Hz is at 660 Hz with a third of the amplitude.
```

A sine has only the 220 Hz component. Because all the extra components are exact multiples, the waveform still repeats every 1/220 s, and the ear still hears 220 Hz.

The harmonic series is also where just ratios come from: harmonics 2, 3, 4, 5 give an octave, a fifth above that, another octave, and a major third. The 5th harmonic of 110 Hz is 550 Hz, about 14 cents below the 12-TET C♯5 (554.37 Hz).

Timbre also depends on how the sound changes over time: the attack, how harmonics fade, noise. Subtractive synthesis works by starting with a harmonically rich wave and filtering harmonics away, changing timbre while leaving pitch alone. That's the next module.

> [!note] The missing fundamental
> Pitch perception isn't just "find the lowest component". If you remove the 220 Hz component from a sawtooth and keep 440, 660, 880 Hz and so on, most listeners still hear a pitch of 220 Hz, because the harmonics are spaced 220 Hz apart. This is why small speakers can suggest bass notes they can't reproduce.

## Key takeaways

- A periodic waveform’s harmonics lie at whole-number multiples of its fundamental.
- Harmonic amplitudes and changes over time shape timbre.
- Listeners can hear a missing fundamental from the spacing of the remaining harmonics.

## Further reading

- [Equal temperament — Wikipedia](https://en.wikipedia.org/wiki/Equal_temperament)
- [Beat (acoustics) — Wikipedia](https://en.wikipedia.org/wiki/Beat_(acoustics))
- [Timbre — Wikipedia](https://en.wikipedia.org/wiki/Timbre)
