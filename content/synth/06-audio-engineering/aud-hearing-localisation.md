---
id: aud-hearing-localisation
title: Locate sound and understand precedence
level: basic
minutes: 4
summary: Time differences dominate low-frequency left–right localisation; level differences matter strongly at high frequencies.
sourceLesson: aud-hearing
---

## Localisation: ITD and ILD

You locate a sound left or right mainly from two cues:

- **Interaural time difference (ITD).** A sound from the side reaches the near ear first. Maximum adult ITDs are of order 0.6–0.7 ms and vary with head size, frequency and source direction; simply dividing ear spacing by sound speed neglects diffraction around the head. ITD (as phase differences) is the main cue at **low frequencies**, below about 1 kHz.
- **Interaural level difference (ILD).** The head casts an acoustic shadow, but only for wavelengths small compared with the head (the acoustics units’ diffraction rule). So ILD is the main cue at **high frequencies**, above about 1.5 kHz.

Between roughly 1 and 1.5 kHz both cues contribute. This "duplex theory" goes back to Lord Rayleigh (1907). Neither cue separates front from back or up from down; for those the brain uses the filtering of the **outer ear (pinna)** and small head movements.

> [!tip] Why one subwoofer is usually enough
> At very low frequencies the head casts almost no shadow (so ILD vanishes), the interaural time difference becomes a tiny fraction of a cycle, and in a room the modes and reflections swamp what cues remain. So localisation of deep bass is poor, which is why a single subwoofer can usually be placed off-centre without the bass seeming to come from it. An 80 Hz crossover is a common system choice, not a hard hearing boundary; it only works if the crossover is low and the sub's distortion and port noise don't add higher-frequency content you *can* locate.

## The precedence (Haas) effect

In a room, you hear the direct sound plus many reflections from other directions, yet you perceive one sound coming from the source. The **precedence effect** is the reason: the auditory system localises a sound by the **first-arriving wavefront** and suppresses the direction of early reflections.

Precedence depends on signal, level, delay, direction and listening conditions. Fusion (hearing one event), localization dominance (hearing it toward the first source), and suppression of information about the reflection are related but distinct; one can persist after another breaks down. There is no universal delay/level boundary guaranteeing all three. Exact Haas-derived limits are absent here because their original experimental conditions were not reliably established in this review.

This has a direct engineering use (the sound-system lessons): a **delay speaker** halfway down a field is held back electronically so that its sound arrives *with or just after* the sound from the stage. If it played undelayed, listeners near it would hear it first, localise the band to the delay tower, and then hear the stage arriving later as an echo.

The starting setting is the difference between the stage-to-listener and fill-to-listener travel times (sound covers about 34.3 m in 100 ms), plus any small precedence offset you deliberately choose so the stage wins the race:

```formula reference
t_delay = (d_main − d_fill) / c + t_off
where
t_delay: the electronic delay applied to the delay speaker, in seconds (s) or milliseconds (ms)
d_main: the distance from the main stage speakers to the listener, in metres (m)
d_fill: the distance from the delay speaker to the listener, in metres (m)
c: the speed of sound, about 343 metres per second (m/s) at 20 °C
t_off: an extra delay, expressed in the same time unit as the path-time term, chosen so the stage sound arrives first; an example to evaluate by listening, not a fixed rule
In words: Hold back the delay speaker by the extra time the stage sound needs to reach the listener, plus a little more if you choose, so the stage wins the race.
```

This starting point ignores electronic latency and temperature changes. Account for the latency of the processing in each path, then measure and listen across the coverage area. A large offset can cause audible echoes or comb filtering rather than guarantee stage localisation.

## Key takeaways
- Time differences dominate low-frequency left–right localisation; level differences matter strongly at high frequencies.
- Outer-ear filtering and head movements provide additional direction cues.
- Delay alignment uses path and electronic-latency differences; an extra offset is a design choice to evaluate.

## Further reading
- [Auditory pathways and localisation — David Heeger, NYU](https://www.cns.nyu.edu/~david/courses/perception/lecturenotes/localization/localization.html)
- [Auditory processing — Brian C. J. Moore](https://pmc.ncbi.nlm.nih.gov/articles/PMC2606789/)
- [Noise regulations — HSE](https://www.hse.gov.uk/noise/regulations.htm)
- [Control of Noise at Work Regulations 2005, regulation 4](https://www.legislation.gov.uk/uksi/2005/1643/regulation/4/made)
- [WHO safe-listening venues standard summary](https://cdn.who.int/media/docs/default-source/documents/health-topics/deafness-and-hearing-loss/mls_whd_infographic.pdf?sfvrsn=93a7a1ef_5)
