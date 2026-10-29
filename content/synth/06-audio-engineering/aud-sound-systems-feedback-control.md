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

> [!analogy] Real-world analogy: two facing mirrors
> Stand between two mirrors facing each other and you see a corridor of reflections, each a little dimmer than the last, fading away. Imagine instead that each mirror made the image slightly *brighter* every time it bounced: the corridor would blaze up until something saturated.
>
> **How it maps:** One trip round the loop, from speaker through the air into the mic and back out of the speaker, is one bounce. Ordinary mirrors are a loop gain below one: each pass is quieter and the sound dies away (the system "rings" briefly when close). An amplifying mirror is a loop gain at or above one with reinforcing phase: each pass is louder and the howl builds until something clips.
>
> **Where it stops:** Real feedback happens at particular frequencies where the phase round the loop reinforces, not at all frequencies at once, and the loop includes the room's reflections. Mirrors also have no equivalent of EQ: in a sound system you can cut the gain at just the frequency that rings.

How to get more **gain before feedback**:

1. **Get the mic close to the source.** Halving the source-to-mic distance gives about 6 dB more source level at the mic (inverse square law), so 6 dB less gain is needed.
2. **Keep speakers away from mics**, and put main speakers in front of the mic line.
3. **Use directional mics and their nulls.** Put wedges in the null of the mic's pattern (the microphone units).
4. **Fewer open mics.** In the usual approximate potential-acoustic-gain model, doubling similarly coupled **open microphones (NOM)** costs about 3 dB; actual loop paths can differ. Mute what isn't in use.
5. **EQ.** "Ringing out" the system: raise gain until it starts to ring, identify the frequency, and cut it by a few dB with a parametric EQ band. RaneNote 158 warns that very narrow, deep notches cope poorly when temperature or positions change, and favours shallow cuts of moderate width. Automatic notch-based feedback suppressors do this live, but they typically add only a couple of dB of margin.
6. **In-ear monitors** remove the wedge-to-mic path when wedges are actually removed from that mix.

The 6 dB figure in step 1 comes from the inverse square law: every halving of the source-to-mic distance gives about 6 dB more source level at the mic, so the channel needs 6 dB less gain for the same output. Very close to a directional mic, the proximity effect also boosts the bass, and a voice is not a point source, so treat 6 dB per halving as a guide.

The 3 dB figure in step 4 comes from the potential acoustic gain (PAG) model. Each open mic picks up some of the PA, and the model treats those similarly coupled pickups as unrelated signals, which add in power: twice as many open mics is about +3 dB of PA in the mix (like two unrelated sources in the acoustics lessons), so each halving of the number of open mics buys back about 3 dB. Real stages differ: mics nearer a wedge contribute more than the model assumes.

## Key takeaways
- Feedback depends on reinforcing loop phase as well as gain.
- Improve source pickup while reducing loudspeaker pickup at microphones.
- The open-microphone count rule is an approximation; geometry and individual coupling matter.

## Further reading
- [Setting system level controls — Rane](https://www.ranecommercial.com/legacy/note135.html)
- [Acoustic feedback — Rane](https://www.ranecommercial.com/legacy/note158.html)
- [Keyboard stage connections — Radial](https://www.radialeng.com/blog/how-to-manage-any-keyboard-setup-on-stage)
