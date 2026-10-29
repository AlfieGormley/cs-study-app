---
id: midi-messages-bend-packing
title: Pack and unpack pitch bend
level: intermediate
minutes: 3
sourceLesson: midi-messages
summary: Pitch bend sends its low seven bits first and centres at 8,192 rather than zero.
---

## Pitch bend

`En ll mm` carries a 14-bit value, **least significant 7 bits first**. Unlike other controllers, the specification says pitch bend is always sent with both data bytes, because the ear is very sensitive to pitch.

- Minimum: `00 00` = 0.
- **Centre (no bend): `00 40` = 0x2000 = 8,192.**
- Maximum: `7F 7F` = 16,383.

Why centre at 8,192 rather than zero? A bend wheel moves both ways, so "no bend" has to sit in the middle of the 0–16,383 range. Resetting bend to zero is a classic bug: it means *full downward* bend.

To send a bend value you split it into two 7-bit halves; to receive one you join them again. Masking with `0x7F` keeps the low seven bits (the fine part, sent first); shifting right by seven bits and masking again gives the high seven bits (the coarse part, sent second). Joining reverses it: shift the coarse part left by seven and combine it with the fine part. Because 8,192 is exactly 64 steps of 128, its fine part is 0 and its coarse part is 64 (`0x40`), which is why the centre message is `En 00 40`.

```python
def bend_bytes(value):
    # value 0..16383, centre 8192
    # Mask the fine seven bits for byte one.
    lsb = value & 0x7F
    # Shift the coarse part into low bits.
    msb = (value >> 7) & 0x7F
    return lsb, msb

def bend_value(lsb, msb):
    return (msb << 7) | lsb

# Output: raw value, fine byte, coarse byte.
for v in (0, 8192, 16383, 12288):
    lsb, msb = bend_bytes(v)
    print(v, hex(lsb), hex(msb))

print(bend_value(0x00, 0x40))
```

```output
0 0x0 0x0
8192 0x0 0x40
16383 0x7f 0x7f
12288 0x0 0x60
8192
```

## Key takeaways
- Pitch bend is a 14-bit value sent as two data bytes, fine (low seven bits) first, then coarse.
- No bend is the centre value 8,192, sent as `En 00 40`; a raw 0 is full downward bend.
- Unlike other controllers, pitch bend is always sent with both data bytes.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
