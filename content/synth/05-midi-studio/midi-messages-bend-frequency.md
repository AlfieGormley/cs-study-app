---
id: midi-messages-bend-frequency
title: Map pitch bend into a pitch offset
level: intermediate
minutes: 3
sourceLesson: midi-messages
summary: Make the bend mapping explicit, keep centre exact, and account for the one-step asymmetry of the raw value range.
---

## Choosing the pitch-bend range

The 14-bit bend value says only *how far* the wheel has moved; it does not say how many semitones that means. The receiver decides the full-scale bend range, or a sender sets it with RPN 0 (pitch bend sensitivity). ±2 semitones is a common default.

A simple, common mapping treats the distance from centre as a fraction of half the range: centre means no bend, and moving halfway from centre to the top bends up half the range. With a ±2 semitone range, a raw value of 12,288 (halfway between centre and the top) bends up one semitone; set the range to ±12 and the same raw value bends up six.

```formula reference
s = ((v − 8192) / 8192)r
where
s: the pitch offset in semitones; negative bends down, positive bends up
v: the received 14-bit bend value, 0 to 16,383
8192: the centre value, meaning no bend
r: the bend range in semitones, chosen by the receiver or set by RPN 0; 2 for a ±2 semitone range
In words: measure how far the raw value is from centre as a fraction of 8,192, then multiply by the configured range; halfway from centre to the top gives half the range.
```

The offset is then applied like any other pitch interval: one semitone up multiplies the held note's frequency by about 1.0595, the same factor used to turn note numbers into frequencies. Bending A 440 Hz up one semitone gives the B♭ above it, about 466 Hz.

The raw range is asymmetric by one step: there are 8,192 values below centre but only 8,191 above. With the mapping above, full upward bend (16,383) reaches about +1.9998 semitones instead of exactly +2. This is an implementation mapping, not a MIDI-mandated bend law. An implementation can instead divide the upper half by 8,191 so the maximum reaches exactly the configured range; keep the centre exactly zero and document the choice.

> [!warning] Reset bend to centre, not zero
> A raw value of 0 is *full downward* bend. Initialise and reset pitch bend to 8,192. The spec's "Reset All Controllers" (CC 121) likewise returns pitch bend to centre.

## Key takeaways
- The bend value is a position; the bend range (receiver setting or RPN 0) decides how many semitones full scale means.
- Map the distance from centre as a fraction of half the range, keep 8,192 exactly at zero, and reset to centre, never to 0.
- The raw range is one step shorter above centre; document how your mapping handles that.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
