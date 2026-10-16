---
id: midi-synth-handling-controller-smoothing
title: Smooth control targets in audio
level: intermediate
minutes: 3
sourceLesson: midi-synth-handling
summary: Publish control targets safely, then smooth them at audio rate using a coefficient matched to the sample rate.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## 2. Use more resolution where it matters


At 128 steps, a slow filter sweep can produce audible stepping. Options: accept 14-bit pairs (each controller from 0 to 31 paired with the controller 32 higher, such as CC 1 with CC 33) where your controller sends them, and in every case **smooth** the value in the audio callback.

### 3. Smooth in the audio domain

The control code only sets a *target*. The audio callback moves the real parameter towards it a little each sample (a one-pole smoother is the usual tool, covered with synthesis DSP). This reduces abrupt control changes and can make zipper noise and MIDI arrival jitter less audible; smoothing adds response lag and cannot guarantee that every modulation artefact vanishes.

Each sample, the smoother closes a fixed fraction of the remaining gap:

```formula
c_new = c + k(c_target − c)
c_new = 1000 Hz + 0.01 × (2000 Hz − 1000 Hz)
c_new = 1010 Hz
where
c_new: the parameter value used for this sample, here a cutoff in hertz (Hz)
c: the value used for the previous sample
c_target: the latest value the control code published from the CC; 2000 Hz in the example
k: the dimensionless smoothing coefficient, strictly between zero and one for a gradual approach; the choice depends on the sample rate and desired smoothing duration
Hz: hertz, cycles per second
In words: every sample, move one small fixed fraction of the way from where the parameter is to where the knob says it should be.
```

For a fixed target and a coefficient strictly between zero and one, each update reduces the remaining gap without overshooting. At zero it never moves; at one it jumps directly to the target. At 48,000 samples per second with a coefficient of 0.01, the gap shrinks to about 37 % of its starting size in about 100 samples, roughly 2 ms. The pseudocode:

```text
control code, on CC 74 value v:
    cutoff_target = cc_to_cutoff(v)
    publish(cutoff_target)   # safe publish

audio callback, per sample:
    cutoff += k * (cutoff_target - cutoff)
    filter.set_cutoff(cutoff)
```

Keep a single **CC map** table in one place: CC number, parameter, curve and range. Print it into your project docs. Use it when configuring the Digitakt MIDI track's CC slots. The publish/read mechanism must be appropriate for the actual platform; this pseudocode does not supply synchronisation.

## Key takeaways
- Publish control targets safely, then smooth them at audio rate using a coefficient matched to the sample rate.

## Further reading
- [One-pole filters — Julius O. Smith](https://www.dsprelated.com/freebooks/filters/One_Pole.html)
- [MIDI 1.0 Detailed Specification 4.2.1, including the running status appendix (CCRMA copy)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Polyphony and monophony in instruments: note priority — Wikipedia](https://en.wikipedia.org/wiki/Polyphony_and_monophony_in_instruments)
- [MIDI library for Teensy (serial MIDI) — PJRC](https://www.pjrc.com/teensy/td_libs_MIDI.html)
