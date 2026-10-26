---
id: snd-sharp-waveform-aliases
title: Why naive sawtooths and squares alias
level: intermediate
minutes: 4
summary: Explain why waveform edges create aliases and why folded harmonics can fall below the note.
sourceLesson: snd-aliasing
---

## Why sharp waveforms alias

A sine has one frequency. A sawtooth has harmonics at every whole-number multiple of its frequency, and their amplitudes fall slowly.

A sawtooth’s second harmonic has half the fundamental’s amplitude, its third one third and so on. Even the twentieth is only about 26 dB below the fundamental, so very high harmonics cannot simply be assumed inaudible.

A square has only the odd harmonics (1st, 3rd, 5th, …), whose amplitudes also fall as one over the harmonic number. That fall-off is slow, so a lot of energy sits in very high harmonics.

The cause is the waveform's **sharp edge**. A discontinuity (an instant jump) needs infinitely many harmonics to describe, and a waveform with a jump has harmonic amplitudes that halve per octave of harmonic number (about 6 dB). A triangle wave has corners but no jumps; its harmonic amplitudes fall fourfold per octave (about 12 dB), so it aliases far less.

A **naive sawtooth** is generated directly from the phase accumulator (the phase-accumulator unit) by rescaling the phase.

Rescaling the wrapped phase from zero-to-one into minus-one-to-plus-one creates a rising ramp. At each wrap it jumps straight from the top back to the bottom: that is the naive sawtooth’s sharp edge.

That jump makes it a sample of the ideal infinite-bandwidth sawtooth. Every harmonic above Nyquist folds back. Take a high note, 1760 Hz (A6), at 48 kHz:

- Harmonics up to the thirteenth (22,880 Hz) are below 24 kHz and fine.
- Harmonics 14 and up fold back; **many land away from multiples of 1760 Hz**. Some higher aliases can also coincide with genuine harmonic bins.

Which aliases land low, where they are most audible?

```python
import math

def alias(f, fs):
    f = f % fs
    # Reflect the upper half below Nyquist.
    return fs - f if f > fs / 2 else f

fs, f0 = 48_000, 1_760
for k in range(14, 31):
    a = alias(k * f0, fs)
    # Show low aliases likely to be audible.
    if a < 5_000:
        # Level of this source harmonic.
        db = 20 * math.log10(1 / k)
        print(f"harmonic {k}: {k*f0} Hz"
              f" -> {a} Hz ({db:.1f} dB)")
```

```text
harmonic 25: 44000 Hz -> 4000 Hz (-28.0 dB)
harmonic 26: 45760 Hz -> 2240 Hz (-28.3 dB)
harmonic 27: 47520 Hz -> 480 Hz (-28.6 dB)
harmonic 28: 49280 Hz -> 1280 Hz (-28.9 dB)
harmonic 29: 51040 Hz -> 3040 Hz (-29.2 dB)
harmonic 30: 52800 Hz -> 4800 Hz (-29.5 dB)
```

Harmonic 27 lands at **480 Hz**, below the note's own fundamental, only about 29 dB down. None of these are harmonics of 1760 Hz, so they sound like an inharmonic, metallic ring. As the note bends, they slide in the wrong directions. Low notes are less affected (their high harmonics are much weaker by the time they reach Nyquist), which is why naive oscillators can sound fine in the bass and terrible at the top.

> [!warning] You can't filter it out afterwards
> Once an alias is at 480 Hz, it's indistinguishable from a real 480 Hz component. A low-pass filter after the oscillator can't remove it without removing real content too. Aliasing has to be prevented where the high frequencies are *created*.

## Key takeaways

- Sawtooth and square jumps need slowly decaying harmonics, so high pitches alias strongly.
- A folded harmonic can fall below the fundamental and become an inharmonic tone.
- After folding, an alias cannot be distinguished from wanted content at the same frequency.

## Further reading

- [Alias-Free Digital Synthesis of Classic Analog Waveforms — Stilson & Smith (CCRMA)](https://ccrma.stanford.edu/~stilti/papers/blit.pdf)
- [Aliasing — Wikipedia](https://en.wikipedia.org/wiki/Aliasing)
- [Sawtooth wave — Wikipedia](https://en.wikipedia.org/wiki/Sawtooth_wave)
