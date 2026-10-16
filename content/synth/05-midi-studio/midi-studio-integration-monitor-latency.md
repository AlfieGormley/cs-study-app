---
id: midi-studio-integration-monitor-latency
title: Estimate and measure monitoring latency
level: advanced
minutes: 4
sourceLesson: midi-studio-integration
summary: Block duration is a timing unit, not a complete measured latency; compare direct and software monitoring on the actual setup.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Monitoring and latency

Latency adds up along the chain. Two simple formulas cover most of it. First, an audio buffer (or block) represents a duration given by its sample count divided by the sample rate. That duration is a useful timing budget; a particular buffering architecture determines how much latency it contributes:

```formula
t_buf = N / f_s
t_buf = 128 / (48000 Hz)
t_buf ≈ 0.00267 s = 2.67 ms
where
t_buf: the time one buffer of audio represents, in seconds (s) or milliseconds (ms)
N: the audio block size, in samples; 128 here
f_s: the sample rate, in samples per second (hertz, Hz); 48,000 here
Hz: hertz, here samples per second
s: seconds
ms: milliseconds, thousandths of a second
≈: approximately equal to (rounded)
In words: 128 samples at 48 kHz is about 2.7 ms of audio, which gives a time unit for this simplified buffer model rather than a measurement of the full path.
```

Second, DIN MIDI delays a message by the time its bytes take on the wire, 0.32 ms per byte:

```formula
t_MIDI = n t_byte
t_MIDI = (1 + 4 × 2) × 0.32 ms
t_MIDI = 9 × 0.32 ms = 2.88 ms
where
t_MIDI: the time to send the messages, in milliseconds (ms)
n: the number of bytes sent; a four-note chord with running status is 1 status byte plus 2 data bytes per note, 9 bytes
t_byte: the time per byte on DIN MIDI, 0.32 ms (10 bits at 31,250 bit/s)
ms: milliseconds, thousandths of a second
In words: a four-note chord with running status takes about 2.9 ms to send; without running status it is 12 bytes, about 3.8 ms.
```

The DIN wire-time result is a minimum for back-to-back bytes. The buffer duration is a model input, not a universal lower bound on each implementation's latency: drivers and converters add their own delays, and other MIDI traffic (clock, CCs) queued ahead of a note delays it further. The same estimates in Python:

```python
def buffer_ms(samples, rate):
    # Block duration, not measured
    # path latency.
    return samples / rate * 1000

for n in (64, 128, 256, 512):
    print(n, round(buffer_ms(n, 48000), 2))

# DIN MIDI: 320 us per byte
def din_ms(n_bytes):
    return n_bytes * 0.32

# 4-note chord: 1 status + 8 data bytes
print("chord", round(din_ms(1 + 4 * 2), 2))
print("chord, no RS", round(din_ms(12), 2))
```

```output
64 1.33
128 2.67
256 5.33
512 10.67
chord 2.88
chord, no RS 3.84
```

- **MIDI transmission**: about 1 ms per three-byte message on DIN.
- **Your synth's audio block**: if it processes 48-sample blocks at 48 kHz, notes can wait up to 1 ms for the next block, plus the codec's own conversion delay (see your board's documentation).
- **Ableton monitoring**: the interface's input buffer, Live's processing and the output buffer, plus converter delays. At 128 samples per buffer and 48 kHz, one buffer represents 2.67 ms. In a simple one-input-buffer plus one-output-buffer model that is about 5.33 ms, before additional delays; use measured or driver-reported audio monitoring latency for the actual hardware.

Practical consequences:

- If you hear the synth *through Ableton* while playing it from the Digitakt, you add the audio monitoring delay. Use **direct monitoring** on the interface (and set the track's monitor to Off) when tight feel matters.
- For recordings, Live compensates: with monitoring In or Auto, "Keep Monitoring Latency in Recorded Audio" aligns the recording with what you heard; with monitoring Off, Live's manual points to the Overall Latency adjustment in its Audio settings.
- Measure rather than guess: record a Digitakt sound and your synth triggered on the same step, and measure the offset in samples on the waveforms.

## Key takeaways
- Block duration is a timing unit, not a complete measured latency; compare direct and software monitoring on the actual setup.

## Further reading
- [Digitakt II user manual (OS 1.17) — Elektron](https://www.elektron.se/wp-content/uploads/2026/10/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf)
- [Digitakt user manual (OS 1.53) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
- [Digitakt II support and downloads — Elektron](https://www.elektron.se/support-downloads/digitakt-ii)
- [Live 12 manual: Routing and I/O (monitoring, external instruments) — Ableton](https://www.ableton.com/en/live-manual/12/routing-and-i-o/)
- [Live 12 manual: External Instrument device — Ableton](https://www.ableton.com/en/live-manual/12/live-instrument-reference/)
- [Live 12 manual: Synchronizing with Link, Tempo Follower and MIDI — Ableton](https://www.ableton.com/en/live-manual/12/synchronizing-with-link-tempo-follower-and-midi/)
- [Ground loop (electricity) — Wikipedia](https://en.wikipedia.org/wiki/Ground_loop_(electricity))
