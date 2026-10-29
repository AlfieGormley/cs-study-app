---
id: aud-hearing-weighting
title: Understand A, C and Z weighting
level: basic
minutes: 4
summary: A-weighting strongly attenuates low-frequency contributions to a meter reading.
sourceLesson: aud-hearing
---

## A and C weighting

Sound level meters apply a **frequency weighting** to make a single number track human response better. The two that matter, both defined for sound level meters in **IEC 61672-1**:

- **A-weighting** (dB(A) or dBA) strongly reduces low frequencies (about −19 dB at 100 Hz, −30 dB at 50 Hz) and slightly boosts 2–4 kHz. It was based on the 40-phon Fletcher–Munson curve. It is the standard weighting for noise exposure and for many noise-floor specifications.
- **C-weighting** (dB(C)) is nearly flat from about 31.5 Hz to 8 kHz (−3 dB points). It is used for **peak level** measurements, and for loud, bass-heavy sound where A-weighting would hide the low end.
- **Z-weighting** is flat ("zero").

In Great Britain, the Control of Noise at Work Regulations 2005 express daily or weekly exposure in dB(A) and peak sound pressure in dB(C) (the next lessons cover the limits).

Because a weighting removes part of the spectrum before the meter measures, the same sound gives different readings under different weightings. Approximate A-weighting values, from the IEC 61672-1 definition:

| Frequency | A-weighting |
|---|---|
| 31.5 Hz | about −39 dB |
| 50 Hz | about −30 dB |
| 100 Hz | about −19 dB |
| 1 kHz | 0 dB |
| 2–4 kHz | about +1 dB |
| 10 kHz | about −2.5 dB |

So a 100 Hz tone read on an A-weighted meter shows about 19 dB less than its unweighted sound pressure level. A dB(A) figure is therefore a statement about a *filtered* measurement, and two sounds with the same dB(A) can have very different amounts of bass.

The curve is not a vague idea: IEC 61672-1 defines it exactly, as a fixed combination of simple filters. You do not need the formula to read meters, but it is the starting point if you build an A-weighted meter in software:

```formula reference
R_A = 12194^2 f^4 / D
D = (f^2 + 20.6^2)(f^2 + 12194^2)
  √((f^2 + 107.7^2)(f^2 + 737.9^2))
A = 20 log_10(R_A) + 2.00
where
R_A: the A-weighting response at frequency f, as a plain gain ratio (no unit)
f: the frequency being weighted, in hertz (Hz)
D: the denominator, written on its own lines only to keep them short
20.6, 107.7, 737.9, 12194: the corner frequencies of the weighting's filter stages, in hertz (Hz)
√: square root
log_10: the base-10 logarithm: the power you raise 10 to in order to get the number
2.00: a rounded correction in decibels that makes the weighting approximately 0 dB at 1 kHz
A: the A-weighting at frequency f, in decibels (dB); negative means the meter reduces that frequency
In words: A-weighting is a fixed filter defined in the standard: two stages cut below about 20 Hz, stages near 108 Hz and 738 Hz shape the low-mid roll-off, two stages cut above about 12 kHz, and an offset sets 1 kHz to 0 dB.
```

> [!note] Why live engineers watch dB(C) as well as dB(A)
> A kick drum and sub-bass can carry enormous energy at 40–60 Hz while barely moving a dB(A) meter. Venues often monitor both.

## Key takeaways
- A-weighting strongly attenuates low-frequency contributions to a meter reading.
- Great Britain workplace exposure uses A-weighting for dose and C-weighting for peaks.
- Weightings are measurement filters, not a loudspeaker behaviour.

## Further reading
- [A-weighting measurement implementation — Son, Kyung and Cho (2019)](https://mdpi-res.com/d_attachment/sensors/sensors-19-03633/article_deploy/sensors-19-03633.pdf)
- [Auditory processing — Brian C. J. Moore](https://pmc.ncbi.nlm.nih.gov/articles/PMC2606789/)
- [Noise regulations — HSE](https://www.hse.gov.uk/noise/regulations.htm)
- [Control of Noise at Work Regulations 2005, regulation 4](https://www.legislation.gov.uk/uksi/2005/1643/regulation/4/made)
- [WHO safe-listening venues standard summary](https://cdn.who.int/media/docs/default-source/documents/health-topics/deafness-and-hearing-loss/mls_whd_infographic.pdf?sfvrsn=93a7a1ef_5)
