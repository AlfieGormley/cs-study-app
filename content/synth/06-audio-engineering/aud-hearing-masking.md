---
id: aud-hearing-masking
title: Masking and auditory filter bandwidth
level: basic
minutes: 4
summary: Masking depends on spectrum, timing and level.
sourceLesson: aud-hearing
---

## Masking

A loud sound can make a quieter one inaudible. This is **masking**, and it's the reason a mix "gets muddy": parts that each sound fine alone hide each other when played together.

- **Simultaneous masking** is strongest when the two sounds are **close in frequency**.
- It **spreads upwards**: a loud low sound masks higher frequencies much more effectively than a loud high sound masks lower ones. The effect grows with level. That's why a heavy bass part can dull a whole mix.
- **Temporal masking** also happens: a loud sound can hide quieter sounds just after it (and, briefly, just before it).

Lossy codecs such as MP3 and AAC exploit masking: they spend fewer bits on what masking will hide anyway.

## Critical bands, intuitively

The cochlea behaves like a bank of overlapping band-pass filters. Critical-band measurements and auditory-filter bandwidths both describe frequency selectivity, but their numerical widths depend on how they are measured. ERB is the width of an ideal rectangular filter with the same peak gain and integrated response as the actual filter. Two tones inside one band interact strongly: they mask each other, beat or sound rough. Tones in well-separated bands are heard more independently.

The bands are narrow at low frequencies and wider at high frequencies. One standard model, Glasberg and Moore's **equivalent rectangular bandwidth (ERB)**, gives the width of the auditory filter centred on a given frequency. It was fitted to listening-test data from young, normally hearing listeners at moderate levels. In words: the auditory filter is about 25 Hz wide at the very bottom of the range and widens roughly in proportion to frequency, approaching about 11 % of the centre frequency at high frequencies.

| Centre | ERB |
|---|---|
| 100 Hz | ≈ 35 Hz |
| 1 kHz | ≈ 133 Hz |
| 4 kHz | ≈ 456 Hz |

```formula reference
ERB = 24.7 (4.37f / 1000 + 1)
where
ERB: the equivalent rectangular bandwidth of the auditory filter, in hertz (Hz)
f: the centre frequency of the filter, in hertz (Hz)
24.7: the bandwidth in hertz the formula gives at very low frequencies
4.37: how fast the bandwidth grows with frequency, per kilohertz of centre frequency
1000: converts f from hertz to kilohertz
Hz: hertz, cycles per second
In words: Glasberg and Moore's fit gives an auditory filter about 25 Hz wide at very low frequencies, widening in proportion to frequency towards about 11 % of the centre frequency.
```

The formula is an average fit, not a sharp boundary: real filters overlap, and their widths change with level and between listeners.

The practical consequence is that a fixed spacing in hertz means very different things in different registers. Two bass parts a few tens of hertz apart fall inside the same or neighbouring auditory filters, while two bright parts the same number of hertz apart at 4 kHz are, to the ear, practically on top of each other. EQ-ing space between parts, or choosing different octaves, does more for clarity than turning one of them up.

## Key takeaways
- Masking depends on spectrum, timing and level.
- Auditory filters overlap and generally widen as centre frequency rises.
- ERB summarizes a filter response; it is not a sharp separation boundary.

## Further reading
- [Auditory processing — Brian C. J. Moore](https://pmc.ncbi.nlm.nih.gov/articles/PMC2606789/)
- [Noise regulations — HSE](https://www.hse.gov.uk/noise/regulations.htm)
- [Control of Noise at Work Regulations 2005, regulation 4](https://www.legislation.gov.uk/uksi/2005/1643/regulation/4/made)
- [WHO safe-listening venues standard summary](https://cdn.who.int/media/docs/default-source/documents/health-topics/deafness-and-hearing-loss/mls_whd_infographic.pdf?sfvrsn=93a7a1ef_5)
