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

Where the factor of two for peak power comes from: a sine wave's instantaneous power swings between zero (as the voltage crosses zero) and a maximum (at the voltage peaks), and it averages exactly half of that maximum. Example: a sine of 40 V peak into 8 Ω peaks at 200 W but averages 100 W, so "200 W peak" and "100 W continuous" can describe the same amp. This only holds for a steady sine into a resistive load; music has a much larger ratio of peak to average.

A complete specification looks like: *"100 W continuous into 8 Ω, 20 Hz–20 kHz, at 0.1% THD"*. Missing conditions usually hide something, such as a rating taken at 10% distortion or at 1 kHz only.

## Key takeaways
- Compare power ratings at stated load, bandwidth, distortion and test conditions.
- Sine-wave instantaneous peak power is twice average into a resistor.
- A marketing peak label alone does not establish continuous output.

## Further reading
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
