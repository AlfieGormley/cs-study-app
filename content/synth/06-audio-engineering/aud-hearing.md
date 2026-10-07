---
id: aud-hearing
title: Hearing and psychoacoustics
level: basic
minutes: 16
summary: The range of human hearing, equal-loudness contours (ISO 226), A and C weighting, masking and critical bands, how we localise sound with time and level differences, the precedence (Haas) effect, and the exposure limits that protect your hearing.
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

Play a 100 Hz tone and a 1 kHz tone at the same dB SPL and the 100 Hz tone sounds much quieter. An **equal-loudness contour** joins up the levels at which pure tones of different frequencies sound equally loud. Each contour is labelled in **phons**: the *n*-phon contour passes through *n* dB SPL at 1 kHz.

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

(A sketch of the shape only: read real values from ISO 226 or the Wikipedia page below.)

Three things to take from the curves:

- **Bass needs much more SPL** than mid frequencies to sound equally loud, especially at low listening levels.
- **The curves flatten as level rises.** The difference between bass and mids is smaller at 80 phon than at 20 phon.
- So **a mix sounds different at different volumes.** Turn it down and the bass and extreme treble seem to fade first. Mix at one consistent, moderate level, and check at quiet and loud levels.

## A and C weighting

Sound level meters apply a **frequency weighting** to make a single number track human response better. The two that matter, both defined for sound level meters in **IEC 61672-1**:

- **A-weighting** (dB(A) or dBA) strongly reduces low frequencies (about −19 dB at 100 Hz, −30 dB at 50 Hz) and slightly boosts 2–4 kHz. It was based on the 40-phon Fletcher–Munson curve. It is the standard weighting for noise exposure and for many noise-floor specifications.
- **C-weighting** (dB(C)) is nearly flat from about 31.5 Hz to 8 kHz (−3 dB points). It is used for **peak** measurements, and for loud, bass-heavy sound where A-weighting would hide the low end.
- **Z-weighting** is flat ("zero").

```python
import math

def a_weight(f):
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

```
   50 Hz:  -30.3 dB
  100 Hz:  -19.1 dB
 1000 Hz:    0.0 dB
 4000 Hz:    1.0 dB
10000 Hz:   -2.5 dB
```

> [!note] Why live engineers watch dB(C) as well as dB(A)
> A kick drum and sub-bass can carry enormous energy at 40–60 Hz while barely moving a dB(A) meter. Venues often monitor both.

## Masking

A loud sound can make a quieter one inaudible. This is **masking**, and it's the reason a mix "gets muddy": parts that each sound fine alone hide each other when played together.

- **Simultaneous masking** is strongest when the two sounds are **close in frequency**.
- It **spreads upwards**: a loud low sound masks higher frequencies much more effectively than a loud high sound masks lower ones. The effect grows with level. That's why a heavy bass part can dull a whole mix.
- **Temporal masking** also happens: a loud sound can hide quieter sounds just after it (and, briefly, just before it).

Lossy codecs such as MP3 and AAC exploit masking: they spend fewer bits on what masking will hide anyway.

## Critical bands, intuitively

The cochlea behaves like a bank of overlapping band-pass filters. Critical-band measurements and auditory-filter bandwidths both describe frequency selectivity, but their numerical widths depend on how they are measured. ERB is the width of an ideal rectangular filter with the same peak gain and integrated response as the actual filter. Two tones inside one band interact strongly: they mask each other, beat or sound rough. Tones in well-separated bands are heard more independently.

The bands are narrow at low frequencies and wider at high frequencies. One standard model, Glasberg and Moore's **equivalent rectangular bandwidth (ERB)**, approximates the bandwidth for young normally hearing listeners at moderate levels as:

```
ERB = 24.7 * (4.37 * f / 1000 + 1)  Hz
```

| Centre | ERB |
|---|---|
| 100 Hz | ≈ 36 Hz |
| 1 kHz | ≈ 133 Hz |
| 4 kHz | ≈ 457 Hz |

In practice: two bass parts a few tens of hertz apart are fighting inside the same band, so EQ-ing space between parts (or choosing different octaves) does more for clarity than turning one up.

## Localisation: ITD and ILD

You locate a sound left or right mainly from two cues:

- **Interaural time difference (ITD).** A sound from the side reaches the near ear first. Maximum adult ITDs are of order 0.6–0.7 ms and vary with head size, frequency and source direction; simply dividing ear spacing by sound speed neglects diffraction around the head. ITD (as phase differences) is the main cue at **low frequencies**, below about 1 kHz.
- **Interaural level difference (ILD).** The head casts an acoustic shadow, but only for wavelengths small compared with the head (lesson 1's diffraction rule). So ILD is the main cue at **high frequencies**, above about 1.5 kHz.

Between roughly 1 and 1.5 kHz both cues contribute. This "duplex theory" goes back to Lord Rayleigh (1907). Neither cue separates front from back or up from down; for those the brain uses the filtering of the **outer ear (pinna)** and small head movements.

> [!tip] Why one subwoofer is usually enough
> At very low frequencies the head casts almost no shadow (so ILD vanishes), the interaural time difference becomes a tiny fraction of a cycle, and in a room the modes and reflections swamp what cues remain. So localisation of deep bass is poor, which is why a single subwoofer can usually be placed off-centre without the bass seeming to come from it. An 80 Hz crossover is a common system choice, not a hard hearing boundary; it only works if the crossover is low and the sub's distortion and port noise don't add higher-frequency content you *can* locate.

## The precedence (Haas) effect

In a room, you hear the direct sound plus many reflections from other directions, yet you perceive one sound coming from the source. The **precedence effect** is the reason: the auditory system localises a sound by the **first-arriving wavefront** and suppresses the direction of early reflections.

Precedence depends on signal, level, delay, direction and listening conditions. Fusion (hearing one event), localization dominance (hearing it toward the first source), and suppression of information about the reflection are related but distinct; one can persist after another breaks down. There is no universal delay/level boundary guaranteeing all three. Exact Haas-derived limits are absent here because their original experimental conditions were not reliably established in this review.

This has a direct engineering use (lesson 8): a **delay speaker** is aligned using the difference between stage-to-listener and fill-to-listener travel times, plus any deliberately chosen precedence offset. Account for electronic latency, then measure and listen across the coverage area. A large offset can cause audible echoes or comb filtering rather than guarantee stage localization.

## Hearing damage and safe exposure

Noise-induced hearing loss is permanent. It depends on **level and time together**: the dose. Tinnitus (ringing) after a loud session is a warning sign.

**Great Britain workplaces: Control of Noise at Work Regulations 2005** (HSE). These apply to music and entertainment work too.

| Threshold | Daily LEP,d / weekly LEP,w | Peak (LCpeak) |
|---|---|---|
| Lower action value | 80 dB(A) | 135 dB(C) |
| Upper action value | 85 dB(A) | 137 dB(C) |
| Exposure limit | 87 dB(A) | 140 dB(C) |

At the lower action value the employer must assess the risk, provide information and training, and make hearing protection available to anyone who asks for it; at the upper one, hearing protection and hearing protection zones become mandatory. The exposure limit values take account of the reduction given by hearing protection and must not be exceeded; the action values do not (regulation 4(5)), so they're judged on unprotected exposure.

**NIOSH (US) recommended exposure limit:** **85 dB(A)** averaged over an eight-hour day, with a **3 dB exchange rate**: every 3 dB increase halves the allowed time.

```python
for level in (85, 88, 91, 94, 97, 100):
    minutes = 480 / 2 ** ((level - 85) / 3)
    print(f"{level} dBA: "
          f"{minutes:5.0f} min")
```

```
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
- Hearing nominally covers 20 Hz–20 kHz; the top end falls with age, and sensitivity peaks around 2–5 kHz.
- Equal-loudness contours (ISO 226, revised 2023) show that bass needs more SPL to sound as loud, especially at low levels, so mixes change with volume.
- A-weighting cuts low frequencies heavily and is used for exposure; C-weighting is nearly flat and used for peaks and bass-heavy sound.
- Masking is strongest within a critical band and spreads upwards in frequency.
- Left–right localisation uses ITD at low frequencies and ILD at high frequencies; the precedence effect localises by the first arrival.
- Great Britain’s workplace action values are 80 and 85 dB(A) (peaks 135 and 137 dB(C)), with limits of 87 dB(A) and 140 dB(C); NIOSH recommends 85 dB(A) for 8 h with a 3 dB exchange rate.

## Further reading
- [Equal-loudness contour — Wikipedia](https://en.wikipedia.org/wiki/Equal-loudness_contour)
- [Equal loudness curves — HyperPhysics](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/eqloud.html)
- [A-weighting — Wikipedia](https://en.wikipedia.org/wiki/A-weighting)
- [Auditory masking — Wikipedia](https://en.wikipedia.org/wiki/Auditory_masking)
- [Equivalent rectangular bandwidth — Wikipedia](https://en.wikipedia.org/wiki/Equivalent_rectangular_bandwidth)
- [Sound localization — Wikipedia](https://en.wikipedia.org/wiki/Sound_localization)
- [Precedence effect — Wikipedia](https://en.wikipedia.org/wiki/Precedence_effect)
- [Noise at work: a brief guide to controlling the risks (INDG362) — HSE](https://www.hse.gov.uk/pubns/indg362.pdf)
- [Noise regulations — HSE](https://www.hse.gov.uk/noise/regulations.htm)
- [Control of Noise at Work Regulations 2005, regulation 4 — legislation.gov.uk](https://www.legislation.gov.uk/uksi/2005/1643/regulation/4/made)
- [About noise and occupational hearing loss — NIOSH](https://www.cdc.gov/niosh/noise/about/noise.html)
- [Global standard for safe listening venues and events (infographic) — WHO](https://cdn.who.int/media/docs/default-source/documents/health-topics/deafness-and-hearing-loss/mls_whd_infographic.pdf?sfvrsn=93a7a1ef_5)
- [WHO–ITU standard for safe listening devices: summary — WHO](https://cdn.who.int/media/docs/default-source/documents/health-topics/deafness-and-hearing-loss/standard-summary-make-listening-safe.pdf?sfvrsn=fc114686_14)
