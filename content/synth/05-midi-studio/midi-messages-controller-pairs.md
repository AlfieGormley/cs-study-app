---
id: midi-messages-controller-pairs
title: Combine coarse and fine controllers
level: intermediate
minutes: 3
sourceLesson: midi-messages
summary: Pair the first 32 controller numbers with their fine controllers, and reset the remembered fine value on a new coarse value.
---

## 14-bit controllers


128 steps are coarse for something like filter cutoff: you can hear each step as a zipper. The specification pairs controllers so that **CC 0–31 carry MIDI coarse parts and CC 32–63 carry the matching MIDI fine parts**. The MIDI LSB's controller number is always 32 more than the MIDI MSB's:

```formula
c_LSB = c_MSB + 32
c_LSB = 1 + 32 = 33
where
c_MSB: the controller number that carries the coarse (most significant) 7 bits, 0 to 31; here CC 1, the modulation wheel
c_LSB: the controller number that carries the fine (least significant) 7 bits, 32 to 63
In words: the fine half of any of the first 32 controllers lives 32 numbers higher, so CC 1 pairs with CC 33 and CC 7 with CC 39.
```

Together the two 7-bit halves give 14 bits, and the combined value is the MIDI MSB scaled up by 128 plus the MIDI LSB:

```formula
v = 128 MSB + LSB
v = 64 × 128 + 32
v = 8224
v_max = 127 × 128 + 127 = 16383
where
v: the combined 14-bit controller value, 0 to 16,383 (16,384 steps)
MSB: the coarse seven-bit part, a dimensionless integer from zero to 127
LSB: the fine seven-bit part, 0 to 127 (the fine part)
v_max: the largest possible combined value
In words: the coarse byte counts in steps of 128 and the fine byte fills in between, giving 128 × 128 = 16,384 steps instead of 128.
```

Multiplying by 128 is the same as applying a bitwise left shift by 7 bits, which is how firmware usually writes it: `(msb << 7) | lsb`.

Rules worth implementing exactly:

- If 128 steps are enough, a transmitter can send only the MIDI MSB.
- After both have been sent, a fine change may send just the MIDI LSB.
- **When a MIDI MSB arrives, the receiver should reset its MIDI LSB to zero.**

So `B0 01 40` then `B0 21 20` means modulation is 8,224: MIDI MSB 0x40 (64) and MIDI LSB 0x20 (32), exactly the worked example above.

## Key takeaways
- Pair the first 32 controller numbers with their fine controllers, and reset the remembered fine value on a new coarse value.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
