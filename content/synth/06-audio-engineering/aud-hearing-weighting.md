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

The A-weighting curve is defined by a formula in IEC 61672-1. It describes a set of simple filters: two that cut below about 20 Hz, one each near 108 Hz and 738 Hz that shape the low-mid roll-off, and two that cut above about 12.2 kHz. You don't need to memorise it, but it shows that "dB(A)" is a precisely defined filter, not a vague idea:

```formula
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
In words: a fixed filter shape, turned into decibels and nudged so that 1 kHz is unchanged; it cuts deep bass and extreme treble and slightly lifts 2–4 kHz.
```

Worked example at 100 Hz:

```formula
R_A = (1.487 × 10^16) / (1.696 × 10^17)
R_A ≈ 0.0877
A = 20 log_10(0.0877) + 2.00
A = 20 × (−1.057) + 2.00
A ≈ −19.1 dB
where
R_A: the A-weighting gain ratio at 100 Hz (no unit)
A: the A-weighting at 100 Hz, in decibels (dB)
log_10: the base-10 logarithm
dB: decibels
≈: approximately equal to (rounded)
In words: an A-weighted meter reads a 100 Hz tone about 19 dB lower than its true sound pressure level.
```

The same formula as a program, evaluated at several frequencies:

```python
import math

def a_weight(f):
    # f is in Hz; the gain is dimensionless.
    f2 = f * f
    ra = (12194**2 * f2**2) / (
        (f2 + 20.6**2)
        * math.sqrt((f2 + 107.7**2)
                    * (f2 + 737.9**2))
        * (f2 + 12194**2))
    return 20 * math.log10(ra) + 2.00

for f in (50, 100, 1000, 4000, 10000):
    a = a_weight(f)
    print(f"{f:>5} Hz: {a:6.1f} dB")
```

```output
   50 Hz:  -30.3 dB
  100 Hz:  -19.1 dB
 1000 Hz:    0.0 dB
 4000 Hz:    1.0 dB
10000 Hz:   -2.5 dB
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
