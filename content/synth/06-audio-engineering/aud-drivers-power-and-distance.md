---
id: aud-drivers-power-and-distance
title: Work backwards from required listener level
level: intermediate
minutes: 4
summary: Use a consistent reference, spectrum and far-field measurement direction.
sourceLesson: aud-drivers
---

## Power, distance and efficiency

To predict how loud a speaker will be, start from its sensitivity, add the decibels gained by using more than 1 W, and subtract the decibels lost by listening further away than 1 m. For a fixed signal spectrum in the linear range, use this approximate on-axis free-field, far-field estimate (neglecting air absorption and power compression):

```formula reference
SPL = S + 10 log_10(P / 1 W)
      − 20 log_10(r / 1 m)
where
SPL: the sound pressure level at the listener, in decibels (dB SPL)
S: the speaker's sensitivity, in dB SPL at 1 W / 1 m; typically 84–90 dB for hi-fi, over 100 dB for PA horns
P: the amplifier power into the speaker's nominal impedance, in watts (W)
r: the listening distance from the speaker, in metres (m); in the actual source’s far field; one metre is a reference distance, not a universal far-field boundary
log_10: the base-10 logarithm
W: watt
m: metre
dB: decibel
In words: Start from the speaker's sensitivity at 1 watt and 1 metre, add about 3 dB for every doubling of amplifier power and subtract about 6 dB for every doubling of listening distance.
```

The two terms behave very differently, and that asymmetry is the whole lesson:

- **Power buys level slowly.** Each **doubling of power adds only 3 dB**; ten times the power adds 10 dB. An 87 dB/1 W/1 m speaker gives about 97 dB at 1 m with 10 W and about 107 dB with 100 W.
- **Distance takes level away quickly.** Each doubling of distance costs about 6 dB, so moving the audience twice as far away needs **four times** the power to keep the same level.
- **Sensitivity is cheap power.** Every 3 dB of extra sensitivity halves the amplifier power needed for the same level; 6 dB quarters it.

Worked example (from Purdue's notes), reasoning backwards from the listener: you want 90 dB SPL at 4 m outdoors from an 86 dB/1 W/1 m speaker.

1. 4 m is two doublings of 1 m, which costs about 12 dB. So you need about 102 dB at 1 m.
2. That is 16 dB above the speaker's 1 W figure.
3. 16 dB is a power ratio of about 40 (10 dB is ×10, and each further 3 dB roughly doubles it). So about **40 W**.

That 40 W is an *average* power for a steady signal. Music has peaks well above its average: a signal whose peaks are 10 dB above its RMS level (a 10 dB crest factor) needs about ten times the average power at each peak. An amplifier sized only for the average will clip on every drum hit, so leave headroom while respecting the driver's excursion and thermal limits (the amplifier lessons).

Sensitivity is closely related to **loudspeaker efficiency**, the fraction of electrical power that comes out as sound. Typical home loudspeakers are only around 1 % efficient, and often less: Purdue's sample driver, rated 86 dB/1 W/1 m, works out at about 0.2 %, so of that 40 W only around a tenth of a watt leaves as sound. The rest becomes heat, mostly in the voice coil, which is why high power heats the coil and raises its resistance (power compression).

## Key takeaways
- Use a consistent reference, spectrum and far-field measurement direction.
- Distance loss can demand much more power than a sensitivity comparison alone suggests.
- Leave appropriate peak margin while respecting driver excursion and thermal limits.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Baffled piston radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/BaffledPiston/BaffledPiston.html)
- [Rated impedance — Dynaudio](https://dynaudio.com/magazine/2023/july/impedance-ask-the-expert)
