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

To send a bend value you split it into two 7-bit halves; to receive one you join them again. The splitting uses a mask and a shift:

```formula
LSB = v & 0x7F
MSB = (v >> 7) & 0x7F
v = (MSB << 7) | LSB
LSB = 8192 & 0x7F = 0x00
MSB = (8192 >> 7) & 0x7F = 0x40
where
v: the 14-bit bend value, 0 to 16,383; centre 8,192
LSB: the first data byte sent, holding the low 7 bits
MSB: the second data byte sent, holding the high 7 bits
&: bitwise AND, keeping only bits set in both values; AND with 0x7F (binary 0111 1111) keeps the low 7 bits
>>: bitwise right shift by the given number of bits (dividing by 128 for a shift of 7, discarding the remainder)
<<: bitwise left shift by the given number of bits (multiplying by 128 for a shift of 7)
|: bitwise OR, combining the bits of both values
0x: prefix meaning hexadecimal (base 16); 0x7F is 127 and 0x40 is 64
In words: the low seven bits go in the first byte and the next seven bits in the second; joining them back gives the original value.
```

The same in Python:

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
- Pitch bend sends its low seven bits first and centres at 8,192 rather than zero.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
