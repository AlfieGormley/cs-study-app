---
id: midi-fundamentals-note-frequency
title: Turn note numbers into frequencies
level: basic
minutes: 4
sourceLesson: midi-fundamentals
summary: MIDI specifies note numbers; the equal-tempered frequency calculation additionally assumes a tuning reference.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Note on and note off

The two messages your synth must handle first:

| Message | Status | Data 1 | Data 2 |
|---|---|---|---|
| Note Off | `0x8n` | key (0–127) | release velocity |
| Note On | `0x9n` | key (0–127) | velocity (0–127) |

The letter in the final hexadecimal position labels the channel nibble; it is not a literal hexadecimal digit. The key number identifies the note: the MIDI specification gives **middle C a value of 60**. Each step is a semitone, so 61 is C♯, 72 is the C an octave up.

Converting a key number to a frequency is a convention from the MIDI Tuning Standard and equal temperament, not something the Note On message carries. Key 69 is A at 440 Hz, and every semitone multiplies the frequency by the same factor, about 1.0595 (the twelfth root of 2), so twelve semitones exactly double it. Pitch is therefore a *ratio* scale: equal steps in key number give equal frequency ratios, not equal numbers of hertz. Your oscillator needs this conversion every time a note starts:

```formula essential
f = 440 Hz × 2^{(n − 69) / 12}
where
f: the frequency the oscillator should play, in hertz (Hz)
n: the MIDI key number, 0 to 127; 60 is middle C, 69 is the A above it
440 Hz: the tuning anchor, the A above middle C (key 69)
Hz: hertz, cycles per second
2^{…}: 2 raised to the power in braces; a power of 1 doubles, −1 halves, 1/12 is one semitone up
In words: count semitones away from key 69, divide by 12 to get octaves, and double 440 Hz once per octave up (or halve it once per octave down).
```

Some landmarks make the pattern easy to check: key 81 is an octave above 69, so 880 Hz; key 57 is an octave below, so 220 Hz; middle C (key 60) is about 261.63 Hz. Halfway between two octave landmarks in key number is *not* halfway in hertz: key 75 sits six semitones above A440 and plays about 622 Hz, not the arithmetic midpoint of 660 Hz. Firmware often stores the 128 results in a table rather than computing powers at note-on.

This holds only for standard 12-tone equal temperament tuned to a 440 Hz reference A. A synth with a different tuning reference or a microtonal scale uses a different formula or table.

> [!note] Octave names differ, numbers don't
> Devices disagree about what to *call* note 60. Ableton Live's note ruler starts at C-2 (note 0), so Live calls middle C (60) **Live C3**. Elektron's Digitakt manuals number notes from Digitakt C0 (note 0, through Digitakt G10 for note 127); the original Digitakt manual states outright that MIDI note 60, middle C, is **Digitakt C5**. Much other software calls it C4. The number 60 is what goes on the wire, so debug with numbers.

## Key takeaways
- Note On carries a key number (middle C = 60), not a frequency.
- Equal temperament makes every semitone the same frequency ratio, so octaves double and in-between notes must be computed exponentially, not interpolated linearly.
- The 440 Hz reference for A and the 12-tone scale are tuning choices layered on top of MIDI; device note *names* differ, so debug with numbers.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [MIDI tuning standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [Live 12 manual: Editing MIDI — Ableton](https://www.ableton.com/en/live-manual/12/editing-midi/)
- [Digitakt user manual (OS 1.53; MIDI track note range) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
