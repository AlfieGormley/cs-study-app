---
id: midi-messages-controller-pairs
title: Combine coarse and fine controllers
level: intermediate
minutes: 3
sourceLesson: midi-messages
summary: Pair the first 32 controller numbers with their fine controllers, and reset the remembered fine value on a new coarse value.
---

## 14-bit controllers

128 steps are coarse for something like filter cutoff: you can hear each step as a zipper. The specification therefore pairs controllers: **CC 0–31 carry MIDI coarse parts and CC 32–63 carry the matching MIDI fine parts**, always 32 numbers apart. So CC 1 (modulation wheel) pairs with CC 33, and CC 7 (Channel Volume) with CC 39.

Together the two 7-bit halves give 14 bits. The coarse byte counts in big steps of 128 and the fine byte fills in between:

```formula essential
v = 128 MSB + LSB
where
v: the combined 14-bit controller value, 0 to 16,383 (16,384 steps)
MSB: the coarse seven-bit part, from the lower-numbered controller (0–31), a whole number from 0 to 127
LSB: the fine seven-bit part, from the controller 32 higher (32–63), a whole number from 0 to 127
In words: the coarse byte chooses one of 128 big steps and the fine byte chooses one of 128 small steps inside it, giving 16,384 steps instead of 128.
```

Firmware usually writes the same thing as a bitwise left shift by 7 bits: `(msb << 7) | lsb`.

Rules worth implementing exactly:

- If 128 steps are enough, a transmitter can send only the MIDI MSB.
- After both have been sent, a fine change may send just the MIDI LSB.
- **When a MIDI MSB arrives, the receiver should reset its MIDI LSB to zero.** A new coarse value therefore never inherits a stale fine value; the sender follows up with a fresh LSB if it wants one.

So `B0 01 40` then `B0 21 20` means the modulation wheel's coarse part is 64 and its fine part 32, a 14-bit value of 8,224. If `B0 01 41` follows, the fine part resets and the value becomes 65 coarse steps with no fine part.

## Key takeaways
- Controllers 0–31 can each be paired with a fine controller 32 numbers higher to give 14-bit resolution.
- The coarse byte supplies big steps of 128 and the fine byte fills in between.
- Reset the remembered fine value to zero whenever a new coarse value arrives, as the specification requires.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
