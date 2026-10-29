---
id: midi-studio-integration-monitor-latency
title: Estimate and measure monitoring latency
level: advanced
minutes: 3
sourceLesson: midi-studio-integration
summary: Block duration is a timing unit, not a complete measured latency; compare direct and software monitoring on the actual setup.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Monitoring and latency

Latency adds up along the chain: MIDI transmission, your synth's processing, the interface's converters, and the computer's audio buffers if you monitor through Ableton. Two pieces are easy to reason about.

**Audio buffers.** Software processes audio in blocks (buffers). A block's duration is its sample count divided by the sample rate, so doubling the block size doubles the time it represents:

```formula reference
t_buf = N / f_s
where
t_buf: the time one buffer of audio represents, in seconds (s)
N: the audio block size, in samples
f_s: the sample rate, in samples per second (hertz, Hz)
Hz: hertz, here samples per second
s: seconds
In words: a buffer lasts its number of samples divided by the sample rate; 128 samples at 48 kHz is about 2.7 ms.
```

| Block at 48 kHz | Duration |
|---|---|
| 64 samples | about 1.3 ms |
| 128 samples | about 2.7 ms |
| 256 samples | about 5.3 ms |
| 512 samples | about 10.7 ms |

That duration is a timing unit, not a measured latency. How many buffers sit in the path depends on the driver and software, and converters and drivers add their own delays.

**DIN MIDI.** Each byte takes 0.32 ms on the wire. A four-note chord sent with running status is 9 bytes (one status byte plus two data bytes per note), about 2.9 ms; without running status it is 12 bytes, about 3.8 ms. That is a minimum for back-to-back bytes: other traffic (clock, CCs) queued ahead of a note delays it further.

Putting it together:

- **MIDI transmission**: about 1 ms per three-byte message on DIN.
- **Your synth's audio block**: if it processes 48-sample blocks at 48 kHz, notes can wait up to 1 ms for the next block, plus the codec's own conversion delay (see your board's documentation).
- **Ableton monitoring**: the interface's input buffer, Live's processing and the output buffer, plus converter delays. At 128 samples per buffer and 48 kHz, one buffer represents 2.67 ms. In a simple one-input-buffer plus one-output-buffer model that is about 5.33 ms, before additional delays; use measured or driver-reported audio monitoring latency for the actual hardware.

Practical consequences:

- If you hear the synth *through Ableton* while playing it from the Digitakt, you add the audio monitoring delay. Use **direct monitoring** on the interface (and set the track's monitor to Off) when tight feel matters.
- For recordings, Live compensates: with monitoring In or Auto, "Keep Monitoring Latency in Recorded Audio" aligns the recording with what you heard; with monitoring Off, Live's manual points to the Overall Latency adjustment in its Audio settings.
- Measure rather than guess: record a Digitakt sound and your synth triggered on the same step, and measure the offset in samples on the waveforms.

## Key takeaways
- Latency is a sum of stages; buffer duration (samples divided by sample rate) and DIN wire time are the easy parts to estimate.
- Monitoring through Ableton adds input and output buffering, so use the interface's direct monitoring when feel matters.
- Treat estimates as a guide, and measure the real offset on recorded waveforms.

## Further reading
- [Digitakt II user manual (OS 1.17) — Elektron](https://www.elektron.se/wp-content/uploads/2026/10/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf)
- [Digitakt user manual (OS 1.53) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
- [Digitakt II support and downloads — Elektron](https://www.elektron.se/support-downloads/digitakt-ii)
- [Live 12 manual: Routing and I/O (monitoring, external instruments) — Ableton](https://www.ableton.com/en/live-manual/12/routing-and-i-o/)
- [Live 12 manual: External Instrument device — Ableton](https://www.ableton.com/en/live-manual/12/live-instrument-reference/)
- [Live 12 manual: Synchronizing with Link, Tempo Follower and MIDI — Ableton](https://www.ableton.com/en/live-manual/12/synchronizing-with-link-tempo-follower-and-midi/)
- [Ground loop (electricity) — Wikipedia](https://en.wikipedia.org/wiki/Ground_loop_(electricity))
