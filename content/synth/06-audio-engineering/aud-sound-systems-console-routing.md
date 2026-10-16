---
id: aud-sound-systems-console-routing
title: Follow a console channel and its sends
level: advanced
minutes: 3
summary: Each system stage has noise and overload limits.
sourceLesson: aud-sound-systems
---

Up to now we've looked at parts: microphones, drivers, boxes, crossovers, amplifiers. A **sound system** connects them so that a source (your synth, a voice, a drum) reaches listeners at the right level, with the right balance and without noise, distortion or feedback. Whether it's a desk in your bedroom or a festival PA, the principles are the same.

## The chain

```flow
Source: synth, mic or instrument
DI box or mic: to balanced mic/line level
Console: preamp gain, EQ, routing, mix
Processing: system EQ, delay, crossover
Power amplifiers (or powered speakers)
Loudspeakers
Room and listeners
```

Every stage has a **noise floor** below the signal and a **clipping point** above it. The job is to keep the signal comfortably between them at every stage.

## The mixing console

A console (mixer, desk) combines many inputs into a few outputs, with independent control over each. Digital consoles and DAWs (Ableton's mixer included) copy the analogue layout, so learning one teaches you the others.

### The channel strip

Signal flows from top to bottom of a typical channel:

1. **Input and preamp gain (trim).** Brings mic or line level up to the console's internal operating level. This is the most important control on the desk for noise and headroom. Phantom power and a pad switch usually live here.
2. **High-pass filter.** Removes rumble and handling noise below the useful range of the source. Engage it only where removing those frequencies suits the source and the intended sound.
3. **Insert point.** A send and return that loops the channel's signal out to an external processor (a compressor, say) and back, in series.
4. **EQ.** Shelving and parametric bands for tone and to make room for other sources.
5. **Dynamics processing** (on many digital desks): gate and compressor.
6. **Aux sends.** Copies of the channel at an adjustable level to separate **aux buses**, used for monitor mixes and effects.
   - **Pre-fader** sends ignore the channel fader: right for **monitor mixes**, so the front-of-house engineer's fader moves don't change what the performer hears.
   - **Post-fader** sends follow the fader: right for effects like reverb, so the wet signal fades with the dry.
7. **Panning** places the signal in the stereo bus.
8. **Fader** sets the channel's level in the mix.
9. **Signal routing** assigns the channel to the main mix and/or **subgroups**.

### Buses and subgroups

A **mix bus** is any point where signals are summed. The main L/R mix is a bus; so are aux sends and subgroups.

- **Subgroups** sum related channels (all drums, all backing vocals) to one fader, so you can ride a whole section, or compress it together, with one control.
- **VCA or DCA groups** (on many consoles) are a variation: one fader remotely controls the faders of its member channels without summing audio.

## Key takeaways
- Each system stage has noise and overload limits.
- Pre-fader sends can keep monitor mixes independent of channel fader moves.
- Subgroups sum audio; VCA and DCA groups control channel gains.

## Further reading
- [Setting system level controls — Rane](https://www.ranecommercial.com/legacy/note135.html)
- [Acoustic feedback — Rane](https://www.ranecommercial.com/legacy/note158.html)
- [Keyboard stage connections — Radial](https://www.radialeng.com/blog/how-to-manage-any-keyboard-setup-on-stage)
