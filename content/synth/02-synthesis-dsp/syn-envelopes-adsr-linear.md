---
id: syn-envelopes-adsr-linear
title: ADSR stages and linear segments
level: intermediate
minutes: 3
summary: ADSR stages and linear segments.
sourceLesson: syn-envelopes
---

A note isn't just a pitch and a timbre; it has a shape in time. A piano note strikes and decays, an organ note starts and stops abruptly, a pad swells. The **envelope** generates that shape as a control signal, usually driving the amplifier (loudness) and often the filter cutoff (brightness).

The same maths solves a second problem: when a knob or MIDI controller changes a parameter in steps, the audio must not step with it. That's **parameter smoothing**.

## ADSR

The classic envelope has four controls, triggered by the key's **gate** (on while held):

- **Envelope attack:** time to rise from the current level to the peak after the key goes down.
- **Decay stage:** time to fall from the peak to the sustain level.
- **Sustain level:** a *level* (not a time), held while the key stays down.
- **Envelope release:** time to fall to zero after the key is released.

```diagram
level
 1.0 |   /\
     |  /  \___________  <- sustain
     | /               \
 0.0 |/                 \____
     +--A--D-----S------R---> time
     gate on      gate off
```

### Linear segments

The simplest implementation moves the level by a fixed step per sample. For an attack from 0 to 1 the step is the total rise divided by the number of samples the attack lasts.

A longer segment spreads the same change across more samples, so each step is smaller. If a retrigger starts partway up, compute the step from the current level rather than assuming the starting level is zero.

Decay and release work the same way, using the distance they have to travel. It's easy to reason about, and each segment ends at a precise time.

Linear segments have a drawback for amplitude: hearing is roughly logarithmic, so a linear fade in *amplitude* sounds like it hangs on, then vanishes abruptly at the end. Linear attacks often sound fine; linear releases and decays often sound unnatural.

## Key takeaways

- Sustain is a level; attack, decay and release controls describe transitions.
- Linear ramps spread a chosen distance across a fixed number of samples.

## Further reading

- [Envelope generators — Nigel Redmon](https://www.earlevel.com/main/2013/06/01/envelope-generators/)
- [Minimoog Model D user guide — Moog](https://cdn.inmusicbrands.com/Moog/Model%20D/Minimoog_Model_D_Manual.pdf)
