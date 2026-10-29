---
id: syn-envelopes-retrigger-legato
title: Retriggering, clicks and legato
level: intermediate
minutes: 3
summary: Retriggering, clicks and legato.
sourceLesson: syn-envelopes
---

## Retriggering and clicks

A **click** can result when a waveform jumps abruptly; its audibility depends on the jump size and signal at that moment. A gain jump produces an output jump when the underlying waveform is non-zero. Envelopes cause clicks in a few classic ways:

- **Abrupt envelope reset on retrigger.** A note is releasing at level 0.4 and you press another key on the same voice. If the envelope jumps to 0 before attacking, the output gain drops 0.4 in one sample. Instead, start the attack **from the current level**, as the exponential ADSR state machine in the neighbouring unit does.
- **Zero-length attack or release.** A gain jump from 0 to 1 on a waveform that isn't at a zero crossing is a step. Enforce a minimum of around a millisecond or two (a rule of thumb, not a standard).
- **Voice stealing.** Reassigning a sounding voice to a new note jumps both its pitch and its envelope. Fade it out quickly first.
- **Phase reset.** Resetting oscillator phase while a voice is audible can change its output abruptly. A reset at matching waveform values need not create a value step.

Some percussive patches *want* a click (a sharp attack). The point is to choose it, not suffer it.

## Legato and trigger modes

On a mono synth, what happens when you press a new key while still holding the old one?

- **Multi-trigger:** every new note retriggers the envelopes. Each note is articulated.
- **Single-trigger (legato):** if a key is already held, the new note changes pitch only; the envelopes carry on from where they are. Only a fresh press after all keys are up retriggers.

Legato is often paired with **glide** (portamento): the pitch slides to the new note, often controlled in the log-frequency (semitone) domain. A linear ramp in that domain gives equal intervals equal time; an exponential smoother instead slows near its target.

## Key takeaways

- Attacking from the current envelope level avoids a hard gain reset.
- Choose multi-trigger or legato deliberately, and treat phase resets and voice stealing as possible discontinuities.

## Further reading

- [ADSR implementation — Nigel Redmon](https://www.earlevel.com/main/2013/06/03/envelope-generators-adsr-code/)
- [Minimoog Model D user guide — Moog](https://cdn.inmusicbrands.com/Moog/Model%20D/Minimoog_Model_D_Manual.pdf)
