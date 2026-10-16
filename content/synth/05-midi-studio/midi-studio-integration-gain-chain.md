---
id: midi-studio-integration-gain-chain
title: Leave headroom at every stage
level: advanced
minutes: 2
sourceLesson: midi-studio-integration
summary: Find the stage that clips and reduce level before it; a later fader cannot repair earlier overload.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Gain staging across the chain

Gain staging means setting each stage's level so the signal stays well above that stage's noise floor and well below its clipping point. In order:

1. **Synth output**: design it to reach line level at full scale (the audio-level units). Don't make it so hot that the interface input can't accept it.
2. **Interface input gain**: set it with your *loudest* patch (high resonance, all oscillators, full velocity). A common rule of thumb is to leave peaks around −12 to −6 dBFS: plenty of headroom, and at 24-bit there's still a large margin above the noise floor. Some systems align analogue nominal levels with −18 or −20 dBFS; your interface's alignment is equipment-dependent, so you don't need to record "hot".
3. **Ableton track**: adjust with the track fader or a utility device, not by going back and changing the input gain mid-session.
4. **Digitakt**: its outputs can deliver up to +18 dBu (II) or +22 dBu (original) peak. Check those maxima against your interface's maximum input level, and use the Digitakt's master level or the interface pad if necessary.

> [!note] Clipping is a stage, not a song
> If you hear distortion, find *which* stage clips: watch the synth's output on a scope, the interface's input meter and Live's track meter in turn. Turning down the end of the chain doesn't fix clipping earlier in it.

Elektron labels these published maximum ratings “dBu peak”. The standard dBu voltage reference is RMS-based; the manufacturer label is quoted here rather than silently converted into waveform peak volts. Confirm the test/measurement convention and permitted input voltage when comparing equipment.

## Key takeaways
- Find the stage that clips and reduce level before it; a later fader cannot repair earlier overload.

## Further reading
- [RMS references and the misleading phrase “peak dBu” — Rane](https://www.ranecommercial.com/legacy/pdf/ranenotes/No_Such_Thing_as_Peak_Volts_dBu.pdf)
- [Digitakt II user manual (OS 1.17) — Elektron](https://www.elektron.se/wp-content/uploads/2026/10/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf)
- [Digitakt user manual (OS 1.53) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
- [Digitakt II support and downloads — Elektron](https://www.elektron.se/support-downloads/digitakt-ii)
- [Live 12 manual: Routing and I/O (monitoring, external instruments) — Ableton](https://www.ableton.com/en/live-manual/12/routing-and-i-o/)
- [Live 12 manual: External Instrument device — Ableton](https://www.ableton.com/en/live-manual/12/live-instrument-reference/)
- [Live 12 manual: Synchronizing with Link, Tempo Follower and MIDI — Ableton](https://www.ableton.com/en/live-manual/12/synchronizing-with-link-tempo-follower-and-midi/)
- [Ground loop (electricity) — Wikipedia](https://en.wikipedia.org/wiki/Ground_loop_(electricity))
