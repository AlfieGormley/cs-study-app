---
id: aud-hearing-listening-dose
title: Noise dose and safe-listening guidance
level: basic
minutes: 4
summary: NIOSH’s recommended eight-hour reference is 85 dBA with a three-decibel noise-dose exchange rate.
sourceLesson: aud-hearing
---

## Noise dose and listening guidance

**NIOSH (US) recommended exposure limit:** **85 dB(A)** averaged over an eight-hour day, with a **3 dB noise-dose exchange rate**: every 3 dB increase halves the allowed time. A 3 dB increase doubles the sound energy, so halving the time keeps the total energy (the dose) the same:

```formula
T = 480 / 2^{(L − 85) / 3}
where
T: the time to reach the NIOSH reference daily dose, in minutes (min)
480: eight hours, in minutes
L: the steady A-weighted exposure level, in dB(A)
85: the NIOSH recommended exposure limit for eight hours, in dB(A)
3: the noise-dose exchange rate, in decibels: each 3 dB step halves the time
2^{(L − 85) / 3}: 2 raised to the number of 3 dB steps above 85 dB(A)
In words: start from 8 hours at 85 dB(A) and halve the time for every 3 dB louder.
```

Worked example at a steady 100 dB(A):

```formula
T = 480 / 2^{(100 − 85) / 3}
T = 480 / 2^5
T = 480 / 32 = 15 min
where
T: the time to reach the reference dose, in minutes
min: minutes
In words: 100 dB(A) is five 3 dB steps above 85, so the time halves five times, from 480 to 15 minutes.
```

The same calculation for several levels, as a program:

```python
# Reference-dose time, not guaranteed safe.
for level in (85, 88, 91, 94, 97, 100):
    minutes = 480 / 2 ** ((level - 85) / 3)
    print(f"{level} dBA: "
          f"{minutes:5.0f} min")
```

```output
85 dBA:   480 min
88 dBA:   240 min
91 dBA:   120 min
94 dBA:    60 min
97 dBA:    30 min
100 dBA:    15 min
```

A steady 100 dB(A) exposure reaches the NIOSH reference daily dose in **15 minutes**, before adding other exposure that day. This is a risk-management limit, not a guarantee of no hearing damage.

**WHO:**
- The WHO–ITU standard for personal audio devices sets a reference weekly allowance of **80 dB for 40 hours a week** for adults (75 dB for children).
- The **WHO Global Standard for Safe Listening Venues and Events** (2022) recommends a maximum of **100 dB LAeq over any 15 minutes** for audiences, alongside monitoring, hearing protection, quiet zones and other measures. This is a ceiling, not a recommended operating target or a guarantee of safety for an entire event.

> [!warning] Protect your hearing while building and testing
> - Bring levels up gradually. A DIY synth can produce a full-scale square wave or a feedback screech the moment you change a line of code.
> - Set headphone and monitor volume *before* putting headphones on, and start low.
> - Use a limiter on the monitoring path while developing.
> - Wear musicians' earplugs at gigs and loud rehearsals; they reduce level fairly evenly across frequency.

## Key takeaways
- NIOSH’s recommended eight-hour reference is 85 dBA with a three-decibel noise-dose exchange rate.
- Other daily exposures add to the total dose.
- WHO venue and personal-device recommendations use different reference periods and additional protective measures.

## Further reading
- [Auditory processing — Brian C. J. Moore](https://pmc.ncbi.nlm.nih.gov/articles/PMC2606789/)
- [Noise regulations — HSE](https://www.hse.gov.uk/noise/regulations.htm)
- [Control of Noise at Work Regulations 2005, regulation 4](https://www.legislation.gov.uk/uksi/2005/1643/regulation/4/made)
- [WHO safe-listening venues standard summary](https://cdn.who.int/media/docs/default-source/documents/health-topics/deafness-and-hearing-loss/mls_whd_infographic.pdf?sfvrsn=93a7a1ef_5)
- [Noise exposure and exchange rate — NIOSH](https://www.cdc.gov/niosh/noise/about/noise.html)
- [Personal-device reference sound allowances — WHO](https://www.who.int/news-room/questions-and-answers/item/deafness-and-hearing-loss-safe-listening)
- [WHO–ITU personal-device reference allowances](https://cdn.who.int/media/docs/default-source/documents/health-topics/deafness-and-hearing-loss/standard-summary-make-listening-safe.pdf?sfvrsn=fc114686_14)
