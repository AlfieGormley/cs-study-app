---
id: midi-synth-handling-controller-smoothing
title: Smooth control targets in audio
level: intermediate
minutes: 3
sourceLesson: midi-synth-handling
summary: Publish control targets safely, then smooth them at audio rate using a coefficient matched to the sample rate.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Use more resolution where it matters

At 128 steps, a slow filter sweep can produce audible stepping, called zipper noise. Two remedies work together. Where your controller sends them, accept 14-bit pairs (each controller from 0 to 31 paired with the controller 32 higher, such as CC 1 with CC 33), which make each jump far smaller. And in every case **smooth** the value in the audio callback.

## Smooth in the audio domain

The control code only sets a *target*. The audio callback moves the real parameter towards it a little each sample; a one-pole smoother is the usual tool, covered with synthesis DSP. Each sample it closes a fixed fraction of the remaining gap, so a sudden CC jump becomes a short glide.

That fraction is the smoothing coefficient (`k` in the pseudocode below), a number between zero and one. Near zero the parameter glides slowly; at one it jumps straight to the target, which is no smoothing at all. The right value depends on the sample rate and the glide time you want: at 48,000 samples per second, closing 1% of the gap each sample shrinks it to about 37% of its starting size in roughly 100 samples, about 2 ms. Run the same coefficient at a different sample rate and the glide time changes, so compute it from the sample rate.

Smoothing reduces abrupt control changes and can make zipper noise and MIDI arrival jitter less audible. It also adds response lag, and it cannot guarantee that every modulation artefact vanishes. The pseudocode:

```text
control code, on CC 74 value v:
    cutoff_target = cc_to_cutoff(v)
    publish(cutoff_target)   # safe publish

audio callback, per sample:
    # close fraction k of the gap
    cutoff += k * (cutoff_target - cutoff)
    filter.set_cutoff(cutoff)
```

Keep a single **CC map** table in one place: CC number, parameter, curve and range. Print it into your project docs. Use it when configuring the Digitakt MIDI track's CC slots. The publish/read mechanism must be appropriate for the actual platform; this pseudocode does not supply synchronisation.

## Key takeaways
- Zipper noise comes from 128-step jumps; 14-bit pairs make the jumps smaller and smoothing turns them into glides.
- The control code publishes a target; the audio callback closes a fixed fraction of the gap each sample.
- Choose the smoothing coefficient from the sample rate and the glide time you want, and accept the small response lag it adds.

## Further reading
- [One-pole filters — Julius O. Smith](https://www.dsprelated.com/freebooks/filters/One_Pole.html)
- [MIDI 1.0 Detailed Specification 4.2.1, including the running status appendix (CCRMA copy)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Polyphony and monophony in instruments: note priority — Wikipedia](https://en.wikipedia.org/wiki/Polyphony_and_monophony_in_instruments)
- [MIDI library for Teensy (serial MIDI) — PJRC](https://www.pjrc.com/teensy/td_libs_MIDI.html)
