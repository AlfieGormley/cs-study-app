---
id: midi-studio-integration-ableton-record-sync
title: Route audio, external MIDI and clock in Live
level: advanced
minutes: 2
sourceLesson: midi-studio-integration
summary: Record the actual audio input, compensate measured external-device timing and choose one tempo source.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Step 3: record into Ableton

For the synth's audio, Ableton Live 12's manual describes the essentials:

1. Create an **audio track**. In its In/Out section, select your interface in Live's Audio settings, then set **Audio From** to **Ext. In** and choose the channel the synth is plugged into.
2. **Arm** the track and record.
3. Choose a **monitoring mode**. **Auto** monitors while the track is armed and not playing clips. **In** always monitors. **Off** relies on the interface's direct monitoring or an external mixer.

If you want Ableton, rather than the Digitakt, to play the synth, the **External Instrument** device sends MIDI out of a chosen port and channel and returns audio from chosen interface inputs. Its **Hardware Latency slider** compensates for delays Live can't detect automatically.

**Clock:** pick one master. Either the Digitakt sends clock (CLOCK SEND) and Live follows it (enable the Digitakt as a sync source in Live's Tempo & MIDI settings, then switch on EXT), or Live sends clock and the Digitakt follows (CLOCK RECEIVE). Live can act as a MIDI Clock host or follower.

## Key takeaways
- Record the actual audio input, compensate measured external-device timing and choose one tempo source.

## Further reading
- [Digitakt II user manual (OS 1.17) — Elektron](https://www.elektron.se/wp-content/uploads/2026/10/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf)
- [Digitakt user manual (OS 1.53) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
- [Digitakt II support and downloads — Elektron](https://www.elektron.se/support-downloads/digitakt-ii)
- [Live 12 manual: Routing and I/O (monitoring, external instruments) — Ableton](https://www.ableton.com/en/live-manual/12/routing-and-i-o/)
- [Live 12 manual: External Instrument device — Ableton](https://www.ableton.com/en/live-manual/12/live-instrument-reference/)
- [Live 12 manual: Synchronizing with Link, Tempo Follower and MIDI — Ableton](https://www.ableton.com/en/live-manual/12/synchronizing-with-link-tempo-follower-and-midi/)
- [Ground loop (electricity) — Wikipedia](https://en.wikipedia.org/wiki/Ground_loop_(electricity))
