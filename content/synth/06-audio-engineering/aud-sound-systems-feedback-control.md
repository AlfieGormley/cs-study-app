---
id: aud-sound-systems-feedback-control
title: Improve gain before acoustic feedback
level: advanced
minutes: 4
summary: Feedback depends on reinforcing loop phase as well as gain.
sourceLesson: aud-sound-systems
---

## Acoustic feedback

**Acoustic feedback** happens when the sound from a speaker re-enters a microphone, is amplified, comes out of the speaker louder, and so on. Sustained feedback can develop where the **loop gain** magnitude reaches or exceeds one (0 dB) and the phase reinforces the circulating signal. The precise stability and onset depend on the whole loop. Feedback develops at a frequency where both loop magnitude and reinforcing phase conditions are met: often a peak in a speaker's or mic's response, or a room resonance.

How to get more **gain before feedback**:

1. **Get the mic close to the source.** Halving the source-to-mic distance gives about 6 dB more source level at the mic (inverse square law), so 6 dB less gain is needed.
2. **Keep speakers away from mics**, and put main speakers in front of the mic line.
3. **Use directional mics and their nulls.** Put wedges in the null of the mic's pattern (the microphone units).
4. **Fewer open mics.** In the usual approximate potential-acoustic-gain model, doubling similarly coupled **open microphones (NOM)** costs about 3 dB; actual loop paths can differ. Mute what isn't in use.
5. **EQ.** "Ringing out" the system: raise gain until it starts to ring, identify the frequency, and cut it with a narrow EQ band. Automatic notch-based feedback suppressors do this live, but they typically add only a few dB of margin.
6. **In-ear monitors** remove the wedge-to-mic path when wedges are actually removed from that mix.

The 6 dB figure in step 1 comes from the inverse square law. For a small source in open air, the level change when you move from one distance to another is:

```formula
L_d = 20 log_10(r_1 / r_2)
L_d = 20 log_10(0.10 / 0.05)
L_d ≈ 20 × 0.301 ≈ 6.0 dB
where
L_d: how much louder the source is at the new distance, in decibels (dB)
log_10: the base-10 logarithm: the power you raise 10 to in order to get the number
r_1: the old source-to-mic distance, in metres (m); here 10 cm = 0.10 m
r_2: the new, closer distance, in metres (m); here 5 cm = 0.05 m
dB: decibels, a logarithmic ratio of levels
In words: every halving of the distance gives about 6 dB more level at the mic, so the channel needs 6 dB less gain for the same output.
```

Very close to a directional mic, the proximity effect also boosts the bass, and a voice is not a point source, so treat 6 dB per halving as a guide.

The 3 dB figure in step 4 comes from the potential acoustic gain (PAG) model, where open mics that each pick up the PA about equally add up as uncorrelated signals:

```formula
G_NOM = 10 log_10(N_1 / N_2)
G_NOM = 10 log_10(4 / 2)
G_NOM ≈ 10 × 0.301 ≈ 3.0 dB
where
G_NOM: the gain before feedback you get back by reducing the number of open microphones, in decibels (dB)
log_10: the base-10 logarithm
N_1: the number of open microphones (NOM) before muting
N_2: the number of open microphones after muting
dB: decibels
NOM: number of open microphones
In words: each halving of the number of open mics buys back about 3 dB of gain before feedback; each doubling costs about 3 dB.
```

It's 10 rather than 20 because the PAG approximation treats the similarly coupled microphone signals as uncorrelated on average. They are summed as voltages physically; their mean-square contributions add under that modelling assumption. Real stages differ: mics nearer a wedge contribute more than the model assumes.

## Key takeaways
- Feedback depends on reinforcing loop phase as well as gain.
- Improve source pickup while reducing loudspeaker pickup at microphones.
- The open-microphone count rule is an approximation; geometry and individual coupling matter.

## Further reading
- [Setting system level controls — Rane](https://www.ranecommercial.com/legacy/note135.html)
- [Acoustic feedback — Rane](https://www.ranecommercial.com/legacy/note158.html)
- [Keyboard stage connections — Radial](https://www.radialeng.com/blog/how-to-manage-any-keyboard-setup-on-stage)
