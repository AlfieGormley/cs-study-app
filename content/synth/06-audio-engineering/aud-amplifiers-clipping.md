---
id: aud-amplifiers-clipping
title: How clipping changes driver power
level: advanced
minutes: 3
summary: At equal peak voltage, a square wave dissipates twice a sine’s average power into a resistor.
sourceLesson: aud-amplifiers
---

## Clipping and why it can kill tweeters

An amplifier can't output more voltage than its supply rails allow. Ask for more and the output shows **clipping**: the waveform's peaks are flattened.

```diagram
  clean:      /\      /\
             /  \    /  \
            /    \  /    \
  clipped:   ____      ____
            /    \    /    \
           /      \__/      \
```

Why that's dangerous for **tweeters**:

- **More average power.** A sine wave clipped hard towards a square wave carries up to **twice** the average power of the clean sine with the same peak voltage (worked out below).
- **High-frequency harmonics.** A square wave contains odd harmonics at 1/3, 1/5, 1/7... of the fundamental's amplitude (about −9.5, −14 and −16.9 dB, worked out below). Clip a loud bass or middle-frequency note and those harmonics land in the tweeter's band. The crossover passes them straight to a driver that normally receives only a small fraction of the total power, and its small voice coil overheats.

A square wave sits at its peak voltage all the time, while a sine only touches its peak briefly:

```formula
P_sine = V_pk^2 / (2R)
P_square = V_pk^2 / R = 2P_sine
L_n = 20 log_10(1 / n)
L_3 = 20 log_10(1/3) ≈ −9.5 dB
L_5 = 20 log_10(1/5) ≈ −14 dB
L_7 = 20 log_10(1/7) ≈ −16.9 dB
where
P_sine: the average power of a clean sine wave, in watts (W)
P_square: the average power of a square wave with the same peak voltage, in watts (W)
V_pk: the peak voltage, in volts (V)
R: the load resistance, in ohms (Ω)
L_n: the level of the nth harmonic relative to the square wave's fundamental, in decibels (dB)
n: the harmonic number (3, 5, 7 ...): the multiple of the fundamental frequency; a square wave has only odd ones
L_3: the 3rd harmonic's level
L_5: the 5th harmonic's level
L_7: the 7th harmonic's level
log_10: the base-10 logarithm
≈: approximately equal to
dB: decibel, the unit of level ratio
In words: hard clipping can double the average power at the same peak voltage, and pushes strong harmonics at three, five and seven times the note's frequency into the tweeter's range.
```

For example, a 1.5 kHz note clipped to a square wave puts its 3rd harmonic at 4.5 kHz, its 5th at 7.5 kHz and its 7th at 10.5 kHz: all above a typical 2–3 kHz crossover.

So sustained clipping can overheat a tweeter; a larger clean amplifier can also damage it if level, spectrum or duration exceeds its limits. Watch for clip indicators, leave headroom, and use limiters in PA systems.

## Key takeaways
- At equal peak voltage, a square wave dissipates twice a sine’s average power into a resistor.
- Symmetric clipping adds odd harmonics.
- Driver damage depends on signal spectrum, duration, filtering and actual limits.

## Further reading
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
