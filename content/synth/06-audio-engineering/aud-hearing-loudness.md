---
id: aud-hearing-loudness
title: Why equal SPL is not equal loudness
level: basic
minutes: 3
summary: Hearing sensitivity varies with frequency, listener and sound level.
sourceLesson: aud-hearing
---

A sound level meter measures pressure. You hear something else: loudness, pitch, direction and timbre, all built by your ear and brain from that pressure. **Psychoacoustics** studies the gap between the two. For anyone mixing, designing speakers or building instruments it explains why a bass line vanishes at low volume, why a quiet pad disappears under a loud lead, and why a delay speaker can be louder than the stage without pulling the image towards it.

It also explains how hearing gets damaged. That part is not optional reading.

## The range of hearing

The commonly quoted range is **20 Hz to 20 kHz**. Treat both ends as soft:

- The top end falls with age and noise exposure. Many adults hear little above 15–16 kHz. Your synth's 18 kHz content may be inaudible to you and obvious to a teenager (or to your dog).
- At the bottom, below about 20 Hz, very loud sound is felt more than heard.
- Hearing is most sensitive roughly between **2 and 5 kHz**, partly because the ear canal resonates in that region.

In level, hearing spans from the threshold near 0 dB SPL at mid frequencies to very high levels that can cause pain and damage. Pain thresholds vary, and harmful exposure can occur far below pain; a 120 dB level difference represents a millionfold pressure ratio.

## Equal-loudness contours

Play a 100 Hz tone and a 1 kHz tone at the same dB SPL and the 100 Hz tone sounds much quieter. An **equal-loudness contour** joins up the levels at which pure tones of different frequencies sound equally loud. Each contour is labelled in **phons**: for example, the forty-phon contour passes through 40 dB SPL at one kilohertz. The standard specifies young, otologically normal listeners, frontal free-field pure tones and binaural listening; it is not a calibration of every listener or broadband music.

The first such curves were Fletcher and Munson's (1933). The current international standard is **ISO 226**. Its 2003 edition replaced older curves that had been shown to be inaccurate, and it was revised again in **2023** with small changes.

```diagram
 dB SPL
 120 |\                        /
     | \___  80 phon     ___/
  80 |     \___________/
     |\
  40 | \___  20 phon     __/
     |     \___________/
   0 +-----+-----+-----+-----+
     20   100    1k    5k   20k Hz
```

(A sketch of the shape only: read real values and listening conditions from the applicable ISO 226 edition.)

Three things to take from the curves:

- **Bass needs much more SPL** than mid frequencies to sound equally loud, especially at low listening levels.
- **The curves flatten as level rises.** The difference between bass and mids is smaller at 80 phon than at 20 phon.
- So **a mix sounds different at different volumes.** Turn it down and the bass and extreme treble seem to fade first. Mix at one consistent, moderate level, and check at quiet and loud levels.

## Key takeaways
- Hearing sensitivity varies with frequency, listener and sound level.
- Equal-loudness contours describe pure tones under specified conditions.
- A mix’s perceived balance changes with listening level.

## Further reading
- [Auditory processing — Brian C. J. Moore](https://pmc.ncbi.nlm.nih.gov/articles/PMC2606789/)
- [Noise regulations — HSE](https://www.hse.gov.uk/noise/regulations.htm)
- [Control of Noise at Work Regulations 2005, regulation 4](https://www.legislation.gov.uk/uksi/2005/1643/regulation/4/made)
- [WHO safe-listening venues standard summary](https://cdn.who.int/media/docs/default-source/documents/health-topics/deafness-and-hearing-loss/mls_whd_infographic.pdf?sfvrsn=93a7a1ef_5)
- [ISO 226:2023 scope and history — Estonian standards body](https://www.evs.ee/en/iso-226-2023)
