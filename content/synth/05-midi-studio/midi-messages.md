---
id: midi-messages
title: The rest of the MIDI message set
level: intermediate
minutes: 15
summary: Control change (common numbers and 14-bit pairs), program change, pitch bend, aftertouch, running status, real-time clock and transport, SysEx, and an overview of MIDI 2.0.
---

Note on and note off make a synth play. Everything else in MIDI makes it *expressive* and *in time*: knobs and wheels (control change), patch selection (program change), pitch bend, pressure, the tempo clock, and manufacturer-specific data (SysEx).

This lesson walks through each message at the byte level, then covers running status, which every receiver must handle, and finishes with what MIDI 2.0 changes.

## The full map

Channel messages carry a channel in the low nibble of the status byte (`n` = 0–15). System messages (`0xF0`–`0xFF`) have no channel.

| Status | Message | Data bytes |
|---|---|---|
| `8n` | Note Off | key, velocity |
| `9n` | Note On | key, velocity |
| `An` | Poly Key Pressure | key, pressure |
| `Bn` | Control Change | controller, value |
| `Cn` | Program Change | program |
| `Dn` | Channel Pressure | pressure |
| `En` | Pitch Bend | LSB, MSB |
| `F0`…`F7` | System Exclusive / Common | varies |
| `F8`…`FF` | System Real-Time | none |

Notice that Program Change and Channel Pressure have **one** data byte; the other channel messages have two. A parser must know this table to tell where one message ends and the next begins.

## Control change

`Bn cc vv`: controller number `cc` (0–119) set to value `vv` (0–127). Controllers 120–127 use the same status byte but are **Channel Mode messages** (more below).

Commonly met controllers, from the MIDI Association's control change table:

| CC | Defined as |
|---|---|
| 0 / 32 | Bank Select MSB / LSB |
| 1 | Modulation wheel |
| 7 | Channel Volume |
| 10 | Pan |
| 11 | Expression |
| 64 | Sustain pedal (≤63 off, ≥64 on) |
| 71 | Sound Ctrl 2 (default: timbre) |
| 72 / 73 | Sound Ctrl 3 / 4 (release / attack) |
| 74 | Sound Ctrl 5 (default: brightness) |

Many synths map CC 74 to filter cutoff and CC 71 to resonance, following those "brightness" and "timbre" defaults, but nothing forces this. Plenty of CC numbers (for example 20–31 and 102–119) are listed as **undefined**, which makes them a sensible home for your synth's own parameters. Whatever you choose, document it in a table: the specification asks manufacturers to publish a controller allocation table, and you will need it yourself when setting up the Digitakt.

### 14-bit controllers

128 steps are coarse for something like filter cutoff: you can hear each step as a zipper. The specification pairs controllers so that **CC 0–31 are MSBs and CC 32–63 are the matching LSBs** (CC 1's LSB is CC 33, CC 7's is CC 39). Together they give 14 bits: 16,384 steps.

Rules worth implementing exactly:

- If 128 steps are enough, a transmitter can send only the MSB.
- After both have been sent, a fine change may send just the LSB.
- **When an MSB arrives, the receiver should reset its LSB to zero.**

So `B0 01 40` then `B0 21 20` means modulation = (64 << 7) | 32 = 8,224.

### RPN: setting pitch-bend range

Registered Parameter Numbers (RPNs) select a parameter with CC 101 (MSB) and CC 100 (LSB), then set it with Data Entry (CC 6, plus CC 38 for fine). RPN 0,0 is **pitch bend sensitivity**: Data Entry MSB is semitones, LSB is cents. To set ±12 semitones on channel 1, a sender transmits:

```
B0 65 00   RPN MSB = 0
B0 64 00   RPN LSB = 0 (bend range)
B0 06 0C   data entry: 12 semitones
B0 26 00   data entry LSB: 0 cents
```

Sending RPN 127,127 (the "null" RPN) afterwards stops later Data Entry messages changing it by accident. NRPNs (CC 99/98) work the same way for manufacturer-defined parameters; the Elektron manuals list which NRPNs their knobs send.

## Program change and bank select

`Cn pp` selects patch `pp`, with a single data byte. Programs are 0–127 on the wire, but many devices display them as 1–128, so the off-by-one appears again.

For more than 128 patches, the specification has the sender transmit Bank Select as a pair (CC 0 MSB, CC 32 LSB), immediately followed by the Program Change. Bank Select alone must not change the program; the new bank applies when the Program Change arrives.

## Pitch bend

`En ll mm` carries a 14-bit value, **least significant 7 bits first**. Unlike other controllers, the specification says pitch bend is always sent with both data bytes, because the ear is very sensitive to pitch.

- Minimum: `00 00` = 0.
- **Centre (no bend): `00 40` = 0x2000 = 8,192.**
- Maximum: `7F 7F` = 16,383.

```python
def bend_bytes(value):
    # value 0..16383, centre 8192
    lsb = value & 0x7F
    msb = (value >> 7) & 0x7F
    return lsb, msb

def bend_value(lsb, msb):
    return (msb << 7) | lsb

for v in (0, 8192, 16383, 12288):
    lsb, msb = bend_bytes(v)
    print(v, hex(lsb), hex(msb))

print(bend_value(0x00, 0x40))
```

```
0 0x0 0x0
8192 0x0 0x40
16383 0x7f 0x7f
12288 0x0 0x60
8192
```

How far is "full bend"? The receiver decides, or it is set via RPN 0. A ±2 semitone range is a common default. Mapping the raw value to semitones:

```python
def bend_semitones(value, rng=2):
    # rng = bend range in semitones (RPN 0)
    return (value - 8192) / 8192 * rng

for v in (0, 8192, 12288, 16383):
    print(v, round(bend_semitones(v), 4))
```

```
0 -2.0
8192 0.0
12288 1.0
16383 1.9998
```

The range is asymmetric by one step (8,192 values below centre, 8,191 above). Some implementations divide the upper half by 8,191 instead so that 16,383 reaches exactly +2; either is fine as long as 8,192 is exactly zero.

> [!warning] Reset bend to centre, not zero
> A raw value of 0 is *full downward* bend. Initialise and reset pitch bend to 8,192. The spec's "Reset All Controllers" (CC 121) likewise returns pitch bend to centre.

## Aftertouch (pressure)

Pressing harder on a key after it bottoms out can send:

- **Channel Pressure** `Dn vv`: one value for the whole channel (the MIDI Association's message summary says to send the single greatest pressure of the keys held).
- **Poly Key Pressure** `An kk vv`: a separate value per key.

The receiver decides what pressure does: volume, brightness, vibrato. Channel pressure is far more common. The Digitakt's MIDI tracks have an "AT" parameter that sends aftertouch to the external synth.

## Running status

Running status is a byte-saving rule for **channel voice and mode messages**: once a status byte has been sent, the transmitter can omit it for following messages of the same type and channel, and send only the data bytes.

```
full:     90 3C 64  90 40 64  90 43 64
running:  90 3C 64     40 64     43 64
```

Nine bytes become seven. Combined with "note on, velocity 0 = note off", a whole melody can go out with a single `90` at the start.

The receiver's rules, from the specification and its appendix:

1. Remember the last channel status byte in a **running status buffer**.
2. A data byte that arrives when a complete message has just ended reuses that status.
3. Any new channel status byte replaces it.
4. **System Exclusive and System Common** status bytes clear it.
5. **Real-time bytes do not touch it**, even when they arrive between data bytes.

Running status is optional for transmitters but mandatory for receivers. Lesson 3 turns these rules into a parser.

## System real-time: clock and transport

Real-time messages are single status bytes with no data. They may appear **anywhere**, even in the middle of another message, so they can keep accurate time.

| Byte | Message |
|---|---|
| `F8` | Timing Clock |
| `FA` | Start |
| `FB` | Continue |
| `FC` | Stop |
| `FE` | Active Sensing |
| `FF` | System Reset |

`F9` and `FD` are undefined and should be ignored.

**Timing Clock is sent 24 times per quarter note** (24 PPQN, pulses per quarter note). A receiver measures the gap between clocks to find the tempo:

```python
def clock_interval_ms(bpm, ppqn=24):
    beats_per_s = bpm / 60
    return 1000 / (beats_per_s * ppqn)

for bpm in (60, 120, 140):
    ms = clock_interval_ms(bpm)
    print(bpm, round(ms, 3))
```

```
60 41.667
120 20.833
140 17.857
```

Six clocks make one sixteenth note, which is the unit the **Song Position Pointer** (`F2 ll mm`) counts in. Transport details from the specification:

- **Start** (`FA`) means play from the beginning. **Continue** (`FB`) means resume from the current position. A synced receiver starts on the *next* `F8` after either, and the specification asks senders to leave at least 1 ms between `FA` and the first `F8`.
- **Stop** (`FC`) should stop playback immediately.
- Clocks may keep flowing while stopped, so receivers can lock to tempo before Start.

**Active Sensing** (`FE`) is optional. Once a receiver has seen it, it should expect some message at least every 300 ms. If they stop, it should assume the cable was unplugged and turn off its voices.

A simple mono synth needs clock only for tempo-synced features such as an arpeggiator or a synced LFO. It must still *tolerate* clock bytes, because a sequencer like the Digitakt may send them constantly.

## System Exclusive

SysEx carries manufacturer-defined data: patch dumps, firmware, parameter edits.

```
F0 <id> <data ...> F7
```

- The ID is 1 byte, or 3 bytes starting with `00`.
- Every SysEx payload byte is a data byte (0–127); independent real-time status bytes may interleave on the wire. 8-bit data must be packed into 7-bit bytes.
- **ID `7D` is reserved for non-commercial use** (education, research): suitable for a private experiment, not for a product released to the public even free of charge.
- IDs `7E` and `7F` are the **Universal** (non-real-time and real-time) SysEx messages defined by the MIDI specs themselves.
- Only real-time bytes may be interleaved inside a SysEx message. Any other status byte terminates it, although senders should always end with `F7`.

The Digitakt uses SysEx to send and receive project, pattern and Sound data (presets on the Digitakt II) through its SYSEX DUMP menu, which is a handy backup route.

## Channel mode messages

CC numbers 120–127 are mode messages:

| CC | Meaning |
|---|---|
| 120 | All Sound Off (silence now) |
| 121 | Reset All Controllers |
| 122 | Local Control on/off |
| 123 | All Notes Off |
| 124–127 | Omni/mono/poly mode changes |

All Notes Off and its cousins matter for stuck notes, covered in the next lesson.

## MIDI 2.0 in one section

MIDI 2.0 (announced in January 2020, core specifications updated in June 2023) **extends** MIDI 1.0 rather than replacing it. The headline changes, from the MIDI Association:

- The **Universal MIDI Packet (UMP)** replaces the byte stream with 32-, 64-, 96- or 128-bit packets. UMP can carry both MIDI 1.0 and MIDI 2.0 messages, organised as 16 groups of 16 channels.
- **Higher resolution**: velocity is 16-bit; control changes, pressure and pitch bend are 32-bit.
- **Per-note** controllers and pitch, and thousands of additional registered and assignable controllers.
- **MIDI-CI** (Capability Inquiry) lets two devices discover each other's features. Profiles and Property Exchange (JSON-based) build on it.
- Optional **Jitter Reduction timestamps**.
- **USB MIDI 2.0** carries UMP natively and can fall back to USB MIDI 1.0.

For this project, MIDI 1.0 is the right target. The Digitakt manuals describe MIDI 1.0 facilities (notes, CC, NRPN, program change, clock), and DIN MIDI carries the MIDI 1.0 byte stream. MIDI 2.0 becomes interesting if you later want very high-resolution or per-note control from a computer over USB.

## Key takeaways
- Program Change and Channel Pressure have one data byte; the other channel messages have two. A parser needs this table.
- CC 0–31 pair with CC 32–63 for 14-bit resolution, and an incoming MSB resets the LSB to zero.
- Pitch bend is 14-bit, LSB first, centred at 8,192 (`00 40`). Its range is set by the receiver or RPN 0.
- Running status lets senders omit repeated channel status bytes; receivers must support it, real-time bytes don't disturb it, and SysEx/System Common clear it.
- MIDI clock is `F8` at 24 per quarter note, with Start/Continue/Stop as `FA`/`FB`/`FC`. Real-time bytes can arrive between any two bytes.
- SysEx is `F0 … F7`. ID `7D` is reserved for non-commercial use. MIDI 2.0 adds packets, resolution and capability discovery but builds on MIDI 1.0.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
