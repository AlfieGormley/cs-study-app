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

Converting a key number to a frequency is a convention from the MIDI Tuning Standard and equal temperament: key 69 is A at 440 Hz, and each semitone multiplies the frequency by the same factor, the twelfth root of 2 (about 1.0595), so that twelve semitones exactly double it. Your oscillator needs this conversion every time a note starts:

```formula
f = 440 Hz × 2^{(n − 69) / 12}
f = 440 Hz × 2^{(60 − 69) / 12}
f = 440 Hz × 2^{−0.75}
f ≈ 261.63 Hz
where
f: the frequency the oscillator should play, in hertz (Hz)
n: the MIDI key number, 0 to 127; 60 is middle C, 69 is the A above it
440 Hz: the tuning anchor, the A above middle C (key 69)
Hz: hertz, cycles per second
2^{…}: 2 raised to the power in braces; a power of 1 doubles, −1 halves, 1/12 is one semitone up
≈: approximately equal to (the result is rounded)
In words: count semitones away from key 69, divide by 12 to get octaves, and double 440 Hz once per octave up (or halve it once per octave down).
```

Worked examples: key 81 is 12 semitones above 69, so the power is 1 and the frequency is 880 Hz; key 57 is 12 below, so the power is −1 and it is 220 Hz. This holds only for standard 12-tone equal temperament tuned to a 440 Hz reference A; a synth with a different tuning reference or a microtonal scale uses a different formula or table. The same calculation in Python:

```python
# Offline 12-TET tuning: note 69 is A440.
def note_to_hz(n):
    # A twelve-note change doubles
    # frequency.
    return 440.0 * 2 ** ((n - 69) / 12)

# Output is note number then hertz.
for n in (60, 69, 36):
    print(n, round(note_to_hz(n), 2))
```

```output
60 261.63
69 440.0
36 65.41
```

> [!note] Octave names differ, numbers don't
> Devices disagree about what to *call* note 60. Ableton Live's note ruler starts at C-2 (note 0), so Live calls middle C (60) **Live C3**. Elektron's Digitakt manuals number notes from Digitakt C0 (note 0, through Digitakt G10 for note 127); the original Digitakt manual states outright that MIDI note 60, middle C, is **Digitakt C5**. Much other software calls it C4. The number 60 is what goes on the wire, so debug with numbers.

## Key takeaways
- MIDI specifies note numbers; the equal-tempered frequency calculation additionally assumes a tuning reference.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [MIDI tuning standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [Live 12 manual: Editing MIDI — Ableton](https://www.ableton.com/en/live-manual/12/editing-midi/)
- [Digitakt user manual (OS 1.53; MIDI track note range) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
