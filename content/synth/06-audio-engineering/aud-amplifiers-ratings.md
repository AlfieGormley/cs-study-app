---
id: aud-amplifiers-ratings
title: Interpret amplifier power specifications
level: advanced
minutes: 3
summary: Compare power ratings at stated load, bandwidth, distortion and test conditions.
sourceLesson: aud-amplifiers
---

## Power ratings

- **Continuous (average) power**, often called **"RMS power"**, is the meaningful figure: the average power the amp can deliver continuously into a stated load, over a stated bandwidth, at a stated distortion. "RMS power" is a loose name: it's the average power calculated from RMS voltage and current, not the RMS of the power waveform.
- **Peak power.** For a sine wave, peak instantaneous power is **twice** the average. A "200 W peak" amp may be a 100 W continuous amp.
- **PMPO** ("peak music power output") has no reliable conversion to continuous power without a defined test method and conditions. Treat an unexplained PMPO number as unsuitable for comparison.

Where the factor of two for peak power comes from: a sine wave's instantaneous power swings between zero and a peak, and spends as long below the halfway line as above it.

```formula
p = V_pk^2 sin^2(2πft) / R
p_peak = V_pk^2 / R
P_avg = V_pk^2 / (2R) = V_rms^2 / R
V_rms = V_pk / √(2)
where
p: the instantaneous power at time t, in watts (W)
V_pk: the sine wave's peak voltage, in volts (V)
sin: the sine function; sin^2 (sine squared) swings between 0 and 1 and averages exactly 0.5
f: the frequency of the sine, in hertz (Hz)
t: time, in seconds (s)
π: pi, about 3.14159
R: the load resistance, in ohms (Ω)
p_peak: the highest instantaneous power, in watts (W)
P_avg: the average (continuous) power, in watts (W)
V_rms: the RMS voltage, the peak divided by √2 (about 0.707 of the peak)
√: square root
In words: for a sine into a resistor, the average power is half the peak instantaneous power, and it equals the RMS voltage squared over the resistance.
```

Example: a sine of 40 V peak into 8 Ω peaks at 1600 ÷ 8 = 200 W but averages 100 W, so "200 W peak" and "100 W continuous" can describe the same amp. This only holds for a steady sine into a resistive load.

A complete specification looks like: *"100 W continuous into 8 Ω, 20 Hz–20 kHz, at 0.1% THD"*. Missing conditions usually hide something, such as a rating taken at 10% distortion or at 1 kHz only.

## Key takeaways
- Compare power ratings at stated load, bandwidth, distortion and test conditions.
- Sine-wave instantaneous peak power is twice average into a resistor.
- A marketing peak label alone does not establish continuous output.

## Further reading
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
