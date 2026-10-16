---
id: midi-messages-rpn-bank-program
title: Select parameters, banks and programs
level: intermediate
minutes: 2
sourceLesson: midi-messages
summary: Use RPN selection before Data Entry, deselect when done, and apply a selected bank when Program Change arrives.
---

## RPN: setting pitch-bend range


Registered Parameter Numbers (RPNs) select a parameter with CC 101 (MIDI MSB) and CC 100 (MIDI LSB), then set it with Data Entry (CC 6, plus CC 38 for fine). RPN 0,0 is **pitch bend sensitivity**: Data Entry MIDI MSB is semitones, MIDI LSB is cents. To set ±12 semitones on channel 1, a sender transmits:

```
B0 65 00   RPN MSB = 0
B0 64 00   RPN LSB = 0 (bend range)
B0 06 0C   data entry: 12 semitones
B0 26 00   data entry LSB: 0 cents
```

Sending RPN 127,127 (the "null" RPN) afterwards stops later Data Entry messages changing it by accident. NRPNs (CC 99/98) work the same way for manufacturer-defined parameters; the Elektron manuals list which NRPNs their knobs send.

## Program change and bank select

`Cn pp` selects patch `pp`, with a single data byte. Programs are 0–127 on the wire, but many devices display them as 1–128, so the off-by-one appears again.

For more than 128 patches, the specification has the sender transmit Bank Select as a pair (CC 0 MIDI MSB, CC 32 MIDI LSB), immediately followed by the Program Change. Bank Select alone must not change the program; the new bank applies when the Program Change arrives.

## Key takeaways
- Use RPN selection before Data Entry, deselect when done, and apply a selected bank when Program Change arrives.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
